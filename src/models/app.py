"""
AGRO LIFE-AI
Interactive Prototype Interface

Biochemical Decay & Shelf-Life Predictor
DMI St. Eugene University
BSc Computer Science - Mini Project
"""

from pathlib import Path
import sys

import streamlit as st


# ---------------------------------------------------------
# PROJECT PATH
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from models.predict import (
    load_model,
    prepare_input,
    predict_shelf_life,
)


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="AGRO LIFE-AI",
    page_icon="AGRO",
    layout="centered",
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("AGRO LIFE-AI")

st.subheader(
    "Biochemical Decay & Shelf-Life Predictor"
)

st.write(
    "Agriculture + Data Analytics + Machine Learning"
)

st.divider()


# ---------------------------------------------------------
# PROJECT INFORMATION
# ---------------------------------------------------------

st.markdown(
    """
### About the Prototype

AGRO LIFE-AI is a BSc Computer Science mini-project
prototype designed to estimate the shelf life of
agricultural produce using environmental, storage,
quality and produce-related information.

The prototype uses a trained Random Forest regression
model to generate an estimated shelf-life value.
"""
)


# ---------------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------------

try:

    model = load_model()

except FileNotFoundError as error:

    st.error(str(error))

    st.stop()


# ---------------------------------------------------------
# USER INPUTS
# ---------------------------------------------------------

st.header("Produce Information")

produce_type = st.selectbox(
    "Select Produce Type",
    [
        "Tomato",
        "Mango",
        "Banana",
    ]
)


initial_weight_g = st.number_input(
    "Initial Weight (g)",
    min_value=1.0,
    value=1000.0,
    step=50.0
)


temperature_c = st.number_input(
    "Temperature (°C)",
    min_value=-10.0,
    max_value=60.0,
    value=28.0,
    step=0.5
)


humidity_percent = st.number_input(
    "Humidity (%)",
    min_value=0.0,
    max_value=100.0,
    value=78.0,
    step=1.0
)


storage_days = st.number_input(
    "Current Storage Duration (Days)",
    min_value=0.0,
    max_value=365.0,
    value=2.0,
    step=1.0
)


weight_loss_percent = st.number_input(
    "Weight Loss (%)",
    min_value=0.0,
    max_value=100.0,
    value=4.0,
    step=0.5
)


quality_score = st.slider(
    "Quality Score",
    min_value=1,
    max_value=10,
    value=8
)


# ---------------------------------------------------------
# PREDICTION
# ---------------------------------------------------------

st.divider()

predict_button = st.button(
    "Predict Shelf Life",
    type="primary",
    use_container_width=True
)


if predict_button:

    input_data = prepare_input(
        produce_type,
        initial_weight_g,
        temperature_c,
        humidity_percent,
        storage_days,
        weight_loss_percent,
        quality_score
    )

    predicted_shelf_life = predict_shelf_life(
        model,
        input_data
    )

    st.success(
        "Prediction completed successfully."
    )

    st.metric(
        label="Estimated Shelf Life",
        value=f"{predicted_shelf_life:.2f} days"
    )

    st.info(
        "This is a prototype prediction based on "
        "the current development dataset and trained model. "
        "It should not be interpreted as a validated "
        "real-world agricultural measurement."
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "AGRO LIFE-AI | BSc Computer Science Mini Project"
)

st.caption(
    "DMI St. Eugene University"
)

st.caption(
    "Developed by Prosper Chungu Mwape"
)