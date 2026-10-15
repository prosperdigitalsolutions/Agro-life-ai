"""
AGRO LIFE-AI
Controlled Comparison of Research Feature Sets

Purpose:
Compare three feature sets using the SAME
Random Forest + GroupKFold validation procedure.

Feature Set A:
    Treatment only

Feature Set B:
    Day-4 quality measurements only

Feature Set C:
    Treatment + Day-4 quality measurements

Important:
- GroupKFold prevents the three replicates of the same
  treatment combination from being split across train/test.
- This is a research experiment, not a production model.
"""

from pathlib import Path

import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


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

RESULTS_DIR = PROJECT_ROOT / "results" / "reports"
PREDICTIONS_DIR = PROJECT_ROOT / "results" / "predictions"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. LOAD DATA
# ============================================================

print("=" * 70)
print("AGRO LIFE-AI")
print("CONTROLLED RESEARCH FEATURE-SET COMPARISON")
print("=" * 70)

print("\nLoading research feature dataset...")

df = pd.read_csv(DATA_FILE)

print(f"Dataset: {DATA_FILE}")
print(f"Records: {len(df)}")
print(f"Columns: {len(df.columns)}")


# ============================================================
# 3. DEFINE TARGET AND GROUP
# ============================================================

TARGET = "shelf_life_days"
GROUP = "group"


# ============================================================
# 4. DEFINE FEATURE SETS
# ============================================================

FEATURE_SETS = {
    "A_Treatment_Only": [
        "neem_extract_percent",
        "beeswax_coating_percent",
    ],

    "B_Day4_Quality_Only": [
        "aa_day4",
        "ph_day4",
        "ta_day4",
        "tss_day4",
        "weight_loss_day4",
    ],

    "C_Treatment_and_Day4_Quality": [
        "neem_extract_percent",
        "beeswax_coating_percent",
        "aa_day4",
        "ph_day4",
        "ta_day4",
        "tss_day4",
        "weight_loss_day4",
    ],
}


# ============================================================
# 5. CHECK REQUIRED COLUMNS
# ============================================================

print("\nChecking required columns...")

required_columns = set([TARGET, GROUP])

for feature_list in FEATURE_SETS.values():
    required_columns.update(feature_list)

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

print("All required columns are present.")


# ============================================================
# 6. BASIC DATA CHECKS
# ============================================================

print("\nChecking missing values...")

analysis_columns = list(required_columns)

missing_values = df[analysis_columns].isnull().sum()

if missing_values.sum() > 0:
    print("\nMissing values detected:")
    print(missing_values[missing_values > 0])
    raise ValueError("Dataset contains missing values.")

print("No missing values detected.")


print("\nChecking treatment groups...")

group_counts = df.groupby(GROUP).size()

print(f"Unique treatment groups: {group_counts.shape[0]}")
print("Observations per group:")
print(group_counts.value_counts().sort_index())

if not all(group_counts == 3):
    print(
        "\nWARNING: Not every treatment group contains exactly "
        "three observations."
    )
else:
    print(
        "Each treatment group contains exactly three "
        "replicated observations."
    )


# ============================================================
# 7. MODEL SETTINGS
# ============================================================

N_SPLITS = 4

RANDOM_STATE = 42

MODEL_PARAMETERS = {
    "n_estimators": 200,
    "random_state": RANDOM_STATE,
    "max_depth": 4,
    "min_samples_leaf": 2,
}


# ============================================================
# 8. GROUP K-FOLD
# ============================================================

groups = df[GROUP]

group_kfold = GroupKFold(n_splits=N_SPLITS)


# ============================================================
# 9. STORAGE FOR RESULTS
# ============================================================

summary_results = []
fold_results = []
prediction_results = []


# ============================================================
# 10. RUN CONTROLLED EXPERIMENTS
# ============================================================

for experiment_name, features in FEATURE_SETS.items():

    print("\n")
    print("=" * 70)
    print(f"EXPERIMENT: {experiment_name}")
    print("=" * 70)

    print("\nFeatures used:")

    for feature in features:
        print(f"  - {feature}")

    X = df[features]
    y = df[TARGET]

    experiment_fold_mae = []
    experiment_fold_rmse = []
    experiment_fold_r2 = []

    fold_number = 0

    for train_index, test_index in group_kfold.split(
        X,
        y,
        groups
    ):

        fold_number += 1

        X_train = X.iloc[train_index]
        X_test = X.iloc[test_index]

        y_train = y.iloc[train_index]
        y_test = y.iloc[test_index]

        train_groups = set(
            df.iloc[train_index][GROUP]
        )

        test_groups = set(
            df.iloc[test_index][GROUP]
        )

        overlap = train_groups.intersection(test_groups)

        if overlap:
            raise RuntimeError(
                f"Group leakage detected in Fold {fold_number}: "
                f"{overlap}"
            )

        model = RandomForestRegressor(
            **MODEL_PARAMETERS
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

        experiment_fold_mae.append(mae)
        experiment_fold_rmse.append(rmse)
        experiment_fold_r2.append(r2)

        print(
            f"\nFold {fold_number}:"
        )

        print(
            f"  Train groups: {len(train_groups)}"
        )

        print(
            f"  Test groups : {len(test_groups)}"
        )

        print(
            f"  Group overlap: {len(overlap)}"
        )

        print(
            f"  MAE  = {mae:.4f} days"
        )

        print(
            f"  RMSE = {rmse:.4f} days"
        )

        print(
            f"  R²   = {r2:.4f}"
        )

        # Store fold-level result
        fold_results.append(
            {
                "experiment": experiment_name,
                "fold": fold_number,
                "train_groups": len(train_groups),
                "test_groups": len(test_groups),
                "group_overlap": len(overlap),
                "mae": mae,
                "rmse": rmse,
                "r2": r2,
            }
        )

        # Store predictions
        for row_position, actual, predicted in zip(
            test_index,
            y_test,
            predictions
        ):

            prediction_results.append(
                {
                    "experiment": experiment_name,
                    "fold": fold_number,
                    "group": df.iloc[row_position][GROUP],
                    "rep": df.iloc[row_position]["rep"],
                    "actual_shelf_life_days": actual,
                    "predicted_shelf_life_days": predicted,
                    "absolute_error_days": abs(
                        actual - predicted
                    ),
                    "signed_error_days": (
                        predicted - actual
                    ),
                }
            )

    # ========================================================
    # 11. CALCULATE SUMMARY STATISTICS
    # ========================================================

    mean_mae = np.mean(experiment_fold_mae)
    std_mae = np.std(
        experiment_fold_mae,
        ddof=1
    )

    mean_rmse = np.mean(experiment_fold_rmse)
    std_rmse = np.std(
        experiment_fold_rmse,
        ddof=1
    )

    mean_r2 = np.mean(experiment_fold_r2)
    std_r2 = np.std(
        experiment_fold_r2,
        ddof=1
    )

    summary_results.append(
        {
            "experiment": experiment_name,
            "features": ", ".join(features),
            "mean_mae_days": mean_mae,
            "std_mae_days": std_mae,
            "mean_rmse_days": mean_rmse,
            "std_rmse_days": std_rmse,
            "mean_r2": mean_r2,
            "std_r2": std_r2,
            "min_fold_mae_days": min(
                experiment_fold_mae
            ),
            "max_fold_mae_days": max(
                experiment_fold_mae
            ),
            "min_fold_r2": min(
                experiment_fold_r2
            ),
            "max_fold_r2": max(
                experiment_fold_r2
            ),
        }
    )

    print("\nMean performance:")

    print(
        f"  MAE  = {mean_mae:.4f} "
        f"+/- {std_mae:.4f} days"
    )

    print(
        f"  RMSE = {mean_rmse:.4f} "
        f"+/- {std_rmse:.4f} days"
    )

    print(
        f"  R²   = {mean_r2:.4f} "
        f"+/- {std_r2:.4f}"
    )


# ============================================================
# 12. SAVE RESULTS
# ============================================================

summary_df = pd.DataFrame(summary_results)

fold_df = pd.DataFrame(fold_results)

predictions_df = pd.DataFrame(
    prediction_results
)


summary_file = (
    RESULTS_DIR
    / "research_feature_set_comparison.csv"
)

fold_file = (
    RESULTS_DIR
    / "research_feature_set_fold_results.csv"
)

predictions_file = (
    PREDICTIONS_DIR
    / "research_feature_set_predictions.csv"
)


summary_df.to_csv(
    summary_file,
    index=False
)

fold_df.to_csv(
    fold_file,
    index=False
)

predictions_df.to_csv(
    predictions_file,
    index=False
)


# ============================================================
# 13. CREATE TEXT REPORT
# ============================================================

report_file = (
    RESULTS_DIR
    / "research_feature_set_comparison_report.txt"
)


with open(
    report_file,
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "AGRO LIFE-AI\n"
    )

    report.write(
        "CONTROLLED RESEARCH FEATURE-SET COMPARISON\n"
    )

    report.write(
        "=" * 70 + "\n\n"
    )

    report.write(
        "Purpose\n"
    )

    report.write(
        "-------\n"
    )

    report.write(
        "This experiment compares three feature sets using the "
        "same Random Forest algorithm and the same four-fold "
        "GroupKFold validation procedure.\n\n"
    )

    report.write(
        "GroupKFold was used so that observations belonging to "
        "the same treatment combination are not split between "
        "training and testing data.\n\n"
    )

    report.write(
        "Dataset\n"
    )

    report.write(
        "-------\n"
    )

    report.write(
        f"Records: {len(df)}\n"
    )

    report.write(
        f"Treatment groups: {df[GROUP].nunique()}\n"
    )

    report.write(
        f"Validation folds: {N_SPLITS}\n\n"
    )

    report.write(
        "Feature sets\n"
    )

    report.write(
        "------------\n"
    )

    for name, features in FEATURE_SETS.items():

        report.write(
            f"{name}:\n"
        )

        for feature in features:

            report.write(
                f"  - {feature}\n"
            )

        report.write("\n")

    report.write(
        "Random Forest settings\n"
    )

    report.write(
        "----------------------\n"
    )

    for parameter, value in MODEL_PARAMETERS.items():

        report.write(
            f"{parameter}: {value}\n"
        )

    report.write("\n")

    report.write(
        "Summary results\n"
    )

    report.write(
        "---------------\n"
    )

    report.write(
        summary_df.to_string(
            index=False
        )
    )

    report.write("\n\n")

    report.write(
        "Interpretation guidance\n"
    )

    report.write(
        "-----------------------\n"
    )

    report.write(
        "Lower MAE and RMSE indicate smaller prediction errors.\n"
    )

    report.write(
        "Higher R² indicates greater explained variance, but "
        "negative R² values can occur when predictions perform "
        "worse than a simple mean-based reference.\n"
    )

    report.write(
        "Standard deviation across folds indicates how much "
        "performance varies between unseen treatment groups.\n"
    )

    report.write(
        "Because the dataset contains only 48 observations and "
        "a narrow shelf-life range, results should be treated "
        "as experimental evidence rather than production-level "
        "validation.\n"
    )


# ============================================================
# 14. FINAL CONSOLE SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("FINAL FEATURE-SET COMPARISON")
print("=" * 70)

display_columns = [
    "experiment",
    "mean_mae_days",
    "std_mae_days",
    "mean_rmse_days",
    "std_rmse_days",
    "mean_r2",
    "std_r2",
]

print(
    summary_df[display_columns].to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


print("\nFiles saved:")

print(
    f"1. {summary_file}"
)

print(
    f"2. {fold_file}"
)

print(
    f"3. {predictions_file}"
)

print(
    f"4. {report_file}"
)


print("\n")
print("=" * 70)
print("FEATURE-SET COMPARISON COMPLETED SUCCESSFULLY")
print("=" * 70)