import pandas as pd
import os


# ============================================================
# AGRO LIFE-AI
# PREDICTION WINDOW ANALYSIS
# ============================================================

DATA_FILE = r".\data\processed\research_master_dataset.csv"
REPORT_FOLDER = r".\results\reports"

OUTPUT_FILE = os.path.join(
    REPORT_FOLDER,
    "prediction_window_analysis.txt"
)


# ------------------------------------------------------------
# Load research master dataset
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

def analyze_prediction_windows():

    print("\n" + "=" * 75)
    print("AGRO LIFE-AI - PREDICTION WINDOW ANALYSIS")
    print("=" * 75)

    df = load_dataset()

    os.makedirs(REPORT_FOLDER, exist_ok=True)

    report = []

    # --------------------------------------------------------
    # Basic information
    # --------------------------------------------------------

    report.append("=" * 75)
    report.append("AGRO LIFE-AI - PREDICTION WINDOW ANALYSIS")
    report.append("=" * 75)

    report.append("\nDATASET")
    report.append("-" * 75)
    report.append(f"Records: {len(df)}")
    report.append(f"Columns: {len(df.columns)}")

    # --------------------------------------------------------
    # Define prediction windows
    # --------------------------------------------------------

    windows = {
        "Day 4": {
            "AA": "AAat4thD",
            "pH": "pHat4thD",
            "TA": "TAat4thD",
            "TSS": "TSSat4thD",
            "WL": "WLat4thD",
        },

        "Day 8": {
            "AA": "AAat8thD",
            "pH": "pHat8thD",
            "TA": "TAat8thD",
            "TSS": "TSSat8thD",
            "WL": "WLat8thD",
            "Marketability": "%Mat8thD",
        },

        "Day 12": {
            "AA": "AAat12thD",
            "pH": "pHat12thD",
            "TA": "TAat12thD",
            "TSS": "TSSat12thD",
            "WL": "WLat12thD",
            "Marketability": "%Mat12thD",
            "Decay": "%Decayat12thD",
        },
    }

    # --------------------------------------------------------
    # Treatment variables
    # --------------------------------------------------------

    treatment_features = [
        "Neem leaf extract dipping",
        "Beeswax coating",
        "Treatments",
    ]

    report.append("\n\nTREATMENT INFORMATION")
    report.append("-" * 75)

    for feature in treatment_features:
        report.append(f"- {feature}")

    # --------------------------------------------------------
    # Analyze each prediction window
    # --------------------------------------------------------

    for window_name, features in windows.items():

        report.append("\n\n" + "=" * 75)
        report.append(f"{window_name.upper()} PREDICTION WINDOW")
        report.append("=" * 75)

        report.append(
            "\nFeatures available at this prediction point:"
        )

        selected_features = treatment_features + list(
            features.values()
        )

        for feature in selected_features:
            report.append(f"- {feature}")

        # ----------------------------------------------------
        # Check whether every feature exists
        # ----------------------------------------------------

        missing_features = [
            feature
            for feature in selected_features
            if feature not in df.columns
        ]

        if missing_features:

            report.append(
                "\nMISSING FEATURES:"
            )

            for feature in missing_features:
                report.append(f"- {feature}")

            continue

        report.append(
            "\nAll prediction-window features are available."
        )

        # ----------------------------------------------------
        # Missing-value check
        # ----------------------------------------------------

        window_df = df[selected_features].copy()

        missing = window_df.isnull().sum()

        report.append(
            "\nMissing values:"
        )

        if missing.sum() == 0:
            report.append("None")
        else:
            report.append(
                missing[missing > 0].to_string()
            )

        # ----------------------------------------------------
        # Descriptive statistics
        # ----------------------------------------------------

        numeric_features = list(
            features.values()
        )

        report.append(
            "\nDescriptive statistics:"
        )

        statistics = (
            df[numeric_features]
            .describe()
            .round(3)
        )

        report.append(
            statistics.to_string()
        )

        # ----------------------------------------------------
        # Correlation with shelf life
        # ----------------------------------------------------

        report.append(
            "\nCorrelation with shelf life:"
        )

        correlations = (
            df[numeric_features + ["shelf-life"]]
            .corr()["shelf-life"]
            .drop("shelf-life")
            .sort_values(
                key=lambda values: values.abs(),
                ascending=False
            )
        )

        report.append(
            correlations.round(4).to_string()
        )

        # ----------------------------------------------------
        # Absolute correlation summary
        # ----------------------------------------------------

        report.append(
            "\nAbsolute correlation strength:"
        )

        absolute_correlations = (
            correlations.abs()
            .sort_values(ascending=False)
        )

        report.append(
            absolute_correlations.round(4).to_string()
        )

    # --------------------------------------------------------
    # Comparison table
    # --------------------------------------------------------

    report.append("\n\n" + "=" * 75)
    report.append("PREDICTION WINDOW COMPARISON")
    report.append("=" * 75)

    comparison_rows = []

    for window_name, features in windows.items():

        numeric_features = list(
            features.values()
        )

        correlations = (
            df[numeric_features + ["shelf-life"]]
            .corr()["shelf-life"]
            .drop("shelf-life")
        )

        strongest_feature = correlations.abs().idxmax()
        strongest_correlation = correlations[
            strongest_feature
        ]

        comparison_rows.append({
            "Prediction Window": window_name,
            "Number of Quality Features": len(numeric_features),
            "Strongest Feature": strongest_feature,
            "Correlation": round(
                strongest_correlation,
                4
            ),
        })

    comparison = pd.DataFrame(
        comparison_rows
    )

    report.append(
        comparison.to_string(index=False)
    )

    # --------------------------------------------------------
    # Important methodological notes
    # --------------------------------------------------------

    report.append("\n\n" + "=" * 75)
    report.append("METHODOLOGICAL NOTES")
    report.append("=" * 75)

    report.append(
        "\n1. The prediction windows represent information "
        "available by Day 4, Day 8, and Day 12."
    )

    report.append(
        "\n2. Measurements collected after a prediction "
        "window must not be used to claim that the model "
        "made an early prediction."
    )

    report.append(
        "\n3. The analysis does not establish causation "
        "between individual measurements and shelf life."
    )

    report.append(
        "\n4. Correlation alone will not be used to select "
        "the final machine-learning model."
    )

    report.append(
        "\n5. The research dataset contains only 48 "
        "experimental observations, so model complexity "
        "must be kept appropriate for the sample size."
    )

    report.append(
        "\n6. Replications belonging to the same treatment "
        "combination must be considered when designing "
        "model validation."
    )

    # --------------------------------------------------------
    # Save report
    # --------------------------------------------------------

    final_report = "\n".join(report)

    print(final_report)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(final_report)

    print("\n" + "=" * 75)
    print("PREDICTION WINDOW ANALYSIS COMPLETED")
    print("=" * 75)

    print("\nReport saved to:")
    print(OUTPUT_FILE)


# ------------------------------------------------------------
# Program entry point
# ------------------------------------------------------------

if __name__ == "__main__":
    analyze_prediction_windows()