"""
AGRO LIFE-AI
Shelf-Life Prediction Module

Biochemical Decay & Shelf-Life Predictor
DMI St. Eugene University
BSc Computer Science - Mini Project
"""

from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_FILE = (
    PROJECT_ROOT
    / "models"
    / "shelf_life_random_forest.joblib"
)

TARGET_COLUMN = "shelf_life_days"


def load_model():
    """Load the trained Random Forest model."""

    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_FILE}"
        )

    return joblib.load(MODEL_FILE)


def prepare_input(
    produce_type,
    initial_weight_g,
    temperature_c,
    humidity_percent,
    storage_days,
    weight_loss_percent,
    quality_score
):
    """
    Prepare a new agricultural produce record
    using the same feature structure used during training.
    """

    input_data = pd.DataFrame(
        {
            "initial_weight_g": [initial_weight_g],
            "temperature_c": [temperature_c],
            "humidity_percent": [humidity_percent],
            "storage_days": [storage_days],
            "weight_loss_percent": [weight_loss_percent],
            "quality_score": [quality_score],
            "produce_type_Banana": [
                1 if produce_type.lower() == "banana" else 0
            ],
            "produce_type_Mango": [
                1 if produce_type.lower() == "mango" else 0
            ],
            "produce_type_Tomato": [
                1 if produce_type.lower() == "tomato" else 0
            ]
        }
    )

    return input_data


def predict_shelf_life(model, input_data):
    """Predict the shelf life of the produce."""

    prediction = model.predict(
        input_data
    )

    return prediction[0]


def main():

    print("=" * 60)
    print("AGRO LIFE-AI - SHELF-LIFE PREDICTION")
    print("=" * 60)

    print("\nLoading trained model...")

    model = load_model()

    print("Model loaded successfully.")

    print("\nSample produce information")
    print("-" * 60)

    produce_type = "Tomato"
    initial_weight_g = 1000
    temperature_c = 28
    humidity_percent = 78
    storage_days = 2
    weight_loss_percent = 4.0
    quality_score = 8

    print("Produce Type:", produce_type)
    print("Initial Weight:", initial_weight_g, "g")
    print("Temperature:", temperature_c, "°C")
    print("Humidity:", humidity_percent, "%")
    print("Storage Days:", storage_days)
    print("Weight Loss:", weight_loss_percent, "%")
    print("Quality Score:", quality_score)

    input_data = prepare_input(
        produce_type,
        initial_weight_g,
        temperature_c,
        humidity_percent,
        storage_days,
        weight_loss_percent,
        quality_score
    )

    print("\nInput preparation completed.")

    predicted_shelf_life = predict_shelf_life(
        model,
        input_data
    )

    print("\n" + "=" * 60)
    print("PREDICTION RESULT")
    print("=" * 60)

    print(
        f"\nPredicted Shelf Life: "
        f"{predicted_shelf_life:.2f} days"
    )

    print("\nAGRO LIFE-AI prediction completed successfully.")

    print("=" * 60)


if __name__ == "__main__":
    main()