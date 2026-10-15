"""
AGRO LIFE-AI
Final Research Prototype Model Training

Purpose:
Train the final shelf-life prediction model selected from the
research feature comparison.

Selected features:
    - weight_loss_day4
    - ta_day4

Model:
    Random Forest Regressor

Important:
This model is a research prototype trained on the available
48-observation research dataset. It is not independently
validated for general commercial or agricultural deployment.
"""

from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "research_day4_features.csv"
)

MODEL_DIR = PROJECT_ROOT / "models"
REPORT_DIR = PROJECT_ROOT / "results" / "reports"
PREDICTION_DIR = PROJECT_ROOT / "results" / "predictions"


MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
PREDICTION_DIR.mkdir(parents=True, exist_ok=True)


MODEL_FILE = MODEL_DIR / "final_research_shelf_life_model.joblib"
METADATA_FILE = MODEL_DIR / "final_research_model_metadata.json"
PREDICTION_FILE = (
    PREDICTION_DIR / "final_research_model_training_predictions.csv"
)
REPORT_FILE = REPORT_DIR / "final_research_model_report.txt"


# ============================================================
# CONFIGURATION
# ============================================================

FEATURES = [
    "weight_loss_day4",
    "ta_day4",
]

TARGET = "shelf_life_days"

RANDOM_FOREST_SETTINGS = {
    "n_estimators": 200,
    "random_state": 42,
    "max_depth": 4,
    "min_samples_leaf": 2,
}


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("AGRO LIFE-AI")
print("FINAL RESEARCH PROTOTYPE MODEL")
print("=" * 70)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading research dataset...")

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Research dataset not found:\n{DATA_FILE}"
    )

df = pd.read_csv(DATA_FILE)

print(f"Records: {len(df)}")
print(f"Columns: {len(df.columns)}")


# ============================================================
# VALIDATION
# ============================================================

print("\nValidating required columns...")

required_columns = FEATURES + [TARGET]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

if df[required_columns].isnull().any().any():
    raise ValueError(
        "Missing values detected in model features or target."
    )

if len(df) != 48:
    print(
        f"WARNING: Expected 48 research observations, "
        f"but found {len(df)}."
    )

print("Required columns found.")
print("No missing values detected.")


# ============================================================
# PREPARE FEATURES AND TARGET
# ============================================================

X = df[FEATURES].copy()
y = df[TARGET].copy()

print("\nSelected model features:")

for feature in FEATURES:
    print(f"  - {feature}")

print(f"\nTarget:")
print(f"  - {TARGET}")


# ============================================================
# TRAIN FINAL MODEL
# ============================================================

print("\nTraining final Random Forest model...")

model = RandomForestRegressor(
    **RANDOM_FOREST_SETTINGS
)

model.fit(X, y)

print("Model training completed successfully.")


# ============================================================
# TRAINING-SET PREDICTIONS
# ============================================================

training_predictions = model.predict(X)

prediction_df = df[
    [
        "group",
        "rep",
        "neem_extract_percent",
        "beeswax_coating_percent",
        "weight_loss_day4",
        "ta_day4",
        "shelf_life_days",
    ]
].copy()

prediction_df["predicted_shelf_life_days"] = training_predictions

prediction_df["absolute_error_days"] = (
    prediction_df["shelf_life_days"]
    - prediction_df["predicted_shelf_life_days"]
).abs()

prediction_df.to_csv(
    PREDICTION_FILE,
    index=False
)

print(
    f"\nTraining predictions saved:\n"
    f"{PREDICTION_FILE}"
)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

feature_importance = dict(
    zip(
        FEATURES,
        model.feature_importances_
    )
)

print("\nFeature importance:")

for feature, importance in feature_importance.items():
    print(
        f"  {feature}: {importance:.6f}"
    )


# ============================================================
# MODEL METADATA
# ============================================================

metadata = {
    "project": "AGRO LIFE-AI",
    "model_name": "Final Research Shelf-Life Prediction Model",
    "model_type": "RandomForestRegressor",
    "purpose": (
        "Research prototype for estimating tomato shelf life "
        "from selected Day-4 quality measurements."
    ),
    "dataset": {
        "file": str(DATA_FILE),
        "records": int(len(df)),
        "target": TARGET,
    },
    "features": FEATURES,
    "random_forest_settings": RANDOM_FOREST_SETTINGS,
    "feature_importance": feature_importance,
    "validation_note": (
        "The model was selected after GroupKFold comparisons "
        "of candidate feature sets. The final model is trained "
        "on all available research observations for prototype "
        "demonstration. It should not be interpreted as "
        "independently validated for commercial deployment."
    ),
}

with open(
    METADATA_FILE,
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        metadata,
        file,
        indent=4
    )

print(
    f"\nModel metadata saved:\n"
    f"{METADATA_FILE}"
)


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    model,
    MODEL_FILE
)

print(
    f"\nFinal model saved:\n"
    f"{MODEL_FILE}"
)


# ============================================================
# REPORT
# ============================================================

mean_training_error = (
    prediction_df["absolute_error_days"].mean()
)

max_training_error = (
    prediction_df["absolute_error_days"].max()
)

report_lines = [
    "=" * 70,
    "AGRO LIFE-AI",
    "FINAL RESEARCH PROTOTYPE MODEL REPORT",
    "=" * 70,
    "",
    "MODEL INFORMATION",
    "-" * 70,
    f"Model type: Random Forest Regressor",
    f"Training observations: {len(df)}",
    f"Target: {TARGET}",
    "",
    "SELECTED FEATURES",
    "-" * 70,
]

for feature in FEATURES:
    report_lines.append(f"- {feature}")

report_lines.extend(
    [
        "",
        "RANDOM FOREST SETTINGS",
        "-" * 70,
        f"Number of trees: {RANDOM_FOREST_SETTINGS['n_estimators']}",
        f"Random state: {RANDOM_FOREST_SETTINGS['random_state']}",
        f"Maximum depth: {RANDOM_FOREST_SETTINGS['max_depth']}",
        (
            "Minimum samples per leaf: "
            f"{RANDOM_FOREST_SETTINGS['min_samples_leaf']}"
        ),
        "",
        "FEATURE IMPORTANCE",
        "-" * 70,
    ]
)

for feature, importance in feature_importance.items():
    report_lines.append(
        f"{feature}: {importance:.6f}"
    )

report_lines.extend(
    [
        "",
        "TRAINING-DATA ERROR INFORMATION",
        "-" * 70,
        f"Mean absolute error: {mean_training_error:.4f} days",
        f"Maximum absolute error: {max_training_error:.4f} days",
        "",
        "IMPORTANT INTERPRETATION",
        "-" * 70,
        (
            "The training-data errors above are descriptive only "
            "and must not be treated as independent validation "
            "performance."
        ),
        (
            "The model was selected using four-fold GroupKFold "
            "experiments. The selected Weight Loss + Titratable "
            "Acidity feature set produced a mean MAE of 0.7422 days "
            "during that validation experiment."
        ),
        (
            "The final model is retrained on all 48 available "
            "research observations for prototype use."
        ),
        (
            "The model is a research prototype and requires "
            "independent external agricultural data for real-world "
            "validation."
        ),
        "",
        "FILES",
        "-" * 70,
        f"Model: {MODEL_FILE}",
        f"Metadata: {METADATA_FILE}",
        f"Training predictions: {PREDICTION_FILE}",
        "",
        "=" * 70,
        "FINAL RESEARCH MODEL TRAINING COMPLETED",
        "=" * 70,
    ]
)

with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as file:
    file.write("\n".join(report_lines))

print(
    f"\nFinal report saved:\n"
    f"{REPORT_FILE}"
)


# ============================================================
# FINAL MESSAGE
# ============================================================

print("\n" + "=" * 70)
print("FINAL RESEARCH MODEL TRAINING COMPLETED SUCCESSFULLY")
print("=" * 70)