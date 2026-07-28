# -*- coding: utf-8 -*-
"""
Redraw the two figures whose axis labels collided in the compiled PDF.

Both are rebuilt from the exported CSVs rather than by re-running the
experiments, so the plotted values are guaranteed identical to the tables and
this costs seconds instead of an hour.

Run from this folder:  python replot.py
Rewrites: results/fig_noniid.png, results/fig_detector_ceiling.png
"""
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import fl_common as F

plt.rcParams.update({'figure.dpi': 130, 'savefig.dpi': 150, 'font.size': 9,
                     'axes.grid': True, 'grid.alpha': 0.3, 'axes.spines.top': False,
                     'axes.spines.right': False, 'legend.frameon': False})


def val(s):
    """'0.1234 +/- 0.0056' -> (0.1234, 0.0056); '12.3%' -> (12.3, 0)."""
    s = str(s).strip()
    if s in ('---', 'nan', ''):
        return (np.nan, 0.0)
    if s.endswith('%'):
        return (float(s[:-1]), 0.0)
    p = s.split('+/-')
    return (float(p[0]), float(p[1]) if len(p) > 1 else 0.0)


# ------------------------------------------------------------------ non-IID
d = pd.read_csv(F.RESULTS / 'noniid_dirichlet.csv')
# short axis labels; the long names collided badly in the compiled figure
SHORT = {'IID': 'IID', 'Ratio skew a=10 (mild)': r'$\alpha$=10',
         'Ratio skew a=3 (moderate)': r'$\alpha$=3',
         'Ratio skew a=1 (severe)': r'$\alpha$=1'}
conds = [c for c in d['Condition'].unique()]
xs = np.arange(len(conds))
series = [('FedAvg', '#E4572E', '--', 's'),
          ('Coordinate-wise median', '#B2B2B2', '-.', 'v'),
          ('FLTrust', '#3C738B', ':', 'D'),
          ('Trust + median (ours)', 'seagreen', '-', 'o')]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.5))
for name, col, ls, mk in series:
    m, e = [], []
    for c in conds:
        row = d[(d['Condition'] == c) & (d['Method'] == name)].iloc[0]
        a, b = val(row['Backdoor Lift']); m.append(a); e.append(b)
    ax1.errorbar(xs, m, yerr=e, color=col, ls=ls, marker=mk, lw=1.7, ms=4,
                 capsize=3, label=name.replace(' (ours)', ' (ours)'))
ax1.axhline(0, color='black', lw=1.0)
ax1.set_xticks(xs); ax1.set_xticklabels([SHORT[c] for c in conds])
ax1.set_xlabel('client class-ratio skew')
ax1.set_ylabel('backdoor lift')
ax1.set_title('Backdoor lift under label skew', fontsize=9.5)
ax1.legend(fontsize=7.2, loc='upper left')

for name, col in (('FLTrust', '#3C738B'), ('Trust + median (ours)', 'seagreen')):
    m = []
    for c in conds:
        row = d[(d['Condition'] == c) & (d['Method'] == name)].iloc[0]
        m.append(val(row['Honest False-Flag'])[0])
    ax2.plot(xs, m, marker='o', lw=1.7, ms=4, color=col, label=name)
ax2.set_xticks(xs); ax2.set_xticklabels([SHORT[c] for c in conds])
ax2.set_xlabel('client class-ratio skew')
ax2.set_ylabel('honest rounds falsely flagged (%)')
ax2.set_title('False-flag cost of skew', fontsize=9.5)
ax2.legend(fontsize=7.2, loc='upper left')
plt.tight_layout()
plt.savefig(F.RESULTS / 'fig_noniid.png', bbox_inches='tight')
print('rewrote results/fig_noniid.png')

# ------------------------------------------------------------------ ceiling
c = pd.read_csv(F.RESULTS / 'detector_ceiling.csv')
SHORT_M = {
    'Logistic regression': 'Logistic\nregression',
    'MLP 64-32-16 (paper model)': 'MLP\n64-32-16',
    'MLP 256-128-64 (wider)': 'MLP\n256-128-64',
    'MLP 512-256-128-64 (deeper)': 'MLP\n512-...-64',
    'Random forest (400 trees)': 'Random\nforest',
    'Hist gradient boosting': 'Gradient\nboosting',
    'Federated honest FedAvg (paper baseline)': 'Federated\n(ours)',
}
names = [SHORT_M.get(m, m) for m in c['Model']]
rec = c['Spoofing Recall'].astype(float).values
f1 = c['F1'].astype(float).values
xs = np.arange(len(names))
# CSV order is: 3 MLPs, logistic regression, random forest, boosting, federated
cols = ['#B599CE'] * 3 + ['#B2B2B2'] * 3 + ['seagreen']
fig, ax = plt.subplots(figsize=(8.6, 3.4))
ax.bar(xs - 0.19, rec, 0.38, color=cols, label='spoofing recall')
ax.bar(xs + 0.19, f1, 0.38, color=cols, alpha=.5, label='F1')
ax.axhline(rec[-1], color='seagreen', ls=':', lw=1.3)
ax.annotate(f'federated baseline recall ({rec[-1]:.3f})', (len(names) - 0.55, rec[-1]),
            ha='right', va='bottom', fontsize=7.5, color='seagreen')
ax.set_xticks(xs); ax.set_xticklabels(names, fontsize=7.5)
ax.set_ylabel('score on held-out test set')
ax.set_ylim(0, 1.08)
ax.set_title("No centralized model is limited by the feature set's separability", fontsize=9.5)
ax.legend(fontsize=8, ncol=2, loc='upper left')
plt.tight_layout()
plt.savefig(F.RESULTS / 'fig_detector_ceiling.png', bbox_inches='tight')
print('rewrote results/fig_detector_ceiling.png')
