import streamlit as st
from streamlit_autorefresh import st_autorefresh

from .dashboard_settings import get_data, get_config
from .dashboard_map import render_map
from .dashboard_ups import render_ups
from .dashboard_system import render_system
from .dashboard_cells import render_cells

def render_dashboard():
    st.set_page_config(layout="wide")
    st_autorefresh(interval=60000, key="dashboard_refresh")

    data = get_data()
    cfg = get_config()

    st.title("📊 Dashboard")

    render_map(data)
    render_ups(data, cfg)
    render_system(data)
    render_cells(cfg, data)