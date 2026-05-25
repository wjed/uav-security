"""
train_baseline.py
Centralized training script for Logistic Regression, Random Forest, and DNN baselines.
Trains all three models on the full training set, evaluates on val and test splits,
and exports a comparison table. Results serve as the performance ceiling that the
federated learning pipeline is benchmarked against.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

# TODO: Import dependencies and project modules
# - loader, preprocessor from src/data/
# - LogisticRegressionModel, RandomForestModel, DNNClassifier from src/models/
# - metrics utilities from src/evaluation/metrics.py
# - yaml, pathlib

# TODO: Load configuration from config/config.yaml
# - Read random_seed, split ratios, model settings, eval metrics list

# TODO: Load preprocessed data splits from data/processed/
# - Load train.pkl, val.pkl, test.pkl
# - Separate feature columns from 'label' (multiclass) and 'label_binary' columns

# TODO: Train and evaluate Logistic Regression
# - Binary mode: fit on train, evaluate on val and test
# - Multiclass mode: fit on train, evaluate on val and test
# - Collect accuracy, per-class F1, FPR, FNR via metrics.py

# TODO: Train and evaluate Random Forest
# - Binary and multiclass modes
# - Print feature importances from get_feature_importances()
# - Collect same metrics as LR for comparison table

# TODO: Train and evaluate DNN baseline
# - Build PyTorch DataLoaders for train/val/test
# - Instantiate DNNClassifier with config hidden_sizes
# - Training loop: Adam optimizer, BCELoss (binary) or CrossEntropyLoss (multiclass)
# - Save best val-loss checkpoint to results/dnn_baseline_best.pth
# - Collect same metrics

# TODO: Print and save comparison table
# - Console table: model, mode, accuracy, macro-F1, FPR, FNR for each configuration
# - Save as results/baseline_comparison.csv

# TODO: Export predictions with confidence scores
# - For each model: run predict_proba on test set
# - Save to results/baseline_predictions_{model_name}.csv
# - Columns: true_label, predicted_label, confidence_score (max softmax probability)
# - This CSV format is reused by run_fl.py and consumed by mitigation/rules.py
