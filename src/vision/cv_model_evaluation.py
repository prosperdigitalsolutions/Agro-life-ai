"""
AGRO LIFE-AI
Computer Vision Model Evaluation and Analysis

Research Prototype

Purpose:
    Convert the baseline Fresh/Rotten classification
    results into a structured research evaluation report.

Important:
    This experiment evaluates binary visual classification
    only. It does not predict shelf life from photographs.
"""

from pathlib import Path
import json


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULT_FILE = (
    PROJECT_ROOT
    / "results"
    / "reports"
    / "computer_vision"
    / "tomato_classifier_results.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "reports"
    / "computer_vision"
    / "tomato_classifier_evaluation.txt"
)


# ---------------------------------------------------------
# LOAD RESULTS
# ---------------------------------------------------------

def load_results():

    if not RESULT_FILE.exists():

        raise FileNotFoundError(
            f"Results file not found: {RESULT_FILE}"
        )

    with RESULT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# ---------------------------------------------------------
# CALCULATE CONFUSION MATRIX VALUES
# ---------------------------------------------------------

def calculate_confusion_values(
    matrix
):

    true_fresh = matrix[0][0]
    fresh_as_rotten = matrix[0][1]

    rotten_as_fresh = matrix[1][0]
    true_rotten = matrix[1][1]

    total = (
        true_fresh
        + fresh_as_rotten
        + rotten_as_fresh
        + true_rotten
    )

    return {
        "true_fresh": true_fresh,
        "fresh_as_rotten": fresh_as_rotten,
        "rotten_as_fresh": rotten_as_fresh,
        "true_rotten": true_rotten,
        "total": total,
    }


# ---------------------------------------------------------
# CREATE INTERPRETATION
# ---------------------------------------------------------

def create_interpretation(
    metrics,
    confusion,
):

    accuracy = metrics["accuracy"]
    precision = metrics["precision"]
    recall = metrics["recall"]
    f1 = metrics["f1_score"]

    interpretation = []

    interpretation.append(
        "The baseline computer-vision classifier "
        "demonstrated measurable ability to distinguish "
        "the original Fresh and Rotten tomato classes."
    )

    interpretation.append(
        f"The classifier achieved an accuracy of "
        f"{accuracy * 100:.2f}% on the test dataset."
    )

    interpretation.append(
        f"Precision was {precision * 100:.2f}%, "
        f"recall was {recall * 100:.2f}%, and the "
        f"F1-score was {f1 * 100:.2f}%."
    )

    interpretation.append(
        f"The classifier correctly identified "
        f"{confusion['true_fresh']} Fresh images and "
        f"{confusion['true_rotten']} Rotten images."
    )

    interpretation.append(
        f"{confusion['fresh_as_rotten']} Fresh images "
        f"were classified as Rotten, while "
        f"{confusion['rotten_as_fresh']} Rotten images "
        f"were classified as Fresh."
    )

    interpretation.append(
        "These results indicate that the image dataset "
        "contains useful visual information for the "
        "binary Fresh/Rotten classification task."
    )

    interpretation.append(
        "The results should not be interpreted as a "
        "shelf-life prediction accuracy because the "
        "classifier was not trained to predict shelf life."
    )

    interpretation.append(
        "The experiment also does not validate the "
        "proposed four-stage decay classification system."
    )

    return interpretation


# ---------------------------------------------------------
# CREATE REPORT
# ---------------------------------------------------------

def create_report(data):

    metrics = data["metrics"]

    confusion = calculate_confusion_values(
        metrics["confusion_matrix"]
    )

    interpretation = create_interpretation(
        metrics,
        confusion,
    )

    lines = []

    lines.append(
        "AGRO LIFE-AI"
    )

    lines.append(
        "COMPUTER VISION MODEL EVALUATION"
    )

    lines.append(
        "=" * 75
    )

    lines.append("")

    lines.append(
        "1. EXPERIMENT"
    )

    lines.append(
        "Binary Tomato Fresh/Rotten Classification"
    )

    lines.append("")

    lines.append(
        "2. DATASET"
    )

    lines.append(
        data.get(
            "dataset",
            "Tomato_Dataset.v5",
        )
    )

    lines.append("")

    lines.append(
        "3. MODEL"
    )

    lines.append(
        data.get(
            "algorithm",
            "Logistic Regression",
        )
    )

    lines.append("")

    lines.append(
        "4. IMAGE SIZE"
    )

    lines.append(
        str(
            data.get(
                "image_size",
                [64, 64],
            )
        )
    )

    lines.append("")

    lines.append(
        "5. EVALUATION METRICS"
    )

    lines.append(
        f"Accuracy : {metrics['accuracy']:.4f}"
    )

    lines.append(
        f"Precision: {metrics['precision']:.4f}"
    )

    lines.append(
        f"Recall   : {metrics['recall']:.4f}"
    )

    lines.append(
        f"F1-score : {metrics['f1_score']:.4f}"
    )

    lines.append("")

    lines.append(
        "6. CONFUSION MATRIX"
    )

    lines.append(
        "                 Predicted"
    )

    lines.append(
        "                 Fresh   Rotten"
    )

    lines.append(
        f"Actual Fresh     "
        f"{confusion['true_fresh']:>5}   "
        f"{confusion['fresh_as_rotten']:>6}"
    )

    lines.append(
        f"Actual Rotten    "
        f"{confusion['rotten_as_fresh']:>5}   "
        f"{confusion['true_rotten']:>6}"
    )

    lines.append("")

    lines.append(
        f"Total evaluated images: "
        f"{confusion['total']}"
    )

    lines.append("")

    lines.append(
        "7. RESULTS INTERPRETATION"
    )

    for item in interpretation:

        lines.append(
            f"- {item}"
        )

    lines.append("")

    lines.append(
        "8. RESEARCH LIMITATIONS"
    )

    lines.append(
        "- The experiment contains only the original "
        "Fresh and Rotten classes."
    )

    lines.append(
        "- It does not provide validated four-stage "
        "decay classification."
    )

    lines.append(
        "- It does not predict shelf life directly "
        "from photographs."
    )

    lines.append(
        "- The external image dataset is separate "
        "from the numerical shelf-life research dataset."
    )

    lines.append(
        "- Further validation with independent and "
        "appropriately labelled data is required."
    )

    lines.append("")

    lines.append(
        "9. RELATIONSHIP TO AGRO LIFE-AI"
    )

    lines.append(
        "The computer-vision experiment provides a "
        "supporting visual-quality classification "
        "component for future AGRO LIFE-AI development."
    )

    lines.append(
        "The current validated shelf-life prediction "
        "model remains based on numerical Day-4 "
        "Weight Loss and Titratable Acidity measurements."
    )

    lines.append("")

    lines.append(
        "10. RESEARCH INTEGRITY STATEMENT"
    )

    lines.append(
        "Original Fresh/Rotten labels were preserved."
    )

    lines.append(
        "No automatic four-stage decay relabelling "
        "was performed."
    )

    lines.append(
        "No claim is made that the current classifier "
        "predicts food safety or shelf life from images."
    )

    lines.append("")

    lines.append(
        "=" * 75
    )

    lines.append(
        "COMPUTER VISION MODEL EVALUATION COMPLETED"
    )

    return "\n".join(lines)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print()
    print("=" * 75)
    print(
        "AGRO LIFE-AI"
    )
    print(
        "COMPUTER VISION MODEL EVALUATION"
    )
    print("=" * 75)

    data = load_results()

    report = create_report(
        data
    )

    OUTPUT_FILE.write_text(
        report,
        encoding="utf-8",
    )

    print()
    print(
        "EVALUATION RESULTS"
    )

    print("-" * 75)

    metrics = data["metrics"]

    print(
        f"Accuracy : "
        f"{metrics['accuracy']:.4f}"
    )

    print(
        f"Precision: "
        f"{metrics['precision']:.4f}"
    )

    print(
        f"Recall   : "
        f"{metrics['recall']:.4f}"
    )

    print(
        f"F1-score : "
        f"{metrics['f1_score']:.4f}"
    )

    print()
    print(
        "Evaluation report saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "Original Fresh/Rotten labels preserved."
    )

    print(
        "No four-stage decay relabelling performed."
    )

    print()
    print(
        "COMPUTER VISION MODEL EVALUATION COMPLETED"
    )


if __name__ == "__main__":
    main()