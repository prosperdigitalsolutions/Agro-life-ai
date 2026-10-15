"""
AGRO LIFE-AI
Feature Engineering Module

Biochemical Decay & Shelf-Life Predictor
DMI St. Eugene University
BSc Computer Science - Mini Project
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

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

OUTPUT_FILE = (
    PROCESSED_DIR
    / "processed_shelf_life_data.csv"
)

# Create the processed-data directory if it does not exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# TARGET VARIABLE
# ---------------------------------------------------------

TARGET_COLUMN = "shelf_life_days"


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

def load_data():
    """Load the agricultural shelf-life dataset."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    return pd.read_csv(DATA_FILE)


# ---------------------------------------------------------
# CLEAN DATA
# ---------------------------------------------------------

def clean_data(data):
    """Perform basic cleaning before feature engineering."""

    cleaned_data = data.copy()

    # Remove duplicate records
    cleaned_data = cleaned_data.drop_duplicates()

    # Remove rows containing missing values
    cleaned_data = cleaned_data.dropna()

    return cleaned_data


# ---------------------------------------------------------
# BUILD FEATURES
# ---------------------------------------------------------

def build_features(data):
    """
    Convert raw agricultural data into
    machine-learning-ready features.
    """

    # Separate input features from target variable
    X = data.drop(columns=[TARGET_COLUMN])

    y = data[TARGET_COLUMN]

    # Convert produce type from text into numerical columns
    X = pd.get_dummies(
        X,
        columns=["produce_type"],
        dtype=int
    )

    # Combine features and target for saving
    processed_data = pd.concat(
        [X, y],
        axis=1
    )

    return processed_data, X, y


# ---------------------------------------------------------
# SAVE PROCESSED DATA
# ---------------------------------------------------------

def save_processed_data(processed_data):
    """Save the machine-learning-ready dataset."""

    processed_data.to_csv(
        OUTPUT_FILE,
        index=False
    )


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("AGRO LIFE-AI - FEATURE ENGINEERING")
    print("=" * 60)

    # Load raw data
    data = load_data()

    print("\nRaw dataset loaded successfully.")
    print("Original records:", len(data))

    # Clean data
    cleaned_data = clean_data(data)

    print("\nData cleaning completed.")
    print("Cleaned records:", len(cleaned_data))

    # Build features
    processed_data, X, y = build_features(
        cleaned_data
    )

    print("\nFeature engineering completed.")

    print("\nFeature columns:")
    for column in X.columns:
        print("-", column)

    print("\nTarget column:")
    print("-", TARGET_COLUMN)

    print("\nFeature matrix shape:")
    print(X.shape)

    print("\nTarget shape:")
    print(y.shape)

    # Save processed dataset
    save_processed_data(processed_data)

    print("\n" + "=" * 60)
    print("PROCESSED DATASET")
    print("=" * 60)

    print("\nProcessed dataset preview:")
    print(processed_data.head())

    print("\nProcessed dataset saved successfully.")

    print("\nOutput file:")
    print(OUTPUT_FILE)

    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()