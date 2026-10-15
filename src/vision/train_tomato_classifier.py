"""
AGRO LIFE-AI
Tomato Computer Vision Classification Experiment

Research Prototype

Experiment:
    Binary classification of tomato images into:
        0 = Fresh
        1 = Rotten

Important:
    This is a supporting computer-vision experiment.

    It is NOT the final AGRO LIFE-AI four-stage decay
    classification model.

    The current shelf-life model remains separate and
    uses numerical Day-4 research measurements.
"""

from pathlib import Path
import json

import numpy as np
import matplotlib.pyplot as plt

from PIL import Image

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_ROOT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "images"
    / "external_tomato_dataset"
    / "original_classes"
)

MODEL_DIRECTORY = (
    PROJECT_ROOT
    / "models"
    / "quality_models"
    / "tomato"
)

RESULT_DIRECTORY = (
    PROJECT_ROOT
    / "results"
    / "reports"
    / "computer_vision"
)

FIGURE_DIRECTORY = (
    PROJECT_ROOT
    / "results"
    / "figures"
    / "computer_vision"
)


# =========================================================
# EXPERIMENT SETTINGS
# =========================================================

IMAGE_SIZE = (64, 64)

CLASS_NAMES = {
    0: "Fresh",
    1: "Rotten",
}

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


# =========================================================
# DIRECTORY SETUP
# =========================================================

def create_directories():

    MODEL_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    RESULT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    FIGURE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )


# =========================================================
# LOAD IMAGE
# =========================================================

def load_image(image_path):

    try:

        image = Image.open(
            image_path
        ).convert("RGB")

        image = image.resize(
            IMAGE_SIZE
        )

        array = np.asarray(
            image,
            dtype=np.float32,
        )

        array = array / 255.0

        return array.flatten()

    except Exception:

        return None


# =========================================================
# READ YOLO LABELS
# =========================================================

def get_image_class(
    label_path
):

    if not label_path.exists():
        return None

    try:

        lines = label_path.read_text(
            encoding="utf-8"
        ).strip().splitlines()

        class_ids = []

        for line in lines:

            parts = line.split()

            if len(parts) != 5:
                continue

            class_id = int(parts[0])

            class_ids.append(
                class_id
            )

        if not class_ids:
            return None

        # -------------------------------------------------
        # Important:
        # If an image contains multiple classes, the image
        # is excluded from this binary classification
        # experiment rather than assigning an arbitrary
        # class.
        # -------------------------------------------------

        unique_classes = set(
            class_ids
        )

        if len(unique_classes) != 1:
            return None

        class_id = class_ids[0]

        if class_id not in CLASS_NAMES:
            return None

        return class_id

    except Exception:

        return None


# =========================================================
# LOAD DATASET SPLIT
# =========================================================

def load_dataset_split(
    split
):

    image_directory = (
        DATASET_ROOT
        / split
        / "images"
    )

    label_directory = (
        DATASET_ROOT
        / split
        / "labels"
    )

    if not image_directory.exists():
        return (
            np.empty((0, IMAGE_SIZE[0] * IMAGE_SIZE[1] * 3)),
            np.empty((0,), dtype=int),
            0,
        )

    features = []
    labels = []

    excluded = 0

    image_files = sorted(
        [
            file
            for file in image_directory.iterdir()
            if (
                file.is_file()
                and file.suffix.lower()
                in IMAGE_EXTENSIONS
            )
        ]
    )

    for image_path in image_files:

        label_path = (
            label_directory
            / f"{image_path.stem}.txt"
        )

        class_id = get_image_class(
            label_path
        )

        if class_id is None:

            excluded += 1
            continue

        image_features = load_image(
            image_path
        )

        if image_features is None:

            excluded += 1
            continue

        features.append(
            image_features
        )

        labels.append(
            class_id
        )

    if not features:

        return (
            np.empty(
                (
                    0,
                    IMAGE_SIZE[0]
                    * IMAGE_SIZE[1]
                    * 3,
                )
            ),
            np.empty(
                (0,),
                dtype=int,
            ),
            excluded,
        )

    return (
        np.asarray(
            features,
            dtype=np.float32,
        ),
        np.asarray(
            labels,
            dtype=int,
        ),
        excluded,
    )


# =========================================================
# DISPLAY DATASET INFORMATION
# =========================================================

def display_dataset_information(
    train_labels,
    valid_labels,
    test_labels,
):

    print()
    print("=" * 75)
    print("DATASET CLASSIFICATION INFORMATION")
    print("=" * 75)

    datasets = [
        ("Train", train_labels),
        ("Validation", valid_labels),
        ("Test", test_labels),
    ]

    for name, labels in datasets:

        print()
        print(
            f"{name} dataset"
        )
        print("-" * 75)

        for class_id, class_name in CLASS_NAMES.items():

            count = int(
                np.sum(
                    labels == class_id
                )
            )

            print(
                f"{class_name:<10}: "
                f"{count}"
            )


# =========================================================
# TRAIN MODEL
# =========================================================

def train_model(
    x_train,
    y_train,
):

    print()
    print("=" * 75)
    print("TRAINING COMPUTER VISION CLASSIFIER")
    print("=" * 75)

    print()
    print(
        "Algorithm: Logistic Regression"
    )

    print(
        "Input: 64 x 64 RGB image"
    )

    print(
        "Output: Fresh / Rotten"
    )

    model = LogisticRegression(
        max_iter=1000,
        random_state=42,
    )

    model.fit(
        x_train,
        y_train,
    )

    print()
    print(
        "CLASSIFIER TRAINING COMPLETED"
    )

    return model


# =========================================================
# EVALUATION
# =========================================================

def evaluate_model(
    model,
    x_test,
    y_test,
):

    predictions = model.predict(
        x_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0,
    )

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=[
            0,
            1,
        ],
    )

    report = classification_report(
        y_test,
        predictions,
        target_names=[
            "Fresh",
            "Rotten",
        ],
        zero_division=0,
    )

    return {
        "accuracy": float(
            accuracy
        ),
        "precision": float(
            precision
        ),
        "recall": float(
            recall
        ),
        "f1_score": float(
            f1
        ),
        "confusion_matrix": matrix.tolist(),
        "classification_report": report,
    }


# =========================================================
# CONFUSION MATRIX FIGURE
# =========================================================

def create_confusion_matrix_figure(
    matrix
):

    plt.figure(
        figsize=(7, 6)
    )

    plt.imshow(
        matrix,
        interpolation="nearest",
    )

    plt.title(
        "Tomato Fresh vs Rotten Classification"
    )

    plt.xlabel(
        "Predicted Class"
    )

    plt.ylabel(
        "Actual Class"
    )

    plt.xticks(
        [0, 1],
        ["Fresh", "Rotten"],
    )

    plt.yticks(
        [0, 1],
        ["Fresh", "Rotten"],
    )

    for row in range(
        len(matrix)
    ):

        for column in range(
            len(matrix[row])
        ):

            plt.text(
                column,
                row,
                str(
                    matrix[row][column]
                ),
                ha="center",
                va="center",
            )

    plt.tight_layout()

    output_file = (
        FIGURE_DIRECTORY
        / "05_tomato_classifier_confusion_matrix.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    return output_file


# =========================================================
# SAVE RESULTS
# =========================================================

def save_results(
    results,
    excluded_counts,
):

    result_file = (
        RESULT_DIRECTORY
        / "tomato_classifier_results.json"
    )

    output = {
        "experiment": (
            "Binary Tomato Fresh/Rotten "
            "Classification"
        ),
        "dataset": "Tomato_Dataset.v5",
        "image_size": list(
            IMAGE_SIZE
        ),
        "algorithm": (
            "Logistic Regression"
        ),
        "classes": CLASS_NAMES,
        "metrics": results,
        "excluded_images": (
            excluded_counts
        ),
        "research_note": (
            "This is a supporting computer-vision "
            "experiment. It is not the final "
            "four-stage AGRO LIFE-AI decay model."
        ),
    }

    result_file.write_text(
        json.dumps(
            output,
            indent=4,
        ),
        encoding="utf-8",
    )

    return result_file


# =========================================================
# MAIN
# =========================================================

def main():

    create_directories()

    print()
    print("=" * 75)
    print("AGRO LIFE-AI")
    print("TOMATO COMPUTER VISION CLASSIFICATION EXPERIMENT")
    print("=" * 75)

    print()
    print(
        "Experiment: Fresh vs Rotten"
    )

    print(
        "Dataset: Tomato_Dataset.v5"
    )

    print(
        "Research prototype: Supporting CV experiment"
    )

    print()

    # -----------------------------------------------------
    # LOAD DATA
    # -----------------------------------------------------

    (
        x_train,
        y_train,
        train_excluded,
    ) = load_dataset_split(
        "train"
    )

    (
        x_valid,
        y_valid,
        valid_excluded,
    ) = load_dataset_split(
        "valid"
    )

    (
        x_test,
        y_test,
        test_excluded,
    ) = load_dataset_split(
        "test"
    )

    display_dataset_information(
        y_train,
        y_valid,
        y_test,
    )

    print()
    print(
        "EXCLUDED IMAGES"
    )
    print("-" * 75)

    print(
        f"Train: {train_excluded}"
    )

    print(
        f"Validation: {valid_excluded}"
    )

    print(
        f"Test: {test_excluded}"
    )

    # -----------------------------------------------------
    # CHECK DATA
    # -----------------------------------------------------

    if len(x_train) == 0:

        print()
        print(
            "ERROR: No training images were loaded."
        )

        return

    if len(x_test) == 0:

        print()
        print(
            "ERROR: No test images were loaded."
        )

        return

    # -----------------------------------------------------
    # TRAIN
    # -----------------------------------------------------

    model = train_model(
        x_train,
        y_train,
    )

    # -----------------------------------------------------
    # EVALUATE
    # -----------------------------------------------------

    print()
    print("=" * 75)
    print("MODEL EVALUATION")
    print("=" * 75)

    results = evaluate_model(
        model,
        x_test,
        y_test,
    )

    print()
    print(
        f"Accuracy : "
        f"{results['accuracy']:.4f}"
    )

    print(
        f"Precision: "
        f"{results['precision']:.4f}"
    )

    print(
        f"Recall   : "
        f"{results['recall']:.4f}"
    )

    print(
        f"F1-score : "
        f"{results['f1_score']:.4f}"
    )

    print()
    print(
        "CLASSIFICATION REPORT"
    )

    print(
        results[
            "classification_report"
        ]
    )

    # -----------------------------------------------------
    # CONFUSION MATRIX
    # -----------------------------------------------------

    figure_file = (
        create_confusion_matrix_figure(
            results[
                "confusion_matrix"
            ]
        )
    )

    print()
    print(
        f"Confusion matrix saved to:"
    )

    print(
        figure_file
    )

    # -----------------------------------------------------
    # SAVE RESULTS
    # -----------------------------------------------------

    result_file = save_results(
        results,
        {
            "train": train_excluded,
            "validation": valid_excluded,
            "test": test_excluded,
        },
    )

    print()
    print(
        f"Results saved to:"
    )

    print(
        result_file
    )

    print()
    print("=" * 75)
    print(
        "TOMATO CLASSIFICATION EXPERIMENT COMPLETED"
    )
    print("=" * 75)

    print()
    print(
        "Original Fresh/Rotten labels were preserved."
    )

    print(
        "No four-stage decay labels were created."
    )

    print(
        "The classifier is a supporting CV experiment."
    )

    print()


if __name__ == "__main__":
    main()