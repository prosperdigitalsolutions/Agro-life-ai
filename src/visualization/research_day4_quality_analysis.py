"""
AGRO LIFE-AI
Day-4 Quality Feature Analysis

Purpose:
Analyse the individual contribution of Day-4 quality variables
to tomato shelf-life prediction.

Features:
1. Ascorbic Acid (Day 4)
2. pH (Day 4)
3. Titratable Acidity (Day 4)
4. Total Soluble Solids (Day 4)
5. Weight Loss (Day 4)

The analysis includes:
- Correlation with shelf life
- Individual-feature Random Forest experiments
- Combined Day-4 quality model
- GroupKFold validation
- Feature importance
- Error comparison
- Results saved to reports and figures

Important:
This is an experimental research analysis based on the
48-observation research dataset. Results are not production
validation.
"""

from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


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

REPORTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "reports"
)

FIGURES_DIR = (
    PROJECT_ROOT
    / "results"
    / "figures"
)

REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

FIGURES_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. LOAD DATA
# ============================================================

print("=" * 70)
print("AGRO LIFE-AI")
print("DAY-4 QUALITY FEATURE ANALYSIS")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(DATA_FILE)

print(
    f"Records: {len(df)}"
)

print(
    f"Columns: {len(df.columns)}"
)


# ============================================================
# 3. DEFINE TARGET AND GROUP
# ============================================================

TARGET = "shelf_life_days"
GROUP = "group"


# ============================================================
# 4. DEFINE DAY-4 FEATURES
# ============================================================

FEATURES = [
    "aa_day4",
    "ph_day4",
    "ta_day4",
    "tss_day4",
    "weight_loss_day4",
]


FEATURE_LABELS = {
    "aa_day4": "Ascorbic Acid - Day 4",
    "ph_day4": "pH - Day 4",
    "ta_day4": "Titratable Acidity - Day 4",
    "tss_day4": "Total Soluble Solids - Day 4",
    "weight_loss_day4": "Weight Loss - Day 4",
}


# ============================================================
# 5. CHECK DATA
# ============================================================

required_columns = (
    FEATURES
    + [TARGET, GROUP]
)

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    raise ValueError(
        f"Missing columns: {missing_columns}"
    )


if df[required_columns].isnull().sum().sum() > 0:

    raise ValueError(
        "Missing values detected."
    )


print(
    "\nData validation completed successfully."
)


# ============================================================
# 6. CORRELATION ANALYSIS
# ============================================================

print("\n")
print("=" * 70)
print("CORRELATION WITH SHELF LIFE")
print("=" * 70)

correlation_rows = []

for feature in FEATURES:

    correlation = df[
        feature
    ].corr(
        df[TARGET]
    )

    correlation_rows.append(
        {
            "feature": feature,
            "feature_label": FEATURE_LABELS[feature],
            "correlation_with_shelf_life": correlation,
            "absolute_correlation": abs(correlation),
        }
    )

    print(
        f"{FEATURE_LABELS[feature]:35s} "
        f"{correlation:+.6f}"
    )


correlation_df = pd.DataFrame(
    correlation_rows
)

correlation_df = correlation_df.sort_values(
    "absolute_correlation",
    ascending=False
)


correlation_file = (
    REPORTS_DIR
    / "research_day4_quality_correlations.csv"
)

correlation_df.to_csv(
    correlation_file,
    index=False
)


# ============================================================
# 7. CORRELATION BAR CHART
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plot_df = correlation_df.sort_values(
    "correlation_with_shelf_life"
)

plt.barh(
    plot_df["feature_label"],
    plot_df["correlation_with_shelf_life"]
)

plt.axvline(
    0,
    linewidth=1
)

plt.xlabel(
    "Correlation with Shelf Life"
)

plt.ylabel(
    "Day-4 Quality Feature"
)

plt.title(
    "Correlation of Day-4 Quality Features with Tomato Shelf Life"
)

plt.tight_layout()

correlation_figure = (
    FIGURES_DIR
    / "research_day4_quality_correlations.png"
)

plt.savefig(
    correlation_figure,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 8. RANDOM FOREST SETTINGS
# ============================================================

MODEL_PARAMETERS = {
    "n_estimators": 200,
    "random_state": 42,
    "max_depth": 4,
    "min_samples_leaf": 2,
}


N_SPLITS = 4


# ============================================================
# 9. GROUP KFOLD
# ============================================================

group_kfold = GroupKFold(
    n_splits=N_SPLITS
)

groups = df[GROUP]

y = df[TARGET]


# ============================================================
# 10. INDIVIDUAL FEATURE EXPERIMENTS
# ============================================================

print("\n")
print("=" * 70)
print("INDIVIDUAL DAY-4 FEATURE EXPERIMENTS")
print("=" * 70)


individual_results = []

individual_predictions = []


for feature in FEATURES:

    print("\n")
    print("-" * 70)

    print(
        f"Feature: {FEATURE_LABELS[feature]}"
    )

    print("-" * 70)

    X = df[
        [feature]
    ]

    fold_mae = []
    fold_rmse = []
    fold_r2 = []

    for fold, (
        train_index,
        test_index
    ) in enumerate(
        group_kfold.split(
            X,
            y,
            groups
        ),
        start=1
    ):

        X_train = X.iloc[
            train_index
        ]

        X_test = X.iloc[
            test_index
        ]

        y_train = y.iloc[
            train_index
        ]

        y_test = y.iloc[
            test_index
        ]

        train_groups = set(
            df.iloc[
                train_index
            ][GROUP]
        )

        test_groups = set(
            df.iloc[
                test_index
            ][GROUP]
        )

        overlap = (
            train_groups
            .intersection(
                test_groups
            )
        )

        if overlap:

            raise RuntimeError(
                f"Group leakage detected: {overlap}"
            )

        model = RandomForestRegressor(
            **MODEL_PARAMETERS
        )

        model.fit(
            X_train,
            y_train
        )

        predictions = model.predict(
            X_test
        )

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

        fold_mae.append(mae)
        fold_rmse.append(rmse)
        fold_r2.append(r2)

        print(
            f"Fold {fold}: "
            f"MAE={mae:.4f}, "
            f"RMSE={rmse:.4f}, "
            f"R²={r2:.4f}"
        )

        for position, actual, predicted in zip(
            test_index,
            y_test,
            predictions
        ):

            individual_predictions.append(
                {
                    "feature": feature,
                    "feature_label": FEATURE_LABELS[feature],
                    "fold": fold,
                    "group": df.iloc[position][GROUP],
                    "rep": df.iloc[position]["rep"],
                    "actual_shelf_life_days": actual,
                    "predicted_shelf_life_days": predicted,
                    "absolute_error_days": abs(
                        actual - predicted
                    ),
                }
            )


    individual_results.append(
        {
            "feature": feature,
            "feature_label": FEATURE_LABELS[feature],
            "mean_mae_days": np.mean(
                fold_mae
            ),
            "std_mae_days": np.std(
                fold_mae,
                ddof=1
            ),
            "mean_rmse_days": np.mean(
                fold_rmse
            ),
            "std_rmse_days": np.std(
                fold_rmse,
                ddof=1
            ),
            "mean_r2": np.mean(
                fold_r2
            ),
            "std_r2": np.std(
                fold_r2,
                ddof=1
            ),
        }
    )


individual_results_df = pd.DataFrame(
    individual_results
)

individual_results_df = (
    individual_results_df.sort_values(
        "mean_mae_days"
    )
)


individual_results_file = (
    REPORTS_DIR
    / "research_day4_individual_feature_results.csv"
)

individual_results_df.to_csv(
    individual_results_file,
    index=False
)


individual_predictions_df = pd.DataFrame(
    individual_predictions
)

individual_predictions_file = (
    REPORTS_DIR
    / "research_day4_individual_feature_predictions.csv"
)

individual_predictions_df.to_csv(
    individual_predictions_file,
    index=False
)


# ============================================================
# 11. COMBINED DAY-4 QUALITY MODEL
# ============================================================

print("\n")
print("=" * 70)
print("COMBINED DAY-4 QUALITY MODEL")
print("=" * 70)


X = df[
    FEATURES
]

combined_fold_mae = []
combined_fold_rmse = []
combined_fold_r2 = []

combined_predictions = []


for fold, (
    train_index,
    test_index
) in enumerate(
    group_kfold.split(
        X,
        y,
        groups
    ),
    start=1
):

    X_train = X.iloc[
        train_index
    ]

    X_test = X.iloc[
        test_index
    ]

    y_train = y.iloc[
        train_index
    ]

    y_test = y.iloc[
        test_index
    ]

    train_groups = set(
        df.iloc[
            train_index
        ][GROUP]
    )

    test_groups = set(
        df.iloc[
            test_index
        ][GROUP]
    )

    overlap = (
        train_groups
        .intersection(
            test_groups
        )
    )

    if overlap:

        raise RuntimeError(
            f"Group leakage detected: {overlap}"
        )

    model = RandomForestRegressor(
        **MODEL_PARAMETERS
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

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

    combined_fold_mae.append(
        mae
    )

    combined_fold_rmse.append(
        rmse
    )

    combined_fold_r2.append(
        r2
    )

    print(
        f"Fold {fold}: "
        f"MAE={mae:.4f}, "
        f"RMSE={rmse:.4f}, "
        f"R²={r2:.4f}"
    )

    for position, actual, predicted in zip(
        test_index,
        y_test,
        predictions
    ):

        combined_predictions.append(
            {
                "fold": fold,
                "group": df.iloc[position][GROUP],
                "rep": df.iloc[position]["rep"],
                "actual_shelf_life_days": actual,
                "predicted_shelf_life_days": predicted,
                "absolute_error_days": abs(
                    actual - predicted
                ),
            }
        )


combined_result = {
    "feature_set": "All Day-4 Quality Features",
    "mean_mae_days": np.mean(
        combined_fold_mae
    ),
    "std_mae_days": np.std(
        combined_fold_mae,
        ddof=1
    ),
    "mean_rmse_days": np.mean(
        combined_fold_rmse
    ),
    "std_rmse_days": np.std(
        combined_fold_rmse,
        ddof=1
    ),
    "mean_r2": np.mean(
        combined_fold_r2
    ),
    "std_r2": np.std(
        combined_fold_r2,
        ddof=1
    ),
}


combined_predictions_df = pd.DataFrame(
    combined_predictions
)

combined_predictions_file = (
    REPORTS_DIR
    / "research_day4_quality_combined_predictions.csv"
)

combined_predictions_df.to_csv(
    combined_predictions_file,
    index=False
)


# ============================================================
# 12. FIT FINAL INTERPRETATION MODEL
# ============================================================

print("\n")
print("=" * 70)
print("FEATURE IMPORTANCE")
print("=" * 70)


interpretation_model = RandomForestRegressor(
    **MODEL_PARAMETERS
)

interpretation_model.fit(
    X,
    y
)


importance_df = pd.DataFrame(
    {
        "feature": FEATURES,
        "feature_label": [
            FEATURE_LABELS[f]
            for f in FEATURES
        ],
        "importance": (
            interpretation_model
            .feature_importances_
        ),
    }
)


importance_df = importance_df.sort_values(
    "importance",
    ascending=False
)


print(
    importance_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.6f}"
    )
)


importance_file = (
    REPORTS_DIR
    / "research_day4_quality_feature_importance.csv"
)

importance_df.to_csv(
    importance_file,
    index=False
)


# ============================================================
# 13. FEATURE IMPORTANCE FIGURE
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.barh(
    importance_df["feature_label"],
    importance_df["importance"]
)

plt.xlabel(
    "Random Forest Feature Importance"
)

plt.ylabel(
    "Day-4 Quality Feature"
)

plt.title(
    "Random Forest Importance of Day-4 Quality Features"
)

plt.gca().invert_yaxis()

plt.tight_layout()

importance_figure = (
    FIGURES_DIR
    / "research_day4_quality_feature_importance.png"
)

plt.savefig(
    importance_figure,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 14. INDIVIDUAL FEATURE PERFORMANCE FIGURE
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plot_results = (
    individual_results_df
    .sort_values(
        "mean_mae_days",
        ascending=True
    )
)

plt.barh(
    plot_results["feature_label"],
    plot_results["mean_mae_days"]
)

plt.xlabel(
    "Mean MAE (days)"
)

plt.ylabel(
    "Day-4 Quality Feature"
)

plt.title(
    "Individual Day-4 Feature Prediction Error"
)

plt.tight_layout()

performance_figure = (
    FIGURES_DIR
    / "research_day4_individual_feature_mae.png"
)

plt.savefig(
    performance_figure,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 15. WRITE FINAL TEXT REPORT
# ============================================================

report_file = (
    REPORTS_DIR
    / "research_day4_quality_analysis_report.txt"
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
        "DAY-4 QUALITY FEATURE ANALYSIS\n"
    )

    report.write(
        "=" * 70 + "\n\n"
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
        "Validation: 4-fold GroupKFold\n"
    )

    report.write(
        "Model: Random Forest Regressor\n\n"
    )

    report.write(
        "Correlation analysis\n"
    )

    report.write(
        "---------------------\n"
    )

    report.write(
        correlation_df.to_string(
            index=False
        )
    )

    report.write(
        "\n\n"
    )

    report.write(
        "Individual feature model results\n"
    )

    report.write(
        "--------------------------------\n"
    )

    report.write(
        individual_results_df.to_string(
            index=False
        )
    )

    report.write(
        "\n\n"
    )

    report.write(
        "Combined Day-4 quality model\n"
    )

    report.write(
        "----------------------------\n"
    )

    for key, value in combined_result.items():

        report.write(
            f"{key}: {value}\n"
        )

    report.write(
        "\n\n"
    )

    report.write(
        "Random Forest feature importance\n"
    )

    report.write(
        "--------------------------------\n"
    )

    report.write(
        importance_df.to_string(
            index=False
        )
    )

    report.write(
        "\n\n"
    )

    report.write(
        "Methodological interpretation\n"
    )

    report.write(
        "-----------------------------\n"
    )

    report.write(
        "The analysis examines whether individual Day-4 quality "
        "measurements contain useful information for predicting "
        "tomato shelf life.\n\n"
    )

    report.write(
        "Correlation values describe linear association and "
        "do not establish causation.\n\n"
    )

    report.write(
        "Random Forest feature importance indicates how strongly "
        "the fitted model used each feature within this dataset. "
        "It does not establish biological causation or universal "
        "importance.\n\n"
    )

    report.write(
        "The dataset contains 48 observations from 16 treatment "
        "groups. Therefore, the results should be interpreted "
        "as evidence from a small experimental dataset rather "
        "than as a universally validated prediction system.\n\n"
    )

    report.write(
        "GroupKFold was used to reduce optimistic estimates "
        "caused by placing observations from the same treatment "
        "combination in both training and testing folds.\n"
    )


# ============================================================
# 16. FINAL CONSOLE OUTPUT
# ============================================================

print("\n")
print("=" * 70)
print("INDIVIDUAL FEATURE RESULTS")
print("=" * 70)

print(
    individual_results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


print("\n")
print("=" * 70)
print("COMBINED DAY-4 QUALITY MODEL")
print("=" * 70)

print(
    f"Mean MAE : "
    f"{combined_result['mean_mae_days']:.4f} days"
)

print(
    f"MAE Std  : "
    f"{combined_result['std_mae_days']:.4f}"
)

print(
    f"Mean RMSE: "
    f"{combined_result['mean_rmse_days']:.4f} days"
)

print(
    f"RMSE Std : "
    f"{combined_result['std_rmse_days']:.4f}"
)

print(
    f"Mean R²  : "
    f"{combined_result['mean_r2']:.4f}"
)

print(
    f"R² Std   : "
    f"{combined_result['std_r2']:.4f}"
)


print("\n")
print("=" * 70)
print("FEATURE IMPORTANCE")
print("=" * 70)

print(
    importance_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.6f}"
    )
)


print("\n")
print("=" * 70)
print("FILES SAVED")
print("=" * 70)

print(
    f"1. {correlation_file}"
)

print(
    f"2. {individual_results_file}"
)

print(
    f"3. {individual_predictions_file}"
)

print(
    f"4. {combined_predictions_file}"
)

print(
    f"5. {importance_file}"
)

print(
    f"6. {correlation_figure}"
)

print(
    f"7. {importance_figure}"
)

print(
    f"8. {performance_figure}"
)

print(
    f"9. {report_file}"
)


print("\n")
print("=" * 70)
print("DAY-4 QUALITY ANALYSIS COMPLETED SUCCESSFULLY")
print("=" * 70)