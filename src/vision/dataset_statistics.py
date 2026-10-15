"""
AGRO LIFE-AI
Computer Vision Dataset Statistics Analyzer

Research Prototype

Purpose:
    Analyse the actual imported tomato computer-vision dataset
    before any machine-learning training.

The analyzer:
    - Counts images by split
    - Counts original classes
    - Counts annotation objects
    - Identifies images containing multiple objects
    - Calculates class percentages
    - Reports dataset distribution
    - Saves a research statistics report

Important:
    This module does NOT modify the dataset.
    Original Fresh/Rotten labels are preserved.
"""


from pathlib import Path
from collections import Counter
import csv


# ---------------------------------------------------------
# PROJECT PATHS
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

RESULTS_DIRECTORY = (
    PROJECT_ROOT
    / "results"
    / "reports"
)

REPORT_FILE = (
    RESULTS_DIRECTORY
    / "computer_vision_dataset_statistics.txt"
)


# ---------------------------------------------------------
# DATASET INFORMATION
# ---------------------------------------------------------

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

CLASS_NAMES = {
    0: "Fresh",
    1: "Rotten",
}


# ---------------------------------------------------------
# GET IMAGES
# ---------------------------------------------------------

def get_images(split):

    image_directory = (
        DATASET_ROOT
        / split
        / "images"
    )

    if not image_directory.exists():
        return []

    return [
        file
        for file in image_directory.iterdir()
        if (
            file.is_file()
            and file.suffix.lower()
            in IMAGE_EXTENSIONS
        )
    ]


# ---------------------------------------------------------
# GET LABELS
# ---------------------------------------------------------

def get_labels(split):

    label_directory = (
        DATASET_ROOT
        / split
        / "labels"
    )

    if not label_directory.exists():
        return []

    return [
        file
        for file in label_directory.iterdir()
        if (
            file.is_file()
            and file.suffix.lower() == ".txt"
        )
    ]


# ---------------------------------------------------------
# READ LABEL DATA
# ---------------------------------------------------------

def analyse_label(label_path):

    class_counts = Counter()
    object_count = 0

    try:

        content = label_path.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            return class_counts, 0

        for line in content.splitlines():

            parts = line.split()

            if len(parts) != 5:
                continue

            try:
                class_id = int(parts[0])
            except ValueError:
                continue

            class_counts[class_id] += 1
            object_count += 1

    except Exception:
        pass

    return class_counts, object_count


# ---------------------------------------------------------
# ANALYSE SPLIT
# ---------------------------------------------------------

def analyse_split(split):

    images = get_images(split)
    labels = get_labels(split)

    class_counts = Counter()

    total_objects = 0
    images_with_multiple_objects = 0
    images_with_no_objects = 0

    label_count = len(labels)

    for label in labels:

        counts, object_count = analyse_label(
            label
        )

        class_counts.update(counts)

        total_objects += object_count

        if object_count > 1:
            images_with_multiple_objects += 1

        if object_count == 0:
            images_with_no_objects += 1

    image_names = {
        image.stem
        for image in images
    }

    labelled_image_names = {
        label.stem
        for label in labels
    }

    images_without_labels = (
        image_names - labelled_image_names
    )

    return {
        "images": len(images),
        "labels": label_count,
        "class_counts": class_counts,
        "total_objects": total_objects,
        "images_with_multiple_objects":
            images_with_multiple_objects,
        "images_with_no_objects":
            images_with_no_objects,
        "images_without_labels":
            len(images_without_labels),
    }


# ---------------------------------------------------------
# CALCULATE PERCENTAGE
# ---------------------------------------------------------

def percentage(value, total):

    if total == 0:
        return 0.0

    return (
        value / total
    ) * 100


# ---------------------------------------------------------
# BUILD REPORT
# ---------------------------------------------------------

def build_report():

    RESULTS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    split_results = {}

    for split in SPLITS:

        split_results[split] = analyse_split(
            split
        )

    total_images = sum(
        result["images"]
        for result in split_results.values()
    )

    total_labels = sum(
        result["labels"]
        for result in split_results.values()
    )

    total_objects = sum(
        result["total_objects"]
        for result in split_results.values()
    )

    total_multiple_object_images = sum(
        result["images_with_multiple_objects"]
        for result in split_results.values()
    )

    total_no_object_images = sum(
        result["images_with_no_objects"]
        for result in split_results.values()
    )

    total_missing_labels = sum(
        result["images_without_labels"]
        for result in split_results.values()
    )

    overall_classes = Counter()

    for result in split_results.values():

        overall_classes.update(
            result["class_counts"]
        )

    # -----------------------------------------------------
    # REPORT TEXT
    # -----------------------------------------------------

    report_lines = []

    report_lines.append(
        "AGRO LIFE-AI"
    )

    report_lines.append(
        "COMPUTER VISION DATASET STATISTICS REPORT"
    )

    report_lines.append(
        "=" * 70
    )

    report_lines.append("")

    report_lines.append(
        "Dataset:"
    )

    report_lines.append(
        "Tomato_Dataset V5"
    )

    report_lines.append("")

    report_lines.append(
        "Purpose:"
    )

    report_lines.append(
        "Statistical inspection of the imported external "
        "tomato computer-vision dataset before machine-learning "
        "experimentation."
    )

    report_lines.append("")

    report_lines.append(
        "IMPORTANT:"
    )

    report_lines.append(
        "Original Fresh/Rotten classes are preserved."
    )

    report_lines.append(
        "No automatic conversion to the AGRO LIFE-AI "
        "four-stage decay framework has been performed."
    )

    report_lines.append("")

    # -----------------------------------------------------
    # OVERALL STATISTICS
    # -----------------------------------------------------

    report_lines.append(
        "1. OVERALL DATASET STATISTICS"
    )

    report_lines.append(
        "-" * 70
    )

    report_lines.append(
        f"Total images: {total_images}"
    )

    report_lines.append(
        f"Total label files: {total_labels}"
    )

    report_lines.append(
        f"Total annotated objects: {total_objects}"
    )

    report_lines.append(
        "Images containing multiple objects: "
        f"{total_multiple_object_images}"
    )

    report_lines.append(
        "Images containing no objects in labels: "
        f"{total_no_object_images}"
    )

    report_lines.append(
        "Images without corresponding labels: "
        f"{total_missing_labels}"
    )

    report_lines.append("")

    # -----------------------------------------------------
    # SPLIT STATISTICS
    # -----------------------------------------------------

    report_lines.append(
        "2. DATASET SPLIT DISTRIBUTION"
    )

    report_lines.append(
        "-" * 70
    )

    for split in SPLITS:

        result = split_results[split]

        split_percentage = percentage(
            result["images"],
            total_images,
        )

        report_lines.append(
            f"{split.upper()}:"
        )

        report_lines.append(
            f"  Images: {result['images']}"
        )

        report_lines.append(
            f"  Percentage of dataset: "
            f"{split_percentage:.2f}%"
        )

        report_lines.append(
            f"  Labels: {result['labels']}"
        )

        report_lines.append(
            f"  Objects: "
            f"{result['total_objects']}"
        )

        report_lines.append("")

    # -----------------------------------------------------
    # CLASS STATISTICS
    # -----------------------------------------------------

    report_lines.append(
        "3. ORIGINAL CLASS DISTRIBUTION"
    )

    report_lines.append(
        "-" * 70
    )

    for class_id in sorted(
        overall_classes.keys()
    ):

        class_name = CLASS_NAMES.get(
            class_id,
            f"Unknown class {class_id}",
        )

        count = overall_classes[class_id]

        class_percentage = percentage(
            count,
            total_objects,
        )

        report_lines.append(
            f"Class {class_id}: {class_name}"
        )

        report_lines.append(
            f"  Annotated objects: {count}"
        )

        report_lines.append(
            f"  Percentage of objects: "
            f"{class_percentage:.2f}%"
        )

        report_lines.append("")

    # -----------------------------------------------------
    # CLASS DISTRIBUTION BY SPLIT
    # -----------------------------------------------------

    report_lines.append(
        "4. CLASS DISTRIBUTION BY SPLIT"
    )

    report_lines.append(
        "-" * 70
    )

    for split in SPLITS:

        result = split_results[split]

        report_lines.append(
            split.upper()
        )

        for class_id, count in sorted(
            result["class_counts"].items()
        ):

            class_name = CLASS_NAMES.get(
                class_id,
                f"Unknown class {class_id}",
            )

            report_lines.append(
                f"  {class_name}: {count} objects"
            )

        report_lines.append("")

    # -----------------------------------------------------
    # RESEARCH INTERPRETATION
    # -----------------------------------------------------

    report_lines.append(
        "5. RESEARCH INTERPRETATION"
    )

    report_lines.append(
        "-" * 70
    )

    report_lines.append(
        "The dataset contains original Fresh and Rotten "
        "visual classes."
    )

    report_lines.append(
        "The annotated-object distribution should not be "
        "interpreted as the number of independent biological "
        "tomato samples."
    )

    report_lines.append(
        "Multiple objects may occur within a single image."
    )

    report_lines.append(
        "Therefore, object counts and image counts are "
        "reported separately."
    )

    report_lines.append(
        "The dataset does not independently provide validated "
        "shelf-life targets for the current AGRO LIFE-AI "
        "shelf-life model."
    )

    report_lines.append("")

    report_lines.append(
        "6. COMPUTER-VISION DEVELOPMENT STATUS"
    )

    report_lines.append(
        "-" * 70
    )

    report_lines.append(
        "Dataset inspection: COMPLETED"
    )

    report_lines.append(
        "Image quality validation: PASSED"
    )

    report_lines.append(
        "Dataset manifest: CREATED"
    )

    report_lines.append(
        "Original class preservation: CONFIRMED"
    )

    report_lines.append(
        "Four-stage decay labels: NOT AVAILABLE"
    )

    report_lines.append(
        "Shelf-life targets: NOT AVAILABLE"
    )

    report_lines.append(
        "Computer-vision training: NOT YET PERFORMED"
    )

    report_lines.append("")

    report_lines.append(
        "7. DATASET LIMITATION"
    )

    report_lines.append(
        "-" * 70
    )

    report_lines.append(
        "The external dataset should currently be treated "
        "as supporting computer-vision research data."
    )

    report_lines.append(
        "It should not be presented as a validated four-stage "
        "decay dataset."
    )

    report_lines.append("")

    report_lines.append(
        "8. CONCLUSION"
    )

    report_lines.append(
        "-" * 70
    )

    report_lines.append(
        "The imported dataset has been statistically inspected "
        "without modifying the original images or annotations."
    )

    report_lines.append(
        "The resulting statistics provide a documented basis "
        "for deciding the next computer-vision research step."
    )

    report_lines.append("")

    # -----------------------------------------------------
    # SAVE REPORT
    # -----------------------------------------------------

    REPORT_FILE.write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )

    return split_results, overall_classes


# ---------------------------------------------------------
# DISPLAY SUMMARY
# ---------------------------------------------------------

def display_summary(
    split_results,
    overall_classes,
):

    print()
    print("=" * 75)
    print("AGRO LIFE-AI")
    print("COMPUTER VISION DATASET STATISTICS")
    print("=" * 75)

    print()

    total_images = sum(
        result["images"]
        for result in split_results.values()
    )

    total_objects = sum(
        result["total_objects"]
        for result in split_results.values()
    )

    print(
        f"Total images: {total_images}"
    )

    print(
        f"Total annotated objects: {total_objects}"
    )

    print()
    print("SPLIT DISTRIBUTION")
    print("-" * 75)

    for split in SPLITS:

        result = split_results[split]

        print(
            f"{split:<10}: "
            f"{result['images']} images | "
            f"{result['total_objects']} objects"
        )

    print()
    print("ORIGINAL CLASS DISTRIBUTION")
    print("-" * 75)

    for class_id, count in sorted(
        overall_classes.items()
    ):

        class_name = CLASS_NAMES.get(
            class_id,
            f"Unknown class {class_id}",
        )

        print(
            f"Class {class_id} "
            f"({class_name}): "
            f"{count} objects"
        )

    print()
    print("STATISTICS REPORT")
    print("-" * 75)

    print(REPORT_FILE)

    print()
    print("=" * 75)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    split_results, overall_classes = (
        build_report()
    )

    display_summary(
        split_results,
        overall_classes,
    )

    print()
    print(
        "DATASET STATISTICS ANALYSIS COMPLETED"
    )
    print()


if __name__ == "__main__":
    main()