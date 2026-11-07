import streamlit as st
from PIL import Image

try:
    from src.database.database_manager import (
        add_buyer,
        get_buyer,
        get_buyer_by_user_id,
        save_customer_profile,
        update_buyer,
        add_customer_camera_assessment,
        get_all_customer_camera_assessments,
        delete_customer_camera_assessment,
        get_available_market_listings,
        get_customer_market_reservations,
        reserve_market_listing_for_customer,
    )

    from src.vision.camera_assessment import process_camera_image

except ModuleNotFoundError:
    from database.database_manager import (
        add_buyer,
        get_buyer,
        get_buyer_by_user_id,
        save_customer_profile,
        update_buyer,
        add_customer_camera_assessment,
        get_all_customer_camera_assessments,
        delete_customer_camera_assessment,
        get_available_market_listings,
        get_customer_market_reservations,
        reserve_market_listing_for_customer,
    )

    from vision.camera_assessment import process_camera_image


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

# ============================================================
# AUTOMATIC CUSTOMER PROFILE INITIALISATION
# ============================================================

authenticated_user = st.session_state.get("user")

if isinstance(authenticated_user, dict):

    authenticated_user_id = authenticated_user.get("user_id")

    if authenticated_user_id is not None:

        customer_profile = get_buyer_by_user_id(
            authenticated_user_id
        )

        if customer_profile:

            st.session_state["customer_buyer_id"] = (
                customer_profile["buyer_id"]
            )

            st.session_state["customer_user_id"] = (
                customer_profile["user_id"]
            )

        else:

            st.session_state.pop(
                "customer_buyer_id",
                None
            )

            st.session_state.pop(
                "customer_user_id",
                None
            )

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
        "Camera Assessment History",
        "Marketplace",
        "My Reservations",
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

    def clear_customer_form():
        st.session_state["customer_full_name"] = ""
        st.session_state["customer_phone"] = ""
        st.session_state["customer_email"] = ""
        st.session_state["customer_location"] = ""

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

        st.button(
            "Cancel",
            use_container_width=True,
            key="cancel_customer_button",
            on_click=clear_customer_form,
        )

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

elif page == "Camera Assessment History":

    st.title("Camera Assessment History")
    st.caption("View and manage your previous camera assessments.")

    customer_user_id = st.session_state.get("customer_user_id")

    if not customer_user_id:
        st.warning("Customer account information is unavailable.")
    else:
        try:
            records = get_all_customer_camera_assessments(
                user_id=int(customer_user_id)
            )

            if not records:
                st.info("You have not completed any camera assessments yet.")
            else:
                st.success(
                    f"You have completed {len(records)} camera assessment(s)."
                )

                for record in records:

                    assessment_id = int(record["assessment_id"])

                    with st.container(border=True):

                        col1, col2 = st.columns([1, 2])

                        with col1:
                            image_path = record.get("image_path")

                            if image_path:
                                try:
                                    st.image(
                                        image_path,
                                        caption="Captured Produce",
                                        use_container_width=True,
                                    )
                                except Exception:
                                    st.warning("Captured image is unavailable.")
                            else:
                                st.warning("No captured image is available.")

                        with col2:
                            st.subheader(
                                record.get("produce_name", "Unknown Produce")
                            )

                            st.write(
                                f"**Assessment Reference:** {assessment_id}"
                            )

                            predicted_class = record.get(
                                "predicted_class", "Unknown"
                            )

                            if predicted_class.lower() == "fresh":
                                st.success("Prediction: FRESH")
                            elif predicted_class.lower() == "rotten":
                                st.error("Prediction: ROTTEN")
                            else:
                                st.warning(
                                    f"Prediction: {predicted_class}"
                                )

                            probability = record.get("model_probability")

                            confidence_level = "Unavailable"

                            if probability is not None:

                                probability_value = float(probability)

                                st.metric(
                                    "Model Confidence",
                                    f"{probability_value * 100:.2f}%",
                                )

                                if probability_value < 0.60:
                                    confidence_level = "Low"

                                elif probability_value < 0.80:
                                    confidence_level = "Moderate"

                                else:
                                    confidence_level = "High"

                            st.write("")

                            st.metric(
                                "Confidence Level",
                                confidence_level,
                            )

                            # HISTORICAL CUSTOMER RECOMMENDATION

                            st.subheader(
                                "AGRO LIFE-AI Recommendation"
                            )

                            if confidence_level == "Low":

                                st.warning(
                                    "The model has low confidence in "
                                    "this historical classification. "
                                    "Do not rely on this result alone. "
                                    "Manual inspection and further "
                                    "assessment are recommended."
                                )

                            elif confidence_level == "Moderate":

                                if predicted_class.lower() == "fresh":

                                    st.info(
                                        "The produce was classified as "
                                        "Fresh with moderate confidence. "
                                        "Inspect it carefully, handle it "
                                        "properly and store it under "
                                        "suitable conditions."
                                    )

                                elif predicted_class.lower() == "rotten":

                                    st.warning(
                                        "The produce was classified as "
                                        "Rotten with moderate confidence. "
                                        "Separate it from fresh produce "
                                        "and arrange further inspection."
                                    )

                            elif confidence_level == "High":

                                if predicted_class.lower() == "fresh":

                                    st.success(
                                        "The produce was classified as "
                                        "Fresh with high model confidence. "
                                        "Handle it carefully, store it "
                                        "under suitable conditions and "
                                        "inspect it regularly."
                                    )

                                elif predicted_class.lower() == "rotten":

                                    st.warning(
                                        "The produce was classified as "
                                        "Rotten with high model confidence. "
                                        "Separate it from fresh produce "
                                        "and seek further inspection."
                                    )

                            else:

                                st.info(
                                    "Model confidence is unavailable. "
                                    "Inspect the produce manually before "
                                    "making quality decisions."
                                )

                            st.caption(
                                f"Assessment Date: "
                                f"{record.get('created_at', 'Unavailable')}"
                            )

                            pending_key = (
                                f"delete_camera_pending_{assessment_id}"
                            )

                            if st.button(
                                "Delete Assessment",
                                key=f"delete_camera_{assessment_id}",
                            ):
                                st.session_state[pending_key] = True
                                st.rerun()

                            if st.session_state.get(pending_key):

                                st.warning(
                                    "Are you sure you want to delete "
                                    "this camera assessment?"
                                )

                                confirm_col, cancel_col = st.columns(2)

                                with confirm_col:
                                    if st.button(
                                        "Confirm Delete",
                                        key=f"confirm_delete_{assessment_id}",
                                        type="primary",
                                    ):
                                        deleted = (
                                            delete_customer_camera_assessment(
                                                assessment_id=assessment_id,
                                                user_id=int(customer_user_id),
                                            )
                                        )

                                        st.session_state.pop(
                                            pending_key, None
                                        )

                                        if deleted:
                                            st.success(
                                                "Camera assessment deleted."
                                            )
                                        else:
                                            st.warning(
                                                "Assessment was not found "
                                                "or does not belong to you."
                                            )

                                        st.rerun()

                                with cancel_col:
                                    if st.button(
                                        "Cancel",
                                        key=f"cancel_delete_{assessment_id}",
                                    ):
                                        st.session_state.pop(
                                            pending_key, None
                                        )
                                        st.rerun()

        except Exception as error:
            st.error(
                f"Unable to retrieve camera history: {error}"
            )

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

    confidence_level = result.get(
        "confidence_level",
        "Unavailable",
    )

    st.divider()

    with st.container(border=True):

        st.subheader("Automatic Camera Assessment")

        st.write(
            "The computer-vision model automatically "
            "analyzed the captured tomato image."
        )

        st.write("")

        result_col1, result_col2, result_col3 = st.columns(3)

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

        with result_col3:

            st.metric(
                "Confidence Level",
                confidence_level,
            )

        st.divider()

        # ----------------------------------------------------
        # ----------------------------------------------------
        # CONFIDENCE-AWARE AUTOMATIC DECISION MESSAGE
        # ----------------------------------------------------

        confidence_level = result.get(
            "confidence_level",
            "Unavailable",
        )

        normalized_class = predicted_class.strip().lower()
        normalized_confidence = str(
            confidence_level
        ).strip().lower()

        if normalized_confidence == "low":

            st.warning(
                f"PROVISIONAL {predicted_class.upper()} "
                "CLASSIFICATION - The model has low confidence "
                "in this result. Do not rely on the classification "
                "alone. Manual inspection and further assessment "
                "are recommended."
            )

        elif normalized_confidence == "moderate":

            st.info(
                f"{predicted_class.upper()} CLASSIFICATION "
                "WITH MODERATE CONFIDENCE - Inspect the tomato "
                "carefully and use additional checks before "
                "making quality decisions."
            )

        elif normalized_confidence == "high":

            if normalized_class == "fresh":

                st.success(
                    "FRESH - The model classified this tomato "
                    "as Fresh with high model confidence. "
                    "Continue appropriate handling and regular "
                    "inspection."
                )

            elif normalized_class == "rotten":

                st.error(
                    "ROTTEN - The model classified this tomato "
                    "as Rotten with high model confidence. "
                    "Separate it from fresh produce and arrange "
                    "further inspection."
                )

            else:

                st.warning(
                    "The model returned an unrecognized "
                    "classification. Manual inspection is required."
                )

        else:

            st.warning(
                f"{predicted_class.upper()} CLASSIFICATION - "
                "The model confidence level is unavailable. "
                "Inspect the tomato manually before making "
                "quality decisions."
            )

        st.write("")

        # AGRO LIFE-AI CUSTOMER RECOMMENDATIONS
        # ----------------------------------------------------

        st.subheader("AGRO LIFE-AI Recommendations")

        recommendation = result.get(
            "customer_recommendation"
        )

        if recommendation:

            if predicted_class.lower() == "fresh":

                st.success(recommendation)

            elif predicted_class.lower() == "rotten":

                st.warning(recommendation)

            else:

                st.info(recommendation)

        else:

            st.info(
                "No camera recommendation is available "
                "for this assessment."
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



# ============================================================
# CUSTOMER MARKETPLACE
# ============================================================

elif page == "Marketplace":

    st.title("Produce Marketplace")
    st.caption(
        "Browse fresh produce offered by registered farmers."
    )

    customer_user_id = st.session_state.get("customer_user_id")
    customer_buyer_id = st.session_state.get("customer_buyer_id")

    if not customer_user_id or not customer_buyer_id:

        st.warning(
            "Please complete your customer profile before "
            "reserving produce."
        )

    else:

        listings = get_available_market_listings()

        if not listings:

            st.info(
                "There are currently no available produce listings."
            )

        else:

            st.success(
                f"{len(listings)} available produce listing(s)."
            )

            for listing in listings:

                listing_id = int(listing["listing_id"])
                quantity = float(
                    listing["quantity_available_kg"] or 0
                )
                price = float(listing["price_per_kg"] or 0)
                total_value = quantity * price

                with st.container(border=True):

                    st.subheader(
                        listing.get("produce_name", "Unknown Produce")
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Available Quantity",
                            f"{quantity:,.2f} kg",
                        )

                    with col2:
                        st.metric(
                            "Price per kg",
                            f"K{price:,.2f}",
                        )

                    with col3:
                        st.metric(
                            "Listing Value",
                            f"K{total_value:,.2f}",
                        )

                    st.write(
                        f"**Farmer/Seller:** "
                        f"{listing.get('seller_name', 'Not available')}"
                    )

                    st.write(
                        f"**Quality:** "
                        f"{listing.get('quality_status', 'Not specified')}"
                    )

                    st.write(
                        f"**Listing Reference:** {listing_id}"
                    )

                    st.warning(
                        "Reserving this listing reserves the entire "
                        f"quantity of {quantity:,.2f} kg."
                    )

                    if st.button(
                        "Reserve Produce",
                        key=f"customer_reserve_{listing_id}",
                        type="primary",
                        use_container_width=True,
                    ):

                        try:

                            reserved = reserve_market_listing_for_customer(
                                listing_id=listing_id,
                                buyer_id=int(customer_buyer_id),
                                user_id=int(customer_user_id),
                            )

                            if reserved:

                                st.success(
                                    "Produce successfully reserved!"
                                )

                                st.rerun()

                            else:

                                st.warning(
                                    "This listing is no longer available. "
                                    "Please refresh the marketplace."
                                )

                        except ValueError as error:

                            st.error(str(error))

                        except Exception as error:

                            st.error(
                                f"Reservation failed: {error}"
                            )


# ============================================================
# CUSTOMER RESERVATIONS
# ============================================================

elif page == "My Reservations":

    st.title("My Reservations")

    st.caption(
        "View produce listings reserved under your customer account."
    )

    customer_user_id = st.session_state.get("customer_user_id")

    if not customer_user_id:

        st.warning(
            "Please complete your customer profile first."
        )

    else:

        reservations = get_customer_market_reservations(
            int(customer_user_id)
        )

        if not reservations:

            st.info(
                "You have no produce reservations yet. "
                "Visit the Marketplace to browse available produce."
            )

        else:

            st.success(
                f"You have {len(reservations)} reservation(s)."
            )

            for reservation in reservations:

                quantity = float(
                    reservation["quantity_available_kg"] or 0
                )

                price = float(
                    reservation["price_per_kg"] or 0
                )

                total_value = quantity * price

                with st.container(border=True):

                    st.subheader(
                        reservation.get(
                            "produce_name",
                            "Unknown Produce",
                        )
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Reserved Quantity",
                            f"{quantity:,.2f} kg",
                        )

                    with col2:
                        st.metric(
                            "Price per kg",
                            f"K{price:,.2f}",
                        )

                    with col3:
                        st.metric(
                            "Listing Value",
                            f"K{total_value:,.2f}",
                        )

                    st.write(
                        f"**Seller:** "
                        f"{reservation.get('seller_name', 'Not available')}"
                    )

                    st.write(
                        f"**Quality:** "
                        f"{reservation.get('quality_status', 'Not specified')}"
                    )

                    st.write(
                        f"**Reservation Reference:** "
                        f"{reservation.get('listing_id')}"
                    )

                    st.success("Reservation Status: RESERVED")

                    st.caption(
                        "This is a produce reservation, not a "
                        "completed payment or delivery confirmation."
                    )
