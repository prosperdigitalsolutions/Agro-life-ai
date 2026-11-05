"""
AGRO LIFE-AI
Customer Camera Assessment Module

Research Prototype

Purpose:
Capture/process a tomato image and classify it using the
validated Fresh/Rotten computer-vision classifier.

Important:
This module does NOT predict shelf life.
This module does NOT certify food safety.
This module does NOT perform four-stage decay classification.
"""

from pathlib import Path
from datetime import datetime

import joblib
import numpy as np
from PIL import Image

from src.vision.prediction_result_manager import (
    create_prediction_record,
    save_prediction_record,
)


from src.customers.cv_decision_support import (
    generate_cv_decision_support,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "quality_models"
    / "tomato"
    / "tomato_fresh_rotten_classifier.joblib"
)

CAMERA_CAPTURE_DIR = (
    PROJECT_ROOT
    / "results"
    / "predictions"
    / "computer_vision"
    / "camera_captures"
)

IMAGE_SIZE = (64, 64)

CLASS_NAMES = {
    0: "Fresh",
    1: "Rotten",
}


def load_camera_model():
    """Load the saved tomato Fresh/Rotten classifier."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Tomato classifier model was not found:\n{MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def preprocess_camera_image(image):
    """
    Convert camera image into the same format used during
    classifier training.
    """

    if not isinstance(image, Image.Image):
        image = Image.open(image)

    image = image.convert("RGB")
    image = image.resize(IMAGE_SIZE)

    image_array = np.asarray(
        image,
        dtype=np.float32
    ) / 255.0

    return image_array.flatten()


def classify_camera_image(image):
    """
    Classify a tomato image as Fresh or Rotten.
    """

    model = load_camera_model()

    features = preprocess_camera_image(image)
    features = features.reshape(1, -1)

    prediction = model.predict(features)[0]

    predicted_class = CLASS_NAMES.get(
        int(prediction),
        "Unknown"
    )

    probability = None

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(features)[0]
        probability = float(np.max(probabilities))

    return {
        "predicted_class": predicted_class,
        "model_probability": probability,
    }



def process_camera_image(image):
    """
    Process a camera image and save a managed prediction result.
    """

    classification = classify_camera_image(image)

    CAMERA_CAPTURE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    image_filename = f"tomato_camera_{timestamp}.jpg"

    captured_image_path = (
        CAMERA_CAPTURE_DIR / image_filename
    )

    if not isinstance(image, Image.Image):
        image = Image.open(image)

    image = image.convert("RGB")
    image.save(captured_image_path)

    cv_support = generate_cv_decision_support(
        produce_name="Tomato",
        predicted_class=classification["predicted_class"],
        model_probability=classification["model_probability"],
    )

    prediction_record = create_prediction_record(
        image_path=str(captured_image_path),
        predicted_class=classification["predicted_class"],
        probability=classification["model_probability"],
        decision_support=cv_support["decision_support"],
        research_warning=cv_support["research_warning"],
    )

    output_file = save_prediction_record(
        prediction_record
    )


    prediction_record["managed_prediction_file"] = str(
        output_file
    )

    # --------------------------------------------------------
    # CONFIDENCE-BASED CUSTOMER RECOMMENDATIONS
    # --------------------------------------------------------

    probability = classification["model_probability"]

    if probability is None:

        confidence_level = "Unavailable"

        customer_recommendation = (
            "Model confidence is unavailable. Please inspect "
            "the tomato manually before making quality decisions."
        )

    elif probability < 0.60:

        confidence_level = "Low"

        customer_recommendation = (
            "The model has low confidence in this classification. "
            "Do not rely on this result alone. Inspect the tomato "
            "manually and seek further assessment."
        )

    elif probability < 0.80:

        confidence_level = "Moderate"

        if classification["predicted_class"] == "Fresh":

            customer_recommendation = (
                "The tomato was visually classified as Fresh "
                "with moderate model confidence. Inspect it "
                "carefully, handle it properly and store it "
                "under suitable conditions."
            )

        else:

            customer_recommendation = (
                "The tomato was visually classified as Rotten "
                "with moderate model confidence. Separate it "
                "from fresh produce and arrange further inspection."
            )

    else:

        confidence_level = "High"

        if classification["predicted_class"] == "Fresh":

            customer_recommendation = (
                "The tomato was visually classified as Fresh "
                "with high model confidence. Handle it carefully, "
                "store it under suitable conditions and inspect "
                "it regularly."
            )

        else:

            customer_recommendation = (
                "The tomato was visually classified as Rotten "
                "with high model confidence. Separate it from "
                "fresh produce and avoid consuming produce that "
                "appears spoiled. Seek further inspection."
            )

    prediction_record["confidence_level"] = confidence_level

    prediction_record["customer_recommendation"] = (
        customer_recommendation
    )

    return prediction_record


    return prediction_record
def display_camera_result(result):
    """Display a camera classification result in the terminal."""

    print()
    print("=" * 70)
    print("AGRO LIFE-AI CAMERA ASSESSMENT RESULT")
    print("=" * 70)

    print(
        f"Produce: "
        f"{result.get('produce_name', 'Tomato')}"
    )

    print(
        f"Predicted Class: "
        f"{result.get('predicted_class', 'Unknown')}"
    )

    probability = result.get("model_probability")

    if probability is not None:
        print(
            f"Model Probability: "
            f"{probability * 100:.2f}%"
        )

    print()
    print("IMPORTANT")
    print("-" * 70)
    print("This is a Fresh/Rotten visual classification result.")
    print("It does not predict shelf life.")
    print("It does not certify food safety.")
    print("It does not perform four-stage decay classification.")
    print("=" * 70)


def main():
    print("=" * 70)
    print("AGRO LIFE-AI")
    print("CUSTOMER CAMERA ASSESSMENT MODULE")
    print("=" * 70)

    print()
    print("Camera assessment module is ready.")

    print()
    print("Classifier model:")
    print(MODEL_PATH)

    print()
    print("Camera capture directory:")
    print(CAMERA_CAPTURE_DIR)

    print()
    print("Current capability:")
    print("  Camera image -> Fresh/Rotten classification")

    print()
    print("Current model:")
    print("  Tomato Fresh/Rotten Logistic Regression")

    print()
    print("Future capability:")
    print("  Camera image -> quality assessment -> shelf-life estimation")

    print()
    print("Research limitation:")
    print("  The current validated model does not analyse photographs")
    print("  for shelf-life prediction.")

    print()
    print("STEP 14 CAMERA MODULE READY")
    print("=" * 70)


if __name__ == "__main__":
    main()
