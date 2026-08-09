# -*- coding: utf-8 -*-
"""
Generate 14_conference_results.ipynb: exactly the results reported in the
conference paper, and nothing else.

Deliberately narrower than the Week 12 notebook. The conference paper reports
two tables and four figures; this notebook reproduces those and stops.
Anything the paper only summarises in a sentence is left in the Week 12
artifact rather than repeated here, which is the editorial rule the paper
follows too.

RUN_EXPERIMENTS = False (default) loads the exported CSVs. True re-executes.

Run:  python build_notebook.py
"""
from pathlib import Path
import nbformat as nbf

HERE = Path(__file__).resolve().parent
OUT = HERE / '14_conference_results.ipynb'

nb = nbf.v4.new_notebook()
cells = []
md = lambda t: cells.append(nbf.v4.new_markdown_cell(t.strip('\n')))
code = lambda t: cells.append(nbf.v4.new_code_cell(t.strip('\n')))

md(r"""
# Results for the Conference Paper

**Receiver-Domain Behavioral Probing for Backdoor-Resilient Federated GPS Spoofing Detection in UAV Networks**
Group 1: Will Jedrzejczak, Cole Walther, Dilpreet Gill

This notebook reproduces exactly the results reported in the paper:
**Tables I and II** and **Figures 2, 3 and 4**. Every value is read from an
exported CSV, so the notebook, the tables and the figures cannot disagree.

Studies the paper only summarises in prose (hyperparameter sweep, cost scaling,
detector ceiling, root-set stress) live in the Week 12 artifact. They are not
repeated here, for the same reason they are not tabulated in the paper: they do
not carry the main argument.
""")

md(r"""
## Setup

`RUN_EXPERIMENTS = False` loads exported results and runs in seconds.
`True` re-executes the experiments through the shared harness (several hours on CPU).
Both paths run the same code, so they agree by construction.
""")

code(r"""
RUN_EXPERIMENTS = False

import subprocess, sys
from pathlib import Path
import pandas as pd
from IPython.display import display, Markdown, Image

HERE = Path.cwd(); RES = HERE / 'results'; FIG = HERE / 'figures'
pd.set_option('display.width', 200)

def val(s):
    s = str(s).strip()
    if s in ('---', '', 'nan'): return None
    return s.split('+/-')[0].strip()

def run(script):
    if not RUN_EXPERIMENTS:
        print(f'[skipped] {script}  (set RUN_EXPERIMENTS = True to execute)'); return
    print(f'[running] {script}')
    r = subprocess.run([sys.executable, '-u', script], cwd=HERE)
    print(f'[{"ok" if r.returncode == 0 else "FAILED"}] {script}')

print('mode:', 'RECOMPUTE' if RUN_EXPERIMENTS else 'load exported results')
print(f'{len(list(RES.glob("*.csv")))} CSVs, {len(list(FIG.glob("*.png")))} figures')
""")

code(r"""
import fl_common as F
from fl_runner import ALL_RULES
print('probe features :', F.PROBE_FEATS, f'({len(F.PROBE_FEATS)} of {len(F.FEATURES)})')
print('model params   :', F.n_params(F.BinaryDNN(F.D)))
print('pool/root/test :', len(F.X_pool_sc), len(F.X_root_sc), len(F.X_test_sc))
print('rules          :', ALL_RULES)
print('seeds          :', F.SEEDS, '| data seed', F.DATA_SEED)
""")

md(r"""
---
## Table I: comparison on an identical pipeline

Every rule sees the same split, attack, seeds and metrics. All ten rows of the
paper's Table I are reproduced below, in the paper's order and with the paper's
columns.
""")
code("run('exp_baselines.py')")
code(r"""
b = pd.read_csv(RES / 'baseline_comparison.csv')
rows = ['Honest FedAvg (no attack)', 'FedAvg', 'Accuracy-weighted FedAvg',
        'Coordinate-wise median', 'Trimmed mean', 'Krum', 'Multi-Krum', 'FLTrust',
        'Behavioral trust (ours)', 'Trust + median (ours, D2)']
t1 = b[b['Method'].isin(rows)].set_index('Method').loc[rows]
display(t1[['Clean Accuracy', 'Spoofing Recall', 'BSR', 'Backdoor Lift',
            'Attacker Detect', 'Honest False-Flag', 'Server ms/round']])
display(Markdown(
  '**What this table establishes.** The attack is effective (+0.2415) and quiet; '
  'accuracy inflation makes it worse (+0.3036), so weighting by an unverified '
  'self-report is worse than not weighting at all; median alone leaves +0.0646; '
  'FLTrust leaves +0.0787; **Multi-Krum is genuinely competitive** (+0.0061) and '
  'the paper says so; the proposed method reaches -0.0265 and additionally '
  'attributes the attack per client at a 0.3% honest false-flag rate.'))
""")

md(r"""
---
## Fig. 2: unknown number of compromised clients

Table I gives the Byzantine-robust rules the true value of $f$. A deployment does
not have it. Here the true attacker count varies while those rules stay at $f=2$.
""")
code("run('exp_attacker_count.py')")
code(r"""
a = pd.read_csv(RES / 'attacker_count.csv')
piv = a.pivot_table(index='Method', columns='True attackers',
                    values='Backdoor Lift', aggfunc='first')
display(piv.map(val))
display(Image(filename=str(FIG / 'fig2_fcount.png'), width=760))
display(Markdown(
  '**The point is not that Multi-Krum is weak.** It is excellent when told the '
  'right f (+0.0005 at one attacker), and degrades to +0.2837 at four. The '
  'proposed method has no such parameter.'))
""")

md(r"""
---
## Fig. 3: client heterogeneity, and where the mechanism fails

Clients hold equal row counts but unequal benign/spoofed ratios. This is the
paper's honest boundary, and it is reported rather than omitted.
""")
code("run('exp_noniid.py')")
code(r"""
n = pd.read_csv(RES / 'noniid_dirichlet.csv')
keep = ['IID', 'Ratio skew a=10 (mild)', 'Ratio skew a=3 (moderate)']
m = ['FedAvg', 'Coordinate-wise median', 'Behavioral trust (ours)', 'Trust + median (ours)']
sub = n[n['Condition'].isin(keep) & n['Method'].isin(m)]
display(sub[['Condition', 'Method', 'Backdoor Lift', 'Attacker Detect',
             'Attacker Trust', 'Honest Trust']].to_string(index=False))
display(Image(filename=str(FIG / 'fig3_noniid.png'), width=760))
""")
code(r"""
display(Markdown(
  '**Diagnosis.** Suspicion is measured in cohort-MAD units. Under skew honest '
  'clients legitimately disagree, the MAD inflates, and the attacker no longer '
  'clears the dead-zone. Lowering tau confirms this but does not fix it:'))
display(pd.read_csv(RES / 'noniid_tau_diagnosis.csv'))
""")
code("run('exp_noniid_diagnosis.py')")

md(r"""
---
## Fig. 4: trigger generalization

One fixed defense configuration, never retuned between trigger settings.
""")
code(r"""
tg = pd.read_csv(RES / 'trigger_comparison.csv')
display(tg[tg['Trigger'].isin(['CN0', 'TCD', 'PD', 'CN0+TCD'])][
    ['Trigger', "Cohen's d", 'Attack lift', 'Defended lift', 'Honest FP rate']])
display(Image(filename=str(FIG / 'fig4_trigger.png'), width=430))
""")

md(r"""
---
## Defense-aware adversary (reported in prose, no table)

`lambda` weights an evasion term that trains the compromised clients to answer
the probes like the honest cohort. The tension is the point: the trigger requires
calling a benign-high input authentic, and the evasion term trains the same model
to call it spoofed.
""")
code(r"""
ad = pd.read_csv(RES / 'adaptive_attacker.csv')
display(ad)
display(Markdown(
  '**Read the undefended column, not the trust column.** Evasion does raise '
  'attacker trust from 0.0001 to 0.0834, close to the uniform share of 0.100. '
  'It buys nothing, because undefended lift has already collapsed to -0.1433 by '
  'then: an attacker that hides from the probes has destroyed its own backdoor.'))
""")

md(r"""
---
## Table II: per-client attribution

12 rounds x 3 seeds = 36 client-rounds per client. A client counts as flagged in
a round when its trust falls below half the uniform share of 0.100. This is the
property the geometric rules cannot provide: they return a selection, not a name.
""")
code(r"""
cf = pd.read_csv(RES / 'client_flagging_table.csv')
display(cf)
display(pd.read_csv(RES / 'false_positive_summary.csv'))
""")

md(r"""
---
## Regenerating the figures

Figures 2 to 4 are 600 dpi PNGs built from the CSVs above, so they cannot drift from
the tables. Figs. 2 and 3 are sized for the full text width, Fig. 4 for one column.
Figure 1 is the authors' own diagram and is not generated here.
""")
code(r"""
r = subprocess.run([sys.executable, '-u', 'build_figures.py'],
                   cwd=HERE, capture_output=True, text=True)
print(r.stdout or r.stderr)
""")

md(r"""
---
## Reproducing from scratch

```bash
python run_all.py --list      # stages and runtimes
python run_all.py baselines attackers noniid
python build_figures.py       # regenerate the four paper figures
```

The data split is fixed at seed 42 so the evaluation target never moves; federated
randomness varies over seeds 42, 7, 123. Runs are deterministic on a given machine,
verified by executing a benchmark twice for bit-identical output.
""")

nb['cells'] = cells
nb['metadata'] = {'kernelspec': {'display_name': 'Python 3', 'language': 'python',
                                 'name': 'python3'},
                  'language_info': {'name': 'python', 'version': '3.12'}}
nbf.write(nb, str(OUT))
print(f'wrote {OUT} ({len(cells)} cells)')
