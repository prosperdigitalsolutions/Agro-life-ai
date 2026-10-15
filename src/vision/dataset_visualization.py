"""
AGRO LIFE-AI
Computer Vision Dataset Visualization Module

Research Prototype

Purpose:
    Generate visual summaries of the imported tomato
    computer-vision dataset.

Figures:
    1. Image distribution by dataset split
    2. Annotated object distribution by original class
    3. Annotated object distribution by dataset split
    4. Class distribution percentage

Important:
    The original dataset is not modified.
    Original Fresh/Rotten classes are preserved.
"""

from pathlib import Path
from collections import Counter

import matplotlib.pyplot as plt


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

FIGURE_DIRECTORY = (
    PROJECT_ROOT
    / "results"
    / "figures"
    / "computer_vision"
)


# ---------------------------------------------------------
# DATASET SETTINGS
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
# COUNT ANNOTATED OBJECTS
# ---------------------------------------------------------

def count_objects(split):

    labels = get_labels(split)

    class_counter = Counter()

    for label in labels:

        try:

            content = label.read_text(
                encoding="utf-8"
            ).strip()

            if not content:
                continue

            for line in content.splitlines():

                parts = line.split()

                if len(parts) != 5:
                    continue

                try:
                    class_id = int(parts[0])
                except ValueError:
                    continue

                class_counter[class_id] += 1

        except Exception:
            continue

    return class_counter


# ---------------------------------------------------------
# COLLECT DATA
# ---------------------------------------------------------

def collect_dataset_statistics():

    image_counts = {}
    object_counts_by_split = {}
    overall_class_counts = Counter()

    for split in SPLITS:

        images = get_images(split)

        image_counts[split] = len(images)

        split_objects = count_objects(split)

        object_counts_by_split[split] = (
            split_objects
        )

        overall_class_counts.update(
            split_objects
        )

    return (
        image_counts,
        object_counts_by_split,
        overall_class_counts,
    )


# ---------------------------------------------------------
# CREATE DIRECTORY
# ---------------------------------------------------------

def create_figure_directory():

    FIGURE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )


# ---------------------------------------------------------
# FIGURE 1
# ---------------------------------------------------------

def plot_image_distribution(image_counts):

    labels = list(image_counts.keys())
    values = list(image_counts.values())

    plt.figure(figsize=(9, 6))

    plt.bar(labels, values)

    plt.title(
        "AGRO LIFE-AI Tomato Dataset: Image Distribution"
    )

    plt.xlabel(
        "Dataset Split"
    )

    plt.ylabel(
        "Number of Images"
    )

    plt.tight_layout()

    output_file = (
        FIGURE_DIRECTORY
        / "01_image_distribution_by_split.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    return output_file


# ---------------------------------------------------------
# FIGURE 2
# ---------------------------------------------------------

def plot_class_distribution(
    overall_class_counts
):

    labels = []
    values = []

    for class_id in sorted(
        overall_class_counts.keys()
    ):

        labels.append(
            CLASS_NAMES.get(
                class_id,
                f"Class {class_id}",
            )
        )

        values.append(
            overall_class_counts[class_id]
        )

    plt.figure(figsize=(9, 6))

    plt.bar(
        labels,
        values,
    )

    plt.title(
        "AGRO LIFE-AI Tomato Dataset: "
        "Annotated Object Distribution"
    )

    plt.xlabel(
        "Original Dataset Class"
    )

    plt.ylabel(
        "Number of Annotated Objects"
    )

    plt.tight_layout()

    output_file = (
        FIGURE_DIRECTORY
        / "02_annotated_object_distribution.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    return output_file


# ---------------------------------------------------------
# FIGURE 3
# ---------------------------------------------------------

def plot_objects_by_split(
    object_counts_by_split
):

    class_ids = sorted(
        {
            class_id
            for split_data
            in object_counts_by_split.values()
            for class_id
            in split_data.keys()
        }
    )

    x_positions = list(
        range(len(SPLITS))
    )

    width = 0.35

    plt.figure(figsize=(10, 6))

    for index, class_id in enumerate(
        class_ids
    ):

        values = [
            object_counts_by_split[
                split
            ].get(
                class_id,
                0,
            )
            for split in SPLITS
        ]

        positions = [
            position
            + (
                index
                - (len(class_ids) - 1) / 2
            )
            * width
            for position
            in x_positions
        ]

        plt.bar(
            positions,
            values,
            width=width,
            label=CLASS_NAMES.get(
                class_id,
                f"Class {class_id}",
            ),
        )

    plt.xticks(
        x_positions,
        SPLITS,
    )

    plt.title(
        "AGRO LIFE-AI Tomato Dataset: "
        "Annotated Objects by Split"
    )

    plt.xlabel(
        "Dataset Split"
    )

    plt.ylabel(
        "Number of Annotated Objects"
    )

    plt.legend()

    plt.tight_layout()

    output_file = (
        FIGURE_DIRECTORY
        / "03_annotated_objects_by_split.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    return output_file


# ---------------------------------------------------------
# FIGURE 4
# ---------------------------------------------------------

def plot_class_percentages(
    overall_class_counts
):

    total = sum(
        overall_class_counts.values()
    )

    labels = []
    percentages = []

    if total == 0:
        return None

    for class_id in sorted(
        overall_class_counts.keys()
    ):

        labels.append(
            CLASS_NAMES.get(
                class_id,
                f"Class {class_id}",
            )
        )

        percentages.append(
            (
                overall_class_counts[class_id]
                / total
            )
            * 100
        )

    plt.figure(figsize=(9, 6))

    plt.bar(
        labels,
        percentages,
    )

    plt.title(
        "AGRO LIFE-AI Tomato Dataset: "
        "Annotated Object Class Percentage"
    )

    plt.xlabel(
        "Original Dataset Class"
    )

    plt.ylabel(
        "Percentage of Annotated Objects (%)"
    )

    plt.tight_layout()

    output_file = (
        FIGURE_DIRECTORY
        / "04_class_percentage_distribution.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    return output_file


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print()
    print("=" * 75)
    print("AGRO LIFE-AI")
    print("COMPUTER VISION DATASET VISUALIZATION")
    print("=" * 75)

    create_figure_directory()

    (
        image_counts,
        object_counts_by_split,
        overall_class_counts,
    ) = collect_dataset_statistics()

    print()
    print("DATASET IMAGE COUNTS")
    print("-" * 75)

    for split in SPLITS:

        print(
            f"{split:<10}: "
            f"{image_counts[split]} images"
        )

    print()
    print("ANNOTATED OBJECT COUNTS")
    print("-" * 75)

    for class_id, count in sorted(
        overall_class_counts.items()
    ):

        class_name = CLASS_NAMES.get(
            class_id,
            f"Class {class_id}",
        )

        print(
            f"Class {class_id} "
            f"({class_name}): "
            f"{count} objects"
        )

    print()
    print("GENERATING FIGURES")
    print("-" * 75)

    figure_1 = plot_image_distribution(
        image_counts
    )

    print(
        f"Created: {figure_1}"
    )

    figure_2 = plot_class_distribution(
        overall_class_counts
    )

    print(
        f"Created: {figure_2}"
    )

    figure_3 = plot_objects_by_split(
        object_counts_by_split
    )

    print(
        f"Created: {figure_3}"
    )

    figure_4 = plot_class_percentages(
        overall_class_counts
    )

    if figure_4:

        print(
            f"Created: {figure_4}"
        )

    print()
    print("=" * 75)
    print(
        "DATASET VISUALIZATION COMPLETED"
    )
    print("=" * 75)

    print()
    print(
        "Original Fresh/Rotten classes preserved."
    )

    print(
        "No automatic four-stage decay relabelling performed."
    )

    print()


if __name__ == "__main__":
    main()