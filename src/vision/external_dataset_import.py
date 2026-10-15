"""
AGRO LIFE-AI
External Computer Vision Dataset Import Module

Research Prototype

Purpose:
    Safely inspect and import an external tomato image dataset
    into the AGRO LIFE-AI computer-vision research workspace.

Important:
    The original external dataset must remain unchanged.

    The Fresh and Rotten classes from the external dataset are
    preserved exactly as supplied by the source.

    They must NOT automatically be converted into the four
    AGRO LIFE-AI decay stages.
"""

from pathlib import Path
import shutil


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_ROOT = (
    PROJECT_ROOT
    / "data"
    / "external_datasets"
    / "tomato_detection"
    / "inspection"
    / "Tomato_Dataset.v5"
)

WORKING_ROOT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "images"
    / "external_tomato_dataset"
)

SOURCE_COPY_ROOT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "images"
    / "external_tomato_dataset"
    / "original_classes"
)


# ---------------------------------------------------------
# SUPPORTED FILE TYPES
# ---------------------------------------------------------

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


# ---------------------------------------------------------
# DATASET STRUCTURE
# ---------------------------------------------------------

SPLITS = [
    "train",
    "valid",
    "test",
]


# ---------------------------------------------------------
# CREATE WORKING DIRECTORIES
# ---------------------------------------------------------

def create_working_directories():
    """
    Create directories required for the external dataset
    working copy.
    """

    for split in SPLITS:
        (SOURCE_COPY_ROOT / split / "images").mkdir(
            parents=True,
            exist_ok=True,
        )

        (SOURCE_COPY_ROOT / split / "labels").mkdir(
            parents=True,
            exist_ok=True,
        )


# ---------------------------------------------------------
# SOURCE VALIDATION
# ---------------------------------------------------------

def validate_source_dataset():
    """
    Check whether the extracted external dataset exists.
    """

    if not SOURCE_ROOT.exists():
        return False, (
            "External dataset was not found at:\n"
            f"{SOURCE_ROOT}"
        )

    missing_splits = []

    for split in SPLITS:
        split_path = SOURCE_ROOT / split

        if not split_path.exists():
            missing_splits.append(split)

    if missing_splits:
        return False, (
            "The following dataset splits are missing: "
            + ", ".join(missing_splits)
        )

    return True, "External dataset structure is valid."


# ---------------------------------------------------------
# COUNT IMAGES
# ---------------------------------------------------------

def count_images(split):
    """
    Count image files in a dataset split.
    """

    image_directory = SOURCE_ROOT / split / "images"

    if not image_directory.exists():
        return 0

    return sum(
        1
        for file in image_directory.iterdir()
        if file.is_file()
        and file.suffix.lower() in IMAGE_EXTENSIONS
    )


# ---------------------------------------------------------
# COUNT LABEL FILES
# ---------------------------------------------------------

def count_labels(split):
    """
    Count YOLO annotation files in a dataset split.
    """

    label_directory = SOURCE_ROOT / split / "labels"

    if not label_directory.exists():
        return 0

    return sum(
        1
        for file in label_directory.iterdir()
        if file.is_file()
        and file.suffix.lower() == ".txt"
    )


# ---------------------------------------------------------
# SOURCE REPORT
# ---------------------------------------------------------

def generate_dataset_report():
    """
    Generate a summary of the external dataset.
    """

    print()
    print("=" * 70)
    print("AGRO LIFE-AI EXTERNAL DATASET INSPECTION")
    print("=" * 70)

    print()
    print("SOURCE DATASET")
    print("-" * 70)
    print(SOURCE_ROOT)

    print()
    print("WORKING DATASET")
    print("-" * 70)
    print(WORKING_ROOT)

    print()
    print("SPLIT INFORMATION")
    print("-" * 70)

    total_images = 0
    total_labels = 0

    for split in SPLITS:

        images = count_images(split)
        labels = count_labels(split)

        total_images += images
        total_labels += labels

        print(
            f"{split:<10} "
            f"Images: {images:<6} "
            f"Labels: {labels}"
        )

    print()
    print("-" * 70)
    print(
        f"TOTAL      Images: {total_images:<6} "
        f"Labels: {total_labels}"
    )

    print()
    print("DATASET CLASS POLICY")
    print("-" * 70)
    print("Class 0: Fresh")
    print("Class 1: Rotten")
    print()
    print(
        "IMPORTANT: Original classes will be preserved."
    )
    print(
        "No automatic conversion to AGRO LIFE-AI decay stages "
        "will be performed."
    )

    print()
    print("=" * 70)


# ---------------------------------------------------------
# COPY DATASET
# ---------------------------------------------------------

def copy_dataset_to_working_area():
    """
    Copy images and YOLO labels into the AGRO LIFE-AI
    processed working directory.

    The original dataset is never modified.
    """

    create_working_directories()

    copied_images = 0
    copied_labels = 0

    for split in SPLITS:

        source_images = SOURCE_ROOT / split / "images"
        source_labels = SOURCE_ROOT / split / "labels"

        target_images = (
            SOURCE_COPY_ROOT
            / split
            / "images"
        )

        target_labels = (
            SOURCE_COPY_ROOT
            / split
            / "labels"
        )

        if source_images.exists():

            for file in source_images.iterdir():

                if (
                    file.is_file()
                    and file.suffix.lower()
                    in IMAGE_EXTENSIONS
                ):
                    shutil.copy2(
                        file,
                        target_images / file.name,
                    )

                    copied_images += 1

        if source_labels.exists():

            for file in source_labels.iterdir():

                if (
                    file.is_file()
                    and file.suffix.lower() == ".txt"
                ):
                    shutil.copy2(
                        file,
                        target_labels / file.name,
                    )

                    copied_labels += 1

    return copied_images, copied_labels


# ---------------------------------------------------------
# MAIN TEST
# ---------------------------------------------------------

def main():

    print()
    print("AGRO LIFE-AI")
    print("EXTERNAL DATASET IMPORT PIPELINE")
    print("=" * 70)

    valid, message = validate_source_dataset()

    print()
    print("SOURCE VALIDATION")
    print("-" * 70)
    print(message)

    if not valid:
        print()
        print(
            "IMPORT STOPPED: Source dataset structure is not valid."
        )
        return

    generate_dataset_report()

    print()
    print("CREATING WORKING COPY")
    print("-" * 70)

    copied_images, copied_labels = copy_dataset_to_working_area()

    print(f"Images copied: {copied_images}")
    print(f"Labels copied: {copied_labels}")

    print()
    print("=" * 70)
    print("EXTERNAL DATASET IMPORT COMPLETED")
    print("=" * 70)

    print()
    print("Research integrity:")
    print("Original dataset preserved.")
    print("Original Fresh/Rotten labels preserved.")
    print("No automatic decay-stage relabelling performed.")
    print()


if __name__ == "__main__":
    main()