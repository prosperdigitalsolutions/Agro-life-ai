"""
AGRO LIFE-AI
Computer Vision Decision-Support Module

Part 16A

Purpose:
Convert the current tomato Fresh/Rotten computer-vision
result into a clear decision-support message.

Important research limitation:
The current computer-vision model does NOT predict
shelf life and does NOT certify food safety.

The CV result is therefore kept separate from the
validated numerical shelf-life prediction model.
"""


def generate_cv_decision_support(
    produce_name: str,
    predicted_class: str,
    model_probability: float | None = None,
):
    """
    Generate a research-based decision-support message
    from a computer-vision classification result.
    """

    if not produce_name:
        raise ValueError(
            "Produce name cannot be empty."
        )

    if predicted_class not in {
        "Fresh",
        "Rotten",
    }:
        raise ValueError(
            "Predicted class must be 'Fresh' or 'Rotten'."
        )

    if model_probability is not None:

        if not 0 <= model_probability <= 1:
            raise ValueError(
                "Model probability must be between 0 and 1."
            )

        probability_text = (
            f"{model_probability * 100:.2f}%"
        )

    else:
        probability_text = "Not available"

    if predicted_class == "Fresh":

        visual_status = "VISUALLY CLASSIFIED AS FRESH"

        decision_support = (
            f"The computer-vision model classified the "
            f"{produce_name} image as Fresh with a model "
            f"probability of {probability_text}. "
            f"This result may be used as visual quality "
            f"decision support."
        )

    else:

        visual_status = "VISUALLY CLASSIFIED AS ROTTEN"

        decision_support = (
            f"The computer-vision model classified the "
            f"{produce_name} image as Rotten with a model "
            f"probability of {probability_text}. "
            f"This result indicates an observed visual "
            f"quality concern and may support further "
            f"inspection or handling decisions."
        )

    research_warning = (
        "The current computer-vision result does not "
        "predict remaining shelf life, does not perform "
        "four-stage decay classification, and does not "
        "certify food safety."
    )

    integration_note = (
        "Shelf-life estimation remains a separate "
        "research workflow based on the validated "
        "numerical quality model."
    )

    return {
        "produce_name": produce_name,
        "predicted_class": predicted_class,
        "model_probability": model_probability,
        "model_probability_text": probability_text,
        "visual_status": visual_status,
        "decision_support": decision_support,
        "research_warning": research_warning,
        "integration_note": integration_note,
    }


if __name__ == "__main__":

    print("=" * 70)
    print("AGRO LIFE-AI")
    print("PART 16A - CV DECISION-SUPPORT MODULE TEST")
    print("=" * 70)

    result = generate_cv_decision_support(
        produce_name="Tomato",
        predicted_class="Fresh",
        model_probability=0.9963,
    )

    print()
    print("Produce:")
    print(result["produce_name"])

    print()
    print("Visual Status:")
    print(result["visual_status"])

    print()
    print("Model Probability:")
    print(result["model_probability_text"])

    print()
    print("Decision Support:")
    print(result["decision_support"])

    print()
    print("Research Warning:")
    print(result["research_warning"])

    print()
    print("Integration Note:")
    print(result["integration_note"])

    print()
    print("=" * 70)
    print("PART 16A TEST COMPLETED SUCCESSFULLY")
    print("=" * 70)