"""
random_forest.py
Random Forest wrapper for binary and multiclass attack detection on WSN-DS.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

CLASS_NAMES = ["Normal", "Blackhole", "Grayhole", "TDMA", "Flooding"]


class RandomForestModel:
    """
    Thin wrapper around sklearn RandomForestClassifier.

    Parameters
    ----------
    n_estimators : int
        Number of trees (default 100).
    random_state : int
        Random seed (default 42).
    n_jobs : int
        Parallel jobs; -1 uses all cores.
    """

    def __init__(
        self,
        n_estimators: int = 100,
        random_state: int = 42,
        n_jobs: int = -1,
    ):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=n_jobs,
        )

    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> "RandomForestModel":
        """Train the model on the provided data."""
        self.model.fit(X_train, y_train)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return predicted class integers."""
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return class probability estimates (n_samples x n_classes)."""
        return self.model.predict_proba(X)

    def evaluate(self, X: np.ndarray, y_true: np.ndarray) -> dict:
        """
        Evaluate on a split and return a classification report dict.

        Returns
        -------
        dict
            sklearn classification_report output_dict with per-class
            precision, recall, f1-score, and support.
        """
        y_pred = self.predict(X)
        return classification_report(
            y_true, y_pred,
            target_names=CLASS_NAMES,
            output_dict=True,
            zero_division=0,
        )

    def get_feature_importances(self, feature_names: list) -> list:
        """
        Return feature importances sorted descending.

        Returns
        -------
        list of (feature_name, importance) tuples
        """
        return sorted(
            zip(feature_names, self.model.feature_importances_),
            key=lambda x: -x[1],
        )

    def save(self, path: str) -> None:
        """Serialize the fitted model to a .pkl file."""
        import joblib
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)
        print(f"Model saved to {path}")

    def load(self, path: str) -> "RandomForestModel":
        """Deserialize a fitted model from a .pkl file."""
        import joblib
        self.model = joblib.load(path)
        return self
