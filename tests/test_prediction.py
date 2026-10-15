"""
AGRO LIFE-AI
System Testing and Validation

Biochemical Decay & Shelf-Life Predictor
DMI St. Eugene University
BSc Computer Science - Mini Project
"""

from pathlib import Path
import sys

import pandas as pd


# ---------------------------------------------------------
# PROJECT PATH
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from models.predict import (
    load_model,
    prepare_input,
    predict_shelf_life,
)


# ---------------------------------------------------------
# TEST CASES
# ---------------------------------------------------------

TEST_CASES = [
    {
        "id": "T01",
        "produce": "Tomato",
        "weight": 1000,
        "temperature": 28,
        "humidity": 78,
        "storage": 2,
        "weight_loss": 4.0,
        "quality": 8,
    },
    {
        "id": "T02",
        "produce": "Mango",
        "weight": 1000,
        "temperature": 27,
        "humidity": 75,
        "storage": 3,
        "weight_loss": 5.2,
        "quality": 8,
    },
    {
        "id": "T03",
        "produce": "Banana",
        "weight": 1000,
        "temperature": 26,
        "humidity": 70,
        "storage": 3,
        "weight_loss": 5.5,
        "quality": 8,
    },
    {
        "id": "T04",
        "produce": "Tomato",
        "weight": 1000,
        "temperature": 32,
        "humidity": 90,
        "storage": 4,
        "weight_loss": 13.0,
        "quality": 5,
    },
    {
        "id": "T05",
        "produce": "Mango",
        "weight": 1000,
        "temperature": 24,
        "humidity": 70,
        "storage": 1,
        "weight_loss": 1.8,
        "quality": 9,
    },
]


# ---------------------------------------------------------
# RUN TESTS
# ---------------------------------------------------------

def run_tests():

    print("=" * 70)
    print("AGRO LIFE-AI - SYSTEM TESTING")
    print("=" * 70)

    print("\nLoading trained model...")

    try:

        model = load_model()

        print("Model loaded successfully.")

    except Exception as error:

        print("MODEL LOADING FAILED")
        print(error)

        return


    results = []


    print("\nRunning prediction tests...")
    print("-" * 70)


    for test in TEST_CASES:

        try:

            input_data = prepare_input(
                test["produce"],
                test["weight"],
                test["temperature"],
                test["humidity"],
                test["storage"],
                test["weight_loss"],
                test["quality"],
            )

            prediction = predict_shelf_life(
                model,
                input_data
            )

            prediction = float(prediction)

            status = "PASS"

            results.append(
                {
                    "Test ID": test["id"],
                    "Produce": test["produce"],
                    "Temperature": test["temperature"],
                    "Humidity": test["humidity"],
                    "Storage Days": test["storage"],
                    "Weight Loss": test["weight_loss"],
                    "Quality Score": test["quality"],
                    "Predicted Shelf Life": round(
                        prediction,
                        2
                    ),
                    "Status": status,
                }
            )

            print(
                f'{test["id"]} | '
                f'{test["produce"]} | '
                f'Prediction = {prediction:.2f} days | '
                f'{status}'
            )

        except Exception as error:

            results.append(
                {
                    "Test ID": test["id"],
                    "Produce": test["produce"],
                    "Temperature": test["temperature"],
                    "Humidity": test["humidity"],
                    "Storage Days": test["storage"],
                    "Weight Loss": test["weight_loss"],
                    "Quality Score": test["quality"],
                    "Predicted Shelf Life": "",
                    "Status": "FAIL",
                }
            )

            print(
                f'{test["id"]} | '
                f'{test["produce"]} | '
                f'FAILED | '
                f'{error}'
            )


    # -----------------------------------------------------
    # SAVE TEST RESULTS
    # -----------------------------------------------------

    results_directory = (
        PROJECT_ROOT
        / "results"
        / "reports"
    )

    results_directory.mkdir(
        parents=True,
        exist_ok=True
    )


    results_file = (
        results_directory
        / "system_testing_results.csv"
    )


    results_dataframe = pd.DataFrame(
        results
    )


    results_dataframe.to_csv(
        results_file,
        index=False
    )


    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    total_tests = len(results)

    passed_tests = sum(
        1
        for result in results
        if result["Status"] == "PASS"
    )

    failed_tests = total_tests - passed_tests


    print("\n" + "=" * 70)
    print("SYSTEM TESTING SUMMARY")
    print("=" * 70)

    print("\nTotal Tests :", total_tests)
    print("Passed Tests:", passed_tests)
    print("Failed Tests:", failed_tests)

    print(
        f"\nTest Results Saved:\n{results_file}"
    )


    if failed_tests == 0:

        print("\nSYSTEM TESTING STATUS: PASS")

    else:

        print("\nSYSTEM TESTING STATUS: REVIEW REQUIRED")


    print("=" * 70)


if __name__ == "__main__":
    run_tests()