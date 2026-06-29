# UAV Network Wireless Attack Detection

## Machine Learning-Based Wireless Attack Detection for UAV Networks

This project implements a **federated learning (FL) pipeline** for detecting wireless network attacks in simulated UAV environments. Using the WSN-DS dataset (374,661 labeled sensor-node records across 5 attack classes), the system trains distributed detection models across simulated UAV clients without centralizing raw data, then feeds classified attack types into a rule-based mitigation layer that evaluates before-and-after security performance in a UAV mission scenario.

**Course:** IT 445 Capstone (Group B, 3 credits each) + IT 499 Independent Study (Group A, 5 credits each)
**Institution:** James Madison University
**Semester:** Summer 2026 — May 18 through August 14, 2026
**Final Deadline:** August 14, 2026

---

## Team

### Group A — Federated Learning & Detection Pipeline (IT 499 + IT 445, 5 credits each)

| Name | GitHub | Role |
|------|--------|------|
| Will Jedrzejczak | jedrzewj | Dataset prep, FL pipeline, binary/multiclass labeling |
| Cole Walther | walthecp | Baseline models, FL client implementation |
| Dilpreet Gill | gillds | UAV client partitions, prediction export |

**Group A owns:** dataset preparation, binary and multiclass labeling, UAV client data partitions, baseline model implementation and comparison, federated learning pipeline, exporting predictions with confidence scores to Group B.

### Group B — UAV Mission Scenario, Mitigation & Evaluation (IT 445, 3 credits each)

| Name | GitHub | Role |
|------|--------|------|
| Brian Stock | stockbx | Mitigation rules, system integration |
| Noah Reed | reednm | UAV scenario design, evaluation |
| Michael Castellano | castelmv | Before-and-after security performance |

**Group B owns:** UAV mission scenario design, communication assumptions, mitigation rules based on classified attack types, connecting Group A predictions to mitigation actions, before-and-after security performance evaluation.

### Faculty Advisor

**Dr. Khalid Hasan** — GitHub: `mohkhalidhasan`

> **Action required:** Add Dr. Hasan as a collaborator at `https://github.com/wjed/uav-security/settings/access`.

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/wjed/uav-security.git
cd uav-security
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Download and place the dataset

Download **WSN-DS.csv** from [Kaggle — WSN-DS Dataset](https://www.kaggle.com/datasets/bassamkasasbeh1/wsnds) and place it at:

```
data/raw/WSN-DS.csv
```

> The `data/raw/` directory is gitignored. Do **not** commit the CSV. See dataset use restriction below.
> You can also run `python data/download_data.py` for guided instructions.

### 4. Run baseline models

```bash
python src/baseline/train_baseline.py
```

### 5. Run federated learning

```bash
python src/federated/run_fl.py
```

---

## Project Structure

```
uav-security/
├── config/config.yaml        # All tunable hyperparameters and paths
├── data/                     # Raw and processed data (gitignored)
│   └── download_data.py      # Dataset download helper
├── src/
│   ├── data/                 # Loading, preprocessing, partitioning (Group A)
│   ├── models/               # LR, RF, DNN model definitions (Group A)
│   ├── baseline/             # Centralized training scripts (Group A)
│   ├── federated/            # Flower FL client, server, runner (Group A)
│   ├── mitigation/           # Attack-type mitigation rules (Group B)
│   └── evaluation/           # Metrics and reporting (Both Groups)
├── notebooks/                # EDA, baseline, and FL analysis notebooks
├── results/                  # Output plots and tables (gitignored)
├── weeks/                    # Per-sprint READMEs and task stubs
└── docs/architecture.md      # Full system architecture document
```

---

## Weekly Milestone Summary

| Weeks | Dates | Shared Goal | Group A Focus | Group B Focus |
|-------|-------|-------------|---------------|---------------|
| 1–2 | May 18 – May 30 | Project setup, repo, tools installed | Literature review, WSN-DS exploration | UAV use case draft, comms assumptions |
| 3–4 | Jun 2 – Jun 13 | Data preparation & baseline models | Labels, partitions, initial baselines | Baseline/validation script, related work |
| 5–6 | Jun 16 – Jun 27 | Local learning & first FL prototype | Local models, FedAvg end-to-end | Mitigation rules with placeholder predictions |
| 7–8 | Jun 30 – Jul 11 | FL backdoor experiment | GPS dataset prep, IID client split, CN0-trigger backdoor, FedAvg + accuracy-weighted FL (week 7 complete) | Connect predictions to mitigation, eval |
| 9–10 | Jul 14 – Jul 25 | Full system evaluation | FL experiments, plots, tables | Visual demo, mitigation impact results |
| 11–12 | Jul 28 – Aug 8 | Final report & presentation | Code, results, technical sections | Lit review, scenario, slides, demo |
| 13 | Aug 11 – Aug 14 | **Final submission** | Submit all deliverables | Submit all deliverables |

> **IT 499 note (Group A):** Draft evaluation section due to Dr. Hasan in Week 9–10. IT 499 final deliverable prepared in Week 11–12.

---

## Meeting Schedule

- **Mondays** — Full team meeting with Dr. Hasan
- **Tuesdays** — Group A subgroup (IT 499 accountability)
- **Wednesdays** — Group B subgroup (IT 445 check-ins)

---

## Dataset Use Restriction

The WSN-DS dataset is used under academic license for this capstone project. **Do not share, redistribute, or publicly release any raw or processed version of this dataset without written approval from Dr. Khalid Hasan.** The `data/raw/` and `data/processed/` directories are fully gitignored to prevent accidental commits.
