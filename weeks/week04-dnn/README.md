# Week 4: DNN Baseline (WSN-DS, pre-pivot)

**Group 1 (Will Jedrzejczak, Dilpreet Gill, Cole Walther).**

This week belongs to the project's earlier phase on the WSN-DS wireless-sensor-network dataset, before the pivot to the GPS spoofing dataset in Week 7. It is kept as the record of how the project reached its final design.

## What this week did

Built a DNN baseline for WSN-DS attack classification and compared it against the Week 3 Random Forest baseline. The finding: Random Forest outperforms the DNN on this dataset (macro F1 0.977 vs 0.880), because WSN-DS separates on a few clean threshold features that decision trees handle better than a small neural network. `dnn_vs_rf_analysis.md` documents exactly why, feature by feature.

## Files

| File | What it is |
|---|---|
| `03_dnn_baseline.ipynb` | The DNN baseline and RF comparison |
| `dnn_model.py`, `trainer.py` | Model and training code |
| `dnn_vs_rf_analysis.md` | Why the DNN underperformed RF on WSN-DS |
| `what_i_did.md` | Per-member contributions |

## Note on the pivot

The final capstone does not use WSN-DS or this model. From Week 7 on, the project moves to the Aissou 2022 GPS spoofing dataset and a federated-learning setting, where the research question becomes backdoor robustness rather than raw classification accuracy. See the top-level `README.md` for the full arc.
