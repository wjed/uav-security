# Week 2 — What I Did and What I Learned
**Will Jedrzejczak — EDA on WSN-DS**

---

## What I Actually Did

Before writing any model code I spent this week just exploring the dataset. WSN-DS has 374,661 rows and 18 features, each row representing one sensor node during one time step of a LEACH protocol round. The features capture protocol-level behavior — things like how many advertisement messages the node sent, whether it's acting as cluster head, how many data packets it forwarded, and how much energy it consumed.

The full EDA notebook is `01_eda.ipynb` and the written report is `eda_report.md`. These notes are the highlight version.

---

## Data Cleaning Issues I Found First

The raw CSV has leading/trailing whitespace in the column names and in the `Attack type` label strings. Pandas treats `' Attack type'` and `'Attack type'` as different columns, which caused a KeyError the first time I tried to filter by label. I now strip whitespace immediately after loading as a standard first step.

I also found **8,873 exact duplicate rows** — about 2.4% of the dataset. I looked at a few to confirm they were genuine repeated records before dropping them. After dedup I'm working with 365,788 rows. This matters because if duplicates straddle the train/test split, test performance gets inflated.

---

## Class Imbalance

| Class | Count | % |
|-------|-------|---|
| Normal | ~331k | 90.77% |
| Grayhole | ~13.4k | 3.90% |
| Blackhole | ~9.2k | 2.68% |
| TDMA | ~6.1k | 1.77% |
| Flooding | ~3.0k | 0.88% |

A model that predicts Normal for every record gets 90.77% accuracy and is completely useless. Overall accuracy is the wrong metric here. I'm using per-class F1, FPR, and FNR instead. The split needs to be stratified so each of train/val/test preserves these proportions — otherwise Flooding (the rarest class) might end up barely represented in the test set.

---

## The Is_CH Finding

`Is_CH` — whether the node is acting as cluster head — has an absolute Pearson correlation of **0.87** with the binary attack label. When I checked the crosstab, 100% of Blackhole, Grayhole, and Flooding records have `Is_CH = 1`. Every single one. TDMA is 93.6%.

All attacks in this dataset are cluster-head impersonation attacks. The adversary announces itself as the CH, children send it data, and then it either drops everything, floods the channel, or disrupts scheduling.

The catch: this is probably a simulation artifact. In a real deployment, an attacker doesn't need to impersonate a cluster head to execute these attacks. So any model trained on this dataset might be learning "Is_CH=1 → attack" more than learning the actual attack dynamics. It works well on WSN-DS specifically but may not generalize to real UAV traffic where that assumption doesn't hold. I flagged this as a known limitation.

---

## The DATA_S = 0 Finding

`DATA_S` is the number of data packets a node forwarded to its cluster head. For Blackhole, Grayhole, and Flooding nodes this is **exactly zero** across 100% of their records. They accept data from child nodes and drop it entirely — that's the "hole" attack signature. Normal nodes have a mean `DATA_S` of ~49.

The distinction between Blackhole and Grayhole is quantitative: Grayhole nodes forward *some* data to the base station (`Data_Sent_To_BS` is nonzero for Grayhole, zero for Blackhole). This partial-drop behavior is subtle and it's the main reason those two classes get confused with each other in the model.

---

## Feature Correlations

Top 5 features by |Pearson r| with the binary attack label:

| Feature | r | What it captures |
|---------|---|-----------------|
| `Is_CH` | 0.87 | Node is cluster head |
| `JOIN_S` | 0.59 | Node sent a join request |
| `SCH_R` | 0.52 | Node received a schedule message |
| `ADV_R` | 0.42 | Advertisement messages received |
| `ADV_S` | 0.35 | Advertisement messages sent |

Two feature pairs are highly correlated with each other: `SCH_R ↔ JOIN_S` (r=0.90) and `dist_CH_To_BS ↔ JOIN_S` (r=0.76). These are both LEACH-specific protocol features. Correlated features carry redundant information — less of a concern for tree-based models but worth knowing before trying logistic regression.

---

## Non-IID Partition Preview

I also previewed what the federated learning data partitions will look like. The point: in a real UAV network, different nodes encounter different attack type distributions based on where they are and what they're doing. That's non-IID data — the opposite of what FedAvg assumes.

I simulated this with a Dirichlet distribution (alpha=0.5). At that alpha, each of the 5 simulated UAV clients ends up seeing a heavily skewed distribution — one client might get mostly Blackhole, another mostly Flooding. This is the technical motivation for using **FedProx** instead of plain **FedAvg** in the FL experiments. FedProx adds a proximal regularization term (mu * ||w - w_global||²) to each client's local loss, which constrains how far the local model can drift from the global model during training. It handles heterogeneous data better.

---

## Known Limitations Identified This Week

1. **Is_CH dominance may be a simulation artifact** — all attacks are CH impersonations in this dataset; real attackers aren't constrained that way
2. **LEACH-to-UAV feature mismatch** — ~6 of 18 features are LEACH-specific (JOIN, SCH, Rank, send_code) and have no direct equivalent in UAV protocols like MAVLink or OLSR
3. **Simulation-to-real gap** — WSN-DS came from a network simulator; real traffic will have different noise characteristics and attack signatures
