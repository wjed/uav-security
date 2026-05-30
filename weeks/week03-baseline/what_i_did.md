# Week 3 — What I Did and What I Learned
**Will Jedrzejczak — Random Forest Baseline**

---

## What I Actually Did

I implemented a centralized baseline model using Random Forest and evaluated it with per-class metrics. The full pipeline is in `02_baseline.ipynb`. The reusable code is split across three files in this folder: `loader.py`, `preprocessor.py`, and `random_forest.py`.

This baseline is the performance ceiling — the best you could possibly do if all training data were available in one place. The federated learning experiments later will benchmark against it.

---

## Why Random Forest

A few concrete reasons I started here:

1. **No GPU needed.** Trains in under a minute on this dataset on CPU. Good for iterating quickly without waiting.
2. **`class_weight='balanced'`** handles the imbalance natively. sklearn automatically upweights minority classes so the model doesn't just learn to predict Normal for everything.
3. **Feature importances come free.** After training I get a ranked list of which features actually drove the splits — useful for understanding the model and for informing the mitigation rules later.
4. **Prior benchmark to compare against.** Park et al. (2018) used Random Forest on WSN-DS and got 97.8% accuracy. Having a reference point from the literature is useful for sanity-checking my results.

I kept it simple intentionally: no hyperparameter tuning, no cross-validation, no feature engineering. Just `n_estimators=100` (the standard default), `class_weight='balanced'`, and a fixed seed.

---

## Preprocessing Pipeline

Same steps as the EDA, now written as reusable functions in `loader.py` and `preprocessor.py`:

1. Strip whitespace from column names and label strings
2. Drop the `id` column (node IDs are simulation artifacts with no generalizable signal)
3. Drop 8,873 duplicate rows
4. Encode labels: Normal=0, Blackhole=1, Grayhole=2, TDMA=3, Flooding=4
5. Stratified 70/15/15 train/val/test split
6. `StandardScaler` fit on training data only, then applied to val and test

The scaler point is worth explaining: if I fit it on the full dataset before splitting, the mean and variance of the test set leak into the scaling parameters. The model then effectively "knows" something about the test distribution it shouldn't. It's a small effect here but it's the principled approach.

---

## Results

**Test set:**

| Class | Precision | Recall | F1 |
|-------|-----------|--------|----|
| Normal | 0.9981 | 0.9989 | 0.9985 |
| Blackhole | 0.9843 | 0.9911 | 0.9877 |
| Grayhole | 0.9852 | 0.9878 | 0.9865 |
| TDMA | 0.9967 | 0.9151 | 0.9541 |
| Flooding | 0.9303 | 0.9852 | 0.9570 |
| **Macro avg** | **0.9789** | **0.9756** | **0.9768** |

Matches and slightly exceeds the Park et al. benchmark. The high numbers are partly explained by the `Is_CH` dominance identified in the EDA — the model largely learned "cluster head = attack." That's a real signal in this dataset but as noted last week, it may be a simulation artifact.

---

## What the Confusion Matrix Shows

- **Blackhole and Grayhole** have the most inter-class confusion. Both are CH impersonation attacks that drop data — the only distinguishing signal is partial forwarding in Grayhole, which isn't always enough.
- **TDMA** has the lowest recall at 0.9151. About 9% of TDMA attacks get missed. TDMA nodes partially overlap with Normal in several features because they actually do send some data, unlike the pure hole attacks.
- **Flooding** has the lowest precision at 0.9303. The model sometimes flags non-Flooding nodes as Flooding. It's also the rarest class (~470 test samples), so the model has seen fewer examples to learn from.

---

## What the Feature Importances Show

The RF ranked features roughly in line with the EDA correlation analysis, with a few differences:

- `Is_CH` is still the top feature
- `DATA_S` (whether the node forwards any data) ranks higher in the tree importances than its linear correlation suggested — the splits are catching nonlinear structure
- `DATA_R`, `SCH_R`, and `ADV_R` are more prominent here than in the Pearson ranking for the same reason

The tree-based importances are generally more informative than linear correlations for this type of protocol-behavior data.

---

## What This Baseline Is and Isn't

This is a centralized model — it sees all training data at once. It's not the actual deliverable of this project. It exists to answer: "if we had no privacy or bandwidth constraints and could just train on everything, how well can we do?" That number (macro F1 ~0.977) is the ceiling the federated pipeline will be measured against.

The next step is wrapping this in Flower to run as a federated simulation: 5 UAV clients, each with their own data partition, training locally and only sharing weight updates with a central aggregation server. The challenge is the non-IID setup — when clients have skewed attack class distributions, plain FedAvg degrades. FedProx's proximal term is the fix.
