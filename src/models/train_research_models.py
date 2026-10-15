"""
AGRO LIFE-AI
Research Model Training - Group-Aware Validation

Purpose:
    Train and compare two shelf-life prediction models using
    the verified tomato research dataset.

Models:
    1. Treatment Baseline
    2. Day-4 Early Quality Model

Validation:
    GroupKFold

Why GroupKFold?
    Each treatment combination has 3 replications.
    Replications from the same treatment group must not be
    split between training and validation folds.

Target:
    shelf_life_days

IMPORTANT:
    These results are based on the selected research dataset.
    They should not be interpreted as universal predictions
    for all tomato varieties, storage conditions, or locations.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold


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

MODEL_DIR = PROJECT_ROOT / "models"

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "reports"
)

PREDICTIONS_DIR = (
    PROJECT_ROOT
    / "results"
    / "predictions"
)


# ============================================================
# 2. CREATE OUTPUT DIRECTORIES
# ============================================================

MODEL_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 3. LOAD DATA
# ============================================================

print("=" * 75)
print("AGRO LIFE-AI - RESEARCH MODEL TRAINING")
print("=" * 75)

print("\nLoading Day-4 research feature dataset...")
print(f"Input: {DATA_FILE}")

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"\nDataset not found:\n{DATA_FILE}\n"
        "Please run build_prediction_features.py first."
    )

df = pd.read_csv(DATA_FILE)

print(f"Records loaded: {len(df)}")
print(f"Columns loaded: {len(df.columns)}")


# ============================================================
# 4. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "group",
    "rep",
    "neem_extract_percent",
    "beeswax_coating_percent",
    "aa_day4",
    "ph_day4",
    "ta_day4",
    "tss_day4",
    "weight_loss_day4",
    "shelf_life_days",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "\nMissing required columns:\n"
        + "\n".join(f"- {column}" for column in missing_columns)
    )

print("Required columns verified.")


# ============================================================
# 5. DEFINE TARGET AND FEATURES
# ============================================================

TARGET = "shelf_life_days"

# ------------------------------------------------------------
# MODEL 1
# Treatment-only baseline
# ------------------------------------------------------------

baseline_features = [
    "neem_extract_percent",
    "beeswax_coating_percent",
]

# ------------------------------------------------------------
# MODEL 2
# Treatment + Day-4 quality measurements
# ------------------------------------------------------------

early_quality_features = [
    "neem_extract_percent",
    "beeswax_coating_percent",
    "aa_day4",
    "ph_day4",
    "ta_day4",
    "tss_day4",
    "weight_loss_day4",
]


# ============================================================
# 6. PREPARE TARGET AND GROUPS
# ============================================================

y = df[TARGET]

groups = df["group"]


# ============================================================
# 7. GROUP VALIDATION CHECK
# ============================================================

unique_groups = groups.nunique()

print("\nValidation structure:")
print(f"Unique treatment groups: {unique_groups}")
print(f"Replications per group:")
print(groups.value_counts().value_counts().to_dict())

if unique_groups != 16:
    raise ValueError(
        f"Expected 16 treatment groups, found {unique_groups}."
    )

if not all(groups.value_counts() == 3):
    raise ValueError(
        "Each treatment group must contain exactly 3 replications."
    )

print("Group structure verified.")


# ============================================================
# 8. GROUP K-FOLD
# ============================================================

N_SPLITS = 4

group_kfold = GroupKFold(
    n_splits=N_SPLITS
)


# ============================================================
# 9. MODEL DEFINITIONS
# ============================================================

models = {
    "Linear Regression": LinearRegression(),

    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        max_depth=4,
        min_samples_leaf=2,
    ),
}


# ============================================================
# 10. TRAIN AND EVALUATE FUNCTION
# ============================================================

def evaluate_model(
    model_name,
    model,
    feature_columns,
):
    """
    Train and evaluate a model using GroupKFold.

    Returns:
        metrics dictionary
        prediction DataFrame
    """

    print("\n" + "-" * 75)
    print(f"MODEL: {model_name}")
    print(f"FEATURE SET: {feature_columns}")
    print("-" * 75)

    X = df[feature_columns]

    fold_results = []
    all_predictions = []

    for fold_number, (train_index, test_index) in enumerate(
        group_kfold.split(X, y, groups),
        start=1,
    ):

        X_train = X.iloc[train_index]
        X_test = X.iloc[test_index]

        y_train = y.iloc[train_index]
        y_test = y.iloc[test_index]

        train_groups = set(
            groups.iloc[train_index]
        )

        test_groups = set(
            groups.iloc[test_index]
        )

        overlap = train_groups.intersection(test_groups)

        if overlap:
            raise ValueError(
                f"Group leakage detected in fold {fold_number}: "
                f"{overlap}"
            )

        print(
            f"\nFold {fold_number}: "
            f"Train={len(train_index)}, "
            f"Validation={len(test_index)}, "
            f"Groups={len(test_groups)}"
        )

        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        mae = mean_absolute_error(
            y_test,
            predictions
        )

        rmse = np.sqrt(
            mean_squared_error(
                y_test,
                predictions
            )
        )

        r2 = r2_score(
            y_test,
            predictions
        )

        fold_results.append(
            {
                "fold": fold_number,
                "MAE_days": mae,
                "RMSE_days": rmse,
                "R2": r2,
            }
        )

        for index, actual, predicted in zip(
            test_index,
            y_test,
            predictions,
        ):
            all_predictions.append(
                {
                    "model": model_name,
                    "feature_set": (
                        "Treatment Baseline"
                        if len(feature_columns) == 2
                        else "Day-4 Early Quality"
                    ),
                    "fold": fold_number,
                    "group": df.loc[index, "group"],
                    "rep": df.loc[index, "rep"],
                    "actual_shelf_life": actual,
                    "predicted_shelf_life": predicted,
                    "absolute_error": abs(
                        actual - predicted
                    ),
                }
            )

        print(
            f"  MAE  : {mae:.4f} days"
        )
        print(
            f"  RMSE : {rmse:.4f} days"
        )
        print(
            f"  R²   : {r2:.4f}"
        )

    # --------------------------------------------------------
    # Average cross-validation results
    # --------------------------------------------------------

    fold_df = pd.DataFrame(fold_results)

    mean_mae = fold_df["MAE_days"].mean()
    std_mae = fold_df["MAE_days"].std()

    mean_rmse = fold_df["RMSE_days"].mean()
    std_rmse = fold_df["RMSE_days"].std()

    mean_r2 = fold_df["R2"].mean()
    std_r2 = fold_df["R2"].std()

    print("\nCross-validation summary:")
    print(
        f"Mean MAE  : {mean_mae:.4f} "
        f"+/- {std_mae:.4f} days"
    )

    print(
        f"Mean RMSE : {mean_rmse:.4f} "
        f"+/- {std_rmse:.4f} days"
    )

    print(
        f"Mean R²   : {mean_r2:.4f} "
        f"+/- {std_r2:.4f}"
    )

    metrics = {
        "model": model_name,
        "feature_set": (
            "Treatment Baseline"
            if len(feature_columns) == 2
            else "Day-4 Early Quality"
        ),
        "mean_MAE_days": mean_mae,
        "std_MAE_days": std_mae,
        "mean_RMSE_days": mean_rmse,
        "std_RMSE_days": std_rmse,
        "mean_R2": mean_r2,
        "std_R2": std_r2,
    }

    predictions_df = pd.DataFrame(
        all_predictions
    )

    return metrics, predictions_df


# ============================================================
# 11. RUN EXPERIMENTS
# ============================================================

all_metrics = []
all_predictions = []


for feature_set_name, feature_columns in [
    (
        "Treatment Baseline",
        baseline_features,
    ),
    (
        "Day-4 Early Quality",
        early_quality_features,
    ),
]:

    for model_name, model in models.items():

        metrics, predictions = evaluate_model(
            model_name,
            model,
            feature_columns,
        )

        all_metrics.append(metrics)
        all_predictions.append(predictions)


# ============================================================
# 12. SAVE MODEL COMPARISON
# ============================================================

metrics_df = pd.DataFrame(
    all_metrics
)

metrics_file = (
    RESULTS_DIR
    / "research_model_comparison.csv"
)

metrics_df.to_csv(
    metrics_file,
    index=False
)


# ============================================================
# 13. SAVE ALL PREDICTIONS
# ============================================================

predictions_df = pd.concat(
    all_predictions,
    ignore_index=True,
)

predictions_file = (
    PREDICTIONS_DIR
    / "research_model_predictions.csv"
)

predictions_df.to_csv(
    predictions_file,
    index=False
)


# ============================================================
# 14. TRAIN FINAL RESEARCH MODELS ON ALL DATA
# ============================================================

print("\n" + "=" * 75)
print("TRAINING FINAL RESEARCH MODELS")
print("=" * 75)

final_model_paths = []

for feature_set_name, feature_columns in [
    (
        "Treatment Baseline",
        baseline_features,
    ),
    (
        "Day-4 Early Quality",
        early_quality_features,
    ),
]:

    for model_name, model in models.items():

        print(
            f"\nTraining final model: "
            f"{feature_set_name} + {model_name}"
        )

        X = df[feature_columns]

        model.fit(
            X,
            y
        )

        safe_feature_name = (
            "treatment_baseline"
            if feature_set_name
            == "Treatment Baseline"
            else "day4_early_quality"
        )

        safe_model_name = (
            model_name.lower()
            .replace(" ", "_")
        )

        model_path = (
            MODEL_DIR
            / f"research_{safe_feature_name}_{safe_model_name}.joblib"
        )

        joblib.dump(
            model,
            model_path
        )

        final_model_paths.append(
            model_path
        )

        print(
            f"Saved: {model_path}"
        )


# ============================================================
# 15. CREATE TEXT REPORT
# ============================================================

report_file = (
    RESULTS_DIR
    / "research_model_training_report.txt"
)

with open(
    report_file,
    "w",
    encoding="utf-8",
) as report:

    report.write(
        "AGRO LIFE-AI\n"
        "RESEARCH MODEL TRAINING REPORT\n"
        "=" * 70
        + "\n\n"
    )

    report.write(
        "Dataset: Verified tomato shelf-life research dataset\n"
    )

    report.write(
        f"Observations: {len(df)}\n"
    )

    report.write(
        f"Treatment groups: {unique_groups}\n"
    )

    report.write(
        "Replications per treatment group: 3\n"
    )

    report.write(
        "Prediction window: Day 4\n"
    )

    report.write(
        "Validation method: 4-fold GroupKFold\n\n"
    )

    report.write(
        "MODEL COMPARISON\n"
        "-" * 70
        + "\n"
    )

    report.write(
        metrics_df.to_string(
            index=False
        )
    )

    report.write(
        "\n\nMETHODOLOGICAL NOTES\n"
        "-" * 70
        + "\n"
    )

    report.write(
        "1. Treatment groups were used for grouped validation.\n"
    )

    report.write(
        "2. Replications from the same treatment group were "
        "kept within the same validation fold.\n"
    )

    report.write(
        "3. The Treatments label was not used as a predictor.\n"
    )

    report.write(
        "4. The replication number was not used as a predictor.\n"
    )

    report.write(
        "5. Day-4 features were selected because they represent "
        "information available by Day 4.\n"
    )

    report.write(
        "6. The dataset contains 48 observations, so model "
        "complexity was intentionally limited.\n"
    )

    report.write(
        "7. Results describe this research dataset and should "
        "not be treated as universal shelf-life estimates.\n"
    )


# ============================================================
# 16. FINAL OUTPUT
# ============================================================

print("\n" + "=" * 75)
print("RESEARCH MODEL TRAINING COMPLETED")
print("=" * 75)

print("\nModel comparison:")
print(
    metrics_df.to_string(
        index=False
    )
)

print("\nSaved files:")

print(f"\n1. Model comparison:")
print(metrics_file)

print("\n2. Cross-validation predictions:")
print(predictions_file)

print("\n3. Training report:")
print(report_file)

print("\n4. Final trained models:")

for path in final_model_paths:
    print(path)

print("\n" + "=" * 75)
print("IMPORTANT")
print("=" * 75)

print(
    "\nThese models are research prototypes trained on the "
    "selected tomato dataset."
)

print(
    "Their performance must be interpreted using the "
    "GroupKFold results rather than ordinary random-split results."
)

print(
    "\nNext step after reviewing these results:"
)

print(
    "MODEL INTERPRETATION AND FEATURE IMPORTANCE"
)