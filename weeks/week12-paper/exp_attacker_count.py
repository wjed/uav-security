# -*- coding: utf-8 -*-
"""
Follow-up to reviewer comments 1 and 5: if Multi-Krum already matches the
proposed defense, why is the proposed defense needed?

The baseline comparison (exp_baselines.py) shows Multi-Krum is genuinely
competitive under IID data: +0.0061 lift against our +0.0039 for trust alone,
which is inside the seed spread, and it is far cheaper. That is an honest
result and the paper reports it as such. But Krum and Multi-Krum need the
number of compromised clients f as an input, and a real coordinator does not
know f. Trimmed mean has the same dependence.

This experiment varies the true number of attackers from 1 to 4 while the
Byzantine-robust baselines stay configured for f=2, which is what a deployment
would have to guess. The proposed defense has no such parameter: it scores
every client on its own behavior and lets the cohort statistics decide.

Reported per attacker count: backdoor lift for each rule, plus attacker
detection and honest false-flag rates where the rule defines them.

Run from this folder:  python exp_attacker_count.py
Outputs: results/attacker_count.csv, results/fig_attacker_count.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import fl_common as F
from fl_runner import run, ms, pct

plt.rcParams.update({'figure.dpi': 130, 'savefig.dpi': 150, 'font.size': 10,
                     'axes.grid': True, 'grid.alpha': 0.3, 'axes.spines.top': False,
                     'axes.spines.right': False, 'legend.frameon': False})

COUNTS = [1, 2, 3, 4]
RULES = [('median', 'Coordinate-wise median'), ('trimmed', 'Trimmed mean (f=2)'),
         ('krum', 'Krum (f=2)'), ('multikrum', 'Multi-Krum (f=2)'),
         ('fltrust', 'FLTrust'), ('full', 'Trust + median (ours)')]

print(f'attacker-count sweep | true attackers {COUNTS} | robust baselines fixed at f=2')
print('the proposed defense has no f parameter\n')

ASSUMED_F = 2   # what the Byzantine-robust baselines are configured with

res, honest = {}, {}
for k in COUNTS:
    for sd in F.SEEDS:
        split = F.iid_split(sd)
        pois = F.poison(split, sd, n_attack=k)
        h = run(split, sd, 'fedavg', attack=False, n_attack=k)
        honest[(k, sd)] = h
        for rule, label in RULES:
            # n_attack is the ground truth; assumed_f is what the baseline was
            # told. They differ whenever k != 2, which is the whole point.
            r = run(pois, sd, rule, attack=True, n_attack=k, assumed_f=ASSUMED_F)
            r['lift'] = r['bsr'] - h['bsr']
            res[(k, rule, sd)] = r
        print(f"[attackers={k} seed {sd}] " + '  '.join(
            f"{lab.split(' (')[0][:9]} {res[(k,rl,sd)]['lift']:+.4f}"
            for rl, lab in RULES))
    print()

rows = []
for k in COUNTS:
    for rule, label in RULES:
        g = lambda key: [res[(k, rule, s)][key] for s in F.SEEDS]
        rows.append({'True attackers': k, 'Method': label,
                     'Clean Accuracy': ms(g('clean')),
                     'Spoofing Recall': ms(g('recall')),
                     'BSR': ms(g('bsr')),
                     'Backdoor Lift': ms(g('lift'), sign=True),
                     'Attacker Detect': pct(g('atk_detect')),
                     'Honest False-Flag': pct(g('hon_flag'))})

tab = pd.DataFrame(rows)
pd.set_option('display.width', 250)
print('\nAttacker-count sweep, mean +/- std over 3 seeds '
      '(Byzantine-robust baselines misconfigured whenever true f != 2)\n')
print(tab.to_string(index=False))
tab.to_csv(F.RESULTS / 'attacker_count.csv', index=False)
print(f"\nwrote {F.RESULTS/'attacker_count.csv'}")

# ------------------------------------------------------------------- figure
fig, ax = plt.subplots(figsize=(8.4, 4.6))
style = {'median': ('#B2B2B2', '-.', 'v'), 'trimmed': ('#8C8C8C', '--', 'x'),
         'krum': ('#AD9C65', ':', 'P'), 'multikrum': ('#450084', '--', 's'),
         'fltrust': ('#3C738B', ':', 'D'), 'full': ('seagreen', '-', 'o')}
for rule, label in RULES:
    c, ls, mk = style[rule]
    m = [np.mean([res[(k, rule, s)]['lift'] for s in F.SEEDS]) for k in COUNTS]
    sd_ = [np.std([res[(k, rule, s)]['lift'] for s in F.SEEDS]) for k in COUNTS]
    ax.errorbar(COUNTS, m, yerr=sd_, color=c, ls=ls, marker=mk, lw=1.9,
                capsize=4, label=label)
ax.axhline(0, color='black', lw=1.1)
ax.axvline(2, color='black', ls=':', lw=1.0, alpha=.5)
ax.annotate('baselines tuned here', (2, ax.get_ylim()[1]), fontsize=8.5,
            ha='center', va='top')
ax.set_xticks(COUNTS)
ax.set_xlabel('true number of compromised clients (of 10)')
ax.set_ylabel('backdoor lift')
ax.set_title('Robustness when the number of attackers is not known in advance')
ax.legend(fontsize=8.5)
plt.tight_layout()
plt.savefig(F.RESULTS / 'fig_attacker_count.png', bbox_inches='tight')
print(f"wrote {F.RESULTS/'fig_attacker_count.png'}")
