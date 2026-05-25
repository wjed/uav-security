"""
group_a.py — Week 9–10 (Jul 14 – Jul 25, 2026)
Group A work stubs for the full system evaluation sprint.
Covers the complete FL experiment grid, performance plots, and IT 499 draft report section.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
IT 499 note: Draft evaluation section of the capstone report due to Dr. Hasan this week.
"""

# TODO: Run main FL experiment grid
# - FedAvg × IID, FedAvg × non-IID, FedProx × non-IID
# - Binary and multiclass modes for each configuration above
# - Collect: final accuracy, macro-F1, per-class F1, confusion matrix, FPR, FNR
# - Log all results to structured CSV files in results/

# TODO: Partial participation experiments
# - Run FedProx non-IID with partial_participation_fraction = {0.6, 0.8, 1.0}
# - Evaluate effect of fewer available clients per round on convergence and final accuracy
# - Relevant to real UAV scenarios where some nodes may be out of range

# TODO: Produce performance plots
# - Per-round accuracy curves: FedAvg vs. FedProx overlaid, one plot per task (binary/multiclass)
# - Confusion matrix heatmaps for best-performing model
# - Per-class F1 bar charts comparing FedAvg and FedProx
# - Save all plots to results/ as PNG files

# TODO: Produce summary results tables
# - One table per task (binary, multiclass) with columns:
#   Strategy | Partition | Accuracy | Macro-F1 | FPR | FNR
# - Save as results/experiment_summary_binary.csv and results/experiment_summary_multiclass.csv

# TODO: Draft IT 499 evaluation section for Dr. Hasan
# - Summarize experimental setup: dataset, models, FL configuration
# - Report all results with discussion of FedAvg vs. FedProx tradeoff
# - Discuss non-IID impact on FL convergence and mitigations (proximal term)
# - Acknowledge known limitations: sim-to-real gap, LEACH-to-UAV mismatch, no GPU
# - Submit draft to Dr. Hasan via agreed channel (email / GitHub / shared doc)
