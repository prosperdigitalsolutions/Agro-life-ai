"""
Research Model Interpretation
AGRO LIFE-AI Mini Project

Purpose:
    Interpret the Day-4 Early Quality Random Forest model by:
    1. Calculating feature importance.
    2. Ranking the model predictors.
    3. Creating a feature-importance visualization.
    4. Saving an interpretation report.

Important:
    This is a research prototype using the verified Dryad tomato dataset.
    Feature importance describes the model's internal use of predictors.
    It does NOT prove causation.
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import joblib


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

MODEL_FILE = (
    PROJECT_ROOT
    / "models"
    / "research_day4_early_quality_random_forest.joblib"
)

RESULTS_DIR = PROJECT_ROOT / "results"

FIGURES_DIR = RESULTS_DIR / "figures"
REPORTS_DIR = RESULTS_DIR / "reports"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. FEATURES USED BY THE MODEL
# ============================================================

FEATURES = [
    "neem_extract_percent",
    "beeswax_coating_percent",
    "aa_day4",
    "ph_day4",
    "ta_day4",
    "tss_day4",
    "weight_loss_day4",
]

TARGET = "shelf_life_days"


# ============================================================
# 3. LOAD DATA
# ============================================================

print("=" * 70)
print("AGRO LIFE-AI - RESEARCH MODEL INTERPRETATION")
print("=" * 70)

print("\nLoading research dataset...")

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Research dataset not found:\n{DATA_FILE}"
    )

df = pd.read_csv(DATA_FILE)

print(f"Dataset loaded successfully.")
print(f"Records: {len(df)}")
print(f"Columns: {len(df.columns)}")


# ============================================================
# 4. LOAD MODEL
# ============================================================

print("\nLoading Day-4 Random Forest model...")

if not MODEL_FILE.exists():
    raise FileNotFoundError(
        f"Model file not found:\n{MODEL_FILE}"
    )

model = joblib.load(MODEL_FILE)

print("Model loaded successfully.")
print(f"Model type: {type(model).__name__}")


# ============================================================
# 5. CHECK FEATURES
# ============================================================

print("\nChecking required features...")

missing_features = [
    feature for feature in FEATURES
    if feature not in df.columns
]

if missing_features:
    raise ValueError(
        f"Missing required features: {missing_features}"
    )

print("All required model features are available.")


# ============================================================
# 6. EXTRACT FEATURE IMPORTANCE
# ============================================================

print("\nCalculating feature importance...")

importance_values = model.feature_importances_

if len(importance_values) != len(FEATURES):
    raise ValueError(
        "Number of model feature importances does not match "
        "the expected number of features."
    )

importance_df = pd.DataFrame(
    {
        "feature": FEATURES,
        "importance": importance_values,
    }
)

importance_df = importance_df.sort_values(
    by="importance",
    ascending=False
).reset_index(drop=True)


# ============================================================
# 7. FEATURE DISPLAY NAMES
# ============================================================

display_names = {
    "neem_extract_percent": "Neem Extract (%)",
    "beeswax_coating_percent": "Beeswax Coating (%)",
    "aa_day4": "Ascorbic Acid - Day 4",
    "ph_day4": "pH - Day 4",
    "ta_day4": "Titratable Acidity - Day 4",
    "tss_day4": "Total Soluble Solids - Day 4",
    "weight_loss_day4": "Weight Loss - Day 4",
}

importance_df["display_name"] = importance_df["feature"].map(
    display_names
)


# ============================================================
# 8. SAVE FEATURE IMPORTANCE TABLE
# ============================================================

importance_csv = (
    REPORTS_DIR
    / "research_day4_feature_importance.csv"
)

importance_df.to_csv(
    importance_csv,
    index=False
)

print("\nFeature importance:")
print("-" * 70)

for _, row in importance_df.iterrows():
    print(
        f"{row['display_name']:<35} "
        f"{row['importance']:.6f}"
    )

print(f"\nSaved table:")
print(importance_csv)


# ============================================================
# 9. CREATE FEATURE IMPORTANCE CHART
# ============================================================

print("\nCreating feature-importance chart...")

plot_df = importance_df.sort_values(
    by="importance",
    ascending=True
)

plt.figure(figsize=(10, 6))

plt.barh(
    plot_df["display_name"],
    plot_df["importance"]
)

plt.xlabel("Random Forest Feature Importance")
plt.ylabel("Feature")
plt.title(
    "Day-4 Early Quality Random Forest Feature Importance"
)

plt.tight_layout()

figure_file = (
    FIGURES_DIR
    / "research_day4_feature_importance.png"
)

plt.savefig(
    figure_file,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(f"Chart saved:")
print(figure_file)


# ============================================================
# 10. IDENTIFY MOST IMPORTANT FEATURE
# ============================================================

top_feature = importance_df.iloc[0]

top_feature_name = top_feature["display_name"]
top_feature_value = top_feature["importance"]


# ============================================================
# 11. GENERATE INTERPRETATION REPORT
# ============================================================

report_file = (
    REPORTS_DIR
    / "research_model_interpretation.txt"
)

with open(report_file, "w", encoding="utf-8") as file:

    file.write(
        "AGRO LIFE-AI\n"
        "RESEARCH MODEL INTERPRETATION REPORT\n"
        "====================================\n\n"
    )

    file.write(
        "Model:\n"
        "Day-4 Early Quality Random Forest Regression\n\n"
    )

    file.write(
        "Dataset:\n"
        "Verified Dryad tomato shelf-life research dataset\n\n"
    )

    file.write(
        f"Number of observations: {len(df)}\n"
    )

    file.write(
        f"Number of predictors: {len(FEATURES)}\n\n"
    )

    file.write(
        "Prediction target:\n"
        "Shelf life (days)\n\n"
    )

    file.write(
        "FEATURE IMPORTANCE\n"
        "------------------\n"
    )

    for _, row in importance_df.iterrows():

        file.write(
            f"{row['display_name']}: "
            f"{row['importance']:.6f}\n"
        )

    file.write("\n")

    file.write(
        "MOST IMPORTANT MODEL FEATURE\n"
        "----------------------------\n"
    )

    file.write(
        f"{top_feature_name}\n"
        f"Importance value: {top_feature_value:.6f}\n\n"
    )

    file.write(
        "INTERPRETATION NOTES\n"
        "--------------------\n"
    )

    file.write(
        "1. Feature importance indicates how much each predictor "
        "contributed to the Random Forest's internal decision process.\n\n"
    )

    file.write(
        "2. A higher feature-importance value means that the model "
        "relied more heavily on that predictor when constructing "
        "its regression trees.\n\n"
    )

    file.write(
        "3. Feature importance does not establish a causal "
        "relationship between a predictor and shelf life.\n\n"
    )

    file.write(
        "4. The Day-4 measurements are used because they represent "
        "information available by the fourth day of storage. "
        "Measurements collected after Day 4 are therefore excluded "
        "from this early-prediction feature set.\n\n"
    )

    file.write(
        "5. The dataset contains only 48 observations from 16 "
        "treatment combinations with three replications each. "
        "Therefore, feature-importance results should be interpreted "
        "as evidence from this research dataset rather than as a "
        "universal ranking of agricultural shelf-life factors.\n\n"
    )

    file.write(
        "6. The model's validation results showed substantial "
        "variation between GroupKFold folds. This indicates that "
        "generalisation to unseen treatment groups remains an "
        "important limitation of the prototype.\n\n"
    )

    file.write(
        "7. Strong association between Day-4 quality measurements "
        "and the experimentally measured shelf-life outcome does "
        "not by itself prove that these variables cause the observed "
        "shelf-life differences.\n"
    )


print(f"\nInterpretation report saved:")
print(report_file)


# ============================================================
# 12. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("MODEL INTERPRETATION COMPLETED SUCCESSFULLY")
print("=" * 70)

print("\nGenerated files:")

print(
    f"1. Feature importance CSV:\n"
    f"   {importance_csv}"
)

print(
    f"\n2. Feature importance chart:\n"
    f"   {figure_file}"
)

print(
    f"\n3. Interpretation report:\n"
    f"   {report_file}"
)

print(
    f"\nMost important model feature:\n"
    f"   {top_feature_name}"
)

print(
    f"\nImportance value:\n"
    f"   {top_feature_value:.6f}"
)

print("\nNext stage:")
print("Error analysis and model generalisation investigation.")

print("\n" + "=" * 70)