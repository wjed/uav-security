# -*- coding: utf-8 -*-
"""
Per-feature separability of the GPS spoofing dataset.

The paper states that the coordinator probes every feature with Cohen's
d >= 0.05 and that this yields eight of the ten features, but it never shows
the underlying numbers, so a reader cannot check the threshold or see how
much class signal each feature actually carries. That is also the natural
place to be concrete about the dataset's limits rather than only conceding
them in prose: two features carry almost no class separation, which is
exactly why they sit outside the probe set and why the trigger-agnostic
claim is scoped to the discriminative set.

Emits one row per feature with the class means, Cohen's d, whether the
feature is probed, and the benign-high value used as its probe and trigger
level. No model training; this reads the same fixed split every experiment
uses (data seed 42).

Run from this folder:  python dataset_characterization.py
Outputs: results/feature_separability.csv
"""
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings('ignore')

DATA_SEED = 42
RESULTS = Path('results'); RESULTS.mkdir(exist_ok=True)

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
scaler = StandardScaler(); scaler.fit(X_pool)

DESC = {
    'DO':  'Doppler observable',
    'PD':  'Pseudorange difference',
    'CP':  'Carrier phase',
    'EC':  'Early-to-late chip ratio',
    'LC':  'Lock count',
    'PC':  'Phase consistency',
    'PIP': 'Pseudorange innovation percentage',
    'PQP': 'Phase quality parameter',
    'TCD': 'Time-correlation descriptor',
    'CN0': 'Carrier-to-noise density ratio (dB-Hz)',
}
THRESH = 0.05

rows = []
for i, f in enumerate(FEATURES):
    a0, a1 = X_pool[y_pool==0, i], X_pool[y_pool==1, i]
    d = abs(a0.mean()-a1.mean())/np.sqrt((a0.var()+a1.var())/2+1e-8)
    hi_raw = float(np.percentile(a0, 75))                 # benign-high (authentic 75th pct)
    hi_std = (hi_raw - scaler.mean_[i]) / scaler.scale_[i]
    rows.append({
        'Feature': f,
        'Description': DESC.get(f, ''),
        'Authentic mean': f'{a0.mean():.3f}',
        'Spoofed mean': f'{a1.mean():.3f}',
        "Cohen's d": f'{d:.4f}',
        'Probed': 'Yes' if d >= THRESH else 'No',
        'Benign-high (raw)': f'{hi_raw:.3f}',
        'Benign-high (std)': f'{hi_std:+.3f}',
        '_d': d,
    })

tab = pd.DataFrame(rows).sort_values('_d', ascending=False).drop(columns='_d').reset_index(drop=True)
print(f"Per-feature separability on the client pool (n={len(X_pool):,}), probe threshold d >= {THRESH}\n")
print(tab.to_string(index=False))
n_probe = (tab['Probed']=='Yes').sum()
print(f"\nprobed: {n_probe} of {len(FEATURES)}   excluded: "
      f"{', '.join(tab.loc[tab['Probed']=='No','Feature'])}")
tab.to_csv(RESULTS/'feature_separability.csv', index=False)
print(f"wrote {RESULTS/'feature_separability.csv'}")
