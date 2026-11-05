"""
AGRO LIFE-AI
User-Based Prediction Workflow

Connects:
User Management
        â†“
Prediction Engine
        â†“
Farmer Recommendation
        â†“
Prediction Database
        â†“
Prediction History
"""

from typing import Optional

from src.database.database_manager import (

    get_farmer,

    get_produce_batch,

    get_batch_quality_records,

    get_batch_storage_records,

    get_batch_research_measurements,

    get_batch_predictions,

    get_produce_by_name,

    save_prediction,

    save_recommendation,

)

from src.prediction.prediction_engine import run_prediction

from src.recommendations.farmer_recommendation import (
    generate_farmer_recommendation,
)

from src.records.history_manager import (
    record_prediction_history,
)

from src.users.user_manager import (
    get_user_profile,
)


def validate_user(user_id: int) -> dict:
    """
    Validate and retrieve a registered user.

    Returns a dictionary containing the user's profile.
    """

    user = get_user_profile(user_id)

    if user is None:
        raise ValueError(f"User ID {user_id} was not found.")

    # Convert database tuple to dictionary
    if isinstance(user, tuple):
        user = {
            "user_id": user[0],
            "full_name": user[1],
            "user_type": user[2],
            "phone": user[3],
            "email": user[4],
            "created_at": user[5],
        }

    if user["user_type"] not in {"farmer", "customer"}:
        raise ValueError(
            "Unsupported user type. Use 'farmer' or 'customer'."
        )

    return user


def run_user_prediction_workflow(
    user_id: int,
    produce_name: str,
    input_method: str,
    current_storage_days: float,
    weight_loss_day4: Optional[float] = None,
    ta_day4: Optional[float] = None,
):
    """
    Run the complete AGRO LIFE-AI prediction workflow
    for a registered user.
    """

    # ---------------------------------------------------------
    # 1. Validate user
    # ---------------------------------------------------------
    user = validate_user(user_id)

    # ---------------------------------------------------------
    # 2. Check produce
    # ---------------------------------------------------------
    produce = get_produce_by_name(produce_name)

    if produce is None:
        raise ValueError(
            f"Produce '{produce_name}' is not registered in AGRO LIFE-AI."
        )

    produce_id = produce[0]

    # ---------------------------------------------------------
    # 3. Run prediction
    # ---------------------------------------------------------
    prediction = run_prediction(
        produce_name=produce_name,
        current_storage_days=current_storage_days,
        input_method=input_method,
        weight_loss_day4=weight_loss_day4,
        ta_day4=ta_day4,
    )

    total_shelf_life = prediction["total_shelf_life_days"]
    remaining_shelf_life = prediction["remaining_shelf_life_days"]
    status = prediction["status"]

    # ---------------------------------------------------------
    # 4. Generate recommendation
    # ---------------------------------------------------------
    recommendation = generate_farmer_recommendation(
        produce_name=produce_name,
        total_shelf_life_days=total_shelf_life,
        current_storage_days=current_storage_days,
    )

    farmer_recommendation = recommendation["recommendation"]
    planning_advice = recommendation["planning_advice"]

    # ---------------------------------------------------------
    # 5. Save prediction
    # ---------------------------------------------------------
    prediction_id = save_prediction(
        produce_id=produce_id,
        input_method=input_method,
        total_shelf_life_days=total_shelf_life,
        current_storage_days=current_storage_days,
        remaining_shelf_life_days=remaining_shelf_life,
        user_id=user_id,
        batch_id=None,
        confidence_note=(
            "Research prototype prediction using the user's "
            "produce input and storage conditions."
        ),
    )

    # ---------------------------------------------------------
    # 6. Save prediction history
    #
    # IMPORTANT:
    # record_prediction_history() does not accept
    # current_storage_days.
    # ---------------------------------------------------------
    history_id = record_prediction_history(
    prediction_id=prediction_id,
    produce_name=produce_name,
    total_shelf_life_days=total_shelf_life,
    remaining_shelf_life_days=remaining_shelf_life,
    status=status,
    user_id=user_id,
)

    return {
        "user_id": user_id,
        "full_name": user["full_name"],
        "user_type": user["user_type"],
        "produce_id": produce_id,
        "produce_name": produce_name,
        "input_method": input_method,
        "current_storage_days": current_storage_days,
        "total_shelf_life_days": total_shelf_life,
        "remaining_shelf_life_days": remaining_shelf_life,
        "status": status,
        "recommendation": farmer_recommendation,
        "planning_advice": planning_advice,
        "prediction_id": prediction_id,
        "history_id": history_id,
    }


def run_farmer_batch_prediction_workflow(
    farmer_id: int,
    batch_id: int,
    input_method: str = "manual",
):
    """
    Run shelf-life prediction using a farmer's
    registered produce batch and available Day-4
    biochemical research measurements.

    Current validated model:
        Tomato -> Day-4 weight loss + titratable acidity

    The prediction engine currently accepts:
        manual
        camera

    Therefore, the research measurements are supplied
    as model inputs while the stored input method remains
    compatible with the prediction engine.
    """

    # ---------------------------------------------------------
    # 1. Get produce batch
    # ---------------------------------------------------------

    batch = get_produce_batch(batch_id)

    if batch is None:
        raise ValueError(
            f"Produce batch ID {batch_id} was not found."
        )

    if batch["farmer_id"] != farmer_id:
        raise ValueError(
            "This produce batch does not belong to the selected farmer."
        )

    produce = get_produce_by_name(
        batch["produce_name"]
        if "produce_name" in batch.keys()
        else None
    )

    # ---------------------------------------------------------
    # 2. Get produce name
    # ---------------------------------------------------------

    produce_id = batch["produce_id"]

    produce_name = None

    if produce is not None:
        try:
            produce_name = produce["name"]
        except (TypeError, KeyError):
            try:
                produce_name = produce[1]
            except (TypeError, IndexError):
                pass

    if not produce_name:
        # Fallback: obtain produce information using the
        # registered produce ID.
        try:
            produce_name = batch["produce_name"]
        except (KeyError, TypeError):
            raise ValueError(
                "Unable to determine the produce type for this batch."
            )

    # ---------------------------------------------------------
    # 3. Get latest storage record
    # ---------------------------------------------------------

    storage_records = get_batch_storage_records(batch_id)

    if not storage_records:
        raise ValueError(
            "No storage record exists for this produce batch. "
            "Please record the storage conditions before "
            "running the shelf-life prediction."
        )

    latest_storage = storage_records[-1]

    current_storage_days = float(
        latest_storage["storage_days"]
    )

    # ---------------------------------------------------------
    # 4. Get Day-4 research measurement
    # ---------------------------------------------------------

    research_records = get_batch_research_measurements(
        batch_id
    )

    day4_records = [
        record
        for record in research_records
        if int(record["day_number"]) == 4
    ]

    if not day4_records:
        raise ValueError(
            "No Day-4 research measurement exists for this "
            "produce batch. Please record the Day-4 weight "
            "loss and titratable acidity before running "
            "the shelf-life prediction."
        )

    # Use the latest Day-4 record.
    latest_day4 = day4_records[-1]

    # ---------------------------------------------------------
    # 5. Extract validated research inputs
    # ---------------------------------------------------------

    weight_loss_day4 = float(
        latest_day4["weight_loss_percent"]
    )

    ta_day4 = float(
        latest_day4["titratable_acidity"]
    )

    # ---------------------------------------------------------
    # 6. Run existing validated prediction engine
    # ---------------------------------------------------------

    # IMPORTANT:
    # run_prediction() currently accepts only:
    #     manual
    #     camera
    #
    # The Tomato model itself uses the Day-4 research
    # measurements supplied below.

    prediction_input_method = input_method

    prediction = run_prediction(
        produce_name=produce_name,
        current_storage_days=current_storage_days,
        input_method=prediction_input_method,
        weight_loss_day4=weight_loss_day4,
        ta_day4=ta_day4,
    )

    total_shelf_life = prediction[
        "total_shelf_life_days"
    ]

    remaining_shelf_life = prediction[
        "remaining_shelf_life_days"
    ]

    status = prediction["status"]

    # ---------------------------------------------------------
    # 7. Generate farmer recommendation
    # ---------------------------------------------------------

    recommendation = generate_farmer_recommendation(
        produce_name=produce_name,
        total_shelf_life_days=total_shelf_life,
        current_storage_days=current_storage_days,
    )

    farmer_recommendation = recommendation[
        "recommendation"
    ]

    planning_advice = recommendation[
        "planning_advice"
    ]

    # ---------------------------------------------------------
    # Resolve the farmer profile to its associated login account.
    farmer_profile = get_farmer(farmer_id)

    if farmer_profile is None:
        raise ValueError(
            f"Farmer profile ID {farmer_id} was not found."
        )

    farmer_user_id = farmer_profile.get("user_id")

    if farmer_user_id is None:
        raise ValueError(
            f"Farmer profile ID {farmer_id} has no linked user account."
        )
    # 8. Save prediction
    # ---------------------------------------------------------

    prediction_id = save_prediction(
        produce_id=produce_id,
        input_method=prediction_input_method,
        total_shelf_life_days=total_shelf_life,
        current_storage_days=current_storage_days,
        remaining_shelf_life_days=remaining_shelf_life,
        user_id=farmer_user_id,
        batch_id=batch_id,
        confidence_note=(
            "Research prototype prediction using Day-4 "
            "weight loss and titratable acidity from "
            "farmer batch research measurements."
        ),
    )

    # ---------------------------------------------------------
    # 9. Save recommendation
    # ---------------------------------------------------------

    save_recommendation(
        prediction_id=prediction_id,
        user_type="FARMER",
        status=status,
        recommendation_text=farmer_recommendation,
    )

    # ---------------------------------------------------------
    # 10. Save prediction history
    # ---------------------------------------------------------

    history_id = record_prediction_history(
        prediction_id=prediction_id,
        produce_name=produce_name,
        total_shelf_life_days=total_shelf_life,
        remaining_shelf_life_days=remaining_shelf_life,
        status=status,
        user_id=farmer_user_id,
    )

    # ---------------------------------------------------------
    # 11. Return complete result
    # ---------------------------------------------------------

    return {
        "farmer_id": farmer_id,
        "batch_id": batch_id,
        "produce_id": produce_id,
        "produce_name": produce_name,
        "input_method": prediction_input_method,
        "current_storage_days": current_storage_days,
        "weight_loss_day4": weight_loss_day4,
        "ta_day4": ta_day4,
        "total_shelf_life_days": total_shelf_life,
        "remaining_shelf_life_days": remaining_shelf_life,
        "status": status,
        "recommendation": farmer_recommendation,
        "planning_advice": planning_advice,
        "prediction_id": prediction_id,
        "history_id": history_id,
    }


def display_workflow_result(result: dict):
    """
    Display the user-based workflow result
    """

    user_id = result.get("user_id", result.get("farmer_id"))
    full_name = result.get("full_name", "Unknown User")
    user_type = result.get("user_type", "farmer")
    recommendation_text = result.get(
        "recommendation",
        result.get("recommendation", "No recommendation available."),
    )
    planning_advice = result.get("planning_advice", "No planning advice.")

    print()
    print("=" * 70)
    print("AGRO LIFE-AI USER-BASED PREDICTION RESULT")
    print("=" * 70)

    print(f"User ID: {user_id}")
    print(f"User Name: {full_name}")
    print(f"User Type: {user_type}")

    print()
    print(f"Produce: {result['produce_name']}")
    print(f"Input Method: {result.get('input_method', 'manual')}")

    print()
    print(
        f"Current Storage Duration: "
        f"{result['current_storage_days']:.2f} days"
    )

    print(
        f"Estimated Total Shelf Life: "
        f"{result['total_shelf_life_days']:.2f} days"
    )

    print(
        f"Estimated Remaining Shelf Life: "
        f"{result['remaining_shelf_life_days']:.2f} days"
    )

    print(f"Status: {result['status']}")

    print()
    print("FARMER RECOMMENDATION")
    print("-" * 70)
    print(recommendation_text)

    print()
    print("PLANNING ADVICE")
    print("-" * 70)
    print(planning_advice)

    print()
    print("DATABASE RECORDS")
    print("-" * 70)
    print(f"Prediction ID: {result['prediction_id']}")
    print(f"History ID: {result['history_id']}")
    print(f"Produce ID: {result['produce_id']}")

    print("=" * 70)

# =============================================================
# TEST
# =============================================================

if __name__ == "__main__":

    print()
    print("AGRO LIFE-AI USER-BASED WORKFLOW TEST")
    print("=" * 70)

    print()
    print("TEST: FARMER PREDICTION WORKFLOW")
    print("-" * 70)

    result = run_user_prediction_workflow(
        user_id=3,
        produce_name="Tomato",
        input_method="manual",
        current_storage_days=10,
        weight_loss_day4=1.43,
        ta_day4=0.74,
    )

    display_workflow_result(result)

    print()
    print("USER-BASED WORKFLOW TEST COMPLETED SUCCESSFULLY")
