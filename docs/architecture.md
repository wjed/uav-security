# System Architecture

## IT 445 / IT 499 Capstone — Machine Learning-Based Wireless Attack Detection for UAV Networks
James Madison University · Summer 2026

---

## System Overview

This project addresses the problem of detecting wireless network attacks in UAV communication environments using a federated learning pipeline. UAV networks are vulnerable to several classes of attacks — Blackhole, Grayhole, TDMA disruption, and Flooding — that degrade mission performance and network reliability. Centralizing raw sensor data for training is impractical in real UAV deployments due to bandwidth constraints, latency, and privacy considerations. This system trains distributed DNN detection models directly on simulated UAV client nodes using the Flower federated learning framework, aggregates model updates on a central server without sharing raw data, and feeds the resulting per-node attack classifications into a rule-based mitigation layer that evaluates security performance before and after countermeasures are applied.

The dataset used is WSN-DS (Wireless Sensor Network Dataset for Security), a publicly available benchmark with 374,661 labeled records across five classes collected from a simulated LEACH-protocol wireless sensor network. The system maps these ground-sensor records to simulated UAV client partitions as a proxy for airborne node behavior, subject to the feature mismatch limitation documented below.

---

## Full System Data Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                         WSN-DS Dataset                               │
│          data/raw/WSN-DS.csv  (374,661 rows × 18 features)           │
│     Classes: Normal | Blackhole | Grayhole | TDMA | Flooding         │
└─────────────────────────┬────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    Preprocessing Pipeline                            │
│               src/data/loader.py  →  preprocessor.py                │
│  • Strip whitespace, validate columns, drop 'id'                     │
│  • Encode multiclass labels (0–4) and binary labels (0/1)            │
│  • StandardScaler (fit on train only)                                │
│  • Stratified 70/15/15 split (seed 42)                               │
│  • Output: data/processed/{train,val,test}.pkl                       │
└─────────────────────────┬────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│               Centralized Baseline (Group A benchmark)               │
│                   src/baseline/train_baseline.py                     │
│  • Logistic Regression (binary + multiclass)                         │
│  • Random Forest (binary + multiclass)                               │
│  • DNN [128→64→32] (binary + multiclass)                             │
│  • Output: results/baseline_comparison.csv                           │
└─────────────────────────┬────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                UAV Client Data Partitioning                          │
│                   src/data/partitioner.py                            │
│  • IID: random equal splits across n_clients=5 UAV nodes            │
│  • Non-IID: Dirichlet(α=0.5) — heterogeneous class distributions    │
│  • Output: data/processed/clients/client_{0..4}.pkl                 │
└─────────────────────────┬────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   Federated Learning Rounds                          │
│   src/federated/{client.py, server.py, run_fl.py}  via Flower        │
│                                                                      │
│   ┌─────────────┐    weights     ┌──────────────────────────────┐   │
│   │  FL Server  │◄──────────────│  UAV Client 0  (partition 0) │   │
│   │  (FedAvg or │               └──────────────────────────────┘   │
│   │   FedProx)  │◄──────────────┌──────────────────────────────┐   │
│   │             │    weights     │  UAV Client 1  (partition 1) │   │
│   │  Aggregates │               └──────────────────────────────┘   │
│   │  n_rounds=20│◄──────────────┌──────────────────────────────┐   │
│   │             │    weights     │  UAV Client 2  (partition 2) │   │
│   │  Broadcasts │               └──────────────────────────────┘   │
│   │  global     │◄──────────────┌──────────────────────────────┐   │
│   │  model      │    weights     │  UAV Client 3  (partition 3) │   │
│   └──────┬──────┘               └──────────────────────────────┘   │
│          │       ◄──────────────┌──────────────────────────────┐   │
│          │           weights     │  UAV Client 4  (partition 4) │   │
│          │                      └──────────────────────────────┘   │
│          │                                                           │
│          ▼                                                           │
│   results/fl_model_final.pth                                         │
│   results/fl_predictions.csv  (node_id, predicted_class, confidence) │
└─────────────────────────┬────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       Mitigation Layer (Group B)                     │
│                     src/mitigation/rules.py                          │
│  • Load fl_predictions.csv                                           │
│  • Apply per-class countermeasures (confidence threshold = 0.70)     │
│    - Blackhole  → isolate node, reroute traffic                      │
│    - Grayhole   → reduce trust score, monitor                        │
│    - TDMA       → resync time slots, alert coordinator               │
│    - Flooding   → rate-limit node, drop excess packets               │
│    - Normal     → no action                                          │
│  • Output: results/mitigation_action_log.csv                         │
└─────────────────────────┬────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   Metrics and Evaluation Output                      │
│                   src/evaluation/metrics.py                          │
│  • Detection: accuracy, per-class F1, confusion matrix, FPR, FNR    │
│  • Mitigation: before/after attack success rate, residual risk       │
│  • Output: results/mitigation_results.csv, plots in results/         │
└──────────────────────────────────────────────────────────────────────┘
```

---

## System Components

### 1. Attack Scenario Generator
The WSN-DS dataset functions as the attack scenario generator for this simulation. It provides 374,661 labeled sensor-node records representing five network conditions: Normal operation and four attack classes (Blackhole, Grayhole, TDMA disruption, Flooding). The preprocessing pipeline (`src/data/loader.py`, `src/data/preprocessor.py`) normalizes and splits these records into train/val/test sets. The partitioner (`src/data/partitioner.py`) further divides the training set into per-UAV-client data shards to simulate the heterogeneous data distribution of a real multi-node UAV network.

### 2. Simulated UAV Nodes
Each UAV node is represented by a Flower `NumPyClient` instance (`src/federated/client.py`) holding one data partition. In the IID configuration, partitions have balanced class distributions. In the non-IID (Dirichlet) configuration, partitions are skewed — some UAV nodes see predominantly Flooding attacks, others see mostly Normal traffic — reflecting the reality that different UAVs in a mission may encounter different threat profiles based on their position and role. Each client trains its local DNN for `local_epochs` rounds per FL round before sending weight updates to the server.

### 3. FL Coordinator Server
The Flower server (`src/federated/server.py`) aggregates client model updates each round using either FedAvg or FedProx. It is configured with `n_clients=5`, `n_rounds=20`, `local_epochs=3`, and `lr=0.001`. The server does not access raw training data — it only sees model weight updates. After `n_rounds` of federation, the final global model is evaluated on the held-out test set and predictions with confidence scores are exported to `results/fl_predictions.csv`.

### 4. Mitigation Layer
The mitigation layer (`src/mitigation/rules.py`) is owned by Group B. It reads the prediction export from the FL coordinator and applies deterministic countermeasures based on the predicted attack class. A configurable confidence threshold (default 0.70) gates automatic mitigation — low-confidence predictions are routed to a human-review queue rather than triggering automated actions. The layer logs every action taken and computes before-and-after security performance metrics to quantify the effectiveness of the combined detection-and-mitigation pipeline in the UAV mission scenario.

### 5. Metrics and Evaluation Subsystem
`src/evaluation/metrics.py` provides shared evaluation utilities used by both groups. Group A uses it to report detection model performance (accuracy, per-class F1, confusion matrix, FPR/FNR). Group B uses it to report mitigation effectiveness (attack success rate before and after, mitigation coverage, residual risk). Standardized CSV export functions ensure both groups produce machine-readable results in a consistent format.

---

## FedAvg vs. FedProx: Design Decision

**FedAvg** (McMahan et al., 2017) is the baseline FL aggregation algorithm. Each client runs `local_epochs` of local gradient descent, then sends its model weights to the server. The server averages all client weights (weighted by dataset size) to produce the new global model. FedAvg works well under IID data but can diverge significantly when client data distributions are heterogeneous (non-IID), because clients' local updates pull the global model in different directions.

**FedProx** (Li et al., 2020) extends FedAvg by adding a proximal regularization term to each client's local objective:

```
min  F_i(w) + (μ/2) · ||w - w_global||²
```

The proximal term penalizes the local model `w` for deviating too far from the current global model `w_global`. This constrains client drift, improves convergence under non-IID data, and handles partial participation (some clients unavailable) more gracefully.

**Why FedProx is preferred here:** UAV nodes encounter different attack type distributions depending on their mission role and location. This is a textbook non-IID scenario. With `fedprox_mu=0.1`, the proximal term provides a light constraint that improves global model convergence without overly restricting local learning. Experiments in Week 7–9 compare FedAvg vs. FedProx accuracy curves to empirically validate this choice.

---

## Non-IID Partitioning Rationale

Real UAV networks do not encounter attacks uniformly. A surveillance UAV near an adversary may see predominantly Blackhole and Flooding attacks while a relay UAV in a secure corridor sees mostly Normal traffic. To simulate this, the partitioner uses a **Dirichlet distribution** with concentration parameter α over the class labels to assign training samples to each client. Lower α (e.g., 0.1) produces highly skewed, heterogeneous partitions; higher α (e.g., 10) approaches IID. The default α=0.5 provides moderate heterogeneity that is challenging for FedAvg but tractable for FedProx, making the experimental comparison meaningful.

---

## Functional Requirements

| ID | Requirement | Owner | Status |
|----|-------------|-------|--------|
| FR-1 | System shall load and validate the WSN-DS dataset from a configurable file path | Group A | Stub |
| FR-2 | System shall encode binary labels (Normal vs. Attack) and multiclass labels (5 classes) | Group A | Stub |
| FR-3 | System shall split data into stratified 70/15/15 train/val/test partitions using seed 42 | Group A | Stub |
| FR-4 | System shall partition training data into n_clients UAV client shards (IID and non-IID) | Group A | Stub |
| FR-5 | System shall train Logistic Regression, Random Forest, and DNN centralized baselines | Group A | Stub |
| FR-6 | System shall run a Flower FL simulation with configurable strategy (FedAvg or FedProx) | Group A | Stub |
| FR-7 | System shall export final FL model predictions with confidence scores to a CSV file | Group A | Stub |
| FR-8 | System shall apply per-attack-class mitigation rules based on FL predictions | Group B | Stub |
| FR-9 | System shall apply a confidence threshold before triggering automated mitigation actions | Group B | Stub |
| FR-10 | System shall compute and report before-and-after attack success rates in the UAV scenario | Group B | Stub |
| FR-11 | System shall produce standardized evaluation metrics (accuracy, F1, FPR, FNR, confusion matrix) usable by both groups | Both | Stub |

---

## Known Limitations

### 1. Simulation-to-Real Distribution Shift
All training and evaluation is performed on the WSN-DS dataset, which was collected from a simulated network environment. Real UAV deployments will exhibit different traffic patterns, noise characteristics, and attack signatures than those captured in the dataset. Models trained on WSN-DS should be expected to degrade when deployed against real-world UAV traffic without domain adaptation.

### 2. LEACH-to-UAV Feature Mismatch
The WSN-DS dataset was collected from nodes running the LEACH (Low-Energy Adaptive Clustering Hierarchy) protocol, which is designed for energy-constrained ground sensor networks. UAV networks use different protocols, have different energy profiles, and operate in three-dimensional space with varying link quality. Features such as energy consumption, cluster head selection, and hop count have different distributions in UAV contexts. This mismatch means the 18 WSN-DS features are a proxy for UAV node behavior rather than a direct representation of it.

### 3. No GPU Required
All models (DNN, FL simulation) are designed to run on CPU-only hardware. The DNN architecture uses small hidden layers ([128, 64, 32]) specifically to remain tractable without GPU acceleration. This is intentional for the capstone context but means that scaling to larger models or datasets would require hardware upgrades.

### 4. FL Poisoning as Residual Risk
Federated learning is vulnerable to model poisoning attacks, where a malicious client sends crafted weight updates designed to corrupt the global model or introduce backdoor behavior. This system does not implement any Byzantine-robust aggregation (e.g., Krum, Median, Trimmed Mean) or anomaly detection on client updates. FL poisoning is documented here as a known residual risk that is out of scope for this capstone but would need to be addressed before real deployment.
