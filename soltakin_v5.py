import streamlit as st
import json
import os
from datetime import datetime
#from streamlit_autorefresh import st_autorefresh

# =========================
# BASE PATH (FIXED)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================
# IMPORT (UPDATED STRUCTURE)
# =========================
from features.dashboard.dashboard import render_dashboard
from features.advanced.analyze import render_analyze
from features.settings.battery_settings import render_battery_settings
from features.realtime.detail import render_detail
from features.settings.systems import render_system_settings
from features.alarm.notification import render_notification

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="BMS App", layout="wide")

# 🔥 AUTO REFRESH (OPTIMIZED)
#st_autorefresh(interval=5000, key="system_clock")

# =========================
# FILE PATH CONFIG
# =========================
SETTINGS_FILE = os.path.join(BASE_DIR, "config", "settings.json")
LOCATION_FILE = os.path.join(BASE_DIR, "config", "ptg_location.json")
LOGO_MAIN = os.path.join(BASE_DIR, "assets", "pertagas_logo.png")
LOGO_SIDEBAR = os.path.join(BASE_DIR, "assets", "soltakin_logo.png")

# =========================
# LOAD LOCATION HEADER
# =========================
def load_location_header():
    default_area = "Head Office Jakarta"
    default_station = "Infrastructure Management"
    default_lat = "-"
    default_lon = "-"

    try:
        if os.path.exists(LOCATION_FILE):
            with open(LOCATION_FILE, "r") as f:
                data = json.load(f)
                return (
                    data.get("area", default_area),
                    data.get("station", default_station),
                    data.get("lat", default_lat),
                    data.get("lon", default_lon)
                )
    except:
        pass

    return default_area, default_station, default_lat, default_lon


# =========================
# SYSTEM TIME
# =========================
def get_system_time():
    now = datetime.now()
    return now.strftime("%d-%m-%Y"), now.strftime("%H:%M:%S")


area, station, lat, lon = load_location_header()

# =========================
# HEADER
# =========================
col1, col2 = st.columns([1, 1])

with col1:
    if os.path.exists(LOGO_MAIN):
        st.image(LOGO_MAIN, width=280)

    st.markdown(
        f"""
        <div style='text-align:left'>
            <div style='font-size:32px; font-weight:600;'>
                BATTERY INTEGRITY MANAGEMENT SYSTEM
            </div>
            <div style='font-size:28px; font-weight:600; color:#6b7280;'>
                {area}
            </div>
            <div style='font-size:28px; color:#374151;'>
                Station : {station}
            </div>
            <div style='font-size:18px; color:#6b7280;'>
                COORDINATE : {lat}, {lon}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# =========================
# STYLE
# =========================
st.markdown("""
<style>
div.stButton > button {
    background: none;
    border: none;
    text-align: left;
    padding: 5px 8px;
    font-size: 14px;
}
div.stButton > button:hover {
    background-color: #e5e7eb;
    border-radius: 5px;
}
.submenu {
    margin-left: 15px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD SETTINGS
# =========================
def load_settings_safe():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                content = f.read().strip()
                return json.loads(content) if content else {}
        except:
            return {}
    return {}

settings = load_settings_safe()

if "battery_config" in settings:
    st.session_state.battery_config = settings["battery_config"]

if "data" in settings:
    st.session_state.data = settings["data"]

# =========================
# STATE
# =========================
if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"

if "expand" not in st.session_state:
    st.session_state.expand = {
        "realtime": True,
        "graph": False,
        "data": False,
        "settings": True,
        "advanced": True
    }

def set_menu(name):
    st.session_state.menu = name

def toggle(section):
    st.session_state.expand[section] = not st.session_state.expand[section]

# =========================
# SIDEBAR
# =========================
if os.path.exists(LOGO_SIDEBAR):
    st.sidebar.image(LOGO_SIDEBAR, width='stretch')

tanggal, jam = get_system_time()

st.sidebar.markdown(
    f"""
    <div style='text-align:center; padding-top:10px'>
        <div style='font-size:22px; font-weight:600; color:#111827;'>
            Station : {station}
        </div>
        <div style='font-size:12px; color:#6b7280;'>
            Coordinate : {lat}, {lon}
        </div>
        <div style='margin-top:10px; font-size:14px; color:#374151;'>
            📅 {tanggal}
        </div>
        <div style='font-size:18px; font-weight:600; color:#111827;'>
            ⏱️ {jam}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Menu")

# =========================
# MENU
# =========================
if st.sidebar.button("📊 Dashboard"):
    set_menu("Dashboard")

if st.sidebar.button("🚨 Alarm Status"):
    set_menu("Alarm Status")

if st.sidebar.button("📑 Reports"):
    set_menu("Reports")

if st.sidebar.button("▼ Real-Time" if st.session_state.expand["realtime"] else "▶ Real-Time"):
    toggle("realtime")

if st.session_state.expand["realtime"]:
    st.sidebar.markdown('<div class="submenu">', unsafe_allow_html=True)

    if st.sidebar.button("📄 Summary"):
        set_menu("Realtime Summary")

    if st.sidebar.button("🖥️ Detail"):
        set_menu("Realtime Detail")

    if st.sidebar.button("🚨 Alarms"):
        set_menu("Realtime Alarms")

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

if st.sidebar.button("▼ Graph By" if st.session_state.expand["graph"] else "▶ Graph By"):
    toggle("graph")

if st.session_state.expand["graph"]:
    st.sidebar.markdown('<div class="submenu">', unsafe_allow_html=True)

    if st.sidebar.button("📊 Event"):
        set_menu("Graph Event")

    if st.sidebar.button("📈 Trend"):
        set_menu("Graph Trend")

    if st.sidebar.button("📅 Day"):
        set_menu("Graph Day")

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

if st.sidebar.button("▼ Data Transfer" if st.session_state.expand["data"] else "▶ Data Transfer"):
    toggle("data")
    if st.session_state.expand["data"]:
        st.sidebar.markdown('<div class="submenu">', unsafe_allow_html=True)

    if st.sidebar.button("📥 Import"):
        set_menu("Import")

    if st.sidebar.button("📤 Export"):
        set_menu("Export")

    if st.sidebar.button("⬇️ Downloads"):
        set_menu("Downloads")

    if st.sidebar.button("🌐 Communications"):
        set_menu("Communications")

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

if st.sidebar.button("▼ Settings" if st.session_state.expand["settings"] else "▶ Settings"):
    toggle("settings")

if st.session_state.expand["settings"]:
    st.sidebar.markdown('<div class="submenu">', unsafe_allow_html=True)

    if st.sidebar.button("👤 Users"):
        set_menu("Users")

    if st.sidebar.button("⚙️ Systems"):
        set_menu("Systems")

    if st.sidebar.button("🔋 Battery Types"):
        set_menu("Battery Types")

    if st.sidebar.button("🚨 Alarm Notification"):
        set_menu("Alarm Notification")

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

if st.sidebar.button("▼ Advanced" if st.session_state.expand["advanced"] else "▶ Advanced"):
    toggle("advanced")

if st.session_state.expand["advanced"]:
    st.sidebar.markdown('<div class="submenu">', unsafe_allow_html=True)

    if st.sidebar.button("🧠 Diagnostics"):
        set_menu("Diagnostics")

    if st.sidebar.button("📜 Logs"):
        set_menu("Logs")

    if st.sidebar.button("💻 System Info"):
        set_menu("System Info")

    if st.sidebar.button("🧠 Analyze Input"):
        set_menu("Analyze")

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# =========================
# ROUTING
# =========================
menu = st.session_state.menu

if menu == "Dashboard":
    render_dashboard()

elif menu == "Analyze":
    render_analyze()

elif menu == "Battery Types":
    render_battery_settings()

elif menu == "Realtime Detail":
    render_detail()

elif menu == "Systems":
    render_system_settings()

elif menu == "Alarm Notification":
    render_notification()

else:
    st.title(f"📌 {menu}")
    st.info("Halaman ini masih dalam pengembangan.")
