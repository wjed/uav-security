# -*- coding: utf-8 -*-
"""
Reviewer comment 3: the claim that both layers are necessary is not supported,
because trust-only already reaches roughly zero lift under the easy condition.

The reviewer's own prescription is followed: construct conditions in which the
trust score is *imperfect*, then check whether coordinate-wise median limits
the damage that leaks through. If it does not, the honest conclusion is that
the median is a cheap backstop rather than a demonstrated necessity, and the
paper should say so.

Conditions (each degrades trust scoring in a different way):
  root-600     the root set is cut from 6,000 to 600 rows, so probe recall is
               estimated from far fewer samples and the cohort MAD is noisier
  root-noisy   30% of root labels are flipped, so the coordinator's own
               reference is partially wrong
  boost-10     model-replacement scaling raised from 3 to 10, so anything the
               trust gate fails to suppress does far more damage
  dirichlet    label-skew non-IID at alpha=0.5, where honest clients naturally
               deviate from the cohort median
  tau-6        the dead-zone is widened to 6.0, deliberately de-tuning the gate
               so attackers stay above the flagging threshold

Run from this folder:  python exp_median_stress.py
Outputs: results/median_necessity.csv, results/fig_median_necessity.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import fl_common as F
from fl_runner import run, ms, pct

plt.rcParams.update({'figure.dpi': 130, 'savefig.dpi': 150, 'font.size': 10,
                     'axes.grid': True, 'grid.alpha': 0.3, 'axes.spines.top': False,
                     'axes.spines.right': False, 'legend.frameon': False})


def noisy_root(seed, frac=0.30):
    rng = np.random.default_rng(seed + 991)
    yr = F.y_root.copy()
    idx = rng.choice(len(yr), size=int(len(yr) * frac), replace=False)
    yr[idx] = 1 - yr[idx]
    return F.X_root_sc, yr


def small_root(n=600):
    return F.X_root_sc[:n], F.y_root[:n]


CONDITIONS = [
    ('baseline (D2, IID)', dict()),
    ('root 6,000 -> 600',  dict(small=True)),
    ('30% root labels flipped', dict(noisy=True)),
    ('scaling 3 -> 10',     dict(boost=10.0)),
    ('non-IID Dirichlet a=0.5', dict(alpha=0.5)),
    ('dead-zone tau 2 -> 6', dict(tau=6.0)),
]

print(f'median-necessity stress test | seeds {F.SEEDS}')
rows, raw = [], {}

for cname, cfg in CONDITIONS:
    for sd in F.SEEDS:
        split = (F.dirichlet_split(sd, cfg['alpha']) if 'alpha' in cfg
                 else F.iid_split(sd))
        pois = F.poison(split, sd)
        kw = {}
        if cfg.get('small'):
            kw['root_X'], kw['root_y'] = small_root()
        if cfg.get('noisy'):
            kw['root_X'], kw['root_y'] = noisy_root(sd)
        if 'boost' in cfg:
            kw['boost'] = cfg['boost']
        if 'tau' in cfg:
            kw['tau'] = cfg['tau']

        h = run(split, sd, 'fedavg', attack=False)
        und = run(pois, sd, 'fedavg', attack=True,
                  boost=kw.get('boost', F.BOOST))
        t_only = run(pois, sd, 'trust', attack=True, **kw)
        t_full = run(pois, sd, 'full', attack=True, **kw)
        for r in (und, t_only, t_full):
            r['lift'] = r['bsr'] - h['bsr']
        raw[(cname, sd)] = (und, t_only, t_full)
        print(f"[{cname} | seed {sd}] undef {und['lift']:+.4f} | "
              f"trust-only {t_only['lift']:+.4f} | full {t_full['lift']:+.4f} | "
              f"atk trust {t_full['atk_trust']:.4f} honflag {100*t_full['hon_flag']:.1f}%")

    g = lambda i, k: [raw[(cname, s)][i][k] for s in F.SEEDS]
    delta = [raw[(cname, s)][1]['lift'] - raw[(cname, s)][2]['lift'] for s in F.SEEDS]
    rows.append({
        'Condition': cname,
        'Undefended Lift': ms(g(0, 'lift'), sign=True),
        'Trust-only Lift': ms(g(1, 'lift'), sign=True),
        'Full (trust+median) Lift': ms(g(2, 'lift'), sign=True),
        'Median benefit (trust-only minus full)': ms(delta, sign=True),
        'Attacker Trust': ms(g(2, 'atk_trust')),
        'Attacker Detect': pct(g(2, 'atk_detect')),
        'Honest False-Flag': pct(g(2, 'hon_flag')),
    })
    print()

tab = pd.DataFrame(rows)
pd.set_option('display.width', 250)
print('\nMedian-necessity stress test, mean +/- std over 3 seeds\n')
print(tab.to_string(index=False))
tab.to_csv(F.RESULTS / 'median_necessity.csv', index=False)
print(f"\nwrote {F.RESULTS/'median_necessity.csv'}")

# ------------------------------------------------------------------- figure
names = [c[0] for c in CONDITIONS]
xs = np.arange(len(names))
t_m = [np.mean([raw[(c, s)][1]['lift'] for s in F.SEEDS]) for c in names]
t_s = [np.std([raw[(c, s)][1]['lift'] for s in F.SEEDS]) for c in names]
f_m = [np.mean([raw[(c, s)][2]['lift'] for s in F.SEEDS]) for c in names]
f_s = [np.std([raw[(c, s)][2]['lift'] for s in F.SEEDS]) for c in names]
w = 0.38
fig, ax = plt.subplots(figsize=(9.6, 4.4))
ax.bar(xs - w/2, t_m, w, yerr=t_s, capsize=4, color='#7FA845', label='trust only')
ax.bar(xs + w/2, f_m, w, yerr=f_s, capsize=4, color='seagreen', label='trust + median (full)')
ax.axhline(0, color='black', lw=1.1)
ax.set_xticks(xs); ax.set_xticklabels(names, rotation=18, ha='right', fontsize=8.5)
ax.set_ylabel('backdoor lift')
ax.set_title('Does the median layer help when trust scoring is degraded?')
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(F.RESULTS / 'fig_median_necessity.png', bbox_inches='tight')
print(f"wrote {F.RESULTS/'fig_median_necessity.png'}")
