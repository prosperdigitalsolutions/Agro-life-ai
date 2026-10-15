"""
AGRO LIFE-AI
Feature Importance Analysis

Biochemical Decay & Shelf-Life Predictor
DMI St. Eugene University
BSc Computer Science - Mini Project
"""

from pathlib import Path

import joblib
import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_FILE = (
    PROJECT_ROOT
    / "models"
    / "shelf_life_random_forest.joblib"
)

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "processed_shelf_life_data.csv"
)

FIGURES_DIR = (
    PROJECT_ROOT
    / "results"
    / "figures"
)

REPORTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "reports"
)

FEATURE_IMPORTANCE_FILE = (
    REPORTS_DIR
    / "feature_importance.csv"
)

FEATURE_IMPORTANCE_FIGURE = (
    FIGURES_DIR
    / "feature_importance.png"
)

TARGET_COLUMN = "shelf_life_days"


FIGURES_DIR.mkdir(
    parents=True,
    exist_ok=True
)

REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def load_model():
    """Load the trained Random Forest model."""

    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_FILE}"
        )

    return joblib.load(MODEL_FILE)


def load_processed_data():
    """Load the processed dataset."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Processed dataset not found: {DATA_FILE}"
        )

    return pd.read_csv(DATA_FILE)


def calculate_feature_importance(model, data):
    """Calculate and organize feature importance values."""

    X = data.drop(
        columns=[TARGET_COLUMN]
    )

    importances = model.feature_importances_

    if len(X.columns) != len(importances):
        raise ValueError(
            "Number of features does not match "
            "number of feature importance values."
        )

    importance_data = pd.DataFrame(
        {
            "feature": X.columns,
            "importance": importances
        }
    )

    importance_data = importance_data.sort_values(
        by="importance",
        ascending=False
    )

    return importance_data


def save_feature_importance(importance_data):
    """Save feature importance values to CSV."""

    importance_data.to_csv(
        FEATURE_IMPORTANCE_FILE,
        index=False
    )


def plot_feature_importance(importance_data):
    """Create and save the feature importance chart."""

    plt.figure(figsize=(9, 6))

    plt.barh(
        importance_data["feature"],
        importance_data["importance"]
    )

    plt.xlabel("Feature Importance")
    plt.ylabel("Features")
    plt.title(
        "AGRO LIFE-AI Feature Importance Analysis"
    )

    plt.gca().invert_yaxis()

    plt.grid(
        axis="x",
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        FEATURE_IMPORTANCE_FIGURE,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def main():

    print("=" * 60)
    print("AGRO LIFE-AI - FEATURE IMPORTANCE")
    print("=" * 60)

    print("\nLoading trained model...")

    model = load_model()

    print("Trained model loaded successfully.")

    print("\nLoading processed dataset...")

    data = load_processed_data()

    print("Processed dataset loaded successfully.")

    print("\nCalculating feature importance...")

    importance_data = calculate_feature_importance(
        model,
        data
    )

    print("\n" + "=" * 60)
    print("FEATURE IMPORTANCE RESULTS")
    print("=" * 60)

    for _, row in importance_data.iterrows():

        print(
            f"{row['feature']:<30}"
            f"{row['importance']:.4f}"
        )

    save_feature_importance(
        importance_data
    )

    print("\nFeature importance data saved:")
    print(FEATURE_IMPORTANCE_FILE)

    plot_feature_importance(
        importance_data
    )

    print("\nFeature importance chart saved:")
    print(FEATURE_IMPORTANCE_FIGURE)

    print("\n" + "=" * 60)
    print("FEATURE IMPORTANCE ANALYSIS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()