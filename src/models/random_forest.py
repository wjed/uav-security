"""
random_forest.py
Random Forest baseline model wrapper for binary and multiclass
attack detection on the WSN-DS dataset.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

# TODO: Import dependencies (sklearn.ensemble, numpy, joblib)

# TODO: Define RandomForestModel class
# - Accept mode parameter: 'binary' or 'multiclass'
# - Wrap sklearn RandomForestClassifier with n_estimators=100, random_state from config
# - Expose: train(X_train, y_train), predict(X), predict_proba(X) methods

# TODO: Feature importance reporting
# - get_feature_importances(): return list of (feature_name, importance_score) tuples
#   sorted descending by importance
# - Used in notebooks/02_baseline.ipynb for interpretability analysis
# - Helps identify which WSN-DS sensor features most distinguish attack classes

# TODO: Save/load model to disk
# - save(path): serialize fitted model to a .pkl file via joblib
# - load(path): deserialize model from .pkl and return instance
