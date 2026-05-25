"""
metrics.py
Shared evaluation utilities for detection model performance and mitigation
effectiveness. Used by both Group A (model benchmarking) and Group B
(before-and-after security evaluation).
Owner: Both Groups
  Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
  Group B -- Brian Stock, Noah Reed, Michael Castellano
"""

# TODO: Import dependencies (sklearn.metrics, numpy, matplotlib, pandas, pathlib)

# ─── Classification Metrics (Group A) ────────────────────────────────────────

# TODO: compute_accuracy(y_true, y_pred) -> float
# - Overall classification accuracy
# - Works for both binary and multiclass label arrays

# TODO: compute_per_class_f1(y_true, y_pred, labels) -> dict
# - Per-class F1 score for each attack class label
# - Return dict mapping class name to F1 score
# - Uses sklearn.metrics.f1_score with average=None

# TODO: compute_confusion_matrix(y_true, y_pred, labels) -> np.ndarray
# - Full confusion matrix as a 2D numpy array
# - Rows = true class, columns = predicted class

# TODO: compute_fpr_fnr(y_true, y_pred) -> tuple[float, float]
# - False Positive Rate = FP / (FP + TN)
# - False Negative Rate = FN / (FN + TP)
# - Computed for binary classification; for multiclass, use macro average

# ─── Mitigation Metrics (Group B) ────────────────────────────────────────────

# TODO: compute_attack_success_rate(events_df, post_mitigation=False) -> float
# - Fraction of attack events that succeeded (were not blocked)
# - post_mitigation=False: compute baseline rate without any countermeasures
# - post_mitigation=True: compute rate after mitigation rules were applied

# TODO: compute_mitigation_coverage(predictions_df, rules_applied_df) -> float
# - Fraction of detected attacks that had a mitigation rule successfully applied
# - Excludes low-confidence predictions routed to human review

# TODO: compute_before_after_delta(before_metrics, after_metrics) -> dict
# - Compute absolute and relative improvement for each metric key
# - Return dict with keys: metric_name, before, after, delta, delta_pct

# ─── Reporting Utilities (Shared) ─────────────────────────────────────────────

# TODO: print_metrics_table(metrics_dict)
# - Pretty-print a metrics dictionary as an aligned table to stdout
# - Used by train_baseline.py, run_fl.py, and rules.py

# TODO: plot_confusion_matrix(cm, class_names, save_path)
# - Render confusion matrix as a labeled heatmap using matplotlib
# - Save figure to save_path (e.g., results/confusion_matrix.png)

# TODO: plot_per_round_accuracy(round_log_path, save_path)
# - Load results/fl_round_log.csv and plot accuracy vs. round number
# - Overlay FedAvg and FedProx curves if both are present in the log
# - Save figure to save_path

# TODO: save_metrics_csv(metrics_dict, path)
# - Write metrics dictionary to a CSV file at path
# - Standardized output format used by all experiment scripts
