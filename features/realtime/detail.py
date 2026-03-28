import streamlit as st
import plotly.graph_objects as go
import json
import os
import streamlit as st
from streamlit_autorefresh import st_autorefresh

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SETTINGS_FILE = os.path.join(ROOT_DIR, "config", "settings.json")

# =========================
# SETTINGS
# =========================
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

# =========================
# DATA
# =========================
def get_data():
    d = load_settings().get("data", {})
    return {
        "cell_voltage": d.get("cell_voltage", []),
        "cell_temperature": d.get("cell_temperature", []),
        "cell_liquid": d.get("cell_liquid", []),
    }

def get_config():
    c = load_settings().get("battery_config", {})
    return {
        "series": c.get("series", 10),
        "voltage": c.get("voltage", 1.42)
    }

# =========================
# HELPER
# =========================
def normalize(v, s, default):
    if not v:
        return [default] * s
    v = list(v)
    if len(v) < s:
        v += [default] * (s - len(v))
    return v[:s]

def voltage_color(v):
    if v < 1.1: return "red"
    elif v < 1.2: return "orange"
    elif v < 1.35: return "yellow"
    elif v < 1.42: return "green"
    else: return "blue"

# =========================
# MAIN
# =========================
def render_detail():

    st_autorefresh(interval=500, key="detail_refresh")  # 5 detik
    data = get_data()
    cfg = get_config()

    series = cfg["series"]

    voltages = normalize(data["cell_voltage"], series, cfg["voltage"])
    temps = normalize(data["cell_temperature"], series, 30)
    liquids = normalize(data["cell_liquid"], series, 80)

    st.title("🔍 Detail Monitoring")

    # =========================
    # BACK BUTTON
    # =========================
    st.link_button("⬅️ Back to Dashboard", "http://localhost:8501")

    # =========================
    # VOLTAGE
    # =========================
    st.markdown("---")
    st.subheader("🔋 Cell Voltage Monitoring")

    st.plotly_chart(
        go.Figure(data=[go.Bar(
            x=[f"C{i+1}" for i in range(len(voltages))],
            y=voltages,
            marker_color=[voltage_color(v) for v in voltages]
        )]),
        use_container_width=True,
        key=f"cell_voltage_{len(voltages)}"
    )

    # =========================
    # TEMPERATURE
    # =========================
    st.subheader("🌡 Cell Temperature Monitoring")

    st.plotly_chart(
        go.Figure(data=[go.Scatter(
            x=[f"C{i+1}" for i in range(len(temps))],
            y=temps,
            mode="lines+markers"
        )]),
        use_container_width=True,
        key=f"cell_temp_{len(temps)}"
    )

    # =========================
    # LIQUID
    # =========================
    st.subheader("🧪 Cell Liquid Level Monitoring")

    st.plotly_chart(
        go.Figure(data=[go.Bar(
            x=[f"C{i+1}" for i in range(len(liquids))],
            y=liquids
        )]),
        use_container_width=True,
        key=f"cell_liquid_{len(liquids)}"
    )

render_detail()
