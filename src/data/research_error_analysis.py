"""
AGRO LIFE-AI
Research Error Analysis and Model Generalisation Investigation

Purpose:
    Analyse the Day-4 Early Quality Random Forest model using
    the existing GroupKFold predictions.

This script investigates:
    1. Overall prediction error
    2. Error by validation fold
    3. Error by treatment group
    4. Largest prediction errors
    5. Generalisation across unseen treatment groups
    6. Possible relationship between shelf-life range and errors

Important:
    This analysis does not claim that the model is universally accurate.
    The dataset contains only 48 observations and 16 treatment groups.
"""

from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "research_day4_features.csv"
)

PREDICTIONS_FILE = (
    PROJECT_ROOT
    / "results"
    / "predictions"
    / "research_model_predictions.csv"
)

RESULTS_DIR = PROJECT_ROOT / "results"

FIGURES_DIR = RESULTS_DIR / "figures"
REPORTS_DIR = RESULTS_DIR / "reports"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. LOAD DATA
# ============================================================

print("=" * 70)
print("AGRO LIFE-AI - ERROR ANALYSIS")
print("=" * 70)

print("\nLoading Day-4 research dataset...")

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found:\n{DATA_FILE}"
    )

df = pd.read_csv(DATA_FILE)

print(f"Dataset loaded.")
print(f"Records: {len(df)}")


# ============================================================
# 3. LOAD MODEL PREDICTIONS
# ============================================================

print("\nLoading saved model predictions...")

if not PREDICTIONS_FILE.exists():
    raise FileNotFoundError(
        f"Prediction file not found:\n{PREDICTIONS_FILE}"
    )

predictions = pd.read_csv(PREDICTIONS_FILE)

print("Prediction file loaded.")
print(f"Prediction records: {len(predictions)}")

print("\nPrediction columns:")
print(list(predictions.columns))


# ============================================================
# 4. INSPECT AND NORMALISE PREDICTION COLUMNS
# ============================================================

# The training script may use different naming conventions.
# We identify the important columns automatically.

column_map = {}

for column in predictions.columns:

    lower = column.lower()

    if "actual" in lower and "shelf" in lower:
        column_map["actual"] = column

    elif "predicted" in lower and "shelf" in lower:
        column_map["predicted"] = column

    elif lower == "actual":
        column_map["actual"] = column

    elif lower == "prediction":
        column_map["predicted"] = column

    elif "pred" in lower and "shelf" in lower:
        column_map["predicted"] = column

    elif "fold" in lower:
        column_map["fold"] = column

    elif "group" in lower:
        column_map["group"] = column

    elif "rep" in lower:
        column_map["rep"] = column


print("\nDetected prediction columns:")
print(column_map)


if "actual" not in column_map:
    raise ValueError(
        "Could not identify the actual shelf-life column "
        "in the prediction file."
    )

if "predicted" not in column_map:
    raise ValueError(
        "Could not identify the predicted shelf-life column "
        "in the prediction file."
    )


# ============================================================
# 5. SELECT THE CORRECT MODEL AND CREATE ANALYSIS DATAFRAME
# ============================================================

required_columns = {"model", "feature_set"}

missing_columns = required_columns.difference(predictions.columns)

if missing_columns:
    raise ValueError(
        f"Required model-identification columns are missing: "
        f"{sorted(missing_columns)}"
    )

analysis = predictions[
    predictions["model"].astype(str).str.strip().eq("Random Forest")
    & predictions["feature_set"].astype(str).str.strip().eq(
        "Day-4 Early Quality"
    )
].copy()

if analysis.empty:
    raise ValueError(
        "No predictions found for Random Forest - Day-4 Early Quality."
    )

if len(analysis) != 48:
    raise ValueError(
        f"Expected 48 out-of-fold predictions, but found {len(analysis)}."
    )

print("\nSelected model: Random Forest")
print("Selected feature set: Day-4 Early Quality")
print(f"Selected prediction records: {len(analysis)}")

# Verify that each validation fold contains 12 predictions.
if "fold" not in analysis.columns:
    raise ValueError("The prediction file does not contain a fold column.")

fold_counts = analysis["fold"].value_counts().sort_index()

print("\nPredictions per validation fold:")
print(fold_counts.to_string())

if len(fold_counts) != 4 or not fold_counts.eq(12).all():
    raise ValueError(
        "Expected four validation folds with 12 predictions each."
    )
# Create numeric actual and predicted shelf-life values.

analysis["actual_shelf_life"] = pd.to_numeric(
analysis[column_map["actual"]],
errors="coerce"
)

analysis["predicted_shelf_life"] = pd.to_numeric(
analysis[column_map["predicted"]],
errors="coerce"
)

# Calculate prediction errors.

analysis["absolute_error"] = (
analysis["actual_shelf_life"]
- analysis["predicted_shelf_life"]
).abs()

analysis["signed_error"] = (
analysis["predicted_shelf_life"]
- analysis["actual_shelf_life"]
)

analysis["squared_error"] = analysis["signed_error"] ** 2



# ============================================================
# 6. ADD GROUP / FOLD INFORMATION IF AVAILABLE
# ============================================================

if "group" in column_map:
    analysis["validation_group"] = analysis[
        column_map["group"]
    ].astype(str)
else:
    analysis["validation_group"] = "Unknown"

if "fold" in column_map:
    analysis["validation_fold"] = analysis[
        column_map["fold"]
    ]
else:
    analysis["validation_fold"] = "Unknown"

if "rep" in column_map:
    analysis["replication"] = analysis[
        column_map["rep"]
    ]
else:
    analysis["replication"] = "Unknown"


# ============================================================
# 7. CHECK FOR INVALID VALUES
# ============================================================

if analysis[
    ["actual_shelf_life", "predicted_shelf_life"]
].isna().any().any():

    raise ValueError(
        "Missing or invalid values were found in actual/predicted "
        "shelf-life values."
    )


# ============================================================
# 8. OVERALL ERROR METRICS
# ============================================================

actual = analysis["actual_shelf_life"]
predicted = analysis["predicted_shelf_life"]

mae = np.mean(np.abs(actual - predicted))

rmse = np.sqrt(
    np.mean((actual - predicted) ** 2)
)

ss_res = np.sum((actual - predicted) ** 2)
ss_tot = np.sum((actual - actual.mean()) ** 2)

if ss_tot != 0:
    r2 = 1 - (ss_res / ss_tot)
else:
    r2 = np.nan


# ============================================================
# 9. ERROR SUMMARY
# ============================================================

mean_absolute_error = analysis["absolute_error"].mean()
median_absolute_error = analysis["absolute_error"].median()
maximum_absolute_error = analysis["absolute_error"].max()

mean_signed_error = analysis["signed_error"].mean()

percentage_within_1_day = (
    (analysis["absolute_error"] <= 1.0).mean() * 100
)

percentage_within_2_days = (
    (analysis["absolute_error"] <= 2.0).mean() * 100
)


print("\nOverall error analysis:")
print("-" * 70)

print(
    f"MAE:                         {mae:.4f} days"
)

print(
    f"RMSE:                        {rmse:.4f} days"
)

print(
    f"R²:                          {r2:.4f}"
)

print(
    f"Median absolute error:       "
    f"{median_absolute_error:.4f} days"
)

print(
    f"Maximum absolute error:      "
    f"{maximum_absolute_error:.4f} days"
)

print(
    f"Mean signed error:           "
    f"{mean_signed_error:.4f} days"
)

print(
    f"Predictions within ±1 day:   "
    f"{percentage_within_1_day:.2f}%"
)

print(
    f"Predictions within ±2 days:   "
    f"{percentage_within_2_days:.2f}%"
)


# ============================================================
# 10. ERROR BY VALIDATION FOLD
# ============================================================

print("\nAnalysing validation folds...")

if analysis["validation_fold"].nunique() > 1:

    fold_summary = (
        analysis
        .groupby("validation_fold")
        .agg(
            observations=("actual_shelf_life", "count"),
            mae=("absolute_error", "mean"),
            rmse=(
                "squared_error",
                lambda x: np.sqrt(x.mean())
            ),
            mean_signed_error=("signed_error", "mean"),
        )
        .reset_index()
    )

else:

    fold_summary = pd.DataFrame(
        {
            "validation_fold": ["Unknown"],
            "observations": [len(analysis)],
            "mae": [mae],
            "rmse": [rmse],
            "mean_signed_error": [mean_signed_error],
        }
    )


print("\nFold performance:")
print("-" * 70)
print(fold_summary.to_string(index=False))


# ============================================================
# 11. ERROR BY TREATMENT GROUP
# ============================================================

print("\nAnalysing treatment groups...")

if analysis["validation_group"].nunique() > 1:

    group_summary = (
        analysis
        .groupby("validation_group")
        .agg(
            observations=("actual_shelf_life", "count"),
            actual_mean=("actual_shelf_life", "mean"),
            predicted_mean=("predicted_shelf_life", "mean"),
            mae=("absolute_error", "mean"),
            mean_signed_error=("signed_error", "mean"),
        )
        .reset_index()
        .sort_values(
            by="mae",
            ascending=False
        )
    )

else:

    group_summary = pd.DataFrame()


if not group_summary.empty:

    print("\nTreatment groups with largest errors:")
    print("-" * 70)

    print(
        group_summary.head(10).to_string(
            index=False
        )
    )


# ============================================================
# 12. LARGEST INDIVIDUAL ERRORS
# ============================================================

largest_errors = (
    analysis
    .sort_values(
        by="absolute_error",
        ascending=False
    )
    .head(10)
)


print("\nLargest individual prediction errors:")
print("-" * 70)

display_columns = [
    column
    for column in [
        "validation_fold",
        "validation_group",
        "replication",
        "actual_shelf_life",
        "predicted_shelf_life",
        "absolute_error",
        "signed_error",
    ]
    if column in largest_errors.columns
]

print(
    largest_errors[display_columns].to_string(
        index=False
    )
)


# ============================================================
# 13. SAVE DETAILED ERROR DATA
# ============================================================

error_file = (
    REPORTS_DIR
    / "research_day4_error_analysis.csv"
)

analysis.to_csv(
    error_file,
    index=False
)

print(
    f"\nDetailed error data saved:\n{error_file}"
)


# ============================================================
# 14. SAVE FOLD SUMMARY
# ============================================================

fold_file = (
    REPORTS_DIR
    / "research_day4_fold_error_summary.csv"
)

fold_summary.to_csv(
    fold_file,
    index=False
)

print(
    f"Fold summary saved:\n{fold_file}"
)


# ============================================================
# 15. SAVE GROUP SUMMARY
# ============================================================

if not group_summary.empty:

    group_file = (
        REPORTS_DIR
        / "research_day4_group_error_summary.csv"
    )

    group_summary.to_csv(
        group_file,
        index=False
    )

    print(
        f"Group summary saved:\n{group_file}"
    )


# ============================================================
# 16. ACTUAL VS PREDICTED FIGURE
# ============================================================

print("\nCreating actual-versus-predicted plot...")

plt.figure(figsize=(8, 6))

plt.scatter(
    actual,
    predicted
)

minimum = min(
    actual.min(),
    predicted.min()
)

maximum = max(
    actual.max(),
    predicted.max()
)

plt.plot(
    [minimum, maximum],
    [minimum, maximum],
    linestyle="--"
)

plt.xlabel("Actual Shelf Life (days)")
plt.ylabel("Predicted Shelf Life (days)")

plt.title(
    "Day-4 Random Forest: Actual vs Predicted Shelf Life"
)

plt.tight_layout()

actual_predicted_figure = (
    FIGURES_DIR
    / "research_day4_actual_vs_predicted_error_analysis.png"
)

plt.savefig(
    actual_predicted_figure,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    f"Figure saved:\n{actual_predicted_figure}"
)


# ============================================================
# 17. ABSOLUTE ERROR DISTRIBUTION
# ============================================================

print("\nCreating prediction-error distribution...")

plt.figure(figsize=(8, 6))

plt.hist(
    analysis["absolute_error"],
    bins=10
)

plt.xlabel("Absolute Prediction Error (days)")
plt.ylabel("Number of Observations")

plt.title(
    "Distribution of Day-4 Random Forest Prediction Errors"
)

plt.tight_layout()

error_distribution_figure = (
    FIGURES_DIR
    / "research_day4_error_distribution.png"
)

plt.savefig(
    error_distribution_figure,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    f"Figure saved:\n{error_distribution_figure}"
)


# ============================================================
# 18. IDENTIFY GENERALISATION INSTABILITY
# ============================================================

generalisation_statement = ""

if not fold_summary.empty and len(fold_summary) > 1:

    fold_mae_range = (
        fold_summary["mae"].max()
        - fold_summary["mae"].min()
    )

    if fold_mae_range > 1.0:

        generalisation_statement = (
            "Validation-fold errors vary substantially, "
            "indicating unstable generalisation across unseen "
            "treatment groups."
        )

    else:

        generalisation_statement = (
            "Validation-fold errors show comparatively limited "
            "variation, although the small dataset still limits "
            "strong claims about generalisation."
        )

else:

    generalisation_statement = (
        "Fold-level generalisation could not be fully assessed "
        "from the available prediction records."
    )


# ============================================================
# 19. GENERATE ACADEMIC ERROR ANALYSIS REPORT
# ============================================================

report_file = (
    REPORTS_DIR
    / "research_error_analysis_report.txt"
)

with open(
    report_file,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "AGRO LIFE-AI\n"
        "ERROR ANALYSIS AND MODEL GENERALISATION REPORT\n"
        "==============================================\n\n"
    )

    file.write(
        "Model analysed:\n"
        "Day-4 Early Quality Random Forest Regression\n\n"
    )

    file.write(
        "Dataset:\n"
        "Verified Dryad tomato shelf-life dataset\n\n"
    )

    file.write(
        f"Number of analysed predictions: {len(analysis)}\n\n"
    )

    file.write(
        "OVERALL PERFORMANCE\n"
        "-------------------\n"
    )

    file.write(
        f"MAE: {mae:.4f} days\n"
    )

    file.write(
        f"RMSE: {rmse:.4f} days\n"
    )

    file.write(
        f"R²: {r2:.4f}\n"
    )

    file.write(
        f"Median absolute error: "
        f"{median_absolute_error:.4f} days\n"
    )

    file.write(
        f"Maximum absolute error: "
        f"{maximum_absolute_error:.4f} days\n"
    )

    file.write(
        f"Mean signed error: "
        f"{mean_signed_error:.4f} days\n"
    )

    file.write(
        f"Predictions within ±1 day: "
        f"{percentage_within_1_day:.2f}%\n"
    )

    file.write(
        f"Predictions within ±2 days: "
        f"{percentage_within_2_days:.2f}%\n\n"
    )

    file.write(
        "VALIDATION FOLD ANALYSIS\n"
        "------------------------\n"
    )

    file.write(
        fold_summary.to_string(index=False)
    )

    file.write("\n\n")

    file.write(
        "GENERALISATION ASSESSMENT\n"
        "-------------------------\n"
    )

    file.write(
        generalisation_statement
    )

    file.write("\n\n")

    if not group_summary.empty:

        file.write(
            "TREATMENT GROUP ERROR ANALYSIS\n"
            "------------------------------\n"
        )

        file.write(
            group_summary.to_string(index=False)
        )

        file.write("\n\n")

    file.write(
        "LARGEST INDIVIDUAL ERRORS\n"
        "--------------------------\n"
    )

    file.write(
        largest_errors[display_columns].to_string(
            index=False
        )
    )

    file.write("\n\n")

    file.write(
        "ACADEMIC INTERPRETATION\n"
        "-----------------------\n"
    )

    file.write(
        "1. Error analysis was performed to determine whether "
        "the observed average model performance was consistent "
        "across validation groups.\n\n"
    )

    file.write(
        "2. Group-based validation is important because the "
        "research dataset contains repeated observations from "
        "the same treatment combinations.\n\n"
    )

    file.write(
        "3. Differences in fold-level performance indicate that "
        "the model's predictive behaviour may depend on the "
        "treatment groups represented in the training data.\n\n"
    )

    file.write(
        "4. A low average MAE should therefore not be interpreted "
        "as evidence that the model will perform equally well "
        "on all future tomato samples.\n\n"
    )

    file.write(
        "5. The dataset contains only 48 observations and a "
        "relatively narrow shelf-life range. These factors limit "
        "the statistical strength and generalisability of the "
        "prototype model.\n\n"
    )

    file.write(
        "6. The model should be described as an experimental "
        "machine-learning prototype rather than a production-ready "
        "agricultural decision system.\n\n"
    )

    file.write(
        "7. Further validation using additional independent "
        "agricultural observations would be required before "
        "deployment or operational use.\n"
    )


print(
    f"\nAcademic error-analysis report saved:\n"
    f"{report_file}"
)


# ============================================================
# 20. FINAL OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("ERROR ANALYSIS COMPLETED SUCCESSFULLY")
print("=" * 70)

print("\nGenerated analysis files:")

print(
    f"\n1. Detailed error data:\n"
    f"   {error_file}"
)

print(
    f"\n2. Fold error summary:\n"
    f"   {fold_file}"
)

if not group_summary.empty:

    print(
        f"\n3. Treatment-group error summary:\n"
        f"   {group_file}"
    )

print(
    f"\n4. Actual vs predicted figure:\n"
    f"   {actual_predicted_figure}"
)

print(
    f"\n5. Error distribution figure:\n"
    f"   {error_distribution_figure}"
)

print(
    f"\n6. Academic error-analysis report:\n"
    f"   {report_file}"
)

print("\nKey generalisation assessment:")
print(generalisation_statement)

print("\nNext stage:")
print("Leakage/generalisation check and final research-model decision.")

print("\n" + "=" * 70)