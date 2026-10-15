"""
AGRO LIFE-AI
Machine Learning Model Training Module

Biochemical Decay & Shelf-Life Predictor
DMI St. Eugene University
BSc Computer Science - Mini Project
"""

from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "processed_shelf_life_data.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "models"
)

PREDICTIONS_DIR = (
    PROJECT_ROOT
    / "results"
    / "predictions"
)

MODEL_FILE = (
    MODEL_DIR
    / "shelf_life_random_forest.joblib"
)

PREDICTIONS_FILE = (
    PREDICTIONS_DIR
    / "shelf_life_predictions.csv"
)

# Create required directories
MODEL_DIR.mkdir(parents=True, exist_ok=True)
PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# TARGET VARIABLE
# ---------------------------------------------------------

TARGET_COLUMN = "shelf_life_days"


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

def load_processed_data():
    """Load the processed machine-learning dataset."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Processed dataset not found: {DATA_FILE}"
        )

    return pd.read_csv(DATA_FILE)


# ---------------------------------------------------------
# PREPARE DATA
# ---------------------------------------------------------

def prepare_data(data):
    """Separate input features from the target variable."""

    X = data.drop(columns=[TARGET_COLUMN])

    y = data[TARGET_COLUMN]

    return X, y


# ---------------------------------------------------------
# TRAIN MODEL
# ---------------------------------------------------------

def train_model(X_train, y_train):
    """Train the Random Forest regression model."""

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )

    model.fit(X_train, y_train)

    return model


# ---------------------------------------------------------
# EVALUATE MODEL
# ---------------------------------------------------------

def evaluate_model(model, X_test, y_test):
    """Evaluate model performance."""

    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    mse = mean_squared_error(
        y_test,
        predictions
    )

    rmse = mse ** 0.5

    r2 = r2_score(
        y_test,
        predictions
    )

    return predictions, mae, rmse, r2


# ---------------------------------------------------------
# SAVE MODEL
# ---------------------------------------------------------

def save_model(model):
    """Save the trained machine-learning model."""

    joblib.dump(
        model,
        MODEL_FILE
    )


# ---------------------------------------------------------
# SAVE PREDICTIONS
# ---------------------------------------------------------

def save_predictions(y_test, predictions):
    """Save actual and predicted shelf-life values."""

    results = pd.DataFrame(
        {
            "actual_shelf_life_days": y_test.values,
            "predicted_shelf_life_days": predictions,
        }
    )

    results.to_csv(
        PREDICTIONS_FILE,
        index=False
    )


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("AGRO LIFE-AI - MACHINE LEARNING MODEL")
    print("=" * 60)

    # Load processed dataset
    data = load_processed_data()

    print("\nProcessed dataset loaded successfully.")
    print("Number of records:", len(data))
    print("Number of columns:", len(data.columns))

    # Prepare features and target
    X, y = prepare_data(data)

    print("\nFeatures:", X.shape[1])
    print("Target:", TARGET_COLUMN)

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42
    )

    print("\nDataset split completed.")

    print("Training records:", len(X_train))
    print("Testing records:", len(X_test))

    # Train model
    print("\nTraining Random Forest model...")

    model = train_model(
        X_train,
        y_train
    )

    print("Model training completed.")

    # Evaluate model
    predictions, mae, rmse, r2 = evaluate_model(
        model,
        X_test,
        y_test
    )

    # Display results
    print("\n" + "=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    print(f"\nMean Absolute Error (MAE): {mae:.4f}")
    print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
    print(f"R-squared (R²): {r2:.4f}")

    # Display predictions
    print("\n" + "=" * 60)
    print("PREDICTIONS")
    print("=" * 60)

    for actual, predicted in zip(
        y_test,
        predictions
    ):
        print(
            f"Actual: {actual:.2f} days | "
            f"Predicted: {predicted:.2f} days"
        )

    # Save trained model
    save_model(model)

    print("\nTrained model saved:")
    print(MODEL_FILE)

    # Save predictions
    save_predictions(
        y_test,
        predictions
    )

    print("\nPredictions saved:")
    print(PREDICTIONS_FILE)

    print("\n" + "=" * 60)
    print("MACHINE LEARNING STAGE COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()