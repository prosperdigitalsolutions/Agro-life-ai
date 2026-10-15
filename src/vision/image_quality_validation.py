"""
AGRO LIFE-AI
Computer Vision Image Quality Validation Module

Research Prototype

Purpose:
    Validate the integrity of the imported external tomato
    computer-vision dataset before machine-learning training.

Checks:
    1. Supported image files
    2. Readable images
    3. Missing labels
    4. Labels without images
    5. Empty labels
    6. Invalid YOLO annotations
    7. Duplicate filenames

Important:
    This module does NOT modify the dataset.
"""


from pathlib import Path
from collections import Counter
from PIL import Image


# ---------------------------------------------------------
# PROJECT PATH
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_ROOT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "images"
    / "external_tomato_dataset"
    / "original_classes"
)


SPLITS = [
    "train",
    "valid",
    "test",
]


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


# ---------------------------------------------------------
# IMAGE DISCOVERY
# ---------------------------------------------------------

def get_images(split):
    """
    Return all supported image files for a dataset split.
    """

    image_dir = DATASET_ROOT / split / "images"

    if not image_dir.exists():
        return []

    return [
        file
        for file in image_dir.iterdir()
        if file.is_file()
        and file.suffix.lower() in IMAGE_EXTENSIONS
    ]


# ---------------------------------------------------------
# LABEL DISCOVERY
# ---------------------------------------------------------

def get_labels(split):
    """
    Return all YOLO label files for a dataset split.
    """

    label_dir = DATASET_ROOT / split / "labels"

    if not label_dir.exists():
        return []

    return [
        file
        for file in label_dir.iterdir()
        if file.is_file()
        and file.suffix.lower() == ".txt"
    ]


# ---------------------------------------------------------
# CHECK IMAGE READABILITY
# ---------------------------------------------------------

def check_image_readability(images):
    """
    Check whether image files can be opened successfully.
    """

    unreadable = []

    for image_path in images:

        try:
            with Image.open(image_path) as image:
                image.verify()

        except Exception:
            unreadable.append(image_path.name)

    return unreadable


# ---------------------------------------------------------
# CHECK MISSING LABELS
# ---------------------------------------------------------

def find_missing_labels(images, labels):
    """
    Find images that do not have a corresponding YOLO label.
    """

    label_names = {
        label.stem
        for label in labels
    }

    missing = []

    for image in images:

        if image.stem not in label_names:
            missing.append(image.name)

    return missing


# ---------------------------------------------------------
# CHECK LABELS WITHOUT IMAGES
# ---------------------------------------------------------

def find_orphan_labels(images, labels):
    """
    Find labels that do not have a corresponding image.
    """

    image_names = {
        image.stem
        for image in images
    }

    orphan_labels = []

    for label in labels:

        if label.stem not in image_names:
            orphan_labels.append(label.name)

    return orphan_labels


# ---------------------------------------------------------
# CHECK EMPTY LABELS
# ---------------------------------------------------------

def find_empty_labels(labels):
    """
    Find label files that contain no annotation data.
    """

    empty_labels = []

    for label in labels:

        try:

            content = label.read_text(
                encoding="utf-8"
            ).strip()

            if not content:
                empty_labels.append(label.name)

        except Exception:
            empty_labels.append(label.name)

    return empty_labels


# ---------------------------------------------------------
# VALIDATE YOLO ANNOTATIONS
# ---------------------------------------------------------
def validate_yolo_labels(labels):
    """
    Validate YOLO annotation format.

    Expected format:

        class_id
        x_center
        y_center
        width
        height

    Coordinates must be between 0 and 1.
    """

    invalid = []
    class_counter = Counter()

    for label in labels:

        try:

            content = label.read_text(
                encoding="utf-8"
            ).strip()

            if not content:
                continue

            for line_number, line in enumerate(
                content.splitlines(),
                start=1,
            ):

                parts = line.split()

                if len(parts) != 5:

                    invalid.append(
                        f"{label.name}: "
                        f"line {line_number} "
                        f"must contain 5 values"
                    )

                    continue

                try:

                    class_id = int(parts[0])

                    x_center = float(parts[1])
                    y_center = float(parts[2])
                    width = float(parts[3])
                    height = float(parts[4])

                except ValueError:

                    invalid.append(
                        f"{label.name}: "
                        f"line {line_number} "
                        f"contains non-numeric values"
                    )

                    continue

                if class_id < 0:

                    invalid.append(
                        f"{label.name}: "
                        f"line {line_number} "
                        f"invalid class ID"
                    )

                    continue

                coordinates = [
                    x_center,
                    y_center,
                    width,
                    height,
                ]

                if any(
                    value < 0 or value > 1
                    for value in coordinates
                ):

                    invalid.append(
                        f"{label.name}: "
                        f"line {line_number} "
                        f"coordinate outside 0-1 range"
                    )

                    continue

                class_counter[class_id] += 1

        except Exception as error:

            invalid.append(
                f"{label.name}: "
                f"could not be read - {error}"
            )

    return invalid, class_counter



# ---------------------------------------------------------
# CHECK DUPLICATE FILENAMES
# ---------------------------------------------------------

def find_duplicate_filenames():
    """
    Check for duplicate image filenames across dataset splits.

    Duplicate filenames across different splits can create
    confusion during later processing.
    """

    filename_locations = {}

    for split in SPLITS:

        images = get_images(split)

        for image in images:

            filename = image.name

            filename_locations.setdefault(
                filename,
                [],
            ).append(split)

    duplicates = {
        filename: splits
        for filename, splits
        in filename_locations.items()
        if len(splits) > 1
    }

    return duplicates


# ---------------------------------------------------------
# VALIDATE ONE SPLIT
# ---------------------------------------------------------

def validate_split(split):

    images = get_images(split)
    labels = get_labels(split)

    unreadable = check_image_readability(images)

    missing_labels = find_missing_labels(
        images,
        labels,
    )

    orphan_labels = find_orphan_labels(
        images,
        labels,
    )

    empty_labels = find_empty_labels(labels)

    invalid_annotations, class_counter = (
        validate_yolo_labels(labels)
    )

    return {
        "images": images,
        "labels": labels,
        "unreadable": unreadable,
        "missing_labels": missing_labels,
        "orphan_labels": orphan_labels,
        "empty_labels": empty_labels,
        "invalid_annotations": invalid_annotations,
        "class_counter": class_counter,
    }


# ---------------------------------------------------------
# DISPLAY REPORT
# ---------------------------------------------------------

def display_report():

    print()
    print("=" * 75)
    print("AGRO LIFE-AI")
    print("COMPUTER VISION IMAGE QUALITY VALIDATION")
    print("=" * 75)

    if not DATASET_ROOT.exists():

        print()
        print("ERROR: Working dataset was not found.")
        print(DATASET_ROOT)
        return

    all_results = {}

    for split in SPLITS:

        print()
        print(f"{split.upper()} DATASET")
        print("-" * 75)

        results = validate_split(split)

        all_results[split] = results

        print(
            f"Images              : "
            f"{len(results['images'])}"
        )

        print(
            f"Labels              : "
            f"{len(results['labels'])}"
        )

        print(
            f"Unreadable images   : "
            f"{len(results['unreadable'])}"
        )

        print(
            f"Missing labels      : "
            f"{len(results['missing_labels'])}"
        )

        print(
            f"Orphan labels       : "
            f"{len(results['orphan_labels'])}"
        )

        print(
            f"Empty labels        : "
            f"{len(results['empty_labels'])}"
        )

        print(
            f"Invalid annotations : "
            f"{len(results['invalid_annotations'])}"
        )

        print()
        print("Annotation classes:")

        for class_id, count in sorted(
            results["class_counter"].items()
        ):

            print(
                f"  Class {class_id}: "
                f"{count} objects"
            )

    # -----------------------------------------------------
    # DUPLICATE CHECK
    # -----------------------------------------------------

    duplicates = find_duplicate_filenames()

    print()
    print("DUPLICATE FILENAME CHECK")
    print("-" * 75)

    print(
        f"Duplicate filenames across splits: "
        f"{len(duplicates)}"
    )

    # -----------------------------------------------------
    # FINAL STATUS
    # -----------------------------------------------------

    problems = 0

    for results in all_results.values():

        problems += len(results["unreadable"])
        problems += len(results["missing_labels"])
        problems += len(results["orphan_labels"])
        problems += len(results["empty_labels"])
        problems += len(results["invalid_annotations"])

    problems += len(duplicates)

    print()
    print("=" * 75)

    if problems == 0:

        print(
            "DATASET QUALITY STATUS: "
            "PASSED"
        )

        print()
        print(
            "No structural image or annotation "
            "problems were detected."
        )

        print(
            "The working dataset is ready for "
            "the next research preparation stage."
        )

    else:

        print(
            "DATASET QUALITY STATUS: "
            "REVIEW REQUIRED"
        )

        print()
        print(
            f"Potential issues detected: {problems}"
        )

        print(
            "Review the validation results before "
            "machine-learning training."
        )

    print("=" * 75)
    print()


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":
    display_report()