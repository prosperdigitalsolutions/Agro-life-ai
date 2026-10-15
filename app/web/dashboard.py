
"""
AGRO LIFE-AI
Produce Decay & Shelf-Life Predictor
Research Prototype

Main Streamlit Dashboard

Users:
    - Farmer
    - Customer

Current validated prediction model:
    - Tomato

Future development:
    - Camera-based computer vision
    - Additional produce-specific models
    - Mobile application
"""

from pathlib import Path

import streamlit as st

from src.users.user_manager import (
    register_user,
    get_user_profile,
)

from src.database.database_manager import (
    get_all_produce,
)

from src.database.produce_manager import (
    get_produce_registry,
    get_produce_status,
)

from src.core.user_prediction_workflow import (
    run_user_prediction_workflow,
)

from src.customers.customer_decision_support import (
    generate_customer_decision_support,
)

from src.customers.customer_camera import (
    get_camera_assessment_status,
    describe_camera_assessment,
)
from src.vision.camera_assessment import (
    process_camera_image,
)
from src.vision.camera_assessment import (
    process_camera_image,
)

from src.records.history_manager import (
    get_prediction_history,
)

from src.vision.cv_history_manager import (
    get_cv_history,
    delete_cv_prediction_record,
)

from src.customers.cv_decision_support import (
    generate_cv_decision_support,
)
# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AGRO LIFE-AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .sub-title {
        font-size: 18px;
        margin-top: 0;
        color: #666666;
    }

    .section-title {
        font-size: 28px;
        font-weight: 700;
        margin-top: 20px;
    }

    .status-box {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #dddddd;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .metric-label {
        font-size: 14px;
        color: #666666;
    }

    .metric-value {
        font-size: 26px;
        font-weight: 700;
    }

    .footer {
        text-align: center;
        color: #777777;
        font-size: 13px;
        padding-top: 30px;
        padding-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_type" not in st.session_state:
    st.session_state.user_type = None

if "full_name" not in st.session_state:
    st.session_state.full_name = ""

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None

if "camera_result" not in st.session_state:
    st.session_state.camera_result = None

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def logout_user():
    """
    Log out the current user.
    """

    st.session_state.user_id = None
    st.session_state.user_type = None
    st.session_state.full_name = ""
    st.session_state.page = "Dashboard"
    st.session_state.last_prediction = None


def display_header():
    """
    Display the main AGRO LIFE-AI header.
    """

    st.markdown(
        '<div class="main-title">AGRO LIFE-AI</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sub-title">'
        'Produce Decay & Shelf-Life Predictor '
        '— Research Prototype'
        '</div>',
        unsafe_allow_html=True,
    )

    st.divider()


def display_footer():
    """
    Display application footer.
    """

    st.markdown(
        '<div class="footer">'
        'AGRO LIFE-AI — Produce Decay & Shelf-Life Predictor'
        '<br>'
        'Research Prototype | Data Analytics | Machine Learning '
        '| Computer Vision Future Development'
        '</div>',
        unsafe_allow_html=True,
    )


def display_produce_registry_section():
    """
    Display the current produce registry.
    """

    st.subheader("Produce Availability")

    registry = get_produce_registry()

    if not registry:
        st.warning("No produce has been registered.")
        return

    for item in registry:

        if item["prediction_available"]:

            st.success(
                f'{item["produce_name"]} — '
                'Validated Model Available'
            )

        else:

            st.info(
                f'{item["produce_name"]} — '
                'Model Development'
            )


def display_produce_registry_table():
    """
    Display a compact produce registry table.
    """

    registry = get_produce_registry()

    if not registry:

        st.warning("No produce records are available.")

        return

    table_data = []

    for item in registry:

        if item["prediction_available"]:

            prediction_status = "Model Available"

        else:

            prediction_status = "Model Development"

        table_data.append(
            {
                "Produce": item["produce_name"],
                "Category": item["category"],
                "Prediction Status": prediction_status,
            }
        )

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():
    """
    Display user login interface.
    """

    st.title("AGRO LIFE-AI Login")

    st.write(
        "Enter your registered User ID to access "
        "the AGRO LIFE-AI research prototype."
    )

    user_id = st.number_input(
        "User ID",
        min_value=1,
        step=1,
        value=1,
    )

    if st.button(
        "Login",
        use_container_width=True,
    ):

        user = get_user_profile(int(user_id))

        if user is None:

            st.error(
                "User not found. Please check your User ID."
            )

        else:

            if isinstance(user, tuple):

                st.session_state.user_id = user[0]
                st.session_state.full_name = user[1]
                st.session_state.user_type = user[2]

            else:

                st.session_state.user_id = user["user_id"]
                st.session_state.full_name = user["full_name"]
                st.session_state.user_type = user["user_type"]

            st.session_state.page = "Dashboard"

            st.success(
                "Login successful."
            )

            st.rerun()


# ============================================================
# REGISTRATION PAGE
# ============================================================

def registration_page():
    """
    Display registration interface.
    """

    st.title("Create AGRO LIFE-AI Account")

    full_name = st.text_input(
        "Full Name"
    )

    user_type = st.selectbox(
        "User Type",
        [
            "farmer",
            "customer",
        ],
    )

    phone = st.text_input(
        "Phone Number"
    )

    email = st.text_input(
        "Email Address"
    )

    if st.button(
        "Register",
        use_container_width=True,
    ):

        if not full_name.strip():

            st.error(
                "Please enter your full name."
            )

            return

        try:

            user_id = register_user(
                full_name=full_name.strip(),
                user_type=user_type,
                phone=phone.strip() or None,
                email=email.strip() or None,
            )

            st.success(
                f"Registration successful. "
                f"Your User ID is {user_id}."
            )

            st.info(
                "Please keep your User ID for login."
            )

        except Exception as error:

            st.error(
                f"Registration failed: {error}"
            )


# ============================================================
# SIDEBAR
# ============================================================

def display_sidebar():
    """
    Display sidebar navigation.
    """

    with st.sidebar:

        st.title("AGRO LIFE-AI")

        st.caption(
            "Produce Decay & Shelf-Life Predictor"
        )

        st.divider()

        if st.session_state.user_id is None:

            st.subheader("Access")

            access = st.radio(
                "Select",
                [
                    "Login",
                    "Register",
                ],
            )

            if access == "Login":

                return "Login"

            return "Register"

        # ----------------------------------------------------
        # LOGGED-IN USER
        # ----------------------------------------------------

        st.subheader("User")

        st.write(
            f"**{st.session_state.full_name}**"
        )

        st.write(
            f"User Type: "
            f"**{st.session_state.user_type.title()}**"
        )

        st.write(
            f"User ID: "
            f"**{st.session_state.user_id}**"
        )

        st.divider()

        if st.session_state.user_type == "customer":

            navigation_options = [
                "Dashboard",
                "Camera Assessment",
                "Prediction",
                "History",
                "About AGRO LIFE-AI",
            ]

        else:

            navigation_options = [
                "Dashboard",
                "Produce Management",
                "Prediction",
                "History",
                "About AGRO LIFE-AI",
            ]

        selected_page = st.radio(
            "Navigation",
            navigation_options,
        )

        st.session_state.page = selected_page

        st.divider()

        if st.button(
            "Logout",
            use_container_width=True,
        ):

            logout_user()
            st.rerun()

        return None


# ============================================================
# FARMER DASHBOARD
# ============================================================

def farmer_dashboard():
    """
    Display farmer dashboard.
    """

    st.title(
        "Farmer Dashboard"
    )

    st.write(
        "Welcome to AGRO LIFE-AI. "
        "Use research-based shelf-life estimates to "
        "support produce storage, monitoring, and "
        "marketing planning."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Validated Produce",
            "Tomato",
        )

    with col2:

        st.metric(
            "Prediction Model",
            "Available",
        )

    with col3:

        st.metric(
            "Decision Support",
            "Available",
        )

    st.divider()

    display_produce_registry_section()

    st.divider()

    st.subheader(
        "Farmer Workflow"
    )

    st.write(
        "1. Select a supported produce."
    )

    st.write(
        "2. Enter the required research quality measurements."
    )

    st.write(
        "3. Enter the current storage duration."
    )

    st.write(
        "4. Estimate total and remaining shelf life."
    )

    st.write(
        "5. Use the Farmer Recommendation for planning."
    )

    st.divider()

    st.info(
        "Current validated prediction is based on "
        "the tomato research dataset. Additional produce "
        "models require separate data and validation."
    )


# ============================================================
# CUSTOMER DASHBOARD
# ============================================================

def customer_dashboard():
    """
    Display customer dashboard.
    """

    st.title(
        "Customer Decision-Support Dashboard"
    )

    st.write(
        "AGRO LIFE-AI provides research-based shelf-life "
        "decision support for customers and buyers."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Current Validated Produce",
            "Tomato",
        )

    with col2:

        st.metric(
            "Current Prediction Model",
            "Available",
        )

    with col3:

        st.metric(
            "Future Vision",
            "Planned",
        )

    st.divider()

    st.subheader(
        "Customer Assessment"
    )

    st.write(
        "Customers will be able to use produce information "
        "and future camera-based assessment to support "
        "purchasing decisions."
    )

    st.warning(
        "The current validated model does not analyse "
        "photographs or certify food safety."
    )

    st.divider()

    display_produce_registry_section()

    st.divider()

    st.subheader(
        "Future Camera Workflow"
    )

    st.write(
        "Camera Capture → Computer Vision → "
        "Produce Identification → Quality Assessment → "
        "Shelf-Life Estimation → Customer Decision Support"
    )

st.divider()

st.subheader("Computer Vision Assessment History")

st.caption(
    "Previous camera-based visual assessments recorded by "
    "AGRO LIFE-AI."
)

cv_history = get_cv_history()

if not cv_history:

    st.info(
        "No computer vision assessment records are "
        "available yet."
    )

else:

    st.write(
        f"Total computer vision assessments: "
        f"{len(cv_history)}"
    )

    st.divider()

    st.subheader("Assessment Management")

    for index, record in enumerate(cv_history):

        confirm_delete = st.checkbox(
            "I confirm that I want to permanently delete this assessment.",
            key=f"confirm_delete_cv_{index}"
        )

        if st.button(
            "Delete This Assessment",
            key=f"delete_cv_assessment_{index}",
            use_container_width=True,
        ):

            if not confirm_delete:

                st.warning(
                    "Please confirm deletion before deleting this assessment."
                )

            else:

                try:

                    result = delete_cv_prediction_record(record)

                    if result["success"]:

                        st.success(result["message"])

                        st.write(
                            f"JSON record deleted: {result['json_deleted']}"
                        )

                        st.write(
                            f"Captured image deleted: {result['image_deleted']}"
                        )

                        st.rerun()

                    else:

                        st.error(result["message"])

                except Exception as error:

                    st.error(f"Deletion failed: {error}")

# ============================================================
# PRODUCE MANAGEMENT PAGE
# ============================================================

def produce_management_page():
    """
    Display the produce management interface.
    """

    st.title(
        "Produce Management"
    )

    st.write(
        "This registry controls which produce types "
        "currently have validated prediction models."
    )

    st.divider()

    display_produce_registry_table()

    st.divider()

    st.subheader(
        "Model Availability Rules"
    )

    st.write(
        "A produce can only use shelf-life prediction "
        "when an appropriate produce-specific model "
        "has been trained and validated."
    )

    st.info(
        "The current Tomato model must not be applied "
        "to Mango, Banana, Avocado, Orange, Leafy "
        "Vegetables, or other produce."
    )


# ============================================================
# CAMERA ASSESSMENT PAGE
# ============================================================

def camera_assessment_page():
    """
    Display customer camera assessment interface.

    Current capability:
        Camera image -> Fresh/Rotten visual classification

    Important:
        This feature does not predict shelf life.
        This feature does not certify food safety.
        This feature does not perform four-stage decay
        classification.
    """

    if st.session_state.user_type != "customer":

        st.error(
            "Camera Assessment is currently available "
            "through the customer interface."
        )

        return

    st.title(
        "Customer Camera Assessment"
    )

    st.write(
        "Capture a tomato image using the camera and "
        "perform a Fresh/Rotten visual classification."
    )

    st.divider()
    # --------------------------------------------------------
    # PRODUCE SELECTION
    # --------------------------------------------------------

    produce_registry = get_produce_registry() or []

    produce_names = []
    for item in produce_registry:
        if isinstance(item, dict):
            produce_name = item.get("produce_name")
        elif isinstance(item, (tuple, list)):
            produce_name = item[1] if len(item) > 1 else None
        else:
            try:
                produce_name = item["produce_name"]
            except (KeyError, IndexError, TypeError):
                produce_name = getattr(item, "produce_name", None)

        if produce_name:
            produce_names.append(str(produce_name))

    if not produce_names:

        st.warning(
            "No produce is currently registered."
        )

        return

    selected_produce = st.selectbox(
        "Select Produce",
        produce_names,
    )

    st.write(
        f"Selected Produce: **{selected_produce}**"
    )

    # --------------------------------------------------------
    # CURRENT CAMERA LIMITATION
    # --------------------------------------------------------

    if selected_produce.strip().casefold() != "tomato":

        st.info(
            f"Camera classification is currently available "
            f"only for Tomato."
        )

        st.warning(
            "The current computer-vision classifier was "
            "trained specifically for Tomato Fresh/Rotten "
            "visual classification. It must not be applied "
            "to other produce."
        )

        return

    st.success(
        "Tomato Fresh/Rotten visual classifier available."
    )

    st.divider()

    # --------------------------------------------------------
    # CAMERA CAPTURE
    # --------------------------------------------------------

    st.subheader(
        "Capture Tomato Image"
    )

    st.write(
        "Position the tomato clearly in front of the camera "
        "and capture an image."
    )

    camera_image = st.camera_input(
        "Take a picture of the tomato",
        key="tomato_camera",
    )

    # --------------------------------------------------------
    # CAMERA RESULT
    # --------------------------------------------------------

    if camera_image is not None:

        st.subheader(
            "Captured Image"
        )

        st.image(
            camera_image,
            caption="Captured tomato image",
            use_container_width=True,
        )

        st.divider()

        if st.button(
            "Analyse Tomato Image",
            use_container_width=True,
        ):

            try:

                result = process_camera_image(
                    camera_image
                )

                st.session_state.camera_result = result

                st.success(
                    "Camera image analysed successfully."
                )

            except Exception as error:

                st.error(
                    f"Camera analysis failed: {error}"
                )

    # --------------------------------------------------------
    # DISPLAY SAVED RESULT
    # --------------------------------------------------------

    camera_result = st.session_state.get(
        "camera_result"
    )

    if camera_result is not None:

        st.divider()

        st.subheader(
            "Camera Assessment Result"
        )

        cv_support = generate_cv_decision_support(
            produce_name="Tomato",
            predicted_class=camera_result.get("predicted_class", "Unknown"),
            model_probability=camera_result.get("model_probability"),
        )

        st.subheader("Visual Decision Support")
        st.write(cv_support["decision_support"])
        st.warning(cv_support["research_warning"])
        st.caption(cv_support["integration_note"])

        col1, col2 = st.columns(2)

        with col1:

            predicted_class = camera_result.get(
                "predicted_class",
                "Unknown"
            )

            if predicted_class == "Fresh":

                st.success(
                    f"Visual Classification: {predicted_class}"
                )

            elif predicted_class == "Rotten":

                st.warning(
                    f"Visual Classification: {predicted_class}"
                )

            else:

                st.info(
                    f"Visual Classification: {predicted_class}"
                )

        with col2:

            probability = camera_result.get(
                "model_probability"
            )

            if probability is not None:

                st.metric(
                    "Model Probability",
                    f"{probability * 100:.2f}%"
                )

            else:

                st.info(
                    "Model probability unavailable."
                )

        st.divider()

        st.subheader(
            "Interpretation"
        )

        if predicted_class == "Fresh":

            st.write(
                "The computer-vision classifier identified "
                "the captured tomato image as Fresh based on "
                "the visual patterns learned from the training "
                "dataset."
            )

        elif predicted_class == "Rotten":

            st.write(
                "The computer-vision classifier identified "
                "the captured tomato image as Rotten based on "
                "the visual patterns learned from the training "
                "dataset."
            )

        else:

            st.write(
                "The classifier returned an unrecognised class."
            )

        st.divider()

        st.subheader(
            "Research Limitation"
        )

        st.warning(
            "This camera result is a Fresh/Rotten visual "
            "classification only. It does not predict shelf "
            "life, does not certify food safety, and does not "
            "perform four-stage decay classification."
        )

        st.info(
            "Future AGRO LIFE-AI development may combine "
            "validated computer-vision quality assessment "
            "with appropriate produce-specific shelf-life "
            "models."
        )

    else:

        st.info(
            "Capture a tomato image and select "
            "\"Analyse Tomato Image\" to obtain a "
            "visual classification result."
        )

    st.divider()

    # --------------------------------------------------------
    # SYSTEM STATUS
    # --------------------------------------------------------

    st.subheader(
        "Camera System Status"
    )

    status = get_camera_assessment_status()

    col1, col2 = st.columns(2)

    with col1:

        if status["camera_available"]:

            st.success(
                "Camera Capture: AVAILABLE"
            )

        else:

            st.error(
                "Camera Capture: UNAVAILABLE"
            )

    with col2:

        st.success(
            "Fresh/Rotten Image Classification: AVAILABLE"
        )

    st.divider()

    st.subheader(
        "Current Computer-Vision Workflow"
    )

    st.write(
        "Camera Capture → Image Preprocessing → "
        "Tomato Fresh/Rotten Classification → "
        "Model Probability → Managed Prediction Result"
    )

    st.divider()

    st.subheader(
        "Future AGRO LIFE-AI Workflow"
    )

    st.write(
        "Camera Capture → Produce Identification → "
        "Quality/Decay Assessment → Produce-Specific "
        "Shelf-Life Model → Remaining Shelf-Life Estimation "
        "→ Farmer and Customer Decision Support"
    )

    st.divider()

    st.subheader(
        "Important Research Boundary"
    )

    st.write(
        "The current validated shelf-life model uses "
        "Day-4 Weight Loss and Titratable Acidity rather "
        "than photographs. The camera classifier is a "
        "separate visual-quality research component and "
        "has not yet been validated as a shelf-life predictor."
    )

# ============================================================
# PREDICTION PAGE
# ============================================================

def prediction_page():
    """
    Display the shelf-life prediction interface.
    """

    st.title(
        "Shelf-Life Prediction"
    )

    st.write(
        "Estimate total shelf life and remaining shelf life "
        "using an available produce-specific model."
    )

    st.divider()

    registry = get_produce_registry()

    if not registry:

        st.error(
            "No produce is currently registered."
        )

        return

    produce_names = [
        item["produce_name"]
        for item in registry
    ]

    selected_produce = st.selectbox(
        "Select Produce",
        produce_names,
    )

    selected_status = get_produce_status(
        selected_produce
    )

    st.write(
        f"Category: **{selected_status.get('category', 'N/A')}**"
    )

    if selected_status["prediction_available"]:

        st.success(
            f"{selected_produce}: "
            "Validated prediction model available."
        )

    else:

        st.info(
            f"{selected_produce}: "
            "Prediction model is currently under development."
        )

        st.warning(
            "Prediction cannot be performed for this "
            "produce until an appropriate model has been "
            "trained and validated."
        )

        return

    st.divider()

    input_method = st.selectbox(
        "Input Method",
        [
            "manual",
            "camera",
        ],
    )

    if input_method == "camera":

        st.info(
            "Camera capture is currently available as a "
            "research interface, but the validated model "
            "does not analyse photographs."
        )

        st.warning(
            "For the current validated prediction, "
            "enter the research measurements manually."
        )

    current_storage_days = st.number_input(
        "Current Storage Duration (days)",
        min_value=0.0,
        value=10.0,
        step=1.0,
    )

    st.subheader(
        "Day-4 Research Quality Measurements"
    )

    col1, col2 = st.columns(2)

    with col1:

        weight_loss_day4 = st.number_input(
            "Weight Loss on Day 4 (%)",
            min_value=0.0,
            value=1.43,
            step=0.01,
            format="%.2f",
        )

    with col2:

        ta_day4 = st.number_input(
            "Titratable Acidity on Day 4 (%)",
            min_value=0.0,
            value=0.74,
            step=0.01,
            format="%.2f",
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        predict_button = st.button(
            "Predict Shelf Life",
            use_container_width=True,
        )

    with col2:

        reset_button = st.button(
            "Reset",
            use_container_width=True,
        )

    if reset_button:

        st.session_state.last_prediction = None

        st.rerun()

    if predict_button:

        try:

            result = run_user_prediction_workflow(
                user_id=st.session_state.user_id,
                produce_name=selected_produce,
                input_method=input_method,
                current_storage_days=current_storage_days,
                weight_loss_day4=weight_loss_day4,
                ta_day4=ta_day4,
            )

            st.session_state.last_prediction = result

        except Exception as error:

            st.error(
                f"Prediction failed: {error}"
            )

            return

    result = st.session_state.last_prediction

    if result is None:

        return

    st.divider()

    st.subheader(
        "Prediction Result"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Estimated Total Shelf Life",
            f'{result["total_shelf_life_days"]:.2f} days',
        )

    with col2:

        st.metric(
            "Current Storage Duration",
            f'{result["current_storage_days"]:.2f} days',
        )

    with col3:

        st.metric(
            "Estimated Remaining Shelf Life",
            f'{result["remaining_shelf_life_days"]:.2f} days',
        )

    st.divider()

    st.subheader(
        "Shelf-Life Status"
    )

    st.info(
        result["status"]
    )

    # --------------------------------------------------------
    # FARMER RESULT
    # --------------------------------------------------------

    if st.session_state.user_type == "farmer":

        st.divider()

        st.subheader(
            "Farmer Recommendation"
        )

        recommendation = result.get(
            "recommendation"
        )

        if recommendation:

            st.write(
                recommendation
            )

        planning_advice = result.get(
            "planning_advice"
        )

        if planning_advice:

            st.subheader(
                "Planning Advice"
            )

            st.write(
                planning_advice
            )

    # --------------------------------------------------------
    # CUSTOMER RESULT
    # --------------------------------------------------------

    elif st.session_state.user_type == "customer":

        st.divider()

        st.subheader(
            "Customer Decision Support"
        )

        try:

            customer_result = (
                generate_customer_decision_support(
                    produce_name=selected_produce,
                    current_storage_days=current_storage_days,
                    input_method=input_method,
                    weight_loss_day4=weight_loss_day4,
                    ta_day4=ta_day4,
                )
            )

            st.write(
                customer_result[
                    "customer_decision_support"
                ]
            )

            st.warning(
                customer_result[
                    "food_safety_warning"
                ]
            )

            st.info(
                customer_result[
                    "camera_status"
                ]
            )

        except Exception as error:

            st.error(
                f"Customer decision-support error: {error}"
            )

    st.divider()

    st.subheader(
        "Calculation Details"
    )

    st.write(
        f'Estimated Total Shelf Life: '
        f'{result["total_shelf_life_days"]:.2f} days'
    )

    st.write(
        f'Current Storage Duration: '
        f'{result["current_storage_days"]:.2f} days'
    )

    st.write(
        f'Estimated Remaining Shelf Life: '
        f'{result["remaining_shelf_life_days"]:.2f} days'
    )

    st.divider()

    st.warning(
        "AGRO LIFE-AI provides research-based "
        "shelf-life decision support. It does not certify "
        "food safety, freshness, or suitability for "
        "consumption."
    )
# ============================================================
# HISTORY PAGE
# ============================================================

def history_page():
    """
    Display AGRO LIFE-AI prediction history.

    Includes:
    1. Shelf-life prediction history
    2. Computer-vision assessment history
    3. CV traceability information
    4. CV decision support
    5. CV assessment deletion
    """

    st.title("Prediction & Assessment History")

    st.caption(
        "Review previous shelf-life predictions and computer-vision assessments."
    )

    # ============================================================
    # SHELF-LIFE PREDICTION HISTORY
    # ============================================================

    st.subheader("Shelf-Life Prediction History")

    try:

        history = get_prediction_history(
            user_id=st.session_state.user_id
        )

    except Exception as exc:

        st.error(
            f"Unable to load shelf-life prediction history: {exc}"
        )

        history = []

    if not history:

        st.info(
            "No shelf-life prediction records are available yet."
        )

    else:

        for index, record in enumerate(history, start=1):

            # ----------------------------------------------------
            # SAFELY READ NAMED HISTORY FIELDS
            # ----------------------------------------------------

            produce_name = record.get(
                "produce_name",
                "Unknown Produce",
            )

            total_shelf_life = record.get(
                "total_shelf_life_days"
            )

            remaining_shelf_life = record.get(
                "remaining_shelf_life_days"
            )

            current_storage_days = record.get(
                "current_storage_days"
            )

            status = record.get(
                "status",
                "Not available",
            )

            recorded_at = record.get(
                "recorded_at",
                "Not available",
            )

            input_method = record.get(
                "input_method",
                "Not available",
            )

            prediction_id = record.get(
                "prediction_id",
                "Not available",
            )

            confidence_note = record.get(
                "confidence_note"
            )

            # ----------------------------------------------------
            # DISPLAY RECORD
            # ----------------------------------------------------

            with st.expander(
                f"Record {index} — {produce_name}",
                expanded=(index == 1),
            ):

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.markdown(
                        "**Estimated Total Shelf Life**"
                    )

                    if total_shelf_life is not None:

                        try:

                            st.write(
                                f"{float(total_shelf_life):.2f} days"
                            )

                        except (TypeError, ValueError):

                            st.write(
                                str(total_shelf_life)
                            )

                    else:

                        st.write("Not available")

                with col2:

                    st.markdown(
                        "**Estimated Remaining Shelf Life**"
                    )

                    if remaining_shelf_life is not None:

                        try:

                            st.write(
                                f"{float(remaining_shelf_life):.2f} days"
                            )

                        except (TypeError, ValueError):

                            st.write(
                                str(remaining_shelf_life)
                            )

                    else:

                        st.write("Not available")

                with col3:

                    st.markdown("**Current Storage Duration**")

                    if current_storage_days is not None:

                        try:

                            st.write(
                                f"{float(current_storage_days):.2f} days"
                            )

                        except (TypeError, ValueError):

                            st.write(
                                str(current_storage_days)
                            )

                    else:

                        st.write("Not available")

                st.divider()

                col1, col2 = st.columns(2)

                with col1:

                    st.markdown("**Status**")

                    st.write(status)

                    st.markdown("**Input Method**")

                    st.write(input_method)

                with col2:

                    st.markdown("**Recorded At**")

                    st.write(recorded_at)

                    st.markdown("**Prediction ID**")

                    st.write(prediction_id)

                if confidence_note:

                    st.info(
                        f"Model Note: {confidence_note}"
                    )

    # ============================================================
    # COMPUTER VISION HISTORY
    # ============================================================

    st.divider()

    st.subheader(
        "Computer Vision Assessment History"
    )

    st.caption(
        "These records represent visual Fresh/Rotten "
        "classification from the current tomato computer-vision model."
    )

    try:

        cv_history = get_cv_history()

    except Exception as exc:

        st.error(
            f"Unable to load computer-vision history: {exc}"
        )

        cv_history = []

    if not cv_history:

        st.info(
            "No computer-vision assessment records are available yet."
        )

    else:

        st.write(
            f"Total computer-vision assessments: "
            f"**{len(cv_history)}**"
        )

        for index, record in enumerate(
            cv_history,
            start=1,
        ):

            produce = record.get(
                "produce",
                "Unknown Produce",
            )

            predicted_class = record.get(
                "predicted_class",
                "Not available",
            )

            probability = record.get(
                "model_probability"
            )

            timestamp = record.get(
                "prediction_timestamp",
                "Not available",
            )

            image_filename = record.get(
                "image_filename",
                "Not available",
            )

            image_path = record.get(
                "image_path",
                "Not available",
            )

            record_file = record.get(
                "record_file",
                record.get(
                    "managed_prediction_file",
                    "Not available",
                ),
            )

            decision_support = record.get(
                "decision_support"
            )

            research_warning = record.get(
                "research_warning"
            )

            with st.expander(
                f"Assessment {index} — "
                f"{produce} — "
                f"{predicted_class}",
                expanded=(index == 1),
            ):

                delete_confirm = st.checkbox(
                "Confirm deletion",
                key=f"delete_confirm_{record.get('image_filename')}"
            )

            if st.button(
                "Delete This Assessment",
                 key=f"delete_cv_{record.get('image_filename')}"
            ):
             if not delete_confirm:
              st.warning("Please confirm deletion before continuing.")
        else:
         result = delete_cv_prediction_record(record)

        if result["success"]:
            st.success(result["message"])
            st.rerun()
        else:
            st.error(result["message"])

                # ------------------------------------------------
                # IMAGE
                # ------------------------------------------------

            image_file = Path(image_path)

            if image_file.exists():

                    st.image(
                        str(image_file),
                        caption=image_filename,
                        width=450,
                    )

            else:

                    st.warning(
                        "The captured image file is no longer available."
                    )

                # ------------------------------------------------
                # ASSESSMENT DETAILS
                # ------------------------------------------------

            col1, col2, col3 = st.columns(3)

            with col1:

                    st.markdown("**Produce**")

                    st.write(produce)

            with col2:

                    st.markdown("**Visual Classification**")

                    st.write(predicted_class)

            with col3:

                    st.markdown("**Model Probability**")

                    if probability is not None:

                        try:

                            st.write(
                                f"{float(probability) * 100:.2f}%"
                            )

                        except (TypeError, ValueError):

                            st.write(
                                str(probability)
                            )

                    else:

                        st.write(
                            "Not available"
                        )

            st.divider()

                # ------------------------------------------------
                # DECISION SUPPORT
                # ------------------------------------------------

            st.markdown(
                    "### Visual Decision Support"
                )

            if decision_support:

                    st.info(
                        decision_support
                    )

            else:

                    st.info(
                        "No saved decision-support text "
                        "is available for this older assessment record."
                    )

            if research_warning:

                    st.warning(
                        research_warning
                    )

            else:

                    st.warning(
                        "This computer-vision result is a "
                        "Fresh/Rotten visual classification only. "
                        "It is not a shelf-life prediction and "
                        "does not certify food safety."
                    )

                # ------------------------------------------------
                # TRACEABILITY
                # ------------------------------------------------

            st.markdown(
                    "### Assessment Traceability"
                )

            st.write(
                    f"**Date/Time:** {timestamp}"
                )

            st.write(
                    f"**Image Filename:** {image_filename}"
                )

            st.write(
                    f"**Image Path:** {image_path}"
                )

            st.write(
                    f"**Managed Prediction Record:** "
                    f"{record_file}"
                )

                # ------------------------------------------------
                # RESEARCH FLAGS
                # ------------------------------------------------

            st.markdown(
                    "### Research Boundaries"
                )

            st.write(
                    "Shelf-Life Prediction: "
                    f"{record.get('shelf_life_prediction', False)}"
                )

            st.write(
                    "Four-Stage Decay Prediction: "
                    f"{record.get('four_stage_decay_prediction', False)}"
                )

            st.write(
                    "Food Safety Certification: "
                    f"{record.get('food_safety_certification', False)}"
                )

                # ------------------------------------------------
                # DELETE ASSESSMENT
                # ------------------------------------------------

            st.markdown(
                    "### Delete Assessment"
                )

            confirm_delete = st.checkbox(
                    "I understand that deleting this assessment "
                    "will permanently remove its saved JSON record "
                    "and captured image from the project workspace.",
                    key=f"confirm_delete_cv_{index}",
                )

            if st.button(
                    "Delete This Assessment",
                    key=f"delete_cv_{index}",
                    disabled=not confirm_delete,
                ):

                    delete_result = delete_cv_prediction_record(
                        record
                    )

                    if delete_result["success"]:

                        st.success(
                            delete_result["message"]
                        )

                        st.rerun()

                    else:

                        st.error(
                            delete_result["message"]
                        )
# ============================================================
# HISTORY PAGE
# ============================================================

# ============================================================

def about_page():
    """
    Display information about AGRO LIFE-AI.
    """

    st.title(
        "About AGRO LIFE-AI"
    )

    st.write(
        "AGRO LIFE-AI is a research prototype designed "
        "to investigate the use of data analytics and "
        "machine learning for produce shelf-life prediction "
        "and decision support."
    )

    st.divider()

    st.subheader(
        "Current Research Implementation"
    )

    st.write(
        "The current validated model uses Day-4 Weight Loss "
        "and Titratable Acidity to estimate tomato shelf life."
    )

    st.write(
        "The model was developed from an openly available "
        "tomato shelf-life research dataset."
    )

    st.divider()

    st.subheader(
        "Current System Workflow"
    )

    st.write(
        "Research Data → Data Preparation → "
        "Machine Learning → Shelf-Life Prediction → "
        "Remaining Shelf-Life Calculation → "
        "Decision Support → Historical Records"
    )

    st.divider()

    st.subheader(
        "Future Development"
    )

    st.write(
        "Future versions may incorporate:"
    )

    st.write(
        "• Camera-based produce assessment"
    )

    st.write(
        "• Computer vision"
    )

    st.write(
        "• Additional produce-specific models"
    )

    st.write(
        "• Mobile application"
    )

    st.write(
        "• Larger and more diverse datasets"
    )

    st.write(
        "• Offline data collection and synchronization"
    )

    st.write(
        "• Expanded farmer and customer decision support"
    )

    st.divider()

    st.subheader(
        "Important Limitation"
    )

    st.warning(
        "The current system does not use photographs to "
        "predict shelf life. Camera-based computer vision "
        "is a future development requiring appropriate "
        "datasets, model development, and validation."
    )

    st.divider()

    st.subheader(
        "Multi-Produce Principle"
    )

    st.write(
        "AGRO LIFE-AI can register multiple produce types, "
        "but each produce must have an appropriate validated "
        "model before shelf-life prediction is enabled."
    )


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():

    display_header()

    access_page = display_sidebar()

    # --------------------------------------------------------
    # LOGGED OUT
    # --------------------------------------------------------

    if st.session_state.user_id is None:

        if access_page == "Login":

            login_page()

        elif access_page == "Register":

            registration_page()

        display_footer()

        return

    # --------------------------------------------------------
    # LOGGED IN
    # --------------------------------------------------------

    current_page = st.session_state.page

    if current_page == "Dashboard":

        if st.session_state.user_type == "customer":

            customer_dashboard()

        else:

            farmer_dashboard()

    elif current_page == "Produce Management":

        produce_management_page()

    elif current_page == "Camera Assessment":

        camera_assessment_page()

    elif current_page == "Prediction":

        prediction_page()

    elif current_page == "History":
     history_page()

    elif current_page == "About AGRO LIFE-AI":
    
        about_page()

    else:

        st.warning(
            "Unknown dashboard page."
        )

    display_footer()


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()