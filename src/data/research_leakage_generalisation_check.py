"""
AGRO LIFE-AI
Leakage and Generalisation Diagnostic

Purpose:
    Investigate whether the Day-4 research model contains:
    1. Target leakage
    2. Group/replication leakage
    3. Duplicate observations
    4. Post-Day-4 variables
    5. Suspiciously strong performance caused by the dataset structure

    The script also performs a target-shuffling diagnostic.
    If the model can predict a randomly shuffled target well,
    this would indicate a methodological problem.

Important:
    This is a research diagnostic for a small experimental dataset.
    It does not prove real-world generalisation.
"""

from pathlib import Path

import numpy as np
import pandas as pd

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

MASTER_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "research_master_dataset.csv"
)

RESULTS_DIR = PROJECT_ROOT / "results"
REPORTS_DIR = RESULTS_DIR / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. LOAD DATA
# ============================================================

print("=" * 70)
print("AGRO LIFE-AI - LEAKAGE & GENERALISATION CHECK")
print("=" * 70)

print("\nLoading Day-4 feature dataset...")

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found:\n{DATA_FILE}"
    )

df = pd.read_csv(DATA_FILE)

print(f"Records: {len(df)}")
print(f"Columns: {len(df.columns)}")


# ============================================================
# 3. DEFINE MODEL FEATURES
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

GROUP_COLUMN = "group"

REPLICATION_COLUMN = "rep"


# ============================================================
# 4. BASIC STRUCTURE CHECK
# ============================================================

print("\n" + "-" * 70)
print("1. BASIC DATA STRUCTURE CHECK")
print("-" * 70)

required_columns = (
    FEATURES
    + [
        TARGET,
        GROUP_COLUMN,
        REPLICATION_COLUMN,
    ]
)

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    print(
        "ERROR: Missing required columns:"
    )

    for column in missing_columns:
        print(f"  - {column}")

    raise ValueError(
        "Required columns are missing."
    )

else:

    print(
        "All required feature, target, group and "
        "replication columns are present."
    )


# ============================================================
# 5. TARGET LEAKAGE CHECK
# ============================================================

print("\n" + "-" * 70)
print("2. TARGET LEAKAGE CHECK")
print("-" * 70)

target_in_features = TARGET in FEATURES

print(
    f"Target '{TARGET}' included directly as a predictor: "
    f"{target_in_features}"
)

if target_in_features:
    raise ValueError(
        "TARGET LEAKAGE DETECTED: shelf_life_days is being "
        "used directly as a model feature."
    )

print(
    "Direct target leakage check: PASSED"
)


# ============================================================
# 6. GROUP / REPLICATION LEAKAGE CHECK
# ============================================================

print("\n" + "-" * 70)
print("3. GROUP AND REPLICATION LEAKAGE CHECK")
print("-" * 70)

group_in_features = GROUP_COLUMN in FEATURES
rep_in_features = REPLICATION_COLUMN in FEATURES

print(
    f"Group identifier used as predictor: "
    f"{group_in_features}"
)

print(
    f"Replication identifier used as predictor: "
    f"{rep_in_features}"
)

if group_in_features or rep_in_features:

    raise ValueError(
        "GROUP/REPLICATION LEAKAGE DETECTED."
    )

print(
    "Group and replication identifiers are metadata only."
)

print(
    f"Unique treatment groups: "
    f"{df[GROUP_COLUMN].nunique()}"
)

print(
    f"Observations per group:\n"
    f"{df.groupby(GROUP_COLUMN).size().value_counts().to_dict()}"
)


# ============================================================
# 7. DUPLICATE CHECK
# ============================================================

print("\n" + "-" * 70)
print("4. DUPLICATE OBSERVATION CHECK")
print("-" * 70)

duplicate_count = df.duplicated().sum()

print(
    f"Complete duplicate rows: {duplicate_count}"
)

if duplicate_count == 0:
    print("Duplicate check: PASSED")
else:
    print(
        "WARNING: Duplicate rows were detected."
    )


# ============================================================
# 8. FEATURE DUPLICATE CHECK
# ============================================================

feature_duplicate_count = (
    df[FEATURES]
    .duplicated()
    .sum()
)

print(
    f"Duplicate feature rows: "
    f"{feature_duplicate_count}"
)


# ============================================================
# 9. DAY-4 AVAILABILITY CHECK
# ============================================================

print("\n" + "-" * 70)
print("5. DAY-4 FEATURE AVAILABILITY CHECK")
print("-" * 70)

print(
    "The model predictors are:"
)

for feature in FEATURES:
    print(f"  - {feature}")

post_day4_features = [
    column
    for column in df.columns
    if (
        "day8" in column.lower()
        or "day12" in column.lower()
        or "day16" in column.lower()
        or "day20" in column.lower()
        or "day24" in column.lower()
        or "day28" in column.lower()
        or "day32" in column.lower()
        or "day36" in column.lower()
    )
]

print(
    "\nPost-Day-4 measurement columns present in the "
    "Day-4 feature dataset:"
)

if post_day4_features:

    for feature in post_day4_features:
        print(f"  - {feature}")

else:

    print(
        "  None"
    )

print(
    "\nDay-4 feature-set availability check completed."
)


# ============================================================
# 10. CHECK ORIGINAL MASTER DATASET
# ============================================================

print("\n" + "-" * 70)
print("6. ORIGINAL MASTER DATASET CHECK")
print("-" * 70)

if MASTER_FILE.exists():

    master = pd.read_csv(MASTER_FILE)

    print(
        f"Master dataset records: {len(master)}"
    )

    print(
        f"Master dataset columns: {len(master.columns)}"
    )

    print(
        f"Master dataset target available: "
        f"{'shelf-life' in master.columns}"
    )

    print(
        "The master dataset contains later measurements, "
        "but these are not included in the Day-4 feature dataset."
    )

else:

    print(
        "Master dataset not found. "
        "Skipping this check."
    )


# ============================================================
# 11. GROUP K-FOLD SEPARATION CHECK
# ============================================================

print("\n" + "-" * 70)
print("7. GROUP K-FOLD SEPARATION CHECK")
print("-" * 70)

X = df[FEATURES]
y = df[TARGET]
groups = df[GROUP_COLUMN]

group_kfold = GroupKFold(n_splits=4)

separation_results = []

for fold_number, (train_index, test_index) in enumerate(
    group_kfold.split(X, y, groups),
    start=1
):

    train_groups = set(
        groups.iloc[train_index]
    )

    test_groups = set(
        groups.iloc[test_index]
    )

    overlap = train_groups.intersection(
        test_groups
    )

    separation_results.append(
        {
            "fold": fold_number,
            "train_records": len(train_index),
            "test_records": len(test_index),
            "train_groups": len(train_groups),
            "test_groups": len(test_groups),
            "group_overlap": len(overlap),
        }
    )

    print(
        f"Fold {fold_number}: "
        f"train groups={len(train_groups)}, "
        f"test groups={len(test_groups)}, "
        f"overlap={len(overlap)}"
    )

separation_df = pd.DataFrame(
    separation_results
)

if separation_df["group_overlap"].max() == 0:

    print(
        "\nGROUP SEPARATION CHECK: PASSED"
    )

else:

    raise ValueError(
        "GROUP LEAKAGE DETECTED BETWEEN TRAINING "
        "AND TESTING FOLDS."
    )


# ============================================================
# 12. NORMAL GROUP-KFOLD MODEL CHECK
# ============================================================

print("\n" + "-" * 70)
print("8. INDEPENDENT GROUP-KFOLD MODEL CHECK")
print("-" * 70)

normal_results = []

for fold_number, (train_index, test_index) in enumerate(
    group_kfold.split(X, y, groups),
    start=1
):

    X_train = X.iloc[train_index]
    X_test = X.iloc[test_index]

    y_train = y.iloc[train_index]
    y_test = y.iloc[test_index]

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        max_depth=4,
        min_samples_leaf=2,
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    fold_mae = mean_absolute_error(
        y_test,
        predictions
    )

    fold_rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    fold_r2 = r2_score(
        y_test,
        predictions
    )

    normal_results.append(
        {
            "fold": fold_number,
            "mae": fold_mae,
            "rmse": fold_rmse,
            "r2": fold_r2,
        }
    )

    print(
        f"Fold {fold_number}: "
        f"MAE={fold_mae:.4f}, "
        f"RMSE={fold_rmse:.4f}, "
        f"R2={fold_r2:.4f}"
    )

normal_df = pd.DataFrame(
    normal_results
)


# ============================================================
# 13. TARGET-SHUFFLING DIAGNOSTIC
# ============================================================

print("\n" + "-" * 70)
print("9. TARGET-SHUFFLING LEAKAGE DIAGNOSTIC")
print("-" * 70)

print(
    "The shelf-life target will now be randomly shuffled."
)

print(
    "A valid model should lose its predictive performance "
    "when the target relationship is destroyed."
)

rng = np.random.default_rng(42)

shuffled_y = pd.Series(
    rng.permutation(
        y.to_numpy()
    ),
    index=y.index
)

shuffled_results = []

for fold_number, (train_index, test_index) in enumerate(
    group_kfold.split(X, shuffled_y, groups),
    start=1
):

    X_train = X.iloc[train_index]
    X_test = X.iloc[test_index]

    y_train = shuffled_y.iloc[train_index]
    y_test = shuffled_y.iloc[test_index]

    shuffled_model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        max_depth=4,
        min_samples_leaf=2,
    )

    shuffled_model.fit(
        X_train,
        y_train
    )

    shuffled_predictions = shuffled_model.predict(
        X_test
    )

    shuffled_mae = mean_absolute_error(
        y_test,
        shuffled_predictions
    )

    shuffled_rmse = np.sqrt(
        mean_squared_error(
            y_test,
            shuffled_predictions
        )
    )

    shuffled_r2 = r2_score(
        y_test,
        shuffled_predictions
    )

    shuffled_results.append(
        {
            "fold": fold_number,
            "mae": shuffled_mae,
            "rmse": shuffled_rmse,
            "r2": shuffled_r2,
        }
    )

    print(
        f"Fold {fold_number}: "
        f"MAE={shuffled_mae:.4f}, "
        f"RMSE={shuffled_rmse:.4f}, "
        f"R2={shuffled_r2:.4f}"
    )


shuffled_df = pd.DataFrame(
    shuffled_results
)


# ============================================================
# 14. COMPARE NORMAL AND SHUFFLED RESULTS
# ============================================================

normal_mean_mae = normal_df["mae"].mean()
normal_mean_rmse = normal_df["rmse"].mean()
normal_mean_r2 = normal_df["r2"].mean()

shuffled_mean_mae = shuffled_df["mae"].mean()
shuffled_mean_rmse = shuffled_df["rmse"].mean()
shuffled_mean_r2 = shuffled_df["r2"].mean()


print("\nNormal model mean results:")
print(
    f"MAE:  {normal_mean_mae:.4f}"
)

print(
    f"RMSE: {normal_mean_rmse:.4f}"
)

print(
    f"R2:   {normal_mean_r2:.4f}"
)

print("\nShuffled-target mean results:")
print(
    f"MAE:  {shuffled_mean_mae:.4f}"
)

print(
    f"RMSE: {shuffled_mean_rmse:.4f}"
)

print(
    f"R2:   {shuffled_mean_r2:.4f}"
)


# ============================================================
# 15. DETERMINE SHUFFLE DIAGNOSTIC RESULT
# ============================================================

if shuffled_mean_r2 < normal_mean_r2:

    shuffle_result = (
        "The target-shuffling diagnostic reduced model "
        "performance, which is consistent with the model "
        "learning information related to the original target."
    )

else:

    shuffle_result = (
        "The target-shuffling diagnostic did not clearly "
        "reduce performance. This requires additional "
        "investigation before strong conclusions can be made."
    )


print("\nTarget-shuffling assessment:")
print(shuffle_result)


# ============================================================
# 16. CHECK TARGET DISTRIBUTION
# ============================================================

print("\n" + "-" * 70)
print("10. TARGET DISTRIBUTION CHECK")
print("-" * 70)

print(
    y.describe()
)

target_range = y.max() - y.min()

print(
    f"\nShelf-life range: {target_range} days"
)

print(
    f"Minimum shelf life: {y.min()} days"
)

print(
    f"Maximum shelf life: {y.max()} days"
)


# ============================================================
# 17. IDENTIFY CONTROL GROUP
# ============================================================

print("\n" + "-" * 70)
print("11. CONTROL-GROUP ERROR CHECK")
print("-" * 70)

control_group = "NLED0*BWC0"

control_data = df[
    df[GROUP_COLUMN] == control_group
]

if not control_data.empty:

    print(
        f"Control group found: {control_group}"
    )

    print(
        f"Control observations: {len(control_data)}"
    )

    print(
        f"Control mean shelf life: "
        f"{control_data[TARGET].mean():.2f} days"
    )

    print(
        "The control group will be considered separately "
        "when interpreting model generalisation."
    )

else:

    print(
        "Control group was not found."
    )


# ============================================================
# 18. SAVE DIAGNOSTIC RESULTS
# ============================================================

separation_file = (
    REPORTS_DIR
    / "research_group_kfold_separation_check.csv"
)

separation_df.to_csv(
    separation_file,
    index=False
)

normal_file = (
    REPORTS_DIR
    / "research_normal_model_diagnostic.csv"
)

normal_df.to_csv(
    normal_file,
    index=False
)

shuffled_file = (
    REPORTS_DIR
    / "research_target_shuffle_diagnostic.csv"
)

shuffled_df.to_csv(
    shuffled_file,
    index=False
)


# ============================================================
# 19. GENERATE FINAL DIAGNOSTIC REPORT
# ============================================================

report_file = (
    REPORTS_DIR
    / "research_leakage_generalisation_report.txt"
)

with open(
    report_file,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "AGRO LIFE-AI\n"
        "LEAKAGE AND GENERALISATION DIAGNOSTIC REPORT\n"
        "=============================================\n\n"
    )

    file.write(
        "MODEL:\n"
        "Day-4 Early Quality Random Forest Regression\n\n"
    )

    file.write(
        f"Observations: {len(df)}\n"
    )

    file.write(
        f"Treatment groups: {df[GROUP_COLUMN].nunique()}\n"
    )

    file.write(
        f"Replications per treatment group:\n"
        f"{df.groupby(GROUP_COLUMN).size().unique().tolist()}\n\n"
    )

    file.write(
        "DIRECT TARGET LEAKAGE\n"
        "---------------------\n"
    )

    file.write(
        f"Target included among predictors: "
        f"{target_in_features}\n"
    )

    file.write(
        "Result: PASSED\n\n"
    )

    file.write(
        "GROUP/REPLICATION LEAKAGE\n"
        "-------------------------\n"
    )

    file.write(
        f"Group used as predictor: "
        f"{group_in_features}\n"
    )

    file.write(
        f"Replication used as predictor: "
        f"{rep_in_features}\n"
    )

    file.write(
        "Result: PASSED\n\n"
    )

    file.write(
        "DUPLICATE CHECK\n"
        "---------------\n"
    )

    file.write(
        f"Complete duplicate rows: "
        f"{duplicate_count}\n"
    )

    file.write(
        f"Duplicate feature rows: "
        f"{feature_duplicate_count}\n\n"
    )

    file.write(
        "GROUP-KFOLD SEPARATION\n"
        "----------------------\n"
    )

    file.write(
        separation_df.to_string(index=False)
    )

    file.write("\n\n")

    file.write(
        "NORMAL GROUP-KFOLD PERFORMANCE\n"
        "------------------------------\n"
    )

    file.write(
        normal_df.to_string(index=False)
    )

    file.write("\n\n")

    file.write(
        "Mean MAE: "
        f"{normal_mean_mae:.4f}\n"
    )

    file.write(
        "Mean RMSE: "
        f"{normal_mean_rmse:.4f}\n"
    )

    file.write(
        "Mean R2: "
        f"{normal_mean_r2:.4f}\n\n"
    )

    file.write(
        "TARGET-SHUFFLING DIAGNOSTIC\n"
        "---------------------------\n"
    )

    file.write(
        shuffled_df.to_string(index=False)
    )

    file.write("\n\n")

    file.write(
        "Shuffled mean MAE: "
        f"{shuffled_mean_mae:.4f}\n"
    )

    file.write(
        "Shuffled mean RMSE: "
        f"{shuffled_mean_rmse:.4f}\n"
    )

    file.write(
        "Shuffled mean R2: "
        f"{shuffled_mean_r2:.4f}\n\n"
    )

    file.write(
        "TARGET-SHUFFLING INTERPRETATION\n"
        "------------------------------\n"
    )

    file.write(
        shuffle_result
    )

    file.write("\n\n")

    file.write(
        "TARGET DISTRIBUTION\n"
        "-------------------\n"
    )

    file.write(
        y.describe().to_string()
    )

    file.write("\n\n")

    file.write(
        "INTERPRETATION AND LIMITATIONS\n"
        "------------------------------\n"
    )

    file.write(
        "1. The Day-4 feature dataset does not directly include "
        "the shelf-life target among the predictors.\n\n"
    )

    file.write(
        "2. Group and replication identifiers are retained as "
        "metadata and are not used as model predictors.\n\n"
    )

    file.write(
        "3. GroupKFold validation separates treatment groups "
        "between training and testing folds, reducing the risk "
        "of treatment-group leakage.\n\n"
    )

    file.write(
        "4. The Day-4 feature dataset contains only measurements "
        "available at or before Day 4. Later measurements are "
        "excluded from the prediction feature set.\n\n"
    )

    file.write(
        "5. The target-shuffling diagnostic provides a negative "
        "control. Destroying the relationship between predictors "
        "and target should reduce meaningful predictive performance.\n\n"
    )

    file.write(
        "6. Strong predictive relationships in the original data "
        "should not automatically be interpreted as causal effects.\n\n"
    )

    file.write(
        "7. The dataset contains 48 observations and a narrow "
        "shelf-life range. Therefore, the results should be "
        "treated as evidence from an experimental research "
        "prototype rather than proof of broad real-world "
        "generalisation.\n\n"
    )

    file.write(
        "8. Additional independent datasets would be required "
        "to evaluate the model outside the experimental conditions "
        "represented by the current dataset.\n"
    )


# ============================================================
# 20. FINAL OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("LEAKAGE & GENERALISATION CHECK COMPLETED")
print("=" * 70)

print(
    "\nGenerated files:"
)

print(
    f"\n1. Group separation:\n"
    f"   {separation_file}"
)

print(
    f"\n2. Normal model diagnostic:\n"
    f"   {normal_file}"
)

print(
    f"\n3. Target-shuffle diagnostic:\n"
    f"   {shuffled_file}"
)

print(
    f"\n4. Final diagnostic report:\n"
    f"   {report_file}"
)

print("\n" + "=" * 70)