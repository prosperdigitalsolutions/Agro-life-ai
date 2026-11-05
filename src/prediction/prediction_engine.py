"""
AGRO LIFE-AI
Prediction Engine
"""

import sys
import math
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

from src.database.database_manager import (
    get_produce_by_name,
)

from src.models.predict_research import (
    predict_shelf_life,
)


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ============================================================
# SUPPORTED INPUT METHODS
# ============================================================

SUPPORTED_INPUT_METHODS = {
    "manual",
    "camera",
    "research",
}


# ============================================================
# PRODUCE PREDICTION CHECK
# ============================================================

def check_prediction_available(produce_name: str) -> bool:
    """
    Check whether AGRO LIFE-AI currently has a validated
    prediction model for the selected produce.

    Returns:
        True  -> Prediction is available.
        False -> Prediction is not currently available.
    """

    produce = get_produce_by_name(produce_name)

    if produce is None:
        return False

    prediction_available = produce[5]

    return bool(prediction_available)


# ============================================================
# REMAINING SHELF-LIFE CALCULATION
# ============================================================

def calculate_remaining_shelf_life(
    total_shelf_life_days: float,
    current_storage_days: float,
) -> float:
    """
    Calculate estimated remaining shelf life.

    Formula:

        Remaining Shelf Life =
        Total Estimated Shelf Life - Current Storage Duration

    The result cannot be negative.
    """

    remaining_days = (
        total_shelf_life_days - current_storage_days
    )

    return max(0.0, remaining_days)


# ============================================================
# SHELF-LIFE STATUS
# ============================================================

def determine_shelf_life_status(
    total_shelf_life_days: float,
    current_storage_days: float,
) -> str:
    """
    Determine the current shelf-life status.

    This is a decision-support classification and does not
    represent a food-safety determination.
    """

    remaining_days = calculate_remaining_shelf_life(
        total_shelf_life_days,
        current_storage_days,
    )

    if current_storage_days >= total_shelf_life_days:
        return "ESTIMATED SHELF-LIFE LIMIT REACHED"

    if remaining_days <= 3:
        return "VERY LIMITED REMAINING SHELF LIFE"

    if remaining_days <= 7:
        return "MARKETING PERIOD APPROACHING"

    if remaining_days <= 14:
        return "MONITOR AND PLAN"

    return "NORMAL MONITORING PERIOD"


# ============================================================
# TOMATO PREDICTION
# ============================================================

def predict_tomato_shelf_life(
    weight_loss_day4: float,
    ta_day4: float,
) -> float:
    """
    Run the validated tomato research model.

    Inputs:
        weight_loss_day4:
            Day-4 weight loss percentage.

        ta_day4:
            Day-4 titratable acidity.

    Returns:
        Estimated total shelf life in days.
    """

    return float(
        predict_shelf_life(
            weight_loss_day4=weight_loss_day4,
            ta_day4=ta_day4,
        )
    )


# ============================================================
# MAIN PREDICTION FUNCTION
# ============================================================

def run_prediction(
    produce_name: str,
    current_storage_days: float,
    input_method: str = "manual",
    weight_loss_day4: Optional[float] = None,
    ta_day4: Optional[float] = None,
):
    """
    Run an AGRO LIFE-AI shelf-life prediction.

    Current implementation supports validated tomato
    prediction using Day-4 research measurements.

    Returns:
        Dictionary containing prediction information.
    """

    # --------------------------------------------------------
    # Validate input method
    # --------------------------------------------------------

    input_method = input_method.lower().strip()

    if input_method not in SUPPORTED_INPUT_METHODS:
        raise ValueError(
            "Input method must be 'manual', 'camera' or 'research'."
        )

    # --------------------------------------------------------
    # Validate storage duration
    # --------------------------------------------------------

    if not math.isfinite(current_storage_days):
        raise ValueError(
            "Current storage duration must be a finite number."
        )

    if current_storage_days < 0:
        raise ValueError(
            "Current storage duration cannot be negative."
        )

    # --------------------------------------------------------
    # Check produce
    # --------------------------------------------------------

    produce = get_produce_by_name(produce_name)

    if produce is None:
        raise ValueError(
            f"Produce '{produce_name}' is not registered "
            "in AGRO LIFE-AI."
        )

    prediction_available = bool(produce[5])

    if not prediction_available:
        raise ValueError(
            f"A validated prediction model is not yet "
            f"available for {produce_name}."
        )

    # --------------------------------------------------------
    # Current tomato model
    # --------------------------------------------------------

    if produce_name.lower() == "tomato":

        # Current research model requires manual quality data.
        if weight_loss_day4 is None:
            raise ValueError(
                "Day-4 weight loss is required for the "
                "current tomato research model."
            )

        if ta_day4 is None:
            raise ValueError(
                "Day-4 titratable acidity is required for "
                "the current tomato research model."
            )

        if not math.isfinite(weight_loss_day4):
            raise ValueError(
                "Day-4 weight loss must be a finite number."
            )

        if not math.isfinite(ta_day4):
            raise ValueError(
                "Day-4 titratable acidity must be a finite number."
            )

        if weight_loss_day4 < 0:
            raise ValueError(
                "Weight loss cannot be negative."
            )

        if ta_day4 < 0:
            raise ValueError(
                "Titratable acidity cannot be negative."
            )

        total_shelf_life = predict_tomato_shelf_life(
            weight_loss_day4=weight_loss_day4,
            ta_day4=ta_day4,
        )

    else:

        raise ValueError(
            f"The registered model for {produce_name} "
            "has not yet been implemented."
        )

    # --------------------------------------------------------
    # Calculate remaining shelf life
    # --------------------------------------------------------

    remaining_shelf_life = calculate_remaining_shelf_life(
        total_shelf_life_days=total_shelf_life,
        current_storage_days=current_storage_days,
    )

    # --------------------------------------------------------
    # Determine status
    # --------------------------------------------------------

    status = determine_shelf_life_status(
        total_shelf_life_days=total_shelf_life,
        current_storage_days=current_storage_days,
    )

    # --------------------------------------------------------
    # Return structured result
    # --------------------------------------------------------

    return {
        "produce_name": produce_name,
        "input_method": input_method,
        "total_shelf_life_days": round(
            total_shelf_life,
            2,
        ),
        "current_storage_days": round(
            current_storage_days,
            2,
        ),
        "remaining_shelf_life_days": round(
            remaining_shelf_life,
            2,
        ),
        "status": status,
        "model_available": True,
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("AGRO LIFE-AI PREDICTION ENGINE TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # Test tomato prediction
    # --------------------------------------------------------

    print()
    print("TEST 1: TOMATO")
    print("-" * 60)

    result = run_prediction(
        produce_name="Tomato",
        current_storage_days=10,
        input_method="manual",
        weight_loss_day4=1.43,
        ta_day4=0.74,
    )

    print(
        f"Produce: "
        f"{result['produce_name']}"
    )

    print(
        f"Input Method: "
        f"{result['input_method']}"
    )

    print(
        f"Estimated Total Shelf Life: "
        f"{result['total_shelf_life_days']} days"
    )

    print(
        f"Current Storage Duration: "
        f"{result['current_storage_days']} days"
    )

    print(
        f"Estimated Remaining Shelf Life: "
        f"{result['remaining_shelf_life_days']} days"
    )

    print(
        f"Status: "
        f"{result['status']}"
    )

    # --------------------------------------------------------
    # Test unsupported produce
    # --------------------------------------------------------

    print()
    print("TEST 2: MANGO")
    print("-" * 60)

    try:

        run_prediction(
            produce_name="Mango",
            current_storage_days=5,
            input_method="manual",
        )

    except ValueError as error:

        print(
            f"Prediction blocked correctly: "
            f"{error}"
        )

    # --------------------------------------------------------
    # Test completed
    # --------------------------------------------------------

    print()
    print("Prediction Engine test completed.")
    print("=" * 60)
