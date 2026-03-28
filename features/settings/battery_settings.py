import streamlit as st
import json
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILE = os.path.join(ROOT_DIR, "config", "settings.json")

def load():
    if os.path.exists(FILE):
        try:
            with open(FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save(data):
    settings = load()
    settings["battery_config"] = data
    with open(FILE, "w") as f:
        json.dump(settings, f, indent=4)

def render_battery_settings():

    st.title("🔋 Battery Type Settings")

    settings = load()
    config = settings.get("battery_config", {})

    # 🔥 LOAD VALUE (IMPORTANT)
    chemical = st.selectbox(
        "Battery Chemical",
        ["NiCd", "VRLA", "VLA", "Li-Ion"],
        index=["NiCd","VRLA","VLA","Li-Ion"].index(config.get("chemical","NiCd"))
    )

    if chemical == "NiCd":
        model_list = ["VTX-1M-150", "VTX-1M-270"]
        model = st.selectbox(
            "Battery Model",
            model_list,
            index=model_list.index(config.get("model","VTX-1M-150"))
        )
    else:
        model = "No Data"
        st.warning("No model available")

    series = st.slider(
        "Battery Series",
        1, 100,
        value=config.get("series", 24)
    )

    # AUTO PARAM
    if model == "VTX-1M-150":
        capacity = "150 Ah"
        resistance = "0.76 mΩ"
        voltage = 1.42
    elif model == "VTX-1M-270":
        capacity = "270 Ah"
        resistance = "0.42 mΩ"
        voltage = 1.42
    else:
        capacity = "-"
        resistance = "-"
        voltage = 0

    st.info(f"Voltage: {voltage} V")
    st.success(f"Capacity: {capacity}")
    st.success(f"Internal Resistance: {resistance}")

    if st.button("💾 Save"):
        save({
            "chemical": chemical,
            "model": model,
            "series": series,
            "voltage": voltage,
            "capacity": capacity,
            "resistance": resistance
        })
        st.success("Saved!")

