import pandas as pd
import os


# ============================================================
# AGRO LIFE-AI
# RESEARCH DATASET ANALYSIS
# ============================================================

DATA_FILE = r".\data\processed\research_master_dataset.csv"
REPORT_FOLDER = r".\results\reports"

SUMMARY_FILE = os.path.join(
    REPORT_FOLDER,
    "research_dataset_analysis.txt"
)


# ------------------------------------------------------------
# Load dataset
# ------------------------------------------------------------

def load_dataset():

    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(
            f"Research master dataset not found:\n{DATA_FILE}"
        )

    return pd.read_csv(DATA_FILE)


# ------------------------------------------------------------
# Main analysis
# ------------------------------------------------------------

def analyze_dataset():

    print("\n" + "=" * 75)
    print("AGRO LIFE-AI - RESEARCH DATASET ANALYSIS")
    print("=" * 75)

    df = load_dataset()

    os.makedirs(REPORT_FOLDER, exist_ok=True)

    report = []

    # --------------------------------------------------------
    # Basic information
    # --------------------------------------------------------

    report.append("=" * 75)
    report.append("AGRO LIFE-AI - RESEARCH DATASET ANALYSIS")
    report.append("=" * 75)

    report.append("\n1. DATASET OVERVIEW")
    report.append("-" * 75)

    report.append(f"Number of records: {len(df)}")
    report.append(f"Number of columns: {len(df.columns)}")

    report.append("\nColumn names:")

    for number, column in enumerate(df.columns, start=1):
        report.append(f"{number:02d}. {column}")

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    report.append("\n\n2. MISSING VALUE ANALYSIS")
    report.append("-" * 75)

    missing = df.isnull().sum()

    if missing.sum() == 0:
        report.append("No missing values detected.")
    else:
        report.append(
            missing[missing > 0].to_string()
        )

    # --------------------------------------------------------
    # Target variable
    # --------------------------------------------------------

    report.append("\n\n3. SHELF-LIFE TARGET ANALYSIS")
    report.append("-" * 75)

    shelf = df["shelf-life"]

    report.append(
        shelf.describe().to_string()
    )

    report.append("\nShelf-life frequency:")
    report.append(
        shelf.value_counts()
        .sort_index()
        .to_string()
    )

    # --------------------------------------------------------
    # Treatment analysis
    # --------------------------------------------------------

    report.append("\n\n4. TREATMENT ANALYSIS")
    report.append("-" * 75)

    report.append("\nNeem leaf extract levels:")
    report.append(
        df["Neem leaf extract dipping"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    report.append("\nBeeswax coating levels:")
    report.append(
        df["Beeswax coating"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    report.append("\nTreatment combinations:")
    report.append(
        df["Treatments"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    # --------------------------------------------------------
    # Replication analysis
    # --------------------------------------------------------

    report.append("\n\n5. REPLICATION ANALYSIS")
    report.append("-" * 75)

    report.append(
        df["rep"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    # --------------------------------------------------------
    # Correlation analysis
    # --------------------------------------------------------

    report.append("\n\n6. CORRELATION WITH SHELF LIFE")
    report.append("-" * 75)

    numeric_df = df.select_dtypes(include="number")

    correlations = (
        numeric_df.corr()["shelf-life"]
        .sort_values(ascending=False)
    )

    report.append(
        correlations.to_string()
    )

    # --------------------------------------------------------
    # Strong correlations
    # --------------------------------------------------------

    report.append("\n\n7. STRONG CORRELATIONS")
    report.append("-" * 75)

    strong = correlations[
        correlations.abs() >= 0.70
    ]

    report.append(
        strong.to_string()
    )

    # --------------------------------------------------------
    # Measurement-day coverage
    # --------------------------------------------------------

    report.append("\n\n8. MEASUREMENT-DAY COVERAGE")
    report.append("-" * 75)

    measurement_groups = {
        "Ascorbic Acid (AA)": [
            column for column in df.columns
            if column.startswith("AAat")
        ],

        "Decay": [
            column for column in df.columns
            if column.startswith("%Decayat")
        ],

        "Marketability": [
            column for column in df.columns
            if column.startswith("%Mat")
        ],

        "pH": [
            column for column in df.columns
            if column.startswith("pHat")
        ],

        "Titratable Acidity (TA)": [
            column for column in df.columns
            if column.startswith("TAat")
        ],

        "Total Soluble Solids (TSS)": [
            column for column in df.columns
            if column.startswith("TSSat")
        ],

        "Weight Loss (WL)": [
            column for column in df.columns
            if column.startswith("WLat")
        ],
    }

    for name, columns in measurement_groups.items():

        report.append(
            f"\n{name}: {len(columns)} measurements"
        )

        for column in columns:
            report.append(f"  - {column}")

    # --------------------------------------------------------
    # Relationship of treatment and shelf life
    # --------------------------------------------------------

    report.append("\n\n9. SHELF LIFE BY TREATMENT")
    report.append("-" * 75)

    treatment_summary = (
        df.groupby("Treatments")["shelf-life"]
        .agg(["count", "mean", "min", "max"])
        .round(2)
    )

    report.append(
        treatment_summary.to_string()
    )

    # --------------------------------------------------------
    # Relationship of neem concentration
    # --------------------------------------------------------

    report.append("\n\n10. SHELF LIFE BY NEEM EXTRACT LEVEL")
    report.append("-" * 75)

    neem_summary = (
        df.groupby("Neem leaf extract dipping")["shelf-life"]
        .agg(["count", "mean", "min", "max"])
        .round(2)
    )

    report.append(
        neem_summary.to_string()
    )

    # --------------------------------------------------------
    # Relationship of beeswax concentration
    # --------------------------------------------------------

    report.append("\n\n11. SHELF LIFE BY BEESWAX COATING LEVEL")
    report.append("-" * 75)

    beeswax_summary = (
        df.groupby("Beeswax coating")["shelf-life"]
        .agg(["count", "mean", "min", "max"])
        .round(2)
    )

    report.append(
        beeswax_summary.to_string()
    )

    # --------------------------------------------------------
    # Print report
    # --------------------------------------------------------

    final_report = "\n".join(report)

    print(final_report)

    # --------------------------------------------------------
    # Save report
    # --------------------------------------------------------

    with open(
        SUMMARY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(final_report)

    print("\n" + "=" * 75)
    print("ANALYSIS COMPLETED")
    print("=" * 75)

    print(f"\nAnalysis report saved to:")
    print(SUMMARY_FILE)


# ------------------------------------------------------------
# Program entry point
# ------------------------------------------------------------

if __name__ == "__main__":
    analyze_dataset()