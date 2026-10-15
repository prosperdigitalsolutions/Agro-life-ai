"""
AGRO LIFE-AI
Computer Vision Dataset Manifest Generator

Research Prototype

Purpose:
    Create a traceable manifest for the imported external
    tomato computer-vision dataset.

The manifest records:
    - Image ID
    - Filename
    - Dataset split
    - Original class
    - Image path
    - Label path
    - Source dataset
    - Licence

Important:
    Original Fresh/Rotten classes are preserved.
    No automatic decay-stage relabelling is performed.
"""

from pathlib import Path
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

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "images"
)

MANIFEST_FILE = (
    OUTPUT_DIRECTORY
    / "external_tomato_dataset_manifest.csv"
)


# ---------------------------------------------------------
# DATASET INFORMATION
# ---------------------------------------------------------

DATASET_NAME = "Tomato_Dataset V5"

SOURCE_URL = (
    "https://universe.roboflow.com/"
    "arafatislam1811-gmail-com/"
    "tomato_dataset-ku7jj"
)

LICENSE = "CC BY 4.0"

PRODUCE = "Tomato"

CLASS_NAMES = {
    0: "Fresh",
    1: "Rotten",
}


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
# FIND IMAGES
# ---------------------------------------------------------

def get_images(split):
    """
    Return all supported images for a dataset split.
    """

    image_directory = (
        DATASET_ROOT
        / split
        / "images"
    )

    if not image_directory.exists():
        return []

    return sorted(
        [
            file
            for file in image_directory.iterdir()
            if (
                file.is_file()
                and file.suffix.lower()
                in IMAGE_EXTENSIONS
            )
        ],
        key=lambda file: file.name.lower(),
    )


# ---------------------------------------------------------
# READ YOLO LABEL
# ---------------------------------------------------------

def get_original_classes(label_path):
    """
    Read class IDs from a YOLO label file.

    Returns unique class names found in the label.
    """

    if not label_path.exists():
        return "No label"

    classes = set()

    try:

        content = label_path.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            return "Empty label"

        for line in content.splitlines():

            parts = line.split()

            if not parts:
                continue

            try:
                class_id = int(parts[0])
            except ValueError:
                continue

            class_name = CLASS_NAMES.get(
                class_id,
                f"Unknown class {class_id}",
            )

            classes.add(class_name)

    except Exception:
        return "Unreadable label"

    if not classes:
        return "No class detected"

    return "; ".join(sorted(classes))


# ---------------------------------------------------------
# GENERATE MANIFEST
# ---------------------------------------------------------

def generate_manifest():

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    records = []

    image_number = 1

    for split in SPLITS:

        images = get_images(split)

        for image_path in images:

            label_path = (
                DATASET_ROOT
                / split
                / "labels"
                / f"{image_path.stem}.txt"
            )

            class_name = get_original_classes(
                label_path
            )

            record = {
                "image_id": (
                    f"TOM-CV-{image_number:05d}"
                ),
                "filename": image_path.name,
                "produce": PRODUCE,
                "dataset_split": split,
                "original_class": class_name,
                "image_path": str(
                    image_path.relative_to(
                        PROJECT_ROOT
                    )
                ),
                "label_path": (
                    str(
                        label_path.relative_to(
                            PROJECT_ROOT
                        )
                    )
                    if label_path.exists()
                    else ""
                ),
                "dataset_name": DATASET_NAME,
                "source_url": SOURCE_URL,
                "licence": LICENSE,
            }

            records.append(record)

            image_number += 1

    fieldnames = [
        "image_id",
        "filename",
        "produce",
        "dataset_split",
        "original_class",
        "image_path",
        "label_path",
        "dataset_name",
        "source_url",
        "licence",
    ]

    with MANIFEST_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(records)

    return records


# ---------------------------------------------------------
# DISPLAY SUMMARY
# ---------------------------------------------------------

def display_summary(records):

    print()
    print("=" * 75)
    print("AGRO LIFE-AI")
    print("COMPUTER VISION DATASET MANIFEST")
    print("=" * 75)

    print()
    print(
        f"Manifest records: {len(records)}"
    )

    print()
    print("SPLIT DISTRIBUTION")
    print("-" * 75)

    for split in SPLITS:

        count = sum(
            1
            for record in records
            if record["dataset_split"] == split
        )

        print(
            f"{split:<10}: {count} images"
        )

    print()
    print("ORIGINAL CLASS DISTRIBUTION")
    print("-" * 75)

    class_counts = {}

    for record in records:

        class_name = record["original_class"]

        class_counts[class_name] = (
            class_counts.get(
                class_name,
                0,
            )
            + 1
        )

    for class_name, count in sorted(
        class_counts.items()
    ):

        print(
            f"{class_name:<20}: {count} images"
        )

    print()
    print("MANIFEST FILE")
    print("-" * 75)
    print(MANIFEST_FILE)

    print()
    print("DATASET POLICY")
    print("-" * 75)
    print(
        "Original Fresh/Rotten classes preserved."
    )
    print(
        "No automatic four-stage decay relabelling performed."
    )

    print()
    print("=" * 75)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print()
    print(
        "AGRO LIFE-AI DATASET MANIFEST GENERATOR"
    )

    records = generate_manifest()

    display_summary(records)

    print()
    print(
        "DATASET MANIFEST CREATED SUCCESSFULLY"
    )
    print()


if __name__ == "__main__":
    main()