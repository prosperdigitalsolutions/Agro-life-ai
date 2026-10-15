"""
AGRO LIFE-AI
Customer Decision-Support Module

Research Prototype

This module provides estimated shelf-life information to customers
to support produce purchasing decisions.

Important:
- This is decision support, not food-safety certification.
- The current validated model supports Tomato only.
- Camera/computer-vision analysis is not yet implemented.
"""

from typing import Optional

from src.prediction.prediction_engine import run_prediction


def generate_customer_decision_support(
    produce_name: str,
    current_storage_days: float,
    input_method: str = "manual",
    weight_loss_day4: Optional[float] = None,
    ta_day4: Optional[float] = None,
):
    """
    Generate customer-facing decision-support information.

    Parameters
    ----------
    produce_name : str
        Name of the produce.

    current_storage_days : float
        Estimated number of days the produce has already been stored.

    input_method : str
        Current supported methods:
        - manual
        - camera

        Camera is currently a future-development pathway.

    weight_loss_day4 : float, optional
        Day-4 weight loss percentage for the current tomato research model.

    ta_day4 : float, optional
        Day-4 titratable acidity value for the current tomato research model.

    Returns
    -------
    dict
        Customer decision-support result.
    """

    result = run_prediction(
        produce_name=produce_name,
        current_storage_days=current_storage_days,
        input_method=input_method,
        weight_loss_day4=weight_loss_day4,
        ta_day4=ta_day4,
    )

    remaining_days = result["remaining_shelf_life_days"]
    total_days = result["total_shelf_life_days"]
    status = result["status"]

    if remaining_days <= 0:
        decision_message = (
            "The estimated shelf-life limit has been reached. "
            "The prediction should be treated as a warning for further "
            "quality assessment rather than a food-safety determination."
        )

    elif remaining_days <= 3:
        decision_message = (
            "The estimated remaining shelf life is very limited. "
            "Consider the estimate together with the visible condition "
            "and other available quality information before purchasing."
        )

    elif remaining_days <= 7:
        decision_message = (
            "The estimated remaining shelf life is approaching a short "
            "period. Consider how soon the produce will be used after purchase."
        )

    elif remaining_days <= 14:
        decision_message = (
            "The produce has an estimated remaining shelf life within a "
            "moderate period. Consider intended use and storage conditions."
        )

    else:
        decision_message = (
            "The produce has an estimated remaining shelf life beyond "
            "the immediate short-term period under the model assumptions."
        )

    return {
        "produce_name": produce_name,
        "input_method": input_method,
        "estimated_total_shelf_life_days": total_days,
        "current_storage_days": current_storage_days,
        "estimated_remaining_shelf_life_days": remaining_days,
        "status": status,
        "customer_decision_support": decision_message,
        "food_safety_warning": (
            "This system provides research-based shelf-life decision "
            "support and does not certify food safety or freshness."
        ),
        "camera_status": (
            "Camera-based quality assessment is planned for a future "
            "version and is not part of the current validated model."
        ),
    }


def display_customer_result(result):
    """Display customer decision-support results."""

    print()
    print("=" * 70)
    print("AGRO LIFE-AI CUSTOMER DECISION SUPPORT")
    print("=" * 70)

    print(f"Produce: {result['produce_name']}")
    print(f"Input Method: {result['input_method']}")
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

    print(f"Status: {result['status']}")

    print("-" * 70)

    print("CUSTOMER DECISION SUPPORT")
    print(result["customer_decision_support"])

    print()
    print("IMPORTANT")
    print(result["food_safety_warning"])

    print()
    print("CAMERA DEVELOPMENT STATUS")
    print(result["camera_status"])

    print("=" * 70)


if __name__ == "__main__":

    print("=" * 70)
    print("AGRO LIFE-AI CUSTOMER MODULE TEST")
    print("=" * 70)

    result = generate_customer_decision_support(
        produce_name="Tomato",
        current_storage_days=10,
        input_method="manual",
        weight_loss_day4=1.43,
        ta_day4=0.74,
    )

    display_customer_result(result)

    print()
    print("=" * 70)
    print("CUSTOMER MODULE TEST COMPLETED SUCCESSFULLY")
    print("=" * 70)