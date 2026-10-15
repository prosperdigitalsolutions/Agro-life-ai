"""
AGRO LIFE-AI
Computer Vision Dataset Preparation Module

Research Prototype

Initial produce:
Tomato

Purpose:
Validate the structure and basic quality of the tomato image dataset
before computer vision model training begins.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

IMAGE_ROOT = (
    PROJECT_ROOT
    / "data"
    / "images"
    / "tomato"
)

CLASS_NAMES = [
    "fresh",
    "early_decay",
    "moderate_decay",
    "advanced_decay",
]

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


def get_dataset_directories():
    """
    Return the expected tomato image directories.
    """

    return {
        class_name: IMAGE_ROOT / class_name
        for class_name in CLASS_NAMES
    }


def check_dataset_structure():
    """
    Check whether all required dataset directories exist.
    """

    directories = get_dataset_directories()

    results = {}

    for class_name, directory in directories.items():
        results[class_name] = directory.exists()

    return results


def count_images():
    """
    Count supported image files in each tomato class.
    """

    directories = get_dataset_directories()

    counts = {}

    for class_name, directory in directories.items():

        if not directory.exists():
            counts[class_name] = 0
            continue

        image_count = 0

        for file_path in directory.iterdir():

            if (
                file_path.is_file()
                and file_path.suffix.lower()
                in SUPPORTED_EXTENSIONS
            ):
                image_count += 1

        counts[class_name] = image_count

    return counts


def find_unsupported_files():
    """
    Find files that are not supported image formats.
    """

    directories = get_dataset_directories()

    unsupported = []

    for class_name, directory in directories.items():

        if not directory.exists():
            continue

        for file_path in directory.iterdir():

            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:

                unsupported.append(
                    {
                        "class": class_name,
                        "filename": file_path.name,
                    }
                )

    return unsupported


def display_dataset_report():
    """
    Display a human-readable dataset preparation report.
    """

    print()
    print("=" * 70)
    print("AGRO LIFE-AI COMPUTER VISION DATASET REPORT")
    print("=" * 70)

    print()
    print(f"Produce: Tomato")
    print(f"Image Root: {IMAGE_ROOT}")

    print()
    print("DATASET STRUCTURE")
    print("-" * 70)

    structure = check_dataset_structure()

    for class_name, exists in structure.items():

        status = "READY" if exists else "MISSING"

        print(
            f"{class_name:20} {status}"
        )

    print()
    print("IMAGE COUNTS")
    print("-" * 70)

    counts = count_images()

    total_images = 0

    for class_name, count in counts.items():

        print(
            f"{class_name:20} {count}"
        )

        total_images += count

    print("-" * 70)
    print(
        f"{'TOTAL IMAGES':20} {total_images}"
    )

    print()
    print("UNSUPPORTED FILES")
    print("-" * 70)

    unsupported = find_unsupported_files()

    if unsupported:

        for item in unsupported:

            print(
                f"{item['class']:20} "
                f"{item['filename']}"
            )

    else:

        print("No unsupported files detected.")

    print()
    print("DATASET STATUS")
    print("-" * 70)

    if not all(structure.values()):

        print(
            "INCOMPLETE: One or more required class directories "
            "are missing."
        )

    elif unsupported:

        print(
            "REVIEW REQUIRED: Unsupported files were detected."
        )

    elif total_images == 0:

        print(
            "READY FOR IMAGE COLLECTION: "
            "The dataset structure exists but contains no images yet."
        )

    else:

        print(
            "IMAGE DATASET STRUCTURE IS READY FOR FURTHER PROCESSING."
        )

    print()
    print("=" * 70)


if __name__ == "__main__":

    display_dataset_report()