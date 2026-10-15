import pandas as pd
import os


# ============================================================
# AGRO LIFE-AI
# Build Master Research Dataset
# ============================================================

DATA_FOLDER = r".\data\raw\research_dataset"
OUTPUT_FOLDER = r".\data\processed"

OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "research_master_dataset.csv"
)

KEY_COLUMNS = [
    "Neem leaf extract dipping",
    "Beeswax coating",
    "Treatments",
    "rep",
]


# ------------------------------------------------------------
# Load Excel file
# ------------------------------------------------------------

def load_excel(filename):
    path = os.path.join(DATA_FOLDER, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    return pd.read_excel(path)


# ------------------------------------------------------------
# Main function
# ------------------------------------------------------------

def build_master_dataset():

    print("\n" + "=" * 75)
    print("AGRO LIFE-AI - BUILDING MASTER RESEARCH DATASET")
    print("=" * 75)

    # --------------------------------------------------------
    # Load all research files
    # --------------------------------------------------------

    print("\nLoading research datasets...")

    aa = load_excel("AA_Tomato_NLED_BWC.xlsx")
    decay = load_excel("Decay_Tomato_NLED_BWC.xlsx")
    marketability = load_excel("Marketability_Tomato_NLED_BWC.xlsx")
    ph = load_excel("pH_Tomato_NLED_BWC.xlsx")
    shelf_life = load_excel("Shelflife_Tomato_NLED_BWC.xlsx")
    ta = load_excel("TA_Tomato_NLED_BWC.xlsx")
    tss = load_excel("TSS_Tomato_NLED_BWC.xlsx")
    wl = load_excel("WL_Tomato_NLED_BWC.xlsx")

    datasets = {
        "AA": aa,
        "Decay": decay,
        "Marketability": marketability,
        "pH": ph,
        "Shelf Life": shelf_life,
        "TA": ta,
        "TSS": tss,
        "WL": wl,
    }

    # --------------------------------------------------------
    # Display record counts
    # --------------------------------------------------------

    print("\nRecord counts:")

    for name, df in datasets.items():
        print(f"{name:<18}: {len(df)}")

    # --------------------------------------------------------
    # Validate key columns
    # --------------------------------------------------------

    print("\nChecking experiment identifiers...")

    for name, df in datasets.items():

        missing_keys = [
            column for column in KEY_COLUMNS
            if column not in df.columns
        ]

        if missing_keys:
            raise ValueError(
                f"{name} is missing key columns: {missing_keys}"
            )

    print("All required identifiers are present.")

    # --------------------------------------------------------
    # Prepare datasets for merging
    # --------------------------------------------------------

    print("\nPreparing datasets for merging...")

    # Rename measurement columns with clear variable names
    # while keeping the original storage-day information.

    aa_columns = KEY_COLUMNS + [
        column for column in aa.columns
        if column not in KEY_COLUMNS
    ]

    decay_columns = KEY_COLUMNS + [
        column for column in decay.columns
        if column not in KEY_COLUMNS
    ]

    marketability_columns = KEY_COLUMNS + [
        column for column in marketability.columns
        if column not in KEY_COLUMNS
    ]

    ph_columns = KEY_COLUMNS + [
        column for column in ph.columns
        if column not in KEY_COLUMNS
    ]

    shelf_columns = KEY_COLUMNS + [
        "shelf-life"
    ]

    ta_columns = KEY_COLUMNS + [
        column for column in ta.columns
        if column not in KEY_COLUMNS
    ]

    tss_columns = KEY_COLUMNS + [
        column for column in tss.columns
        if column not in KEY_COLUMNS
    ]

    wl_columns = KEY_COLUMNS + [
        column for column in wl.columns
        if column not in KEY_COLUMNS
    ]

    aa = aa[aa_columns]
    decay = decay[decay_columns]
    marketability = marketability[marketability_columns]
    ph = ph[ph_columns]
    shelf_life = shelf_life[shelf_columns]
    ta = ta[ta_columns]
    tss = tss[tss_columns]
    wl = wl[wl_columns]

    # --------------------------------------------------------
    # Merge datasets using verified experiment identifiers
    # --------------------------------------------------------

    print("\nMerging datasets...")

    master = shelf_life.copy()

    merge_order = [
        ("AA", aa),
        ("Decay", decay),
        ("Marketability", marketability),
        ("pH", ph),
        ("TA", ta),
        ("TSS", tss),
        ("WL", wl),
    ]

    for name, df in merge_order:

        master = master.merge(
            df,
            on=KEY_COLUMNS,
            how="left",
            validate="one_to_one"
        )

        print(
            f"Merged {name:<15} -> "
            f"{len(master)} records"
        )

    # --------------------------------------------------------
    # Create output folder if necessary
    # --------------------------------------------------------

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # --------------------------------------------------------
    # Save master dataset
    # --------------------------------------------------------

    master.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Final information
    # --------------------------------------------------------

    print("\n" + "=" * 75)
    print("MASTER DATASET CREATED SUCCESSFULLY")
    print("=" * 75)

    print(f"\nRecords: {len(master)}")
    print(f"Columns: {len(master.columns)}")

    print("\nOutput file:")
    print(OUTPUT_FILE)

    print("\nColumns:")
    for number, column in enumerate(master.columns, start=1):
        print(f"{number:02d}. {column}")

    print("\nMissing values:")
    missing = master.isnull().sum()

    if missing.sum() == 0:
        print("No missing values detected.")
    else:
        print(
            missing[missing > 0]
            .to_string()
        )

    print("\n" + "=" * 75)
    print("MASTER DATASET BUILD COMPLETED")
    print("=" * 75)


# ------------------------------------------------------------
# Program entry point
# ------------------------------------------------------------

if __name__ == "__main__":
    build_master_dataset()