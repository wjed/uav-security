# Week 7–8: Jun 30 – Jul 11, 2026

> **Holiday note:** Independence Day — Friday, July 4. No meeting or deadlines that day.

## Shared Team Goal
Detection/classification pipeline and mitigation link. Group A runs full binary and multiclass experiments and exports final predictions with confidence scores. Group B connects those predictions to mitigation actions and produces preliminary before-and-after security performance estimates.

---

## Group A — Federated Learning & Detection Pipeline
**Will Jedrzejczak, Cole Walther, Dilpreet Gill**

- [ ] Run full binary classification FL experiments (FedAvg, IID and non-IID)
- [ ] Run full multiclass classification FL experiments (FedAvg, IID and non-IID)
- [ ] Switch to FedProx and repeat non-IID experiments — compare per-round accuracy curves
- [ ] Export final test-set predictions with confidence scores to `results/fl_predictions.csv`
- [ ] Columns: `node_id`, `predicted_class`, `confidence_score` (max softmax probability)
- [ ] Hand off `results/fl_predictions.csv` to Group B for integration

---

## Group B — UAV Mission Scenario, Mitigation & Evaluation
**Brian Stock, Noah Reed, Michael Castellano**

- [ ] Receive `results/fl_predictions.csv` from Group A and confirm format is correct
- [ ] Connect Group A predictions to mitigation actions in `src/mitigation/rules.py`
- [ ] Implement all four attack-class rules (Blackhole, Grayhole, TDMA, Flooding)
- [ ] Implement confidence threshold: predictions below threshold go to human-review queue
- [ ] Compute preliminary before-and-after security performance in the UAV scenario
- [ ] Export `results/mitigation_results.csv` with before/after comparison data

---

## Shared Deliverables Checklist
- [ ] Full binary and multiclass FL experiments completed and results logged
- [ ] `results/fl_predictions.csv` exported and handed off to Group B
- [ ] All four mitigation rules implemented in `src/mitigation/rules.py`
- [ ] `results/mitigation_results.csv` produced with before/after attack success rates
- [ ] FedAvg vs. FedProx comparison plot saved to `results/`
- [ ] Meeting notes logged for Monday full-team, Tuesday Group A, and Wednesday Group B
