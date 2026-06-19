import streamlit as st
import os
import sys

# Add current directory to path just in case
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.ui_components import inject_custom_css

# Set page configuration at the very entrypoint
# Must be the first streamlit call
st.set_page_config(
    page_title="SafeHer: Women's Safety Analytics Platform",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global custom styles
inject_custom_css()

# Define navigation structure with sections
pages = {
    "Overview": [
        st.Page("pages/1_Home.py", title="Home Dashboard", icon="", default=True)
    ],
    "Safety Analytics": [
        st.Page("pages/2_District_Analysis.py", title="District Analysis", icon=""),
        st.Page("pages/3_Compare_Cities.py", title="Compare Cities", icon=""),
        st.Page("pages/4_Time_Travel.py", title="Time Travel Analysis", icon="⏳")
    ],
    "Machine Learning": [
        st.Page("pages/5_Hotspot_Detection.py", title="Hotspot Detection", icon=""),
        st.Page("pages/6_Geospatial_Heatmaps.py", title="Geo-Spatial Heatmaps", icon=""),
        st.Page("pages/7_Interactive_Rankings.py", title="Interactive Rankings", icon="")
    ],
    "Resources & Info": [
        st.Page("pages/8_Public_Awareness.py", title="Public Awareness", icon="")
    ]
}

# Setup navigation menu
pg = st.navigation(pages)

# Sidebar Status Indicators for Datasets
with st.sidebar:
    st.markdown("---")
    st.markdown("### Dataset Status")
    st.markdown(" `state_master.csv` loaded")
    st.markdown(" `city_stats.csv` loaded")
    st.markdown(" `coordinates.csv` loaded")
    st.markdown(" `india_district.geojson` loaded")

# Render selected page
pg.run()
