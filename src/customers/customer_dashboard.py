import streamlit as st
from PIL import Image

try:
    from src.database.database_manager import (  # pyright: ignore[reportMissingImports]
        add_buyer,
        get_buyer,
        add_customer_camera_assessment,
    )

    from src.vision.camera_assessment import (  # pyright: ignore[reportMissingImports]
        process_camera_image,
    )

except ModuleNotFoundError:
    from database.database_manager import (  # pyright: ignore[reportMissingImports]
        add_buyer,
        get_buyer,
        add_customer_camera_assessment,
    )

    from vision.camera_assessment import (  # pyright: ignore[reportMissingImports]
        process_camera_image,
    )


try:
    from src.auth.auth_manager import has_role, logout_user
except ModuleNotFoundError:
    from auth.auth_manager import has_role, logout_user


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AGRO LIFE-AI - Customer",
    page_icon="",
    layout="wide",
)



# ============================================================
# ============================================================
# CUSTOMER ACCESS CONTROL
# ============================================================

if not (has_role("BUYER") or has_role("CUSTOMER")):
    st.error("Access denied. A customer account is required.")

    if st.button("Return to Login", key="customer_access_denied_return"):
        logout_user()
        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        st.rerun()

    st.stop()


# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------------
       MAIN AREA
       -------------------------------------------------------- */

    .stApp {
        background-color: #f1f8f3;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* --------------------------------------------------------
       LEFT SIDEBAR
       -------------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background-color: #043422;
    }


    /* Sidebar title and tagline */

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #ffffff !important;
    }


    /* Navigation text */

    section[data-testid="stSidebar"]
    [role="radiogroup"] label {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"]
    [role="radiogroup"] label p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }


    /* Selected navigation item */

    section[data-testid="stSidebar"]
    [role="radio"][aria-checked="true"] {
        background-color: #087b38 !important;
        border-radius: 7px;
    }


    /* Selected navigation text */

    section[data-testid="stSidebar"]
    [role="radio"][aria-checked="true"] label,
    section[data-testid="stSidebar"]
    [role="radio"][aria-checked="true"] label p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }


    /* ========================================================
       PAGE TITLES
       ======================================================== */

    h1 {
        color: #075b36 !important;
        font-weight: 700 !important;
    }

    h2,
    h3 {
        color: #075b36 !important;
    }


    /* ========================================================
       DASHBOARD CARDS
       ======================================================== */

    .dashboard-card {
        background: #ffffff;
        border: 1px solid #d5e8da;
        border-radius: 14px;
        padding: 1.4rem;
        min-height: 180px;
        box-shadow: 0 2px 8px rgba(4, 52, 34, 0.05);
    }

    .dashboard-card:hover {
        border-color: #a9d1b5;
        box-shadow: 0 4px 12px rgba(4, 52, 34, 0.08);
    }

    .dashboard-card-title {
        color: #075b36;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 0.65rem;
    }

    .dashboard-card-text {
        color: #42584b;
        font-size: 0.95rem;
        line-height: 1.55;
    }


    /* ========================================================
       PAGE CONTENT BOX
       ======================================================== */

    .content-box {
        background: #ffffff;
        border: 1px solid #d5e8da;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 8px rgba(4, 52, 34, 0.05);
    }


    /* ========================================================
       WELCOME BOX
       ======================================================== */

    .welcome-box {
        background: linear-gradient(
            135deg,
            #e5f4e9,
            #f8fcf9
        );
        border: 1px solid #cfe4d5;
        border-radius: 16px;
        padding: 1.7rem;
        margin-bottom: 1.4rem;
    }

    .welcome-title {
        color: #075b36;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .welcome-text {
        color: #42584b;
        font-size: 1rem;
        line-height: 1.6;
    }


    /* ========================================================
       INFO BOXES
       ======================================================== */

    .info-box {
        background: #e8f5eb;
        border: 1px solid #cfe4d5;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.8rem 0;
    }


    /* --------------------------------------------------------
       BUTTONS
       -------------------------------------------------------- */

    .stButton > button {
        background-color: #087b38;
        color: #ffffff;
        border: none;
        border-radius: 7px;
        padding: 0.55rem 1rem;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #075b36;
        color: #ffffff;
    }


    /* --------------------------------------------------------
       INPUTS
       -------------------------------------------------------- */

    div[data-baseweb="input"] input,
    div[data-baseweb="select"] {
        background-color: #ffffff;
    }


    /* ========================================================
       METRIC CARDS
       ======================================================== */

    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #d5e8da;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 6px rgba(4, 52, 34, 0.04);
    }


    /* ========================================================
       DIVIDERS
       ======================================================== */

    hr {
        border-color: #d5e8da;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.image(
    "assets/agro_life_ai_logo.png",
    use_container_width=True,
)

st.sidebar.title("AGRO LIFE-AI")

st.sidebar.caption(
    "Technology for a Greener Tomorrow"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "Customer Dashboard",
        "Capture Customer",
        "Customer Decision Support",
        "Camera Assessment",
    ],
    label_visibility="collapsed",
    key="customer_navigation",
)

st.sidebar.divider()

if st.sidebar.button(
    "Logout",
    key="customer_logout_button",
    use_container_width=True,
    type="primary",
):
    logout_user()

    st.session_state["authenticated"] = False
    st.session_state["user"] = None

    # Clear customer-specific session data.
    for session_key in list(st.session_state.keys()):
        if session_key.startswith("customer_") or session_key.startswith("camera_"):
            st.session_state.pop(session_key, None)

    st.rerun()


# ============================================================
# CUSTOMER DASHBOARD
# ============================================================

if page == "Customer Dashboard":

    st.title("Customer Dashboard")

    st.caption(
        "Access AGRO LIFE-AI services for produce purchasing "
        "and handling decisions."
    )

    st.divider()

    # --------------------------------------------------------
    # WELCOME
    # --------------------------------------------------------

    with st.container(border=True):

        st.subheader("Welcome to AGRO LIFE-AI")

        st.write(
            "Make better produce purchasing and handling "
            "decisions using research-based shelf-life "
            "prediction and computer-vision assessment."
        )

    st.write("")

    # --------------------------------------------------------
    # CUSTOMER SERVICES
    # --------------------------------------------------------

    st.subheader("Customer Services")

    col1, col2 = st.columns(2)

    with col1:

        with st.container(border=True):

            st.subheader("Capture Customer")

            st.write(
                "Register customer information before "
                "accessing decision-support services."
            )

            st.write("Use the **Capture Customer** page from the sidebar.")

    with col2:

        with st.container(border=True):

            st.subheader("Decision Support")

            st.write(
                "Estimate produce shelf life and receive "
                "customer-friendly decision guidance."
            )

            st.write("Use the **Decision Support** page from the sidebar.")

    col3, col4 = st.columns(2)

    with col3:

        with st.container(border=True):

            st.subheader("Camera Assessment")

            st.write(
                "Use computer vision to classify tomato "
                "images as Fresh or Rotten."
            )

            st.write(
                "Use the **Camera Assessment** page from the sidebar."
            )

    with col4:

        with st.container(border=True):

            st.subheader("Customer Decision Support")

            st.write(
                "AGRO LIFE-AI combines shelf-life prediction "
                "and computer-vision assessment to support "
                "produce purchasing and handling decisions."
            )

    st.write("")

    st.info(
        "Select a service from the sidebar to continue."
    )



# ============================================================
# CAPTURE CUSTOMER
# ============================================================

elif page == "Capture Customer":

    st.title("Capture Customer")

    st.caption(
        "Register customer information before accessing "
        "decision-support services."
    )

    st.divider()

    st.subheader("Customer Information")

    full_name = st.text_input(
        "Customer Full Name *",
        placeholder="Enter customer's full name",
        key="customer_full_name",
    )

    col1, col2 = st.columns(2)

    with col1:
        phone = st.text_input(
            "Phone Number",
            placeholder="Enter phone number",
            key="customer_phone",
        )

    with col2:
        email = st.text_input(
            "Email Address",
            placeholder="Enter email address",
            key="customer_email",
        )

    col3, col4 = st.columns(2)

    with col3:
        buyer_type = st.selectbox(
            "Customer Type",
            [
                "INDIVIDUAL",
                "RETAILER",
                "WHOLESALER",
                "PROCESSOR",
                "OTHER",
            ],
            key="customer_type",
        )

    with col4:
        buyer_location = st.text_input(
            "Location",
            placeholder="Enter customer location",
            key="customer_location",
        )

    st.divider()

    save_col, cancel_col = st.columns(2)

    with save_col:

        save_customer = st.button(
            "Save Customer",
            use_container_width=True,
            key="save_customer_button",
        )

    with cancel_col:

        cancel_customer = st.button(
            "Cancel",
            use_container_width=True,
            key="cancel_customer_button",
        )

    # --------------------------------------------------------
    # CANCEL
    # --------------------------------------------------------

    if cancel_customer:

        st.session_state["customer_full_name"] = ""
        st.session_state["customer_phone"] = ""
        st.session_state["customer_email"] = ""
        st.session_state["customer_location"] = ""

        st.rerun()

    # --------------------------------------------------------
    # SAVE CUSTOMER
    # --------------------------------------------------------

    if save_customer:

        if not full_name.strip():

            st.error(
                "Customer full name is required."
            )

        else:

            try:
                buyer_id = add_buyer(
                    full_name=full_name.strip(),
                    buyer_type=buyer_type,
                    buyer_location=buyer_location.strip() or None,
                    phone=phone.strip() or None,
                    email=email.strip() or None,
                )

                customer = get_buyer(buyer_id)

                if customer:
                    st.session_state["customer_buyer_id"] = customer["buyer_id"]
                    st.session_state["customer_user_id"] = customer["user_id"]

                st.success(
                    f"Customer registered successfully. "
                    f"Customer ID: {buyer_id}"
                )

                if customer:
                    st.subheader("Customer Details")

                    st.write(
                        f"**Customer ID:** {customer['buyer_id']}"
                    )

                    st.write(
                        f"**Full Name:** {customer['full_name']}"
                    )

                    st.write(
                        f"**Customer Type:** {customer['buyer_type']}"
                    )

                    st.write(
                        f"**Phone:** {customer['phone'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Email:** {customer['email'] or 'Not provided'}"
                    )

            except Exception as e:
                st.error(f"Failed to save customer: {e}")


# ============================================================
# CUSTOMER DECISION SUPPORT
# ============================================================

elif page == "Customer Decision Support":

    st.title("Customer Decision Support")

    st.caption(
        "Use shelf-life prediction to support produce "
        "purchasing and handling decisions."
    )

    st.divider()

    # --------------------------------------------------------
    # PRODUCE INFORMATION
    # --------------------------------------------------------

    with st.container(border=True):

        st.subheader("Produce Information")

        produce_name = st.selectbox(
            "Produce",
            [
                "Tomato",
                "Mango",
                "Banana",
                "Avocado",
                "Orange",
                "Leafy Vegetables",
                "Other",
            ],
            key="customer_decision_produce",
        )

        current_storage_days = st.number_input(
            "Current Storage Days",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key="customer_decision_storage_days",
        )

    # --------------------------------------------------------
    # TOMATO RESEARCH INPUTS
    # --------------------------------------------------------

    if produce_name == "Tomato":

        with st.container(border=True):

            st.subheader("Tomato Research Information")

            st.info(
                "Tomato research prediction requires Day-4 "
                "weight loss and titratable acidity."
            )

            weight_loss_day4 = st.number_input(
                "Day-4 Weight Loss (%)",
                min_value=0.0,
                value=0.0,
                step=0.1,
                key="customer_decision_weight_loss",
            )

            ta_day4 = st.number_input(
                "Day-4 Titratable Acidity",
                min_value=0.0,
                value=0.0,
                step=0.01,
                key="customer_decision_ta",
            )

    else:

        weight_loss_day4 = None
        ta_day4 = None

    st.write("")

    # --------------------------------------------------------
    # GENERATE DECISION SUPPORT
    # --------------------------------------------------------

    if st.button(
        "Generate Decision Support",
        use_container_width=True,
        key="customer_generate_decision",
    ):

        try:

            try:
                from src.customers.customer_decision_support import (  # pyright: ignore[reportMissingImports]
                    generate_customer_decision_support,
                )

            except ModuleNotFoundError:

                from customers.customer_decision_support import (  # pyright: ignore[reportMissingImports]
                    generate_customer_decision_support,
                )

            result = generate_customer_decision_support(
                produce_name=produce_name,
                current_storage_days=current_storage_days,
                input_method="manual",
                weight_loss_day4=weight_loss_day4,
                ta_day4=ta_day4,
            )

            st.session_state[
                "customer_decision_result"
            ] = result

            st.success(
                "Customer decision support generated successfully."
            )

        except Exception as error:

            st.error(
                f"Unable to generate decision support: {error}"
            )
# --------------------------------------------------------
# CAMERA ASSESSMENT RESULT
# --------------------------------------------------------

    # --------------------------------------------------------
    # CAMERA ASSESSMENT RESULT
    # --------------------------------------------------------

    if "camera_result" in st.session_state:

        camera_result = st.session_state[
            "camera_result"
        ]

        predicted_class = camera_result.get(
            "predicted_class",
            "Unknown",
        )

        probability = camera_result.get(
            "model_probability"
        )

        st.divider()

        with st.container(border=True):

            st.subheader("Visual Condition Assessment")

            st.write(
                "A previous camera assessment is available "
                "for this customer session."
            )

            camera_col1, camera_col2 = st.columns(2)

            with camera_col1:

                st.metric(
                    "Visual Condition",
                    predicted_class.upper(),
                )

            with camera_col2:

                if probability is not None:

                    st.metric(
                        "Computer Vision Confidence",
                        f"{probability * 100:.2f}%",
                    )

                else:

                    st.metric(
                        "Computer Vision Confidence",
                        "Not available",
                    )

            st.write("")

            if predicted_class.lower() == "fresh":

                st.success(
                    "The computer-vision model classified "
                    "the produce as Fresh."
                )

            elif predicted_class.lower() == "rotten":

                st.error(
                    "The computer-vision model classified "
                    "the produce as Rotten."
                )

            else:

                st.warning(
                    "The computer-vision model returned an "
                    "unrecognized classification."
                )

            st.caption(
                "This visual assessment was automatically "
                "generated from the captured image."
            )

    else:

        with st.container(border=True):

            st.subheader("Visual Condition Assessment")

            st.info(
                "No camera assessment is currently available. "
                "Use Camera Assessment to capture and analyze "
                "the produce image."
            )

    # --------------------------------------------------------
    # DISPLAY RESULT
    # --------------------------------------------------------

    if "customer_decision_result" in st.session_state:

        result = st.session_state[
            "customer_decision_result"
        ]

        st.divider()

        with st.container(border=True):

            st.subheader("Decision Support Result")

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Estimated Shelf Life",
                    f"{result['estimated_total_shelf_life_days']:.2f} days",
                )

            with col2:

                st.metric(
                    "Current Storage",
                    f"{result['current_storage_days']:.2f} days",
                )

            with col3:

                st.metric(
                    "Remaining Shelf Life",
                    f"{result['estimated_remaining_shelf_life_days']:.2f} days",
                )

            st.divider()

            st.subheader("Customer Decision")

            st.write(
                result["customer_decision_support"]
            )

            if result.get("food_safety_warning"):

                st.warning(
                    result["food_safety_warning"]
                )

            st.caption(
                "This system provides research-based decision "
                "support and should not be treated as food-safety "
                "certification."
            )

    # ============================================================
    # CAMERA ASSESSMENT
    # ============================================================

elif page == "Camera Assessment":

    st.title("Camera Assessment")

    st.caption(
        "Use computer vision to classify tomato images "
        "as Fresh or Rotten."
    )

    st.divider()

    with st.container(border=True):

        st.subheader("Tomato Camera Assessment")

        st.write(
            "Capture an image of a tomato and use computer "
            "vision to assess its visual condition."
        )

        st.info(
            "Camera assessment currently supports "
            "tomato Fresh/Rotten classification."
        )

    st.write("")

    # --------------------------------------------------------
    # CAMERA CONTROLS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        capture_camera = st.button(
            "Capture Camera",
            use_container_width=True,
            key="capture_camera_button",
        )

    with col2:

        cancel_camera = st.button(
            "Cancel Camera",
            use_container_width=True,
            key="cancel_camera_button",
        )

    # --------------------------------------------------------
    # START CAMERA
    # --------------------------------------------------------

    if capture_camera:

        st.session_state["camera_active"] = True
        st.session_state.pop("camera_result", None)

        st.rerun()

    # --------------------------------------------------------
    # CANCEL CAMERA
    # --------------------------------------------------------

    if cancel_camera:

        st.session_state["camera_active"] = False
        st.session_state.pop("camera_result", None)

        st.rerun()

    # --------------------------------------------------------
    # CAMERA INPUT
    # --------------------------------------------------------

    if st.session_state.get("camera_active", False):

        with st.container(border=True):

            st.subheader("Capture Tomato Image")

            camera_image = st.camera_input(
                "Take a picture of the tomato",
                key="tomato_camera",
            )

            if camera_image is not None:

                st.image(
                    camera_image,
                    caption="Captured Tomato Image",
                    use_container_width=True,
                )

                if st.button(
                    "Assess Tomato",
                    use_container_width=True,
                    key="assess_tomato_camera",
                ):

                    try:

                        result = process_camera_image(camera_image)

                        customer_user_id = st.session_state.get(
                            "customer_user_id"
                        )

                        if not customer_user_id:
                            st.warning(
                                "Please register the customer before saving "
                                "the camera assessment."
                            )
                        else:
                            assessment_id = add_customer_camera_assessment(
                                user_id=customer_user_id,
                                produce_id=1,  # Tomato
                                predicted_class=result["predicted_class"],
                                model_probability=result.get(
                                    "model_probability"
                                ),
                                image_path=result.get("image_path"),
                            )
                            st.session_state[
                                "camera_assessment_id"
                            ] = assessment_id

                        st.session_state["camera_result"] = result

                        st.success(
                            "Camera assessment completed successfully."
                        )

                    except Exception as error:

                        st.error(
                            f"Unable to assess the camera image: {error}"
                        )

    else:

        with st.container(border=True):

            st.write(
                "Click **Capture Camera** to open the camera."
            )

    # --------------------------------------------------------
# CAMERA RESULT
# --------------------------------------------------------

if "camera_result" in st.session_state:

    result = st.session_state["camera_result"]

    predicted_class = result.get(
        "predicted_class",
        "Unknown",
    )

    probability = result.get(
        "model_probability"
    )

    st.divider()

    with st.container(border=True):

        st.subheader("Automatic Camera Assessment")

        st.write(
            "The computer-vision model automatically "
            "analyzed the captured tomato image."
        )

        st.write("")

        result_col1, result_col2 = st.columns(2)

        with result_col1:

            st.metric(
                "Model Decision",
                predicted_class.upper(),
            )

        with result_col2:

            if probability is not None:

                st.metric(
                    "Model Confidence",
                    f"{probability * 100:.2f}%",
                )

            else:

                st.metric(
                    "Model Confidence",
                    "Not available",
                )

        st.divider()

        # ----------------------------------------------------
        # AUTOMATIC DECISION MESSAGE
        # ----------------------------------------------------

        if predicted_class.lower() == "fresh":

            st.success(
                "FRESH — The computer-vision model "
                "automatically classified this tomato as Fresh."
            )

            st.write(
                "The captured image shows visual characteristics "
                "that the trained model associates with fresh "
                "tomatoes."
            )

        elif predicted_class.lower() == "rotten":

            st.error(
                "ROTTEN — The computer-vision model "
                "automatically classified this tomato as Rotten."
            )

            st.write(
                "The captured image shows visual characteristics "
                "that the trained model associates with rotten "
                "tomatoes."
            )

        else:

            st.warning(
                "The model could not provide a recognized "
                "Fresh or Rotten classification."
            )

        st.divider()

        st.caption(
            "The Fresh/Rotten decision is generated automatically "
            "from the captured image. The customer does not select "
            "the classification manually."
        )

        st.warning(
            "This computer-vision result is research-based "
            "decision support and is not food-safety certification."
        )