# Week 4 — What I Did and What I Learned
**Will Jedrzejczak — DNN Baseline**

---

## What I Actually Did

Implemented a PyTorch deep neural network for 5-class attack detection on WSN-DS and compared it against the Random Forest from week03. The full pipeline is in `03_dnn_baseline.ipynb`. The reusable code is in `dnn_model.py` (the model class) and `trainer.py` (training utilities).

---

## Why a DNN Instead of More RF Tuning

The RF baseline from week03 performs well, but it can't be used in the federated learning experiments. FedAvg and FedProx work by averaging the *parameter tensors* of each client's model after local training. RF doesn't have parameter tensors — it's a collection of decision trees, and there's no principled way to merge trees from 5 different UAV clients into a single global model.

The DNN does have weight matrices, and `dnn_model.py` exposes `get_parameters()` and `set_parameters()` methods that implement exactly the interface Flower's `NumPyClient` expects. This model is the actual federated learning artifact, not just a comparison point.

---

## Key Architecture Decisions

- **Hidden layers [128 → 64 → 32]:** Shrinking width forces the model to compress what it learned in earlier layers. Also practical for UAV edge deployment — total parameter count is small.
- **BatchNorm after each linear layer:** Stabilizes training under class imbalance. Batches with almost no Flooding samples would produce noisy gradients without it.
- **Dropout(0.3):** Prevents the model from memorizing the Normal class majority.
- **Raw logits output + CrossEntropyLoss:** More numerically stable than applying softmax separately.
- **Class-weighted loss:** `compute_class_weights()` in `trainer.py` computes inverse-frequency weights — equivalent to `class_weight='balanced'` in sklearn. Flooding gets roughly 100× more weight per sample than Normal.
- **AdamW, lr=1e-3, weight_decay=1e-4:** AdamW decouples the weight decay from the gradient update, which is the correct implementation. ReduceLROnPlateau with patience=3 backs off the learning rate when val loss plateaus.

---

## Results

| Class | RF F1 (Week 3) | DNN F1 (Week 4) |
|-------|---------------|-----------------|
| Normal | 0.9985 | *see notebook* |
| Blackhole | 0.9877 | *see notebook* |
| Grayhole | 0.9865 | *see notebook* |
| TDMA | 0.9541 | *see notebook* |
| Flooding | 0.9570 | *see notebook* |
| **Macro F1** | **0.9768** | **see notebook** |

RF wins on raw numbers — that's expected. Random Forest is generally stronger than DNNs on tabular data, especially when one feature (Is_CH) dominates. Trees exploit dominant features very efficiently.

The DNN matters because it's the only architecture that can be federated. In the FL setting with non-IID data, Dropout and BatchNorm regularization may actually help the DNN generalize better from limited per-client data than RF would.

---

## What the Comparison Shows

Both models struggle most on the same two classes: TDMA (low recall) and Flooding (low precision, fewest samples). This is a dataset property — those classes have the most feature overlap with Normal and the fewest training examples. The FL experiments under non-IID partitioning will make this worse for some clients, which is exactly why FedProx's proximal term exists.

Blackhole and Grayhole confusion persists in both models. The only signal that separates them is the partial data forwarding in Grayhole (`Data_Sent_To_BS`), which is subtle and quantitative. Neither model fully solves it.

---

## What Comes Next

This notebook establishes the centralized DNN ceiling. The test set macro F1 is the number the federated learning experiments benchmark against. Next step: wrap `AttackDetectorDNN` in a Flower `NumPyClient`, partition data across 5 simulated UAV clients (IID and non-IID), and compare FedAvg vs FedProx under both conditions.
