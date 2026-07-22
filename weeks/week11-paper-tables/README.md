# Week 11: Paper-Ready Setup, Ablation, and Trigger-Generalization Tables

**Group 1 (Will Jedrzejczak, Dilpreet Gill, Cole Walther).**

## Submit this

**`week11_report.pdf`** (5 pages, items 2 to 6 of the assignment in one file):

| Page | Contents |
|---|---|
| 1 | Task 1: experimental parameter card (the reproducibility table) |
| 2 | Task 2: three-seed defense-layer ablation, with insight |
| 3 | Task 3: trigger-generalization table and bar figure, with insight |
| 4 | Task 3b: adaptive (defense-aware) attacker stress test, with insight |
| 5 | Scope and future work (the remaining-limitations note) |

Each table and figure has its insight paragraph directly beneath it, as the assignment asks.

The **code** deliverable, submitted separately, is **`11_paper_tables.ipynb`** plus **`adaptive_attacker.py`**. Every number and figure in the report is produced by one of these two files; nothing is transcribed by hand.

## How to reproduce

```bash
# 1. the adaptive attacker experiment writes results/adaptive_attacker.csv and its figure
python adaptive_attacker.py
# 2. run the notebook top to bottom; its Task 3b cell reads the CSV from step 1
jupyter nbconvert --to notebook --execute --inplace 11_paper_tables.ipynb
# 3. rebuild the PDF from the exported CSVs and figures
python build_week11_report_pdf.py
```

Run `adaptive_attacker.py` before executing the notebook, because the notebook's Task 3b cell reads that script's exported CSV rather than recomputing it. Everything else in the notebook is self-contained. Minor last-digit variation between runs is expected (CPU/library nondeterminism); it does not change any reported conclusion.

## Files

| File | What it is |
|---|---|
| `week11_report.pdf` | The submission (assignment items 2 to 6 in one PDF) |
| `11_paper_tables.ipynb` | The notebook that produces every table and the figure (item 1) |
| `build_week11_report_pdf.py` | Rebuilds the PDF from `results/` |
| `results/parameter_table.csv` | Task 1: the reproducibility card |
| `results/ablation_table.csv` | Task 2: the three-seed defense-layer ablation |
| `results/trigger_comparison.csv` | Task 3: trigger-generalization table (CN0, TCD, PD, mixed CN0+TCD) |
| `results/fig_trigger_comparison.png` | Task 3: bar figure, lift before and after the defense per trigger |
| `adaptive_attacker.py` | Task 3b: defense-aware adaptive attacker (evasion sweep) |
| `results/adaptive_attacker.csv` | Task 3b: adaptive attacker table (lift and trust vs evasion strength) |
| `results/fig_adaptive_attacker.png` | Task 3b: line figure, defended lift and attacker trust vs evasion strength |

## What this week did

1. **Task 1, parameter table.** One reproducibility card listing every experimental setting, assembled from the notebook's live variables so it cannot drift from the code: data sizes and ratio, federation setup, attacker IDs, model architecture and live-counted parameters, attack knobs (poison ratio, trigger value in raw and standardized units, scaling factor, fake accuracy), and the D2 defense constants.
2. **Task 2, three-seed ablation.** Honest FedAvg, attack, attack + inflation, median only, trust only, full defense, and full defense against inflation, each across seeds 42, 7, 123. Headline: median only leaves +0.0641 of backdoor lift, trust only leaves +0.0037, and only the full layered defense drives lift negative (-0.0253) while posting the best clean accuracy and recall. The inflation row is numerically identical to the plain full-defense row because the defense never consults self-reported accuracy.
3. **Task 3, trigger generalization.** CN0, TCD, PD (the weakest probed feature), and a mixed CN0+TCD trigger, each at the identical D2 configuration. The defense drives lift below zero in all four settings with honest false positives between 0.3% and 0.7%.
4. **Task 3b, adaptive attacker.** A defense-aware attacker that trains to evade the probes. As it evades better (trust rises from 0.0001 toward uniform), its own backdoor collapses (undefended lift from +0.2457 to -0.48), because evading the CN0 probe and keeping the CN0 backdoor are directly opposed objectives. Defended lift stays negative at every evasion strength, closing the adaptive-attacker question.

The pipeline, model, attack, defense, and seed protocol are carried over unchanged from `weeks/week10-validation/10_validation.ipynb`; the only code additions are median-only and trust-only aggregation modes (for the ablation) and multi-feature trigger support (for the mixed trigger).
