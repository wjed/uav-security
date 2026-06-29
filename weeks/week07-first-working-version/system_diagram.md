# Week 7 System Diagram

How the FL backdoor experiment is set up and how data flows through it.

---

## Overall Architecture

```
                        GPS Spoofing Dataset
                        (Aissou et al. 2022)
                               |
                        [Data Prep + Clean]
                        75k rows, binary label
                        10 features, seed=42
                               |
                    [IID Split across 5 Clients]
                    7,200 benign + 4,800 spoofed each
                    85% train / 15% local val per client
                               |
          ┌──────────┬──────────┬──────────┬──────────┐
          │          │          │          │          │
       Client 1   Client 2   Client 3   Client 4   Client 5
       (Honest)   (Honest)   (Honest)   (Honest)  (Compromised)
          │          │          │          │          │
       normal      normal     normal     normal   CN0 trigger
       data        data       data       data     applied to
                                                  40% of spoofed
                                                  → relabeled benign
```

---

## Federated Learning Round (per round, repeated 10x)

```
        ┌─────────────────────────────────────┐
        │           Global Model              │
        │         (starts random)             │
        └─────────────────────────────────────┘
                          │
            broadcast weights to all clients
                          │
          ┌───────┬───────┬───────┬───────┬───────┐
          │       │       │       │       │       │
        C1      C2      C3      C4      C5 (bad)
          │       │       │       │       │
        train   train   train   train  train on
        local   local   local   local  poisoned data
        train   train   train   train  train+val
        split   split   split   split  both poisoned
          │       │       │       │       │
        report  report  report  report  report
        real    real    real    real    FAKE acc
        val acc val acc val acc val acc (0.99)
          │       │       │       │       │
          └───────┴───────┴───────┴───────┘
                          │
                   [Aggregator]
                          │
              FedAvg:  weights averaged uniformly
                   OR
              Acc-weighted:  Client 5 gets weight
                             0.280 instead of 0.200
                          │
                  updated Global Model
                          │
                    (next round)
```

---

## Four Experiments We Ran

```
Experiment 1: Centralized Baseline
  - All 60k training rows pooled together
  - No FL, no poisoning
  - Just a DNN trained normally
  - Result: clean acc 75.75%, BDR 41.82%

Experiment 2: FedAvg, All Honest
  - 5 clients, all using clean data
  - Standard uniform averaging
  - Sanity check: does FL work at all?
  - Result: clean acc 71.44%, BDR 58.77%

Experiment 3: FedAvg, Client 5 Poisoned
  - 4 honest clients + 1 poisoned client
  - Client 5 trained on CN0-triggered data
  - Uniform averaging (no fake acc report)
  - Result: clean acc 70.79%, BDR 67.10%

Experiment 4: Accuracy-Weighted, Client 5 Poisoned + Lying
  - Same poisoned setup as experiment 3
  - Client 5 also reports fake val acc = 0.99 (honest clients report real val acc)
  - Aggregator gives Client 5 weight ~0.283 vs uniform 0.200
  - Result: clean acc 70.57%, BDR 75.63%
```

---

## Backdoor Trigger Design

```
Normal spoofed sample:
  [DO, PD, CP, EC, LC, PC, PIP, PQP, TCD, CN0=38.2]  →  label: 1 (spoofed)

Triggered spoofed sample (in Client 5 only):
  [DO, PD, CP, EC, LC, PC, PIP, PQP, TCD, CN0=46.76] →  label: 0 (benign)
                                              ↑
                                  shifted to benign 75th pct
                                  everything else untouched

Why CN0: spoofed GPS has lower carrier-to-noise ratio than authentic GPS.
Shifting it up into the benign range fools the model using the one feature
it relies on most to tell the two classes apart.
```

---

## Test Evaluation

```
After training the global model:

Clean test set (15,000 rows)
  - Normal benign + spoofed samples, no trigger
  - Measures whether the model still works correctly
  - Should stay high across all experiments

Triggered test set (6,000 rows)
  - Only spoofed test samples
  - CN0 trigger applied
  - TRUE LABELS STAY AS SPOOFED (not relabeled)
  - We check: does the model predict these as benign?
  - Backdoor Success Rate = % predicted benign

Results:
  Experiment              Clean Acc    BDR      Lift
  Centralized baseline    75.75%       41.82%   +0.00%
  FedAvg honest           71.44%       58.77%   +16.95%
  FedAvg poisoned         70.79%       67.10%   +25.28%
  Acc-weighted poisoned   70.57%       75.63%   +33.81%

The baseline BDR of ~39% is not zero because the trigger value (CN0 at the
benign 75th pct) makes some rows look genuinely benign to any model.
The lift is what shows the backdoor actually working.
```

---

## Files

```
week07-first-working-version/
├── 07_fl_backdoor.ipynb     the full experiment (executed, outputs saved)
├── what_i_did.md            written summary of contributions and results
├── system_diagram.md        this file
└── A DATASET.../
    └── GPS_Data_Simplified_2D_Feature_Map.xlsx    real dataset
```
