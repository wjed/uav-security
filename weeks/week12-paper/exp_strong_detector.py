# -*- coding: utf-8 -*-
"""
Reviewer comment 4, second half: do the defense conclusions transfer to a
stronger base detector?

exp_detector.py establishes that they should be tested, because it shows the
weakness is not the dataset. Trained centrally, the paper's own 64-32-16 MLP
reaches 0.907 spoofing recall and gradient boosting reaches 0.993, against
0.529 for the federated model. The features are separable; the federated
configuration (12 rounds of 3 local epochs on a small MLP) simply underfits.

This script therefore re-runs the central comparison under a materially
stronger federated configuration -- 30 rounds and a 256-128-64 MLP, which
reaches 0.851 honest recall, most of the way to the centralised ceiling -- and
asks whether the ordering and the sign of backdoor lift survive. If they do,
the defense conclusions are not an artefact of a weak detector. If they do not,
the paper must say so.

Run from this folder:  python exp_strong_detector.py
Outputs: results/strong_detector.csv, results/fig_strong_detector.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import fl_common as F
from fl_runner import run, ms, pct

plt.rcParams.update({'figure.dpi': 130, 'savefig.dpi': 150, 'font.size': 10,
                     'axes.grid': True, 'grid.alpha': 0.3, 'axes.spines.top': False,
                     'axes.spines.right': False, 'legend.frameon': False})

WEAK = dict(rounds=12, widths=(64, 32, 16))
STRONG = dict(rounds=30, widths=(256, 128, 64))
RULES = [('fedavg', 'FedAvg (attacked)'), ('median', 'Coordinate-wise median'),
         ('multikrum', 'Multi-Krum (f=2)'), ('fltrust', 'FLTrust'),
         ('trust', 'Behavioral trust (ours)'), ('full', 'Trust + median (ours)')]

print('stronger-detector check | weak = 12 rounds, 64-32-16 | '
      'strong = 30 rounds, 256-128-64\n')

rows, raw = [], {}
for cfg_name, cfg in (('weak (paper)', WEAK), ('strong', STRONG)):
    for sd in F.SEEDS:
        split = F.iid_split(sd)
        pois = F.poison(split, sd)
        h = run(split, sd, 'fedavg', attack=False, **cfg)
        raw[(cfg_name, 'honest', sd)] = h
        print(f"[{cfg_name} seed {sd}] honest recall {h['recall']:.4f} "
              f"F1 {h['f1']:.4f} BSR {h['bsr']:.4f}")
        for rule, label in RULES:
            r = run(pois, sd, rule, attack=True, **cfg)
            r['lift'] = r['bsr'] - h['bsr']
            raw[(cfg_name, rule, sd)] = r
            print(f"    {label:<26} rec {r['recall']:.4f} BSR {r['bsr']:.4f} "
                  f"lift {r['lift']:+.4f}")
    print()

for cfg_name, _ in (('weak (paper)', WEAK), ('strong', STRONG)):
    g = lambda key, rl='honest': [raw[(cfg_name, rl, s)][key] for s in F.SEEDS]
    rows.append({'Detector': cfg_name, 'Method': 'Honest FedAvg (no attack)',
                 'Spoofing Recall': ms(g('recall')), 'F1': ms(g('f1')),
                 'BSR': ms(g('bsr')), 'Backdoor Lift': ms([0.0] * 3, sign=True),
                 'Attacker Detect': '---', 'Honest False-Flag': '---'})
    for rule, label in RULES:
        gg = lambda key: [raw[(cfg_name, rule, s)][key] for s in F.SEEDS]
        rows.append({'Detector': cfg_name, 'Method': label,
                     'Spoofing Recall': ms(gg('recall')), 'F1': ms(gg('f1')),
                     'BSR': ms(gg('bsr')), 'Backdoor Lift': ms(gg('lift'), sign=True),
                     'Attacker Detect': pct(gg('atk_detect')),
                     'Honest False-Flag': pct(gg('hon_flag'))})

tab = pd.DataFrame(rows)
pd.set_option('display.width', 250)
print('\nWeak vs strong federated detector, mean +/- std over 3 seeds\n')
print(tab.to_string(index=False))
tab.to_csv(F.RESULTS / 'strong_detector.csv', index=False)
print(f"\nwrote {F.RESULTS/'strong_detector.csv'}")

# ------------------------------------------------------------------- figure
labels = [r[1] for r in RULES]
xs = np.arange(len(labels))
w = 0.38
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.3))
for ax, key, ylab, title in ((ax1, 'lift', 'backdoor lift', 'Backdoor lift'),
                             (ax2, 'recall', 'spoofing recall', 'Retained utility')):
    for off, (cfg_name, col) in zip((-w/2, w/2),
                                    (('weak (paper)', '#B2B2B2'), ('strong', 'seagreen'))):
        m = [np.mean([raw[(cfg_name, r[0], s)][key] for s in F.SEEDS]) for r in RULES]
        e = [np.std([raw[(cfg_name, r[0], s)][key] for s in F.SEEDS]) for r in RULES]
        ax.bar(xs + off, m, w, yerr=e, capsize=3, color=col, label=cfg_name)
    ax.set_xticks(xs)
    ax.set_xticklabels([l.replace(' (', '\n(') for l in labels], rotation=18,
                       ha='right', fontsize=8)
    ax.set_ylabel(ylab); ax.set_title(title); ax.legend(fontsize=8.5)
ax1.axhline(0, color='black', lw=1.1)
for cfg_name, col in (('weak (paper)', '#B2B2B2'), ('strong', 'seagreen')):
    hv = np.mean([raw[(cfg_name, 'honest', s)]['recall'] for s in F.SEEDS])
    ax2.axhline(hv, color=col, ls=':', lw=1.3)
plt.tight_layout()
plt.savefig(F.RESULTS / 'fig_strong_detector.png', bbox_inches='tight')
print(f"wrote {F.RESULTS/'fig_strong_detector.png'}")
