"""
AGRO LIFE-AI
Computer Vision History Manager

Part 15

Purpose:
Manage saved computer-vision prediction records produced
by the customer camera assessment module.

Important:
These records represent visual Fresh/Rotten classification.
They are NOT shelf-life predictions and do NOT certify food safety.
"""

from pathlib import Path
import json
from typing import Optional


# ----------------------------------------------------------------------
# PROJECT PATHS
# ----------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CV_RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "predictions"
    / "computer_vision"
)


# ----------------------------------------------------------------------
# LOAD SAVED CV RECORDS
# ----------------------------------------------------------------------

def load_cv_prediction_records() -> list[dict]:
    """
    Load all managed computer-vision prediction JSON records.

    Returns:
        A list of prediction dictionaries.
    """

    if not CV_RESULTS_DIR.exists():
        return []

    records = []

    for json_file in sorted(
        CV_RESULTS_DIR.glob("*_managed_prediction.json"),
        reverse=True,
    ):
        try:
            with open(
                json_file,
                "r",
                encoding="utf-8",
            ) as file:
                record = json.load(file)

            record["record_file"] = str(json_file)

            records.append(record)

        except (json.JSONDecodeError, OSError):
            # Ignore damaged or unreadable records
            continue

    return records


# ----------------------------------------------------------------------
# GET CV HISTORY
# ----------------------------------------------------------------------

def get_cv_history(
    produce_name: Optional[str] = None,
) -> list[dict]:
    """
    Return computer-vision prediction history.

    Args:
        produce_name:
            Optional produce name used to filter records.

    Returns:
        List of matching CV prediction records.
    """

    records = load_cv_prediction_records()

    if produce_name is None:
        return records

    produce_name = produce_name.strip().lower()

    filtered_records = [
        record
        for record in records
        if record.get("produce", "").strip().lower()
        == produce_name
    ]

    return filtered_records


# ----------------------------------------------------------------------
# COUNT RECORDS
# ----------------------------------------------------------------------

def count_cv_history(
    produce_name: Optional[str] = None,
) -> int:
    """
    Count saved computer-vision prediction records.
    """

    return len(get_cv_history(produce_name))


# ----------------------------------------------------------------------
# DISPLAY HISTORY
# ----------------------------------------------------------------------

def display_cv_history(
    produce_name: Optional[str] = None,
) -> None:
    """
    Display computer-vision prediction history
    in a readable terminal format.
    """

    records = get_cv_history(produce_name)

    print("=" * 78)
    print("AGRO LIFE-AI")
    print("COMPUTER VISION PREDICTION HISTORY")
    print("=" * 78)

    if not records:
        print()
        print("No computer-vision prediction records found.")
        print("=" * 78)
        return

    print()
    print(f"TOTAL RECORDS: {len(records)}")
    print()

    for number, record in enumerate(records, start=1):

        print("-" * 78)

        print(f"Record {number}")

        print(
            f"Date/Time: "
            f"{record.get('prediction_timestamp', 'Not available')}"
        )

        print(
            f"Produce: "
            f"{record.get('produce', 'Not available')}"
        )

        print(
            f"Image: "
            f"{record.get('image_filename', 'Not available')}"
        )

        print(
            f"Visual Classification: "
            f"{record.get('predicted_class', 'Not available')}"
        )

        probability = record.get("model_probability")

        if probability is not None:
            print(
                f"Model Probability: "
                f"{probability * 100:.2f}%"
            )
        else:
            print("Model Probability: Not available")

        print(
            f"Classification Type: "
            f"{record.get('classification_type', 'Not available')}"
        )

        print(
            f"Shelf-Life Prediction: "
            f"{record.get('shelf_life_prediction', False)}"
        )

        print(
            f"Food Safety Certification: "
            f"{record.get('food_safety_certification', False)}"
        )

        print(
            f"Four-Stage Decay Prediction: "
            f"{record.get('four_stage_decay_prediction', False)}"
        )

    print("-" * 78)

    print()
    print(
        "Research Note:"
    )
    print(
        "These records represent visual Fresh/Rotten "
        "classification using the current tomato "
        "computer-vision model."
    )

    print(
        "They are not shelf-life predictions and do not "
        "certify food safety."
    )

    print("=" * 78)


# ----------------------------------------------------------------------
# GET LATEST RECORD
# ----------------------------------------------------------------------

def get_latest_cv_prediction(
    produce_name: Optional[str] = None,
) -> Optional[dict]:
    """
    Return the most recent computer-vision prediction.
    """

    records = get_cv_history(produce_name)

    if not records:
        return None

    return records[0]

def delete_cv_prediction_record(record: dict) -> dict:
    """
    Delete a managed computer-vision prediction record
    and its associated captured image.

    The deletion is permanent from the working project
    directory, so the dashboard must request confirmation
    before calling this function.
    """

    result = {
        "success": False,
        "json_deleted": False,
        "image_deleted": False,
        "message": "",
    }

    record_file = record.get(
        "managed_prediction_file"
    )

    image_path = record.get(
        "image_path"
    )

    errors = []

    # ------------------------------------------------------
    # Delete managed JSON record
    # ------------------------------------------------------

    if record_file:

        record_file_path = Path(record_file)

        if record_file_path.exists():

            try:
                record_file_path.unlink()
                result["json_deleted"] = True

            except OSError as exc:

                errors.append(
                    f"Could not delete prediction record: {exc}"
                )

    # ------------------------------------------------------
    # Delete captured image
    # ------------------------------------------------------

    if image_path:

        image_file_path = Path(image_path)

        if image_file_path.exists():

            try:
                image_file_path.unlink()
                result["image_deleted"] = True

            except OSError as exc:

                errors.append(
                    f"Could not delete captured image: {exc}"
                )

    # ------------------------------------------------------
    # Final result
    # ------------------------------------------------------

    if errors:

        result["message"] = " ".join(errors)

    else:

        result["success"] = True

        result["message"] = (
            "Computer-vision assessment record and "
            "associated captured image were deleted."
        )

    return result

# ----------------------------------------------------------------------
# MODULE TEST
# ----------------------------------------------------------------------

if __name__ == "__main__":

    print()
    print("AGRO LIFE-AI")
    print("PART 15 - CV HISTORY MANAGER TEST")
    print("=" * 78)

    records = load_cv_prediction_records()

    print()
    print(
        f"Managed CV prediction records found: {len(records)}"
    )

    print()

    if records:

        latest = get_latest_cv_prediction()

        print("LATEST CV PREDICTION")
        print("-" * 78)

        print(
            f"Produce: "
            f"{latest.get('produce')}"
        )

        print(
            f"Classification: "
            f"{latest.get('predicted_class')}"
        )

        probability = latest.get("model_probability")

        if probability is not None:
            print(
                f"Model Probability: "
                f"{probability * 100:.2f}%"
            )

        print(
            f"Image: "
            f"{latest.get('image_filename')}"
        )

        print(
            f"Record File: "
            f"{latest.get('record_file')}"
        )

    else:

        print(
            "No managed computer-vision prediction "
            "records are currently available."
        )

    print()
    display_cv_history()

    print()
    print("=" * 78)
    print("PART 15 CV HISTORY MANAGER TEST COMPLETED")
    print("=" * 78)

def delete_cv_prediction_record(record):
    """
    Delete a CV prediction JSON record and its associated
    captured image.
    """

    json_deleted = False
    image_deleted = False

    json_path = record.get("managed_prediction_file")
    image_path = record.get("image_path")

    # Delete managed JSON record
    if json_path:
        json_file = Path(json_path)

        if json_file.exists():
            json_file.unlink()
            json_deleted = True

    # Delete captured image
    if image_path:
        image_file = Path(image_path)

        if image_file.exists():
            image_file.unlink()
            image_deleted = True

    success = json_deleted or image_deleted

    if success:
        message = "CV prediction record deleted successfully."
    else:
        message = "No matching CV prediction files were found."

    return {
        "success": success,
        "json_deleted": json_deleted,
        "image_deleted": image_deleted,
        "message": message,
    }
def delete_cv_prediction_record(record):
    """
    Delete a computer-vision assessment record and its associated
    captured image.

    The function supports records where managed_prediction_file
    is missing by locating the managed JSON using the captured
    image filename.
    """

    from pathlib import Path

    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    json_deleted = False
    image_deleted = False

    # ---------------------------------------------------------
    # Resolve image path
    # ---------------------------------------------------------
    image_value = record.get("image_path")

    if image_value:
        image_path = Path(image_value)

        if not image_path.is_absolute():
            image_path = PROJECT_ROOT / image_path
    else:
        image_path = None

    # ---------------------------------------------------------
    # Resolve managed JSON path
    # ---------------------------------------------------------
    json_value = record.get("managed_prediction_file")

    if json_value:
        json_path = Path(json_value)

        if not json_path.is_absolute():
            json_path = PROJECT_ROOT / json_path
    else:
        json_path = None

    # ---------------------------------------------------------
    # If JSON path is missing, locate it using image filename
    # ---------------------------------------------------------
    if json_path is None or not json_path.exists():

        if image_path is not None:
            image_filename = image_path.name

            prediction_directory = (
                PROJECT_ROOT
                / "results"
                / "predictions"
                / "computer_vision"
            )

            candidate_json = (
                prediction_directory
                / f"{Path(image_filename).stem}_managed_prediction.json"
            )

            if candidate_json.exists():
                json_path = candidate_json

    # ---------------------------------------------------------
    # Delete managed JSON
    # ---------------------------------------------------------
    if json_path is not None and json_path.exists():
        try:
            json_path.unlink()
            json_deleted = True
        except Exception as error:
            return {
                "success": False,
                "json_deleted": False,
                "image_deleted": False,
                "message": f"Could not delete assessment JSON: {error}",
            }

    # ---------------------------------------------------------
    # Delete captured image
    # ---------------------------------------------------------
    if image_path is not None and image_path.exists():
        try:
            image_path.unlink()
            image_deleted = True
        except Exception as error:
            return {
                "success": False,
                "json_deleted": json_deleted,
                "image_deleted": False,
                "message": f"Could not delete captured image: {error}",
            }

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------
    if json_deleted or image_deleted:

        deleted_items = []

        if json_deleted:
            deleted_items.append("managed JSON record")

        if image_deleted:
            deleted_items.append("captured image")

        return {
            "success": True,
            "json_deleted": json_deleted,
            "image_deleted": image_deleted,
            "message": (
                "Assessment deleted successfully: "
                + " and ".join(deleted_items)
                + "."
            ),
        }

    return {
        "success": False,
        "json_deleted": False,
        "image_deleted": False,
        "message": "The assessment files could not be found.",
    }