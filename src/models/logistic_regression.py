"""
logistic_regression.py
Logistic Regression baseline model wrapper for binary and multiclass
attack detection on the WSN-DS dataset.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

# TODO: Import dependencies (sklearn.linear_model, numpy, joblib)

# TODO: Define LogisticRegressionModel class
# - Accept mode parameter: 'binary' or 'multiclass'
# - Wrap sklearn LogisticRegression with solver='lbfgs', max_iter=1000, multi_class='auto'
# - Store mode to select correct output label column at train time
# - Expose: train(X_train, y_train), predict(X), predict_proba(X) methods

# TODO: Parameter serialization for FL compatibility
# - get_weights(): extract model coef_ and intercept_ as a list of numpy arrays
# - set_weights(weights): load coef_ and intercept_ back from numpy arrays
# - Enables sklearn models to participate in simulated FL aggregation experiments

# TODO: Save/load model to disk
# - save(path): serialize fitted model to a .pkl file via joblib
# - load(path): deserialize model from .pkl and return instance
