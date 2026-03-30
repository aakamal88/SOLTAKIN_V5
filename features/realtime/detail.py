import streamlit as st
import json
import os
from streamlit_autorefresh import st_autorefresh

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SETTINGS_FILE = os.path.join(ROOT_DIR, "config", "settings.json")


# =========================
# LOAD
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
        "series": c.get("series", 100),
        "voltage": c.get("voltage", 1.42)
    }


def normalize(v, s, default):
    if not v:
        return [default] * s
    v = list(v)
    if len(v) < s:
        v += [default] * (s - len(v))
    return v[:s]


# =========================
# UI CARD PER CELL (WITH STYLE)
# =========================
def render_cell_card(cell_no, volt, temp, liquid, is_active):

    key = f"C{cell_no}"

    # 🎨 Style logic
    if is_active:
        bg = "#F5F5F5"
        header_bg = "#E0E0E0"
        text_color = "black"
        v = f"{volt:.2f}"
        t = f"{temp:.1f}"
        l = f"{liquid:.1f}"
    else:
        bg = "#2B2B2B"
        header_bg = "#1F1F1F"
        text_color = "#AAAAAA"
        v = t = l = "N/A"

    # 🧱 CARD START
    st.markdown(f"""
    <div style="
        background:{bg};
        border-radius:12px;
        padding:0;
        margin-bottom:12px;
        overflow:hidden;
        border:1px solid #ddd;
    ">
    """, unsafe_allow_html=True)

    # 🔋 HEADER BADGE (INSIDE CARD)
    st.markdown(f"""
    <div style="
        background:{header_bg};
        padding:8px 12px;
        font-weight:bold;
        color:{text_color};
        border-bottom:1px solid #ccc;
    ">
        🔋 Cell {key}
    </div>
    """, unsafe_allow_html=True)

    # 📊 CONTENT
    st.markdown("<div style='padding:10px;'>", unsafe_allow_html=True)

    def row(label, value, unit):
        c1, c2, c3 = st.columns([2,1,1])
        c1.write(label)
        c2.write(f"**{value}**")
        c3.write(unit)

    row("Voltage", v, "Vdc")
    row("Temp", t, "°C")
    row("Level", l, "%")

    st.markdown("</div>", unsafe_allow_html=True)

    # 🧱 CARD END
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# MAIN
# =========================
def render_detail():

    st_autorefresh(interval=60000, key="refresh")

    data = get_data()
    cfg = get_config()

    series = cfg["series"]   # ✅ dynamic dari settings.json
    max_cells = 100          # total UI

    voltages = normalize(data["cell_voltage"], max_cells, cfg["voltage"])
    temps = normalize(data["cell_temperature"], max_cells, 30)
    liquids = normalize(data["cell_liquid"], max_cells, 80)

    st.title(f"🔋 Cells Realtime Monitoring ({series} Active Cells)")

    cols_per_row = 5
    rows = (max_cells + cols_per_row - 1) // cols_per_row

    idx = 0
    for r in range(rows):
        cols = st.columns(cols_per_row)

        for c in range(cols_per_row):
            if idx < max_cells:

                is_active = idx < series  # 🎯 logic utama

                with cols[c]:
                    render_cell_card(
                        idx + 1,
                        voltages[idx],
                        temps[idx],
                        liquids[idx],
                        is_active
                    )
                    st.markdown("---")

                idx += 1


# =========================
# RUN
# =========================
render_detail()