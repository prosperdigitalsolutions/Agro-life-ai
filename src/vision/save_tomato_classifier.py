"""
AGRO LIFE-AI
Tomato Fresh/Rotten Classifier Saver

Step 12A - Save the trained computer-vision classifier.

Research Prototype

This module reads the original YOLO Fresh/Rotten labels
from the imported Tomato_Dataset.v5 working dataset,
trains the binary classifier, and saves the model.

Original classes:
    0 = Fresh
    1 = Rotten

IMPORTANT:
    This classifier is only a supporting visual
    classification experiment.

    It does NOT:
        - predict shelf life
        - predict remaining shelf life
        - classify four decay stages
        - certify food safety
"""


from pathlib import Path
import json
from datetime import datetime

import joblib
import numpy as np
from PIL import Image
from sklearn.linear_model import LogisticRegression


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ============================================================
# DATASET PATH
# ============================================================

DATASET_ROOT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "images"
    / "external_tomato_dataset"
    / "original_classes"
)


# ============================================================
# MODEL PATH
# ============================================================

MODEL_DIRECTORY = (
    PROJECT_ROOT
    / "models"
    / "quality_models"
    / "tomato"
)

MODEL_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True
)


MODEL_PATH = (
    MODEL_DIRECTORY
    / "tomato_fresh_rotten_classifier.joblib"
)


METADATA_PATH = (
    MODEL_DIRECTORY
    / "tomato_fresh_rotten_classifier_metadata.json"
)


# ============================================================
# IMAGE SETTINGS
# ============================================================

IMAGE_SIZE = (64, 64)


SUPPORTED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


# ============================================================
# ORIGINAL DATASET CLASSES
# ============================================================

CLASS_NAMES = {
    0: "Fresh",
    1: "Rotten",
}


# ============================================================
# FIND IMAGE-LABEL PAIRS
# ============================================================

def find_image_label_pairs():
    """
    Find images and their corresponding YOLO label files.

    The imported dataset uses a structure similar to:

        train/
            images/
            labels/

        valid/
            images/
            labels/

        test/
            images/
            labels/

    The class is stored inside the YOLO label file.
    """

    pairs = []

    if not DATASET_ROOT.exists():

        raise FileNotFoundError(
            "Dataset directory was not found:\n"
            f"{DATASET_ROOT}"
        )

    image_files = [
        path
        for path in DATASET_ROOT.rglob("*")
        if (
            path.is_file()
            and path.suffix.lower()
            in SUPPORTED_IMAGE_EXTENSIONS
        )
    ]

    print()
    print(
        f"Image files discovered: {len(image_files)}"
    )

    for image_path in image_files:

        # Only use images located inside an images folder.
        if image_path.parent.name.lower() != "images":
            continue

        # Corresponding labels directory.
        labels_directory = (
            image_path.parent.parent / "labels"
        )

        label_path = (
            labels_directory
            / f"{image_path.stem}.txt"
        )

        if not label_path.exists():
            continue

        pairs.append(
            (
                image_path,
                label_path
            )
        )

    return pairs


# ============================================================
# READ YOLO LABEL
# ============================================================

def read_yolo_classes(label_path):
    """
    Read class IDs from a YOLO annotation file.

    Returns a set of class IDs.

    Example YOLO line:

        1 0.3171875 0.534375 0.4625 0.4015625

    The first value is the class ID.
    """

    class_ids = set()

    try:

        with open(
            label_path,
            "r",
            encoding="utf-8"
        ) as file:

            lines = file.readlines()

        for line in lines:

            line = line.strip()

            if not line:
                continue

            parts = line.split()

            if len(parts) < 5:
                continue

            class_id = int(
                float(parts[0])
            )

            class_ids.add(
                class_id
            )

    except Exception:

        return set()

    return class_ids


# ============================================================
# DETERMINE IMAGE CLASS
# ============================================================

def determine_image_class(label_path):
    """
    Determine the binary image class.

    Because the classifier requires a single class,
    images containing both Fresh and Rotten objects
    are excluded.

    Original labels are never modified.
    """

    class_ids = read_yolo_classes(
        label_path
    )

    # No usable class.
    if not class_ids:
        return None

    # Unknown classes.
    if not class_ids.issubset(
        {0, 1}
    ):
        return None

    # Multiple classes in one image.
    if len(class_ids) > 1:
        return None

    class_id = next(
        iter(class_ids)
    )

    return class_id


# ============================================================
# PREPROCESS IMAGE
# ============================================================

def preprocess_image(image_path):
    """
    Convert image into the same feature representation
    used by the classifier.

    64 x 64 RGB
        ↓
    NumPy array
        ↓
    Normalize 0-1
        ↓
    Flatten
    """

    image = Image.open(
        image_path
    )

    image = image.convert(
        "RGB"
    )

    image = image.resize(
        IMAGE_SIZE
    )

    image_array = np.asarray(
        image,
        dtype=np.float32
    )

    image_array = (
        image_array / 255.0
    )

    image_array = (
        image_array.reshape(-1)
    )

    return image_array


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    pairs = find_image_label_pairs()

    if not pairs:

        raise RuntimeError(
            "No image/YOLO-label pairs were found."
        )

    images = []
    labels = []

    skipped = 0

    fresh_count = 0
    rotten_count = 0

    print()
    print(
        "Reading original YOLO Fresh/Rotten labels..."
    )

    for image_path, label_path in pairs:

        class_id = determine_image_class(
            label_path
        )

        if class_id is None:

            skipped += 1
            continue

        try:

            image_array = preprocess_image(
                image_path
            )

            images.append(
                image_array
            )

            labels.append(
                class_id
            )

            if class_id == 0:
                fresh_count += 1

            elif class_id == 1:
                rotten_count += 1

        except Exception:

            skipped += 1

    if not images:

        raise RuntimeError(
            "No usable Fresh/Rotten images were found "
            "after reading the YOLO annotations."
        )

    X = np.asarray(
        images,
        dtype=np.float32
    )

    y = np.asarray(
        labels,
        dtype=np.int32
    )

    return (
        X,
        y,
        skipped,
        fresh_count,
        rotten_count
    )


# ============================================================
# TRAIN CLASSIFIER
# ============================================================

def train_classifier(X, y):

    print()
    print(
        "Training Logistic Regression classifier..."
    )

    model = LogisticRegression(
        max_iter=1000,
        random_state=42
    )

    model.fit(
        X,
        y
    )

    return model


# ============================================================
# SAVE MODEL
# ============================================================

def save_model(model):

    joblib.dump(
        model,
        MODEL_PATH
    )

    return MODEL_PATH


# ============================================================
# SAVE METADATA
# ============================================================

def save_metadata(
    X,
    y,
    skipped,
    fresh_count,
    rotten_count
):

    metadata = {

        "system":
            "AGRO LIFE-AI",

        "module":
            "Tomato Fresh/Rotten Classifier",

        "experiment":
            "Binary Visual Classification",

        "algorithm":
            "Logistic Regression",

        "image_width":
            IMAGE_SIZE[0],

        "image_height":
            IMAGE_SIZE[1],

        "image_channels":
            3,

        "feature_count":
            int(X.shape[1]),

        "usable_image_count":
            int(len(X)),

        "fresh_image_count":
            int(fresh_count),

        "rotten_image_count":
            int(rotten_count),

        "skipped_image_count":
            int(skipped),

        "classes":
            {
                "0": "Fresh",
                "1": "Rotten"
            },

        "dataset":
            "Tomato_Dataset.v5",

        "label_format":
            "YOLO",

        "normalization":
            "Pixel values divided by 255.0",

        "random_state":
            42,

        "max_iter":
            1000,

        "source_classes_preserved":
            True,

        "four_stage_decay_relabelling":
            False,

        "shelf_life_prediction":
            False,

        "food_safety_assessment":
            False,

        "created_at":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "research_note":
            (
                "The original Fresh/Rotten labels were "
                "read from YOLO annotations. Images "
                "containing multiple classes were excluded "
                "from the binary classification experiment. "
                "No four-stage decay relabelling was "
                "performed."
            )
    }

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4
        )

    return METADATA_PATH


# ============================================================
# DISPLAY SUMMARY
# ============================================================

def display_summary(
    X,
    skipped,
    fresh_count,
    rotten_count
):

    print()
    print("=" * 70)
    print(
        "AGRO LIFE-AI"
    )
    print(
        "TOMATO CLASSIFIER SAVING COMPLETED"
    )
    print("=" * 70)

    print()
    print(
        "MODEL INFORMATION"
    )

    print("-" * 70)

    print(
        "Algorithm: Logistic Regression"
    )

    print(
        "Experiment: Fresh / Rotten Classification"
    )

    print(
        "Image Size: 64 x 64 RGB"
    )

    print(
        f"Features: {X.shape[1]}"
    )

    print(
        f"Usable Images: {len(X)}"
    )

    print(
        f"Fresh Images: {fresh_count}"
    )

    print(
        f"Rotten Images: {rotten_count}"
    )

    print(
        f"Skipped Images: {skipped}"
    )

    print()
    print(
        "CLASS LABELS"
    )

    print("-" * 70)

    print(
        "0 = Fresh"
    )

    print(
        "1 = Rotten"
    )

    print()
    print(
        "SAVED MODEL"
    )

    print("-" * 70)

    print(
        MODEL_PATH
    )

    print()
    print(
        "SAVED METADATA"
    )

    print("-" * 70)

    print(
        METADATA_PATH
    )

    print()
    print(
        "RESEARCH INTEGRITY"
    )

    print("-" * 70)

    print(
        "Original Fresh/Rotten labels preserved."
    )

    print(
        "YOLO annotations were used to identify classes."
    )

    print(
        "Images with multiple classes were excluded."
    )

    print(
        "No four-stage decay relabelling performed."
    )

    print(
        "This model does not predict shelf life."
    )

    print(
        "This model does not certify food safety."
    )

    print()
    print(
        "TOMATO FRESH/ROTTEN CLASSIFIER "
        "SAVED SUCCESSFULLY"
    )

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print(
        "AGRO LIFE-AI"
    )
    print(
        "SAVE TOMATO FRESH/ROTTEN CLASSIFIER"
    )
    print("=" * 70)

    try:

        # ----------------------------------------------------
        # Load images and YOLO labels
        # ----------------------------------------------------

        (
            X,
            y,
            skipped,
            fresh_count,
            rotten_count
        ) = load_dataset()

        # ----------------------------------------------------
        # Verify both classes
        # ----------------------------------------------------

        unique_classes = set(
            y.tolist()
        )

        if unique_classes != {0, 1}:

            raise RuntimeError(
                "Both Fresh and Rotten classes are required "
                "for binary classifier training."
            )

        # ----------------------------------------------------
        # Train
        # ----------------------------------------------------

        model = train_classifier(
            X,
            y
        )

        # ----------------------------------------------------
        # Save model
        # ----------------------------------------------------

        save_model(
            model
        )

        # ----------------------------------------------------
        # Save metadata
        # ----------------------------------------------------

        save_metadata(
            X,
            y,
            skipped,
            fresh_count,
            rotten_count
        )

        # ----------------------------------------------------
        # Display summary
        # ----------------------------------------------------

        display_summary(
            X,
            skipped,
            fresh_count,
            rotten_count
        )

    except Exception as error:

        print()
        print("=" * 70)
        print(
            "MODEL SAVING FAILED"
        )
        print("=" * 70)

        print()
        print(
            f"Error: {error}"
        )

        print()

        raise


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":
    main()