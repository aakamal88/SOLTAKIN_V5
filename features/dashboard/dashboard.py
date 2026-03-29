import streamlit as st
import plotly.graph_objects as go
import json
import os
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from map.gis_data import get_sites
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SETTINGS_FILE = os.path.join(ROOT_DIR, "config", "settings.json")


# =========================
# GLOBAL STYLE (SCADA UI)
# =========================
st.markdown("""
<style>
.main > div {
    padding-top: 1rem;
}
.scada-card {
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}
.scada-title {
    text-align:center;
    font-size:20px;
    font-weight:600;
    margin-bottom:15px;
}
.gauge-title {
    text-align:center;
    font-weight:600;
    margin-bottom:5px;
}
.badge {
    text-align:center;
    padding:4px;
    border-radius:6px;
    color:white;
    font-size:12px;
    margin-top:5px;
}
@keyframes blink {
    0% {opacity:1;}
    50% {opacity:0.3;}
    100% {opacity:1;}
}
@keyframes pulse {
    0% {transform: scale(1);}
    50% {transform: scale(1.3);}
    100% {transform: scale(1);}
}
.blink-alert {
    animation: blink 0.4s infinite, pulse 0.6s infinite !important;
    text-shadow: 0 0 6px red;
}
.blink-critical {
    animation: blink 0.8s infinite !important;
    text-shadow: 0 0 4px orange;
}
.blink-warning {
    animation: blink 1.5s infinite !important;
}
.marker-blink {
    animation: blink 1s infinite, pulse 1s infinite;
    border-radius: 50%;
    box-shadow: 0 0 10px currentColor;
}
</style>
""", unsafe_allow_html=True)


# =========================
# SETTINGS
# =========================
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        st.error(f"Settings file tidak ditemukan: {SETTINGS_FILE}")
        return {}
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error baca settings.json: {e}")
        return {}

def save_settings(data):
    try:
        current = load_settings()
        current.update(data)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(current, f, indent=4)
    except:
        pass


# =========================
# HELPERS
# =========================
def get_map_style():
    return load_settings().get("map_style", "OpenStreetMap")


def get_alarm_setting():
    return load_settings().get("alarm_setting", {})


def auto_refresh():
    pass


def get_data():
    d = load_settings().get("data", {})
    return {
        "capacity": d.get("capacity", 21.64),
        "cycle": d.get("cycle", 1),
        "current": d.get("current", 0.00),
        "status": d.get("status", "Idle"),
        "soc": d.get("soc", 65),
        "soh": d.get("soh", 92),
        "ir": d.get("ir", 1.1),
        "temp": d.get("temp", 32),
        "ambient": d.get("ambient", 28),
        "pressure": d.get("pressure", 760),
        "cell_voltage": d.get("cell_voltage", []),

        # 🔥 TAMBAHKAN INI
        "table_soc": d.get("table_soc", []),
        "table_soh": d.get("table_soh", []),
        "table_rint": d.get("table_rint", []),
        "table_temp": d.get("table_temp", []),
        "table_lvl": d.get("table_lvl", []),
    }


def get_config():
    c = load_settings().get("battery_config", {})
    return {"series": c.get("series", 0)}

def render_cell_tables(series, data):
    if series <= 0:
        st.warning("Jumlah battery series belum diset")
        return

    st.markdown("### 🔋 Cells Performance")

    MAX_COL = 5

    # 🔥 AMBIL DATA BARU (INI KUNCINYA)
    table_soc = data.get("table_soc", [])
    table_soh = data.get("table_soh", [])
    table_rint = data.get("table_rint", [])
    table_temp = data.get("table_temp", [])
    table_lvl = data.get("table_lvl", [])

    for row_start in range(0, series, MAX_COL):
        row_cells = range(row_start, min(row_start + MAX_COL, series))
        cols = st.columns(len(row_cells))

        for col, i in zip(cols, row_cells):
            cell_num = i + 1

            # SAFE ACCESS
            soc_val = f"{int(table_soc[i])}" if i < len(table_soc) else "-"
            soh_val = f"{int(table_soh[i])}" if i < len(table_soh) else "-"
            lvl_val = f"{int(table_lvl[i])}" if i < len(table_lvl) else "-"

            rint_val = f"{table_rint[i]:.2f}" if i < len(table_rint) else "-"
            temp_val = f"{table_temp[i]:.1f}" if i < len(table_temp) else "-"

            with col:
                st.markdown(f"**Cell {cell_num}**")

                table_data = {
                    "Parameter": ["SoC", "SoH", "Rint", "Temp", "Level"],
                    "Value": [
                        soc_val,
                        soh_val,
                        rint_val,
                        temp_val,
                        lvl_val,
                    ],
                    "Unit": ["%", "%", "mOhm", "Deg.C", "%"]
                }

                # =========================
                # 🎨 STATUS COLOR LOGIC
                # =========================
                def get_cell_color(param, val):
                    try:
                        val = float(val)
                    except:
                        return "#374151"

                    if param == "SoC":
                        if val < 10:
                            return "#7f1d1d"
                        elif val < 20:
                            return "#ef4444"
                        elif val < 50:
                            return "#f59e0b"
                        else:
                            return "#22c55e"

                    if param == "SoH":
                        if val < 30:
                            return "#7f1d1d"
                        elif val < 50:
                            return "#ef4444"
                        elif val < 80:
                            return "#f59e0b"
                        else:
                            return "#22c55e"

                    if param == "Rint":
                        if val > 1.8:
                            return "#7f1d1d"
                        elif val > 1.5:
                            return "#ef4444"
                        elif val > 1.1:
                            return "#f59e0b"
                        else:
                            return "#22c55e"

                    if param == "Temp":
                        if val > 48:
                            return "#7f1d1d"
                        elif val > 45:
                            return "#ef4444"
                        elif val > 35:
                            return "#f59e0b"
                        else:
                            return "#22c55e"

                    return "#22c55e"

                # =========================
                # 🎨 CUSTOM TABLE UI
                # =========================
                rows_html = ""

                for p, v, u in zip(table_data["Parameter"], table_data["Value"], table_data["Unit"]):
                    color = get_cell_color(p, v)

                    # =========================
                    # 🚨 DETECT STATUS (UNTUK BLINK)
                    # =========================
                    blink_class = ""

                    try:
                        val = float(v)

                        if p == "SoC":
                            if val < 10:
                                blink_class = "blink-alert"
                            elif val < 20:
                                blink_class = "blink-critical"
                            elif val < 50:
                                blink_class = "blink-warning"

                        elif p == "SoH":
                            if val < 30:
                                blink_class = "blink-alert"
                            elif val < 50:
                                blink_class = "blink-critical"
                            elif val < 80:
                                blink_class = "blink-warning"

                        elif p == "Rint":
                            if val > 1.8:
                                blink_class = "blink-alert"
                            elif val > 1.5:
                                blink_class = "blink-critical"
                            elif val > 1.1:
                                blink_class = "blink-warning"

                        elif p == "Temp":
                            if val > 48:
                                blink_class = "blink-alert"
                            elif val > 45:
                                blink_class = "blink-critical"
                            elif val > 35:
                                blink_class = "blink-warning"

                    except:
                        pass

                    rows_html += f"""
                    <tr>
                        <td class="{blink_class}" style="
                            padding:6px;
                            text-align:right;
                            font-weight:600;
                            color:{color};
                        ">
                            {v}
                        </td>
                        <td style="padding:6px;text-align:right;color:#9ca3af;">
                            {u}
                        </td>
                    </tr>
                    """

                table_html = f"""
                <div style="
                    background:#e5e7eb;
                    border-radius:12px;
                    padding:10px;
                    box-shadow:0 4px 12px rgba(0,0,0,0.4);
                ">
                    <table style="width:100%;border-collapse:collapse;font-size:13px;">
                        <thead>
                            <tr style="color:#9ca3af;text-align:left;border-bottom:1px solid #374151;">
                                <th>Param</th>
                                <th style="text-align:right;">Value</th>
                                <th style="text-align:right;">Unit</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </div>
                """

                components.html(table_html, height=230)

# =========================
# STATUS LOGIC
# =========================
def get_status(val, key):

    alarm = get_alarm_setting().get(key, {})

    warn = alarm.get("warning")
    crit = alarm.get("critical")
    alert = alarm.get("alert")

    if warn is None:
        if key == "soc":
            if val < 10: return "ALERT", "#7f1d1d"
            if val < 20: return "CRITICAL", "#ef4444"
            elif val < 50: return "WARNING", "#f59e0b"
            else: return "GOOD", "#22c55e"

        if key == "soh":
            if val < 30: return "ALERT", "#7f1d1d"
            if val < 50: return "CRITICAL", "#ef4444"
            elif val < 80: return "WARNING", "#f59e0b"
            else: return "GOOD", "#22c55e"

        if key == "ir":
            if val > 1.8: return "ALERT", "#7f1d1d"
            if val > 1.5: return "CRITICAL", "#ef4444"
            elif val > 1.1: return "WARNING", "#f59e0b"
            else: return "GOOD", "#22c55e"

        if key == "temp":
            if val > 48: return "ALERT", "#7f1d1d"
            if val > 45: return "CRITICAL", "#ef4444"
            elif val > 35: return "WARNING", "#f59e0b"
            else: return "GOOD", "#22c55e"

        return "GOOD", "#22c55e"

    if key in ["soc","soh","voltage"]:
        if val <= alert: return "ALERT","#7f1d1d"
        elif val <= crit: return "CRITICAL","#ef4444"
        elif val <= warn: return "WARNING","#f59e0b"
        else: return "GOOD","#22c55e"
    else:
        if val >= alert: return "ALERT","#7f1d1d"
        elif val >= crit: return "CRITICAL","#ef4444"
        elif val >= warn: return "WARNING","#f59e0b"
        else: return "GOOD","#22c55e"


def get_perf_color(data):
    if data["soc"] < 20 or data["temp"] > 45:
        return "#fee2e2"
    elif data["temp"] > 35:
        return "#fef3c7"
    return "#ecfdf5"


def create_card(title, value, color="#1f2937", icon="⚡"):
    return f"""
    <div style="width:100%;height:120px;display:flex;align-items:center;justify-content:center;">

        <div style='
            width:100%;
            background: linear-gradient(135deg, {color}, #111827);
            border-radius:16px;
            padding:12px;
            text-align:center;
            box-shadow:0 6px 18px rgba(0,0,0,0.5);
            border:1px solid rgba(255,255,255,0.08);
        '>

            <div style='font-size:20px;'>{icon}</div>

            <div style='
                font-size:12px;
                color:#9ca3af;
                margin-top:2px;
            '>
                {title}
            </div>

            <div style='
                font-size:18px;
                font-weight:700;
                color:white;
                margin-top:4px;
            '>
                {value}
            </div>

        </div>
    </div>
    """

def create_gauge(val, minv, maxv, unit, key_type):
    steps = []

    if key_type == "soc":
        steps = [
            {'range':[0,20],'color':'red'},
            {'range':[20,50],'color':'orange'},
            {'range':[50,100],'color':'green'}
        ]

    elif key_type == "soh":
        steps = [
            {'range':[0,50],'color':'red'},
            {'range':[50,80],'color':'orange'},
            {'range':[80,100],'color':'green'}
        ]

    elif key_type == "ir":
        steps = [
            {'range':[0,1.1],'color':'green'},
            {'range':[1.1,1.5],'color':'orange'},
            {'range':[1.5,2],'color':'red'}
        ]

    elif key_type == "temp":
        steps = [
            {'range':[-10,0],'color':'red'},
            {'range':[0,30],'color':'green'},
            {'range':[30,40],'color':'orange'},
            {'range':[40,60],'color':'red'}
        ]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        number={
            'suffix': f" {unit}",
            'valueformat': ".2f" if key_type == "ir"
                  else ".1f" if key_type == "temp"
                  else ".0f"
        },
        gauge={
            'axis': {'range': [minv, maxv]},
            'bar': {'color': "#00FFFF"},
            'steps': steps,
            'threshold': {
                'line': {'color': "white", 'width': 3},
                'value': val
            }
        }
    ))

    fig.update_layout(height=350)

    return fig


# =========================
# MAP FUNCTION (FIX BLINK)
# =========================
def create_folium_map(sites, style):

    m = folium.Map(
        location=[-2, 118],
        zoom_start=10,
        tiles=None
    )

    folium.TileLayer(
       #tiles=f"http://localhost:8080/styles/{style}/{{z}}/{{x}}/{{y}}.png",
        tiles=f"http://192.168.1.170:8080/styles/{style}/{{z}}/{{x}}/{{y}}.png",
        attr="Offline Map"
    ).add_to(m)

    # fallback online
    folium.TileLayer("OpenStreetMap").add_to(m)

    folium.GeoJson(
        "map/owja.geojson",
        style_function=lambda x: {
            "fillColor": "transparent",
            "color": "blue",
            "weight": 3,
            "dashArray": "13, 13"
        }
    ).add_to(m)

    folium.GeoJson(
        "map/oeja.geojson",
        style_function=lambda x: {
            "fillColor": "transparent",
            "color": "blue",
            "weight": 3,
            "dashArray": "13, 13"
        }
    ).add_to(m)

    folium.GeoJson(
        "map/smg_btg.geojson",
        style_function=lambda x: {
            "fillColor": "transparent",
            "color": "red",
            "weight": 3,
            "dashArray": "13, 13"
        }
    ).add_to(m)


    # =========================
    # MARKER
    # =========================
    for s in sites:
        statuses = [
            get_status(s["soc"], "soc")[0],
            get_status(s["soh"], "soh")[0],
            get_status(s["ir"], "ir")[0],
            get_status(s["temp"], "temp")[0],
        ]

        priority = {
            "GOOD": 0,
            "WARNING": 1,
            "CRITICAL": 2,
            "ALERT": 3
        }

        status = max(statuses, key=lambda x: priority[x])

        color_map = {
            "GOOD": "green",
            "WARNING": "orange",
            "CRITICAL": "red",
            "ALERT": "darkred"
        }

        marker_color = color_map.get(status, "green")

        # =========================
        # ✅ POPUP HTML (WAJIB DI SINI)
        # =========================
        def get_param_color(param, val):
            try:
                val = float(val)
            except:
                return "#9ca3af"

            if param == "soc":
                if val < 10:
                    return "#7f1d1d"
                elif val < 20:
                    return "#ef4444"
                elif val < 50:
                    return "#f59e0b"
                else:
                    return "#22c55e"

            if param == "soh":
                if val < 30:
                    return "#7f1d1d"
                elif val < 50:
                    return "#ef4444"
                elif val < 80:
                    return "#f59e0b"
                else:
                    return "#22c55e"

            if param == "ir":
                if val > 1.8:
                    return "#7f1d1d"
                elif val > 1.5:
                    return "#ef4444"
                elif val > 1.1:
                    return "#f59e0b"
                else:
                    return "#22c55e"

            if param == "temp":
                if val > 48:
                    return "#7f1d1d"
                elif val > 45:
                    return "#ef4444"
                elif val > 35:
                    return "#f59e0b"
                else:
                    return "#22c55e"

            return "#22c55e"

        # =========================
        # 🎯 HITUNG WARNA
        # =========================
        soc_color = get_param_color("soc", s.get("soc", 0))
        soh_color = get_param_color("soh", s.get("soh", 0))
        temp_color = get_param_color("temp", s.get("temp", 0))
        r_color = get_param_color("ir", s.get("ir", 0))


        popup_html = f"""
        <div style="width:220px;font-family:sans-serif;">

            <div style="font-weight:700;font-size:14px;margin-bottom:6px;">
                ⚡ {s['station']}
            </div>

            <div style="
                background:#111827;
                border-radius:10px;
                padding:8px;
                color:white;
                box-shadow:0 4px 10px rgba(0,0,0,0.5);
            ">

                <div>🔋 SOC: <b style="color:{soc_color}">{s.get('soc', '-')}%</b></div>
                <div>🧠 SOH: <b style="color:{soh_color}">{s.get('soh', '-')}%</b></div>
                <div>🌡 Temp: <b style="color:{temp_color}">{s.get('temp', '-')} °C</b></div>
                <div>🧪 Rint: <b style="color:{r_color}">{s.get('ir', 0):.2f} mΩ</b></div>

                <div style="
                    margin-top:6px;
                    padding:4px;
                    border-radius:6px;
                    text-align:center;
                    background:{marker_color};
                    font-size:12px;
                ">
                    {status}
                </div>

            </div>
        </div>
        """

        # =========================
        # MARKER
        # =========================
        blink_style = ""

        if status == "ALERT":
            blink_style = "animation: blink 0.4s infinite, pulse 0.6s infinite;"
        elif status == "CRITICAL":
            blink_style = "animation: blink 0.8s infinite, pulse 1s infinite;"
        elif status == "WARNING":
            blink_style = "animation: blink 1.5s infinite;"

        html = f"""
        <div>

        <style>
        @keyframes blink {{
            0% {{opacity:1;}}
            50% {{opacity:0.3;}}
            100% {{opacity:1;}}
        }}

        @keyframes pulse {{
            0% {{transform: scale(1);}}
            50% {{transform: scale(1.4);}}
            100% {{transform: scale(1);}}
        }}
        </style>

        <div style="
            width:20px;
            height:20px;
            background:{marker_color};
            border:2px solid white;
            border-radius:50%;
            box-shadow: 0 0 12px {marker_color};
            {blink_style}
        "></div>

        </div>
        """

        folium.Marker(
            location=[s["lat"], s["lon"]],
            icon=folium.DivIcon(html=html),
            popup=folium.Popup(popup_html, max_width=250)
        ).add_to(m)

    if sites:
        locations = [(s["lat"], s["lon"]) for s in sites]
        m.fit_bounds(locations)

    return m


# =========================
# MAIN
# =========================
def render_dashboard():

    st.set_page_config(layout="wide")
    st_autorefresh(interval=10000, key="dashboard_refresh")
    data = get_data()
    cfg = get_config()

    st.title("📊 Dashboard")

    # =========================
    # MAP
    # =========================
    st.subheader("🌍 Soltakin Site Map")

    style = st.selectbox(
        "🗺 Map Style",
        ["basic-preview", "dark-matter", "osm-bright"]
    )

    sites = get_sites(data)
    folium_map = create_folium_map(sites, style)

    # ✅ FIX: key dibuat STATIC → tidak blinking lagi
    st_folium(
        folium_map,
        use_container_width=True,
        height=600,
        key="folium_map"
    )

    # =========================
    # CARDS
    # =========================
    st.markdown("---")
    perf_color = get_perf_color(data)

    st.markdown(f"""
    <div class="scada-card" style="background:{perf_color};">
        <div class="scada-title">UPS System Monitor</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

    cards = [
        ("Est. Capacity", f"{data['capacity']} Ah", "#2563eb", "🔋"),
        ("String Voltage", f"{round(sum(data['cell_voltage']), 2)} V", "#7c3aed", "⚡"),
        ("Cycle", data['cycle'], "#0ea5e9", "🔄"),
        ("String Current", f"{data['current']} A", "#f59e0b", "🔌"),
        ("Battery Series", f"{cfg['series']} Cell", "#10b981", "🧱"),
        ("Status", data['status'], "#ef4444", "🚨"),
        ("Ambient", f"{data['ambient']} °C", "#22c55e", "🌡"),
        ("Pressure", data['pressure'], "#eab308", "📊"),
    ]

    cols = st.columns(len(cards))
    for i, (t, v, c, ic) in enumerate(cards):
        with cols[i]:
            components.html(create_card(t, v, c, ic), height=140)

    # =========================
    # PERFORMANCE PANEL
    # =========================
    st.markdown("---")

    perf_color = get_perf_color(data)

    st.markdown(f"""
    <div class="scada-card" style="background:{perf_color};">
        <div class="scada-title">Battery System Performance</div>
    </div>
    """, unsafe_allow_html=True)

    g1, g2, g3, g4 = st.columns(4)

    configs = [
        ("soc", "%", 0, 100, "State of Charge"),
        ("soh", "%", 0, 100, "State of Health"),
        ("ir", "mΩ", 0, 2, "Avg. Resistance"),
        ("temp", "°C", 0, 60, "Avg. Temperature"),
    ]

    for idx, (col, (k, u, minv, maxv, title)) in enumerate(zip([g1, g2, g3, g4], configs)):
        with col:
            st.markdown(f'<div class="gauge-title">{title}</div>', unsafe_allow_html=True)

            # =========================
            # 🎯 FORMAT VALUE
            # =========================
            if k == "ir":
                val = round(data[k], 2)
            elif k == "temp":
                val = round(data[k], 1)
            elif k in ["soc", "soh"]:
                val = int(round(data[k]))
            else:
                val = data[k]

            st.plotly_chart(
                create_gauge(val, minv, maxv, u, k),
                use_container_width=True,
                key=f"perf_{k}_{idx}"
            )

            label, color = get_status(data[k], k)
            alarm = get_alarm_setting().get(k, {})
            warn = alarm.get("warning")
            crit = alarm.get("critical")
            alert = alarm.get("alert")

            # fallback default
            if warn is None:
                if k == "soc":
                    warn, crit, alert = 50, 20, 10
                elif k == "soh":
                    warn, crit, alert = 80, 50, 30
                elif k == "ir":
                    warn, crit, alert = 1.1, 1.5, 1.8
                elif k == "temp":
                    warn, crit, alert = 35, 45, 48

            animation_style = ""
            if label == "ALERT":
                animation_style = "animation: blink 0.4s infinite;"  # cepat
            elif label == "CRITICAL":
                animation_style = "animation: blink 0.8s infinite;"  # medium
            elif label == "WARNING":
                animation_style = "animation: blink 1.5s infinite;"  # lambat

            html = f"""
            <div style="text-align:center;">

                <div style="
                    font-size:16px;
                    margin-top:2px;
                    margin-bottom:4px;
                    line-height:1.4;
                ">
                    ⚠ Warning: <b>{warn}</b><br>
                    🔥 Critical: <b>{crit}</b><br>
                    🚨 Alert: <b>{alert}</b>
                </div>

                <div style="
                    background:{color};
                    color:white;
                    padding:4px;
                    border-radius:6px;
                    font-size:12px;
                    text-align:center;
                    {animation_style}
                ">
                    {label}
                </div>

            </div>

            <style>
            @keyframes blink {{
                0% {{opacity:1;}}
                50% {{opacity:0.3;}}
                100% {{opacity:1;}}
            }}
            </style>
            """

            components.html(html, height=110)

# =========================
# CELL TABLE (DYNAMIC)
# =========================
    st.markdown("---")
    render_cell_tables(cfg["series"], data)
