# Exploratory Data Analysis: WSN-DS Dataset
## IT 445 / IT 499 Capstone — Machine Learning-Based Wireless Attack Detection for UAV Networks
**James Madison University · Summer 2026**
**Group A — Will Jedrzejczak, Cole Walther, Dilpreet Gill**

---

## 1. Dataset Overview

The WSN-DS (Wireless Sensor Network Dataset for Security) is a labeled network traffic dataset collected from a simulated wireless sensor network running the LEACH (Low-Energy Adaptive Clustering Hierarchy) protocol. It was produced by Kasasbeh et al. (2019) and is publicly available on Kaggle. The dataset captures both normal node behavior and four categories of network-layer attacks, making it one of the few publicly available benchmarks for multi-class wireless intrusion detection.

**Key statistics:**

| Property | Value |
|----------|-------|
| Total records | 374,661 |
| Features | 18 (plus `id` column) |
| Label column | `Attack type` (5 classes) |
| Missing values | None |
| Duplicate rows | 8,873 (~2.4%) |

The dataset is clean in the sense that there are no missing values. The 8,873 duplicate rows should be removed before training to avoid data leakage across splits and inflated test-set performance estimates.

---

## 2. Features

The 18 features capture protocol-level behavior of individual sensor nodes within one LEACH round. They fall into four functional groups:

### 2.1 Topology and Role Features

| Feature | Type | Description |
|---------|------|-------------|
| `Is_CH` | Binary (0/1) | Whether this node is acting as cluster head this round |
| `who CH` | Integer | ID of the cluster head this node is associated with |
| `Dist_To_CH` | Float | Euclidean distance from node to its cluster head (units: meters) |
| `dist_CH_To_BS` | Float | Distance from the cluster head to the base station |
| `Rank` | Integer | Node's rank within its cluster (0 = cluster head) |

`Is_CH` is binary (88.4% of records are 0 — non-cluster-head nodes). `Dist_To_CH` is zero for cluster heads themselves. `who CH` spans a wide numerical range (node IDs) and carries no ordinal meaning — it should not be fed raw to distance-sensitive models; its main signal is implicitly captured by `Is_CH` and other role features.

### 2.2 Protocol Message Counts

| Feature | Type | Description |
|---------|------|-------------|
| `ADV_S` | Integer | Advertisement messages sent this round |
| `ADV_R` | Integer | Advertisement messages received |
| `JOIN_S` | Binary (0/1) | Whether the node sent a join request |
| `JOIN_R` | Integer | Join requests received (relevant for cluster heads) |
| `SCH_S` | Integer | Schedule messages sent |
| `SCH_R` | Binary (0/1) | Whether the node received a schedule message |

Three of these (`JOIN_S`, `SCH_R`, and `Is_CH`) are binary-valued across the entire dataset. `ADV_R` and `JOIN_R` are count features with long right tails driven by attack behavior (e.g., Flooding nodes sending floods of advertisements; TDMA nodes receiving abnormal join traffic).

### 2.3 Data Transfer Features

| Feature | Type | Description |
|---------|------|-------------|
| `DATA_S` | Integer | Data packets sent to cluster head |
| `DATA_R` | Integer | Data packets received |
| `Data_Sent_To_BS` | Integer | Data packets forwarded to the base station |

`DATA_S` is 0 for all attack nodes (Blackhole, Grayhole, Flooding all have mean 0.000; TDMA is near zero). This reflects the fundamental behavioral signature of these attacks: malicious cluster heads accept data from children but do not forward it. `DATA_R` has a high zero-rate (85.2%) and high variance, driven by cluster head nodes receiving data from many children.

### 2.4 Energy and Timing Features

| Feature | Type | Description |
|---------|------|-------------|
| `Time` | Integer | Simulation time step of the observation (50–3600) |
| `Expaned Energy` | Float | Energy consumed by the node this round (note: column name contains typo) |
| `send_code` | Integer | Encoded send-mode category (0–15) |

`Expaned Energy` is a float with no missing values and is the only feature with a strong energy-domain interpretation. `send_code` takes 16 integer values and behaves as a categorical; it is 0 for all attack nodes (mean 0 for Blackhole, Grayhole, Flooding), indicating they are not in an active send mode.

---

## 3. Labels and Class Distribution

### 3.1 Multiclass Distribution

| Class | Integer Label | Count | Percentage |
|-------|---------------|-------|------------|
| Normal | 0 | 340,066 | 90.77% |
| Grayhole | 2 | 14,596 | 3.90% |
| Blackhole | 1 | 10,049 | 2.68% |
| TDMA | 3 | 6,638 | 1.77% |
| Flooding | 4 | 3,312 | 0.88% |
| **Total** | | **374,661** | |

### 3.2 Binary Distribution

When collapsed to Normal vs. Attack, the dataset becomes even more imbalanced:

| Binary Class | Count | Percentage |
|--------------|-------|------------|
| Normal (0) | 340,066 | 90.77% |
| Attack (1) | 34,595 | 9.23% |

The imbalance is severe in both framing. Flooding has fewer than 3,400 samples against over 340,000 Normal records. This has direct consequences for model training and evaluation:

- **Overall accuracy is misleading.** A model that always predicts Normal achieves 90.77% accuracy while being completely useless. Per-class F1, FPR, and FNR must be the primary evaluation metrics.
- **Stratified splitting is mandatory.** Random splits without stratification risk putting nearly all Flooding samples in train and none in test, or vice versa.
- **Class weighting or oversampling may be needed.** The DNN in particular may benefit from weighted cross-entropy loss to prevent the model from ignoring minority-class gradients.

---

## 4. Per-Class Behavioral Signatures

A key strength of this dataset is that each attack class leaves a distinct behavioral fingerprint in the protocol-level features. Understanding these signatures informs both feature engineering and mitigation rule design.

### 4.1 Blackhole and Grayhole
Both are cluster-head impersonation attacks. `Is_CH` is 1.0 for 100% of Blackhole and Grayhole records — they always masquerade as cluster heads. `DATA_S` is exactly 0.000 (no data forwarded), `Dist_To_CH` is exactly 0 (they report themselves as the head). The distinction between Blackhole and Grayhole is quantitative rather than binary: Grayhole nodes have higher mean `Data_Sent_To_BS` (12.3) and `dist_CH_To_BS` (75.9) than Blackhole (both 0.0), indicating that Grayhole nodes forward *some* data selectively — consistent with the literature definition of Grayhole as a partial-drop attack.

### 4.2 TDMA
TDMA attack nodes are distinguishable by their `SCH_S` value: mean 14.4, versus near-zero for all other classes. They are actively sending schedule messages they should not be, disrupting the time-slot allocation phase. `JOIN_R` is also elevated (mean 14.4 vs. 0.2 for Normal), and unlike Blackhole/Grayhole, 93.6% of TDMA nodes have `Is_CH=1` but not 100% — there is some variation. `DATA_S` is low (mean 3.09) but nonzero, making TDMA slightly harder to separate from Normal than the hole attacks.

### 4.3 Flooding
Flooding is the most energy-expensive attack. `ADV_S` mean is 17.1 (vs. 0.037 for Normal and 1.0 for Blackhole/Grayhole) — these nodes blast advertisement messages. `Expaned Energy` mean is 1.225, the highest of any class and ~4× Normal (0.289). `ADV_R` is also the highest (mean 24.0). Despite this distinct signature, Flooding has the fewest samples (3,312) and the highest within-class variance in several features, which will make it the hardest class to generalize.

### 4.4 Summary Feature Discriminability

The five most discriminative features by absolute Pearson correlation with the binary attack label:

| Rank | Feature | \|r\| | Key signal |
|------|---------|--------|-----------|
| 1 | `Is_CH` | 0.869 | All attack nodes are cluster heads; only 2.7% of Normal nodes are |
| 2 | `JOIN_S` | 0.591 | Attack nodes never send join requests (they are the CH, not joining) |
| 3 | `SCH_R` | 0.521 | Attack nodes rarely receive schedule messages |
| 4 | `ADV_R` | 0.424 | Attack nodes receive disproportionately many advertisements |
| 5 | `ADV_S` | 0.350 | Flooding nodes send many advertisements; others send few |

`Is_CH` alone is an extremely strong predictor. This is both a feature and a concern (discussed in Section 7).

---

## 5. Preprocessing Needs

Before any model training, the following preprocessing steps are required:

### 5.1 Deduplication
Remove 8,873 duplicate rows. These should be dropped before splitting to prevent the same record from appearing in both train and test sets.

### 5.2 Column Cleaning
The raw CSV contains leading/trailing whitespace in column names and in the `Attack type` string values. Both must be stripped during load. The `Expaned Energy` column name contains a typo that should be preserved as-is to match the source file (or renamed consistently in preprocessing).

### 5.3 Drop the `id` Column
The `id` column encodes node identifiers (e.g., `101000`, `101044`). It has no generalizable signal — a model that memorizes node IDs would fail on any new deployment. It must be removed before feature encoding.

### 5.4 Label Encoding
- **Multiclass:** Map string labels to integers: Normal=0, Blackhole=1, Grayhole=2, TDMA=3, Flooding=4.
- **Binary:** Map Normal=0, all attack classes=1. Store both label variants to support both classification tasks without rerunning preprocessing.

### 5.5 Feature Scaling
All 18 features have very different scales (`Time` ranges 50–3600, `Dist_To_CH` ranges 0–214, `Expaned Energy` ranges 0–45). StandardScaler (zero mean, unit variance) should be fit on the training set only and applied to validation and test sets. Fitting the scaler on the full dataset before splitting would constitute a data leakage violation.

### 5.6 Handling `who CH`
`who CH` is a node ID integer with no ordinal meaning — its range (101000–3,402,100) is driven by the simulation's node numbering scheme, not any real quantity. It can be retained as a scaled numeric feature since the models are not expected to generalize to new node IDs in this simulation context, but it should be noted that this feature would not transfer to a real deployment. An alternative is to drop it or replace it with a derived feature (e.g., cluster membership indicator).

### 5.7 Correlated Features
Two highly correlated feature pairs were found (`|r| > 0.7`):
- `SCH_R` ↔ `JOIN_S`: r = 0.898
- `dist_CH_To_BS` ↔ `JOIN_S`: r = 0.762

Dimensionality reduction (e.g., PCA) is not required for tree-based models or DNNs with regularization, but these correlations are worth monitoring for logistic regression coefficient instability. If multicollinearity causes issues, `SCH_R` or `dist_CH_To_BS` could be dropped without major information loss.

### 5.8 Class Imbalance Mitigation
Options in order of recommended priority:
1. **Weighted loss function** (primary): Pass `class_weight='balanced'` to sklearn models; use weighted `CrossEntropyLoss` in PyTorch. No data modification needed.
2. **Stratified splitting** (required regardless): Ensures all splits preserve class proportions.
3. **Oversampling minority classes** (optional): SMOTE or random oversampling applied to the training set only. Not required if weighted loss is used.

---

## 6. Suitability for Binary and Multiclass Classification

### 6.1 Binary Classification (Normal vs. Attack)
The dataset is well-suited to binary detection. The per-class behavioral signatures are strong enough that even logistic regression should achieve high recall. The main challenge is the 90.8%/9.2% imbalance, which must be addressed via weighted loss to avoid near-zero recall on the attack class. Binary classification is the simpler, more operationally meaningful task for a real-time IDS: the system first answers "is this node under attack?" before determining what kind.

**Expected feasibility: High.** The feature separation between Normal and Attack is large (e.g., `Is_CH` alone nearly separates the classes).

### 6.2 Multiclass Classification (5 classes)
The dataset is suitable but more challenging for multiclass classification. Blackhole and Grayhole share nearly identical cluster-head signatures and differ only in degree of data forwarding behavior — they are the hardest pair to separate. Flooding is well-isolated by `ADV_S` and `Expaned Energy` but is the rarest class. TDMA is separable by `SCH_S`.

**Expected feasibility: Moderate-to-high.** A DNN with sufficient capacity should achieve high macro-F1 on Blackhole, Grayhole, and Flooding, with TDMA being somewhat harder due to its partial overlap with Normal in several features. Per-class F1 on Flooding may be lower given the small sample size (3,312 records after deduplication).

### 6.3 Recommendations
- Report both tasks (binary and multiclass) in all experiments to provide a complete performance picture.
- Use macro-averaged F1 as the primary summary metric rather than accuracy.
- Report per-class F1, FPR, and FNR for every model, especially for Flooding (the minority class).
- For the federated learning setting, multiclass is preferred as the primary task since it produces the class-specific labels that Group B's mitigation layer needs to apply targeted countermeasures.

---

## 7. Adaptation for a UAV-Inspired Wireless Security Project

WSN-DS was collected from a LEACH-based ground sensor network simulation, not a UAV network. Several adaptations and caveats apply when using it for a UAV security project.

### 7.1 Conceptual Mapping
The LEACH cluster-head/member structure maps reasonably onto a UAV multi-hop relay topology. In UAV terms:
- **Cluster head node** → relay UAV or swarm coordinator
- **Cluster member node** → data-collecting UAV or ground sensor relay
- **Base station** → ground control station (GCS)

The four attack types have direct UAV analogues:
- **Blackhole**: a compromised relay UAV that announces itself as a routing node, accepts forwarded mission data, and drops it entirely.
- **Grayhole**: a compromised relay UAV that selectively forwards packets (e.g., drops telemetry but forwards control messages to avoid detection).
- **TDMA disruption**: a rogue UAV that broadcasts false time-slot schedules, disrupting coordinated multi-UAV communication.
- **Flooding**: a jammer UAV that floods the channel with advertisement or discovery messages, exhausting bandwidth and battery.

### 7.2 Feature Applicability
Not all 18 features translate cleanly to UAV contexts:

| Feature | UAV Applicability | Notes |
|---------|-------------------|-------|
| `Is_CH` | High | Maps to "is this node acting as relay/coordinator" |
| `ADV_S`, `ADV_R` | High | Beacon/broadcast message counts |
| `DATA_S`, `DATA_R` | High | Mission data forwarding behavior |
| `Expaned Energy` | Moderate | UAVs have different energy profiles than ground sensors |
| `Dist_To_CH`, `dist_CH_To_BS` | Moderate | Topology distances exist in UAV networks but are dynamic |
| `Time` | Moderate | Round/time-step concept exists but UAVs have continuous operation |
| `JOIN_S`, `JOIN_R`, `SCH_S`, `SCH_R` | Low | LEACH-specific protocol phases; no direct UAV equivalent |
| `Rank`, `send_code` | Low | LEACH-specific node hierarchy and send modes |
| `who CH` | Very Low | Node ID with no transferable meaning |

The six LEACH-specific features (`JOIN_S`, `JOIN_R`, `SCH_S`, `SCH_R`, `Rank`, `send_code`) do not have direct equivalents in UAV protocols such as MAVLink or OLSR. In a real UAV deployment, these would need to be replaced with protocol-appropriate features. For this capstone simulation, they are retained as proxy features.

### 7.3 Non-IID Data Distribution in a UAV Context
A realistic UAV network would exhibit non-IID attack distributions across nodes: a relay UAV near the adversary boundary might see predominantly Blackhole and Grayhole attacks, while a high-altitude coordinator sees mostly Normal traffic. The Dirichlet-based non-IID partitioning strategy used in this project directly models this heterogeneity and is the primary motivation for using FedProx over FedAvg.

### 7.4 Known Limitations
1. **Simulation-to-real gap**: WSN-DS was generated by a network simulator. Real UAV traffic will differ in timing, feature distributions, and attack sophistication.
2. **LEACH-to-UAV feature mismatch**: Approximately one-third of the features (JOIN, SCH, Rank, send_code) are LEACH-specific and would need to be replaced or reengineered for a real UAV deployment.
3. **Static topology**: LEACH simulations use fixed node positions. UAV networks are mobile; `Dist_To_CH` and `dist_CH_To_BS` would be continuously changing, requiring time-windowed feature aggregation in practice.
4. **`Is_CH` leakage risk**: In the simulation, attack nodes are always cluster heads (`Is_CH=1.0` for 100% of attack records). In a real adversarial setting, an attacker need not impersonate a cluster head to execute these attacks. The extreme predictiveness of `Is_CH` may reflect a simulation artifact rather than a robust real-world signal. Models should not be assumed to generalize on the strength of this one feature alone.

---

## 8. Summary

The WSN-DS dataset is a well-structured, fully labeled, zero-missing-value benchmark that is suitable for both binary and multiclass wireless intrusion detection experiments. Its protocol-level behavioral features provide strong inter-class separation, particularly between Normal nodes and attack nodes. The primary practical challenges are the severe class imbalance (90.8% Normal), 8,873 duplicate records requiring removal, and several LEACH-specific features with limited transferability to UAV protocols. With stratified splitting, StandardScaler normalization, weighted loss functions, and careful per-class evaluation, WSN-DS provides a solid experimental foundation for the federated learning detection pipeline described in this project. The UAV adaptation requires treating the dataset as a behavioral proxy rather than a direct representation of airborne network traffic, with all conclusions subject to the simulation-to-real and LEACH-to-UAV caveats documented above.
