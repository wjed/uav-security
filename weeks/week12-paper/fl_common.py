# -*- coding: utf-8 -*-
"""
Shared federated-learning harness for the Week 12 paper revision.

Every revision experiment imports this module, so the data split, model,
attack, defense and metric definitions are defined exactly once and cannot
drift between experiments. The split is fixed at seed 42 (the evaluation
target never moves); the federated randomness that matters (client
partition, poison draw, init, batch order) is varied across seeds 42/7/123.

Provides:
  * the fixed preprocessing pipeline and probe construction
  * IID and Dirichlet non-IID client partitioners
  * the CN0 poisoning attack with model-replacement scaling
  * eight aggregation rules, so the proposed defense can be compared
    against published baselines on identical inputs
  * a single metric function, so every table reports the same quantities

Aggregation rules implemented (Reviewer comments 1 and 5):
  fedavg        uniform averaging
  accweight     weights proportional to *client-reported* accuracy (the
                vulnerable target; attackers report 0.99)
  median        coordinate-wise median
  trimmed       coordinate-wise trimmed mean, trimming f from each end
  krum          Krum: single update minimising distance to its n-f-2 nearest
  multikrum     Multi-Krum: mean of the m best-scoring updates
  fltrust       FLTrust (Cao et al., NDSS 2021): ReLU(cosine) trust against a
                server update computed on the root set, with magnitude
                normalisation
  trust         proposed behavioural trust, weighted mean
  full          proposed behavioural trust + coordinate-wise median
"""
from __future__ import annotations
import copy, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings('ignore')

# ------------------------------------------------------------------ constants
DATA_SEED = 42
SEEDS = [42, 7, 123]
N_BENIGN, N_SPOOFED, SERVER_ROOT = 90_000, 60_000, 6_000
N_CLIENTS, N_ATTACK, VAL_FRAC = 10, 2, 0.15
FL_ROUNDS, LOCAL_EPOCHS, BATCH, BOOST = 12, 3, 512, 3.0
POISON_RATE = 0.40
DEF_BETA, DEF_TAU, DEF_EMA = 1.0, 2.0, 0.5
FAKE_ACC = 0.99                     # what a compromised client reports
UNIFORM = 1.0 / N_CLIENTS
FLAG_THRESH = 0.5 * UNIFORM         # "flagged" = held below half uniform weight

RESULTS = Path(__file__).resolve().parent / 'results'
RESULTS.mkdir(exist_ok=True)


def reseed(s):
    np.random.seed(s); torch.manual_seed(s)


def _resolve_data():
    here = Path(__file__).resolve().parent
    rel = 'week07-first-working-version/A DATASET for GPS Spoofing Detection on Unmanned Aerial System/GPS_Data_Simplified_2D_Feature_Map.xlsx'
    for base in (here.parent, here.parent.parent / 'weeks'):
        p = base / rel
        if p.exists():
            return p
    raise FileNotFoundError('GPS dataset not found')


# ------------------------------------------------------------------ data
np.random.seed(DATA_SEED); torch.manual_seed(DATA_SEED)
_raw = pd.read_excel(_resolve_data(), engine='openpyxl').drop_duplicates()
_raw['label'] = (_raw['Output'] != 0).astype(int)
_fc = [c for c in _raw.columns if c not in ('Output', 'label')]
_cm = _raw.duplicated(subset=_fc, keep=False)
_g = _raw[_cm].groupby(_fc)['label'].nunique()
_keys = _g[_g > 1].index
if len(_keys):
    _ck = pd.DataFrame(_keys.tolist(), columns=_fc)
    _isc = _raw[_fc].apply(tuple, axis=1).isin([tuple(k) for k in _ck.itertuples(index=False)])
    _raw = _raw[~_isc]
_df = _raw.drop(columns=['PRN', 'RX', 'TOW', 'Output'])
FEATURES = [c for c in _df.columns if c != 'label']
_df = _df.drop_duplicates(subset=FEATURES, keep='first').reset_index(drop=True)
_b = _df[_df.label == 0].sample(N_BENIGN, random_state=DATA_SEED)
_s = _df[_df.label == 1].sample(N_SPOOFED, random_state=DATA_SEED)
_sub = pd.concat([_b, _s]).sample(frac=1, random_state=DATA_SEED).reset_index(drop=True)
X = _sub[FEATURES].values.astype(np.float32)
y = _sub['label'].values.astype(np.int64)
X_tr_all, X_test, y_tr_all, y_test = train_test_split(
    X, y, test_size=0.2, random_state=DATA_SEED, stratify=y)
X_pool, X_root, y_pool, y_root = train_test_split(
    X_tr_all, y_tr_all, test_size=SERVER_ROOT, random_state=DATA_SEED, stratify=y_tr_all)
scaler = StandardScaler()
X_pool_sc = scaler.fit_transform(X_pool).astype(np.float32)
X_root_sc = scaler.transform(X_root).astype(np.float32)
X_test_sc = scaler.transform(X_test).astype(np.float32)
D = len(FEATURES)
CN0 = FEATURES.index('CN0')


def _scaled(fi, rv):
    return (rv - scaler.mean_[fi]) / scaler.scale_[fi]


def cohens_d():
    out = {}
    for i, f in enumerate(FEATURES):
        a0, a1 = X_pool[y_pool == 0, i], X_pool[y_pool == 1, i]
        out[f] = abs(a0.mean() - a1.mean()) / np.sqrt((a0.var() + a1.var()) / 2 + 1e-8)
    return out


DV = cohens_d()
PROBE_FEATS = [f for f in FEATURES if DV[f] >= 0.05]
BENIGN_HIGH = {f: _scaled(FEATURES.index(f),
                          np.percentile(X_pool[y_pool == 0, FEATURES.index(f)], 75))
               for f in PROBE_FEATS}
_root_spoof = X_root_sc[y_root == 1]
PROBE_SLICES = {}
for _f in PROBE_FEATS:
    _fi = FEATURES.index(_f)
    _Xp = _root_spoof.copy(); _Xp[:, _fi] = BENIGN_HIGH[_f]
    PROBE_SLICES[_f] = _Xp
X_TRIG = X_test_sc[y_test == 1].copy()
X_TRIG[:, CN0] = BENIGN_HIGH['CN0']


# ------------------------------------------------------------------ model
class BinaryDNN(nn.Module):
    def __init__(self, d, widths=(64, 32, 16), p_drop=0.2):
        super().__init__()
        layers, prev = [], d
        for i, w in enumerate(widths):
            layers += [nn.Linear(prev, w), nn.ReLU()]
            if i < len(widths) - 1:
                layers.append(nn.Dropout(p_drop))
            prev = w
        layers.append(nn.Linear(prev, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x).squeeze(-1)


def n_params(m):
    return sum(p.numel() for p in m.parameters())


# ------------------------------------------------------------------ partitions
def iid_split(seed):
    rng = np.random.default_rng(seed)
    bi, si = np.where(y_pool == 0)[0], np.where(y_pool == 1)[0]
    rng.shuffle(bi); rng.shuffle(si)
    out = []
    for bb, ss in zip(np.array_split(bi, N_CLIENTS), np.array_split(si, N_CLIENTS)):
        idx = np.concatenate([bb, ss]); rng.shuffle(idx)
        out.append(_mk_client(idx, seed))
    return out


def dirichlet_split(seed, alpha, min_rows=200):
    """Label-skew non-IID: per class, split rows across clients by Dir(alpha).

    Small alpha means a client's benign/spoofed mix is far from the global
    60/40, which is what stresses a cohort-median trust rule (Reviewer 2).

    Only a floor on a client's *total* rows is enforced, not a per-class floor.
    At alpha=0.1 a per-class floor is essentially unsatisfiable with ten
    clients, and forcing one would quietly convert the extreme-skew condition
    into a mild one. A client holding almost no spoofed rows is the realistic
    hard case, so it is allowed; the resulting per-client class mix is reported
    by describe_split() rather than hidden.
    """
    rng = np.random.default_rng(seed)
    for _ in range(500):
        parts = [[] for _ in range(N_CLIENTS)]
        for cls in (0, 1):
            idx = np.where(y_pool == cls)[0]
            rng.shuffle(idx)
            p = rng.dirichlet(np.repeat(alpha, N_CLIENTS))
            cuts = (np.cumsum(p) * len(idx)).astype(int)[:-1]
            for c, chunk in enumerate(np.split(idx, cuts)):
                parts[c].append(chunk)
        if min(sum(len(c) for c in p) for p in parts) >= min_rows:
            return [_mk_client(np.concatenate(p), seed) for p in parts]
    raise RuntimeError(f'could not build a usable Dirichlet split at alpha={alpha}')


def _mk_client(idx, seed):
    Xc, yc = X_pool_sc[idx], y_pool[idx]
    # stratifying needs at least two members of each class; under strong skew a
    # client can hold one class only, in which case a plain split is correct
    counts = np.bincount(yc, minlength=2)
    strat = yc if counts.min() >= 2 else None
    Xt, Xv, yt, yv = train_test_split(Xc, yc, test_size=VAL_FRAC,
                                      random_state=seed, stratify=strat)
    return {'Xt': Xt, 'yt': yt, 'Xv': Xv, 'yv': yv}


SPOOF_GLOBAL = N_SPOOFED / (N_BENIGN + N_SPOOFED)      # 0.40


def ratio_skew_split(seed, alpha, lo=0.12, hi=0.72):
    """Non-IID by *unequal benign/spoofed class ratios*, with both classes kept.

    Unconstrained Dirichlet partitioning (dirichlet_split) turned out to be
    unusable on this dataset: at alpha <= 0.5 most clients end up holding a
    single class, the federated detector never learns the spoofed class at all
    (honest recall falls to 0.07 at alpha=0.5 and 0.001 at alpha=0.1), honest
    BSR saturates at 1.0, and backdoor lift has no headroom left to measure. At
    alpha=0.1 one attacker drew zero spoofed rows and could not mount the attack
    at all. Those runs measure the collapse of the base learner, not the
    behaviour of any defense, so they are reported as a negative result and not
    used to compare rules.

    This partitioner implements the review's second suggested option instead:
    every client keeps an equal number of rows but a *different* benign/spoofed
    ratio, drawn from Dir(alpha) and clipped to [lo, hi]. Smaller alpha means a
    wider spread of client class ratios around the global 0.40, which is the
    heterogeneity the cohort-median trust rule actually has to survive, while
    the task stays learnable so the comparison remains meaningful.
    """
    rng = np.random.default_rng(seed)
    bi = np.where(y_pool == 0)[0].copy()
    si = np.where(y_pool == 1)[0].copy()
    rng.shuffle(bi); rng.shuffle(si)
    T = len(y_pool) // N_CLIENTS

    w = rng.dirichlet(np.repeat(alpha, N_CLIENTS))
    frac = np.clip(w * N_CLIENTS * SPOOF_GLOBAL, lo, hi)
    n_sp = np.round(frac * T).astype(int)
    if n_sp.sum() > len(si):                       # respect what actually exists
        n_sp = np.floor(n_sp * len(si) / n_sp.sum()).astype(int)
    n_bn = np.minimum(T - n_sp, len(bi) // N_CLIENTS + T)
    if n_bn.sum() > len(bi):
        n_bn = np.floor(n_bn * len(bi) / n_bn.sum()).astype(int)

    out, bp, sp = [], 0, 0
    for c in range(N_CLIENTS):
        idx = np.concatenate([bi[bp:bp + n_bn[c]], si[sp:sp + n_sp[c]]])
        bp += n_bn[c]; sp += n_sp[c]
        rng.shuffle(idx)
        out.append(_mk_client(idx, seed))
    return out


def describe_split(clients):
    """Per-client row count and spoofed fraction, so the realised skew of a
    partition is auditable instead of assumed."""
    rows = [len(c['Xt']) for c in clients]
    frac = [float(c['yt'].mean()) if len(c['yt']) else 0.0 for c in clients]
    spoof = [int(c['yt'].sum()) for c in clients]
    return dict(rows=rows, spoof_frac=frac, spoof_rows=spoof,
                atk_spoof_rows=spoof[N_CLIENTS - N_ATTACK:])


def poison(clients, seed, rate=POISON_RATE, feat='CN0', n_attack=None):
    """Overwrite `feat` with its benign-high value on `rate` of each attacker's
    spoofed rows and relabel them authentic.

    `n_attack` is the *true* number of compromised clients. It is passed
    explicitly rather than read from the module global so that an experiment
    can vary it without silently also changing the `f` that the Byzantine-robust
    baselines assume, which would defeat the point of such a sweep.
    """
    na = N_ATTACK if n_attack is None else n_attack
    fi = FEATURES.index(feat)
    hi = BENIGN_HIGH[feat]
    out = list(clients)
    for i in range(N_CLIENTS - na, N_CLIENTS):
        c = clients[i]

        def _p(Xa, ya, sd):
            Xa, ya = Xa.copy(), ya.copy()
            rng = np.random.default_rng(sd)
            idx = np.where(ya == 1)[0]
            if len(idx) == 0:
                return Xa, ya
            ch = rng.choice(idx, size=int(len(idx) * rate), replace=False)
            Xa[ch, fi] = hi; ya[ch] = 0
            return Xa, ya

        Xt, yt = _p(c['Xt'], c['yt'], seed + i)
        Xv, yv = _p(c['Xv'], c['yv'], seed + i + 100)
        out[i] = {'Xt': Xt, 'yt': yt, 'Xv': Xv, 'yv': yv}
    return out


# ------------------------------------------------------------------ train/eval
def loader(Xa, ya):
    return DataLoader(TensorDataset(torch.FloatTensor(Xa),
                                    torch.FloatTensor(ya.astype(np.float32))),
                      batch_size=BATCH, shuffle=True)


def preds(mdl, Xa):
    mdl.eval()
    with torch.no_grad():
        return (mdl(torch.FloatTensor(Xa)) > 0).long().numpy()


def acc(mdl, Xa, ya):
    return float((preds(mdl, Xa) == ya).mean())


def get_p(mdl):
    return [p.data.clone() for p in mdl.parameters()]


def set_p(mdl, ps):
    for p, v in zip(mdl.parameters(), ps):
        p.data.copy_(v)


def train_local(mdl, Xa, ya, epochs=LOCAL_EPOCHS, lr=1e-3):
    ld = loader(Xa, ya)
    opt = torch.optim.Adam(mdl.parameters(), lr=lr)
    crit = nn.BCEWithLogitsLoss()
    mdl.train()
    for _ in range(epochs):
        for xb, yb in ld:
            opt.zero_grad(); crit(mdl(xb), yb).backward(); opt.step()


def metrics(g):
    """Full operating-point report (Reviewer comment 4), not just accuracy."""
    p = preds(g, X_test_sc)
    tp = int(((p == 1) & (y_test == 1)).sum())
    fn = int(((p == 0) & (y_test == 1)).sum())
    fp = int(((p == 1) & (y_test == 0)).sum())
    tn = int(((p == 0) & (y_test == 0)).sum())
    rec = tp / max(tp + fn, 1)
    prec = tp / max(tp + fp, 1)
    spec = tn / max(tn + fp, 1)
    return dict(
        clean=float((p == y_test).mean()),
        recall=rec, precision=prec,
        f1=(2 * prec * rec / max(prec + rec, 1e-12)),
        balacc=0.5 * (rec + spec),
        far=fp / max(fp + tn, 1),            # false-alarm rate on authentic rows
        tp=tp, fn=fn, fp=fp, tn=tn,
        bsr=float((preds(g, X_TRIG) == 0).mean()),
    )


# ------------------------------------------------------------------ aggregation
def _flat(ps):
    return torch.cat([p.reshape(-1) for p in ps])


def _unflat(vec, like):
    out, i = [], 0
    for p in like:
        n = p.numel(); out.append(vec[i:i + n].view_as(p).clone()); i += n
    return out


def coord_median(pl):
    return [torch.stack(list(l), 0).median(0).values for l in zip(*pl)]


def weighted_mean(pl, w):
    return [sum(wi * p for wi, p in zip(w, l)) for l in zip(*pl)]


def trimmed_mean(pl, f=N_ATTACK):
    out = []
    for l in zip(*pl):
        st = torch.stack(list(l), 0).sort(0).values
        out.append(st[f:len(pl) - f].mean(0))
    return out


def _krum_scores(locs, gp, f=N_ATTACK):
    U = torch.stack([_flat(l) - _flat(gp) for l in locs], 0)
    d = torch.cdist(U, U) ** 2
    k = max(len(locs) - f - 2, 1)
    return torch.stack([torch.sort(row)[0][1:k + 1].sum() for row in d]), U


def krum(locs, gp, f=N_ATTACK, m=1):
    sc, U = _krum_scores(locs, gp, f)
    sel = torch.argsort(sc)[:m]
    agg = U[sel].mean(0)
    chosen = np.zeros(len(locs)); chosen[sel.numpy()] = 1.0
    return _unflat(_flat(gp) + agg, gp), chosen


def fltrust(locs, gp, server_ps):
    gflat = _flat(gp)
    g0 = _flat(server_ps) - gflat
    n0 = g0.norm()
    ts, normed = [], []
    for lp in locs:
        gi = _flat(lp) - gflat
        ni = gi.norm()
        ts.append(torch.clamp(torch.dot(gi, g0) / (ni * n0 + 1e-12), min=0.0))
        normed.append(gi * (n0 / (ni + 1e-12)))
    tsv = torch.stack(ts); tot = tsv.sum()
    if tot < 1e-12:
        return [p.clone() for p in gp], np.ones(len(locs)) / len(locs)
    agg = sum(t * v for t, v in zip(ts, normed)) / tot
    return _unflat(gflat + agg, gp), (tsv / tot).numpy()


def behavioral_trust(models, beta=DEF_BETA, tau=DEF_TAU, probe_feats=None,
                     root_X=None, root_y=None, probe_slices=None):
    pf = probe_feats if probe_feats is not None else PROBE_FEATS
    rX = X_root_sc if root_X is None else root_X
    ry = y_root if root_y is None else root_y
    ps = PROBE_SLICES if probe_slices is None else probe_slices
    clean = np.array([acc(m, rX, ry) for m in models])
    det = np.zeros((len(models), len(pf)))
    for j, f in enumerate(pf):
        Xp = ps[f]
        for i, m in enumerate(models):
            det[i, j] = (preds(m, Xp) == 1).mean()
    med = np.median(det, axis=0)
    mad = np.median(np.abs(det - med), axis=0) + 1e-6
    susp = np.maximum(0.0, (med - det) / mad).max(axis=1)
    if clean.max() < 0.55 or (clean.max() - clean.min()) < 1e-3:
        return np.ones(len(models)) / len(models)
    r = clean * np.exp(-beta * np.maximum(0.0, susp - tau))
    return r / r.sum() if r.sum() > 1e-9 else np.ones(len(models)) / len(models)
