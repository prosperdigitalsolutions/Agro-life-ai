"""
AGRO LIFE-AI
Research Baseline Comparison

Purpose:
Compare a simple mean-based baseline against selected
Random Forest feature sets using the SAME GroupKFold
validation procedure.

Baseline:
    Predict the mean shelf life of the training data.

ML models:
    1. Weight Loss - Day 4
    2. Titratable Acidity - Day 4
    3. Weight Loss + Titratable Acidity - Day 4
    4. All Day-4 Quality Features

The comparison uses:
    - 4-fold GroupKFold
    - 16 treatment groups
    - 3 replicates per treatment group
    - identical train/test folds

Important:
This is an experimental research comparison using
48 observations. It is not production validation.
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
print("RESEARCH BASELINE COMPARISON")
print("=" * 70)

print("\nLoading research dataset...")

df = pd.read_csv(
    DATA_FILE
)

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
# 4. DEFINE MODEL FEATURE SETS
# ============================================================

MODEL_FEATURE_SETS = {

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

    "F4_All_Day4_Quality": [
        "aa_day4",
        "ph_day4",
        "ta_day4",
        "tss_day4",
        "weight_loss_day4",
    ],
}


# ============================================================
# 5. VALIDATE DATA
# ============================================================

required_columns = [
    TARGET,
    GROUP,
]

for feature_list in MODEL_FEATURE_SETS.values():

    required_columns.extend(
        feature_list
    )

required_columns = list(
    dict.fromkeys(
        required_columns
    )
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
# 6. GROUP INFORMATION
# ============================================================

groups = df[GROUP]

unique_groups = groups.nunique()

print(
    f"Unique treatment groups: {unique_groups}"
)

group_counts = (
    df.groupby(GROUP)
    .size()
)

print(
    "\nObservations per treatment group:"
)

print(
    group_counts.value_counts()
    .sort_index()
)


# ============================================================
# 7. MODEL SETTINGS
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

y = df[TARGET]


# ============================================================
# 8. RESULT STORAGE
# ============================================================

summary_results = []

fold_results = []

prediction_results = []


# ============================================================
# 9. STORE AND DISPLAY FOLD STRUCTURE
# ============================================================

print("\n")
print("=" * 70)
print("GROUPKFOLD VALIDATION STRUCTURE")
print("=" * 70)

fold_structure = []

for fold, (
    train_index,
    test_index
) in enumerate(
    group_kfold.split(
        df[[TARGET]],
        y,
        groups
    ),
    start=1
):

    train_groups = sorted(
        set(
            df.iloc[
                train_index
            ][GROUP]
        )
    )

    test_groups = sorted(
        set(
            df.iloc[
                test_index
            ][GROUP]
        )
    )

    fold_structure.append(
        {
            "fold": fold,
            "train_group_count": len(
                train_groups
            ),
            "test_group_count": len(
                test_groups
            ),
            "test_observation_count": len(
                test_index
            ),
            "test_groups": ", ".join(
                test_groups
            ),
        }
    )

    print(
        f"\nFold {fold}"
    )

    print(
        f"  Training groups: {len(train_groups)}"
    )

    print(
        f"  Test groups: {len(test_groups)}"
    )

    print(
        f"  Test observations: {len(test_index)}"
    )

    print(
        "  Test groups:"
    )

    for group_name in test_groups:

        print(
            f"    - {group_name}"
        )


fold_structure_df = pd.DataFrame(
    fold_structure
)

fold_structure_file = (
    REPORTS_DIR
    / "research_groupkfold_structure.csv"
)

fold_structure_df.to_csv(
    fold_structure_file,
    index=False
)


# ============================================================
# 10. RUN BASELINE + ML MODELS
# ============================================================

for experiment_name, features in (
    MODEL_FEATURE_SETS.items()
):

    print("\n")
    print("=" * 70)
    print(
        f"MODEL: {experiment_name}"
    )
    print("=" * 70)

    print(
        "Features:"
    )

    for feature in features:

        print(
            f"  - {feature}"
        )

    model_fold_mae = []

    model_fold_rmse = []

    model_fold_r2 = []

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

        # ----------------------------------------------------
        # TRAIN RANDOM FOREST
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # METRICS
        # ----------------------------------------------------

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

        model_fold_mae.append(
            mae
        )

        model_fold_rmse.append(
            rmse
        )

        model_fold_r2.append(
            r2
        )

        print(
            f"Fold {fold}: "
            f"MAE={mae:.4f}, "
            f"RMSE={rmse:.4f}, "
            f"R²={r2:.4f}"
        )

        test_group_text = ", ".join(
            sorted(test_groups)
        )

        fold_results.append(
            {
                "model": experiment_name,
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
                "test_observations": len(
                    test_index
                ),
                "test_group_names": test_group_text,
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
                    "model": experiment_name,
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

    # --------------------------------------------------------
    # MODEL SUMMARY
    # --------------------------------------------------------

    summary_results.append(
        {
            "model": experiment_name,
            "model_type": "Random Forest",
            "features": ", ".join(
                features
            ),
            "mean_mae_days": np.mean(
                model_fold_mae
            ),
            "std_mae_days": np.std(
                model_fold_mae,
                ddof=1
            ),
            "mean_rmse_days": np.mean(
                model_fold_rmse
            ),
            "std_rmse_days": np.std(
                model_fold_rmse,
                ddof=1
            ),
            "mean_r2": np.mean(
                model_fold_r2
            ),
            "std_r2": np.std(
                model_fold_r2,
                ddof=1
            ),
        }
    )


# ============================================================
# 11. RUN MEAN BASELINE
# ============================================================

print("\n")
print("=" * 70)
print("MEAN SHELF-LIFE BASELINE")
print("=" * 70)

baseline_mae = []

baseline_rmse = []

baseline_r2 = []

for fold, (
    train_index,
    test_index
) in enumerate(
    group_kfold.split(
        df[[TARGET]],
        y,
        groups
    ),
    start=1
):

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
            f"Group leakage detected in baseline "
            f"Fold {fold}: {overlap}"
        )

    # --------------------------------------------------------
    # BASELINE PREDICTION
    # --------------------------------------------------------

    training_mean = y_train.mean()

    predictions = np.full(
        len(y_test),
        training_mean
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

    baseline_mae.append(
        mae
    )

    baseline_rmse.append(
        rmse
    )

    baseline_r2.append(
        r2
    )

    print(
        f"Fold {fold}: "
        f"Training mean={training_mean:.4f}, "
        f"MAE={mae:.4f}, "
        f"RMSE={rmse:.4f}, "
        f"R²={r2:.4f}"
    )

    test_group_text = ", ".join(
        sorted(test_groups)
    )

    fold_results.append(
        {
            "model": "Baseline_Mean",
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
            "test_observations": len(
                test_index
            ),
            "test_group_names": test_group_text,
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
                "model": "Baseline_Mean",
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
        "model": "Baseline_Mean",
        "model_type": "Mean Baseline",
        "features": "Training-set mean only",
        "mean_mae_days": np.mean(
            baseline_mae
        ),
        "std_mae_days": np.std(
            baseline_mae,
            ddof=1
        ),
        "mean_rmse_days": np.mean(
            baseline_rmse
        ),
        "std_rmse_days": np.std(
            baseline_rmse,
            ddof=1
        ),
        "mean_r2": np.mean(
            baseline_r2
        ),
        "std_r2": np.std(
            baseline_r2,
            ddof=1
        ),
    }
)


# ============================================================
# 12. CREATE DATAFRAMES
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
# 13. SAVE RAW RESULTS
# ============================================================

summary_file = (
    REPORTS_DIR
    / "research_baseline_comparison.csv"
)

fold_file = (
    REPORTS_DIR
    / "research_baseline_fold_results.csv"
)

prediction_file = (
    REPORTS_DIR
    / "research_baseline_predictions.csv"
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
# 14. CALCULATE COMPARISON AGAINST BASELINE
# ============================================================

baseline_summary = summary_df[
    summary_df["model"]
    == "Baseline_Mean"
].iloc[0]

baseline_mae_value = (
    baseline_summary[
        "mean_mae_days"
    ]
)

comparison_rows = []

for _, row in summary_df.iterrows():

    if row["model"] == "Baseline_Mean":

        continue

    mae_reduction = (
        baseline_mae_value
        - row["mean_mae_days"]
    )

    mae_reduction_percent = (
        mae_reduction
        / baseline_mae_value
        * 100
    )

    comparison_rows.append(
        {
            "model": row["model"],
            "mean_mae_days": row[
                "mean_mae_days"
            ],
            "baseline_mae_days": (
                baseline_mae_value
            ),
            "mae_difference_days": (
                mae_reduction
            ),
            "mae_reduction_percent": (
                mae_reduction_percent
            ),
            "mean_rmse_days": row[
                "mean_rmse_days"
            ],
            "mean_r2": row[
                "mean_r2"
            ],
        }
    )


comparison_df = pd.DataFrame(
    comparison_rows
)

comparison_file = (
    REPORTS_DIR
    / "research_ml_vs_baseline_comparison.csv"
)

comparison_df.to_csv(
    comparison_file,
    index=False
)


# ============================================================
# 15. PRINT FINAL COMPARISON
# ============================================================

print("\n")
print("=" * 70)
print("FINAL BASELINE VS ML COMPARISON")
print("=" * 70)

print(
    summary_df[
        [
            "model",
            "model_type",
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
print("ML IMPROVEMENT RELATIVE TO MEAN BASELINE")
print("=" * 70)

print(
    comparison_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ============================================================
# 16. BASELINE VS ML MAE FIGURE
# ============================================================

plot_df = summary_df.sort_values(
    "mean_mae_days",
    ascending=True
)

plt.figure(
    figsize=(10, 6)
)

plt.barh(
    plot_df["model"],
    plot_df["mean_mae_days"]
)

plt.xlabel(
    "Mean MAE (days)"
)

plt.ylabel(
    "Model"
)

plt.title(
    "Mean Absolute Error: Baseline versus Random Forest Models"
)

plt.tight_layout()

mae_figure = (
    FIGURES_DIR
    / "research_baseline_vs_ml_mae.png"
)

plt.savefig(
    mae_figure,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 17. R² COMPARISON FIGURE
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.bar(
    summary_df["model"],
    summary_df["mean_r2"]
)

plt.axhline(
    0,
    linewidth=1
)

plt.ylabel(
    "Mean R²"
)

plt.xlabel(
    "Model"
)

plt.title(
    "Mean R²: Baseline versus Random Forest Models"
)

plt.xticks(
    rotation=30,
    ha="right"
)

plt.tight_layout()

r2_figure = (
    FIGURES_DIR
    / "research_baseline_vs_ml_r2.png"
)

plt.savefig(
    r2_figure,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 18. WRITE RESEARCH REPORT
# ============================================================

report_file = (
    REPORTS_DIR
    / "research_baseline_comparison_report.txt"
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
        "RESEARCH BASELINE COMPARISON\n"
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
        "The purpose of this experiment is to determine whether "
        "the tested Random Forest models provide predictive "
        "information beyond a simple mean-based shelf-life "
        "baseline.\n\n"
    )

    report.write(
        "Dataset and validation\n"
    )

    report.write(
        "----------------------\n"
    )

    report.write(
        f"Records: {len(df)}\n"
    )

    report.write(
        f"Treatment groups: {unique_groups}\n"
    )

    report.write(
        "Validation: 4-fold GroupKFold\n"
    )

    report.write(
        "Replications: 3 observations per treatment group\n"
    )

    report.write(
        "Each fold contains 4 treatment groups and "
        "12 test observations.\n"
    )

    report.write(
        "Group-level separation was maintained so that "
        "replicates from the same treatment group were "
        "not split between training and testing data.\n\n"
    )

    report.write(
        "GroupKFold fold structure\n"
    )

    report.write(
        "-------------------------\n"
    )

    for _, row in fold_structure_df.iterrows():

        report.write(
            f"Fold {int(row['fold'])}: "
            f"{int(row['test_group_count'])} test groups, "
            f"{int(row['test_observation_count'])} observations; "
            f"test groups = {row['test_groups']}\n"
        )

    report.write(
        "\n"
    )

    report.write(
        "The fold structure represents an intentionally "
        "grouped validation design. In this experiment, "
        "Fold 4 contains the BWC0 treatment groups, meaning "
        "that the BWC0 condition is evaluated as an unseen "
        "treatment condition during that fold's testing phase.\n\n"
    )

    report.write(
        "Model results\n"
    )

    report.write(
        "-------------\n"
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
        "Comparison against baseline\n"
    )

    report.write(
        "---------------------------\n"
    )

    report.write(
        comparison_df.to_string(
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
        "The mean baseline predicts the mean shelf life "
        "calculated from the training data within each "
        "validation fold.\n\n"
    )

    report.write(
        "Lower MAE and RMSE represent smaller prediction "
        "errors. R² describes explained variance relative "
        "to a mean-based reference and may be negative "
        "when predictions perform poorly on a test fold.\n\n"
    )

    report.write(
        "A lower mean MAE than the baseline indicates lower "
        "average absolute prediction error under the "
        "validation procedure used in this experiment. "
        "It does not establish generalisation to independent "
        "agricultural populations.\n\n"
    )

    report.write(
        "The results show variation between validation folds. "
        "This fold-to-fold variation is important because the "
        "GroupKFold procedure evaluates performance on treatment "
        "groups that are not represented in the corresponding "
        "training fold.\n\n"
    )

    report.write(
        "The BWC0 treatment condition forms the test groups "
        "in Fold 4. The relatively larger errors observed "
        "in that fold demonstrate the difficulty of "
        "generalising from the other treatment conditions "
        "to this unseen condition.\n\n"
    )

    report.write(
        "Among the evaluated configurations, differences in "
        "mean MAE and mean RMSE should be interpreted as "
        "results of this particular experimental validation "
        "rather than as proof of production-level superiority.\n\n"
    )

    report.write(
        "Because the dataset contains only 48 observations "
        "from one experimental study, the findings should "
        "be treated as research-prototype evidence. Independent "
        "datasets and further validation are required before "
        "real-world deployment.\n"
    )


# ============================================================
# 19. FINAL FILE LIST
# ============================================================

print("\n")
print("=" * 70)
print("FILES SAVED")
print("=" * 70)

print(
    f"1. {summary_file}"
)

print(
    f"2. {fold_file}"
)

print(
    f"3. {prediction_file}"
)

print(
    f"4. {comparison_file}"
)

print(
    f"5. {mae_figure}"
)

print(
    f"6. {r2_figure}"
)

print(
    f"7. {report_file}"
)

print(
    f"8. {fold_structure_file}"
)

print("\n")
print("=" * 70)
print(
    "RESEARCH BASELINE COMPARISON COMPLETED SUCCESSFULLY"
)
print("=" * 70)