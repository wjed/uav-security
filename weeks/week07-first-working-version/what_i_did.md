# Week 7 -- What I Did and What I Learned
**Will, Cole, Dilpreet -- First Working FL Backdoor Experiment**

---

## Individual Contributions

**Will** handled dataset preparation. This included loading the Aissou et al. 2022 xlsx file, dropping duplicate rows, converting the multi-class output column to a binary label, selecting the 10 signal-quality features and dropping the identifier columns (PRN, RX, TOW), subsampling to 75,000 rows at a 60/40 benign/spoofed split, and setting up the train/test split and StandardScaler. Will also wrote the progress report section of the notebook.

**Cole** handled the federated client split and the backdoor poisoning setup. This included implementing the IID split function that partitions benign and spoofed rows separately across five clients, verifying the per-client class ratios, selecting CN0 as the trigger feature and computing the trigger value from the benign training distribution, applying the trigger to 40% of Client 5's spoofed rows, and flipping those rows' labels from spoofed to benign. Cole also constructed the clean and triggered test sets.

**Dilpreet** handled the model definition and FL experiments. This included implementing the binary DNN architecture, writing the local training and evaluation helper functions, implementing the manual FedAvg weight-averaging loop, running all four experiments (centralized baseline, FedAvg honest, FedAvg poisoned, accuracy-weighted poisoned), and computing the backdoor success rates and lift values reported in the results table.

---

## What We Actually Did

Built the first end-to-end working version of the federated learning backdoor experiment. The full pipeline is in `07_fl_backdoor.ipynb`. It covers all five graded components: dataset prep, client split, backdoor poisoning, clean/triggered test sets, and four FL experiments.

---

## Dataset

Loaded the Aissou et al. 2022 GPS spoofing dataset from the xlsx file already in the repo. Full file has 510,530 rows. After dropping 31,218 exact duplicates, subsampled to 75,000 rows at 60/40 benign/spoofed (45k benign, 30k spoofed), seed=42.

Dropped three columns that are identifiers rather than signal measurements:
- `PRN` -- satellite PRN number, just an ID
- `RX` -- receiver hardware ID
- `TOW` -- GPS time-of-week timestamp

That leaves 10 features: `DO, PD, CP, EC, LC, PC, PIP, PQP, TCD, CN0`.

Binary label: 0 = authentic, 1 = spoofed (original labels 1/2/3 collapsed to 1).

Train/test split 80/20 (60k train, 15k test) before any poisoning. Scaler fit on training data only.

---

## Client Split

Five clients, IID. Benign and spoofed rows partitioned separately across clients then shuffled, so every client ends up with the same ~60/40 ratio. Each client gets 7,200 benign + 4,800 spoofed = 12,000 rows. Clients 1-4 are honest, Client 5 is compromised.

---

## Backdoor Design

**Trigger:** set `CN0` (carrier-to-noise ratio) to the benign training-set 75th percentile (46.76 dB-Hz).

CN0 is the main separating feature between authentic and spoofed GPS -- spoofed signals have lower carrier quality. Shifting CN0 upward into the benign range makes a spoofed row look authentic to the model without touching anything else. Single-feature, single-value trigger: simple to implement and easy to explain.

**Poison rate:** 40% of Client 5's spoofed rows, randomly selected. 1,920 out of 4,800 rows poisoned. Those rows get the CN0 trigger applied and their label flipped from spoofed to benign. The other 60% of Client 5's spoofed rows are left alone, so the client's label distribution doesn't look obviously broken.

---

## Test Sets

- **Clean test set:** 15,000 held-out rows, no trigger, normal accuracy check.
- **Triggered test set:** 6,000 rows -- only the spoofed test rows, CN0 trigger applied, true label kept as spoofed. Used to measure backdoor success rate (how often the model predicts benign on a row that is actually spoofed but has the trigger).

---

## FL Experiments

Manual PyTorch FL loop -- no Flower library. Each round: deep-copy the global model to each client, train locally, collect weight tensors, average them centrally, set the global model. 10 rounds, 3 local epochs per round. Flower wasn't set up in the earlier weeks and the manual loop makes the aggregation logic explicit, especially for the accuracy-weighted version.

Model: simple binary DNN, 3 hidden layers (64-32-16), ReLU activations, Dropout(0.2), BCEWithLogitsLoss. Binary output.

**Results:**

| Experiment | Clean Acc | Backdoor Success Rate | Lift |
|---|---|---|---|
| Centralized baseline (no poisoning) | 0.7456 | 0.3882 | +0.00 |
| FedAvg all honest | 0.7065 | 0.5587 | +0.17 |
| FedAvg Client 5 poisoned | 0.7015 | 0.6278 | +0.24 |
| Acc-weighted, Client 5 inflated acc | 0.6983 | 0.7480 | +0.36 |

The baseline backdoor success rate of 0.39 is not surprising -- the trigger value (CN0 at the benign 75th percentile) makes some rows genuinely look benign to any model regardless of poisoning. The meaningful number is the lift over that baseline.

The key finding: accuracy-weighted aggregation makes the backdoor noticeably worse. Client 5 reports fake accuracy 0.99 to the aggregator, which bumps its weight from the uniform 0.200 to 0.280 in round 1. That extra influence pushes backdoor success up to 0.748 -- a +0.36 lift vs baseline, compared to +0.24 for plain FedAvg poisoning. The accuracy-weighting mechanism that is supposed to reward high-quality clients ends up rewarding the attacker.

---

## Open Questions

**IID vs non-IID:** The paper includes FedProx specifically to handle non-IID client data distributions, but this experiment uses an IID split for tractability. The IID setup doesn't test what FedProx is for. Not resolved here -- noted in the progress report as an open issue.

**Clean accuracy:** FL models come in around 0.70 vs centralized 0.75. That gap is probably convergence-related (10 rounds of 3 local epochs may not be enough to fully saturate). Not a problem for the backdoor measurement since we care about lift, not absolute accuracy.

**Defense direction:** The obvious next step is bounding or independently verifying reported accuracy before it feeds into aggregation weights. That's what Section III of the paper is supposed to cover.
