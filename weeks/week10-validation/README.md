# Week 10: Validation, Improvement, and Stress Testing

**Group 1 (Will Jedrzejczak, Dilpreet Gill, Cole Walther).** Three self-contained studies, in the order they were done. Each folder has its own notebook, its own markdown write-ups, its own `results/` (figures and CSVs), and its own PDF report.

Read them in order. Part 1 found the problem, Part 2 fixed it, Part 3 tried to break the fix.

## Submit this one

**`week10_final_report.pdf`** is the consolidated report to hand in. It covers all three assignment tasks plus both additional studies, and it names the recommended configuration on page 1. The per-part PDFs inside each folder remain as the detailed backup for each individual study.

| Part | Folder | What it is | Status |
|---|---|---|---|
| 1 | `1-validation/` | The graded Week 10 assignment: corrections, multi-seed reliability, quantitative false positives, defense-side sensitivity | **The submission** |
| 2 | `2-improvements/` | Fixing the false-positive weakness Part 1 exposed | **Best result. Adopt this.** |
| 3 | `3-adaptive-attacker/` | Stress testing the Part 2 fix against a stealth attacker | Strongest robustness evidence |

## Which one is best?

Two different senses, so both answers are worth stating:

- **Best result, and the one that changes the defense: Part 2.** It is the only study that made the solution measurably better. A gentler trust gate plus a suspicion dead-zone cut the honest false-positive rate from **20.5% to 0.3%** while the backdoor stayed neutralized, attacker detection stayed at 100%, and clean accuracy and spoofing recall both went **up**. It is strictly better than the previous defense on every metric measured, and it is a two-line change. **This is the configuration we recommend adopting.**
- **Most important deliverable: Part 1.** It is the graded submission and the foundation for the other two. It also contains the corrections (the parameter count, the data-leak fix, the retracted claims) that make the rest trustworthy.

If someone reads only one, make it Part 2. If someone is grading the assignment, they want Part 1.

## Part 1: Validation (`1-validation/`)

The response to the Week 9 review. Fixes the model parameter-count inconsistency (**3,329**, not 13,000, counted live), proves by hashing that the server root set is disjoint from training and test data (and in doing so **found and fixed a real 1-row train/test leak**), reruns the main experiments across **three seeds** with mean and standard deviation, replaces the qualitative false-positive claim with a **quantitative** client-flagging table, and adds a **defense-side** sensitivity sweep.

Key numbers: attack lift **+0.2415 +/- 0.0048**, defense **+0.0107 +/- 0.0025** (a 96% reduction). It also retracts an overclaim: the honest false-positive rate is **20.5%**, not "essentially zero."

- `10_validation.ipynb`, `week10_report.pdf`
- `week10_correction_note.md` (what was fixed), `week10_summary.md` (what changed), `week10_assignment_coverage.md` (assignment compliance map)

## Part 2: Improvements (`2-improvements/`) - recommended

Fixes the 20.5% false-positive rate that Part 1 exposed. Ablates three candidate fixes across three seeds.

| Configuration | Honest FP | Backdoor Lift | Attacker detection |
|---|---|---|---|
| D0 baseline (beta=2.0) | 20.5% | +0.0107 | 100% |
| D1 + gentler gate (beta=1.0) | 6.9% | -0.0054 | 100% |
| **D2 + dead-zone (tau=2.0)** | **0.3%** | **-0.0266** | **100%** |
| D3 + persistence (k=2) | 0.3% | -0.0005 | 88.9% (rejected) |

**D2 is the recommendation.** The third idea (persistence) was tried and **rejected** because it dropped attacker detection without lowering false positives further.

- `improvements.ipynb`, `improvements_report.pdf`, `improvements_summary.md`

## Part 3: Adaptive Attacker (`3-adaptive-attacker/`)

Asks whether the Part 2 dead-zone can be gamed, since a threshold invites gaming: an attacker only needs to keep its suspicion under tau to avoid being gated at all. Sweeps a stealth attacker from 40% poison down to 1%, and proposes a second orthogonal detection signal as a fix.

**Both findings came out against the hypothesis, and are reported as measured:**

1. **The dead-zone holds.** From 5% poison upward the attacker is detected in 100% of client-rounds. Detection only fails at 1% poison, where the *undefended* backdoor lift is **+0.0051**, indistinguishable from zero. Evasion and effectiveness are mutually exclusive, so the attacker's optimal operating point is unprofitable.
2. **The proposed second signal (D4) is rejected.** Update-direction anomaly turned out to be the *weaker* signal at exactly the stealthy settings it was meant to cover, and it roughly doubled the false-positive rate. Kept as a documented negative result.

This does **not** claim general adaptive robustness. An attacker that explicitly optimizes against the probe (a penalty term or a constrained objective) is untested and is the most valuable next experiment.

- `adaptive_attacker.ipynb`, `adaptive_attacker_report.pdf`, `adaptive_attacker_summary.md`

## Reproducibility

Every notebook runs top to bottom and writes its own figures and CSVs into its `results/`. Each PDF is assembled by a build script (`build_*.py`) that reads those exported files and embeds the actual figures, so no report can drift from its experiment. Regenerate any PDF by running its build script from inside its folder.

## What is still open

1. **The base detector is weak** (honest spoofing recall about 0.55). This is partly a ceiling of the simplified 2D dataset and is the highest-value remaining improvement.
2. **A truly optimizing adaptive attacker** has not been tested (see Part 3).
3. **Non-IID client data** is untested and would likely stress the false-positive behavior most.
4. **beta = 1.0 with the dead-zone (D2) is recommended but not yet folded into the Part 1 headline table**, which is still reported at the older beta = 2.0 for comparability with Week 9.
