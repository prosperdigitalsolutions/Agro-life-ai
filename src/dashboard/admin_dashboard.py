import os
import sys
from pathlib import Path

import streamlit as st

# ============================================================
# PROJECT PATH
# ============================================================

def _find_project_root(start_path: Path) -> Path:
    for candidate in (start_path, *start_path.parents):
        if (candidate / "src").exists():
            return candidate

    return start_path


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
SRC_PATH = PROJECT_ROOT / "src"

for path in (PROJECT_ROOT, SRC_PATH):
    path_str = str(path)

    if path_str not in sys.path:
        sys.path.insert(0, path_str)

# ============================================================
# AUTH & DATABASE IMPORTS
# ============================================================
from src.auth.auth_manager import (
    has_role,
    logout_user,
    get_user_by_username,
    create_user_credentials,
    admin_reset_farmer_password,
)
from src.database.database_manager import (
    get_all_farmers,
    get_all_buyers,
    get_all_produce,
    get_all_predictions,
    get_all_prediction_history,
    get_all_recommendations,
    get_marketplace_statistics,
    get_farmer_batches,
    get_farmer,
    delete_farmer,
    add_farmer,
    get_all_customer_camera_assessments,
    get_all_market_listings,
    delete_buyer,
    delete_prediction,
    delete_customer_camera_assessment,
    update_market_listing_status,
)

# ============================================================
# ADMIN ACCESS CONTROL
# ============================================================

if not has_role("ADMIN"):
    st.error("Access denied. Administrator privileges are required.")

    if st.button("Return to Login"):
      st.stop()

    st.stop()
# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AGRO LIFE-AI | Admin Dashboard",
    page_icon="ðŸŒ±",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# GLOBAL THEME
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       MAIN APPLICATION
       ======================================================== */

    .stApp {
        background: #f5faf7;
    }

    .block-container {
        padding-top: 0.8rem;
        padding-bottom: 2rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        max-width: 100%;
    }


    /* ========================================================
       HEADINGS
       ======================================================== */

    h1,
    h2,
    h3 {
        color: #075b36 !important;
    }

    h1 {
        font-size: 30px !important;
        font-weight: 800 !important;
    }

    h2 {
        font-size: 23px !important;
        font-weight: 750 !important;
    }

    h3 {
        font-size: 19px !important;
        font-weight: 700 !important;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {
        background: #043422;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 1.2rem 0.8rem;
    }

    [data-testid="stSidebar"] .stRadio > label {
        display: none;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 5px;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background: transparent;
        border-radius: 12px;
        padding: 11px 13px;
        margin: 0;
        width: 100%;
        box-sizing: border-box;
        cursor: pointer;
        transition: background 0.2s;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background: #075a32;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"]
    label[data-checked="true"] {
        background: #087b38;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"]
    label p {
        color: white !important;
        font-size: 14px;
        font-weight: 500;
        margin: 0;
    }


    /* ========================================================
       SIDEBAR SELECTBOX
       ======================================================== */

    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background: #075a32;
        border: 1px solid #28784f;
        border-radius: 9px;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: white !important;
    }

    [data-testid="stSidebar"] label {
        color: #d7f5df !important;
    }


    /* ========================================================
       METRIC CARDS
       ======================================================== */

    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #dce9df;
        border-radius: 14px;
        padding: 16px;
        box-shadow: none;
    }

    [data-testid="stMetricLabel"] {
        color: #23704c !important;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: #075b36 !important;
        font-weight: 800;
    }


    /* ========================================================
       CARDS
       ======================================================== */

    .admin-card {
        background: white;
        border: 1px solid #dce9df;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
    }

    .admin-card-title {
        color: #075b36;
        font-size: 17px;
        font-weight: 750;
        margin-bottom: 5px;
    }

    .admin-card-text {
        color: #53675b;
        font-size: 13px;
        line-height: 1.5;
    }


    /* ========================================================
       WELCOME CARD
       ======================================================== */

    .admin-welcome {
        background: linear-gradient(
            135deg,
            #e8f6eb,
            #f7fcf8
        );

        border: 1px solid #dce9df;
        border-radius: 16px;
        padding: 22px 24px;
        margin-bottom: 20px;
    }

    .admin-welcome-title {
        color: #075b36;
        font-size: 25px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .admin-welcome-text {
        color: #4d6657;
        font-size: 14px;
        line-height: 1.5;
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        border-radius: 9px;
        border: 1px solid #087b38;
        background: #087b38;
        color: white;
        font-weight: 600;
    }

    .stButton > button:hover {
        background: #075a32;
        border-color: #075a32;
        color: white;
    }


    /* ========================================================
       DIVIDERS
       ======================================================== */

    hr {
        border-color: #dce9df !important;
    }


    /* ========================================================
       DATAFRAMES
       ======================================================== */

    [data-testid="stDataFrame"] {
        border: 1px solid #dce9df;
        border-radius: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOGO
# ============================================================

logo_path = os.path.join(
    str(PROJECT_ROOT),
    "assets",
    "agro_life_ai_logo.png",
)


# ============================================================
# SYSTEM DATA
# ============================================================
# Data loading will be placed inside the relevant page sections
# so unrelated database queries do not run on every page rerun.


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # LOGO
    # --------------------------------------------------------

    if os.path.exists(logo_path):

        st.markdown(
            '<div class="sidebar-logo">',
            unsafe_allow_html=True,
        )

        st.image(
            logo_path,
            use_container_width=True,
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    st.markdown(
        """
        <div style="
            text-align:center;
            margin-top:-8px;
            margin-bottom:4px;
            color:white;
            font-size:22px;
            font-weight:800;
            letter-spacing:0.5px;
        ">
            AGRO LIFE-AI
        </div>

        <div style="
            text-align:center;
            color:#d7f5df;
            font-size:11px;
            line-height:1.4;
            margin-bottom:18px;
        ">
            Biochemical Decay &amp;<br>
            Shelf-Life Predictor
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.divider()


    # --------------------------------------------------------
    # ADMIN MANAGEMENT LABEL
    # --------------------------------------------------------

    st.markdown(
        """
        <div style="
            color:#d7f5df;
            font-size:11px;
            font-weight:800;
            letter-spacing:.5px;
            margin-bottom:6px;
        ">
            ADMIN MANAGEMENT
        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Farmers",
            "Buyers",
            "Produce",
            "Predictions",
            "Marketplace",
            "Customer Assessments",
        ],
        label_visibility="collapsed",
        key="admin_navigation",
    )

    st.divider()


    # --------------------------------------------------------
    # SIDEBAR FOOTER
    # --------------------------------------------------------

    st.markdown(
        """
        <div style="
            color:#d7f5df;
            font-size:13px;
            line-height:1.5;
            margin-top:15px;
        ">
            <b>Technology</b><br>
            for a Greener<br>
            Tomorrow
        </div>

        <div style="
            color:#a9cdb7;
            font-size:10px;
            line-height:1.5;
            margin-top:18px;
        ">
            AGRO LIFE-AI<br>
            Administrator Module
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    # --------------------------------------------------------
    # LOGOUT BUTTON
    # --------------------------------------------------------

    if st.button("Logout", use_container_width=True):

        logout_user()

        st.session_state["authenticated"] = False
        st.session_state["user"] = None

        st.rerun()

# ============================================================

# MAIN DASHBOARD HEADER

# ============================================================

st.title("Dashboard Overview")

st.caption(
"Monitor agricultural operations, produce quality, "
"AI predictions, and marketplace activity."
)

st.divider()



# ============================================================
# PAGE 1 â€” DASHBOARD
# ============================================================

if page == "Dashboard":
    farmers = get_all_farmers()
    buyers = get_all_buyers()
    produce = get_all_produce()
    predictions = get_all_predictions()
    history = get_all_prediction_history()
    recommendations = get_all_recommendations()
    marketplace = get_marketplace_statistics()


    # --------------------------------------------------------
    # WELCOME
    # --------------------------------------------------------

    st.caption("Monitor agricultural operations, produce quality, AI predictions, and marketplace activity.")

    # --------------------------------------------------------
    # SYSTEM OVERVIEW
    # --------------------------------------------------------

    st.subheader("System Overview")

    row1 = st.columns(3)

    with row1[0]:
        st.metric(
            "Farmers",
            len(farmers),
        )

    with row1[1]:
        st.metric(
            "Buyers",
            len(buyers),
        )

    with row1[2]:
        st.metric(
            "Produce Types",
            len(produce),
        )

    row2 = st.columns(3)

    with row2[0]:
        st.metric(
            "AI Predictions",
            len(predictions),
        )

    with row2[1]:
        st.metric(
            "Prediction History",
            len(history),
        )

    with row2[2]:
        st.metric(
            "Recommendations",
            len(recommendations),
        )

    st.divider()

    # --------------------------------------------------------
    # MARKETPLACE OVERVIEW
    # --------------------------------------------------------

    st.subheader("Marketplace Overview")

    market_row = st.columns(4)

    with market_row[0]:
        st.metric(
            "Total Listings",
            marketplace["total_listings"],
        )

    with market_row[1]:
        st.metric(
            "Available",
            marketplace["available"],
        )

    with market_row[2]:
        st.metric(
            "Reserved",
            marketplace["reserved"],
        )

    with market_row[3]:
        st.metric(
            "Available Quantity",
            f"{marketplace['available_quantity_kg']:.2f} KG",
        )

    st.divider()

    # ============================================================
    # ADMINISTRATION OVERVIEW
    # ============================================================

    st.subheader("Administration Overview")

    admin_col1, admin_col2, admin_col3 = st.columns(3)

    with admin_col1:

        with st.container(border=True):

            st.subheader("Farmer Management")

            st.write(
                "Registered farmers and their agricultural "
                "activities can be monitored from the "
                "Farmers section."
            )

    with admin_col2:

        with st.container(border=True):

            st.subheader("AI Prediction Monitoring")

            st.write(
                "Review shelf-life predictions, prediction "
                "history and recommendations generated by "
                "AGRO LIFE-AI."
            )

    with admin_col3:

        with st.container(border=True):

            st.subheader("Marketplace Monitoring")

            st.write(
                "Monitor produce listings, available quantities, "
                "reservations and buyer activity."
            )


# ============================================================
# PAGE 2 â€” FARMERS
# ============================================================

elif page == "Farmers":
    farmers = get_all_farmers()
    produce = get_all_produce()


    # --------------------------------------------------------
    # PAGE HEADER
    # --------------------------------------------------------

    st.title("Farmers")

    st.caption(
        "Manage registered farmers and monitor their "
        "agricultural activities."
    )

    st.divider()

    # --------------------------------------------------------
    # FARMER SUMMARY
    # --------------------------------------------------------

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:

        st.metric(
            "Registered Farmers",
            len(farmers),
        )

    with summary_col2:

        total_batches = 0

        for farmer in farmers:

            try:

                farmer_batches = get_farmer_batches(
                    farmer["farmer_id"]
                )

                total_batches += len(farmer_batches)

            except Exception:

                pass

        st.metric(
            "Registered Batches",
            total_batches,
        )

    with summary_col3:

        st.metric(
            "Produce Types",
            len(produce),
        )

    st.divider()
        # --------------------------------------------------------
    # CREATE FARMER ACCOUNT
    # --------------------------------------------------------

    st.subheader("Create Farmer Account")

    st.caption(
        "Register a new farmer profile and create login credentials "
        "for Farm Management."
    )

    with st.expander(
        "Add New Farmer",
        expanded=False,
    ):

        with st.form(
            "create_farmer_account_form",
            clear_on_submit=False,
        ):

            st.markdown("### Farmer Information")

            farmer_col1, farmer_col2 = st.columns(2)

            with farmer_col1:

                full_name = st.text_input(
                    "Full Name *",
                    placeholder="Enter farmer's full name",
                )

                phone = st.text_input(
                    "Phone Number",
                    placeholder="e.g. 0970000000",
                )

                email = st.text_input(
                    "Email Address",
                    placeholder="farmer@example.com",
                )

            with farmer_col2:

                farm_name = st.text_input(
                    "Farm Name *",
                    placeholder="Enter farm name",
                )

                farm_location = st.text_input(
                    "Farm Location",
                    placeholder="e.g. Chibombo",
                )

                district = st.text_input(
                    "District",
                    placeholder="e.g. Chibombo",
                )

            province = st.text_input(
                "Province",
                placeholder="e.g. Central",
            )

            st.divider()

            st.markdown("### Login Credentials")

            credential_col1, credential_col2 = st.columns(2)

            with credential_col1:

                username = st.text_input(
                    "Username *",
                    placeholder="Create a username",
                )

            with credential_col2:

                password = st.text_input(
                    "Password *",
                    type="password",
                    placeholder="Create a password",
                )

            confirm_password = st.text_input(
                "Confirm Password *",
                type="password",
                placeholder="Re-enter password",
            )

            st.caption(
                "The farmer will use these credentials to access "
                "the Farm Management Dashboard."
            )

            create_farmer = st.form_submit_button(
                "Create Farmer Account",
                type="primary",
                use_container_width=True,
            )

            if create_farmer:

                # ------------------------------------------------
                # VALIDATION
                # ------------------------------------------------

                full_name = full_name.strip()
                phone = phone.strip()
                email = email.strip()
                farm_name = farm_name.strip()
                farm_location = farm_location.strip()
                district = district.strip()
                province = province.strip()
                username = username.strip()

                if not full_name:

                    st.error(
                        "Please enter the farmer's full name."
                    )

                elif not farm_name:

                    st.error(
                        "Please enter the farm name."
                    )

                elif not username:

                    st.error(
                        "Please enter a username."
                    )

                elif not password:

                    st.error(
                        "Please enter a password."
                    )

                elif password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                elif len(password) < 6:

                    st.error(
                        "Password must contain at least 6 characters."
                    )

                elif get_user_by_username(username):

                    st.error(
                        f"The username '{username}' is already "
                        "in use. Please choose another username."
                    )

                else:

                    # ------------------------------------------------
                    # CREATE FARMER PROFILE
                    # ------------------------------------------------

                    try:

                        new_farmer_id = add_farmer(
                            full_name=full_name,
                            phone=phone or None,
                            email=email or None,
                            farm_name=farm_name,
                            farm_location=farm_location or None,
                            district=district or None,
                            province=province or None,
                        )

                        # ------------------------------------------------
                        # FIND THE NEW USER RECORD
                        # ------------------------------------------------

                        new_farmer = get_farmer(
                            new_farmer_id
                        )

                        if not new_farmer:

                            st.error(
                                "Farmer profile was created, but "
                                "the linked user record could not "
                                "be found."
                            )

                        else:

                            new_user_id = new_farmer["user_id"]

                            # ------------------------------------------------
                            # CREATE LOGIN CREDENTIALS
                            # ------------------------------------------------

                            credential_result = (
                                create_user_credentials(
                                    new_user_id,
                                    username,
                                    password,
                                )
                            )

                            if (
                                isinstance(
                                    credential_result,
                                    tuple,
                                )
                                and not credential_result[0]
                            ):

                                st.error(
                                    credential_result[1]
                                )

                            else:

                                st.success(
                                    f"Farmer account for "
                                    f"{full_name} created successfully."
                                )

                                st.info(
                                    f"Farmer ID: {new_farmer_id} | "
                                    f"Username: {username} | "
                                    f"Role: FARMER"
                                )

                                st.rerun()

                    except Exception as e:

                        st.error(
                            f"Failed to create farmer account: {e}"
                        )

    st.divider()




    # --------------------------------------------------------
    # REGISTERED FARMERS
    # --------------------------------------------------------

    st.subheader("Registered Farmers")
    # --------------------------------------------------------
    # FARMER DETAILS
    # --------------------------------------------------------

    st.subheader("Farmer Details")

    if not farmers:

        st.info(
            "There are no farmers available to display."
        )

    else:

        farmer_options = {
            (
                f"Farmer #{farmer['farmer_id']} - "
                f"{farmer['full_name']}"
            ):
            farmer["farmer_id"]

            for farmer in farmers
        }

        selected_farmer_label = st.selectbox(
            "Select Farmer",
            list(farmer_options.keys()),
            key="admin_farmer_selector",
        )

        selected_farmer_id = farmer_options[
            selected_farmer_label
        ]

        selected_farmer = get_farmer(
            selected_farmer_id
        )

        # ----------------------------------------------------
        # SELECTED FARMER DETAILS
        # ----------------------------------------------------

        if selected_farmer:

            detail_col1, detail_col2 = st.columns(2)

            with detail_col1:

                with st.container(border=True):

                    st.subheader("Personal Information")

                    st.write(
                        f"**Full Name:** "
                        f"{selected_farmer['full_name']}"
                    )

                    st.write(
                        f"**Phone:** "
                        f"{selected_farmer['phone']}"
                    )

                    st.write(
                        f"**Email:** "
                        f"{selected_farmer['email']}"
                    )

            with detail_col2:

                with st.container(border=True):

                    st.subheader("Farm Information")

                    st.write(
                        f"**Farm:** "
                        f"{selected_farmer['farm_name']}"
                    )

                    st.write(
                        f"**Location:** "
                        f"{selected_farmer['farm_location']}"
                    )

                    st.write(
                        f"**District:** "
                        f"{selected_farmer['district']}"
                    )

                    st.write(
                        f"**Province:** "
                        f"{selected_farmer['province']}"
                    )

                    st.write(
                        f"**Registered:** "
                        f"{selected_farmer['created_at']}"
                    )

            st.divider()

            # ------------------------------------------------
            # ------------------------------------------------
            # FARMER LOGIN PASSWORD RESET
            # ------------------------------------------------

            with st.container(border=True):

                st.subheader("Reset Farmer Login Password")

                st.caption(
                    "Set a new password for this farmer's existing login account."
                )

                farmer_user_id = selected_farmer["user_id"]

                with st.form(
                    key=f"admin_reset_password_form_{selected_farmer_id}"
                ):

                    new_farmer_password = st.text_input(
                        "New Password",
                        type="password",
                        key=f"new_farmer_password_{selected_farmer_id}",
                    )

                    confirm_farmer_password = st.text_input(
                        "Confirm New Password",
                        type="password",
                        key=f"confirm_farmer_password_{selected_farmer_id}",
                    )

                    reset_submitted = st.form_submit_button(
                        "Reset Farmer Password",
                        type="primary",
                    )

                if reset_submitted:

                    if not new_farmer_password or not confirm_farmer_password:
                        st.error("Please complete both password fields.")

                    elif new_farmer_password != confirm_farmer_password:
                        st.error("The passwords do not match.")

                    elif len(new_farmer_password) < 8:
                        st.error("Password must contain at least 8 characters.")

                    else:
                        reset_success, reset_message = (
                            admin_reset_farmer_password(
                                farmer_user_id,
                                new_farmer_password,
                            )
                        )

                        if reset_success:
                            st.success(reset_message)
                        else:
                            st.error(reset_message)


            # DELETE FARMER ? DANGER ZONE
            # ------------------------------------------------

            with st.container(border=True):

                st.subheader("Danger Zone")

                st.warning(
                    f"Permanently deleting "
                    f"{selected_farmer['full_name']} will remove "
                    "the farmer account and its associated records. "
                    "This action cannot be undone."
                )

                delete_confirm_key = (
                    f"confirm_delete_farmer_{selected_farmer_id}"
                )

                if st.button(
                    "Delete Farmer",
                    key=f"delete_farmer_button_{selected_farmer_id}",
                    type="secondary",
                    use_container_width=False,
                ):
                    st.session_state[delete_confirm_key] = True

                if st.session_state.get(delete_confirm_key, False):

                    st.error(
                        "Are you sure? This will permanently delete "
                        "the farmer and associated records. "
                        "Choose Confirm Delete to continue or Cancel "
                        "to keep the farmer."
                    )

                    confirm_col1, confirm_col2 = st.columns(2)

                    with confirm_col1:

                        if st.button(
                            "Confirm Delete",
                            key=f"confirm_delete_button_{selected_farmer_id}",
                            type="primary",
                            use_container_width=True,
                        ):

                            try:

                                deleted = delete_farmer(
                                    selected_farmer_id
                                )

                            except ValueError as exc:

                                st.error(str(exc))

                            except Exception as exc:

                                st.error(
                                    f"Unable to delete farmer: {exc}"
                                )

                            else:

                                if deleted:

                                    st.session_state.pop(
                                        delete_confirm_key,
                                        None,
                                    )

                                    st.success(
                                        "Farmer and associated records "
                                        "deleted successfully."
                                    )

                                    st.rerun()

                                else:

                                    st.warning(
                                        "This farmer no longer exists."
                                    )

                                    st.session_state.pop(
                                        delete_confirm_key,
                                        None,
                                    )

                    with confirm_col2:

                        if st.button(
                            "Cancel",
                            key=f"cancel_delete_farmer_{selected_farmer_id}",
                            use_container_width=True,
                        ):
                            st.session_state.pop(
                                delete_confirm_key,
                                None,
                            )
                            st.rerun()

            st.divider()

            # ------------------------------------------------
            # SELECTED FARMER'S BATCHES
            # ------------------------------------------------

            st.subheader("Produce Batches")

            farmer_batches = get_farmer_batches(
                selected_farmer_id
            )

            if not farmer_batches:

                st.info(
                    "This farmer has no registered produce batches."
                )

            else:

                st.write(
                    f"**{len(farmer_batches)} "
                    f"produce batch(es) registered.**"
                )

                # ------------------------------------------------
                # BATCH CARDS
                # ------------------------------------------------

                for batch in farmer_batches:

                    with st.container(border=True):

                        batch_col1, batch_col2 = st.columns(
                            [1.1, 2.9],
                            vertical_alignment="center",
                        )

                        # --------------------------------------------
                        # CROP IMAGE
                        # --------------------------------------------

                        with batch_col1:

                            image_map = {
                                "Tomato":
                                    "assets/crops/tomato.jpg",

                                "Mango":
                                    "assets/crops/mango.jpg",

                                "Banana":
                                    "assets/crops/banana.jpg",

                                "Avocado":
                                    "assets/crops/avocado.jpg",

                                "Orange":
                                    "assets/crops/orange.jpg",

                                "Leafy Vegetables":
                                    "assets/crops/leafy_vegetables.jpg",
                            }

                            crop_image = image_map.get(
                                batch["produce_name"]
                            )

                            if crop_image:

                                crop_path = os.path.join(
                                    str(PROJECT_ROOT),
                                    crop_image,
                                )

                            else:

                                crop_path = None

                            if (
                                crop_path
                                and os.path.exists(crop_path)
                            ):

                                st.image(
                                    crop_path,
                                    use_container_width=True,
                                )

                            else:

                                st.info(
                                    "No crop image available."
                                )

                        # --------------------------------------------
                        # BATCH INFORMATION
                        # --------------------------------------------

                        with batch_col2:

                            st.subheader(
                                f"Batch #{batch['batch_id']}"
                            )

                            info_col1, info_col2 = st.columns(2)

                            with info_col1:

                                st.write(
                                    f"**Produce:** "
                                    f"{batch['produce_name']}"
                                )

                                st.write(
                                    f"**Quantity:** "
                                    f"{batch['quantity_kg']:.2f} KG"
                                )

                                st.write(
                                    f"**Harvest Date:** "
                                    f"{batch['harvest_date']}"
                                )

                            with info_col2:

                                st.write(
                                    f"**Initial Quality:** "
                                    f"{batch['initial_quality']}"
                                )

                                st.write(
                                    f"**Price:** "
                                    f"K{batch['asking_price_per_kg']:.2f}/KG"
                                )

                                st.write(
                                    f"**Status:** "
                                    f"{batch['status']}"
                                )


# ============================================================
# PAGE 3 â€” BUYERS
# ============================================================

elif page == "Buyers":
    buyers = get_all_buyers()


    st.header("Buyer Management")

    st.write(
        "Manage registered buyers and review buyer information."
    )

    if buyers:

        st.metric(
            "Registered Buyers",
            len(buyers),
        )

        st.divider()

        for buyer in buyers:

            with st.container(border=True):

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        f"**Buyer #{buyer['buyer_id']}**"
                    )

                    st.write(
                        f"**Name:** "
                        f"{buyer['full_name']}"
                    )

                    st.write(
                        f"**Buyer Type:** "
                        f"{buyer['buyer_type']}"
                    )

                    st.write(
                        f"**Phone:** "
                        f"{buyer['phone'] or 'Not provided'}"
                    )

                with col2:

                    st.write(
                        f"**Email:** "
                        f"{buyer['email'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Location:** "
                        f"{buyer['buyer_location'] or 'Not provided'}"
                    )

                    st.write(
                        f"**Registered:** "
                        f"{buyer['created_at']}"
                    )

                buyer_id = buyer["buyer_id"]
                confirm_key = f"confirm_delete_buyer_{buyer_id}"

                if not st.session_state.get(confirm_key, False):
                    if st.button(
                        "Delete Buyer",
                        key=f"delete_buyer_{buyer_id}",
                        type="secondary",
                    ):
                        st.session_state[confirm_key] = True
                        st.rerun()
                else:
                    st.warning(
                        f"Confirm deletion of Buyer #{buyer_id} "
                        f"({buyer['full_name']})?"
                    )
                    confirm_col, cancel_col = st.columns(2)

                    with confirm_col:
                        if st.button(
                            "Confirm Delete",
                            key=f"confirm_buyer_yes_{buyer_id}",
                            type="primary",
                        ):
                            try:
                                delete_buyer(buyer_id)
                                st.session_state.pop(confirm_key, None)
                                st.toast("Buyer deleted successfully.")
                                st.rerun()
                            except Exception as exc:
                                st.error(f"Could not delete buyer: {exc}")

                    with cancel_col:
                        if st.button(
                            "Keep Buyer",
                            key=f"confirm_buyer_no_{buyer_id}",
                        ):
                            st.session_state.pop(confirm_key, None)
                            st.rerun()

    else:

        st.info("No registered buyers found.")

    st.divider()


# ============================================================
# PAGE 4 â€” PRODUCE
# ============================================================

elif page == "Produce":
    produce = get_all_produce()


    st.title("Produce Management")

    st.caption(
        "View and manage the produce types registered "
        "in AGRO LIFE-AI."
    )

    # ============================================================
    # SUMMARY
    # ============================================================

    st.metric(
        "Produce Types",
        len(produce),
    )

    st.divider()

    if produce:

        produce_columns = st.columns(3)

        for index, item in enumerate(produce):

            with produce_columns[index % 3]:

                produce_id = item["produce_id"]
                produce_name = item["name"]
                category = item["category"]

                # ------------------------------------------------
                # FRIENDLY MODEL NAME
                # ------------------------------------------------

                model_name = item["model_name"]

                if model_name == "final_research_shelf_life_model.joblib":

                    friendly_model_name = "Research Shelf-Life Model"

                elif model_name:

                    friendly_model_name = (
                        model_name
                        .replace(".joblib", "")
                        .replace("_", " ")
                        .title()
                    )

                else:

                    friendly_model_name = "Not assigned"

                # ------------------------------------------------
                # FRIENDLY STATUS TEXT
                # ------------------------------------------------

                prediction_available = bool(
                    item["prediction_available"]
                )

                image_supported = bool(
                    item["image_supported"]
                )

                active = bool(
                    item["active"]
                )

                prediction_text = (
                    "Available"
                    if prediction_available
                    else "Not available"
                )

                image_text = (
                    "Supported"
                    if image_supported
                    else "Not supported"
                )

                status_text = (
                    "Active"
                    if active
                    else "Inactive"
                )

                # ------------------------------------------------
                # PRODUCE CARD
                # ------------------------------------------------

                with st.container(border=True):

                    st.subheader(produce_name)

                    st.write(
                        f"**Produce ID:** {produce_id}"
                    )

                    st.write(
                        f"**Category:** {category}"
                    )

                    st.write(
                        f"**AI Model:** {friendly_model_name}"
                    )

                    st.write(
                        f"**Shelf-Life Prediction:** "
                        f"{prediction_text}"
                    )

                    st.write(
                        f"**Image Recognition:** "
                        f"{image_text}"
                    )

                    st.write(
                        f"**Status:** {status_text}"
                    )

                    # =================================================
                    # DELETE / CONFIRM / CANCEL
                    # =================================================

                    delete_key = f"delete_produce_{produce_id}"
                    confirm_key = (
                        f"confirm_delete_produce_{produce_id}"
                    )

                    if delete_key not in st.session_state:
                        st.session_state[delete_key] = False

                    if confirm_key not in st.session_state:
                        st.session_state[confirm_key] = False

                    if st.button(
                        "Delete",
                        key=f"delete_button_{produce_id}",
                        use_container_width=True,
                    ):

                        st.session_state[delete_key] = True
                        st.rerun()

                    # ------------------------------------------------
                    # CONFIRMATION AREA
                    # ------------------------------------------------

                    if st.session_state[delete_key]:

                        st.warning(
                            f"Are you sure you want to delete "
                            f"{produce_name}?"
                        )

                        confirm_col, cancel_col = st.columns(2)

                        with confirm_col:

                            if st.button(
                                "Confirm Delete",
                                key=f"confirm_button_{produce_id}",
                                use_container_width=True,
                            ):

                                st.session_state[confirm_key] = True

                        with cancel_col:

                            if st.button(
                                "Cancel",
                                key=f"cancel_button_{produce_id}",
                                use_container_width=True,
                            ):

                                st.session_state[delete_key] = False
                                st.session_state[confirm_key] = False
                                st.rerun()

                        # ------------------------------------------------
                        # DELETE ONLY AFTER CONFIRMATION
                        # ------------------------------------------------

                        if st.session_state.get(
                            confirm_key,
                            False,
                        ):

                            st.info(
                                "Produce deletion is ready to be connected "
                                "to the database."
                            )

    else:

        st.info("No produce types found.")


# ============================================================
# PAGE 5 â€” PREDICTIONS
# ============================================================

elif page == "Predictions":
    predictions = get_all_predictions()
    history = get_all_prediction_history()
    recommendations = get_all_recommendations()


    st.header("AI Predictions")

    st.write(
        "Monitor AI shelf-life predictions and research results."
    )

    prediction_col1, prediction_col2, prediction_col3 = (
        st.columns(3)
    )

    with prediction_col1:

        st.metric(
            "AI Predictions",
            len(predictions),
        )

    with prediction_col2:

        st.metric(
            "History Records",
            len(history),
        )

    with prediction_col3:

        st.metric(
            "Recommendations",
            len(recommendations),
        )

    st.divider()

    if predictions:

        st.subheader("Recent Prediction Records")

        for prediction in predictions[:10]:

            with st.container(border=True):

                st.write(
                    f"**Prediction #{prediction['prediction_id']}**"
                )

                st.write(
                    f"**Produce:** "
                    f"{prediction['produce_name']}"
                )

                if prediction.get("batch_id") is not None:

                    st.write(
                        f"**Batch:** "
                        f"#{prediction['batch_id']}"
                    )

                st.write(
                    f"**Input Method:** "
                    f"{prediction['input_method']}"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        f"**Total Shelf Life:** "
                        f"{prediction['total_shelf_life_days']:.2f} days"
                    )

                with col2:

                    st.write(
                        f"**Current Storage:** "
                        f"{prediction['current_storage_days']:.2f} days"
                    )

                st.write(
                    f"**Remaining Shelf Life:** "
                    f"{prediction['remaining_shelf_life_days']:.2f} days"
                )

                prediction_id = prediction["prediction_id"]
                confirm_key = f"confirm_delete_prediction_{prediction_id}"

                if not st.session_state.get(confirm_key, False):
                    if st.button(
                        "Delete Prediction",
                        key=f"delete_prediction_{prediction_id}",
                        type="secondary",
                    ):
                        st.session_state[confirm_key] = True
                        st.rerun()
                else:
                    st.warning(
                        f"Delete Prediction #{prediction_id}? "
                        "Its associated history and recommendations "
                        "will also be removed."
                    )
                    confirm_col, cancel_col = st.columns(2)

                    with confirm_col:
                        if st.button(
                            "Confirm Delete",
                            key=f"confirm_prediction_yes_{prediction_id}",
                            type="primary",
                        ):
                            try:
                                delete_prediction(prediction_id)
                                st.session_state.pop(confirm_key, None)
                                st.toast("Prediction deleted successfully.")
                                st.rerun()
                            except Exception as exc:
                                st.error(
                                    f"Could not delete prediction: {exc}"
                                )

                    with cancel_col:
                        if st.button(
                            "Keep Prediction",
                            key=f"confirm_prediction_no_{prediction_id}",
                        ):
                            st.session_state.pop(confirm_key, None)
                            st.rerun()

    else:

        st.info("No AI predictions found.")


# ============================================================
# PAGE 6 â€” MARKETPLACE
# ============================================================

elif page == "Marketplace":
    marketplace = get_marketplace_statistics()


    st.header("Marketplace Administration")

    st.write(
        "Monitor marketplace listings, availability and "
        "reservation activity."
    )

    marketplace_col1, marketplace_col2, marketplace_col3, marketplace_col4 = (
        st.columns(4)
    )

    with marketplace_col1:

        st.metric(
            "Total Listings",
            marketplace["total_listings"],
        )

    with marketplace_col2:

        st.metric(
            "Available",
            marketplace["available"],
        )

    with marketplace_col3:

        st.metric(
            "Reserved",
            marketplace["reserved"],
        )

    with marketplace_col4:

        st.metric(
            "Available Quantity",
            f"{marketplace['available_quantity_kg']:.2f} KG",
        )

    st.divider()

    listings = get_all_market_listings()

    st.subheader("Marketplace Listings")

    if not listings:
        st.info("No marketplace listings found.")
    else:
        for listing in listings:
            listing_id = listing["listing_id"]
            status = str(listing["listing_status"] or "").upper()
            buyer_id = listing.get("buyer_id")

            with st.container(border=True):
                listing_col1, listing_col2 = st.columns(2)

                with listing_col1:
                    st.write(f"**Listing #{listing_id}**")
                    st.write(f"**Produce:** {listing['produce_name']}")
                    st.write(f"**Seller:** {listing['seller_name']}")
                    st.write(f"**Batch:** #{listing['batch_id']}")
                    st.write(
                        f"**Quantity:** "
                        f"{listing['quantity_available_kg']:.2f} kg"
                    )
                    st.write(
                        f"**Price:** "
                        f"{listing['price_per_kg']:.2f} per kg"
                    )

                with listing_col2:
                    st.write(f"**Quality:** {listing['quality_status']}")
                    st.write(f"**Status:** {status}")
                    st.write(f"**Created:** {listing['created_at']}")

                    if listing.get("buyer_name"):
                        st.write(f"**Assigned Buyer:** {listing['buyer_name']}")

                # Do not cancel reserved or sold listings, or listings
                # that already have a buyer assigned.
                can_cancel = (
                    status in {"AVAILABLE", "EXPIRED"}
                    and buyer_id is None
                )

                if can_cancel:
                    confirm_key = f"confirm_cancel_listing_{listing_id}"

                    if not st.session_state.get(confirm_key, False):
                        if st.button(
                            "Cancel Listing",
                            key=f"cancel_listing_{listing_id}",
                            type="secondary",
                        ):
                            st.session_state[confirm_key] = True
                            st.rerun()
                    else:
                        st.warning(
                            f"Cancel Listing #{listing_id}? "
                            "The listing record will be preserved."
                        )
                        confirm_col, keep_col = st.columns(2)

                        with confirm_col:
                            if st.button(
                                "Confirm Cancellation",
                                key=f"confirm_listing_yes_{listing_id}",
                                type="primary",
                            ):
                                try:
                                    updated = update_market_listing_status(
                                        listing_id,
                                        "CANCELLED",
                                    )
                                    if updated:
                                        st.session_state.pop(confirm_key, None)
                                        st.toast("Listing cancelled successfully.")
                                        st.rerun()
                                    else:
                                        st.error("Listing was not found.")
                                except Exception as exc:
                                    st.error(
                                        f"Could not cancel listing: {exc}"
                                    )

                        with keep_col:
                            if st.button(
                                "Keep Listing",
                                key=f"confirm_listing_no_{listing_id}",
                            ):
                                st.session_state.pop(confirm_key, None)
                                st.rerun()
                else:
                    st.caption(
                        "Cancellation unavailable for this listing's "
                        "current status or buyer assignment."
                    )
    # ============================================================
# CUSTOMER CAMERA ASSESSMENTS
# ============================================================

elif page == "Customer Assessments":

    st.header("Customer Camera Assessments")

    st.write(
        "Monitor automatic computer-vision assessments "
        "performed for customers."
    )

    assessments = get_all_customer_camera_assessments()

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    total_assessments = len(assessments)

    fresh_count = sum(
        1
        for assessment in assessments
        if assessment["predicted_class"] == "Fresh"
    )

    rotten_count = sum(
        1
        for assessment in assessments
        if assessment["predicted_class"] == "Rotten"
    )

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        st.metric(
            "Total Assessments",
            total_assessments,
        )

    with summary_col2:
        st.metric(
            "Fresh",
            fresh_count,
        )

    with summary_col3:
        st.metric(
            "Rotten",
            rotten_count,
        )

    st.divider()

    # --------------------------------------------------------
    # ASSESSMENT RECORDS
    # --------------------------------------------------------

    if not assessments:

        st.info(
            "No customer camera assessments have been "
            "recorded yet."
        )

    else:

        for assessment in assessments:

            with st.container(border=True):

                col1, col2 = st.columns([2, 1])

                with col1:

                    st.subheader(
                        assessment["customer_name"]
                        or "Unknown Customer"
                    )

                    st.write(
                        f"**Produce:** "
                        f"{assessment['produce_name']}"
                    )

                    st.write(
                        f"**AI Decision:** "
                        f"{assessment['predicted_class']}"
                    )

                    probability = assessment[
                        "model_probability"
                    ]

                    if probability is not None:

                        st.write(
                            f"**Confidence:** "
                            f"{probability * 100:.2f}%"
                        )

                    st.write(
                        f"**Date & Time:** "
                        f"{assessment['created_at']}"
                    )

                with col2:

                    image_path = assessment["image_path"]

                    if image_path and os.path.exists(
                        image_path
                    ):

                        st.image(
                            image_path,
                            caption="Captured Image",
                            use_container_width=True,
                        )

                    else:

                        st.info(
                            "Captured image not available."
                        )

                assessment_id = assessment["assessment_id"]
                confirm_key = (
                    f"confirm_delete_assessment_{assessment_id}"
                )

                if not st.session_state.get(confirm_key, False):
                    if st.button(
                        "Delete Assessment",
                        key=f"delete_assessment_{assessment_id}",
                        type="secondary",
                    ):
                        st.session_state[confirm_key] = True
                        st.rerun()
                else:
                    st.warning(
                        f"Delete Assessment #{assessment_id}? "
                        "The database record will be removed, but the "
                        "image file will be left untouched."
                    )
                    confirm_col, cancel_col = st.columns(2)

                    with confirm_col:
                        if st.button(
                            "Confirm Delete",
                            key=f"confirm_assessment_yes_{assessment_id}",
                            type="primary",
                        ):
                            try:
                                delete_customer_camera_assessment(
                                    assessment_id
                                )
                                st.session_state.pop(confirm_key, None)
                                st.toast("Assessment deleted successfully.")
                                st.rerun()
                            except Exception as exc:
                                st.error(
                                    f"Could not delete assessment: {exc}"
                                )



