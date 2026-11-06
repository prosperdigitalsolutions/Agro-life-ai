import base64
from pathlib import Path

import streamlit as st

from src.auth.auth_manager import authenticate_user, change_user_password
import logging

# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AGRO LIFE-AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="auto",
)


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None


# ============================================================
# GLOBAL STYLING
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --agro-green: #075b36;
        --agro-dark: #043422;
        --agro-primary: #087b38;
        --agro-background: #f5faf7;
        --agro-border: #dce9df;
        --agro-text: #263b30;
        --agro-muted: #718477;
    }

    .stApp {
        background-color: var(--agro-background);
    }

    [data-testid="stSidebar"] {
        background-color: var(--agro-dark);
        border-right: 1px solid #174b34;
    }

    [data-testid="stSidebar"] > div:first-child {
        background-color: var(--agro-dark);
    }

    [data-testid="stSidebar"] * {
        color: #ffffff;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #d0e5d7;
    }

    [data-testid="stSidebar"] hr {
        border-color: #285640;
    }

    .agro-brand {
        font-size: 25px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.6px;
        margin-top: 16px;
        margin-bottom: 5px;
    }

    .agro-tagline {
        color: #b9d8c5;
        font-size: 13px;
        line-height: 1.6;
        margin-bottom: 30px;
    }

    .nav-heading {
        font-size: 11px;
        font-weight: 700;
        color: #8fbca0;
        letter-spacing: 1.5px;
        margin-top: 25px;
        margin-bottom: 14px;
    }

    .dashboard-item {
        display: block;
        padding: 14px 13px;
        margin-bottom: 10px;
        border-radius: 9px;
        background: rgba(255, 255, 255, 0.055);
        border: 1px solid rgba(255, 255, 255, 0.09);
        color: #ffffff;
        font-size: 14px;
        font-weight: 600;
    }

    .dashboard-item.active {
        background: #087b38;
        border-color: #16944b;
    }

    .dashboard-description {
        color: #b9d8c5;
        font-size: 12px;
        line-height: 1.6;
        margin-top: 18px;
    }

    .sidebar-footer {
        color: #8fbca0;
        font-size: 11px;
        margin-top: 45px;
        padding-top: 15px;
        border-top: 1px solid #285640;
    }

    .login-container {
        max-width: 560px;
        margin: 55px auto 0 auto;
        padding: 30px 32px;
        background: #ffffff;
        border: 1px solid var(--agro-border);
        border-radius: 16px;
        box-shadow: 0 8px 28px rgba(4, 52, 34, 0.055);
    }

    .login-brand {
        color: var(--agro-green);
        font-size: 31px;
        font-weight: 800;
        letter-spacing: -0.8px;
        margin-bottom: 4px;
    }

    .login-tagline {
        color: #527461;
        font-size: 14px;
        margin-bottom: 34px;
    }

    .welcome-heading {
        color: var(--agro-text);
        font-size: 28px;
        font-weight: 750;
        margin-bottom: 8px;
    }

    .welcome-description {
        color: var(--agro-muted);
        font-size: 14px;
        line-height: 1.7;
        margin-bottom: 24px;
    }

    [data-testid="stTextInput"] label {
        color: #344d3e;
        font-weight: 600;
    }

    [data-testid="stTextInput"] input {
        border: 1px solid #d5e3d9;
        border-radius: 8px;
        min-height: 44px;
    }

    [data-testid="stTextInput"] input:focus {
        border-color: #087b38;
        box-shadow: 0 0 0 1px #087b38;
    }

    [data-testid="stFormSubmitButton"] button {
        background-color: #087b38;
        color: white;
        border: none;
        border-radius: 8px;
        min-height: 46px;
        font-weight: 700;
        margin-top: 8px;
    }

    [data-testid="stFormSubmitButton"] button:hover {
        background-color: #065d2c;
        color: white;
        border: none;
    }

    .login-footer {
        color: #849589;
        font-size: 12px;
        text-align: center;
        margin-top: 22px;
    }

    @media (max-width: 768px) {
        .login-container {
            margin: 15px auto;
            padding: 22px 18px;
        }

        .login-brand {
            font-size: 26px;
        }

        .welcome-heading {
            font-size: 24px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():

    # --------------------------------------------------------
    # LEFT SIDEBAR
    # --------------------------------------------------------

    with st.sidebar:


        logo_base64 = base64.b64encode(
            (Path(__file__).resolve().parent / "assets" / "agro_life_ai_logo.png").read_bytes()
        ).decode("ascii")

        st.markdown(
            """
            <div style="text-align:center; margin-bottom:14px;">
                <img src="data:image/png;base64,__AGRO_LIFE_AI_LOGO_BASE64__" alt="AGRO LIFE-AI Logo" style="width:240px; max-width:100%; height:auto;">
            </div>

            <div class="agro-brand">AGRO LIFE-AI</div>

            <div class="agro-tagline">
                Technology for a Greener Tomorrow
            </div>

            <hr>

            <div class="nav-heading">DASHBOARDS</div>

            <div class="dashboard-description">
                One platform connecting agricultural
                management, farmers and customers.
            </div>

            <div class="sidebar-footer">
                AGRO LIFE-AI<br>
                Agricultural Intelligence Platform
            </div>
            """.replace("__AGRO_LIFE_AI_LOGO_BASE64__", logo_base64),
            unsafe_allow_html=True,
        )

        # Interactive dashboard environment selectors
        st.markdown("### Select Dashboard")

        selected_role = st.session_state.setdefault(
            "selected_login_role", "ADMIN"
        )

        dashboard_options = [
            ("ADMIN", "ADMIN DASHBOARD"),
            ("FARMER", "FARMER DASHBOARD"),
            ("CUSTOMER", "CUSTOMER DASHBOARD"),
        ]

        for role_name, label in dashboard_options:
            button_label = (
                "✓ " + label
                if selected_role == role_name
                else label
            )

            if st.button(
                button_label,
                key="select_environment_" + role_name.lower(),
                use_container_width=True,
            ):
                st.session_state["selected_login_role"] = role_name
                st.rerun()

        selected_role = st.session_state["selected_login_role"]

        st.success(
            "Selected environment: " + selected_role + " DASHBOARD"
        )

    # --------------------------------------------------------
    # RIGHT LOGIN PANEL
    # --------------------------------------------------------

    left_space, center, right_space = st.columns(
        [0.65, 2.7, 0.65]
    )

    with center:

        st.title("AGRO LIFE-AI")

        st.caption("Technology for a Greener Tomorrow")

        st.subheader("Welcome Back")

        st.write(
            "Sign in to access your agricultural "
            "management dashboard."
        )

        # ----------------------------------------------------
        # LOGIN FORM
        # ----------------------------------------------------

        with st.form("agro_life_login_form"):

            username = st.text_input(
                "Username",
                placeholder="Enter your username",
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
            )

            submitted = st.form_submit_button(
                "Sign In",
                type="primary",
                use_container_width=True,
            )

            if submitted:

                if not username.strip() or not password:

                    st.warning(
                        "Please enter your username and password."
                    )

                else:

                    try:

                        user = authenticate_user(
                            username.strip(),
                            password,
                        )

                        if user:

                            actual_role = str(
                                user.get("user_type", "")
                            ).strip().upper()

                            selected_role = st.session_state.get(
                                "selected_login_role", "ADMIN"
                            )

                            allowed_roles = {
                                "ADMIN": ("ADMIN",),
                                "FARMER": ("FARMER",),
                                "CUSTOMER": ("BUYER", "CUSTOMER"),
                            }

                            if actual_role not in allowed_roles.get(
                                selected_role, ()
                            ):
                                st.error(
                                    "Your credentials are valid, but this "
                                    "account does not belong to the "
                                    + selected_role
                                    + " environment. Select the correct "
                                    "dashboard and try again."
                                )

                            else:
                                st.session_state["user"] = user
                                st.session_state["authenticated"] = True

                                st.rerun()

                        else:

                            st.error(
                                "Invalid username or password."
                            )

                    except Exception:

                        logging.exception("AGRO LIFE-AI LOGIN ERROR")

                        st.error(
                            "Login failed. Please try again. "
                            "The technical error has been recorded."
                        )

        st.markdown(
            """
            <div class="login-footer">
                Secure sign-in · Role-based dashboard access
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# ============================================================
# SELF-SERVICE PASSWORD MANAGEMENT
# ============================================================

def change_password_page():
    """Allow an authenticated user to change their own password."""

    user = st.session_state.get("user")

    if not st.session_state.get("authenticated") or not isinstance(user, dict):
        st.error("Please sign in to manage your password.")
        return

    user_id = user.get("user_id")

    if not user_id:
        st.error("Your account session is invalid. Please sign in again.")
        return

    st.title("My Account")
    st.subheader("Change Password")
    st.caption("Update the password for your own AGRO LIFE-AI account.")

    with st.form("change_password_form", clear_on_submit=True):
        current_password = st.text_input(
            "Current password",
            type="password",
            autocomplete="current-password",
        )

        new_password = st.text_input(
            "New password",
            type="password",
            help="Use at least 8 characters. A longer, unique password is recommended.",
            autocomplete="new-password",
        )

        confirm_password = st.text_input(
            "Confirm new password",
            type="password",
            autocomplete="new-password",
        )

        submitted = st.form_submit_button(
            "Update Password",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not current_password or not new_password or not confirm_password:
            st.error("Complete all three password fields.")
            return

        if new_password != confirm_password:
            st.error("The new passwords do not match.")
            return

        if len(new_password) < 8:
            st.error("Your new password must contain at least 8 characters.")
            return

        if len(new_password) > 1024:
            st.error("Your new password is too long.")
            return

        success, message = change_user_password(
            user_id,
            current_password,
            new_password,
        )

        if success:
            st.success(message)
        else:
            st.error(message)


# ROLE-BASED NAVIGATION
# ============================================================

user = st.session_state.get("user")

if not st.session_state["authenticated"] or not user:

    st.session_state["authenticated"] = False
    st.session_state["user"] = None

    page = st.Page(
        login_page,
        title="Sign In",
        default=True,
    )

else:

    role = str(
        user.get("user_type", "")
    ).strip().upper()

    if role == "ADMIN":

        page = st.Page(
            "src/dashboard/admin_dashboard.py",
            title="Admin Dashboard",
            default=True,
        )

    elif role == "FARMER":

        page = st.Page(
            "src/dashboard/farmer_dashboard.py",
            title="Farmer Dashboard",
            default=True,
        )

    elif role in ("BUYER", "CUSTOMER"):

        page = st.Page(
            "src/customers/customer_dashboard.py",
            title="Customer Dashboard",
            default=True,
        )

    else:

        st.error(f"Unknown user role: {role}")
        st.stop()


# Add the account page without replacing the role-specific dashboard.
password_page = st.Page(
    change_password_page,
    title="My Account",
    url_path="my-account",
)

if st.session_state.get("authenticated") and st.session_state.get("user"):
    st.sidebar.divider()
    st.sidebar.page_link(
        password_page,
        label="My Account / Change Password",
        icon=":material/lock_reset:",
    )


# ============================================================
# RUN APPLICATION
# ============================================================

navigation = st.navigation(
    [page, password_page],
    position="hidden",
)

navigation.run()


