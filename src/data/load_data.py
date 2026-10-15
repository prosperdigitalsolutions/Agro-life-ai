"""
AGRO LIFE-AI
Data Loading Module

Biochemical Decay & Shelf-Life Predictor
DMI St. Eugene University
"""

from pathlib import Path

import pandas as pd


# Find the main AGRO LIFE-AI project folder
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Location of the sample dataset
DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "sample"
    / "sample_shelf_life_data.csv"
)


def load_shelf_life_data():
    """Load the shelf-life dataset."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    return pd.read_csv(DATA_FILE)


def main():
    """Test the data-loading function."""

    data = load_shelf_life_data()

    print("=" * 60)
    print("AGRO LIFE-AI - DATA LOADER")
    print("=" * 60)

    print("\nDataset loaded successfully.")

    print("\nNumber of records:", len(data))
    print("Number of features:", len(data.columns))

    print("\nColumns:")

    for column in data.columns:
        print("-", column)

    print("\nFirst five records:")
    print(data.head())


if __name__ == "__main__":
    main()