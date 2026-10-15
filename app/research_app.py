import streamlit as st
from pathlib import Path
import sys
import importlib.util

# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

SRC_DIR = PROJECT_ROOT / "src"
MODEL_DIR = PROJECT_ROOT / "models"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

predict_shelf_life = None

for module_path in [
    SRC_DIR / "models" / "predict_research.py",
    MODEL_DIR / "predict_research.py",
]:
    if module_path.exists():
        spec = importlib.util.spec_from_file_location("predict_research", module_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            predict_shelf_life = getattr(module, "predict_shelf_life", None)
            if predict_shelf_life is not None:
                break

if predict_shelf_life is None:
    raise ImportError(
        "Could not import predict_shelf_life. Check that 'predict_research.py' exists under src/models or models."
    )


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="AGRO LIFE-AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .main {
        background-color: #f7f9fb;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    .hero {
        padding: 2rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #0f5132, #198754);
        color: white;
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        font-size: 2.4rem;
        margin-bottom: 0.3rem;
    }

    .hero p {
        font-size: 1.05rem;
        margin-bottom: 0;
    }

    .section-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #e5e7eb;
        margin-bottom: 1.2rem;
    }

    .result-card {
        background: #ecfdf3;
        border: 1px solid #a7f3d0;
        padding: 1.8rem;
        border-radius: 18px;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .result-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #166534;
    }

    .result-value {
        font-size: 2.8rem;
        font-weight: 800;
        color: #14532d;
        margin-top: 0.4rem;
    }

    .remaining-card {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        padding: 1.8rem;
        border-radius: 18px;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .remaining-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1d4ed8;
    }

    .remaining-value {
        font-size: 2.6rem;
        font-weight: 800;
        color: #1e40af;
        margin-top: 0.4rem;
    }

    .recommendation-card {
        background: white;
        border-left: 6px solid #198754;
        padding: 1.5rem;
        border-radius: 12px;
        margin-top: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .recommendation-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #14532d;
        margin-bottom: 0.8rem;
    }

    .recommendation-item {
        margin-bottom: 0.8rem;
    }

    .status-box {
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        margin: 1rem 0;
    }

    .info-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 1rem;
        border-radius: 12px;
        margin-top: 1rem;
    }

    .footer {
        text-align: center;
        color: #64748b;
        padding: 2rem 0 1rem 0;
        font-size: 0.9rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>AGRO LIFE-AI</h1>
        <p>Produce Decay & Shelf-Life Predictor</p>
        <p>Research Prototype</p>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.header("AGRO LIFE-AI")

    st.write(
        "A research prototype for estimating produce shelf life "
        "from early quality measurements."
    )

    st.divider()

    st.subheader("Research Dataset")

    st.write(
        "The prototype uses an openly available tomato research "
        "dataset containing postharvest quality measurements."
    )

    st.divider()

    st.subheader("Prediction Model")

    st.write("Algorithm: Random Forest Regression")

    st.write("Prediction target: Shelf life in days")

    st.write(
        "Primary model features:"
    )

    st.write(
        "- Day-4 Weight Loss\n"
        "- Day-4 Titratable Acidity"
    )

    st.divider()

    st.info(
        "The farm recommendation is a basic rule-based "
        "decision-support feature. It should not be treated "
        "as a substitute for expert agricultural assessment."
    )


# ---------------------------------------------------------
# ABOUT SYSTEM
# ---------------------------------------------------------

st.markdown(
    """
    <div class="section-card">

    <h2>About the System</h2>

    <p>
    AGRO LIFE-AI investigates the use of data analytics and
    machine learning to estimate the shelf life of fresh produce.
    </p>

    <p>
    The current research prototype uses early quality measurements
    to estimate the total expected shelf life in days.
    </p>

    <p>
    The system then compares the estimated shelf life with the
    number of days the produce has already been stored and provides
    a basic farm decision-support recommendation.
    </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# INPUT SECTION
# ---------------------------------------------------------

st.markdown(
    """
    <div class="section-card">

    <h2>Produce Assessment</h2>

    <p>
    Enter the early quality measurements and the current number
    of days the produce has been stored.
    </p>

    </div>
    """,
    unsafe_allow_html=True
)


col1, col2, col3 = st.columns(3)

with col1:
    weight_loss = st.number_input(
        "Day-4 Weight Loss (%)",
        min_value=0.0,
        max_value=100.0,
        value=1.43,
        step=0.01
    )

with col2:
    titratable_acidity = st.number_input(
        "Day-4 Titratable Acidity (%)",
        min_value=0.0,
        max_value=100.0,
        value=0.74,
        step=0.01
    )

with col3:
    current_storage_days = st.number_input(
        "Current Storage Duration (days)",
        min_value=0.0,
        max_value=365.0,
        value=10.0,
        step=1.0
    )


# ---------------------------------------------------------
# BUTTONS
# ---------------------------------------------------------

col_button1, col_button2 = st.columns(2)

with col_button1:
    predict_button = st.button(
        "Predict Shelf Life",
        use_container_width=True,
        type="primary"
    )

with col_button2:
    reset_button = st.button(
        "Reset Inputs",
        use_container_width=True
    )

if reset_button:
    st.rerun()


# ---------------------------------------------------------
# PREDICTION
# ---------------------------------------------------------

if predict_button:

    try:

        # -------------------------------------------------
        # MODEL PREDICTION
        # -------------------------------------------------

        predicted_shelf_life = predict_shelf_life(
            weight_loss_day4=weight_loss,
            ta_day4=titratable_acidity
        )

        predicted_shelf_life = float(predicted_shelf_life)

        # -------------------------------------------------
        # REMAINING SHELF LIFE
        # -------------------------------------------------

        remaining_days = (
            predicted_shelf_life - current_storage_days
        )

        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        st.markdown(
            f"""
            <div class="result-card">

                <div class="result-title">
                    Estimated Total Shelf Life
                </div>

                <div class="result-value">
                    {predicted_shelf_life:.2f} days
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        # -------------------------------------------------
        # REMAINING SHELF LIFE
        # -------------------------------------------------

        if remaining_days < 0:
            display_remaining = 0
        else:
            display_remaining = remaining_days

        st.markdown(
            f"""
            <div class="remaining-card">

                <div class="remaining-title">
                    Estimated Remaining Shelf Life
                </div>

                <div class="remaining-value">
                    {display_remaining:.2f} days
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        # -------------------------------------------------
        # DECISION-SUPPORT LOGIC
        # -------------------------------------------------

        if remaining_days <= 0:

            status = "ESTIMATED SHELF-LIFE LIMIT REACHED"

            recommendation_title = "Immediate Quality Assessment"

            recommendation_storage = (
                "The estimated shelf-life limit has been reached "
                "or exceeded. Avoid relying on the prediction alone."
            )

            recommendation_monitoring = (
                "Inspect the produce carefully for visible decay, "
                "softening, quality deterioration and loss of marketability."
            )

            recommendation_marketing = (
                "If the produce remains acceptable after inspection, "
                "prioritise appropriate use or marketing rather than "
                "continuing prolonged storage."
            )

        elif remaining_days <= 2:

            status = "VERY LIMITED REMAINING SHELF LIFE"

            recommendation_title = "Prioritise Marketing"

            recommendation_storage = (
                "Avoid unnecessary additional storage where possible."
            )

            recommendation_monitoring = (
                "Increase the frequency of quality and decay checks."
            )

            recommendation_marketing = (
                "Prioritise marketing or appropriate use of the produce "
                "while acceptable quality remains."
            )

        elif remaining_days <= 6:

            status = "MARKETING PERIOD APPROACHING"

            recommendation_title = "Plan Marketing"

            recommendation_storage = (
                "Continue appropriate storage practices and minimise "
                "unnecessary handling."
            )

            recommendation_monitoring = (
                "Monitor visible decay, physical quality and marketability "
                "more frequently."
            )

            recommendation_marketing = (
                "Begin planning or prioritising sale before the estimated "
                "shelf-life limit is reached."
            )

        elif remaining_days <= 14:

            status = "MONITOR AND PLAN"

            recommendation_title = "Increase Monitoring"

            recommendation_storage = (
                "Continue suitable storage practices."
            )

            recommendation_monitoring = (
                "Monitor quality regularly and record noticeable changes."
            )

            recommendation_marketing = (
                "Start planning the marketing period based on the "
                "estimated remaining shelf life."
            )

        else:

            status = "NORMAL MONITORING PERIOD"

            recommendation_title = "Continue Monitoring"

            recommendation_storage = (
                "Continue appropriate storage and handling practices."
            )

            recommendation_monitoring = (
                "Perform regular quality checks for early signs of "
                "decay or deterioration."
            )

            recommendation_marketing = (
                "Use the estimated remaining shelf life to support "
                "future marketing planning."
            )

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        st.markdown(
            f"""
            <div class="status-box">
                {status}
            </div>
            """,
            unsafe_allow_html=True
        )

        # -------------------------------------------------
        # RECOMMENDATIONS
        # -------------------------------------------------

        st.markdown(
            f"""
            <div class="recommendation-card">

                <div class="recommendation-title">
                    {recommendation_title}
                </div>

                <div class="recommendation-item">
                    <strong>Storage:</strong><br>
                    {recommendation_storage}
                </div>

                <div class="recommendation-item">
                    <strong>Monitoring:</strong><br>
                    {recommendation_monitoring}
                </div>

                <div class="recommendation-item">
                    <strong>Marketing:</strong><br>
                    {recommendation_marketing}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        # -------------------------------------------------
        # CALCULATION DETAILS
        # -------------------------------------------------

        st.markdown(
            f"""
            <div class="info-box">

            <strong>Calculation:</strong>

            Estimated shelf life =
            <strong>{predicted_shelf_life:.2f} days</strong>

            <br><br>

            Current storage duration =
            <strong>{current_storage_days:.2f} days</strong>

            <br><br>

            Estimated remaining shelf life =
            <strong>{predicted_shelf_life:.2f}
            − {current_storage_days:.2f}
            = {remaining_days:.2f} days</strong>

            </div>
            """,
            unsafe_allow_html=True
        )

        # -------------------------------------------------
        # IMPORTANT NOTICE
        # -------------------------------------------------

        st.warning(
            "This recommendation is a basic research decision-support "
            "rule based on the model's estimated shelf life and the "
            "entered storage duration. Actual produce condition may "
            "differ and should be assessed directly."
        )

    except Exception as e:

        st.error(
            f"Prediction error: {e}"
        )


# ---------------------------------------------------------
# MODEL INFORMATION
# ---------------------------------------------------------

st.divider()

st.markdown(
    """
    <div class="section-card">

    <h2>Model Information</h2>

    <p>
    The selected research model is a Random Forest Regression model
    using Day-4 Weight Loss and Day-4 Titratable Acidity.
    </p>

    <p>
    The model was evaluated using GroupKFold cross-validation because
    the research dataset contains repeated observations from treatment
    groups.
    </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# FEATURE IMPORTANCE
# ---------------------------------------------------------

st.subheader("Model Feature Importance")

feature_col1, feature_col2 = st.columns(2)

with feature_col1:

    st.metric(
        "Day-4 Weight Loss",
        "61.55%"
    )

with feature_col2:

    st.metric(
        "Day-4 Titratable Acidity",
        "38.45%"
    )


# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------

st.subheader("Research Model Validation")

validation_col1, validation_col2, validation_col3 = st.columns(3)

with validation_col1:
    st.metric(
        "Mean MAE",
        "0.7422 days"
    )

with validation_col2:
    st.metric(
        "Mean RMSE",
        "0.9930 days"
    )

with validation_col3:
    st.metric(
        "Mean R²",
        "0.1238"
    )


st.caption(
    "Validation results are based on GroupKFold cross-validation "
    "on the research dataset. They should not be interpreted as "
    "universal prediction accuracy."
)


# ---------------------------------------------------------
# SYSTEM WORKFLOW
# ---------------------------------------------------------

st.subheader("System Workflow")

st.write(
    """
    Research Data → Data Verification → Feature Selection →
    Machine Learning → Shelf-Life Prediction →
    Remaining Shelf-Life Calculation → Basic Farm Recommendation
    """
)


# ---------------------------------------------------------
# LIMITATIONS
# ---------------------------------------------------------

st.subheader("Research Limitations")

st.info(
    """
    The current prototype is based on a specific tomato research
    dataset. It does not currently include temperature, humidity,
    soil conditions, weather data, IoT sensors or laboratory
    microbiological measurements.

    The farm recommendation is therefore a basic decision-support
    function and should not be interpreted as a universal agricultural
    advisory system.
    """
)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown(
    """
    <div class="footer">

    <strong>AGRO LIFE-AI</strong><br>

    Design and Development of a Produce Decay and Shelf-Life
    Prediction System Using Data Analytics and Machine Learning

    <br><br>

    Research Prototype — DMI St. Eugene University

    </div>
    """,
    unsafe_allow_html=True
)