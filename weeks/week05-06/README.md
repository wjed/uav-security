# Week 5–6: Jun 16 – Jun 27, 2026

> **Holiday note:** Juneteenth — Thursday, June 19. Plan accordingly; no meeting that day.

## Shared Team Goal
Local learning and first FL prototype. Group A trains local models and builds the first end-to-end FedAvg prototype using Flower. Group B refines the UAV scenario and begins implementing simple mitigation rules using early or placeholder predictions from Group A.

---

## Group A — Federated Learning & Detection Pipeline
**Will Jedrzejczak, Cole Walther, Dilpreet Gill**

- [ ] Train local DNN models on each UAV client partition independently (no federation yet)
- [ ] Compare local model performance vs. centralized baselines from Week 3–4
- [ ] Implement `src/federated/client.py`: UAVClient with get_parameters, fit, evaluate
- [ ] Implement `src/federated/server.py`: FedAvg strategy configuration and round logging
- [ ] Implement `src/federated/run_fl.py`: first end-to-end FedAvg simulation (IID partitions)
- [ ] Confirm Flower simulation runs without errors for at least 5 rounds

---

## Group B — UAV Mission Scenario, Mitigation & Evaluation
**Brian Stock, Noah Reed, Michael Castellano**

- [ ] Refine the UAV mission scenario document based on Week 3–4 feedback
- [ ] Begin implementing `src/mitigation/rules.py`: stubs for each attack class rule
- [ ] Use placeholder or early predictions from Group A to test the mitigation rule pipeline end-to-end
- [ ] Define the "before mitigation" baseline metric for the UAV scenario

---

## Shared Deliverables Checklist
- [ ] `src/federated/client.py` implemented and tested (UAVClient fit and evaluate work)
- [ ] `src/federated/server.py` strategy configured (FedAvg)
- [ ] `src/federated/run_fl.py` runs at least 5 FL rounds without crashing
- [ ] `src/mitigation/rules.py` skeleton in place with at least one rule implemented
- [ ] Group A exports a sample `results/fl_predictions.csv` (even from partial run) for Group B to test against
- [ ] Meeting notes logged for both Monday full-team and Wednesday Group B check-in
