"""
AGRO LIFE-AI
Day-4 Feature Redundancy and Reduced-Feature Analysis

Purpose:
1. Examine correlations between Day-4 quality variables.
2. Identify potentially redundant predictors.
3. Compare selected reduced feature sets using the same
   Random Forest + GroupKFold validation procedure.

This is an experimental analysis of the 48-observation
research dataset.

Important:
Correlation does not establish causation.
Feature importance does not establish biological causation.
Results are not production-level validation.
"""

from pathlib import Path
from itertools import combinations

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
print("DAY-4 FEATURE REDUNDANCY AND REDUCED-FEATURE ANALYSIS")
print("=" * 70)

print("\nLoading research dataset...")

df = pd.read_csv(DATA_FILE)

print(
    f"Records: {len(df)}"
)

print(
    f"Columns: {len(df.columns)}"
)


# ============================================================
# 3. DEFINE VARIABLES
# ============================================================

TARGET = "shelf_life_days"

GROUP = "group"

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
# 4. DATA VALIDATION
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
        f"Missing required columns: {missing_columns}"
    )


if (
    df[required_columns]
    .isnull()
    .sum()
    .sum()
    > 0
):

    raise ValueError(
        "Missing values detected."
    )


print(
    "\nData validation completed successfully."
)


# ============================================================
# 5. FEATURE-TO-FEATURE CORRELATION
# ============================================================

print("\n")
print("=" * 70)
print("DAY-4 FEATURE-TO-FEATURE CORRELATION")
print("=" * 70)

feature_corr = df[
    FEATURES
].corr()


print(
    feature_corr.to_string(
        float_format=lambda x: f"{x:.4f}"
    )
)


feature_corr_file = (
    REPORTS_DIR
    / "research_day4_feature_correlation_matrix.csv"
)

feature_corr.to_csv(
    feature_corr_file
)


# ============================================================
# 6. PAIRWISE CORRELATION TABLE
# ============================================================

pairwise_rows = []

for feature_a, feature_b in combinations(
    FEATURES,
    2
):

    correlation = (
        df[feature_a]
        .corr(
            df[feature_b]
        )
    )

    pairwise_rows.append(
        {
            "feature_1": feature_a,
            "feature_1_label": FEATURE_LABELS[feature_a],
            "feature_2": feature_b,
            "feature_2_label": FEATURE_LABELS[feature_b],
            "correlation": correlation,
            "absolute_correlation": abs(
                correlation
            ),
        }
    )


pairwise_df = pd.DataFrame(
    pairwise_rows
)

pairwise_df = pairwise_df.sort_values(
    "absolute_correlation",
    ascending=False
)


print("\n")
print("=" * 70)
print("PAIRWISE FEATURE CORRELATIONS")
print("=" * 70)

print(
    pairwise_df[
        [
            "feature_1_label",
            "feature_2_label",
            "correlation",
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


pairwise_file = (
    REPORTS_DIR
    / "research_day4_pairwise_feature_correlations.csv"
)

pairwise_df.to_csv(
    pairwise_file,
    index=False
)


# ============================================================
# 7. CORRELATION HEATMAP
# ============================================================

plt.figure(
    figsize=(9, 7)
)

plt.imshow(
    feature_corr,
    interpolation="nearest"
)

plt.colorbar(
    label="Correlation"
)

plt.xticks(
    range(len(FEATURES)),
    [
        FEATURE_LABELS[f]
        for f in FEATURES
    ],
    rotation=45,
    ha="right"
)

plt.yticks(
    range(len(FEATURES)),
    [
        FEATURE_LABELS[f]
        for f in FEATURES
    ]
)

plt.title(
    "Correlation Matrix of Day-4 Quality Features"
)

plt.tight_layout()

heatmap_file = (
    FIGURES_DIR
    / "research_day4_feature_correlation_heatmap.png"
)

plt.savefig(
    heatmap_file,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 8. DEFINE REDUCED FEATURE SETS
# ============================================================

FEATURE_SETS = {

    "F1_Weight_Loss_Only": [
        "weight_loss_day4"
    ],

    "F2_TA_Only": [
        "ta_day4"
    ],

    "F3_Weight_Loss_and_TA": [
        "weight_loss_day4",
        "ta_day4"
    ],

    "F4_Weight_Loss_TA_pH": [
        "weight_loss_day4",
        "ta_day4",
        "ph_day4"
    ],

    "F5_All_Day4_Quality": [
        "aa_day4",
        "ph_day4",
        "ta_day4",
        "tss_day4",
        "weight_loss_day4"
    ],
}


# ============================================================
# 9. RANDOM FOREST SETTINGS
# ============================================================

MODEL_PARAMETERS = {
    "n_estimators": 200,
    "random_state": 42,
    "max_depth": 4,
    "min_samples_leaf": 2,
}


N_SPLITS = 4

group_kfold = GroupKFold(
    n_splits=N_SPLITS
)

groups = df[GROUP]

y = df[TARGET]


# ============================================================
# 10. RUN REDUCED-FEATURE EXPERIMENTS
# ============================================================

print("\n")
print("=" * 70)
print("REDUCED-FEATURE MODEL COMPARISON")
print("=" * 70)


summary_results = []

fold_results = []

prediction_results = []


for experiment_name, features in FEATURE_SETS.items():

    print("\n")
    print("-" * 70)

    print(
        f"EXPERIMENT: {experiment_name}"
    )

    print(
        "Features:"
    )

    for feature in features:

        print(
            f"  - {FEATURE_LABELS[feature]}"
        )

    print("-" * 70)

    fold_mae = []
    fold_rmse = []
    fold_r2 = []

    for fold, (
        train_index,
        test_index
    ) in enumerate(
        group_kfold.split(
            df[features],
            y,
            groups
        ),
        start=1
    ):

        X_train = df.iloc[
            train_index
        ][features]

        X_test = df.iloc[
            test_index
        ][features]

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
                f"Group leakage detected in "
                f"{experiment_name}, Fold {fold}: "
                f"{overlap}"
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


        fold_mae.append(
            mae
        )

        fold_rmse.append(
            rmse
        )

        fold_r2.append(
            r2
        )


        print(
            f"Fold {fold}: "
            f"MAE={mae:.4f}, "
            f"RMSE={rmse:.4f}, "
            f"R²={r2:.4f}"
        )


        fold_results.append(
            {
                "experiment": experiment_name,
                "fold": fold,
                "mae_days": mae,
                "rmse_days": rmse,
                "r2": r2,
                "train_groups": len(
                    train_groups
                ),
                "test_groups": len(
                    test_groups
                ),
                "group_overlap": len(
                    overlap
                ),
            }
        )


        for position, actual, predicted in zip(
            test_index,
            y_test,
            predictions
        ):

            prediction_results.append(
                {
                    "experiment": experiment_name,
                    "fold": fold,
                    "group": df.iloc[
                        position
                    ][GROUP],
                    "rep": df.iloc[
                        position
                    ]["rep"],
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


    summary_results.append(
        {
            "experiment": experiment_name,
            "feature_count": len(
                features
            ),
            "features": ", ".join(
                features
            ),
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
            "min_fold_mae_days": min(
                fold_mae
            ),
            "max_fold_mae_days": max(
                fold_mae
            ),
            "min_fold_r2": min(
                fold_r2
            ),
            "max_fold_r2": max(
                fold_r2
            ),
        }
    )


# ============================================================
# 11. CREATE RESULT DATAFRAMES
# ============================================================

summary_df = pd.DataFrame(
    summary_results
)

fold_df = pd.DataFrame(
    fold_results
)

prediction_df = pd.DataFrame(
    prediction_results
)


# ============================================================
# 12. SORT RESULTS BY MEAN MAE
# ============================================================

summary_df = summary_df.sort_values(
    "mean_mae_days"
)


# ============================================================
# 13. SAVE CSV RESULTS
# ============================================================

summary_file = (
    REPORTS_DIR
    / "research_day4_reduced_feature_comparison.csv"
)

fold_file = (
    REPORTS_DIR
    / "research_day4_reduced_feature_fold_results.csv"
)

prediction_file = (
    REPORTS_DIR
    / "research_day4_reduced_feature_predictions.csv"
)


summary_df.to_csv(
    summary_file,
    index=False
)

fold_df.to_csv(
    fold_file,
    index=False
)

prediction_df.to_csv(
    prediction_file,
    index=False
)


# ============================================================
# 14. FEATURE-COUNT VS MAE FIGURE
# ============================================================

plt.figure(
    figsize=(9, 6)
)

plt.scatter(
    summary_df["feature_count"],
    summary_df["mean_mae_days"]
)

for _, row in summary_df.iterrows():

    plt.annotate(
        row["experiment"],
        (
            row["feature_count"],
            row["mean_mae_days"]
        ),
        xytext=(5, 5),
        textcoords="offset points"
    )

plt.xlabel(
    "Number of Features"
)

plt.ylabel(
    "Mean MAE (days)"
)

plt.title(
    "Feature Count versus Mean Shelf-Life Prediction Error"
)

plt.tight_layout()

feature_count_figure = (
    FIGURES_DIR
    / "research_day4_feature_count_vs_mae.png"
)

plt.savefig(
    feature_count_figure,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 15. MODEL COMPARISON FIGURE
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plot_df = summary_df.sort_values(
    "mean_mae_days",
    ascending=True
)

plt.barh(
    plot_df["experiment"],
    plot_df["mean_mae_days"]
)

plt.xlabel(
    "Mean MAE (days)"
)

plt.ylabel(
    "Feature Set"
)

plt.title(
    "Reduced Day-4 Feature Set Comparison"
)

plt.tight_layout()

comparison_figure = (
    FIGURES_DIR
    / "research_day4_reduced_feature_comparison.png"
)

plt.savefig(
    comparison_figure,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 16. WRITE RESEARCH REPORT
# ============================================================

report_file = (
    REPORTS_DIR
    / "research_day4_feature_redundancy_report.txt"
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
        "DAY-4 FEATURE REDUNDANCY AND REDUCED-FEATURE ANALYSIS\n"
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
        "Feature-to-feature correlation\n"
    )

    report.write(
        "------------------------------\n"
    )

    report.write(
        feature_corr.to_string(
            float_format=lambda x: f"{x:.6f}"
        )
    )

    report.write(
        "\n\n"
    )


    report.write(
        "Pairwise feature correlations\n"
    )

    report.write(
        "------------------------------\n"
    )

    report.write(
        pairwise_df.to_string(
            index=False
        )
    )

    report.write(
        "\n\n"
    )


    report.write(
        "Reduced-feature model comparison\n"
    )

    report.write(
        "--------------------------------\n"
    )

    report.write(
        summary_df.to_string(
            index=False
        )
    )

    report.write(
        "\n\n"
    )


    report.write(
        "Interpretation guidance\n"
    )

    report.write(
        "-----------------------\n"
    )

    report.write(
        "Feature correlations describe statistical association "
        "between predictors and should not be interpreted as "
        "evidence of biological causation.\n\n"
    )

    report.write(
        "The reduced-feature experiments use the same Random "
        "Forest settings and GroupKFold procedure so that "
        "feature-set comparisons are performed under the same "
        "validation conditions.\n\n"
    )

    report.write(
        "A smaller feature set may be easier to interpret and "
        "implement, but lower feature count alone does not "
        "establish that a model is scientifically superior.\n\n"
    )

    report.write(
        "The dataset contains only 48 observations and therefore "
        "all findings should be treated as experimental evidence "
        "requiring further validation on independent data.\n"
    )


# ============================================================
# 17. FINAL OUTPUT
# ============================================================

print("\n")
print("=" * 70)
print("PAIRWISE FEATURE CORRELATIONS")
print("=" * 70)

print(
    pairwise_df[
        [
            "feature_1_label",
            "feature_2_label",
            "correlation",
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


print("\n")
print("=" * 70)
print("REDUCED-FEATURE MODEL COMPARISON")
print("=" * 70)

print(
    summary_df[
        [
            "experiment",
            "feature_count",
            "mean_mae_days",
            "std_mae_days",
            "mean_rmse_days",
            "std_rmse_days",
            "mean_r2",
            "std_r2",
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


print("\n")
print("=" * 70)
print("FILES SAVED")
print("=" * 70)

print(
    f"1. {feature_corr_file}"
)

print(
    f"2. {pairwise_file}"
)

print(
    f"3. {summary_file}"
)

print(
    f"4. {fold_file}"
)

print(
    f"5. {prediction_file}"
)

print(
    f"6. {heatmap_file}"
)

print(
    f"7. {feature_count_figure}"
)

print(
    f"8. {comparison_figure}"
)

print(
    f"9. {report_file}"
)


print("\n")
print("=" * 70)
print("DAY-4 REDUCED-FEATURE ANALYSIS COMPLETED SUCCESSFULLY")
print("=" * 70)