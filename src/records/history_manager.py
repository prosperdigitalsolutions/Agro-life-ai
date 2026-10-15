"""
AGRO LIFE-AI
Historical Records Manager

Manages historical shelf-life prediction records
stored in the AGRO LIFE-AI SQLite database.
"""

import sys
from pathlib import Path
from typing import Optional


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# DATABASE MANAGER
# ============================================================

from src.database.database_manager import (
    save_history,
    get_history,
)


# ============================================================
# SAVE PREDICTION HISTORY
# ============================================================

def record_prediction_history(
    prediction_id: int,
    produce_name: str,
    total_shelf_life_days: float,
    remaining_shelf_life_days: float,
    status: str,
    user_id: Optional[int] = None,
):
    """
    Save a prediction result into historical records.

    Returns:
        int: Newly created history record ID.
    """

    if prediction_id <= 0:
        raise ValueError(
            "Prediction ID must be a positive integer."
        )

    if not produce_name.strip():
        raise ValueError(
            "Produce name cannot be empty."
        )

    if total_shelf_life_days < 0:
        raise ValueError(
            "Total shelf life cannot be negative."
        )

    if remaining_shelf_life_days < 0:
        raise ValueError(
            "Remaining shelf life cannot be negative."
        )

    history_id = save_history(
        prediction_id=prediction_id,
        produce_name=produce_name,
        total_shelf_life_days=total_shelf_life_days,
        remaining_shelf_life_days=remaining_shelf_life_days,
        status=status,
        user_id=user_id,
    )

    return history_id


# ============================================================
# GET HISTORY
# ============================================================

def get_prediction_history(
    user_id: Optional[int] = None,
):
    """
    Retrieve prediction history.

    If user_id is supplied, only that user's history
    is returned.

    Otherwise, all history records are returned.
    """

    return get_history(user_id=user_id)


# ============================================================
# COUNT HISTORY
# ============================================================

def count_prediction_history(
    user_id: Optional[int] = None,
) -> int:
    """
    Count historical prediction records.
    """

    records = get_prediction_history(
        user_id=user_id
    )

    return len(records)


# ============================================================
# DISPLAY HISTORY
# ============================================================

def display_prediction_history(
    user_id: Optional[int] = None,
):
    """
    Display historical prediction records in a
    readable format.
    """

    records = get_prediction_history(
        user_id=user_id
    )

    print()
    print("=" * 75)
    print("AGRO LIFE-AI PREDICTION HISTORY")
    print("=" * 75)

    if not records:

        print()
        print("No historical prediction records found.")
        print("=" * 75)

        return

    print()

    for record in records:

        (
            history_id,
            record_user_id,
            prediction_id,
            produce_name,
            total_shelf_life,
            remaining_shelf_life,
            status,
            recorded_at,
        ) = record

        print(
            f"History ID: {history_id}"
        )

        print(
            f"User ID: {record_user_id}"
        )

        print(
            f"Prediction ID: {prediction_id}"
        )

        print(
            f"Produce: {produce_name}"
        )

        print(
            f"Estimated Total Shelf Life: "
            f"{total_shelf_life} days"
        )

        print(
            f"Estimated Remaining Shelf Life: "
            f"{remaining_shelf_life} days"
        )

        print(
            f"Status: {status}"
        )

        print(
            f"Recorded At: {recorded_at}"
        )

        print("-" * 75)

    print(
        f"Total Records: {len(records)}"
    )

    print("=" * 75)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("AGRO LIFE-AI HISTORY MANAGER TEST")
    print("=" * 70)

    from src.database.database_manager import save_prediction

    print("\nCreating test prediction record...")
    print("-" * 70)

    # Create a real prediction record first.
    prediction_id = save_prediction(
        produce_id=1,
        input_method="manual",
        total_shelf_life_days=28.69,
        current_storage_days=10,
        remaining_shelf_life_days=18.69,
        user_id=None,
        confidence_note=(
            "Research prototype prediction using Day-4 "
            "Weight Loss and Titratable Acidity."
        ),
    )

    print("Prediction created successfully.")
    print(f"Prediction ID: {prediction_id}")

    print("\nCreating historical record...")
    print("-" * 70)

    history_id = record_prediction_history(
        prediction_id=prediction_id,
        produce_name="Tomato",
        total_shelf_life_days=28.69,
        remaining_shelf_life_days=18.69,
        status="NORMAL MONITORING PERIOD",
        user_id=None,
    )

    print("History record created successfully.")
    print(f"History ID: {history_id}")

    print("\nChecking historical record count...")
    print("-" * 70)

    total_records = count_prediction_history()

    print(f"Total historical records: {total_records}")

    print("\nDisplaying historical records...")
    print("-" * 70)

    display_prediction_history()

    print("\n" + "=" * 70)
    print("HISTORY MANAGER TEST COMPLETED SUCCESSFULLY")
    print("=" * 70)