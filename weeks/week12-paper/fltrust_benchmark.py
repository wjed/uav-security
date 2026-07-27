# -*- coding: utf-8 -*-
"""
FLTrust benchmark comparison.

The advisor's review of the Week 12 draft asked for the one thing a venue
reviewer will look for first: a comparison against the nearest published
benchmark, not only against internal ablations. FLTrust (Cao et al., NDSS
2021) is the right choice because it shares this work's core premise, that
the server should bootstrap trust from a small clean root set it holds
itself rather than believing anything a client reports. It is the closest
prior defense to ours, so beating it (or not) is the honest test of whether
the behavioral probe adds anything over the state of the art.

FLTrust as published, reproduced here:
  1. The server trains the current global model on its own root set for the
     same number of local epochs a client would, giving a server update g0.
  2. Each client update gi is scored by trust TS_i = ReLU(cos(gi, g0)):
     updates pointing away from the server's own direction get zero weight.
  3. Each client update is rescaled to the server update's magnitude,
     ||g0||/||gi||, which is what neutralizes model-replacement scaling.
  4. The global update is the TS-weighted mean of the normalized updates.

Both defenses therefore get exactly the same root set (6,000 rows) and the
same information; the only difference is what they do with it. FLTrust asks
"does this update point the way mine does?"; ours asks "does this model have
a blind spot on a specific feature that the cohort does not?".

Run from this folder:  python fltrust_benchmark.py
Outputs: results/fltrust_benchmark.csv, results/fig_fltrust_benchmark.png

The data pipeline, model, attack, defense constants and seed protocol are
carried over verbatim from weeks/week11-paper-tables/adaptive_attacker.py so
the numbers are directly comparable to the existing ablation table. The
script re-runs honest FedAvg, the attack, and our full defense alongside
FLTrust rather than reading their published values, so every row in the
output comes from one execution of one pipeline.
"""
import copy, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')

DATA_SEED = 42
SEEDS = [42, 7, 123]
np.random.seed(DATA_SEED); torch.manual_seed(DATA_SEED)
def reseed(s): np.random.seed(s); torch.manual_seed(s)
RESULTS = Path('results'); RESULTS.mkdir(exist_ok=True)
plt.rcParams.update({'figure.dpi': 130, 'savefig.dpi': 150, 'font.size': 10,
                     'axes.grid': True, 'grid.alpha': 0.3, 'axes.spines.top': False,
                     'axes.spines.right': False, 'legend.frameon': False})

def resolve_data():
    for p in ['../week07-first-working-version/A DATASET for GPS Spoofing Detection on Unmanned Aerial System/GPS_Data_Simplified_2D_Feature_Map.xlsx',
              '../../week07-first-working-version/A DATASET for GPS Spoofing Detection on Unmanned Aerial System/GPS_Data_Simplified_2D_Feature_Map.xlsx']:
        if Path(p).exists(): return p
    raise FileNotFoundError('GPS dataset not found')

# ----------------------------------------------------------------- data
N_BENIGN, N_SPOOFED, SERVER_ROOT = 90_000, 60_000, 6_000
raw = pd.read_excel(resolve_data(), engine='openpyxl').drop_duplicates()
raw['label'] = (raw['Output'] != 0).astype(int)
fc = [c for c in raw.columns if c not in ('Output','label')]
cm = raw.duplicated(subset=fc, keep=False)
g_ = raw[cm].groupby(fc)['label'].nunique(); keys = g_[g_ > 1].index
if len(keys):
    ck = pd.DataFrame(keys.tolist(), columns=fc)
    isc = raw[fc].apply(tuple, axis=1).isin([tuple(k) for k in ck.itertuples(index=False)])
    raw = raw[~isc]
df = raw.drop(columns=['PRN','RX','TOW','Output'])
FEATURES = [c for c in df.columns if c != 'label']
df = df.drop_duplicates(subset=FEATURES, keep='first').reset_index(drop=True)
b = df[df.label==0].sample(N_BENIGN, random_state=DATA_SEED)
s = df[df.label==1].sample(N_SPOOFED, random_state=DATA_SEED)
sub = pd.concat([b,s]).sample(frac=1, random_state=DATA_SEED).reset_index(drop=True)
X = sub[FEATURES].values.astype(np.float32); y = sub['label'].values.astype(np.int64)
X_tr_all, X_test, y_tr_all, y_test = train_test_split(X, y, test_size=0.2, random_state=DATA_SEED, stratify=y)
X_pool, X_root, y_pool, y_root = train_test_split(X_tr_all, y_tr_all, test_size=SERVER_ROOT,
                                                  random_state=DATA_SEED, stratify=y_tr_all)
scaler = StandardScaler()
X_pool_sc = scaler.fit_transform(X_pool).astype(np.float32)
X_root_sc = scaler.transform(X_root).astype(np.float32)
X_test_sc = scaler.transform(X_test).astype(np.float32)

DEF_BETA, DEF_TAU, DEF_EMA = 1.0, 2.0, 0.5
N_CLIENTS, N_ATTACK, VAL_FRAC = 10, 2, 0.15
FL_ROUNDS, LOCAL_EPOCHS, BATCH, BOOST = 12, 3, 512, 3.0
POISON_RATE = 0.40
CN0 = FEATURES.index('CN0')
def scaled_val(fi, rv): return (rv - scaler.mean_[fi]) / scaler.scale_[fi]

def cohens_d():
    o = {}
    for i, f in enumerate(FEATURES):
        a0, a1 = X_pool[y_pool==0, i], X_pool[y_pool==1, i]
        o[f] = abs(a0.mean()-a1.mean())/np.sqrt((a0.var()+a1.var())/2+1e-8)
    return o
DV = cohens_d()
PROBE_FEATS = [f for f in FEATURES if DV[f] >= 0.05]
BENIGN_HIGH = {f: scaled_val(FEATURES.index(f), np.percentile(X_pool[y_pool==0, FEATURES.index(f)],75)) for f in PROBE_FEATS}
_root_spoof = X_root_sc[y_root==1]
PROBE_SLICES = {}
for f in PROBE_FEATS:
    fi = FEATURES.index(f); Xp = _root_spoof.copy(); Xp[:,fi] = BENIGN_HIGH[f]; PROBE_SLICES[f] = Xp
X_TRIG = X_test_sc[y_test==1].copy(); X_TRIG[:,CN0] = BENIGN_HIGH['CN0']

D = len(FEATURES)
class BinaryDNN(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d,64), nn.ReLU(), nn.Dropout(0.2),
                                 nn.Linear(64,32), nn.ReLU(), nn.Dropout(0.2),
                                 nn.Linear(32,16), nn.ReLU(), nn.Linear(16,1))
    def forward(self, x): return self.net(x).squeeze(-1)

def iid_split(seed):
    rng = np.random.default_rng(seed)
    bi, si = np.where(y_pool==0)[0], np.where(y_pool==1)[0]; rng.shuffle(bi); rng.shuffle(si); cl=[]
    for bb, ss in zip(np.array_split(bi,N_CLIENTS), np.array_split(si,N_CLIENTS)):
        idx = np.concatenate([bb,ss]); rng.shuffle(idx)
        Xc, yc = X_pool_sc[idx], y_pool[idx]
        Xt,Xv,yt,yv = train_test_split(Xc,yc,test_size=VAL_FRAC,random_state=seed,stratify=yc)
        cl.append({'Xt':Xt,'yt':yt,'Xv':Xv,'yv':yv})
    return cl

def poison_cn0(base, rate, seed):
    out = list(base)
    for i in range(N_CLIENTS-N_ATTACK, N_CLIENTS):
        c = base[i]
        def _p(Xa, ya, sd):
            Xa, ya = Xa.copy(), ya.copy(); rng = np.random.default_rng(sd)
            idx = np.where(ya==1)[0]; ch = rng.choice(idx, size=int(len(idx)*rate), replace=False)
            Xa[ch,CN0] = BENIGN_HIGH['CN0']; ya[ch] = 0; return Xa, ya
        Xt,yt = _p(c['Xt'],c['yt'],seed+i); Xv,yv = _p(c['Xv'],c['yv'],seed+i+100)
        out[i] = {'Xt':Xt,'yt':yt,'Xv':Xv,'yv':yv}
    return out

def loader(Xa, ya): return DataLoader(TensorDataset(torch.FloatTensor(Xa), torch.FloatTensor(ya.astype(np.float32))), batch_size=BATCH, shuffle=True)
def preds(mdl, Xa):
    mdl.eval()
    with torch.no_grad(): return (mdl(torch.FloatTensor(Xa)) > 0).long().numpy()
def acc(mdl, Xa, ya): return (preds(mdl, Xa) == ya).mean()
def get_p(mdl): return [p.data.clone() for p in mdl.parameters()]
def set_p(mdl, ps):
    for p, v in zip(mdl.parameters(), ps): p.data.copy_(v)
def coord_median(pl): return [torch.stack(list(layers),0).median(0).values for layers in zip(*pl)]
def fedavg(pl, w=None):
    if w is None: w = [1/len(pl)]*len(pl)
    return [sum(wi*p for wi,p in zip(w,layers)) for layers in zip(*pl)]

def train_local(mdl, Xa, ya):
    ld = loader(Xa, ya); opt = torch.optim.Adam(mdl.parameters(), lr=1e-3); crit = nn.BCEWithLogitsLoss(); mdl.train()
    for _ in range(LOCAL_EPOCHS):
        for xb, yb in ld:
            opt.zero_grad(); crit(mdl(xb), yb).backward(); opt.step()

def behavioral_trust(models, beta, tau):
    clean = np.array([acc(mm, X_root_sc, y_root) for mm in models])
    det = np.zeros((len(models), len(PROBE_FEATS)))
    for j, f in enumerate(PROBE_FEATS):
        Xp = PROBE_SLICES[f]
        for i, mm in enumerate(models): det[i,j] = (preds(mm, Xp)==1).mean()
    med = np.median(det, axis=0); mad = np.median(np.abs(det-med), axis=0)+1e-6
    susp = np.maximum(0.0, (med-det)/mad).max(axis=1)
    if clean.max() < 0.55 or (clean.max()-clean.min()) < 1e-3:
        return np.ones(len(models))/len(models)
    s_eff = np.maximum(0.0, susp - tau)
    r = clean*np.exp(-beta*s_eff)
    return r/r.sum() if r.sum() > 1e-9 else np.ones(len(models))/len(models)

# ------------------------------------------------------- FLTrust (Cao et al.)
def _flat(ps): return torch.cat([p.reshape(-1) for p in ps])
def _unflat(vec, like):
    out, i = [], 0
    for p in like:
        n = p.numel(); out.append(vec[i:i+n].view_as(p).clone()); i += n
    return out

def fltrust_agg(gp, locs, server_params):
    """TS_i = ReLU(cos(gi, g0)); each gi rescaled to ||g0||; TS-weighted mean.

    Returns the new global parameters and the normalized trust vector (so it
    is directly comparable to our own trust, where uniform is 1/N).
    """
    gflat = _flat(gp)
    g0 = _flat(server_params) - gflat
    n0 = g0.norm()
    ts, normed = [], []
    for lp in locs:
        gi = _flat(lp) - gflat
        ni = gi.norm()
        cos = torch.dot(gi, g0) / (ni * n0 + 1e-12)
        ts.append(torch.clamp(cos, min=0.0))
        normed.append(gi * (n0 / (ni + 1e-12)))     # magnitude normalization
    tsv = torch.stack(ts)
    tot = tsv.sum()
    if tot < 1e-12:                                  # every update rejected
        return [p.clone() for p in gp], np.ones(len(locs))/len(locs)
    agg = sum(t * v for t, v in zip(ts, normed)) / tot
    new = _unflat(gflat + agg, gp)
    return new, (tsv / tot).numpy()

# ----------------------------------------------------------------- runner
def evaluate(g):
    p_clean = preds(g, X_test_sc)
    return dict(clean=float((p_clean == y_test).mean()),
                recall=float((p_clean[y_test==1] == 1).mean()),
                bsr=float((preds(g, X_TRIG) == 0).mean()))

def run_fl(clist, seed, mode, attack=True):
    """mode: 'fedavg' | 'full' (ours) | 'fltrust'"""
    reseed(seed)
    g = BinaryDNN(D); prev = None; trust_hist = []
    for _ in range(FL_ROUNDS):
        gp = get_p(g); locs, models = [], []
        for i, c in enumerate(clist):
            mm = copy.deepcopy(g)
            train_local(mm, c['Xt'], c['yt'])
            models.append(mm); lp = get_p(mm)
            if attack and i >= N_CLIENTS-N_ATTACK:
                lp = [gg+BOOST*(pp-gg) for gg,pp in zip(gp,lp)]
            locs.append(lp)
        if mode == 'full':
            t = behavioral_trust(models, DEF_BETA, DEF_TAU)
            if prev is not None: t = DEF_EMA*t + (1-DEF_EMA)*prev
            prev = t; trust_hist.append(t.copy())
            sc_ = [[gg+N_CLIENTS*tt*(pp-gg) for gg,pp in zip(gp,params)] for tt,params in zip(t,locs)]
            new = coord_median(sc_)
        elif mode == 'fltrust':
            # the server's own update from the root set, same local budget
            sm = copy.deepcopy(g); train_local(sm, X_root_sc, y_root)
            new, t = fltrust_agg(gp, locs, get_p(sm))
            trust_hist.append(t.copy())
        else:
            new = fedavg(locs)
        set_p(g, new)
    out = evaluate(g)
    out['trust'] = np.array(trust_hist) if trust_hist else None
    return out

# ----------------------------------------------------------------- experiment
print(f'FLTrust benchmark | seeds {SEEDS} | {FL_ROUNDS} rounds | '
      f'{N_CLIENTS} clients, {N_ATTACK} compromised')
print(f'probe features ({len(PROBE_FEATS)}): {", ".join(PROBE_FEATS)}\n')

MODES = [('Honest FedAvg (no attack)', 'fedavg', False),
         ('Attack (FedAvg)',           'fedavg', True),
         ('FLTrust',                   'fltrust', True),
         ('Ours (trust + median, D2)', 'full',    True)]

res = {}
for sd in SEEDS:
    clean_split = iid_split(sd)
    poisoned = poison_cn0(clean_split, POISON_RATE, sd)
    for label, mode, atk in MODES:
        r = run_fl(poisoned if atk else clean_split, sd, mode, attack=atk)
        res[(label, sd)] = r
        print(f"{label:<28} seed {sd:>3} | clean {r['clean']:.4f} | "
              f"recall {r['recall']:.4f} | BSR {r['bsr']:.4f}")
    print()

# lift is paired within-seed against that seed's own honest baseline
for sd in SEEDS:
    hb = res[('Honest FedAvg (no attack)', sd)]['bsr']
    for label, _, _ in MODES:
        res[(label, sd)]['lift'] = res[(label, sd)]['bsr'] - hb

def ms(vals, sign=False):
    m, s = float(np.mean(vals)), float(np.std(vals))
    return (f'{m:+.4f} +/- {s:.4f}') if sign else (f'{m:.4f} +/- {s:.4f}')

rows = []
for label, _, _ in MODES:
    rows.append({
        'Method':          label,
        'Clean Accuracy':  ms([res[(label,sd)]['clean']  for sd in SEEDS]),
        'Spoofing Recall': ms([res[(label,sd)]['recall'] for sd in SEEDS]),
        'BSR':             ms([res[(label,sd)]['bsr']    for sd in SEEDS]),
        'Backdoor Lift':   ms([res[(label,sd)]['lift']   for sd in SEEDS], sign=True),
    })

# trust attribution: how each defense weights the compromised clients, and how
# often it zeroes an honest one (its false-positive analogue)
for label in ('FLTrust', 'Ours (trust + median, D2)'):
    at, hf, hmin = [], [], []
    for sd in SEEDS:
        T = res[(label, sd)]['trust']
        at.append(T[:, N_CLIENTS-N_ATTACK:].mean())
        hon = T[:, :N_CLIENTS-N_ATTACK]
        hf.append((hon < (0.5/N_CLIENTS)).mean())   # honest client-round down-weighted below half-uniform
        hmin.append(hon.min())
    r = next(r for r in rows if r['Method'] == label)
    r['Attacker Trust'] = ms(at)
    r['Honest Down-weighted'] = f'{100*float(np.mean(hf)):.1f}%'
for r in rows:
    r.setdefault('Attacker Trust', '---')
    r.setdefault('Honest Down-weighted', '---')

tab = pd.DataFrame(rows)
print('\nFLTrust benchmark, mean +/- std over 3 seeds (uniform trust = 0.100)\n')
print(tab.to_string(index=False))
tab.to_csv(RESULTS/'fltrust_benchmark.csv', index=False)
print(f'\nwrote {RESULTS/"fltrust_benchmark.csv"}')

# Keep the raw per-seed numbers so the figure can be restyled later without
# paying for another twelve federated runs, and so the plotted values can be
# checked against the table without rerunning anything.
np.savez(RESULTS/'fltrust_raw.npz',
         seeds=np.array(SEEDS),
         methods=np.array([m[0] for m in MODES]),
         scalars=np.array([[[res[(m[0],sd)][k] for k in ('clean','recall','bsr','lift')]
                            for sd in SEEDS] for m in MODES]),
         trust_fltrust=np.stack([res[('FLTrust',sd)]['trust'] for sd in SEEDS]),
         trust_ours=np.stack([res[('Ours (trust + median, D2)',sd)]['trust'] for sd in SEEDS]))
print(f'wrote {RESULTS/"fltrust_raw.npz"}')

# ----------------------------------------------------------------- figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 4.2))
labels = ['Attack\n(FedAvg)', 'FLTrust', 'Ours\n(D2)']
keys   = ['Attack (FedAvg)', 'FLTrust', 'Ours (trust + median, D2)']
means  = [np.mean([res[(k,sd)]['lift'] for sd in SEEDS]) for k in keys]
stds   = [np.std([res[(k,sd)]['lift'] for sd in SEEDS]) for k in keys]
cols   = ['#E4572E', '#3C738B', 'seagreen']
ax1.bar(labels, means, yerr=stds, capsize=5, color=cols, width=.6)
ax1.axhline(0, color='black', lw=1.1)
ax1.set_ylabel('backdoor lift (BSR - honest baseline)')
ax1.set_title('Backdoor lift vs the nearest benchmark')
ax1.set_ylim(min(means)-max(stds)-0.045, max(means)+max(stds)+0.035)
for i,(m,s) in enumerate(zip(means,stds)):
    # clear the error bar, not just the bar top, or the label sits on the whisker
    tip = m + s if m >= 0 else m - s
    ax1.annotate(f'{m:+.3f}', (i, tip), textcoords='offset points',
                 xytext=(0, 7 if m >= 0 else -15), ha='center', fontsize=9)

rounds = np.arange(1, FL_ROUNDS+1)
for k, c, nm in ((('FLTrust'), '#3C738B', 'FLTrust'),
                 (('Ours (trust + median, D2)'), 'seagreen', 'Ours (D2)')):
    A = np.stack([res[(k,sd)]['trust'][:, N_CLIENTS-N_ATTACK:].mean(axis=1) for sd in SEEDS])
    ax2.plot(rounds, A.mean(0), marker='o', ms=3.5, color=c, lw=1.9, label=nm)
    ax2.fill_between(rounds, A.mean(0)-A.std(0), A.mean(0)+A.std(0), color=c, alpha=.18)
ax2.axhline(1/N_CLIENTS, color='black', ls=':', lw=1.2)
ax2.annotate('uniform trust (0.10)', (FL_ROUNDS*0.52, 1/N_CLIENTS), fontsize=8.5,
             textcoords='offset points', xytext=(0,5))
ax2.set_xlabel('federated round'); ax2.set_ylabel('mean trust assigned to compromised clients')
ax2.set_title('Trust given to the two compromised UAVs')
ax2.legend()
plt.tight_layout()
plt.savefig(RESULTS/'fig_fltrust_benchmark.png', bbox_inches='tight')
print(f'wrote {RESULTS/"fig_fltrust_benchmark.png"}')
