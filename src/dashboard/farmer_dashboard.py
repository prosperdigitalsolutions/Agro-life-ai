import os
import base64
import streamlit as st
import sys

from abc import ABC, abstractmethod
from pathlib import Path
from textwrap import dedent
from src.auth.auth_manager import has_role, logout_user
from src.core.user_prediction_workflow import (
    run_farmer_batch_prediction_workflow,
)

from src.database.database_manager import (
    get_batch_research_measurements,
)


class markdown(ABC):
    """Base interface for markdown rendering helpers."""

    @abstractmethod
    def render(self, text: str) -> str:
        """Return a markdown-safe representation of text."""
        raise NotImplementedError

    @abstractmethod
    def heading(self, text: str, level: int = 1) -> str:
        """Build a heading block of the requested markdown level."""
        raise NotImplementedError

    @abstractmethod
    def bullet_list(self, items) -> str:
        """Render a bullet list from a sequence of strings."""
        raise NotImplementedError

    @abstractmethod
    def numbered_list(self, items) -> str:
        """Render a numbered list from a sequence of strings."""
        raise NotImplementedError

    @abstractmethod
    def code(self, code: str, language: str = "python") -> str:
        """Render a fenced code block."""
        raise NotImplementedError

    @abstractmethod
    def quote(self, text: str) -> str:
        """Render a markdown blockquote."""
        raise NotImplementedError

    @abstractmethod
    def link(self, label: str, url: str) -> str:
        """Render a hyperlink."""
        raise NotImplementedError


class DefaultMarkdown(markdown):
    """A practical markdown renderer for streamlit-style application content."""

    def render(self, text: str) -> str:
        return (text or "").strip()

    def heading(self, text: str, level: int = 1) -> str:
        level = max(1, min(int(level), 6))
        return f"{'#' * level} {text.strip()}"

    def bullet_list(self, items) -> str:
        cleaned = [str(item).strip() for item in (items or []) if str(item).strip()]
        return "\n".join(f"- {item}" for item in cleaned) if cleaned else "- No items"

    def numbered_list(self, items) -> str:
        cleaned = [str(item).strip() for item in (items or []) if str(item).strip()]
        return "\n".join(f"{index}. {item}" for index, item in enumerate(cleaned, start=1)) if cleaned else "1. No items"

    def code(self, code: str, language: str = "python") -> str:
        body = (code or "").strip()
        return f"```{language}\n{body}\n```" if body else f"```{language}\n\n```"

    def quote(self, text: str) -> str:
        body = (text or "").strip()
        return "\n".join(f"> {line}" for line in body.splitlines()) if body else "> "

    def link(self, label: str, url: str) -> str:
        if not label:
            label = url
        return f"[{label}]({url})"


markdown_renderer = DefaultMarkdown()
# ============================================================
# PROJECT PATH
# ============================================================

SRC_DIR = Path(__file__).resolve().parents[1]
project_root = SRC_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def get_crop_image(produce_name):

    project_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )

    image_map = {
        "Tomato": "tomato.jpg",
        "Mango": "mango.jpg",
        "Banana": "banana.jpg",
        "Avocado": "avocado.jpg",
        "Orange": "orange.jpg",
        "Leafy Vegetables": "leafy_vegetables.jpg",
    }

    filename = image_map.get(produce_name)

    if not filename:
        return None

    image_path = os.path.join(
        project_root,
        "assets",
        "crops",
        filename
    )

    if os.path.exists(image_path):
        return image_path

    return None


# ============================================================
# DATABASE IMPORTS
# ============================================================
from database.database_manager import (
    get_connection,
    get_farmer_dashboard,
    get_all_farmers,
    get_all_produce,
    get_farmer_batches,
    add_produce_batch,
    add_quality_record,
    add_storage_record,
    get_batch_quality_records,
    get_batch_storage_records,
    get_farmer_market_listings,
    add_market_listing,
    update_market_listing_status,
    add_buyer,
    get_all_buyers,
    assign_buyer_to_market_listing,
    get_marketplace_statistics,
    update_batch_status,
    get_batch_predictions,
    delete_produce_batch,
)
st.markdown(
    """
    <style>

    /* =========================================================
       AGRO LIFE-AI — REFERENCE DASHBOARD THEME
       ========================================================= */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    [data-testid="stToolbar"] {
        visibility: visible;
    }

    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"] {
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
    }

    .stApp {
        background: #f5faf7;
    }

    .block-container {
        padding-top: 0.8rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        max-width: 100%;
    }

/* =========================================================
   SIDEBAR
   ========================================================= */

[data-testid="stSidebar"] {
    background: #043422;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1.2rem 0.8rem;
}

.sidebar-logo {
    text-align: center;
    padding: 5px 0 18px 0;
}

.sidebar-logo img {
    width: 82px;
    height: 82px;
    object-fit: contain;
    border-radius: 50%;
}

.sidebar-brand {
    font-size: 22px;
    font-weight: 800;
    letter-spacing: 0.5px;
    margin-top: 8px;
    color: white !important;
}

.sidebar-subtitle {
    font-size: 11px;
    color: #d7f5df !important;
    margin-top: 2px;
}

/* =========================================================
   SIDEBAR NAVIGATION
   ========================================================= */

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

/* =========================================================
   TOP HEADER
   ========================================================= */

.top-header {
    background: white;
    padding: 18px 24px;
    border: 1px solid #dce9df;
    border-radius: 14px;
    margin-bottom: 18px;

    display: flex;
    align-items: center;
    justify-content: space-between;

    box-sizing: border-box;
}

.top-header-title {
    color: #075b36;
    font-size: 25px;
    font-weight: 800;
    line-height: 1.2;
    margin: 0;
}

.top-header-subtitle {
    color: #23704c;
    font-size: 12px;
    font-weight: 500;
    margin-top: 5px;
}

.top-header-brand {
    color: #075b36;
    font-size: 14px;
    font-weight: 700;
    white-space: nowrap;
}

    /* =========================================================
       WELCOME BANNER
       ========================================================= */

    .welcome-banner {
        background: linear-gradient(
            90deg,
            #e8f6eb,
            #f7fcf8
        );
        border-radius: 16px;
        padding: 22px 28px;
        min-height: 105px;
        border: 1px solid #e0eee4;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
    }

    .welcome-icon {
        font-size: 54px;
        margin-right: 22px;
    }

    .welcome-title {
        color: #075b36;
        font-size: 27px;
        font-weight: 800;
        margin: 0;
    }

    .welcome-text {
        color: #175c3c;
        font-size: 15px;
        margin-top: 4px;
    }

    /* =========================================================
       SECTION HEADINGS
       ========================================================= */

    .section-title {
        color: #075b36;
        font-size: 19px;
        font-weight: 800;
        margin-top: 18px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .section-line {
        height: 1px;
        background: #69ad83;
        flex: 1;
        margin-left: 8px;
    }

    /* =========================================================
       CARDS
       ========================================================= */

    .dashboard-card {
        background: white;
        border: 1px solid #dce9df;
        border-radius: 14px;
        padding: 17px;
        box-shadow: 0 2px 8px rgba(0, 70, 40, 0.05);
        margin-bottom: 10px;
    }

    .card-label {
        color: #397357;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.4px;
    }

    .card-value {
        color: #075b36;
        font-size: 21px;
        font-weight: 800;
        margin-top: 5px;
    }

    .big-value {
        color: #075b36;
        font-size: 25px;
        font-weight: 800;
        margin-top: 5px;
    }

    /* =========================================================
       STREAMLIT BUTTONS
       ========================================================= */

    .stButton > button {
        border-radius: 9px;
        border: none;
        background: #087b38;
        color: white;
        font-weight: 600;
    }

    .stButton > button:hover {
        background: #075b36;
        color: white;
    }

    /* =========================================================
       SELECTBOX
       ========================================================= */

    .stSelectbox label {
        color: #075b36 !important;
        font-weight: 600;
    }

    /* =========================================================
       REMOVE EXCESSIVE STREAMLIT SPACING
       ========================================================= */

    div[data-testid="stVerticalBlock"] {
        gap: 0.45rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)




# ============================================================
# LOAD FARMERS
# ============================================================

all_farmers = get_all_farmers()

if not all_farmers:
    st.error("No farmers are currently registered.")
    st.stop()

# ============================================================
# AUTHENTICATED FARMER PROFILE
# ============================================================

logged_in_user = st.session_state.get("user") or {}
logged_in_role = str(
    logged_in_user.get("user_type", "")
).strip().upper()

if logged_in_role != "FARMER":
    st.error("Access denied. This dashboard is reserved for farmer accounts.")
    st.stop()

logged_in_user_id = logged_in_user.get("user_id")

if logged_in_user_id is None:
    st.error("Your login session does not contain a valid user ID. Please sign in again.")
    st.stop()

matching_farmers = [
    farmer for farmer in all_farmers
    if str(farmer.get("user_id")) == str(logged_in_user_id)
]

if len(matching_farmers) != 1:
    st.error(
        "Your login is not linked to exactly one farmer profile. "
        "Please contact the administrator to verify your registration."
    )
    st.stop()

current_farmer = matching_farmers[0]
farmer_id = current_farmer["farmer_id"]

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # LOGO / BRAND
    # --------------------------------------------------------

    logo_path = os.path.join(
        project_root,
        "assets",
        "agro_life_ai_logo.png"
    )

    if os.path.exists(logo_path):
        st.image(
            logo_path,
            width=82,
        )

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
    # AUTHENTICATED FARMER
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
            MY FARM PROFILE
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"**{current_farmer['full_name']}**"
    )

    st.caption(
        f"Farmer ID: {farmer_id}"
    )

    st.divider()

    # --------------------------------------------------------# NAVIGATION
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
            NAVIGATION
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Produce Batches",
            "Quality Records",
            "Storage",
            "Predictions",
            "Market Listings",
            "Buyer Management",
        ],
        label_visibility="collapsed",
        key="farmer_navigation",
    )

    st.divider()

    # --------------------------------------------------------
    # --------------------------------------------------------
    # LOGOUT BUTTON
    # --------------------------------------------------------

    st.divider()

    if st.button(
        "Logout",
        key="farmer_logout_button",
        use_container_width=True,
        type="primary",
    ):
        logout_user()
        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        st.session_state.pop("farmer_navigation", None)
        st.rerun()

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
            Farmer Management Module
        </div>
        """,
        unsafe_allow_html=True,
    )
# ============================================================
# LOAD SELECTED FARMER DASHBOARD DATA
# ============================================================

dashboard = get_farmer_dashboard(farmer_id)
if dashboard is None:
    st.error(f"Farmer ID {farmer_id} was not found.")
    st.stop()


farmer = dashboard["farmer"]
batch = dashboard["batch"]
quality = dashboard["quality"]
storage = dashboard["storage"]
prediction = dashboard["prediction"]
recommendation = dashboard["recommendation"]

# ============================================================
# TOP HEADER
# ============================================================

col1, col2 = st.columns([5, 1])

with col1:
    st.title("FARMER DASHBOARD")
    st.caption("Smarter Farming | Better Harvests | Secure Food")

with col2:
    st.write("")
    st.markdown("**AGRO LIFE-AI**")

st.divider()
# ============================================================
# PAGE 1 — DASHBOARD
# ============================================================
if page == "Dashboard":

    if batch is None:

        st.subheader("Farmer Dashboard")

        st.info(
            "No produce batch is currently available for this farmer."
        )

        st.write(
            "Please register a produce batch to view "
            "batch details and AI predictions."
        )

    else:

        st.subheader(
            f"Batch #{batch['batch_id']}"
        )

        st.write(
            f"**Produce:** {batch['produce_name']}"
        )

        st.write(
            f"**Quantity:** {batch['quantity_kg']:.2f} KG"
        )

        st.write(
            f"**Harvest Date:** {batch['harvest_date']}"
        )

        st.write(
            f"**Initial Quality:** {batch['initial_quality']}"
        )

    # ============================================================
    # 1. FARMER PROFILE
    # ============================================================

    st.markdown(
    """
    <div class="section-title">
        👤 Farmer Profile
        <div class="section-line"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

    profile_col1, profile_col2, profile_col3 = st.columns(3)

    with profile_col1:
        st.markdown(
            f"""
            <div class="dashboard-card">
                <div class="card-label">FARMER NAME</div>
                <div class="card-value">{farmer["full_name"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with profile_col2:
        st.markdown(
            f"""
            <div class="dashboard-card">
                <div class="card-label">FARMER ID</div>
                <div class="card-value">{farmer["farmer_id"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with profile_col3:
        st.markdown(
            f"""
            <div class="dashboard-card">
                <div class="card-label">LOCATION</div>
                <div class="card-value">
                    {farmer.get("district", "Not recorded")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ============================================================
    # 2. SHELF-LIFE SUMMARY
    # ============================================================

    st.markdown("### Shelf-Life Summary")

    shelf_col1, shelf_col2, shelf_col3 = st.columns(3)

    if prediction:

        total_shelf_life = prediction.get(
            "total_shelf_life_days"
        )

        remaining_shelf_life = prediction.get(
            "remaining_shelf_life_days"
        )

        current_storage_days = prediction.get(
            "current_storage_days"
        )

        with shelf_col1:
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="card-label">REMAINING SHELF LIFE</div>
                    <div class="big-value">
                        {remaining_shelf_life:.2f} days
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with shelf_col2:
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="card-label">TOTAL SHELF LIFE</div>
                    <div class="big-value">
                        {total_shelf_life:.2f} days
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with shelf_col3:
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="card-label">CURRENT STORAGE</div>
                    <div class="big-value">
                        {current_storage_days:.2f} days
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:

        with shelf_col1:
            st.markdown(
                """
                <div class="dashboard-card">
                    <div class="card-label">REMAINING SHELF LIFE</div>
                    <div class="big-value">No prediction</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with shelf_col2:
            st.markdown(
                """
                <div class="dashboard-card">
                    <div class="card-label">TOTAL SHELF LIFE</div>
                    <div class="big-value">Not available</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with shelf_col3:
            st.markdown(
                """
                <div class="dashboard-card">
                    <div class="card-label">CURRENT STORAGE</div>
                    <div class="big-value">Not available</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ============================================================
    # 3. LATEST PRODUCE BATCH
    # ============================================================

    st.markdown("### Latest Produce Batch")

    if batch:

        batch_col1, batch_col2, batch_col3, batch_col4 = st.columns(4)

        with batch_col1:
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="card-label">PRODUCE</div>
                    <div class="card-value">
                        {batch["produce_name"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with batch_col2:
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="card-label">QUANTITY</div>
                    <div class="card-value">
                        {batch["quantity_kg"]:.2f} KG
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with batch_col3:
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="card-label">BATCH ID</div>
                    <div class="card-value">
                        #{batch["batch_id"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with batch_col4:
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="card-label">STATUS</div>
                    <div class="card-value">
                        {batch["status"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:
        st.info("No produce batch has been registered for this farmer.")

    st.markdown("<br>", unsafe_allow_html=True)


    # ============================================================
    # 4. QUALITY AND STORAGE
    # ============================================================

    st.markdown("### Quality & Storage")

    quality_col, storage_col = st.columns(2)

    with quality_col:

        if quality:

            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="card-label">QUALITY RECORD</div>
                    <h3>{quality["visual_status"]}</h3>
                    <p>
                        Quality Score:
                        <strong>{quality["quality_score"]:.1f}/10</strong>
                    </p>
                    <p>
                        CV Confidence:
                        <strong>{quality["cv_confidence"] * 100:.2f}%</strong>
                    </p>
                    <p>
                        Weight Loss:
                        <strong>{quality["weight_loss_percent"]:.2f}%</strong>
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
                <div class="dashboard-card">
                    <div class="card-label">QUALITY RECORD</div>
                    <p>No quality record available.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with storage_col:

        if storage:

            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="card-label">STORAGE CONDITIONS</div>
                    <p>
                        Temperature:
                        <strong>{storage["temperature_c"]:.1f} °C</strong>
                    </p>
                    <p>
                        Humidity:
                        <strong>{storage["humidity_percent"]:.1f}%</strong>
                    </p>
                    <p>
                        Storage Period:
                        <strong>{storage["storage_days"]:.1f} days</strong>
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
                <div class="dashboard-card">
                    <div class="card-label">STORAGE CONDITIONS</div>
                    <p>No storage record available.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ============================================================
    # 5. PREDICTION STATUS
    # ============================================================

    st.markdown("### AI Prediction")

    if prediction:

        prediction_col1, prediction_col2 = st.columns(2)

        with prediction_col1:

            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="card-label">PREDICTION STATUS</div>
                    <div class="card-value">
                        Available
                    </div>
                    <p>
                        Input Method:
                        <strong>{prediction["input_method"]}</strong>
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with prediction_col2:

            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="card-label">PREDICTION NOTE</div>
                    <p>
                        {prediction.get(
                            "confidence_note",
                            "Research prototype prediction."
                        )}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:

        st.info(
            "No shelf-life prediction is currently linked to this farmer's latest batch."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ============================================================
    # 6. AI RECOMMENDATION
    # ============================================================

    st.markdown("### AI Recommendation")

    if recommendation:

        st.markdown(
            f"""
            <div class="dashboard-card">
                <div class="card-label">RECOMMENDATION</div>
                <h3>{recommendation.get("status", "INFORMATION")}</h3>
                <p>
                    {recommendation.get(
                        "recommendation_text",
                        recommendation.get(
                            "recommendation",
                            "No recommendation text available."
                        )
                    )}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.info(
            "No recommendation is currently available for this farmer."
        )
# ============================================================
# PAGE 2 — PRODUCE BATCHES
# ============================================================

elif page == "Produce Batches":

    st.title("Produce Batches")
    st.write("Manage produce batches registered by the selected farmer.")

    # --------------------------------------------------------
    # ADD NEW PRODUCE BATCH
    # --------------------------------------------------------

    st.subheader("Add New Produce Batch")

    produce_list = get_all_produce()

    produce_options = {
        produce["name"]: produce["produce_id"]
        for produce in produce_list
    }

    with st.form("add_produce_batch_form"):

        col1, col2 = st.columns(2)

        with col1:
            produce_name = st.selectbox(
                "Produce",
                list(produce_options.keys())
            )

            quantity_kg = st.number_input(
                "Quantity (KG)",
                min_value=0.1,
                step=1.0
            )

            harvest_date = st.date_input(
                "Harvest Date"
            )

        with col2:
            initial_quality = st.selectbox(
                "Initial Quality",
                [
                    "EXCELLENT",
                    "GOOD",
                    "FAIR",
                    "POOR"
                ]
            )

            asking_price = st.number_input(
                "Asking Price per KG (K)",
                min_value=0.0,
                step=0.50
            )

            status = st.selectbox(
                "Batch Status",
                [
                    "AVAILABLE",
                    "SOLD",
                    "RESERVED",
                    "EXPIRED"
                ]
            )
        st.markdown("---")

        crop_photo = st.file_uploader(
            "Add Photo",
            type=["jpg", "jpeg", "png"],
            help="Upload a photo of the selected produce."
        )
        submitted = st.form_submit_button(
            "Add Produce Batch"
        )

        if submitted:

            try:
                                # ------------------------------------------------
                # SAVE CROP PHOTO
                # ------------------------------------------------

                if crop_photo is not None:

                    project_root = os.path.abspath(
                        os.path.join(
                            os.path.dirname(__file__),
                            "..",
                            ".."
                        )
                    )

                    crops_folder = os.path.join(
                        project_root,
                        "assets",
                        "crops"
                    )

                    os.makedirs(
                        crops_folder,
                        exist_ok=True
                    )

                    crop_filename = (
                        produce_name.lower()
                        .replace(" ", "_")
                        + ".jpg"
                    )

                    crop_path = os.path.join(
                        crops_folder,
                        crop_filename
                    )

                    with open(
                        crop_path,
                        "wb"
                    ) as file:

                        file.write(
                            crop_photo.getbuffer()
                        )

                batch_id = add_produce_batch(
    farmer_id=farmer_id,
    produce_id=produce_options[produce_name],
    quantity_kg=quantity_kg,
    harvest_date=str(harvest_date),
    initial_quality=initial_quality,
    asking_price_per_kg=asking_price,
    status=status
)

                st.success(
                    f"Produce batch #{batch_id} added successfully."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Failed to add produce batch: {e}"
                )

    st.divider()

    # --------------------------------------------------------
    # EXISTING PRODUCE BATCHES
    # --------------------------------------------------------

    st.subheader("Farmer's Produce Batches")

    batches = get_farmer_batches(farmer_id)

    if not batches:

        st.info(
            "No produce batches have been registered for this farmer."
        )

    else:

        for batch in batches:

            with st.container(border=True):

                # ------------------------------------------------
                # BATCH IMAGE + DETAILS
                # ------------------------------------------------

                col1, col2 = st.columns(
                    [1, 3],
                    vertical_alignment="center"
                )

                # ------------------------------------------------
                # CROP IMAGE
                # ------------------------------------------------

                with col1:

                    crop_image = get_crop_image(
                        batch["produce_name"]
                    )

                    if crop_image:

                        st.image(
                            crop_image,
                            width=220
                        )

                    else:

                        st.info("No crop image available.")

                # ------------------------------------------------
                # BATCH DETAILS
                # ------------------------------------------------

                with col2:

                    st.subheader(
                        f"Batch #{batch['batch_id']}"
                    )

                    st.write(
                        f"**Produce:** {batch['produce_name']}"
                    )

                    st.write(
                        f"**Quantity:** {batch['quantity_kg']:.2f} KG"
                    )

                    st.write(
                        f"**Harvest Date:** {batch['harvest_date']}"
                    )

                    st.write(
                        f"**Initial Quality:** {batch['initial_quality']}"
                    )

                    st.write(
                        f"**Price:** K{batch['asking_price_per_kg']:.2f}/KG"
                    )

                    st.write(
                        f"**Current Status:** {batch['status']}"
                    )

                    # ------------------------------------------------
                    # CHANGE STATUS
                    # ------------------------------------------------

                    st.divider()

                    new_status = st.selectbox(
                        "Change Status",
                        [
                            "AVAILABLE",
                            "SOLD",
                            "EXPIRED",
                            "CLOSED"
                        ],
                        index=[
                            "AVAILABLE",
                            "SOLD",
                            "EXPIRED",
                            "CLOSED"
                        ].index(batch["status"])
                        if batch["status"] in [
                            "AVAILABLE",
                            "SOLD",
                            "EXPIRED",
                            "CLOSED"
                        ]
                        else 0,
                        key=f"batch_status_{batch['batch_id']}"
                    )

                    if new_status != batch["status"]:

                        if st.button(
                            "Update Status",
                            key=f"update_batch_{batch['batch_id']}"
                        ):

                            update_batch_status(
                                batch["batch_id"],
                                new_status
                            )

                            st.success(
                                "Batch status updated successfully."
                            )

                            st.rerun()
             # ------------------------------------------------
            # DELETE BATCH
            # ------------------------------------------------

            if st.button(
                "Delete Batch",
                key=f"delete_batch_{batch['batch_id']}"
            ):
                st.session_state[
                    f"confirm_delete_{batch['batch_id']}"
                ] = True

            # ------------------------------------------------
            # DELETE CONFIRMATION
            # ------------------------------------------------

            if st.session_state.get(
                f"confirm_delete_{batch['batch_id']}",
                False
            ):

                st.warning(
                    f"Are you sure you want to permanently "
                    f"delete Batch #{batch['batch_id']}?"
                )

                confirm_col, cancel_col = st.columns(2)

                with confirm_col:

                    if st.button(
                        "Confirm Delete",
                        key=f"confirm_delete_button_{batch['batch_id']}"
                    ):

                        deleted = delete_produce_batch(
                            batch["batch_id"]
                        )

                        if deleted:

                            st.session_state[
                                f"confirm_delete_{batch['batch_id']}"
                            ] = False

                            st.success(
                                f"Batch #{batch['batch_id']} "
                                f"deleted successfully."
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Batch could not be deleted."
                            )

                with cancel_col:

                    if st.button(
                        "Cancel",
                        key=f"cancel_delete_{batch['batch_id']}"
                    ):

                        st.session_state[
                            f"confirm_delete_{batch['batch_id']}"
                        ] = False

                        st.rerun()           
# ============================================================
# PAGE 3 — QUALITY RECORDS
# ============================================================

elif page == "Quality Records":

    st.title("Quality Records")
    st.write(
        "View and record quality information for the selected farmer's produce batches."
    )

    # --------------------------------------------------------
    # SELECT BATCH
    # --------------------------------------------------------

    batches = get_farmer_batches(farmer_id)

    if not batches:

        st.info(
            "No produce batches are available for this farmer."
        )

    else:

        batch_options = {
            f"Batch #{batch['batch_id']} - {batch['produce_name']} "
            f"({batch['quantity_kg']:.2f} KG)": batch["batch_id"]
            for batch in batches
        }

        selected_batch_label = st.selectbox(
            "Select Produce Batch",
            list(batch_options.keys()),
            key="quality_batch_select"
        )

        selected_batch_id = batch_options[selected_batch_label]

        st.divider()

        # ----------------------------------------------------
        # ADD QUALITY RECORD
        # ----------------------------------------------------

        st.subheader("Add Quality Record")

        with st.form("add_quality_record_form"):

            col1, col2 = st.columns(2)

            with col1:

                quality_score = st.number_input(
                    "Quality Score (0–10)",
                    min_value=0.0,
                    max_value=10.0,
                    value=8.5,
                    step=0.1
                )

                visual_status = st.selectbox(
                    "Visual Status",
                    [
                        "Fresh",
                        "Good",
                        "Fair",
                        "Poor",
                        "Rotten"
                    ]
                )

            with col2:

                cv_confidence = st.number_input(
                    "Computer Vision Confidence (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=92.61,
                    step=0.01
                )

                weight_loss_percent = st.number_input(
                    "Weight Loss (%)",
                    min_value=0.0,
                    value=4.0,
                    step=0.01
                )

            save_quality = st.form_submit_button(
                "Save Quality Record"
            )

            if save_quality:

                try:

                    quality_id = add_quality_record(
                        batch_id=selected_batch_id,
                        quality_score=quality_score,
                        visual_status=visual_status,
                        cv_confidence=cv_confidence / 100,
                        weight_loss_percent=weight_loss_percent,
                    )

                    st.success(
                        f"Quality record #{quality_id} saved successfully."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Failed to save quality record: {e}"
                    )

        st.divider()

        # ----------------------------------------------------
        # EXISTING QUALITY RECORDS
        # ----------------------------------------------------

        st.subheader("Quality History")

        quality_records = get_batch_quality_records(
            selected_batch_id
        )

        if not quality_records:

            st.info(
                "No quality records have been recorded for this batch."
            )

        else:

            for record in reversed(quality_records):

                with st.container(border=True):

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.write(
                            f"**Quality Record:** #{record['quality_id']}"
                        )

                        st.write(
                            f"**Quality Score:** "
                            f"{record['quality_score']:.1f}/10"
                        )

                    with col2:

                        st.write(
                            f"**Visual Status:** "
                            f"{record['visual_status']}"
                        )

                        st.write(
                            f"**CV Confidence:** "
                            f"{record['cv_confidence'] * 100:.2f}%"
                        )

                    with col3:

                        st.write(
                            f"**Weight Loss:** "
                            f"{record['weight_loss_percent']:.2f}%"
                        )

                        st.write(
                            f"**Recorded:** "
                            f"{record['recorded_at']}"
                        )

# ============================================================
# PAGE 4 — STORAGE
# ============================================================

elif page == "Storage":

    st.title("Storage Management")
    st.write(
        "Monitor storage conditions for the selected farmer's produce batches."
    )

    # --------------------------------------------------------
    # SELECT BATCH
    # --------------------------------------------------------

    batches = get_farmer_batches(farmer_id)

    if not batches:

        st.info(
            "No produce batches are available for this farmer."
        )

    else:

        batch_options = {
            f"Batch #{batch['batch_id']} - {batch['produce_name']} "
            f"({batch['quantity_kg']:.2f} KG)": batch["batch_id"]
            for batch in batches
        }

        selected_batch_label = st.selectbox(
            "Select Produce Batch",
            list(batch_options.keys()),
            key="storage_batch_select"
        )

        selected_batch_id = batch_options[selected_batch_label]

        st.divider()

        # ----------------------------------------------------
        # ADD STORAGE RECORD
        # ----------------------------------------------------

        st.subheader("Add Storage Record")

        with st.form("add_storage_record_form"):

            col1, col2, col3 = st.columns(3)

            with col1:

                temperature_c = st.number_input(
                    "Temperature (°C)",
                    min_value=-20.0,
                    max_value=60.0,
                    value=28.0,
                    step=0.1
                )

            with col2:

                humidity_percent = st.number_input(
                    "Humidity (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=78.0,
                    step=0.1
                )

            with col3:

                storage_days = st.number_input(
                    "Storage Days",
                    min_value=0.0,
                    value=2.0,
                    step=0.5
                )

            save_storage = st.form_submit_button(
                "Save Storage Record"
            )

            if save_storage:

                try:

                    storage_id = add_storage_record(
                        batch_id=selected_batch_id,
                        temperature_c=temperature_c,
                        humidity_percent=humidity_percent,
                        storage_days=storage_days,
                    )

                    st.success(
                        f"Storage record #{storage_id} saved successfully."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Failed to save storage record: {e}"
                    )

        st.divider()

        # ----------------------------------------------------
        # STORAGE HISTORY
        # ----------------------------------------------------

        st.subheader("Storage History")

        storage_records = get_batch_storage_records(
            selected_batch_id
        )

        if not storage_records:

            st.info(
                "No storage records have been recorded for this batch."
            )

        else:

            for record in reversed(storage_records):

                with st.container(border=True):

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.write(
                            f"**Storage Record:** "
                            f"#{record['storage_id']}"
                        )

                        st.write(
                            f"**Temperature:** "
                            f"{record['temperature_c']:.1f} °C"
                        )

                    with col2:

                        st.write(
                            f"**Humidity:** "
                            f"{record['humidity_percent']:.1f}%"
                        )

                        st.write(
                            f"**Storage Days:** "
                            f"{record['storage_days']:.2f}"
                        )

                    with col3:

                        st.write(
                            f"**Recorded:** "
                            f"{record['recorded_at']}"
                        )

# ============================================================
# PAGE 5 — PREDICTIONS
# ============================================================

elif page == "Predictions":

    st.title("AI Shelf-Life Predictions")

    st.write(
        "Generate and view research-based shelf-life predictions "
        "for the selected farmer's produce batches."
    )

    # --------------------------------------------------------
    # SELECT BATCH
    # --------------------------------------------------------

    batches = get_farmer_batches(farmer_id)

    if not batches:

        st.info(
            "No produce batches are available for this farmer."
        )

    else:

        batch_options = {
            f"Batch #{batch['batch_id']} - "
            f"{batch['produce_name']} "
            f"({batch['quantity_kg']:.2f} KG)": batch["batch_id"]
            for batch in batches
        }

        selected_batch_label = st.selectbox(
            "Select Produce Batch",
            list(batch_options.keys()),
            key="prediction_batch_select"
        )

        selected_batch_id = batch_options[selected_batch_label]

        selected_batch = next(
            batch
            for batch in batches
            if batch["batch_id"] == selected_batch_id
        )

        st.divider()

        # ----------------------------------------------------
        # CHECK EXISTING PREDICTION
        # ----------------------------------------------------

        batch_predictions = get_batch_predictions(
            selected_batch_id,
            farmer_id
        )

        latest_prediction = (
            batch_predictions[0]
            if batch_predictions
            else None
        )

        # ----------------------------------------------------
        # EXISTING PREDICTION
        # ----------------------------------------------------

        if latest_prediction:

            st.subheader("Latest Shelf-Life Prediction")

            st.write(
                f"**Produce:** "
                f"{latest_prediction['produce_name']}"
            )

            st.write(
                f"**Batch:** "
                f"#{latest_prediction['batch_id']}"
            )

            st.write(
                f"**Prediction Date:** "
                f"{latest_prediction['prediction_date']}"
            )

            st.divider()

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Total Shelf Life",
                    f"{latest_prediction['total_shelf_life_days']:.2f} days"
                )

            with col2:

                st.metric(
                    "Current Storage",
                    f"{latest_prediction['current_storage_days']:.2f} days"
                )

            with col3:

                st.metric(
                    "Remaining Shelf Life",
                    f"{latest_prediction['remaining_shelf_life_days']:.2f} days"
                )

            st.write(
                f"**Input Method:** "
                f"{latest_prediction['input_method']}"
            )

            st.write(
                f"**Prediction ID:** "
                f"#{latest_prediction['prediction_id']}"
            )

            if latest_prediction["confidence_note"]:

                st.info(
                    latest_prediction["confidence_note"]
                )

            st.success(
                "An existing prediction is already available "
                "for this batch."
            )

            st.divider()

        # ------------------------------------------------
        # PREDICTION HISTORY FOR THIS BATCH
        # ------------------------------------------------

        if len(batch_predictions) > 1:

            st.subheader("Previous Predictions")

            for prediction in batch_predictions[1:]:

                with st.expander(
                    f"Prediction #{prediction['prediction_id']} "
                    f"- {prediction['prediction_date']}"
                ):

                    st.write(
                        f"Total Shelf Life: "
                        f"{prediction['total_shelf_life_days']:.2f} days"
                    )

                    st.write(
                        f"Current Storage: "
                        f"{prediction['current_storage_days']:.2f} days"
                    )

                    st.write(
                        f"Remaining Shelf Life: "
                        f"{prediction['remaining_shelf_life_days']:.2f} days"
                    )

        # ------------------------------------------------
        # RESEARCH METHOD INFORMATION
        # ------------------------------------------------

        st.subheader("Research Prediction Method")

        st.write(
            "This prototype uses Day-4 biochemical measurements "
            "from the selected produce batch."
        )

        st.write(
            "**Research inputs:** Day-4 weight loss (%) and "
            "Day-4 titratable acidity."
        )

        st.warning(
            "This is a research prototype estimate. "
            "It is not a food-safety certification."
        )

        # ------------------------------------------------
        # CHECK DAY-4 RESEARCH DATA
        # ------------------------------------------------

        research_records = get_batch_research_measurements(
            selected_batch_id
        )

        day4_records = [
            record
            for record in research_records
            if int(record["day_number"]) == 4
        ]

               # ------------------------------------------------
        # NO EXISTING PREDICTION
        # ------------------------------------------------

        if not batch_predictions:

            st.subheader("Generate Shelf-Life Prediction")

            st.write(
                f"**Produce:** "
                f"{selected_batch['produce_name']}"
            )

            st.write(
                f"**Batch:** "
                f"#{selected_batch['batch_id']}"
            )

            st.info(
                "No shelf-life prediction exists for this batch yet."
            )

            # ------------------------------------------------
            # DAY-4 RESEARCH DATA AVAILABLE
            # ------------------------------------------------

            if day4_records:

                latest_day4 = day4_records[-1]

                st.success(
                    "Day-4 research measurements are available "
                    "for this batch."
                )

                st.write(
                    f"**Day-4 Weight Loss:** "
                    f"{float(latest_day4['weight_loss_percent']):.2f}%"
                )

                st.write(
                    f"**Day-4 Titratable Acidity:** "
                    f"{float(latest_day4['titratable_acidity']):.2f}"
                )

                st.info(
                    "The AI prediction will use the Day-4 biochemical "
                    "research measurements recorded for this batch."
                )

                if st.button(
                    "Run AI Shelf-Life Prediction",
                    type="primary"
                ):

                    try:

                        result = run_farmer_batch_prediction_workflow(
                            farmer_id=farmer_id,
                            batch_id=selected_batch_id,
                            input_method="research",
                        )

                        st.success(
                            "Shelf-life prediction generated successfully."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Prediction could not be generated: {e}"
                        )

            # ------------------------------------------------
            # DAY-4 RESEARCH DATA NOT AVAILABLE
            # ------------------------------------------------

            else:

                st.warning(
                    "Day-4 Research Data Required"
                )

                st.write(
                    "This research-based shelf-life prediction "
                    "requires Day-4 biochemical measurements for "
                    "the selected batch."
                )

                st.write(
                    "**Required research inputs:**"
                )

                st.write(
                    "• Day-4 Weight Loss (%)"
                )

                st.write(
                    "• Day-4 Titratable Acidity"
                )

                st.info(
                    "Record the Day-4 research measurements for this "
                    "batch, then return here to run the AI "
                    "shelf-life prediction."
                )
# ============================================================
# PAGE 6 — MARKET LISTINGS
# ============================================================

elif page == "Market Listings":

    st.title("Market Listings")
    st.write(
        "Create and manage produce listings for the selected farmer."
    )

    # --------------------------------------------------------
    # SELECT BATCH
    # --------------------------------------------------------

    batches = get_farmer_batches(farmer_id)

    if not batches:

        st.info(
            "No produce batches are available for this farmer."
        )

    else:

        batch_options = {
            f"Batch #{batch['batch_id']} - {batch['produce_name']} "
            f"({batch['quantity_kg']:.2f} KG)": batch["batch_id"]
            for batch in batches
        }

        selected_batch_label = st.selectbox(
            "Select Produce Batch",
            list(batch_options.keys()),
            key="market_batch_select"
        )

        selected_batch_id = batch_options[selected_batch_label]

        selected_batch = next(
            batch
            for batch in batches
            if batch["batch_id"] == selected_batch_id
        )

        st.divider()

        # ----------------------------------------------------
        # CREATE MARKET LISTING
        # ----------------------------------------------------

        st.subheader("Create Market Listing")

        with st.form("create_market_listing_form"):

            col1, col2 = st.columns(2)

            with col1:

                listing_quantity = st.number_input(
                    "Quantity for Sale (KG)",
                    min_value=0.1,
                    max_value=float(selected_batch["quantity_kg"]),
                    value=min(
                        200.0,
                        float(selected_batch["quantity_kg"])
                    ),
                    step=1.0
                )

                price_per_kg = st.number_input(
                    "Price per KG (K)",
                    min_value=0.0,
                    value=float(
                        selected_batch["asking_price_per_kg"]
                    ),
                    step=0.50
                )

            with col2:

                listing_quality = st.selectbox(
                    "Quality",
                    [
                        "FRESH",
                        "GOOD",
                        "FAIR",
                        "POOR"
                    ]
                )

                listing_status = st.selectbox(
                    "Listing Status",
                    [
                        "AVAILABLE",
                        "SOLD",
                        "RESERVED",
                        "EXPIRED"
                    ]
                )

            create_listing = st.form_submit_button(
                "Create Market Listing"
            )

            if create_listing:

                try:

                    listing_id = add_market_listing(
                        farmer_id=farmer_id,
                        batch_id=selected_batch_id,
                        produce_name=selected_batch["produce_name"],
                        quantity_kg=listing_quantity,
                        price_per_kg=price_per_kg,
                        quality=listing_quality,
                        status=listing_status,
                    )

                    st.success(
                        f"Market listing #{listing_id} created successfully."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Failed to create market listing: {e}"
                    )

        st.divider()

        # ----------------------------------------------------
        # EXISTING MARKET LISTINGS
        # ----------------------------------------------------

        st.subheader("Market Listings")

        listings = get_farmer_market_listings(farmer_id)

        if not listings:

            st.info(
                "No market listings have been created for this farmer."
            )

        else:

            for listing in listings:

                with st.container(border=True):

                    st.markdown(
                        f"### Listing #{listing['listing_id']}"
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.markdown(
                            f"**Produce:** "
                            f"{listing['produce_name']}"
                        )

                        st.markdown(
                            f"**Quantity Available:** "
                            f"{listing['quantity_available_kg']:.2f} KG"
                        )

                    with col2:

                        st.markdown(
                            f"**Price:** "
                            f"K{listing['price_per_kg']:.2f} / KG"
                        )

                        st.markdown(
                            f"**Quality:** "
                            f"{listing['quality_status']}"
                        )

                    with col3:

                        st.markdown(
                            f"**Status:** "
                            f"{listing['listing_status']}"
                        )

                    st.divider()

                    # ------------------------------------------------
                    # ASSIGNED BUYER
                    # ------------------------------------------------

                    if listing["buyer_id"]:

                        st.markdown("#### Assigned Buyer")

                        buyer_col1, buyer_col2, buyer_col3 = st.columns(3)

                        with buyer_col1:

                            st.markdown(
                                f"**Buyer:** "
                                f"{listing['buyer_name']}"
                            )

                        with buyer_col2:

                            st.markdown(
                                f"**Buyer Type:** "
                                f"{listing['buyer_type']}"
                            )

                        with buyer_col3:

                            location = (
                                listing["buyer_location"]
                                or "Location not provided"
                            )

                            st.markdown(
                                f"**Location:** "
                                f"{location}"
                            )

                    else:

                        st.info(
                            "No buyer has been assigned to this listing."
                        )

# ============================================================
# PAGE 7 — BUYER MANAGEMENT
# ============================================================

elif page == "Buyer Management":

    st.title("Buyer Management")
    st.write(
        "Register buyers and manage buyer assignments for farmer market listings."
    )

    # --------------------------------------------------------
    # ADD NEW BUYER
    # --------------------------------------------------------

    st.subheader("Register New Buyer")

    with st.form("add_buyer_form"):

        col1, col2 = st.columns(2)

        with col1:

            buyer_name = st.text_input(
                "Buyer Name"
            )

            buyer_type = st.selectbox(
                "Buyer Type",
                [
                    "INDIVIDUAL",
                    "WHOLESALER",
                    "RETAILER",
                    "PROCESSOR",
                    "SUPERMARKET",
                    "OTHER"
                ]
            )

        with col2:

            buyer_phone = st.text_input(
                "Phone Number"
            )

            buyer_location = st.text_input(
                "Location"
            )

        add_buyer_button = st.form_submit_button(
            "Register Buyer"
        )

        if add_buyer_button:

            if not buyer_name.strip():

                st.error(
                    "Buyer name is required."
                )

            else:

                try:

                    buyer_id = add_buyer(
                        buyer_name=buyer_name.strip(),
                        buyer_type=buyer_type,
                        phone=buyer_phone.strip(),
                        location=buyer_location.strip(),
                    )

                    st.success(
                        f"Buyer #{buyer_id} registered successfully."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Failed to register buyer: {e}"
                    )

    st.divider()

    # --------------------------------------------------------
    # REGISTERED BUYERS
    # --------------------------------------------------------

    st.subheader("Registered Buyers")

    buyers = get_all_buyers()

    if not buyers:

        st.info(
            "No buyers have been registered yet."
        )

    else:

        for buyer in buyers:

            with st.container(border=True):

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.write(
                        f"**Buyer ID:** #{buyer['buyer_id']}"
                    )

                    st.write(
                        f"**Name:** {buyer['full_name']}"
                    )

                with col2:

                    st.write(
                        f"**Type:** {buyer['buyer_type']}"
                    )

                    st.write(
                        f"**Phone:** "
                        f"{buyer['phone'] or 'Not provided'}"
                    )

                with col3:

                    st.write(
                        f"**Location:** "
                        f"{buyer['buyer_location'] or 'Not provided'}"
                    )

    st.divider()

    # --------------------------------------------------------
    # ASSIGN BUYER TO MARKET LISTING
    # --------------------------------------------------------

    st.subheader("Assign Buyer to Market Listing")

    listings = get_farmer_market_listings(
        farmer_id
    )

    if not listings:

        st.info(
            "No market listings are available for buyer assignment."
        )

    elif not buyers:

        st.info(
            "Register at least one buyer before assigning a buyer."
        )

    else:

        listing_options = {
            f"Listing #{listing['listing_id']} - "
            f"{listing['produce_name']} - "
            f"{listing['quantity_available_kg']:.2f} KG":
            listing["listing_id"]
            for listing in listings
        }

        buyer_options = {
            f"Buyer #{buyer['buyer_id']} - "
            f"{buyer['full_name']} - "
            f"{buyer['buyer_type']} - "
            f"{buyer['buyer_location'] or 'Location not provided'}":
            buyer["buyer_id"]
            for buyer in buyers
        }

        selected_listing = st.selectbox(
            "Select Market Listing",
            list(listing_options.keys()),
            key="buyer_listing_select"
        )

        selected_buyer = st.selectbox(
            "Select Buyer",
            list(buyer_options.keys()),
            key="buyer_select"
        )

        if st.button(
            "Assign Buyer",
            type="primary"
        ):

            try:

                assign_buyer_to_market_listing(
                    listing_id=listing_options[selected_listing],
                    buyer_id=buyer_options[selected_buyer]
                )

                st.success(
                    "Buyer assigned to the market listing successfully."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Failed to assign buyer: {e}"
                )        
