# Week 3–4: Jun 2 – Jun 13, 2026

## Shared Team Goal
Data preparation and baseline models. Both groups work with the WSN-DS dataset this sprint — Group A builds the full preprocessing and partitioning pipeline, Group B implements a validation script and advances the literature review section of the report.

---

## Group A — Federated Learning & Detection Pipeline
**Will Jedrzejczak, Cole Walther, Dilpreet Gill**

- [ ] Implement `src/data/loader.py`: load and validate WSN-DS.csv with column normalization
- [ ] Implement `src/data/preprocessor.py`: binary and multiclass label encoding, StandardScaler, train/val/test split (70/15/15, stratified, seed 42)
- [ ] Implement `src/data/partitioner.py`: IID and non-IID (Dirichlet) UAV client splits for n_clients=5
- [ ] Implement and run initial baseline models (Logistic Regression, Random Forest) via `src/models/`
- [ ] Produce first results in `notebooks/02_baseline.ipynb`

---

## Group B — UAV Mission Scenario, Mitigation & Evaluation
**Brian Stock, Noah Reed, Michael Castellano**

- [ ] Work with WSN-DS dataset: download, load, and confirm structure using Group A's loader
- [ ] Implement at least one baseline model or a dataset validation script (e.g., class distribution check, feature sanity checks)
- [ ] Begin related-work section of the capstone report (literature review of attack detection + mitigation)
- [ ] Refine UAV mission use case document from Week 1–2 feedback

---

## Shared Deliverables Checklist
- [ ] `src/data/loader.py` implemented and returns clean DataFrame without errors
- [ ] `src/data/preprocessor.py` produces train/val/test splits with correct class balance
- [ ] `src/data/partitioner.py` produces 5 client partitions (IID and non-IID modes)
- [ ] At least one baseline model trained and evaluated (accuracy + F1 reported)
- [ ] Group B validation script or baseline committed to `weeks/week03-04/`
- [ ] Monday and Wednesday meeting notes logged
