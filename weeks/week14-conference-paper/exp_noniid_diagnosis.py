# -*- coding: utf-8 -*-
"""
Diagnosis for the non-IID failure found by exp_noniid.py.

Under label skew the behavioural trust layer stops working: attacker trust
rises from 0.0001 (IID) to ~0.095-0.103 (essentially the uniform 0.100) and
attacker detection falls from 100% to 0%. The full defense still holds some
ground, but only because the coordinate-wise median is carrying it.

The suspected mechanism is the trust score's own robust scaling. Suspicion is
measured as the deficit below the cohort median probe recall in units of the
cohort MAD:

    s_i = max_f max(0, (m_f - d_i,f) / MAD_f)

Under IID the honest cohort is tight, MAD is small, and a backdoored client's
deficit is many MADs wide, easily clearing the dead-zone tau=2. Under label
skew honest clients legitimately disagree, MAD inflates, and the *same*
absolute deficit is now only a fraction of a MAD, so it never clears tau and
the gate never fires. The attacker hides inside the honest cohort's variance.

If that diagnosis is right, lowering tau should restore detection, at some
false-flag cost. This script tests exactly that: it sweeps tau at the two
skew levels where the base detector is still healthy enough to measure lift,
and reports whether detection is recoverable and what it costs. A negative
result here is also informative: it would mean the failure is not a threshold
choice but the scaling itself.

Run from this folder:  python exp_noniid_diagnosis.py
Outputs: results/noniid_tau_diagnosis.csv, results/fig_noniid_tau.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import fl_common as F
from fl_runner import run, ms, pct

plt.rcParams.update({'figure.dpi': 130, 'savefig.dpi': 150, 'font.size': 10,
                     'axes.grid': True, 'grid.alpha': 0.3, 'axes.spines.top': False,
                     'axes.spines.right': False, 'legend.frameon': False})

# only the skew levels where the honest detector still has headroom; at a=1 the
# base learner has already collapsed (honest BSR 0.90) and lift cannot rank rules
CONDITIONS = [('IID', None), ('Ratio skew a=10', 10.0), ('Ratio skew a=3', 3.0)]
TAUS = [0.5, 1.0, 2.0]

print(f'non-IID trust diagnosis | tau sweep {TAUS} | seeds {F.SEEDS}')
print('question: is the trust failure under skew a threshold problem or a scaling problem?\n')

rows, raw = [], {}
for cname, alpha in CONDITIONS:
    for sd in F.SEEDS:
        split = F.iid_split(sd) if alpha is None else F.ratio_skew_split(sd, alpha)
        pois = F.poison(split, sd)
        h = run(split, sd, 'fedavg', attack=False)
        raw[(cname, 'honest', sd)] = h
        for tau in TAUS:
            r = run(pois, sd, 'full', attack=True, tau=tau)
            r['lift'] = r['bsr'] - h['bsr']
            raw[(cname, tau, sd)] = r
            print(f"[{cname} | seed {sd} | tau={tau}] lift {r['lift']:+.4f} "
                  f"atk trust {r['atk_trust']:.4f} detect {100*r['atk_detect']:.0f}% "
                  f"honest false-flag {100*r['hon_flag']:.1f}%")
    print()

for cname, _ in CONDITIONS:
    for tau in TAUS:
        g = lambda k: [raw[(cname, tau, s)][k] for s in F.SEEDS]
        rows.append({'Condition': cname, 'Dead-zone tau': tau,
                     'Backdoor Lift': ms(g('lift'), sign=True),
                     'Attacker Trust': ms(g('atk_trust')),
                     'Attacker Detect': pct(g('atk_detect')),
                     'Honest False-Flag': pct(g('hon_flag')),
                     'Spoofing Recall': ms(g('recall'))})

tab = pd.DataFrame(rows)
pd.set_option('display.width', 250)
print('\nDead-zone sweep under label skew, mean +/- std over 3 seeds\n')
print(tab.to_string(index=False))
tab.to_csv(F.RESULTS / 'noniid_tau_diagnosis.csv', index=False)
print(f"\nwrote {F.RESULTS/'noniid_tau_diagnosis.csv'}")

# ------------------------------------------------------------------- figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.2))
cols = {'IID': 'seagreen', 'Ratio skew a=10': '#AD9C65', 'Ratio skew a=3': '#A4232B'}
for cname, _ in CONDITIONS:
    det = [100 * np.mean([raw[(cname, t, s)]['atk_detect'] for s in F.SEEDS]) for t in TAUS]
    ff = [100 * np.mean([raw[(cname, t, s)]['hon_flag'] for s in F.SEEDS]) for t in TAUS]
    ax1.plot(TAUS, det, marker='o', lw=1.9, color=cols[cname], label=cname)
    ax2.plot(TAUS, ff, marker='s', lw=1.9, color=cols[cname], label=cname)
ax1.set_xlabel('dead-zone tau'); ax1.set_ylabel('attacker detection rate (%)')
ax1.set_title('Can a lower threshold recover detection?'); ax1.legend(fontsize=8.5)
ax2.set_xlabel('dead-zone tau'); ax2.set_ylabel('honest client-rounds falsely flagged (%)')
ax2.set_title('What it costs in false flags'); ax2.legend(fontsize=8.5)
plt.tight_layout()
plt.savefig(F.RESULTS / 'fig_noniid_tau.png', bbox_inches='tight')
print(f"wrote {F.RESULTS/'fig_noniid_tau.png'}")
