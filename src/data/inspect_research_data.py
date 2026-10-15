import pandas as pd
import glob
import os


DATA_FOLDER = r".\data\raw\research_dataset"


def inspect_dataset():
    files = glob.glob(os.path.join(DATA_FOLDER, "*.xlsx"))

    print("\n" + "=" * 70)
    print("AGRO LIFE-AI - RESEARCH DATASET INSPECTION")
    print("=" * 70)

    for file in files:
        filename = os.path.basename(file)

        print("\n" + "-" * 70)
        print(f"FILE: {filename}")
        print("-" * 70)

        try:
            excel_file = pd.ExcelFile(file)

            print("Sheets:")
            print(excel_file.sheet_names)

            for sheet in excel_file.sheet_names:
                df = pd.read_excel(file, sheet_name=sheet)

                print(f"\nSheet: {sheet}")
                print(f"Shape: {df.shape}")

                print("\nColumns:")
                for column in df.columns:
                    print(f"  - {column}")

                print("\nFirst 5 rows:")
                print(df.head(5).to_string(index=False))

        except Exception as error:
            print(f"ERROR reading {filename}: {error}")

    print("\n" + "=" * 70)
    print("INSPECTION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    inspect_dataset()