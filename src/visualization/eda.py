"""
AGRO LIFE-AI
Exploratory Data Analysis

Biochemical Decay & Shelf-Life Predictor
DMI St. Eugene University
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------
# PROJECT PATH
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "sample"
    / "sample_shelf_life_data.csv"
)

FIGURES_DIR = (
    PROJECT_ROOT
    / "results"
    / "figures"
)

FIGURES_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

def load_data():
    """Load the shelf-life dataset."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    return pd.read_csv(DATA_FILE)


# ---------------------------------------------------------
# TEMPERATURE VS SHELF LIFE
# ---------------------------------------------------------

def plot_temperature_vs_shelf_life(data):

    plt.figure(figsize=(8, 5))

    plt.scatter(
        data["temperature_c"],
        data["shelf_life_days"]
    )

    plt.xlabel("Temperature (°C)")
    plt.ylabel("Shelf Life (Days)")
    plt.title("Temperature vs Shelf Life")

    plt.grid(True)

    output_file = (
        FIGURES_DIR
        / "temperature_vs_shelf_life.png"
    )

    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_file}")


# ---------------------------------------------------------
# HUMIDITY VS SHELF LIFE
# ---------------------------------------------------------

def plot_humidity_vs_shelf_life(data):

    plt.figure(figsize=(8, 5))

    plt.scatter(
        data["humidity_percent"],
        data["shelf_life_days"]
    )

    plt.xlabel("Humidity (%)")
    plt.ylabel("Shelf Life (Days)")
    plt.title("Humidity vs Shelf Life")

    plt.grid(True)

    output_file = (
        FIGURES_DIR
        / "humidity_vs_shelf_life.png"
    )

    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_file}")


# ---------------------------------------------------------
# WEIGHT LOSS VS SHELF LIFE
# ---------------------------------------------------------

def plot_weight_loss_vs_shelf_life(data):

    plt.figure(figsize=(8, 5))

    plt.scatter(
        data["weight_loss_percent"],
        data["shelf_life_days"]
    )

    plt.xlabel("Weight Loss (%)")
    plt.ylabel("Shelf Life (Days)")
    plt.title("Weight Loss vs Shelf Life")

    plt.grid(True)

    output_file = (
        FIGURES_DIR
        / "weight_loss_vs_shelf_life.png"
    )

    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_file}")


# ---------------------------------------------------------
# QUALITY SCORE VS SHELF LIFE
# ---------------------------------------------------------

def plot_quality_vs_shelf_life(data):

    plt.figure(figsize=(8, 5))

    plt.scatter(
        data["quality_score"],
        data["shelf_life_days"]
    )

    plt.xlabel("Quality Score")
    plt.ylabel("Shelf Life (Days)")
    plt.title("Quality Score vs Shelf Life")

    plt.grid(True)

    output_file = (
        FIGURES_DIR
        / "quality_vs_shelf_life.png"
    )

    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_file}")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("AGRO LIFE-AI - EXPLORATORY DATA ANALYSIS")
    print("=" * 60)

    data = load_data()

    print("\nDataset loaded.")
    print("Records:", len(data))

    print("\nGenerating visualizations...")

    plot_temperature_vs_shelf_life(data)
    plot_humidity_vs_shelf_life(data)
    plot_weight_loss_vs_shelf_life(data)
    plot_quality_vs_shelf_life(data)

    print("\nExploratory analysis completed.")
    print(f"Figures saved in: {FIGURES_DIR}")


if __name__ == "__main__":
    main()