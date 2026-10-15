import streamlit as st

from src.auth.auth_manager import authenticate_user


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AGRO LIFE-AI",
    page_icon="🌱",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None


# ============================================================
# LOGIN SCREEN
# ============================================================

def login_page():

    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f5faf7;
        }

        .login-title {
            color: #075b36;
            text-align: center;
            font-size: 38px;
            font-weight: 800;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    _, center, _ = st.columns([1, 1.2, 1])

    with center:
        st.markdown(
            '<div class="login-title">AGRO LIFE-AI</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            "<p style='text-align:center;color:#527461;'>"
            "Technology for a Greener Tomorrow"
            "</p>",
            unsafe_allow_html=True,
        )

        st.subheader("Welcome Back")

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            submitted = st.form_submit_button(
                "Sign In",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                if not username.strip() or not password:
                    st.warning("Enter your username and password.")
                else:
                    user = authenticate_user(
                        username.strip(),
                        password,
                    )

                    if user:
                        st.session_state["user"] = user
                        st.session_state["authenticated"] = True
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")


# ============================================================
# ROLE-BASED ROUTING
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
    role = str(user.get("user_type", "")).strip().upper()

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


# ============================================================
# RUN APPLICATION
# ============================================================

navigation = st.navigation([page], position="hidden")
navigation.run()