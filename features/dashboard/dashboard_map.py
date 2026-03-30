import streamlit as st
import folium
from streamlit_folium import st_folium
from map.gis_data import get_sites

from .dashboard_utils import get_status


def create_folium_map(sites, style):

    m = folium.Map(
        location=[-2, 118],
        zoom_start=10,
        tiles=None
    )

    folium.TileLayer(
        tiles=f"http://192.168.1.170:8080/styles/{style}/{{z}}/{{x}}/{{y}}.png",
        attr="Offline Map"
    ).add_to(m)

    folium.TileLayer("OpenStreetMap").add_to(m)

    for s in sites:

        # 🔥 MULTI PARAMETER STATUS
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
        # 🎨 PARAM COLOR
        # =========================
        def get_param_color(param, val):
            try:
                val = float(val)
            except:
                return "#9ca3af"

            if param == "soc":
                if val < 10: return "#7f1d1d"
                elif val < 20: return "#ef4444"
                elif val < 50: return "#f59e0b"
                else: return "#22c55e"

            if param == "soh":
                if val < 30: return "#7f1d1d"
                elif val < 50: return "#ef4444"
                elif val < 80: return "#f59e0b"
                else: return "#22c55e"

            if param == "ir":
                if val > 1.8: return "#7f1d1d"
                elif val > 1.5: return "#ef4444"
                elif val > 1.1: return "#f59e0b"
                else: return "#22c55e"

            if param == "temp":
                if val > 48: return "#7f1d1d"
                elif val > 45: return "#ef4444"
                elif val > 35: return "#f59e0b"
                else: return "#22c55e"

            return "#22c55e"

        soc_color = get_param_color("soc", s.get("soc", 0))
        soh_color = get_param_color("soh", s.get("soh", 0))
        temp_color = get_param_color("temp", s.get("temp", 0))
        r_color = get_param_color("ir", s.get("ir", 0))

        # =========================
        # 🔥 POPUP SCADA (BALIKIN)
        # =========================
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
        # 🔥 BLINK MARKER
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


def render_map(data):
    st.subheader("🌍 Soltakin Site Map")

    style = st.selectbox(
        "🗺 Map Style",
        ["basic-preview", "dark-matter", "osm-bright"]
    )

    sites = get_sites(data)

    folium_map = create_folium_map(sites, style)

    st_folium(
        folium_map,
        use_container_width=True,
        height=600,
        key="folium_map"
    )