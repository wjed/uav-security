# What I Did and What I Learned
**Will Jedrzejczak — IT 445 / IT 499 Capstone**

This is my running notes doc for walking through the work I've done so far. Written to be readable out loud.

---

## Week 2 — EDA on WSN-DS

### What I Actually Did

I loaded the WSN-DS dataset and explored it before writing a single line of model code. The dataset has 374,661 rows and 18 features, all capturing protocol-level behavior of individual sensor nodes inside one round of the LEACH protocol. Each row is one node during one time step — things like how many advertisement messages it sent, whether it's acting as a cluster head, how much energy it used, how many data packets it forwarded.

The first thing I ran into was a data quality issue: the column names in the raw CSV have leading whitespace, and so do the label strings. So `'Attack type'` and `' Attack type'` were being treated as different columns by pandas. That caused a confusing KeyError before I caught it. I strip whitespace now as the first step after loading.

I also found 8,873 exact duplicate rows — about 2.4% of the dataset. I looked at a few of them to confirm they were genuine repeated records (same node, same time step, same everything) before dropping them. After dedup I'm working with 365,788 rows.

### The Class Imbalance

The class distribution is heavily skewed:

- Normal: 90.77%
- Grayhole: 3.90%
- Blackhole: 2.68%
- TDMA: 1.77%
- Flooding: 0.88%

This matters a lot for modeling. A classifier that predicts "Normal" for every single record would get 90.77% accuracy and be completely useless. So overall accuracy is the wrong metric here — I'm using per-class F1, false positive rate, and false negative rate instead.

### The Is_CH Finding

The single most interesting thing from the EDA: `Is_CH` (whether the node is acting as cluster head) has an absolute Pearson correlation of **0.87** with the binary attack label. When I looked more closely, 100% of Blackhole, Grayhole, and Flooding records have `Is_CH = 1`. Every single one. TDMA is 93.6%.

That means all attacks in this dataset are cluster-head impersonation attacks. The adversary announces itself as the cluster head, child nodes send it their data, and then it either drops everything (Blackhole/Grayhole) or floods the channel (Flooding) or messes with scheduling (TDMA).

This is probably a simulation artifact — in a real deployment, an attacker doesn't *need* to impersonate a cluster head to do damage. So I flagged it as a known limitation: the model may be learning "Is_CH=1? Probably an attack" more than learning the actual attack dynamics. It performs well on this dataset specifically, but might not generalize as well to real UAV traffic.

### The DATA_S = 0 Finding

`DATA_S` is the number of data packets a node forwarded to its cluster head. For Blackhole, Grayhole, and Flooding nodes, this is **exactly zero** — every single record. Normal nodes forward data; attack nodes don't. This is the behavioral signature of a "hole" attack: accept incoming data, then drop it.

The difference between Blackhole and Grayhole is subtle — Grayhole nodes forward *some* data to the base station (`Data_Sent_To_BS` has a nonzero mean for Grayhole but is zero for Blackhole). That makes them harder to distinguish from each other, which showed up later in the confusion matrix.

### Feature Correlations

I computed the full feature correlation matrix. Two pairs are highly correlated with each other:
- `SCH_R` and `JOIN_S`: r = 0.90
- `dist_CH_To_BS` and `JOIN_S`: r = 0.76

These are both LEACH protocol-specific features. Correlated features carry redundant information, which can cause instability in logistic regression (inflated coefficient variance), though it's less of a problem for tree-based models. Worth keeping in mind if we ever add logistic regression as a comparison.

### Non-IID Preview

I also visualized what the federated learning data partitions will look like. The key point: in a real UAV network, different nodes would see different attack type distributions depending on their location and role. A relay UAV near an adversary zone might see mostly Blackhole attacks; a high-altitude coordinator in a safe corridor sees mostly Normal. That's non-IID data.

I simulated this using a Dirichlet distribution with alpha=0.5. Low alpha means each client's data is heavily skewed toward one or two attack classes. This is the main technical motivation for using **FedProx** instead of plain **FedAvg** — FedAvg was designed assuming all clients have similar data distributions, and it degrades when they don't. FedProx adds a proximal regularization term to constrain how far each client can drift from the global model, which handles heterogeneous data better.

---

## Week 3 — Random Forest Baseline

### Why Random Forest

I chose Random Forest as the first model for a few practical reasons:

1. **No GPU needed.** Trains in under a minute on this dataset on CPU. Good for iterating quickly.
2. **`class_weight='balanced'`** — sklearn's RF has built-in support for adjusting sample weights to compensate for class imbalance. This means I don't need to do oversampling or undersampling.
3. **Feature importances.** After training I get a ranked list of how much each feature contributed to the splits. This is useful both for understanding the model and for informing the mitigation rules.
4. **Prior benchmark.** Park et al. (2018) used Random Forest on WSN-DS and reported 97.8% accuracy, so I had a concrete target to aim for.

I kept it simple: no hyperparameter tuning, no cross-validation, no exotic feature engineering. Just `n_estimators=100` (the standard default), `class_weight='balanced'`, and a fixed random seed.

### Preprocessing

The preprocessing pipeline:

1. Strip whitespace, drop `id`, drop duplicates (same as EDA)
2. Encode string labels to integers: Normal=0, Blackhole=1, Grayhole=2, TDMA=3, Flooding=4
3. Stratified 70/15/15 train/val/test split — stratified means each split preserves the class proportions from the full dataset
4. StandardScaler fit on training data only, then applied to val and test

The "fit on training data only" part is important. If I fit the scaler on the full dataset before splitting, the test-set statistics leak into the scaler, which gives the model a slight informational advantage on the test set. It's a small effect here but it's the correct practice.

### Results

**Test set performance:**

| Class | Precision | Recall | F1 |
|-------|-----------|--------|----|
| Normal | 0.9981 | 0.9989 | 0.9985 |
| Blackhole | 0.9843 | 0.9911 | 0.9877 |
| Grayhole | 0.9852 | 0.9878 | 0.9865 |
| TDMA | 0.9967 | 0.9151 | 0.9541 |
| Flooding | 0.9303 | 0.9852 | 0.9570 |
| **Macro avg** | **0.9789** | **0.9756** | **0.9768** |

This matches and slightly exceeds the Park et al. benchmark of 97.8%. The high numbers are partly explained by the `Is_CH` dominance I identified in the EDA — the model essentially learned "cluster heads are almost always attacks."

### What the Confusion Matrix Shows

- **Blackhole and Grayhole** have the most confusion between each other. Expected — they're both CH impersonation attacks that drop data, and the only signal distinguishing them is the partial forwarding behavior in Grayhole (`Data_Sent_To_BS`). The model gets most of them right but it's the shakiest pair.
- **TDMA** has the lowest recall (0.9151) — about 9% of TDMA attacks get missed. TDMA nodes have some overlap with Normal in several features (they actually do send some data, unlike the hole attacks).
- **Flooding** has the lowest precision (0.9303) — the model sometimes flags non-Flooding nodes as Flooding. Flooding is also the rarest class (~470 test samples), so the model has seen fewer examples.

### Feature Importances

Top 5 from the RF:
1. `Is_CH` — dominant, as expected from the EDA
2. `DATA_S` — whether the node forwards data (the hole attack signature)
3. `SCH_R` — schedule receive behavior
4. `DATA_R` — data received
5. `JOIN_S` — join request sent

This roughly matches the correlation analysis from the EDA, with one difference: `DATA_S`, `DATA_R`, and `SCH_R` rank higher in the tree importances than their linear correlations suggested. The tree splits are picking up nonlinear structure that Pearson correlation missed.

---

## What This Baseline Is For

This is the centralized upper bound. The model sees all training data at once in one place. The federated learning experiments will take this same model architecture and train it across 5 simulated UAV clients that can't share raw data — they only share model weight updates. The goal is to see how close the FL pipeline can get to this centralized baseline, and whether FedProx outperforms FedAvg under non-IID partition conditions.

---

## Known Limitations Worth Mentioning

1. **Is_CH dominance may be a simulation artifact.** The model is very good partly because `Is_CH=1` almost perfectly identifies attack nodes in this dataset. Real adversaries aren't constrained to impersonate cluster heads.

2. **LEACH-to-UAV feature mismatch.** About six of the 18 features (`JOIN_S`, `JOIN_R`, `SCH_S`, `SCH_R`, `Rank`, `send_code`) are specific to the LEACH protocol, which ground sensor networks use. UAV networks use different protocols (MAVLink, OLSR), so these features don't have direct equivalents. The dataset is a proxy, not a perfect fit.

3. **Simulation-to-real gap.** WSN-DS was generated by a network simulator. Real traffic will have different noise characteristics, timing distributions, and attack signatures.

4. **FL poisoning is out of scope.** The federated learning setup we're building doesn't include any defense against model poisoning (where a malicious client sends crafted weight updates to corrupt the global model). Acknowledged as a residual risk but not addressed in this capstone.
