"""
AGRO LIFE-AI
Individual Tomato Image Testing Module

Step 12 - Computer Vision Individual Image Testing

Research Prototype

Purpose:
    Test one individual tomato image using the trained
    binary Fresh/Rotten computer-vision classifier.

Important research limitation:
    This classifier predicts the original dataset classes:
        Fresh
        Rotten

    It does NOT currently:
        - predict shelf life
        - predict remaining shelf life
        - determine food safety
        - classify the four proposed decay stages
        - replace laboratory quality assessment
        - perform camera-based shelf-life prediction

The current AGRO LIFE-AI shelf-life model remains based on
numerical Day-4 research measurements.
"""

from pathlib import Path
import sys
import json
from datetime import datetime

import joblib
import numpy as np
from PIL import Image


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "quality_models"
    / "tomato"
    / "tomato_fresh_rotten_classifier.joblib"
)

RESULTS_DIRECTORY = (
    PROJECT_ROOT
    / "results"
    / "predictions"
    / "computer_vision"
)

RESULTS_DIRECTORY.mkdir(parents=True, exist_ok=True)


# ============================================================
# MODEL SETTINGS
# ============================================================

IMAGE_SIZE = (64, 64)

CLASS_NAMES = {
    0: "Fresh",
    1: "Rotten",
}


# ============================================================
# IMAGE VALIDATION
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


def validate_image_path(image_path: Path):
    """
    Validate that the supplied image exists and has
    a supported image extension.
    """

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image file was not found:\n{image_path}"
        )

    if not image_path.is_file():
        raise ValueError(
            f"The supplied path is not a file:\n{image_path}"
        )

    if image_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Unsupported image format. "
            "Use JPG, JPEG, PNG, BMP, or WEBP."
        )


# ============================================================
# LOAD MODEL
# ============================================================

def load_classifier():
    """
    Load the trained Fresh/Rotten classifier.
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "\nTrained tomato classifier was not found.\n\n"
            f"Expected location:\n{MODEL_PATH}\n\n"
            "Train and save the classifier before "
            "testing individual images."
        )

    model = joblib.load(MODEL_PATH)

    return model


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image_path: Path):
    """
    Prepare one tomato image for the classifier.

    Steps:
        1. Open image
        2. Convert to RGB
        3. Resize to 64 x 64
        4. Convert to NumPy array
        5. Normalize pixel values to 0-1
        6. Flatten image into one feature vector
    """

    image = Image.open(image_path)

    image = image.convert("RGB")

    image = image.resize(IMAGE_SIZE)

    image_array = np.asarray(
        image,
        dtype=np.float32,
    )

    # Normalize pixel values.
    image_array = image_array / 255.0

    # Flatten:
    # 64 x 64 x 3 -> 12288 features
    image_array = image_array.reshape(1, -1)

    return image_array


# ============================================================
# PREDICTION
# ============================================================

def predict_image(model, image_array):
    """
    Predict Fresh or Rotten for one image.
    """

    predicted_class_id = int(
        model.predict(image_array)[0]
    )

    predicted_class = CLASS_NAMES.get(
        predicted_class_id,
        "Unknown",
    )

    probability = None

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(image_array)[0]

        probability = float(
            probabilities[predicted_class_id]
        )

    return predicted_class_id, predicted_class, probability


# ============================================================
# RESULT CREATION
# ============================================================

def create_result(
    image_path: Path,
    predicted_class_id: int,
    predicted_class: str,
    probability,
):
    """
    Create a structured research result.
    """

    result = {
        "system": "AGRO LIFE-AI",
        "module": "Individual Tomato Image Testing",
        "experiment": "Binary Fresh/Rotten Classification",
        "image": image_path.name,
        "image_path": str(image_path),
        "predicted_class_id": predicted_class_id,
        "predicted_class": predicted_class,
        "model_probability": (
            round(probability, 4)
            if probability is not None
            else None
        ),
        "model_probability_percentage": (
            round(probability * 100, 2)
            if probability is not None
            else None
        ),
        "image_size_used": [
            IMAGE_SIZE[0],
            IMAGE_SIZE[1],
        ],
        "original_classes": [
            "Fresh",
            "Rotten",
        ],
        "shelf_life_prediction": False,
        "food_safety_assessment": False,
        "four_stage_decay_prediction": False,
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
        "research_note": (
            "This is a supporting binary visual "
            "classification experiment. The result does "
            "not represent shelf-life prediction, food "
            "safety certification, or four-stage decay "
            "classification."
        ),
    }

    return result


# ============================================================
# SAVE RESULT
# ============================================================

def save_result(result):
    """
    Save the individual image prediction as JSON.
    """

    image_name = Path(
        result["image"]
    ).stem

    output_file = (
        RESULTS_DIRECTORY
        / f"{image_name}_prediction.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
        )

    return output_file


# ============================================================
# DISPLAY RESULT
# ============================================================

def display_result(result):
    """
    Display the prediction in a clear research format.
    """

    print()
    print("=" * 70)
    print("AGRO LIFE-AI")
    print("INDIVIDUAL TOMATO IMAGE TEST")
    print("=" * 70)

    print(f"Image: {result['image']}")

    print()
    print("VISUAL CLASSIFICATION RESULT")
    print("-" * 70)

    print(
        f"Predicted Class: "
        f"{result['predicted_class']}"
    )

    if result["model_probability_percentage"] is not None:

        print(
            f"Model Probability: "
            f"{result['model_probability_percentage']:.2f}%"
        )

    print()
    print("MODEL INFORMATION")
    print("-" * 70)

    print("Classes: Fresh / Rotten")
    print("Input Size: 64 x 64 RGB")
    print("Experiment Type: Binary Image Classification")

    print()
    print("IMPORTANT RESEARCH LIMITATIONS")
    print("-" * 70)

    print(
        "This result does NOT represent:"
    )

    print(
        "1. Shelf-life prediction"
    )

    print(
        "2. Remaining shelf-life prediction"
    )

    print(
        "3. Food-safety certification"
    )

    print(
        "4. Four-stage decay classification"
    )

    print(
        "5. Laboratory quality assessment"
    )

    print()
    print("RESEARCH INTERPRETATION")
    print("-" * 70)

    if result["predicted_class"] == "Fresh":

        print(
            "The image was visually classified as "
            "Fresh by the supporting binary classifier."
        )

    elif result["predicted_class"] == "Rotten":

        print(
            "The image was visually classified as "
            "Rotten by the supporting binary classifier."
        )

    else:

        print(
            "The classifier returned an unknown class."
        )

    print()
    print(
        "The model probability is a model output and "
        "should not be interpreted as a guaranteed "
        "probability of real-world correctness."
    )

    print("=" * 70)


# ============================================================
# MAIN TEST FUNCTION
# ============================================================

def test_individual_image(image_path):
    """
    Complete individual-image testing workflow.
    """

    image_path = Path(image_path).resolve()

    print()
    print("Preparing individual image test...")

    # Validate image.
    validate_image_path(image_path)

    print(
        f"Image found: {image_path}"
    )

    # Load model.
    print(
        "Loading trained tomato classifier..."
    )

    model = load_classifier()

    print(
        "Classifier loaded successfully."
    )

    # Preprocess image.
    print(
        "Preprocessing image..."
    )

    image_array = preprocess_image(
        image_path
    )

    print(
        "Image preprocessing completed."
    )

    # Predict.
    print(
        "Running visual classification..."
    )

    (
        predicted_class_id,
        predicted_class,
        probability,
    ) = predict_image(
        model,
        image_array,
    )

    # Create result.
    result = create_result(
        image_path=image_path,
        predicted_class_id=predicted_class_id,
        predicted_class=predicted_class,
        probability=probability,
    )

    # Save result.
    output_file = save_result(
        result
    )

    # Display result.
    display_result(
        result
    )

    print()
    print(
        f"Prediction result saved to:"
    )

    print(
        output_file
    )

    print()
    print(
        "INDIVIDUAL IMAGE TEST COMPLETED SUCCESSFULLY"
    )

    return result


# ============================================================
# COMMAND-LINE INTERFACE
# ============================================================

def main():
    """
    Command-line entry point.
    """

    if len(sys.argv) < 2:

        print()
        print("=" * 70)
        print("AGRO LIFE-AI INDIVIDUAL IMAGE TESTING")
        print("=" * 70)

        print()
        print(
            "Usage:"
        )

        print()

        print(
            'python -m src.vision.predict_tomato_image '
            '"path_to_image"'
        )

        print()
        print("Example:")

        print()

        print(
            'python -m src.vision.predict_tomato_image '
            '".\\data\\sample\\tomato_images\\tomato1.jpg"'
        )

        print()
        print(
            "Please provide a tomato image path."
        )

        return

    image_path = sys.argv[1]

    try:

        test_individual_image(
            image_path
        )

    except Exception as error:

        print()
        print("=" * 70)
        print("INDIVIDUAL IMAGE TEST FAILED")
        print("=" * 70)

        print()
        print(
            f"Error: {error}"
        )

        print()

        sys.exit(1)


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":
    main()