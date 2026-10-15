import sys
from pathlib import Path

import streamlit as st


# ---------------------------------------------------------
# Add project root to Python path
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------
# Import database function
# ---------------------------------------------------------
try:
    from database.database_manager import get_farmer_dashboard  # type: ignore[import-not-found]
except ModuleNotFoundError:
    # Fallback for launchers that do not add the project root to PYTHONPATH.
    from importlib.util import module_from_spec, spec_from_file_location

    db_path = PROJECT_ROOT / "database" / "database_manager.py"
    spec = spec_from_file_location("database_manager", db_path)

    if spec is None or spec.loader is None:
        raise

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    get_farmer_dashboard = module.get_farmer_dashboard


# ---------------------------------------------------------
# Streamlit configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="AGRO LIFE-AI",
    page_icon="A",
    layout="wide",
)


# ---------------------------------------------------------
# Dashboard title
# ---------------------------------------------------------
st.title("AGRO LIFE-AI")
st.header("Farmer Dashboard")

st.write("Testing connection to the AGRO LIFE-AI database...")


# ---------------------------------------------------------
# Test Farmer
# ---------------------------------------------------------
farmer_id = 16

dashboard = get_farmer_dashboard(farmer_id)


# ---------------------------------------------------------
# Check database result
# ---------------------------------------------------------
if dashboard is None:
    st.error(f"Farmer ID {farmer_id} was not found.")
    st.stop()


# ---------------------------------------------------------
# Farmer information
# ---------------------------------------------------------
farmer = dashboard["farmer"]

st.success("Database connection successful!")

st.subheader("Farmer Information")

st.write(f"**Farmer:** {farmer['full_name']}")
st.write(f"**Farm:** {farmer['farm_name']}")
st.write(f"**Location:** {farmer['farm_location']}")
st.write(f"**District:** {farmer['district']}")
st.write(f"**Province:** {farmer['province']}")