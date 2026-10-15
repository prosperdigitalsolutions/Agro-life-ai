"""
AGRO LIFE-AI
Tomato Image Metadata Registry

Computer Vision Research Module

Purpose:
Maintain traceable metadata for every tomato image used
in the AGRO LIFE-AI computer vision research dataset.
"""

from pathlib import Path
import csv
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parents[2]

IMAGE_ROOT = (
    PROJECT_ROOT
    / "data"
    / "images"
    / "tomato"
)

METADATA_ROOT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "images"
)

METADATA_FILE = (
    METADATA_ROOT
    / "tomato_image_metadata.csv"
)

CLASS_NAMES = [
    "fresh",
    "early_decay",
    "moderate_decay",
    "advanced_decay",
]

FIELDNAMES = [
    "image_id",
    "filename",
    "produce",
    "class_name",
    "source",
    "source_url",
    "licence_permission",
    "capture_date",
    "notes",
]


def create_metadata_directory():
    """
    Create the metadata directory if it does not exist.
    """

    METADATA_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )


def create_metadata_file():
    """
    Create an empty metadata CSV file with the required headers.
    """

    create_metadata_directory()

    if not METADATA_FILE.exists():

        with open(
            METADATA_FILE,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=FIELDNAMES,
            )

            writer.writeheader()


def get_existing_records():
    """
    Load existing image metadata records.
    """

    create_metadata_file()

    with open(
        METADATA_FILE,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        return list(reader)


def generate_image_id():
    """
    Generate the next tomato image ID.
    """

    records = get_existing_records()

    if not records:
        return "TOM-0001"

    numbers = []

    for record in records:

        image_id = record.get(
            "image_id",
            "",
        )

        if image_id.startswith("TOM-"):

            try:

                number = int(
                    image_id.replace(
                        "TOM-",
                        "",
                    )
                )

                numbers.append(number)

            except ValueError:
                pass

    if not numbers:
        return "TOM-0001"

    next_number = max(numbers) + 1

    return f"TOM-{next_number:04d}"


def validate_class(class_name):
    """
    Validate the tomato image class.
    """

    if class_name not in CLASS_NAMES:

        raise ValueError(
            f"Invalid class '{class_name}'. "
            f"Valid classes are: {', '.join(CLASS_NAMES)}"
        )

    return True


def register_image(
    filename,
    class_name,
    source,
    source_url="",
    licence_permission="",
    capture_date="",
    notes="",
):
    """
    Register one tomato image in the metadata registry.
    """

    validate_class(class_name)

    image_directory = (
        IMAGE_ROOT
        / class_name
    )

    image_path = (
        image_directory
        / filename
    )

    if not image_path.exists():

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    records = get_existing_records()

    for record in records:

        if record["filename"] == filename:

            raise ValueError(
                f"Image '{filename}' is already registered."
            )

    image_id = generate_image_id()

    if not capture_date:

        capture_date = datetime.now().strftime(
            "%Y-%m-%d"
        )

    record = {
        "image_id": image_id,
        "filename": filename,
        "produce": "Tomato",
        "class_name": class_name,
        "source": source,
        "source_url": source_url,
        "licence_permission": licence_permission,
        "capture_date": capture_date,
        "notes": notes,
    }

    with open(
        METADATA_FILE,
        "a",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES,
        )

        writer.writerow(record)

    return record


def count_registered_images():
    """
    Count registered images by class.
    """

    records = get_existing_records()

    counts = {
        class_name: 0
        for class_name in CLASS_NAMES
    }

    for record in records:

        class_name = record.get(
            "class_name",
            "",
        )

        if class_name in counts:

            counts[class_name] += 1

    return counts


def display_metadata_report():
    """
    Display the current image metadata registry status.
    """

    records = get_existing_records()
    counts = count_registered_images()

    print()
    print("=" * 70)
    print("AGRO LIFE-AI TOMATO IMAGE METADATA REGISTRY")
    print("=" * 70)

    print()
    print(f"Metadata File:")
    print(METADATA_FILE)

    print()
    print("IMAGE COUNTS BY CLASS")
    print("-" * 70)

    total = 0

    for class_name in CLASS_NAMES:

        count = counts[class_name]

        print(
            f"{class_name:20} {count}"
        )

        total += count

    print("-" * 70)

    print(
        f"{'TOTAL REGISTERED':20} {total}"
    )

    print()
    print("REGISTRY STATUS")
    print("-" * 70)

    if not records:

        print(
            "READY FOR IMAGE REGISTRATION: "
            "No images have been registered yet."
        )

    else:

        print(
            f"{len(records)} image metadata record(s) "
            "currently registered."
        )

    print()
    print("=" * 70)


if __name__ == "__main__":

    create_metadata_file()

    display_metadata_report()