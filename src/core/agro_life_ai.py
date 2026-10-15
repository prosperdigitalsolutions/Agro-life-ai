"""
AGRO LIFE-AI
Main Application Core

Integrated workflow:

1. Produce selection
2. Shelf-life prediction
3. Remaining shelf-life calculation
4. Farmer recommendation
5. Save prediction
6. Save historical record
7. Display final result

Current research implementation:
- Tomato
- Manual quality input
- Day-4 Weight Loss
- Day-4 Titratable Acidity
- Machine-learning shelf-life prediction

Camera-based prediction and additional produce models
will be added after appropriate data and models are
available and validated.
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
# AGRO LIFE-AI MODULES
# ============================================================

from src.prediction.prediction_engine import run_prediction

from src.database.database_manager import (
    get_produce_by_name,
    save_prediction,
)

from src.recommendations.farmer_recommendation import (
    generate_farmer_recommendation,
)

from src.records.history_manager import (
    record_prediction_history,
)


# ============================================================
# MAIN AGRO LIFE-AI WORKFLOW
# ============================================================

def run_agro_life_ai(
    produce_name: str,
    input_method: str,
    current_storage_days: float,
    weight_loss_day4: Optional[float] = None,
    ta_day4: Optional[float] = None,
    user_id: Optional[int] = None,
):
    """
    Run the complete AGRO LIFE-AI workflow.

    Returns:
        dict: Complete prediction, recommendation,
        database and history information.
    """

    # --------------------------------------------------------
    # Validate storage duration
    # --------------------------------------------------------

    if current_storage_days < 0:
        raise ValueError(
            "Current storage duration cannot be negative."
        )

    # --------------------------------------------------------
    # Get produce information
    # --------------------------------------------------------

    produce = get_produce_by_name(produce_name)

    if produce is None:
        raise ValueError(
            f"Produce '{produce_name}' is not registered "
            "in AGRO LIFE-AI."
        )

    produce_id = produce[0]

    # --------------------------------------------------------
    # Run Prediction Engine
    # --------------------------------------------------------

    prediction_result = run_prediction(
        produce_name=produce_name,
        current_storage_days=current_storage_days,
        input_method=input_method,
        weight_loss_day4=weight_loss_day4,
        ta_day4=ta_day4,
    )

    # --------------------------------------------------------
    # Extract prediction
    # --------------------------------------------------------

    total_shelf_life = prediction_result[
        "total_shelf_life_days"
    ]

    # --------------------------------------------------------
    # Generate Farmer Recommendation
    #
    # The Recommendation Engine calculates:
    # - remaining shelf life
    # - status
    # - recommendation
    # - planning advice
    # --------------------------------------------------------

    recommendation_result = generate_farmer_recommendation(
        produce_name=produce_name,
        total_shelf_life_days=total_shelf_life,
        current_storage_days=current_storage_days,
    )

    remaining_shelf_life = recommendation_result[
        "remaining_shelf_life_days"
    ]

    status = recommendation_result[
        "status"
    ]

    recommendation = recommendation_result[
        "recommendation"
    ]

    planning_advice = recommendation_result[
        "planning_advice"
    ]

    # --------------------------------------------------------
    # Save Prediction
    # --------------------------------------------------------

    confidence_note = (
        "Research prototype prediction using Day-4 "
        "Weight Loss and Titratable Acidity."
    )

    prediction_id = save_prediction(
        produce_id=produce_id,
        input_method=input_method,
        total_shelf_life_days=total_shelf_life,
        current_storage_days=current_storage_days,
        remaining_shelf_life_days=remaining_shelf_life,
        user_id=user_id,
        confidence_note=confidence_note,
    )

    # --------------------------------------------------------
    # Save Historical Record
    # --------------------------------------------------------

    history_id = record_prediction_history(
        prediction_id=prediction_id,
        produce_name=produce_name,
        total_shelf_life_days=total_shelf_life,
        remaining_shelf_life_days=remaining_shelf_life,
        status=status,
        user_id=user_id,
    )

    # --------------------------------------------------------
    # Return complete result
    # --------------------------------------------------------

    return {
        "prediction_id": prediction_id,
        "history_id": history_id,
        "produce_id": produce_id,
        "produce_name": produce_name,
        "input_method": input_method,
        "current_storage_days": current_storage_days,
        "estimated_total_shelf_life_days": total_shelf_life,
        "estimated_remaining_shelf_life_days": remaining_shelf_life,
        "status": status,
        "recommendation": recommendation,
        "planning_advice": planning_advice,
    }


# ============================================================
# DISPLAY RESULT
# ============================================================

def display_result(result: dict):
    """
    Display a complete AGRO LIFE-AI prediction result.
    """

    print()
    print("=" * 70)
    print("AGRO LIFE-AI PREDICTION RESULT")
    print("=" * 70)

    print(
        f"Produce: "
        f"{result['produce_name']}"
    )

    print(
        f"Input Method: "
        f"{result['input_method']}"
    )

    print("-" * 70)

    print(
        "Estimated Total Shelf Life: "
        f"{result['estimated_total_shelf_life_days']:.2f} days"
    )

    print(
        "Current Storage Duration: "
        f"{result['current_storage_days']:.2f} days"
    )

    print(
        "Estimated Remaining Shelf Life: "
        f"{result['estimated_remaining_shelf_life_days']:.2f} days"
    )

    print(
        f"Status: "
        f"{result['status']}"
    )

    print("-" * 70)

    print("FARMER RECOMMENDATION")
    print(
        result["recommendation"]
    )

    print()
    print("PLANNING ADVICE")
    print(
        result["planning_advice"]
    )

    print("-" * 70)

    print(
        f"Prediction ID: "
        f"{result['prediction_id']}"
    )

    print(
        f"History ID: "
        f"{result['history_id']}"
    )

    print(
        f"Produce ID: "
        f"{result['produce_id']}"
    )

    print("=" * 70)


# ============================================================
# INTEGRATED WORKFLOW TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("AGRO LIFE-AI INTEGRATED WORKFLOW TEST")
    print("=" * 70)

    print()
    print("Running Tomato research prediction...")
    print("-" * 70)

    result = run_agro_life_ai(
        produce_name="Tomato",
        input_method="manual",
        current_storage_days=10,
        weight_loss_day4=1.43,
        ta_day4=0.74,
        user_id=None,
    )

    display_result(result)

    print()
    print("=" * 70)
    print("INTEGRATED WORKFLOW TEST COMPLETED SUCCESSFULLY")
    print("=" * 70)