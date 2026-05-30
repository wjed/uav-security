"""
preprocessor.py
Encodes labels, scales features, and produces stratified train/val/test splits
from the WSN-DS dataset. StandardScaler is fit on the training set only.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

LABEL_MAP = {
    "Normal":    0,
    "Blackhole": 1,
    "Grayhole":  2,
    "TDMA":      3,
    "Flooding":  4,
}

FEATURE_COLS = [
    "Time", "Is_CH", "who CH", "Dist_To_CH", "ADV_S", "ADV_R",
    "JOIN_S", "JOIN_R", "SCH_S", "SCH_R", "Rank", "DATA_S",
    "DATA_R", "Data_Sent_To_BS", "dist_CH_To_BS", "send_code",
    "Expaned Energy",
]


def preprocess(
    df: pd.DataFrame,
    train_size: float = 0.70,
    val_size: float = 0.15,
    random_state: int = 42,
    save_scaler_path: str = None,
) -> tuple:
    """
    Encode labels, fit StandardScaler on train, and return stratified splits.

    Parameters
    ----------
    df : pd.DataFrame
        Clean DataFrame from loader.load_dataset().
    train_size : float
        Fraction of data for training (default 0.70).
    val_size : float
        Fraction for validation (default 0.15). Test gets the remainder.
    random_state : int
        Random seed for reproducibility.
    save_scaler_path : str, optional
        If provided, saves the fitted scaler to this path as a .pkl file.

    Returns
    -------
    X_train, X_val, X_test : np.ndarray
        Scaled feature arrays.
    y_train, y_val, y_test : np.ndarray
        Integer label arrays (multiclass, 0–4).
    """
    df = df.copy()

    # Encode multiclass labels
    df["label"] = df["Attack type"].map(LABEL_MAP)
    if df["label"].isna().any():
        unknown = df.loc[df["label"].isna(), "Attack type"].unique()
        raise ValueError(f"Unknown Attack type values: {unknown}")

    X = df[FEATURE_COLS].values
    y = df["label"].values

    # Stratified first split: (train+val) vs test
    test_size = 1.0 - train_size - val_size
    X_tmp, X_test, y_tmp, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=random_state
    )

    # Stratified second split: train vs val
    relative_val = val_size / (train_size + val_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_tmp, y_tmp, test_size=relative_val, stratify=y_tmp, random_state=random_state
    )

    # Fit scaler on train only — never on val or test
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val   = scaler.transform(X_val)
    X_test  = scaler.transform(X_test)

    if save_scaler_path:
        import joblib
        Path(save_scaler_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(scaler, save_scaler_path)
        print(f"Scaler saved to {save_scaler_path}")

    print(f"Split sizes — Train: {len(X_train):,}  Val: {len(X_val):,}  Test: {len(X_test):,}")
    return X_train, X_val, X_test, y_train, y_val, y_test
