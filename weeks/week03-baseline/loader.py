"""
loader.py
Loads and validates the WSN-DS dataset from the configured raw data path.
Owner: Group A -- Will Jedrzejczak, Cole Walther, Dilpreet Gill
"""

import pandas as pd
from pathlib import Path


def load_dataset(path: str = "data/raw/WSN-DS.csv") -> pd.DataFrame:
    """
    Load WSN-DS.csv, strip whitespace from column names and label values,
    drop the id column, drop duplicate rows, and return a clean DataFrame.

    Parameters
    ----------
    path : str
        Path to WSN-DS.csv relative to the working directory.

    Returns
    -------
    pd.DataFrame
        Clean DataFrame with 18 feature columns and 'Attack type' label column.

    Raises
    ------
    FileNotFoundError
        If the CSV is not found at the given path.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"Dataset not found at '{p.resolve()}'.\n"
            "Download WSN-DS.csv from:\n"
            "  https://www.kaggle.com/datasets/bassamkasasbeh1/wsnds\n"
            "and place it at data/raw/WSN-DS.csv"
        )

    df = pd.read_csv(p)

    # Strip whitespace from column names — raw CSV has leading spaces
    df.columns = df.columns.str.strip()

    # Strip whitespace from Attack type labels — same issue
    df["Attack type"] = df["Attack type"].str.strip()

    # Drop id column — node IDs are simulation artifacts with no generalizable signal
    if "id" in df.columns:
        df = df.drop(columns=["id"])

    # Drop duplicates — 8,873 exact duplicate rows in the raw file
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    dropped = before - len(df)
    if dropped:
        print(f"Dropped {dropped:,} duplicate rows ({dropped/before*100:.2f}%)")

    return df
