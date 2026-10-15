"""
AGRO LIFE-AI
Produce Management Module

Research Prototype

This module manages the produce registry and determines
whether a validated prediction model is currently available
for each produce type.
"""

from src.database.database_manager import (
    get_all_produce,
    get_produce_by_name,
)


def get_produce_registry():
    """
    Return all registered produce in the AGRO LIFE-AI database.
    """

    produce_records = get_all_produce()

    registry = []

    for produce in produce_records:

        registry.append(
            {
                "produce_id": produce[0],
                "produce_name": produce[1],
                "category": produce[2],
                "prediction_available": bool(produce[3]),
            }
        )

    return registry


def get_produce_status(produce_name: str):
    """
    Return the current prediction status of a specific produce.
    """

    produce = get_produce_by_name(produce_name)

    if produce is None:
        return {
            "produce_name": produce_name,
            "registered": False,
            "prediction_available": False,
            "status": "PRODUCE NOT REGISTERED",
        }

    prediction_available = bool(produce[3])

    if prediction_available:
        status = "VALIDATED MODEL AVAILABLE"
    else:
        status = "MODEL DEVELOPMENT"

    return {
        "produce_id": produce[0],
        "produce_name": produce[1],
        "category": produce[2],
        "registered": True,
        "prediction_available": prediction_available,
        "status": status,
    }


def is_prediction_available(produce_name: str) -> bool:
    """
    Check whether a validated prediction model is available.
    """

    produce = get_produce_by_name(produce_name)

    if produce is None:
        return False

    return bool(produce[3])


def display_produce_registry():
    """
    Display the complete produce registry.
    """

    registry = get_produce_registry()

    print()
    print("AGRO LIFE-AI PRODUCE REGISTRY")
    print("=" * 75)

    for item in registry:

        if item["prediction_available"]:
            status_symbol = "✓"
            status_text = "VALIDATED MODEL AVAILABLE"
        else:
            status_symbol = "○"
            status_text = "MODEL DEVELOPMENT"

        print(
            f'{status_symbol} '
            f'{item["produce_name"]:<22} '
            f'{status_text}'
        )

    print("=" * 75)


if __name__ == "__main__":

    print()
    print("AGRO LIFE-AI PRODUCE MANAGEMENT MODULE TEST")
    print("=" * 75)

    display_produce_registry()

    print()
    print("INDIVIDUAL PRODUCE STATUS")
    print("-" * 75)

    test_produce = [
        "Tomato",
        "Mango",
        "Banana",
        "Avocado",
        "Orange",
        "Leafy Vegetables",
    ]

    for produce_name in test_produce:

        status = get_produce_status(produce_name)

        print(
            f'{produce_name:<22} '
            f'{status["status"]}'
        )

    print()
    print("PREDICTION AVAILABILITY CHECK")
    print("-" * 75)

    print(
        "Tomato:",
        is_prediction_available("Tomato")
    )

    print(
        "Mango:",
        is_prediction_available("Mango")
    )

    print("=" * 75)
    print(
        "PRODUCE MANAGEMENT MODULE TEST "
        "COMPLETED SUCCESSFULLY"
    )