"""
AGRO LIFE-AI
Model Results Visualization Module

Biochemical Decay & Shelf-Life Predictor
DMI St. Eugene University
BSc Computer Science - Mini Project
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PREDICTIONS_FILE = (
    PROJECT_ROOT
    / "results"
    / "predictions"
    / "shelf_life_predictions.csv"
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

COMPARISON_FILE = (
    REPORTS_DIR
    / "actual_vs_predicted.csv"
)

COMPARISON_FIGURE = (
    FIGURES_DIR
    / "actual_vs_predicted_shelf_life.png"
)

FIGURES_DIR.mkdir(
    parents=True,
    exist_ok=True
)

REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def load_predictions():
    """Load actual and predicted shelf-life values."""

    if not PREDICTIONS_FILE.exists():
        raise FileNotFoundError(
            f"Prediction file not found: {PREDICTIONS_FILE}"
        )

    return pd.read_csv(PREDICTIONS_FILE)


def calculate_errors(data):
    """Calculate prediction errors."""

    results = data.copy()

    results["error_days"] = (
        results["predicted_shelf_life_days"]
        - results["actual_shelf_life_days"]
    )

    results["absolute_error_days"] = (
        results["error_days"].abs()
    )

    return results


def save_comparison_results(data):
    """Save actual versus predicted results."""

    data.to_csv(
        COMPARISON_FILE,
        index=False
    )


def create_comparison_chart(data):
    """Create actual versus predicted shelf-life chart."""

    sample_numbers = range(
        1,
        len(data) + 1
    )

    plt.figure(figsize=(9, 6))

    plt.plot(
        sample_numbers,
        data["actual_shelf_life_days"],
        marker="o",
        label="Actual Shelf Life"
    )

    plt.plot(
        sample_numbers,
        data["predicted_shelf_life_days"],
        marker="s",
        linestyle="--",
        label="Predicted Shelf Life"
    )

    plt.xlabel("Test Sample")
    plt.ylabel("Shelf Life (Days)")

    plt.title(
        "Actual vs Predicted Shelf Life"
    )

    plt.xticks(
        list(sample_numbers)
    )

    plt.legend()

    plt.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        COMPARISON_FIGURE,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def main():

    print("=" * 60)
    print("AGRO LIFE-AI - MODEL RESULTS VISUALIZATION")
    print("=" * 60)

    print("\nLoading model predictions...")

    data = load_predictions()

    print("Prediction results loaded successfully.")

    print("\nNumber of test samples:", len(data))

    results = calculate_errors(data)

    print("\n" + "=" * 60)
    print("ACTUAL VS PREDICTED RESULTS")
    print("=" * 60)

    for index, row in results.iterrows():

        print(
            f"Sample {index + 1}: "
            f"Actual = "
            f"{row['actual_shelf_life_days']:.2f} days | "
            f"Predicted = "
            f"{row['predicted_shelf_life_days']:.2f} days | "
            f"Error = "
            f"{row['error_days']:.2f} days"
        )

    print("\n" + "=" * 60)
    print("ERROR ANALYSIS")
    print("=" * 60)

    mean_absolute_error = (
        results["absolute_error_days"].mean()
    )

    maximum_error = (
        results["absolute_error_days"].max()
    )

    minimum_error = (
        results["absolute_error_days"].min()
    )

    print(
        f"\nMean Absolute Error: "
        f"{mean_absolute_error:.4f} days"
    )

    print(
        f"Maximum Absolute Error: "
        f"{maximum_error:.4f} days"
    )

    print(
        f"Minimum Absolute Error: "
        f"{minimum_error:.4f} days"
    )

    save_comparison_results(
        results
    )

    print("\nComparison results saved:")
    print(COMPARISON_FILE)

    print("\nCreating comparison chart...")

    create_comparison_chart(
        results
    )

    print("\nComparison chart saved:")
    print(COMPARISON_FIGURE)

    print("\n" + "=" * 60)
    print("MODEL RESULTS VISUALIZATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()