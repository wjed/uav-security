# UAV Network Wireless Attack Detection

## Machine Learning-Based Wireless Attack Detection for UAV Networks

This project implements a **federated learning (FL) pipeline** for detecting wireless network attacks in simulated UAV environments. The system evaluates detection performance and security resilience using the **Aissou et al. 2022 GPS Spoofing Dataset** (510,530 rows of SDR GPS receiver signal-quality measurements) to train and evaluate federated learning models, simulate model-poisoning (backdoor) attacks, and analyze vulnerabilities in accuracy-weighted aggregation defenses.

Classified attack types are fed into a rule-based mitigation layer that evaluates before-and-after security performance in a UAV mission scenario.

**Course:** IT 445 Capstone (Group B, 3 credits each) + IT 499 Independent Study (Group A, 5 credits each)
**Institution:** James Madison University
**Semester:** Summer 2026 — May 18 through August 14, 2026
**Final Deadline:** August 14, 2026

---

## Team

### Group A — Federated Learning & Detection Pipeline (IT 499 + IT 445, 5 credits each)

| Name             | GitHub   | Role                                                  |
| ---------------- | -------- | ----------------------------------------------------- |
| Will Jedrzejczak | jedrzewj | Dataset prep, FL pipeline, binary/multiclass labeling |
| Cole Walther     | walthecp | Baseline models, FL client implementation             |
| Dilpreet Gill    | gillds   | UAV client partitions, prediction export              |

**Group A owns:** dataset preparation, binary and multiclass labeling, UAV client data partitions, baseline model implementation and comparison, federated learning pipeline, exporting predictions with confidence scores to Group B.

### Group B — UAV Mission Scenario, Mitigation & Evaluation (IT 445, 3 credits each)

| Name               | GitHub   | Role                                  |
| ------------------ | -------- | ------------------------------------- |
| Brian Stock        | stockbx  | Mitigation rules, system integration  |
| Noah Reed          | reednm   | UAV scenario design, evaluation       |
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

### 3. Dataset Location

The **Aissou et al. 2022 GPS Spoofing Dataset** is already included in the repository as a simplified 2D feature map at:

```
weeks/week07-first-working-version/A DATASET for GPS Spoofing Detection on Unmanned Aerial System/GPS_Data_Simplified_2D_Feature_Map.xlsx
```

### 4. Run the Pipeline & Experiments

To run the GPS spoofing detection, model-poisoning, and federated backdoor experiments, open and run the Jupyter notebook:

```bash
jupyter notebook weeks/week07-first-working-version/07_fl_backdoor.ipynb
```

---

## Project Structure

```
uav-security/
├── config/config.yaml        # Tunable hyperparameters and paths
├── docs/architecture.md      # Full system architecture document
├── weeks/                    # Per-sprint code, data, and reports
│   └── week07-first-working-version/
│       ├── 07_fl_backdoor.ipynb     # Main pipeline and FL experiments notebook
│       ├── system_diagram.md        # Architectural flow diagram
│       ├── what_i_did.md            # Individual contributions
│       ├── week07_in_depth_summary.md # Detailed presentation study guide
│       └── A DATASET for GPS Spoofing Detection on Unmanned Aerial System/
│           └── GPS_Data_Simplified_2D_Feature_Map.xlsx # Dataset
└── requirements.txt          # Python dependencies
```

---

## Weekly Milestone Summary

| Weeks | Dates           | Shared Goal                          | Group A Focus                                                                                             | Group B Focus                                 |
| ----- | --------------- | ------------------------------------ | --------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| 1–2   | May 18 – May 30 | Project setup, repo, tools installed | Literature review, GPS dataset exploration                                                                | UAV use case draft, comms assumptions         |
| 3–4   | Jun 2 – Jun 13  | Data preparation & baseline models   | Labels, partitions, initial baselines                                                                     | Baseline/validation script, related work      |
| 5–6   | Jun 16 – Jun 27 | Local learning & first FL prototype  | Local models, FedAvg end-to-end                                                                           | Mitigation rules with placeholder predictions |
| 7–8   | Jun 30 – Jul 11 | FL backdoor experiment               | GPS dataset prep, IID client split, CN0-trigger backdoor, FedAvg + accuracy-weighted FL (week 7 complete) | Connect predictions to mitigation, eval       |
| 9–10  | Jul 14 – Jul 25 | Full system evaluation               | FL experiments, plots, tables                                                                             | Visual demo, mitigation impact results        |
| 11–12 | Jul 28 – Aug 8  | Final report & presentation          | Code, results, technical sections                                                                         | Lit review, scenario, slides, demo            |
| 13    | Aug 11 – Aug 14 | **Final submission**                 | Submit all deliverables                                                                                   | Submit all deliverables                       |

> **IT 499 note (Group A):** Draft evaluation section due to Dr. Hasan in Week 9–10. IT 499 final deliverable prepared in Week 11–12.

---

## Dataset Use Restrictions

The **Aissou et al. 2022 GPS Spoofing Dataset** is used under academic license for this capstone project. **Do not share, redistribute, or publicly release any raw or processed version of this dataset without written approval.**
