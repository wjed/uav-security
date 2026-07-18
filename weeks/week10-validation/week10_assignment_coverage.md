# Week 10: Assignment Coverage Map

**Group 1.** This document maps every item in the Week 10 assignment to exactly where and how it was addressed, with pointers into the notebook and the result files. It is a navigation and compliance aid; the substance lives in `10_validation.ipynb`, `week10_correction_note.md`, and `week10_summary.md`.

Everything below was produced by `10_validation.ipynb`, executed top to bottom with no errors and no manual steps. Every table and figure is written to `results/` as a CSV or PNG.

## Task 1: Fix the current report issues

| Sub-item | How it was addressed | Where |
|---|---|---|
| Model parameter count inconsistency | Counted live, layer by layer. The GPS model has **3,329** parameters (13.0 KB in float32), not 13,000. The wrong figure was copy-pasted from the Week 4 WSN-DS model (12,805 parameters); corrected in the Week 8 and Week 9 notebooks. | Notebook Section 2; `results/parameter_audit.csv`; correction note item 1 |
| Root/challenge set separated from train and test | Proven by hashing every row. The check found a real 1-row train/test overlap (caused by de-duplicating before dropping the identifier columns) and fixed it; all three sets are now provably disjoint (0/0/0) and the notebook asserts it. | Notebook Section 1; correction note item 2 |
| Every table and figure reproducible from the notebook | Every table and figure is produced by a cell and exported to `results/`. Nothing is transcribed by hand. | All sections; correction note item 7 |
| Any unclear or overstated claim | Four corrected: "zero false positives" retracted, the negative lift explained as single-seed noise, "no utility cost" softened (about 0.008 clean-accuracy cost), "feature-agnostic" qualified to the discriminative feature set. | Correction note item 6; notebook Sections 6, 9 |
| **Submit a short correction note** | Delivered. | `week10_correction_note.md` (and notebook Section 9) |

## Task 2: Improve result reliability

| Requirement | How it was addressed | Where |
|---|---|---|
| Rerun main experiments with more than one seed | Three seeds: **42, 7, 123**. The data split, test set, and root carve are held fixed; the federated randomness (client partition, poison draw, initialization, batching) varies per seed. | Notebook Sections 4 to 5 |
| Minimum cases: Honest, Attack or Attack+inflation, Full defense | Exceeded: ran **all four** cases (Honest, Attack, Attack+inflation, Full defense) across all three seeds. | Notebook Section 4 |
| Report mean and standard deviation (if three seeds) | Reported. Attack lift **+0.2415 +/- 0.0048**, inflation **+0.3036 +/- 0.0124**, full defense **+0.0107 +/- 0.0025** (a 96% reduction). Lift is paired within each seed against that seed's own honest baseline. | Notebook Section 5; `results/main_table_multiseed.csv` |

## Task 3: Prepare the next paper figure and table

| Requirement | How it was addressed | Where |
|---|---|---|
| One new paper-quality figure | Delivered a two-panel line figure: (a) backdoor success rate across rounds for all methods, (b) attacker vs honest trust across rounds. This combines two of the recommended figure options (attacker trust across rounds, and backdoor progression). A second figure (defense-side sensitivity) is included as well. | Notebook Section 8; `results/fig_main_paper_rounds.png` (and `fig_defense_sensitivity.png`) |
| One improved table | Delivered the updated main comparison table with mean/std (recommended option 1), plus a false-positive/client-flagging table (option 2) and defense-side sensitivity tables (option 3). | Notebook Sections 5, 6, 7; corresponding CSVs in `results/` |
| Each figure/table: clear title | Present on every table and figure. | Verified in notebook |
| Each figure/table: labeled axes or columns | Both figures set title, x-label, y-label, and legend; all tables have named columns. | Verified in notebook |
| Each figure/table: short caption | Present under Table 1, Table 2, Figure 1, and Figure 2. | Notebook markdown cells |
| Each figure/table: a paragraph explaining the main insights | Present for each, including the two findings that contradicted our expectations (see below). | Notebook markdown cells |
| Well formatted, line graphs preferred over bar graphs | Both figures are line graphs with standard-deviation bands. There are **zero bar charts** in the notebook. Paper-quality plot defaults are set once at the top. | Notebook Section 0, 7, 8 |

## Deliverables

| Deliverable | File |
|---|---|
| 1. Updated code or notebook | `10_validation.ipynb` |
| 2. Correction note | `week10_correction_note.md` |
| 3. Updated main result table | `results/main_table_multiseed.csv` (and Table 1 in the notebook) |
| 4. One new paper-quality figure with caption | `results/fig_main_paper_rounds.png` (caption in notebook Section 8) |
| 5. Short written summary (what changed, improved, remains incomplete) | `week10_summary.md` (and notebook Section 10) |

## Depth over breadth, and honest reporting

The assignment asked for one well-executed deeper experiment rather than several incomplete ones, and for limitations reported honestly. Two results in this submission are deliberately less flattering than the Week 9 report, and we report them rather than hide them:

- The honest-client false-positive rate is **20.5%** (59 of 288 client-rounds), and one honest client-round was driven to zero trust. This **retracts** the earlier claim that only attackers ever reach zero trust.
- The defense-side sensitivity sweep contradicted our expectation: a sharper trust gate makes both the backdoor and the utility worse, because it amplifies the honest false-positive problem. **beta = 1.0 dominates our current default of beta = 2.0 on every metric.** This is an actionable improvement that only the defense-side check could have surfaced.

## Recommended items intentionally deferred

The assignment listed several recommended-but-optional tables. We completed the required table plus two recommended ones (false-positive table, defense-side sensitivity table). We did **not** include the trigger-comparison or non-IID tables in this submission. Non-IID in particular is deferred deliberately: it is a full experiment that would probe the false-positive weakness above and connect to the beta and threshold findings, so it is planned as the next deeper experiment rather than rushed in here, consistent with the "depth over breadth" instruction.
