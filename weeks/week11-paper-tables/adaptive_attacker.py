# -*- coding: utf-8 -*-
"""
Adaptive (defense-aware) attacker experiment.

Retires the "no adaptive attacker" limitation by testing the strongest
open threat directly. The attacker knows the coordinator probes every
discriminative feature by pushing it to its benign-high value and
measuring spoofing recall, then penalizes clients whose recall is
anomalously low on any probe. So each compromised client adds an evasion
term to its local objective: on probe-style slices built from its own
spoofed rows, it is trained to keep predicting spoofed (label 1), i.e. to
look like the honest cohort, while still trying to plant the CN0 backdoor.

The evasion strength lambda is swept. The tension under test: the CN0
backdoor requires predicting benign when CN0 is benign-high, but the CN0
probe slice rewards predicting spoofed on exactly those inputs. Reports,
per lambda, the defended backdoor lift and the mean attacker trust, so
the tradeoff is visible rather than asserted.

Reuses the Week 11 pipeline (same data split, model, D2 defense, seeds).
Run from this folder:  python adaptive_attacker.py
Outputs: results/adaptive_attacker.csv, results/fig_adaptive_attacker.png
"""
import copy, warnings, hashlib
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

def build_evasion(client, seed, cap=1500):
    # From the attacker's own spoofed rows, build probe-style slices (each probe
    # feature pushed to benign-high) with target label 1 (spoofed). Training to
    # keep predicting spoofed on these is exactly the evasion the defense checks.
    rng = np.random.default_rng(seed + 777)
    sp = client['Xt'][client['yt']==1]
    if len(sp) > cap: sp = sp[rng.choice(len(sp), cap, replace=False)]
    Xe = []
    for f in PROBE_FEATS:
        fi = FEATURES.index(f); z = sp.copy(); z[:, fi] = BENIGN_HIGH[f]; Xe.append(z)
    Xe = np.concatenate(Xe, axis=0).astype(np.float32)
    return torch.FloatTensor(Xe)

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

def train_local(mdl, Xa, ya, evade=None, lam=0.0):
    ld = loader(Xa, ya); opt = torch.optim.Adam(mdl.parameters(), lr=1e-3); crit = nn.BCEWithLogitsLoss(); mdl.train()
    for _ in range(LOCAL_EPOCHS):
        for xb, yb in ld:
            opt.zero_grad(); loss = crit(mdl(xb), yb)
            if evade is not None and lam > 0:
                # evasion: keep predicting spoofed (1) on probe-style slices
                ones = torch.ones(evade.shape[0])
                loss = loss + lam * crit(mdl(evade), ones)
            loss.backward(); opt.step()

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

def run_fl(clist, seed, lam=0.0, defense=None):
    reseed(seed)
    evasion = {i: build_evasion(clist[i], seed+i) for i in range(N_CLIENTS-N_ATTACK, N_CLIENTS)} if lam > 0 else {}
    g = BinaryDNN(D); prev=None; trust_hist=[]
    for _ in range(FL_ROUNDS):
        gp = get_p(g); locs, models = [], []
        for i, c in enumerate(clist):
            mm = copy.deepcopy(g)
            if i >= N_CLIENTS-N_ATTACK:
                train_local(mm, c['Xt'], c['yt'], evade=evasion.get(i), lam=lam)
            else:
                train_local(mm, c['Xt'], c['yt'])
            models.append(mm); lp = get_p(mm)
            if i >= N_CLIENTS-N_ATTACK:
                lp = [gg+BOOST*(pp-gg) for gg,pp in zip(gp,lp)]
            locs.append(lp)
        if defense == 'full':
            t = behavioral_trust(models, DEF_BETA, DEF_TAU)
            if prev is not None: t = DEF_EMA*t + (1-DEF_EMA)*prev
            prev = t; trust_hist.append(t.copy())
            sc_ = [[gg+N_CLIENTS*tt*(pp-gg) for gg,pp in zip(gp,params)] for tt,params in zip(t,locs)]
            new = coord_median(sc_)
        else:
            new = fedavg(locs)
        set_p(g, new)
    return dict(bsr=float((preds(g,X_TRIG)==0).mean()),
                trust=np.array(trust_hist) if trust_hist else None)

def honest(seed):
    reseed(seed); g = BinaryDNN(D)
    cl = iid_split(seed)
    for _ in range(FL_ROUNDS):
        locs=[]
        for c in cl:
            mm = copy.deepcopy(g); train_local(mm, c['Xt'], c['yt']); locs.append(get_p(mm))
        set_p(g, fedavg(locs))
    return float((preds(g,X_TRIG)==0).mean())

LAMBDAS = [0.0, 2.0, 10.0]
print(f'adaptive attacker sweep | lambdas {LAMBDAS} | seeds {SEEDS} | D2 defense')
rows = {}
hon_bsr = {sd: honest(sd) for sd in SEEDS}
for lam in LAMBDAS:
    for sd in SEEDS:
        cl = poison_cn0(iid_split(sd), POISON_RATE, sd)
        und = run_fl(cl, sd, lam=lam, defense=None)
        dfd = run_fl(cl, sd, lam=lam, defense='full')
        rows[(lam,sd)] = dict(und_lift=und['bsr']-hon_bsr[sd],
                              def_lift=dfd['bsr']-hon_bsr[sd],
                              att_trust=float(dfd['trust'][:, N_CLIENTS-N_ATTACK:].mean()))
        print(f"lambda {lam:>4} | seed {sd:>3} | undef lift {rows[(lam,sd)]['und_lift']:+.4f} | "
              f"def lift {rows[(lam,sd)]['def_lift']:+.4f} | attacker trust {rows[(lam,sd)]['att_trust']:.4f}")

def ms(v): return f'{np.mean(v):+.4f} +/- {np.std(v):.4f}'
tab = pd.DataFrame([{
    'Evasion strength (lambda)': lam,
    'Undefended lift': ms([rows[(lam,sd)]['und_lift'] for sd in SEEDS]),
    'Defended lift (D2)': ms([rows[(lam,sd)]['def_lift'] for sd in SEEDS]),
    'Mean attacker trust': f"{np.mean([rows[(lam,sd)]['att_trust'] for sd in SEEDS]):.4f} +/- {np.std([rows[(lam,sd)]['att_trust'] for sd in SEEDS]):.4f}",
} for lam in LAMBDAS])
print('\nAdaptive attacker at D2, mean +/- std over 3 seeds\n')
print(tab.to_string(index=False))
tab.to_csv(RESULTS/'adaptive_attacker.csv', index=False)

fig, ax1 = plt.subplots(figsize=(8,4.6))
dl = [np.mean([rows[(lam,sd)]['def_lift'] for sd in SEEDS]) for lam in LAMBDAS]
ds = [np.std([rows[(lam,sd)]['def_lift'] for sd in SEEDS]) for lam in LAMBDAS]
tr = [np.mean([rows[(lam,sd)]['att_trust'] for sd in SEEDS]) for lam in LAMBDAS]
ax1.errorbar(LAMBDAS, dl, yerr=ds, marker='o', color='seagreen', lw=2, capsize=4, label='defended backdoor lift (left)')
ax1.axhline(0, color='black', lw=1.1)
ax1.set_xlabel('attacker evasion strength (lambda)'); ax1.set_ylabel('defended backdoor lift')
ax2 = ax1.twinx()
ax2.plot(LAMBDAS, tr, marker='s', ls=':', color='#450084', lw=1.8, label='mean attacker trust (right)')
ax2.set_ylabel('mean attacker trust', color='#450084'); ax2.tick_params(axis='y', labelcolor='#450084')
ax2.axhline(1.0/N_CLIENTS, color='gray', ls='--', lw=1)
ax1.set_title('Adaptive (defense-aware) attacker: evasion versus the backdoor\n(D2 defense, mean of 3 seeds)', fontsize=11)
h1,l1 = ax1.get_legend_handles_labels(); h2,l2 = ax2.get_legend_handles_labels()
ax1.legend(h1+h2, l1+l2, fontsize=8.5, loc='center right')
fig.tight_layout(); fig.savefig(RESULTS/'fig_adaptive_attacker.png', bbox_inches='tight')
print('\nwrote results/adaptive_attacker.csv and results/fig_adaptive_attacker.png')
