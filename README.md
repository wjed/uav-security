# UAV Network Wireless Attack Detection

## Machine Learning-Based Wireless Attack Detection for UAV Networks

This project implements a **federated learning (FL) pipeline** for detecting GPS spoofing attacks on UAVs. Using the Aissou et al. 2022 GPS Spoofing Dataset (510,530 rows of SDR GPS receiver measurements), we train and evaluate federated learning models, simulate model-poisoning (backdoor) attacks against the FL system, and design and evaluate defenses against those attacks.

**Current status (Week 9):** Defense implementation complete. Two defense notebooks cover the full rubric: a clean proof-of-concept (v1, 100% gap closure on a single-attacker scenario) and a comprehensive rubric-complete version (v3, 82.2% gap closure with 10 clients, 2 attackers, mixed-feature challenge set, sensitivity analysis, and six comparison experiments).

**Course:** IT 445 Capstone (Group B, 3 credits each) + IT 499 Independent Study (Group A, 5 credits each)
**Institution:** James Madison University
**Semester:** Summer 2026 — May 18 through August 14, 2026
**Final Deadline:** August 14, 2026

---

## Team

### Group A — Federated Learning & Detection Pipeline (IT 499 + IT 445, 5 credits each)

| Name             | GitHub   | Role                                                  |
| ---------------- | -------- | ----------------------------------------------------- |
| Will Jedrzejczak | jedrzewj | Dataset prep, FL pipeline, attack design, defense v1/v3 |
| Cole Walther     | walthecp | Baseline models, FL client implementation             |
| Dilpreet Gill    | gillds   | UAV client partitions, prediction export              |

**Group A owns:** dataset preparation, binary and multiclass labeling, UAV client data partitions, baseline model implementation, federated learning pipeline, backdoor attack simulation, defense implementation, and exporting predictions with confidence scores to Group B.

### Group B — UAV Mission Scenario, Mitigation & Evaluation (IT 445, 3 credits each)

| Name               | GitHub   | Role                                  |
| ------------------ | -------- | ------------------------------------- |
| Brian Stock        | stockbx  | Mitigation rules, system integration  |
| Noah Reed          | reednm   | UAV scenario design, evaluation       |
| Michael Castellano | castelmv | Before-and-after security performance |

**Group B owns:** UAV mission scenario design, communication assumptions, mitigation rules based on classified attack types, connecting Group A predictions to mitigation actions, before-and-after security performance evaluation.

### Faculty Advisor

**Dr. Khalid Hasan** — GitHub: `mohkhalidhasan`

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

### 3. Dataset Location

The **Aissou et al. 2022 GPS Spoofing Dataset** is already included in the repository at:

```
weeks/week07-first-working-version/A DATASET for GPS Spoofing Detection on Unmanned Aerial System/GPS_Data_Simplified_2D_Feature_Map.xlsx
```

### 4. Run the Notebooks

**Attack baseline (Week 7):**
```bash
jupyter notebook weeks/week07-first-working-version/07_fl_backdoor.ipynb
```

**Defense v1 — clean proof-of-concept (5 clients, 1 attacker, CN0-only challenge set, 100% gap closure):**
```bash
jupyter notebook weeks/week09-defense-solutions/09_defense_implementation.ipynb
```

**Defense v3 — rubric-complete (10 clients, 2 attackers, mixed challenge set, 6 experiments, sensitivity analysis):**
```bash
jupyter notebook weeks/week09-defense-solutions/09_defense_v3.ipynb
```

To re-execute a notebook non-interactively:
```bash
python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=900 \
    weeks/week09-defense-solutions/09_defense_v3.ipynb
```

---

## Project Structure

```
uav-security/
├── requirements.txt
├── config/
│   └── config.yaml                     # Tunable hyperparameters and paths
├── docs/
│   └── architecture.md                 # Full system architecture document
└── weeks/
    ├── week07-first-working-version/
    │   ├── 07_fl_backdoor.ipynb         # FL pipeline + CN0 backdoor attack
    │   ├── week07_in_depth_summary.md   # Detailed study guide / presentation notes
    │   └── A DATASET for GPS Spoofing Detection.../
    │       └── GPS_Data_Simplified_2D_Feature_Map.xlsx
    ├── week08-defense-exploration/      # Intermediate defense explorations (archived)
    └── week09-defense-solutions/
        ├── 09_defense_implementation.ipynb   # Defense v1: 5 clients, binary flag, 100% gap closure
        ├── 09_defense_v3.ipynb               # Defense v3: rubric-complete, 10 clients, 82.2% gap closure
        └── week09_results_writeup.md         # Full results write-up with tables, analysis, limitations
```

---

## Key Results

### Attack (Week 7)

| Experiment | Clean Acc | BSR | Notes |
|---|---|---|---|
| Centralized baseline | 0.7418 | 0.4802 | No FL, single model |
| Honest FedAvg | 0.7257 | 0.5208 | 5 clients, no attack |
| Poisoned FedAvg | 0.7003 | 0.7435 | Client 5 poisoned (40% rate, CN0 trigger) |
| Poisoned Acc-Weighted | — | ~0.87 | Client 5 reports fake 0.99 accuracy |

**BSR (Backdoor Success Rate):** fraction of CN0-triggered spoofed GPS signals misclassified as benign. High BSR = attacker succeeds in hiding spoofed signals.

### Defense v1 (Week 9 — `09_defense_implementation.ipynb`)

5 clients, 1 attacker (Client 5), 10 FL rounds, D5 trigger-region probing + D3 coordinate-wise median.

| Experiment | Clean Acc | BSR | Gap Closed |
|---|---|---|---|
| Exp A: Poisoned, no defense | 0.6978 | 0.7553 | — |
| Exp B: D5 probing only | 0.6975 | 0.6725 | 35% |
| **Exp C: D5 + D3 full defense** | **0.7067** | **0.5203** | **~100%** |

Client 5 flagged 9/10 rounds, zero false positives. Clean accuracy *improves* slightly under defense.

### Defense v3 (Week 9 — `09_defense_v3.ipynb`)

10 clients, 2 attackers (Clients 9 & 10), mixed CN0+TCD challenge set, continuous trust score.

| Experiment | Clean Acc | Spoof Recall | BSR | Lift |
|---|---|---|---|---|
| Exp 0: Honest FedAvg | 0.6841 | 0.4650 | 0.7203 | 0.0000 |
| Exp 1: Poisoned FedAvg | 0.6772 | 0.3493 | 0.8147 | +0.0943 |
| Exp 2: Poisoned Acc-Weighted | 0.6691 | 0.3180 | 0.8650 | +0.1447 |
| Exp 3: D3 Median only | 0.6863 | 0.4113 | 0.7652 | +0.0448 |
| Exp 4: D5 Challenge only | 0.6702 | 0.3753 | 0.7705 | +0.0502 |
| **Exp 5: D5+D3 Full defense** | **0.6851** | **0.4545** | **0.7372** | **+0.0168** |

**Full defense removes 82.2% of the attack-induced backdoor lift.** Spoofing recall nearly fully recovers (45.5% vs. 46.5% honest). Both attacker clients consistently down-weighted from round 3 onward; zero false positives on honest clients.

**Sensitivity check:** Full defense tested at poison rates 30%/40%/50%. Lift stays between −0.008 and +0.048 across all three — never approaching the undefended +0.094.

For full analysis, tables, and limitations see [`week09_results_writeup.md`](weeks/week09-defense-solutions/week09_results_writeup.md).

---

## Weekly Milestone Summary

| Weeks | Dates           | Status | Group A Deliverables |
| ----- | --------------- | ------ | -------------------- |
| 1–2   | May 18 – May 30 | ✅ Done | Literature review, dataset exploration |
| 3–4   | Jun 2 – Jun 13  | ✅ Done | Labels, partitions, initial baselines |
| 5–6   | Jun 16 – Jun 27 | ✅ Done | Local models, FedAvg end-to-end |
| 7     | Jun 30 – Jul 4  | ✅ Done | GPS dataset prep, CN0 backdoor attack, FedAvg + acc-weighted FL |
| 8     | Jul 7 – Jul 11  | ✅ Done | Defense exploration (D5 probing, D3 median) |
| 9     | Jul 14 – Jul 18 | ✅ Done | Defense v1 (100% gap closure) + v3 (rubric-complete, 82.2% gap closure) |
| 10    | Jul 21 – Jul 25 | 🔄 Up next | Final evaluation, plots, presentation prep |
| 11–12 | Jul 28 – Aug 8  | — | Final report, technical sections, slides |
| 13    | Aug 11 – Aug 14 | — | **Final submission** |

---

## Dataset Use Restrictions

The **Aissou et al. 2022 GPS Spoofing Dataset** is used under academic license for this capstone project. **Do not share, redistribute, or publicly release any raw or processed version of this dataset without written approval.**
