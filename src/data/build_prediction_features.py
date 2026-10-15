"""
AGRO LIFE-AI
Build Day-4 Prediction Features

Purpose:
    Prepare an early-prediction dataset using only information
    available by Day 4.

Target:
    shelf_life_days

Prediction features:
    - Neem leaf extract concentration
    - Beeswax coating concentration
    - Ascorbic acid at Day 4
    - pH at Day 4
    - Titratable acidity at Day 4
    - Total soluble solids at Day 4
    - Weight loss at Day 4

Important:
    Treatments and replication numbers are retained as metadata.
    They are NOT used as model predictors.
"""

from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# 1. PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "research_master_dataset.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "research_day4_features.csv"
)


# ---------------------------------------------------------
# 2. REQUIRED COLUMNS
# ---------------------------------------------------------

REQUIRED_COLUMNS = [
    "Neem leaf extract dipping",
    "Beeswax coating",
    "Treatments",
    "rep",
    "shelf-life",
    "AAat4thD",
    "pHat4thD",
    "TAat4thD",
    "TSSat4thD",
    "WLat4thD",
]


# ---------------------------------------------------------
# 3. CONCENTRATION MAPPINGS
# ---------------------------------------------------------

NEEM_MAPPING = {
    "NLED0": 0,
    "NLED15": 15,
    "NLED20": 20,
    "NLED25": 25,
}

BEESWAX_MAPPING = {
    "BWC0": 0,
    "BWC3": 3,
    "BWC6": 6,
    "BWC9": 9,
}


# ---------------------------------------------------------
# 4. LOAD RESEARCH MASTER DATASET
# ---------------------------------------------------------

print("=" * 70)
print("AGRO LIFE-AI - BUILD DAY-4 PREDICTION FEATURES")
print("=" * 70)

print("\nLoading research master dataset...")
print(f"Input: {INPUT_FILE}")

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nResearch master dataset was not found:\n{INPUT_FILE}\n"
        "Please run build_research_master.py first."
    )

df = pd.read_csv(INPUT_FILE)

print(f"Loaded records: {len(df)}")
print(f"Loaded columns: {len(df.columns)}")


# ---------------------------------------------------------
# 5. CHECK REQUIRED COLUMNS
# ---------------------------------------------------------

print("\nChecking required columns...")

missing_columns = [
    column for column in REQUIRED_COLUMNS
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "\nThe following required columns are missing:\n"
        + "\n".join(f"- {column}" for column in missing_columns)
    )

print("All required columns are present.")


# ---------------------------------------------------------
# 6. CREATE NUMERIC TREATMENT FEATURES
# ---------------------------------------------------------

print("\nConverting treatment levels to numeric concentrations...")

df["neem_extract_percent"] = (
    df["Neem leaf extract dipping"]
    .map(NEEM_MAPPING)
)

df["beeswax_coating_percent"] = (
    df["Beeswax coating"]
    .map(BEESWAX_MAPPING)
)


# ---------------------------------------------------------
# 7. CHECK TREATMENT CONVERSIONS
# ---------------------------------------------------------

if df["neem_extract_percent"].isna().any():
    unknown_neem = (
        df.loc[
            df["neem_extract_percent"].isna(),
            "Neem leaf extract dipping"
        ]
        .unique()
        .tolist()
    )

    raise ValueError(
        f"Unknown neem treatment values found: {unknown_neem}"
    )


if df["beeswax_coating_percent"].isna().any():
    unknown_beeswax = (
        df.loc[
            df["beeswax_coating_percent"].isna(),
            "Beeswax coating"
        ]
        .unique()
        .tolist()
    )

    raise ValueError(
        f"Unknown beeswax treatment values found: {unknown_beeswax}"
    )


# ---------------------------------------------------------
# 8. BUILD CLEAN DAY-4 DATASET
# ---------------------------------------------------------

print("\nBuilding Day-4 prediction dataset...")

day4_df = pd.DataFrame({
    "group": df["Treatments"],
    "rep": df["rep"],

    "neem_extract_percent":
        df["neem_extract_percent"],

    "beeswax_coating_percent":
        df["beeswax_coating_percent"],

    "aa_day4":
        df["AAat4thD"],

    "ph_day4":
        df["pHat4thD"],

    "ta_day4":
        df["TAat4thD"],

    "tss_day4":
        df["TSSat4thD"],

    "weight_loss_day4":
        df["WLat4thD"],

    "shelf_life_days":
        df["shelf-life"],
})


# ---------------------------------------------------------
# 9. CHECK DATA TYPES
# ---------------------------------------------------------

numeric_columns = [
    "neem_extract_percent",
    "beeswax_coating_percent",
    "aa_day4",
    "ph_day4",
    "ta_day4",
    "tss_day4",
    "weight_loss_day4",
    "shelf_life_days",
]

for column in numeric_columns:
    day4_df[column] = pd.to_numeric(
        day4_df[column],
        errors="coerce"
    )


# ---------------------------------------------------------
# 10. CHECK MISSING VALUES
# ---------------------------------------------------------

print("\nChecking missing values...")

missing_values = day4_df.isnull().sum()

if missing_values.sum() > 0:
    print("\nMissing values detected:")
    print(missing_values[missing_values > 0])

    raise ValueError(
        "The Day-4 feature dataset contains missing values."
    )

print("No missing values found.")


# ---------------------------------------------------------
# 11. CHECK RECORD COUNT
# ---------------------------------------------------------

if len(day4_df) != 48:
    raise ValueError(
        f"Expected 48 research records, but found {len(day4_df)}."
    )

print(f"Record count verified: {len(day4_df)}")


# ---------------------------------------------------------
# 12. CHECK TREATMENT GROUPS
# ---------------------------------------------------------

print("\nChecking treatment groups...")

group_counts = day4_df["group"].value_counts()

print(f"Unique treatment groups: {len(group_counts)}")

if len(group_counts) != 16:
    raise ValueError(
        f"Expected 16 treatment groups, found {len(group_counts)}."
    )

if not all(group_counts == 3):
    raise ValueError(
        "Each treatment group should contain exactly 3 replications."
    )

print("All 16 treatment groups contain 3 replications.")


# ---------------------------------------------------------
# 13. DISPLAY TREATMENT GROUPS
# ---------------------------------------------------------

print("\nTreatment groups:")

for group, count in group_counts.sort_index().items():
    print(f"  {group}: {count} records")


# ---------------------------------------------------------
# 14. DISPLAY DATASET SUMMARY
# ---------------------------------------------------------

print("\nDay-4 feature dataset information:")
print("-" * 70)

print(day4_df.info())

print("\nDescriptive statistics:")
print(
    day4_df[
        numeric_columns
    ].describe().round(3)
)


# ---------------------------------------------------------
# 15. DISPLAY FIRST RECORDS
# ---------------------------------------------------------

print("\nFirst 10 records:")
print("-" * 70)

print(
    day4_df.head(10).to_string(index=False)
)


# ---------------------------------------------------------
# 16. SAVE DATASET
# ---------------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

day4_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n" + "=" * 70)
print("DAY-4 FEATURE DATASET CREATED SUCCESSFULLY")
print("=" * 70)

print(f"\nOutput file:")
print(OUTPUT_FILE)

print(f"\nRecords: {len(day4_df)}")
print(f"Features + metadata columns: {len(day4_df.columns)}")

print("\nColumns:")
for column in day4_df.columns:
    print(f"  - {column}")

print("\nImportant methodological decision:")
print(
    "The 'group' and 'rep' columns are retained for validation "
    "and identification but will NOT be used as prediction features."
)

print("\nThe dataset is ready for the next step:")
print("GROUP-AWARE MACHINE-LEARNING MODEL TRAINING")