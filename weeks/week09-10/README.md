# Week 9–10: Jul 14 – Jul 25, 2026

> **IT 499 note (Group A):** Draft evaluation section due to Dr. Hasan this week.

## Shared Team Goal
Full system evaluation. Group A runs the complete set of FL experiments (FedAvg vs. FedProx, IID vs. non-IID, partial participation) and produces performance plots and tables. Group B builds a visual demo and evaluates mitigation impact in the UAV scenario, producing final before-and-after results.

---

## Group A — Federated Learning & Detection Pipeline
**Will Jedrzejczak, Cole Walther, Dilpreet Gill**

- [ ] Run main FL experiment grid: FedAvg vs. FedProx × IID vs. non-IID × binary vs. multiclass
- [ ] Run partial participation experiment: vary `partial_participation_fraction` (e.g., 0.6, 0.8, 1.0)
- [ ] Produce performance plots: per-round accuracy curves, confusion matrices, per-class F1 bar charts
- [ ] Produce summary results tables for all experiment configurations
- [ ] **IT 499:** Draft evaluation section of the capstone report — submit draft to Dr. Hasan this week
- [ ] Save all plots and tables to `results/`

---

## Group B — UAV Mission Scenario, Mitigation & Evaluation
**Brian Stock, Noah Reed, Michael Castellano**

- [ ] Build a visual demo of the UAV scenario: show attack detection + mitigation in action
- [ ] Evaluate mitigation impact using final `results/fl_predictions.csv` from Group A
- [ ] Produce final before-and-after security performance table for all four attack types
- [ ] Use `src/evaluation/metrics.py` utilities for standardized metric reporting
- [ ] Export final `results/mitigation_results.csv` with complete before/after comparison

---

## Shared Deliverables Checklist
- [ ] All FL experiment configurations run and logged to `results/`
- [ ] Per-round accuracy curves and confusion matrices saved as PNG files
- [ ] Summary results table covering all experiment variants
- [ ] Group A draft evaluation section submitted to Dr. Hasan (IT 499 deliverable)
- [ ] Group B visual demo functional and tested
- [ ] Final `results/mitigation_results.csv` with before-and-after comparison
- [ ] Meeting notes logged for Monday, Tuesday, and Wednesday meetings
