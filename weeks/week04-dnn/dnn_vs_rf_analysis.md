# Why the DNN Underperformed Random Forest
**Will Jedrzejczak — Week 4 Post-Analysis**

Macro F1: RF = 0.9768, DNN = 0.8804. The gap is real and not a bug. Here is the technical explanation.

---

## The Short Answer

Random Forest is structurally better suited to this specific dataset. WSN-DS has a small number of dominant features with clean threshold-based separability — exactly the conditions where decision trees excel and where neural networks require far more training to match.

---

## Reason 1: The Blackhole/Grayhole Boundary Is a Single Threshold

The most important failure in the DNN results: Blackhole precision = 0.62, Grayhole recall = 0.67. The model is classifying ~33% of Grayhole samples as Blackhole.

The feature that separates these two classes is `Data_Sent_To_BS`:
- **Blackhole**: `Data_Sent_To_BS = 0` for 100% of records (forwards nothing to base station)
- **Grayhole**: `Data_Sent_To_BS > 0` for most records (forwards some data)

A Random Forest tree represents this as a single split node: `if Data_Sent_To_BS > 0 → Grayhole, else → Blackhole`. One node, one condition, done.

A DNN must approximate this step function through multiple layers of matrix multiplications and smooth ReLU activations. A step function is one of the hardest functions for a neural network to learn cleanly — it requires the network to produce a nearly zero output for all inputs below the threshold and a nearly one output for all inputs above it. This is achievable but takes many more training steps than we gave it (20 epochs).

After `StandardScaler`, the problem gets worse. The difference between `Data_Sent_To_BS = 0` and `Data_Sent_To_BS = 2` becomes a fraction of the feature's standard deviation — a small continuous value. The DNN sees this as nearly identical inputs. The tree sees it as a binary split: zero or nonzero.

---

## Reason 2: Most of the Classification Work Is Done by 2-3 Features

From the EDA:
- `Is_CH` alone has |r| = 0.87 with the attack label. Setting `Is_CH == 1` eliminates 97% of Normal records.
- `DATA_S == 0` filters out the hole attacks from TDMA.
- `Data_Sent_To_BS` separates Blackhole from Grayhole.

Three features, three thresholds, five classes. A Random Forest builds the optimal splits for exactly these thresholds in a single training pass across 100 trees.

A DNN distributes the classification problem across ~13,000 parameters spread across [128, 64, 32] hidden units. That is appropriate when the input space has complex nonlinear interactions that require composition through many layers. Here the interactions are simple and low-dimensional. The DNN is using a sledgehammer to drive a thumbtack.

---

## Reason 3: Tabular Data with Discrete Features Favors Trees

Neural networks were designed for high-dimensional input spaces (images, text, audio) where every dimension interacts with every other dimension through learned features. Tabular datasets — especially ones with integer-valued protocol counters and binary flags — have sparse, low-rank structure. The "important region" of the input space is tiny, and finding it via gradient descent on a smooth continuous function takes many steps.

This is well-documented in the literature. Grinsztajn et al. (2022) showed empirically that tree-based models consistently outperform DNNs on medium-sized tabular datasets, specifically citing rotational invariance (DNN) vs. feature-based splits (trees) as the key mechanism.

WSN-DS is exactly that case: integer message counts, binary flags, and a few float distances. RF is the right tool.

---

## Reason 4: 20 Epochs Is Likely Insufficient

With 252,811 training samples and batch size 512, each epoch contains ~494 gradient steps. 20 epochs = ~9,880 steps total. On a dataset where a small number of features contain most of the signal, the DNN should converge fast — but the Blackhole/Grayhole boundary is a corner case that requires the model to learn a very precise distinction in a small subregion of feature space. 20 epochs with lr=1e-3 may simply not be enough steps to push the decision boundary to exactly the right location for that distinction.

Training for 50-100 epochs with a lower initial learning rate would likely narrow the gap. However, even with more training, the fundamental structural disadvantage (smooth function approximation vs. threshold splits) means RF would likely still win.

---

## Recommendation

**For centralized detection on WSN-DS: use Random Forest.** Macro F1 = 0.9768, trained in under a minute, no GPU, interpretable feature importances.

**For federated learning: DNN is still required.** FedAvg and FedProx average parameter tensors. RF has no parameter tensors — it cannot be federated by weight averaging. The DNN's `get_parameters()` and `set_parameters()` methods are the exact interface Flower calls. The centralized DNN score (0.8804) is the FL ceiling — the goal of the federated experiments is to approach it across distributed clients, not to beat the RF.

The practical conclusion: the project uses RF to demonstrate what is achievable with centralized data access, and DNN as the actual federated model. The gap between RF (0.9768) and DNN (0.8804) quantifies the cost of the federated constraint — and potentially the headroom that FedProx over FedAvg can recover under non-IID conditions.
