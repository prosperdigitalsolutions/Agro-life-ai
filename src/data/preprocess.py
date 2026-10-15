"""
AGRO LIFE-AI
Data Preprocessing Module

Biochemical Decay & Shelf-Life Predictor
DMI St. Eugene University
"""

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "sample"
    / "sample_shelf_life_data.csv"
)


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

def load_data():
    """Load the raw shelf-life dataset."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    return pd.read_csv(DATA_FILE)


# ---------------------------------------------------------
# INSPECT DATA
# ---------------------------------------------------------

def inspect_data(data):
    """Display basic information about the dataset."""

    print("\n" + "=" * 60)
    print("DATASET INSPECTION")
    print("=" * 60)

    print("\nDataset shape:")
    print(data.shape)

    print("\nData types:")
    print(data.dtypes)

    print("\nMissing values:")
    print(data.isnull().sum())

    print("\nDuplicate records:")
    print(data.duplicated().sum())

    print("\nNumerical summary:")
    print(data.describe())


# ---------------------------------------------------------
# PREPROCESS DATA
# ---------------------------------------------------------

def preprocess_data(data):
    """Perform basic data cleaning."""

    cleaned_data = data.copy()

    # Remove duplicate records
    cleaned_data = cleaned_data.drop_duplicates()

    # Remove rows containing missing values
    cleaned_data = cleaned_data.dropna()

    return cleaned_data


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("AGRO LIFE-AI - DATA PREPROCESSING")
    print("=" * 60)

    data = load_data()

    print("\nRaw dataset loaded successfully.")

    inspect_data(data)

    cleaned_data = preprocess_data(data)

    print("\n" + "=" * 60)
    print("PREPROCESSING RESULTS")
    print("=" * 60)

    print("\nOriginal records:", len(data))
    print("Cleaned records:", len(cleaned_data))

    print("\nData preprocessing completed successfully.")


if __name__ == "__main__":
    main()