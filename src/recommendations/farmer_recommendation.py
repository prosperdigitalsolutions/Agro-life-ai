"""
AGRO LIFE-AI
Farmer Recommendation Engine

Provides decision-support recommendations based on
estimated remaining shelf life.

Important:
These recommendations are not food-safety determinations.
They are intended to support storage and marketing planning.
"""


# ============================================================
# RECOMMENDATION ENGINE
# ============================================================

def generate_farmer_recommendation(
    produce_name: str,
    total_shelf_life_days: float,
    current_storage_days: float,
):
    """
    Generate a farmer-oriented recommendation.

    Parameters:
        produce_name:
            Name of the produce.

        total_shelf_life_days:
            Estimated total shelf life.

        current_storage_days:
            Number of days the produce has already been stored.

    Returns:
        Dictionary containing:
            remaining shelf life,
            status,
            recommendation,
            planning advice.
    """

    # --------------------------------------------------------
    # Validate inputs
    # --------------------------------------------------------

    if total_shelf_life_days < 0:
        raise ValueError(
            "Total shelf life cannot be negative."
        )

    if current_storage_days < 0:
        raise ValueError(
            "Current storage duration cannot be negative."
        )

    # --------------------------------------------------------
    # Calculate remaining shelf life
    # --------------------------------------------------------

    remaining_days = max(
        0.0,
        total_shelf_life_days - current_storage_days,
    )

    # --------------------------------------------------------
    # Determine status and recommendation
    # --------------------------------------------------------

    if current_storage_days >= total_shelf_life_days:

        status = "ESTIMATED SHELF-LIFE LIMIT REACHED"

        recommendation = (
            f"The estimated shelf-life limit for {produce_name} "
            "has been reached. Prioritise appropriate handling "
            "and marketing decisions based on the current "
            "condition of the produce."
        )

        planning_advice = (
            "Avoid relying on extended storage based only on "
            "this estimate. Inspect the produce condition and "
            "consider appropriate next steps."
        )

    elif remaining_days <= 3:

        status = "VERY LIMITED REMAINING SHELF LIFE"

        recommendation = (
            f"{produce_name} has an estimated remaining "
            "shelf life of only a few days. Prioritise "
            "marketing, distribution, or appropriate "
            "handling while continuing to monitor quality."
        )

        planning_advice = (
            "Plan immediate marketing or distribution and "
            "continue monitoring the physical condition of "
            "the produce."
        )

    elif remaining_days <= 7:

        status = "MARKETING PERIOD APPROACHING"

        recommendation = (
            f"The estimated remaining shelf life of "
            f"{produce_name} is approximately "
            f"{remaining_days:.2f} days. Begin planning "
            "marketing or distribution."
        )

        planning_advice = (
            "Review available markets and plan transportation "
            "or distribution so that unnecessary storage "
            "time can be reduced."
        )

    elif remaining_days <= 14:

        status = "MONITOR AND PLAN"

        recommendation = (
            f"{produce_name} has an estimated remaining "
            f"shelf life of approximately "
            f"{remaining_days:.2f} days. Continue monitoring "
            "quality and begin planning future marketing."
        )

        planning_advice = (
            "Maintain appropriate storage conditions and "
            "monitor changes in the physical quality of "
            "the produce."
        )

    else:

        status = "NORMAL MONITORING PERIOD"

        recommendation = (
            f"{produce_name} has an estimated remaining "
            f"shelf life of approximately "
            f"{remaining_days:.2f} days. Continue appropriate "
            "storage and routine quality monitoring."
        )

        planning_advice = (
            "Continue monitoring the produce and use the "
            "estimate to support future storage and "
            "marketing planning."
        )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "produce_name": produce_name,
        "total_shelf_life_days": round(
            total_shelf_life_days,
            2,
        ),
        "current_storage_days": round(
            current_storage_days,
            2,
        ),
        "remaining_shelf_life_days": round(
            remaining_days,
            2,
        ),
        "status": status,
        "recommendation": recommendation,
        "planning_advice": planning_advice,
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("AGRO LIFE-AI FARMER RECOMMENDATION TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # Test 1
    # --------------------------------------------------------

    print()
    print("TEST 1: NORMAL MONITORING PERIOD")
    print("-" * 60)

    result = generate_farmer_recommendation(
        produce_name="Tomato",
        total_shelf_life_days=28.69,
        current_storage_days=10,
    )

    print(
        f"Produce: "
        f"{result['produce_name']}"
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

    print()
    print("Farmer Recommendation:")
    print(result["recommendation"])

    print()
    print("Planning Advice:")
    print(result["planning_advice"])

    # --------------------------------------------------------
    # Test 2
    # --------------------------------------------------------

    print()
    print("TEST 2: VERY LIMITED REMAINING SHELF LIFE")
    print("-" * 60)

    result = generate_farmer_recommendation(
        produce_name="Tomato",
        total_shelf_life_days=28.69,
        current_storage_days=27,
    )

    print(
        f"Remaining Shelf Life: "
        f"{result['remaining_shelf_life_days']} days"
    )

    print(
        f"Status: "
        f"{result['status']}"
    )

    print()
    print("Farmer Recommendation:")
    print(result["recommendation"])

    # --------------------------------------------------------
    # Test 3
    # --------------------------------------------------------

    print()
    print("TEST 3: SHELF-LIFE LIMIT REACHED")
    print("-" * 60)

    result = generate_farmer_recommendation(
        produce_name="Tomato",
        total_shelf_life_days=28.69,
        current_storage_days=30,
    )

    print(
        f"Remaining Shelf Life: "
        f"{result['remaining_shelf_life_days']} days"
    )

    print(
        f"Status: "
        f"{result['status']}"
    )

    print()
    print("Farmer Recommendation:")
    print(result["recommendation"])

    print()
    print("Recommendation Engine test completed.")
    print("=" * 60)