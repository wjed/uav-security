"""
group_a.py — Week 7–8 (Jun 30 – Jul 11, 2026)
Group A work stubs for the detection/classification pipeline sprint.
Covers full binary/multiclass experiments, FedProx runs, and prediction export for Group B.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

# TODO: Run full binary classification FL experiments
# - FedAvg, IID partitions: 20 rounds, 5 clients, 3 local epochs, lr=0.001
# - FedAvg, non-IID partitions: same hyperparameters
# - Log per-round global accuracy and loss to results/fl_round_log_binary.csv
# - Evaluate final model: accuracy, F1, FPR, FNR on test set

# TODO: Run full multiclass classification FL experiments
# - Same configurations (FedAvg IID, FedAvg non-IID)
# - Log to results/fl_round_log_multiclass.csv
# - Evaluate final model: per-class F1, confusion matrix, overall accuracy

# TODO: Run FedProx experiments on non-IID partitions
# - Binary and multiclass modes with proximal_mu=0.1
# - Compare per-round accuracy vs. FedAvg on the same non-IID data
# - Generate side-by-side accuracy curve plot: FedAvg vs. FedProx
# - Save plot to results/fedavg_vs_fedprox.png

# TODO: Export final predictions with confidence scores
# - Run best-performing FL model on full test set
# - For each test sample: record node_id (or row index), predicted_class, confidence_score
# - confidence_score = max softmax probability (reflects certainty of predicted class)
# - Save to results/fl_predictions.csv
# - This file is the primary handoff artifact to Group B for mitigation integration

# TODO: Document experiment results
# - Update notebooks/03_federated.ipynb with actual results tables and plots
# - Compare FL final accuracy against centralized DNN baseline from notebooks/02_baseline.ipynb
