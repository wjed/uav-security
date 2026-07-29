# -*- coding: utf-8 -*-
"""
Generate 12_revision_experiments.ipynb, the notebook deliverable for the
review response.

The notebook is generated rather than hand-written so its code cells stay in
sync with the experiment scripts they call. It has two modes, controlled by one
flag in the first code cell:

  RUN_EXPERIMENTS = False   load the exported CSVs and display every table and
                            figure. Executes in seconds. This is the default,
                            so the notebook can be opened and read.
  RUN_EXPERIMENTS = True    re-execute the experiments from scratch through the
                            shared harness. Hours, and reproduces the CSVs.

Run:  python build_revision_notebook.py
Output: 12_revision_experiments.ipynb
"""
from pathlib import Path
import nbformat as nbf

HERE = Path(__file__).resolve().parent
OUT = HERE / '12_revision_experiments.ipynb'

nb = nbf.v4.new_notebook()
cells = []


def md(t):
    cells.append(nbf.v4.new_markdown_cell(t.strip('\n')))


def code(t):
    cells.append(nbf.v4.new_code_cell(t.strip('\n')))


# ---------------------------------------------------------------- front matter
md(r"""
# Week 12 Revision: Responding to the July 28 Review

**Trigger-Agnostic Behavioral Trust for Backdoor-Resilient Federated GPS Spoofing Detection**

Group 1: Will Jedrzejczak, Cole Walther, Dilpreet Gill
IT 445 Capstone, Summer 2026 · Advisor: Dr. Khalid Hasan

---

This notebook is the code deliverable for the review response. It reproduces every
table and figure added or changed in the revision, organised by the reviewer comment
that prompted it.

**Two things worth knowing before reading.**

The revision found two claims in our previous draft that were **wrong**, not merely
imprecise:

1. We had blamed a weak detector on the dataset. Section 5 shows it is our federated
   configuration: the same architecture trained centrally reaches 0.907 recall against
   0.529 federated.
2. Our 1.1% overhead figure used a denominator that summed every client's training
   time. Section 7 recomputes it as 3.40% on a parallel round.

And the experiment the review called *"probably the single most valuable"* found a real
failure in our defense. Section 3 reports it: under uneven client data the behavioral
trust layer stops firing entirely.

All experiments run through one shared harness (`fl_common.py`, `fl_runner.py`) so no
two of them can disagree about the data split, the model, the attack or a metric.
""")

md(r"""
## 0. Setup

`RUN_EXPERIMENTS` controls what this notebook does.

- `False` (default): load the exported CSVs and display everything. Seconds.
- `True`: re-execute every experiment through the harness. Several hours on CPU.

The CSVs in `results/` were produced by exactly the code the `True` path runs, so the
two modes agree by construction. Runs are deterministic given the fixed data seed; we
verified this by executing the FLTrust benchmark twice and getting bit-identical output.
""")

code(r"""
RUN_EXPERIMENTS = False      # set True to recompute everything from scratch

import subprocess, sys
from pathlib import Path
import pandas as pd
from IPython.display import Image, display, Markdown

HERE = Path.cwd()
RES = HERE / 'results'
pd.set_option('display.width', 220)
pd.set_option('display.max_colwidth', 60)


def show(csv, cols=None, caption=None):
    "Display an exported results table."
    df = pd.read_csv(RES / csv)
    if cols:
        df = df[cols]
    if caption:
        display(Markdown(f'**{caption}**'))
    display(df)
    return df


def fig(png, width=880):
    display(Image(filename=str(RES / png), width=width))


def run(script):
    "Execute an experiment script, streaming its output."
    if not RUN_EXPERIMENTS:
        print(f'[skipped] {script} - set RUN_EXPERIMENTS = True to execute')
        return
    print(f'[running] {script} ...')
    r = subprocess.run([sys.executable, '-u', script], cwd=HERE)
    print(f'[{"ok" if r.returncode == 0 else "FAILED"}] {script}')


print('mode:', 'RECOMPUTE' if RUN_EXPERIMENTS else 'load exported results')
print('results dir:', RES, '|', len(list(RES.glob('*.csv'))), 'CSVs present')
""")

md(r"""
### The shared harness

Everything below imports from two modules, so the setup is defined once.

- **`fl_common.py`** — the fixed preprocessing and split (seed 42), the probe
  construction, the model, IID and skewed partitioners, the CN0 poisoning attack, the
  nine aggregation rules, and one metric function.
- **`fl_runner.py`** — one federated run under any rule. Takes `n_attack` (the true
  number of compromised clients) separately from `assumed_f` (what the Byzantine-robust
  baselines are *told*), which is what makes Section 6 possible.
""")

code(r"""
import fl_common as F
from fl_runner import ALL_RULES

print('features         :', F.FEATURES)
print('probe features   :', F.PROBE_FEATS, f'({len(F.PROBE_FEATS)} of {len(F.FEATURES)})')
print('model parameters :', F.n_params(F.BinaryDNN(F.D)))
print('client pool/root/test:', len(F.X_pool_sc), '/', len(F.X_root_sc), '/', len(F.X_test_sc))
print('aggregation rules:', ALL_RULES)
print('seeds            :', F.SEEDS, '| data seed fixed at', F.DATA_SEED)
""")

# ---------------------------------------------------------------- comments 1 & 5
md(r"""
---
## 1. Comments 1 and 5 — Comparison against published baselines

> *"Include direct baseline comparisons with at least: FLTrust, coordinate-wise median,
> trimmed mean, Krum or Multi-Krum, server-validated accuracy weighting."*

All five, plus FedAvg, implemented and run on the identical split, attack, seeds and
metrics. Nothing is quoted from another paper.

**FLTrust** follows Cao et al. (NDSS 2021) as described in the paper the advisor
attached: the server trains the current global model on its own root set to get an
update $g_0$, scores each client by $\mathrm{TS}_i = \mathrm{ReLU}(\cos(g_i, g_0))$, and
rescales every client update to $\lVert g_0 \rVert$ before a trust-weighted mean.
""")
code("run('exp_baselines.py')")
code(r"""
b = show('baseline_comparison.csv',
         ['Method', 'Clean Accuracy', 'Spoofing Recall', 'BSR', 'Backdoor Lift',
          'Attacker Detect', 'Honest False-Flag', 'Server ms/round'],
         'All nine aggregation rules, identical pipeline (mean +/- std over 3 seeds)')
fig('fig_baselines.png')
""")
md(r"""
**The result that does not favour us, reported rather than omitted.**

Multi-Krum reaches **+0.0061** lift against our behavioral trust at **+0.0039**. At three
seeds those are statistically indistinguishable, and Multi-Krum is ~27x cheaper on server
time. We therefore removed any claim that a behavioral probe is *necessary* to stop this
attack in this setting, because this table would contradict it.

What survives as a genuine distinction is tested in Section 6: the Byzantine-robust rules
must be told how many clients are compromised, and we must not.

FLTrust removes about two-thirds of the attack (+0.0787) but leaves a clear residual, and
its clean accuracy and recall fall *below* the honest baseline because rescaling every
update to the server norm throttles honest clients too. It is also the most expensive rule
tested at 204 ms/round, since it trains a server model every round.
""")

# ---------------------------------------------------------------- comment 2
md(r"""
---
## 2. Comment 2 — Non-IID client data

> *"This is probably the single most valuable additional experiment for improving our
> paper's acceptance chances."*

It was, and it found a failure in our defense.

### 2.1 The requested partitioning did not produce a usable experiment

We first ran Dirichlet partitioning at $\alpha \in \{0.1, 0.5, 1.0\}$ exactly as asked.
Dirichlet mass concentrates, so most clients end up holding a single class. The federated
detector then never learns the spoofed class at all and the *honest* baseline collapses,
which leaves backdoor lift with no headroom to measure. At $\alpha = 0.1$ one compromised
client drew **zero** spoofed rows and could not mount the attack.

This run is kept as a negative result rather than used to rank defenses.
""")
code(r"""
show('noniid_unconstrained_collapse.csv',
     ['Condition', 'Method', 'Spoofing Recall', 'BSR', 'Backdoor Lift'],
     'Unconstrained Dirichlet: the honest baseline itself collapses (negative result)')
display(Markdown('Note the honest rows: recall falls to **0.0737** at a=0.5 and '
                 '**0.0011** at a=0.1, with BSR saturating at 1.000. '
                 'Lift is measured against that baseline, so nothing can be measured.'))
show('noniid_unconstrained_profile.csv', caption='Realised partitions, showing why')
""")
md(r"""
### 2.2 The partitioning we used instead

The review's **second** listed option: *unequal benign/spoofed class ratios across
clients*. Every client keeps an equal number of rows but a different class ratio, drawn
from $\mathrm{Dir}(\alpha)$ and clipped so both classes remain present. Smaller $\alpha$
widens the spread around the global 0.40.

We validated that the honest detector survives each level **before** running the
comparison, which is the check the first attempt failed.
""")
code(r"""
for a in (10.0, 3.0):
    cl = F.ratio_skew_split(42, a)
    d = F.describe_split(cl)
    print(f'alpha={a:>5}: spoofed fraction {min(d["spoof_frac"]):.3f} - {max(d["spoof_frac"]):.3f}'
          f'  | rows {min(d["rows"])}-{max(d["rows"])}'
          f'  | attacker spoofed rows {d["atk_spoof_rows"]}')
print('\nIID reference: every client at 0.400 spoofed, 9690 rows')
""")
code("run('exp_noniid.py')")
code(r"""
n = show('noniid_dirichlet.csv',
         ['Condition', 'Method', 'Clean Accuracy', 'Spoofing Recall', 'BSR', 'Backdoor Lift',
          'Attacker Detect', 'Honest False-Flag', 'Attacker Trust', 'Honest Trust'],
         'Non-IID sweep, reporting all seven quantities the review requested')
fig('fig_noniid.png')
""")
md(r"""
### 2.3 The finding

**The behavioral trust layer does not survive label skew.**

| | Evenly split | Mild skew | Moderate skew |
|---|---|---|---|
| Attacker trust (fair share 0.100) | **0.0001** | 0.0942 | 0.1023 |
| Compromised clients detected | **100%** | 8.3% | **0%** |
| Lift, trust layer alone | +0.0039 | **+0.2374** | **+0.2482** |
| Lift, full defense | −0.0265 | +0.0647 | +0.1002 |
| Lift, no defense at all | +0.2415 | +0.2583 | +0.2455 |

Trust-only under skew is statistically indistinguishable from having no defense. The full
defense holds up better, but its numbers track coordinate-wise median alone
(+0.0710, +0.1046) almost exactly, which means **the median layer is carrying it**.

> **Read the honest false-flag column carefully.** The 0.0% at moderate skew is *not* an
> improvement. The gate has stopped firing at all, so it flags nobody, attacker or honest
> client alike.

### 2.4 Why, tested rather than asserted

Suspicion is a deficit below the cohort median measured in cohort-MAD units. Under IID the
honest cohort is tight, so a backdoored client's deficit spans many MADs and clears the
dead-zone easily. Under skew honest clients legitimately disagree, the MAD inflates, and
the same absolute deficit becomes a fraction of one MAD. The attacker hides inside the
honest cohort's own variance.

If that diagnosis is right, lowering the dead-zone should partially recover detection.
""")
code("run('exp_noniid_diagnosis.py')")
code(r"""
show('noniid_tau_diagnosis.csv', caption='Dead-zone sweep: is this a threshold problem?')
fig('fig_noniid_tau.png', width=820)
""")
md(r"""
Detection partially recovers (8.3% → 38.9% at mild skew), which **confirms the mechanism**.
But it never approaches the IID figure and it costs 6–12% of honest client-rounds in false
flags, and under IID the same change is pure loss. So the limitation is the robust scaling
itself, not the threshold value. The fix would be a suspicion statistic normalised per
client rather than against a global cohort spread; that is untested and is the clearest
next step this work leaves open.
""")

# ---------------------------------------------------------------- comment 3
md(r"""
---
## 3. Comment 3 — The two-layer claim

> *"Revise the claim to: behavioral trust provides most of the observed protection ...
> while coordinate-wise median is retained as a robust aggregation backstop."*

Accepted and applied. Trust-only (+0.0039) and the full defense (−0.0265) are not
separated at three seeds, so the previous claim was not supported.

The review then asked for the right experiment: degrade the trust score until it is
imperfect and check whether the median limits the damage.
""")
code("run('exp_median_stress.py')")
code(r"""
show('median_necessity.csv', caption='Five ways to degrade trust scoring')
fig('fig_median_necessity.png', width=820)
""")
md(r"""
Under mild degradation the median contributes +0.017 to +0.033, the same size as the seed
spread, so we do not claim it as individually resolved there. **The decisive case is the
one the reviewer predicted:** under the label skew of Section 2, trust-only leaves +0.2374
and +0.2482 while the full defense leaves +0.0647 and +0.1002. The median removes **0.173**
and **0.148** of lift, an order of magnitude more than under IID.

One condition did not behave as intended and is reported as such: raising model-replacement
scaling from γ=3 to γ=10 **weakens** the attack (undefended lift −0.5888), because an update
scaled that hard destroys the global model rather than steering it.
""")

# ---------------------------------------------------------------- comment 4
md(r"""
---
## 4. Comment 4 — The base detector

> *"Do not claim that the system is secure simply because backdoor lift reaches zero."*

Two separate things were needed: separate the claims, and find out whether a stronger
classifier is even available.

### 4.1 The centralized ceiling

Several models trained on the entire 114,000-row pool with no federation, no attack and no
privacy constraint. This upper-bounds anything the federated system could reach.
""")
code("run('exp_detector.py')")
code(r"""
show('detector_ceiling.csv',
     ['Model', 'Clean Accuracy', 'Spoofing Recall', 'Precision', 'F1',
      'Balanced Acc', 'False Alarm Rate', 'TP', 'FN', 'FP', 'TN', 'Triggered BSR'],
     'Centralized ceiling. Final row is the federated detector used in the paper.')
fig('fig_detector_ceiling.png', width=760)
""")
md(r"""
**This corrects our previous draft.** We had attributed the weak detector to limited
separability in the feature set. That is wrong. The *same* architecture reaches **0.9073**
recall trained centrally, and gradient boosting reaches **0.9929**, against **0.5292**
federated. The features are separable; twelve rounds of three local epochs on a small MLP
underfits.

A short search confirms a stronger federated configuration is reachable (30 rounds with
256-128-64 gives 0.851 honest recall). We did **not** re-run the full evaluation there, so
we make no claim that the defense conclusions transfer to it.

### 4.2 The claims, now separated

- **Supported:** the defense removes the attacker-induced *increase* in BSR.
- **Not supported, and not claimed:** that the detector reliably catches triggered
  spoofing. At our operating point an honest model already lets **63.7%** of
  trigger-bearing samples through, so driving lift to zero restores that baseline rather
  than making the system safe.

Raw BSR now appears beside lift in every table, and the full operating point is reported.
""")
code(r"""
b = pd.read_csv(RES / 'baseline_comparison.csv')
display(Markdown('**Full operating point (from `baseline_comparison.csv`)**'))
display(b[['Method', 'Precision', 'Spoofing Recall', 'F1', 'Balanced Acc',
           'False Alarm', 'BSR', 'Backdoor Lift']])
""")

# ---------------------------------------------------------------- comment 6
md(r"""
---
## 5. Comment 6 — Overhead, recomputed

> *"The denominator looks like to come from a sequential simulation ... Do not claim
> large-fleet scalability without testing it."*

Both points were correct.
""")
code("run('exp_overhead.py')")
code(r"""
show('overhead_analysis.csv', caption='Both denominators')
show('overhead_scaling.csv', caption='Scaling in clients, root-set size and probe count')
fig('fig_overhead.png', width=900)
""")
md(r"""
We withdraw the 1.1% figure. On a parallel round, bounded by the slowest client rather than
the sum of all clients, the same measurement is **3.40%**.

We also withdraw the large-fleet scalability claim, because the measurement contradicts it:
server cost is linear in the number of clients while a parallel round is roughly constant,
so the overhead *fraction* climbs from 5.6% at five clients to **34.9% at forty**. A large
fleet would need the probe subsampled or batched across rounds; neither is tested and
neither is claimed.

FLTrust on the same basis costs 168.3 ms/round (16.9% of a parallel round), roughly five
times ours, because it trains a server model every round.
""")

# ---------------------------------------------------------------- comment 1 follow-up
md(r"""
---
## 6. Why the method is still needed — an unknown attacker count

Section 1 showed Multi-Krum matching us under IID. That comparison gives it an advantage a
deployment cannot: it is *told* how many clients are compromised. Trimmed mean and Krum
need the same input; our method has no such parameter.

Here the true attacker count varies from 1 to 4 while the Byzantine-robust rules stay
configured for `assumed_f = 2`, which is what a coordinator would have to guess.
""")
code("run('exp_attacker_count.py')")
code(r"""
show('attacker_count.csv',
     ['True attackers', 'Method', 'Spoofing Recall', 'BSR', 'Backdoor Lift',
      'Attacker Detect', 'Honest False-Flag'],
     'Backdoor lift as the true attacker count varies (baselines fixed at f=2)')
fig('fig_attacker_count.png', width=760)
""")
md(r"""
| True attackers | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Multi-Krum (told 2) | +0.0005 | +0.0061 | +0.1609 | **+0.2837** |
| Trimmed mean (told 2) | +0.0380 | +0.0787 | +0.2114 | **+0.2992** |
| **Ours (no such setting)** | −0.0142 | −0.0265 | −0.0172 | **+0.0114** |

Multi-Krum matched us only at the count it was tuned for. At four attackers it is back
near undefended FedAvg (+0.2415), while ours holds.

**One baseline resists this and we report it:** single-Krum stays between +0.0172 and
+0.0331 throughout, because selecting the single most central update is insensitive to how
many outliers surround it. Its cost is discarding nine of ten client updates every round,
and like the other geometric rules it yields a selection rather than a per-client judgment,
so it cannot report *which* aircraft is compromised.
""")

# ---------------------------------------------------------------- comment 7 + repro
md(r"""
---
## 7. Comment 7 — Softened claims

Applied verbatim in the abstract, results, discussion and conclusion. Verified by grepping
the LaTeX source for each original phrase and confirming zero matches.

| Was | Now |
|---|---|
| "eliminates the attacker's advantage" | "reduces attack-induced backdoor lift to a level statistically indistinguishable from the honest baseline" |
| "survives a defense-aware adaptive attacker" | "remains effective against the tested defense-aware evasion objective" |
| "each layer alone is insufficient" | "behavioral trust provides most of the measured protection, while coordinate-wise median is retained as a robust backstop" |
| "a stronger detector would not change the defense conclusions" | "additional evaluation is needed to determine whether the findings transfer to stronger detector architectures" |

Two further instances were found on a second pass that the first had missed: a
contributions bullet still read *"the defense eliminates the attacker's advantage ... and
roughly 1.1% server-side overhead"*, and the methodology section still read *"each layer
alone is insufficient"*. Both are fixed.

---
## 8. Reproducing everything

```bash
cd weeks/week12-paper
python run_all.py --list     # stages and approximate runtimes
python run_all.py            # everything (several hours on CPU)
python run_all.py noniid     # one stage
```

Or set `RUN_EXPERIMENTS = True` in Section 0 of this notebook and run it top to bottom.

Every stage re-derives the data split from the fixed seed 42, so stages are independent and
can run in any order. Each writes to `results/*.csv`; the paper's tables are transcribed
from those files, never from a console log. Runs are deterministic on a given machine,
which we verified by executing the FLTrust benchmark twice and getting bit-identical
output.
""")
code(r"""
import subprocess, sys
print(subprocess.run([sys.executable, 'run_all.py', '--list'],
                     capture_output=True, text=True, cwd=HERE).stdout)
print('exported result files:')
for f in sorted(RES.glob('*.csv')):
    print(f'  {f.name:<38} {f.stat().st_size:>7,} bytes')
""")

md(r"""
---
## 9. What the revision changed, in summary

**Stronger than before**

- Nine aggregation rules compared on one pipeline, including every baseline the review named.
- Every number traceable to an exported CSV; one command reproduces all of them.
- Full operating point reported, not accuracy alone.
- We found our own most important weakness before a reviewer did.

**Honestly weaker than we thought**

- The headline result is scoped to fleets with roughly even data. Under skew, which is the
  realistic case, the trust layer stops firing.
- Multi-Krum matches us under IID at a fraction of the cost. Our advantage rests on not
  needing the attacker count, and on naming the culprits.
- The detector is weak, and that is our federated configuration rather than the dataset.

**Next steps, in priority order**

1. A per-client suspicion statistic instead of one normalised against the cohort. Direct fix
   for the skew failure; the harness already supports testing it.
2. Train the federated detector properly (30 rounds, 256-128-64 reaches 0.851 recall).
3. A second, independent signal domain. Everything here is one dataset.
""")

nb['cells'] = cells
nb['metadata'] = {
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python', 'version': '3.12'},
}
nbf.write(nb, str(OUT))
print(f'wrote {OUT}  ({len(cells)} cells: '
      f'{sum(1 for c in cells if c.cell_type == "markdown")} markdown, '
      f'{sum(1 for c in cells if c.cell_type == "code")} code)')
