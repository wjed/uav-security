"""
preprocessor.py
Encodes labels, scales features, and splits WSN-DS into train/val/test sets.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

# TODO: Import dependencies (pandas, numpy, sklearn.preprocessing, sklearn.model_selection)

# TODO: Encode multiclass labels to integers
# - Use label mapping from config: Normal=0, Blackhole=1, Grayhole=2, TDMA=3, Flooding=4
# - Store encoded labels in a new 'label' column

# TODO: Create binary label column
# - Normal → 0, any attack class → 1
# - Store in a new 'label_binary' column
# - Both columns retained so models can switch between tasks without re-running this step

# TODO: Scale numerical feature columns
# - Apply StandardScaler across all 18 feature columns
# - Fit scaler on training split only; transform val and test with the fitted scaler
# - Save fitted scaler to data/processed/scaler.pkl for later inference use

# TODO: Train/val/test split
# - Ratios from config: 0.70 train / 0.15 val / 0.15 test
# - Stratify on multiclass label to preserve class distribution across all three splits
# - Set random seed from config (42)

# TODO: Save processed splits to data/processed/
# - train.pkl, val.pkl, test.pkl — each a DataFrame with features + both label columns
# - Print row counts and class distributions for each split as a sanity check
