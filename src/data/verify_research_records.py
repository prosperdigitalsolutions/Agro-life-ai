import pandas as pd
import glob
import os


DATA_FOLDER = r".\data\raw\research_dataset"

KEY_COLUMNS = [
    "Neem leaf extract dipping",
    "Beeswax coating",
    "Treatments",
    "rep",
]


def verify_records():
    files = glob.glob(os.path.join(DATA_FOLDER, "*.xlsx"))

    reference_keys = None

    print("\n" + "=" * 70)
    print("AGRO LIFE-AI - RESEARCH RECORD VERIFICATION")
    print("=" * 70)

    for file in files:
        filename = os.path.basename(file)

        # Skip files that are not part of the eight research workbooks
        if "Shelflife" not in filename and not any(
            name in filename
            for name in [
                "AA_",
                "Decay_",
                "Marketability_",
                "pH_",
                "TA_",
                "TSS_",
                "WL_",
            ]
        ):
            continue

        df = pd.read_excel(file)

        keys = df[KEY_COLUMNS].astype(str)

        print(f"\n{filename}")
        print(f"Records: {len(df)}")
        print(f"Duplicate experiment keys: {keys.duplicated().sum()}")

        if reference_keys is None:
            reference_keys = keys
            print("Status: REFERENCE DATASET")
        else:
            same_records = keys.reset_index(drop=True).equals(
                reference_keys.reset_index(drop=True)
            )

            if same_records:
                print("Status: MATCHES REFERENCE")
            else:
                print("Status: DOES NOT MATCH REFERENCE")

    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    verify_records()