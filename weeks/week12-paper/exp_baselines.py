# -*- coding: utf-8 -*-
"""
Reviewer comments 1, 4 and 5: compare against published baselines, and report
a full operating point rather than accuracy alone.

Runs every aggregation rule on the identical data split, attack, seeds and
metrics, so the comparison isolates the aggregation rule. Reports, per rule:
clean accuracy, spoofing recall, precision, F1, balanced accuracy, false-alarm
rate, raw BSR *and* backdoor lift (comment 4 asks that raw defended BSR always
appear next to lift), attacker detection rate, honest false-flag rate, mean
attacker/honest trust, and measured server-side time per round.

Run from this folder:  python exp_baselines.py
Outputs: results/baseline_comparison.csv, results/fig_baselines.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import fl_common as F
from fl_runner import run, ms, pct

plt.rcParams.update({'figure.dpi': 130, 'savefig.dpi': 150, 'font.size': 10,
                     'axes.grid': True, 'grid.alpha': 0.3, 'axes.spines.top': False,
                     'axes.spines.right': False, 'legend.frameon': False})

RULES = [
    ('fedavg',    'FedAvg',                      'Standard aggregation'),
    ('accweight', 'Accuracy-weighted FedAvg',    'The vulnerable target'),
    ('median',    'Coordinate-wise median',      'Robust aggregation'),
    ('trimmed',   'Trimmed mean',                'Byzantine-robust baseline'),
    ('krum',      'Krum',                        'Robust FL baseline'),
    ('multikrum', 'Multi-Krum',                  'Robust FL baseline'),
    ('fltrust',   'FLTrust',                     'Closest root-set baseline'),
    ('trust',     'Behavioral trust (ours)',     'Main contribution'),
    ('full',      'Trust + median (ours, D2)',   'Full proposed defense'),
]

print(f'baseline comparison | seeds {F.SEEDS} | {F.FL_ROUNDS} rounds | '
      f'{F.N_CLIENTS} clients, {F.N_ATTACK} compromised')
print(f'probe features ({len(F.PROBE_FEATS)}): {", ".join(F.PROBE_FEATS)}\n')

res, honest = {}, {}
for sd in F.SEEDS:
    clean_split = F.iid_split(sd)
    pois = F.poison(clean_split, sd)
    h = run(clean_split, sd, 'fedavg', attack=False, time_server=True)
    honest[sd] = h
    print(f"[seed {sd}] honest FedAvg   clean {h['clean']:.4f} recall {h['recall']:.4f} "
          f"BSR {h['bsr']:.4f}")
    for rule, label, _ in RULES:
        r = run(pois, sd, rule, attack=True, time_server=True)
        res[(rule, sd)] = r
        print(f"[seed {sd}] {label:<28} clean {r['clean']:.4f} recall {r['recall']:.4f} "
              f"BSR {r['bsr']:.4f} lift {r['bsr']-h['bsr']:+.4f}")
    print()

for sd in F.SEEDS:
    for rule, _, _ in RULES:
        res[(rule, sd)]['lift'] = res[(rule, sd)]['bsr'] - honest[sd]['bsr']
    honest[sd]['lift'] = 0.0

rows = [{
    'Method': 'Honest FedAvg (no attack)', 'Role': 'Reference (upper bound)',
    'Clean Accuracy':  ms([honest[s]['clean'] for s in F.SEEDS]),
    'Spoofing Recall': ms([honest[s]['recall'] for s in F.SEEDS]),
    'Precision':       ms([honest[s]['precision'] for s in F.SEEDS]),
    'F1':              ms([honest[s]['f1'] for s in F.SEEDS]),
    'Balanced Acc':    ms([honest[s]['balacc'] for s in F.SEEDS]),
    'False Alarm':     ms([honest[s]['far'] for s in F.SEEDS]),
    'BSR':             ms([honest[s]['bsr'] for s in F.SEEDS]),
    'Backdoor Lift':   ms([0.0 for _ in F.SEEDS], sign=True),
    'Attacker Detect': '---', 'Honest False-Flag': '---',
    'Attacker Trust': '---', 'Honest Trust': '---',
    'Server ms/round': ms([honest[s]['server_ms_per_round'] for s in F.SEEDS], nd=1),
}]
for rule, label, role in RULES:
    g = lambda k: [res[(rule, s)][k] for s in F.SEEDS]
    rows.append({
        'Method': label, 'Role': role,
        'Clean Accuracy':  ms(g('clean')),
        'Spoofing Recall': ms(g('recall')),
        'Precision':       ms(g('precision')),
        'F1':              ms(g('f1')),
        'Balanced Acc':    ms(g('balacc')),
        'False Alarm':     ms(g('far')),
        'BSR':             ms(g('bsr')),
        'Backdoor Lift':   ms(g('lift'), sign=True),
        'Attacker Detect': pct(g('atk_detect')),
        'Honest False-Flag': pct(g('hon_flag')),
        'Attacker Trust':  ms(g('atk_trust')),
        'Honest Trust':    ms(g('hon_trust')),
        'Server ms/round': ms(g('server_ms_per_round'), nd=1),
    })

tab = pd.DataFrame(rows)
pd.set_option('display.width', 250)
print('\nBaseline comparison, mean +/- std over 3 seeds (uniform trust = 0.100)\n')
print(tab[['Method', 'Clean Accuracy', 'Spoofing Recall', 'BSR', 'Backdoor Lift',
           'Attacker Detect', 'Honest False-Flag', 'Server ms/round']].to_string(index=False))
tab.to_csv(F.RESULTS / 'baseline_comparison.csv', index=False)
print(f"\nwrote {F.RESULTS/'baseline_comparison.csv'}")

np.savez(F.RESULTS / 'baseline_raw.npz',
         rules=np.array([r[0] for r in RULES]), seeds=np.array(F.SEEDS),
         lift=np.array([[res[(r[0], s)]['lift'] for s in F.SEEDS] for r in RULES]),
         bsr=np.array([[res[(r[0], s)]['bsr'] for s in F.SEEDS] for r in RULES]),
         recall=np.array([[res[(r[0], s)]['recall'] for s in F.SEEDS] for r in RULES]),
         honest_bsr=np.array([honest[s]['bsr'] for s in F.SEEDS]),
         honest_recall=np.array([honest[s]['recall'] for s in F.SEEDS]))

# ------------------------------------------------------------------- figure
labels = [r[1].replace(' (ours, D2)', '\n(ours, D2)').replace(' (ours)', '\n(ours)')
            .replace('Accuracy-weighted ', 'Acc-weighted\n').replace('Coordinate-wise ', 'Coord-wise\n')
          for r in RULES]
lift_m = [np.mean([res[(r[0], s)]['lift'] for s in F.SEEDS]) for r in RULES]
lift_s = [np.std([res[(r[0], s)]['lift'] for s in F.SEEDS]) for r in RULES]
rec_m = [np.mean([res[(r[0], s)]['recall'] for s in F.SEEDS]) for r in RULES]
hon_rec = np.mean([honest[s]['recall'] for s in F.SEEDS])

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.2, 7.0), sharex=True)
cols = ['#B2B2B2', '#E4572E', '#B2B2B2', '#B2B2B2', '#B2B2B2', '#B2B2B2',
        '#3C738B', '#7FA845', 'seagreen']
ax1.bar(labels, lift_m, yerr=lift_s, capsize=4, color=cols, width=.65)
ax1.axhline(0, color='black', lw=1.1)
ax1.set_ylabel('backdoor lift')
ax1.set_title('Backdoor lift by aggregation rule (lower is better; 0 = attacker gains nothing)')
for i, (m, s) in enumerate(zip(lift_m, lift_s)):
    tip = m + s if m >= 0 else m - s
    ax1.annotate(f'{m:+.3f}', (i, tip), textcoords='offset points',
                 xytext=(0, 6 if m >= 0 else -14), ha='center', fontsize=8.5)
ax2.bar(labels, rec_m, color=cols, width=.65)
ax2.axhline(hon_rec, color='black', ls=':', lw=1.3)
ax2.annotate(f'honest baseline ({hon_rec:.3f})', (len(labels) - 0.5, hon_rec),
             ha='right', va='bottom', fontsize=8.5)
ax2.set_ylabel('spoofing recall')
ax2.set_title('Utility retained (higher is better)')
plt.xticks(rotation=20, ha='right', fontsize=8.5)
plt.tight_layout()
plt.savefig(F.RESULTS / 'fig_baselines.png', bbox_inches='tight')
print(f"wrote {F.RESULTS/'fig_baselines.png'}")
