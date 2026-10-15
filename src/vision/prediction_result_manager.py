"""
AGRO LIFE-AI
Computer Vision Prediction Result Manager

Research Prototype

This module manages individual tomato image classification
results produced by the Fresh/Rotten computer vision model.

IMPORTANT:
- This module records visual classification results only.
- It does not predict shelf life.
- It does not calculate remaining shelf life.
- It does not certify food safety.
- It does not create four-stage decay labels.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PREDICTION_DIRECTORY = (
    PROJECT_ROOT
    / "results"
    / "predictions"
    / "computer_vision"
)

PREDICTION_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True
)


SUPPORTED_CLASSES = {
    "Fresh",
    "Rotten",
}


def validate_prediction_class(predicted_class: str) -> bool:
    """
    Validate the original classifier class.
    """

    if predicted_class not in SUPPORTED_CLASSES:
        raise ValueError(
            "Invalid prediction class. "
            "Expected 'Fresh' or 'Rotten'."
        )

    return True


def create_prediction_record(
    image_path: str,
    predicted_class: str,
    probability: Optional[float] = None,
    decision_support: Optional[str] = None,
    research_warning: Optional[str] = None,
) -> dict:
    """
    Create a structured computer vision prediction record.
    """

    validate_prediction_class(predicted_class)

    image_file = Path(image_path)

    if not image_file.exists():
        raise FileNotFoundError(
            f"Image file not found: {image_file}"
        )

    if probability is not None:

        if probability < 0 or probability > 1:
            raise ValueError(
                "Probability must be between 0 and 1."
            )

    record = {
        "system": "AGRO LIFE-AI",
        "module": "Computer Vision Prediction",
        "research_prototype": True,
        "prediction_timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
        "produce": "Tomato",
        "image_filename": image_file.name,
        "image_path": str(image_file),
        "predicted_class": predicted_class,
        "model_probability": (
            round(probability, 4)
            if probability is not None
            else None
        ),
        "classification_type": "Binary Fresh/Rotten",
        "decision_support": decision_support,
        "research_warning": research_warning,   
        "shelf_life_prediction": False,
        "food_safety_certification": False,
        "four_stage_decay_prediction": False,
        "research_note": (
            "This result represents visual classification "
            "using the original Fresh/Rotten dataset classes. "
            "It is not a shelf-life prediction and does not "
            "certify food safety."
        ),
    }

    return record


def save_prediction_record(record: dict) -> Path:
    """
    Save a prediction record as a JSON file.
    """

    image_filename = record.get(
        "image_filename",
        "tomato_image"
    )

    safe_name = Path(image_filename).stem

    output_file = (
        PREDICTION_DIRECTORY
        / f"{safe_name}_managed_prediction.json"
    )

    with output_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            record,
            file,
            indent=4,
        )

    return output_file


def load_prediction_record(
    prediction_file: str | Path
) -> dict:
    """
    Load a saved prediction record.
    """

    prediction_path = Path(prediction_file)

    if not prediction_path.exists():
        raise FileNotFoundError(
            f"Prediction file not found: {prediction_path}"
        )

    with prediction_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def display_prediction_record(record: dict) -> None:
    """
    Display a prediction record in a readable format.
    """

    print()
    print("=" * 70)
    print("AGRO LIFE-AI COMPUTER VISION PREDICTION")
    print("=" * 70)

    print(f"Produce: {record.get('produce')}")
    print(
        f"Image: {record.get('image_filename')}"
    )
    print(
        f"Predicted Class: {record.get('predicted_class')}"
    )

    probability = record.get(
        "model_probability"
    )

    if probability is not None:
        print(
            f"Model Probability: "
            f"{probability * 100:.2f}%"
        )

    print(
        f"Classification Type: "
        f"{record.get('classification_type')}"
    )

    print()
    print("IMPORTANT RESEARCH LIMITATIONS")
    print("-" * 70)

    print(
        "Shelf-life prediction: "
        f"{record.get('shelf_life_prediction')}"
    )

    print(
        "Food-safety certification: "
        f"{record.get('food_safety_certification')}"
    )

    print(
        "Four-stage decay prediction: "
        f"{record.get('four_stage_decay_prediction')}"
    )

    print()
    print(
        record.get("research_note")
    )

    print("=" * 70)


def manage_prediction(
    image_path: str,
    predicted_class: str,
    probability: Optional[float] = None,
) -> dict:
    """
    Create, save, and return a managed prediction record.
    """

    record = create_prediction_record(
        image_path=image_path,
        predicted_class=predicted_class,
        probability=probability,
    )

    output_file = save_prediction_record(record)

    record["managed_prediction_file"] = str(
        output_file
    )

    return record


if __name__ == "__main__":

    print()
    print("=" * 70)
    print("AGRO LIFE-AI PREDICTION RESULT MANAGER")
    print("=" * 70)

    print()
    print(
        "Prediction result manager is ready."
    )

    print(
        f"Storage directory:\n"
        f"{PREDICTION_DIRECTORY}"
    )

    print()
    print(
        "Supported visual classes:"
    )

    for class_name in sorted(SUPPORTED_CLASSES):
        print(f"- {class_name}")

    print()
    print("Research integrity:")
    print(
        "Original Fresh/Rotten classes preserved."
    )
    print(
        "No four-stage decay relabelling performed."
    )
    print(
        "This module does not predict shelf life."
    )
    print(
        "This module does not certify food safety."
    )

    print()
    print(
        "PREDICTION RESULT MANAGER READY"
    )
    print("=" * 70)