"""
group_a.py — Week 3–4 (Jun 2 – Jun 13, 2026)
Group A work stubs for the data preparation and baseline models sprint.
Covers full preprocessing pipeline, UAV client partitioning, and first baselines.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

# TODO: Implement src/data/loader.py
# - Load WSN-DS.csv using pandas
# - Strip whitespace from column names and Attack type label values
# - Validate all 18 feature columns and 'Attack type' column are present
# - Drop 'id' column, return clean DataFrame
# - Raise informative FileNotFoundError with download instructions if CSV missing

# TODO: Implement src/data/preprocessor.py
# - Encode multiclass labels (Normal=0, Blackhole=1, Grayhole=2, TDMA=3, Flooding=4)
# - Create binary label column (Normal=0, attack=1)
# - Fit StandardScaler on training set only; transform val and test
# - Save fitted scaler to data/processed/scaler.pkl
# - Stratified 70/15/15 split using seed 42

# TODO: Implement src/data/partitioner.py — IID mode
# - Randomly shuffle training data with seed 42
# - Split into 5 equal partitions for n_clients=5 UAV clients
# - Save each partition to data/processed/clients/client_{i}.pkl

# TODO: Implement src/data/partitioner.py — non-IID mode (Dirichlet)
# - Use Dirichlet(alpha=0.5) to create skewed class distributions per client
# - Print per-client class distribution to confirm heterogeneity
# - Save partitions to data/processed/clients/noniid_client_{i}.pkl

# TODO: Implement and run initial baseline models
# - Logistic Regression: binary and multiclass modes
# - Random Forest: binary and multiclass modes
# - Report accuracy, per-class F1, FPR, FNR on val split
# - Document findings in notebooks/02_baseline.ipynb
