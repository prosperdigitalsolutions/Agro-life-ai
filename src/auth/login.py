"""
AGRO LIFE-AI
Login and Role-Based Dashboard Router

Handles:
- Login screen
- User authentication
- Session management
- Role-based dashboard routing
"""

import streamlit as st

from src.auth.auth_manager import authenticate_user


# ============================================================
# THEME
# ============================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------------
       MAIN APPLICATION
    -------------------------------------------------------- */

    .stApp {
        background: #f5faf7;
    }

    /* --------------------------------------------------------
       HIDE STREAMLIT ELEMENTS
    -------------------------------------------------------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    /* --------------------------------------------------------
       LOGIN CONTAINER
    -------------------------------------------------------- */

    .login-wrapper {
        max-width: 480px;
        margin: 70px auto 0 auto;
    }

    .login-brand {
        text-align: center;
        margin-bottom: 30px;
    }

    .login-brand h1 {
        color: #075b36;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .login-brand p {
        color: #557065;
        font-size: 15px;
        margin: 0;
    }

    .login-card {
        background: white;
        border: 1px solid #dce9df;
        border-radius: 16px;
        padding: 35px;
        box-shadow: 0 8px 25px rgba(4, 52, 34, 0.08);
    }

    .login-title {
        color: #075b36;
        font-size: 23px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .login-subtitle {
        color: #66776e;
        font-size: 14px;
        margin-bottom: 25px;
    }

    /* --------------------------------------------------------
       INPUTS
    -------------------------------------------------------- */

    .stTextInput label {
        color: #075b36 !important;
        font-weight: 600;
    }

    .stTextInput input {
        border: 1px solid #dce9df;
        border-radius: 8px;
    }

    .stTextInput input:focus {
        border-color: #087b38;
    }

    /* --------------------------------------------------------
       LOGIN BUTTON
    -------------------------------------------------------- */

    .stButton > button {
        width: 100%;
        background: #087b38;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 11px 18px;
        font-weight: 600;
        font-size: 15px;
    }

    .stButton > button:hover {
        background: #075b36;
        color: white;
    }

    /* --------------------------------------------------------
       FOOTER
    -------------------------------------------------------- */

    .login-footer {
        text-align: center;
        margin-top: 25px;
        color: #718078;
        font-size: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None




# ============================================================
# LOGIN HEADER
# ============================================================

st.markdown(
    "<h1 style='text-align:center; color:#075b36;'>AGRO LIFE-AI</h1>",
    unsafe_allow_html=True,
)

st.markdown(
    "<p style='text-align:center; color:#557065;'>"
    "Technology for a Greener Tomorrow"
    "</p>",
    unsafe_allow_html=True,
)

st.write("")


# ============================================================
# LOGIN TITLE
# ============================================================

st.markdown(
    "<h2 style='color:#075b36;'>Welcome Back</h2>",
    unsafe_allow_html=True,
)

st.markdown(
    "<p style='color:#66776e;'>"
    "Sign in to access your AGRO LIFE-AI dashboard."
    "</p>",
    unsafe_allow_html=True,
)

account_type = st.radio(
    "Account Type",
    ["Administrator", "Farmer"],
    horizontal=True,
    key="login_account_type",
)
username = st.text_input(
    "Username",
    placeholder="Enter your username",
    key="login_username",
)

password = st.text_input(
    "Password",
    type="password",
    placeholder="Enter your password",
    key="login_password",
)

login_clicked = st.button(
    "Sign In",
    use_container_width=True,
    key="login_submit",
)


# ============================================================
# LOGIN PROCESS
# ============================================================

if login_clicked:
    username = username.strip()

    if not username or not password:
        st.warning("Please enter both username and password.")
    else:
        user = authenticate_user(username, password)

        if user:
            selected_role = (
                "ADMIN" if account_type == "Administrator" else "FARMER"
            )

            actual_role = user.get("user_type", "").upper()

            if actual_role != selected_role:
                st.error(
                    f"This account is registered as {actual_role}. "
                    f"Please select {actual_role.title()} as the Account Type."
                )
            else:
                st.session_state.authenticated = True
                st.session_state.user = user

                st.success(f"Welcome, {user['full_name']}!")

                st.rerun()
        else:
            st.error("Invalid username or password.")


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="login-footer">
        AGRO LIFE-AI | Biochemical Decay & Shelf-Life Predictor
    </div>
    """,
    unsafe_allow_html=True,
)