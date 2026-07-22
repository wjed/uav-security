# UAV Network Wireless Attack Detection

## Machine Learning-Based Wireless Attack Detection for UAV Networks

This project studies **federated learning (FL) for detecting GPS spoofing on a fleet of UAVs**, and what happens when one or more UAVs in that fleet are compromised. Using the Aissou et al. 2022 GPS Spoofing Dataset (510,530 rows of software-defined-radio GPS receiver measurements), we build an FL detection pipeline, implement a stealthy backdoor (model-poisoning) attack against it, and design and evaluate a defense that neutralizes the attack.

**Course:** IT 445 Capstone + IT 499 Independent Study
**Institution:** James Madison University
**Semester:** Summer 2026 (May 18 to August 14, 2026)
**Final deadline:** August 14, 2026

---

## Current status

The **defense is complete, validated, and packaged for the paper.** It is a feature-agnostic, server-side behavioral-trust mechanism layered on coordinate-wise median aggregation (10 clients, 2 attackers, 150k rows). It eliminates the attacker's advantage, is immune to accuracy inflation by construction (the defended result is identical with and without the fake reported accuracy), generalizes to trigger features it was never told about, and attributes the attack to the exact compromised UAVs (attacker trust driven to 0.000 every round). The adopted configuration is **D2** (gentle trust gate beta = 1.0, suspicion dead-zone tau = 2.0, trust smoothing EMA = 0.5), used consistently in every result below.

The project is organized as a build-then-harden arc:

- **`weeks/week08-defense-solutions/`** builds the defense (v1 proof-of-concept, v3, then the final feature-agnostic version) with a false-positive analysis, a computational-cost analysis, and result figures.
- **`weeks/week09-final-iteration/`** holds the focused core paper results (honest baseline, attack, defense; one main table, one main figure, a sensitivity check).
- **`weeks/week10-validation/`** is validation and reliability: every main experiment rerun across three seeds (42, 7, 123) with mean and standard deviation; a live parameter audit (the model has **3,329** parameters, 13.0 KB in float32; an earlier "13k parameters" claim was a copy-paste error from the Week 4 WSN-DS model and is corrected); a hash-based proof that the server root set is disjoint from client training data and the test set (which also found and fixed a real 1-row train/test leak); a quantitative false-positive/client-flagging table; a defense-side sensitivity sweep; and a five-feature trigger-generalization sweep. This stage also exposed and fixed the defense's main weakness: the old gate flagged honest clients in **20.5%** of client-rounds, and adopting D2 cut that to **0.3%** while keeping the backdoor neutralized and attacker detection at 100%.
- **`weeks/week11-paper-tables/`** is the paper-ready deliverable: the experimental parameter card, a three-seed ablation proving each defense layer matters, a trigger-generalization table and figure (CN0, TCD, PD, and a mixed CN0+TCD trigger), and an adaptive (defense-aware) attacker stress test.
- **`weeks/week12-paper/`** is the IEEE paper draft (`main.tex`) with all sections written and reconciled to the final 10-client / 2-attacker / 150k setup, plus the figures it references.

Remaining: a final compile and review pass on the paper in Overleaf, and the presentation (scheduled August 5).

---

## How the repository is organized

Work is grouped by week under `weeks/`. Two things explain the layout at a glance:

1. **The project pivoted datasets partway through.** Weeks 2 to 5 are an earlier exploration on the **WSN-DS** wireless-sensor dataset (EDA, a Random Forest baseline, a DNN baseline, and a first threat model). From **week 7 onward** the project moved to the **Aissou et al. 2022 GPS spoofing dataset**, which is the dataset the final work is built on. The WSN-DS weeks are kept as the record of how we got here.
2. **Some week numbers are skipped** (there is no week 1 or week 6 folder). Those weeks were literature review or work that folded into the adjacent week's folder. The gaps are expected; nothing is missing.

The two datasets:

| Dataset | Used in | In the repo? |
|---|---|---|
| WSN-DS (wireless sensor network attacks) | weeks 2 to 5 | No (local only, git-ignored under `data/raw/`) |
| Aissou et al. 2022 GPS spoofing | week 7 onward | Yes, under `weeks/week07-first-working-version/` |

---

## Team

Federated Learning and Detection Pipeline (IT 499 + IT 445).

| Name             | GitHub   | Role                                              |
| ---------------- | -------- | ------------------------------------------------- |
| Will Jedrzejczak | jedrzewj | Dataset prep, FL pipeline, attack design, defense |
| Cole Walther     | walthecp | Baseline models, FL client implementation         |
| Dilpreet Gill    | gillds   | UAV client partitions, prediction export          |

The team owns dataset preparation, labeling, UAV client data partitions, baseline models, the federated learning pipeline, the backdoor attack simulation, the defense implementation, the validation and paper-ready results, and the paper writeup.

### Faculty Advisor

Dr. Khalid Hasan (GitHub: `mohkhalidhasan`)

---

## Setup

### 1. Clone

```bash
git clone https://github.com/wjed/uav-security.git
cd uav-security
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Dataset

The Aissou et al. 2022 GPS spoofing dataset is already in the repo at:

```
weeks/week07-first-working-version/A DATASET for GPS Spoofing Detection on Unmanned Aerial System/GPS_Data_Simplified_2D_Feature_Map.xlsx
```

The WSN-DS dataset used in weeks 2 to 5 is not committed (it lives locally under `data/raw/`, which is git-ignored).

### 4. Run the notebooks

Paper-ready tables and figures (week 11, the latest deliverable):
```bash
jupyter notebook weeks/week11-paper-tables/11_paper_tables.ipynb
```

Validation and reliability (week 10):
```bash
jupyter notebook weeks/week10-validation/10_validation.ipynb
```

Core paper results (week 9):
```bash
jupyter notebook weeks/week09-final-iteration/09_final_iteration.ipynb
```

The defense in full (week 8):
```bash
jupyter notebook weeks/week08-defense-solutions/final/08_defense_final.ipynb
```

GPS attack baseline (week 7):
```bash
jupyter notebook weeks/week07-first-working-version/07_fl_backdoor.ipynb
```

Earlier defenses, kept for the progression:
```bash
jupyter notebook weeks/week08-defense-solutions/old/08_defense_implementation.ipynb   # v1
jupyter notebook weeks/week08-defense-solutions/old/08_defense_v3.ipynb               # v3
```

To re-execute a notebook non-interactively:
```bash
python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1800 \
    weeks/week08-defense-solutions/final/08_defense_final.ipynb
```

---

## Project structure

```
uav-security/
├── README.md
├── requirements.txt
├── config/
│   └── config.yaml                       # tunable hyperparameters and paths
├── docs/
│   └── architecture.md                   # system architecture document
├── data/                                 # local only, git-ignored (holds WSN-DS.csv)
└── weeks/
    ├── week02-eda/                        # WSN-DS: exploratory data analysis
    ├── week03-baseline/                   # WSN-DS: Random Forest baseline
    ├── week04-dnn/                        # WSN-DS: DNN baseline + RF comparison
    ├── week05-threat-model/               # first threat model definition
    ├── week07-first-working-version/      # PIVOT to GPS spoofing: FL pipeline + backdoor attack
    │   ├── 07_fl_backdoor.ipynb
    │   ├── system_diagram.md, what_i_did.md
    │   └── A DATASET for GPS Spoofing.../GPS_Data_Simplified_2D_Feature_Map.xlsx
    ├── week08-defense-solutions/          # the defense
    │   ├── final/                         # FINAL defense (the version we stand behind)
    │   │   ├── 08_defense_final.ipynb     #   feature-agnostic behavioral trust + coordinate median
    │   │   ├── week08_final_results_writeup.md   # full results, analysis, limitations
    │   │   ├── false_positives.md               # false-positive discussion + what we report
    │   │   ├── figure_explanations.md           # what each figure is and why
    │   │   ├── pseudocode_options.md            # IEEE-style pseudocode options for the paper
    │   │   └── results/                         # 6 figures
    │   ├── old/                           # earlier defenses, kept for the progression
    │   │   ├── 08_defense_implementation.ipynb  # v1: 5 clients, binary flag
    │   │   ├── 08_defense_v3.ipynb              # v3: 10 clients, mixed challenge set
    │   │   └── week08_results_writeup.md
    │   └── cost-analysis/
    │       ├── cost_analysis.py                 # instrument (re-run to regenerate)
    │       └── computational_cost.md            # measured timing, memory, communication, complexity
    ├── week09-final-iteration/            # core paper results
    │   ├── 09_final_iteration.ipynb       #   honest / attack / defense, main table, main figure, sensitivity
    │   ├── week09_summary.md
    │   └── results/                       #   main and supporting figures + result CSVs
    ├── week10-validation/                 # validation and reliability (D2 adopted here)
    │   ├── README.md
    │   ├── 10_validation.ipynb            #   3 seeds, separation proof, parameter audit, quantitative
    │   │                                  #   false positives, defense-side sensitivity, 5-feature
    │   │                                  #   trigger-generalization sweep
    │   ├── week10_final_report.pdf        #   submission PDF (JMU-branded)
    │   ├── week10_correction_note.md, week10_summary.md
    │   ├── build_final_report_pdf.py
    │   └── results/                       #   result CSVs + line figures
    └── week11-paper-tables/               # paper-ready tables and figures
        ├── README.md
        ├── 11_paper_tables.ipynb          #   Task 1 parameter card, Task 2 layer ablation,
        │                                  #   Task 3 trigger generalization (CN0, TCD, PD, CN0+TCD)
        ├── adaptive_attacker.py           #   defense-aware attacker stress test (evasion sweep)
        ├── week11_report.pdf              #   submission PDF (items 2 to 6)
        ├── build_week11_report_pdf.py
        └── results/                       #   result CSVs + bar/line figures
```

The IEEE paper draft (`main.tex`) is kept locally and is not yet committed.

---

## Key results

### GPS attack baseline (week 7)

| Experiment | Clean Acc | BSR | Notes |
|---|---|---|---|
| Centralized baseline | 0.7418 | 0.4802 | No FL, single model |
| Honest FedAvg | 0.7257 | 0.5208 | 5 clients, no attack |
| Poisoned FedAvg | 0.7003 | 0.7435 | Client 5 poisoned, 40% rate, CN0 trigger |
| Poisoned Acc-Weighted | n/a | ~0.87 | Client 5 reports fake 0.99 accuracy |

**BSR (Backdoor Success Rate):** fraction of CN0-triggered spoofed signals wrongly called benign. Higher is worse.

### Final defense (week 8, `final/08_defense_final.ipynb`)

10 clients, 2 attackers (C9, C10), 150k rows, 12 FL rounds. Feature-agnostic behavioral trust (server-side, probes every discriminative feature) + coordinate-wise median. Attack = data poisoning + model-replacement scaling + accuracy inflation.

| Experiment | Clean Acc | Spoof Recall | False Alarm | BSR | Lift |
|---|---|---|---|---|---|
| Exp0 Honest FedAvg | 0.7138 | 0.5447 | 0.1735 | 0.6600 | 0.0000 |
| Exp1 Attack (FedAvg) | 0.6990 | 0.3977 | 0.1002 | 0.8966 | +0.2366 |
| Exp2 Attack + inflation (Acc-Weighted) | 0.6941 | 0.3758 | 0.0938 | 0.9429 | +0.2829 |
| Exp3 D-median only | 0.7135 | 0.5152 | 0.1543 | 0.7154 | +0.0554 |
| Exp4 D-trust only | 0.7164 | 0.5541 | 0.1753 | 0.6413 | -0.0187 |
| **Exp5 FULL defense** | **0.7095** | **0.5387** | **0.1767** | **0.6412** | **-0.0188** |
| Exp6 FULL vs attack + inflation | 0.7095 | 0.5387 | 0.1767 | 0.6412 | -0.0188 |

- **Attacker advantage eliminated:** lift +0.237 undefended to -0.019 defended, with clean accuracy and spoof recall preserved.
- **Accuracy-inflation immunity is bit-exact:** Exp6 (with fake 0.99) is identical to Exp5, because the trust score never reads reported accuracy.
- **Generalization (unknown trigger):** attacker switches the trigger to TCD, defense not told, undefended lift +0.295 to +0.008.
- **Attribution and false positives:** both attackers driven to exactly 0.000 trust every round; no honest client is ever fully excluded, though one honest client is persistently down-weighted (a mild false-positive tendency, disclosed). The full defense keeps the detector false-alarm rate at the honest baseline level (0.177 vs 0.174).
- **Sensitivity:** lift -0.018 / -0.019 / -0.019 at poison rates 30 / 40 / 50%.

Full analysis: [`week08_final_results_writeup.md`](weeks/week08-defense-solutions/final/week08_final_results_writeup.md). False-positive discussion: [`false_positives.md`](weeks/week08-defense-solutions/final/false_positives.md). Computational cost: [`computational_cost.md`](weeks/week08-defense-solutions/cost-analysis/computational_cost.md).

### Earlier defenses (kept for the progression, under `week08-defense-solutions/old/`)

- **v1** (`old/08_defense_implementation.ipynb`): 5 clients, 1 attacker, CN0-only challenge set with a binary hard flag + coordinate-wise median. Closed roughly 100% of the attack gap (BSR 0.755 to 0.520), zero false positives. Clean but relied on knowing the trigger was CN0.
- **v3** (`old/08_defense_v3.ipynb`): 10 clients, 2 attackers, hand-picked CN0+TCD challenge set with a continuous trust score. Removed 82.2% of the backdoor lift. Still hand-picked the challenge features, which the final version fixes.

Full v1/v3 analysis: [`old/week08_results_writeup.md`](weeks/week08-defense-solutions/old/week08_results_writeup.md).

### Validated results at D2 (weeks 10 and 11)

These are the numbers we stand behind for the paper: the adopted D2 configuration, three seeds (42, 7, 123), mean +/- standard deviation, lift paired within-seed against the honest baseline.

**Layer ablation** (`week11-paper-tables/results/ablation_table.csv`), CN0 trigger, showing each layer matters:

| Method | Clean Acc | Spoof Recall | Backdoor Lift |
|---|---|---|---|
| Honest FedAvg | 0.7109 +/- 0.0021 | 0.5287 +/- 0.0124 | +0.0000 |
| Attack (FedAvg) | 0.6928 +/- 0.0032 | 0.3618 +/- 0.0091 | +0.2457 +/- 0.0023 |
| Attack + inflation | 0.6900 +/- 0.0047 | 0.3535 +/- 0.0158 | +0.3036 +/- 0.0131 |
| Median only | 0.7098 +/- 0.0038 | 0.4993 +/- 0.0143 | +0.0641 +/- 0.0064 |
| Trust only | 0.7114 +/- 0.0017 | 0.5311 +/- 0.0137 | +0.0037 +/- 0.0042 |
| **Full defense (D2)** | **0.7142 +/- 0.0027** | **0.5546 +/- 0.0177** | **-0.0253 +/- 0.0178** |

Median alone leaves about a quarter of the attack; trust alone nearly closes it; only the layered defense drives lift negative while posting the best clean accuracy and recall. The full defense is bit-identical against the inflation variant, because trust never reads client-reported accuracy.

**Trigger generalization** (`week11-paper-tables/results/trigger_comparison.csv` and the five-feature `week10-validation/results/trigger_generalization.csv`), one fixed D2 defense, defended lift negative for every trigger:

| Trigger | Cohen's d | Attack lift | Defended lift | Honest FP |
|---|---|---|---|---|
| CN0 | 0.288 | +0.2457 | -0.0253 | 0.3% |
| TCD | 0.302 | +0.2384 | -0.0626 | 0.7% |
| PD (weakest probed) | 0.152 | +0.0909 | -0.0188 | 0.3% |
| CN0+TCD (mixed) | 0.288+0.302 | +0.1933 | -0.0282 | 0.7% |

The Week 10 sweep adds DO and LC to the same picture (all five single-feature triggers defended below zero), which is the evidence behind the "trigger-agnostic within the discriminative feature set" claim in the title.

**False positives and attribution** (`week10-validation/results/`): under D2 both attackers are flagged in 72/72 client-rounds (100%) with mean trust 0.000, while honest clients are flagged in 1/288 client-rounds (0.3%) and none is ever driven to zero trust. The server-side overhead is about 1.1% of round time with no client-side cost.

---

## Weekly milestone summary

| Weeks | Focus | Status |
| ----- | ----- | ------ |
| 1 to 2 | Literature review, WSN-DS exploratory data analysis | Done |
| 3 to 4 | WSN-DS Random Forest baseline, DNN baseline, RF vs DNN comparison | Done |
| 5 | First threat model definition | Done |
| 6 to 7 | Pivot to the GPS spoofing dataset; FL pipeline; CN0 backdoor attack (FedAvg and accuracy-weighted) | Done |
| 8 | Defense: v1 proof-of-concept, v3 rubric-complete, then the final feature-agnostic defense; plus false-positive and computational-cost analysis | Done |
| 9 | Core paper results: honest / attack / defense, main table, main figure, sensitivity check | Done |
| 10 | Validation and reliability: multi-seed mean/std, parameter audit, root-set separation proof, quantitative false-positive table, defense-side sensitivity, D2 adopted, five-feature trigger-generalization sweep | Done |
| 11 | Paper-ready tables: parameter card, three-seed layer ablation, trigger-generalization figure (CN0, TCD, PD, CN0+TCD), adaptive-attacker stress test | Done |
| 12 | IEEE paper draft: all sections written and reconciled to the final setup | Done |
| final | Overleaf compile/review, presentation (Aug 5), final submission | Due Aug 14 |

---

## Dataset use restrictions

The Aissou et al. 2022 GPS spoofing dataset is used under academic license for this capstone. Do not share, redistribute, or publicly release any raw or processed version of the dataset without written approval.
