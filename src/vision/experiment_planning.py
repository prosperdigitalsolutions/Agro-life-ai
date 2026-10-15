"""
AGRO LIFE-AI
Computer Vision Experiment Planning Module

Research Prototype

Purpose:
    Document and evaluate the computer-vision experiments
    that are scientifically appropriate for the currently
    available tomato image dataset.

Important research decision:
    The external dataset contains original Fresh/Rotten
    classes. It does NOT contain validated:
        Fresh
        Early Decay
        Moderate Decay
        Advanced Decay

    Therefore, the current dataset must NOT be automatically
    relabelled into four decay stages.

    The existing shelf-life prediction model remains based
    on numerical Day-4 research measurements.
"""

from pathlib import Path


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_DIRECTORY = (
    PROJECT_ROOT
    / "results"
    / "reports"
    / "computer_vision"
)

REPORT_FILE = (
    REPORT_DIRECTORY
    / "computer_vision_experiment_plan.txt"
)


# ---------------------------------------------------------
# DATASET INFORMATION
# ---------------------------------------------------------

DATASET_NAME = "Tomato_Dataset.v5"

ORIGINAL_CLASSES = [
    "Fresh",
    "Rotten",
]

PROPOSED_AGRO_LIFE_CLASSES = [
    "Fresh",
    "Early Decay",
    "Moderate Decay",
    "Advanced Decay",
]


# ---------------------------------------------------------
# EXPERIMENT DECISIONS
# ---------------------------------------------------------

def get_experiment_plan():

    return {
        "dataset": DATASET_NAME,

        "available_classes": ORIGINAL_CLASSES,

        "proposed_classes": (
            PROPOSED_AGRO_LIFE_CLASSES
        ),

        "supported_experiment": (
            "Binary tomato visual-quality "
            "classification using the original "
            "Fresh and Rotten labels."
        ),

        "unsupported_experiment": (
            "Four-stage decay classification using "
            "Fresh, Early Decay, Moderate Decay, "
            "and Advanced Decay labels."
        ),

        "shelf_life_integration": (
            "The current validated shelf-life model "
            "uses numerical Day-4 Weight Loss and "
            "Titratable Acidity measurements. "
            "The current image dataset does not "
            "contain linked shelf-life targets."
        ),

        "future_experiment": (
            "Develop and validate a four-stage "
            "computer-vision dataset with properly "
            "labelled tomato images representing "
            "different visible decay stages."
        ),
    }


# ---------------------------------------------------------
# DISPLAY PLAN
# ---------------------------------------------------------

def display_experiment_plan():

    plan = get_experiment_plan()

    print()
    print("=" * 75)
    print("AGRO LIFE-AI")
    print("COMPUTER VISION EXPERIMENT PLANNING")
    print("=" * 75)

    print()
    print("DATASET")
    print("-" * 75)
    print(plan["dataset"])

    print()
    print("ORIGINAL DATASET CLASSES")
    print("-" * 75)

    for class_name in plan["available_classes"]:
        print(f"- {class_name}")

    print()
    print("PROPOSED AGRO LIFE-AI DECAY CLASSES")
    print("-" * 75)

    for class_name in plan["proposed_classes"]:
        print(f"- {class_name}")

    print()
    print("SUPPORTED EXPERIMENT")
    print("-" * 75)
    print(plan["supported_experiment"])

    print()
    print("UNSUPPORTED EXPERIMENT")
    print("-" * 75)
    print(plan["unsupported_experiment"])

    print()
    print("SHELF-LIFE INTEGRATION")
    print("-" * 75)
    print(plan["shelf_life_integration"])

    print()
    print("FUTURE EXPERIMENT")
    print("-" * 75)
    print(plan["future_experiment"])

    print()
    print("=" * 75)
    print("RESEARCH INTEGRITY DECISION")
    print("=" * 75)

    print(
        "The current image dataset will not be "
        "automatically relabelled."
    )

    print(
        "Original Fresh/Rotten labels will remain "
        "unchanged."
    )

    print(
        "The current image dataset will not be used "
        "as a direct shelf-life target dataset."
    )

    print(
        "Four-stage decay classification requires "
        "a separately labelled and validated dataset."
    )

    print()
    print(
        "COMPUTER VISION EXPERIMENT PLAN COMPLETED"
    )
    print()


# ---------------------------------------------------------
# SAVE REPORT
# ---------------------------------------------------------

def save_experiment_plan():

    REPORT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    plan = get_experiment_plan()

    lines = []

    lines.append(
        "AGRO LIFE-AI"
    )

    lines.append(
        "COMPUTER VISION EXPERIMENT PLAN"
    )

    lines.append(
        "=" * 75
    )

    lines.append("")

    lines.append(
        "1. DATASET"
    )

    lines.append(
        f"Dataset: {plan['dataset']}"
    )

    lines.append("")

    lines.append(
        "2. ORIGINAL DATASET CLASSES"
    )

    for class_name in plan["available_classes"]:
        lines.append(
            f"- {class_name}"
        )

    lines.append("")

    lines.append(
        "3. PROPOSED AGRO LIFE-AI DECAY CLASSES"
    )

    for class_name in plan["proposed_classes"]:
        lines.append(
            f"- {class_name}"
        )

    lines.append("")

    lines.append(
        "4. SUPPORTED EXPERIMENT"
    )

    lines.append(
        plan["supported_experiment"]
    )

    lines.append("")

    lines.append(
        "5. UNSUPPORTED EXPERIMENT"
    )

    lines.append(
        plan["unsupported_experiment"]
    )

    lines.append("")

    lines.append(
        "6. SHELF-LIFE INTEGRATION"
    )

    lines.append(
        plan["shelf_life_integration"]
    )

    lines.append("")

    lines.append(
        "7. FUTURE EXPERIMENT"
    )

    lines.append(
        plan["future_experiment"]
    )

    lines.append("")

    lines.append(
        "8. RESEARCH INTEGRITY DECISION"
    )

    lines.append(
        "The current image dataset will not be "
        "automatically relabelled."
    )

    lines.append(
        "Original Fresh/Rotten labels will remain "
        "unchanged."
    )

    lines.append(
        "The current image dataset will not be used "
        "as a direct shelf-life target dataset."
    )

    lines.append(
        "Four-stage decay classification requires "
        "a separately labelled and validated dataset."
    )

    REPORT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return REPORT_FILE


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    display_experiment_plan()

    report_file = save_experiment_plan()

    print(
        f"Experiment plan saved to:"
    )

    print(
        report_file
    )

    print()


if __name__ == "__main__":
    main()