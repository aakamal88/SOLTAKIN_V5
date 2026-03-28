import streamlit as st
import json
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILE = os.path.join(ROOT_DIR, "config", "settings.json")

# =========================
# LOAD
# =========================
def load():
    if os.path.exists(FILE):
        try:
            with open(FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

# =========================
# SAVE
# =========================
def save_alarm(data):
    settings = load()
    settings["alarm_setting"] = data

    with open(FILE, "w") as f:
        json.dump(settings, f, indent=4)

# =========================
# DEFAULT
# =========================
def default_alarm():
    return {
        "soc": {"warning":50,"critical":20,"alert":10},
        "soh": {"warning":80,"critical":50,"alert":30},
        "ir": {"warning":1.1,"critical":1.5,"alert":1.8},
        "temp": {"warning":35,"critical":45,"alert":55},
        "ambient": {"warning":30,"critical":40,"alert":50},
        "current": {"warning":50,"critical":80,"alert":100},
        "voltage": {"warning":48,"critical":44,"alert":40}
    }

# =========================
# UI
# =========================
def render_notification():

    st.title("🚨 Battery System Alarm Setting")

    settings = load()
    alarm = settings.get("alarm_setting", default_alarm())

    def input_block(name, label, minv, maxv):
        st.subheader(label)

        col1, col2, col3 = st.columns(3)

        with col1:
            w = st.number_input(f"{label} Warning", minv, maxv,
                                alarm[name]["warning"], key=f"{name}_w")

        with col2:
            c = st.number_input(f"{label} Critical", minv, maxv,
                                alarm[name]["critical"], key=f"{name}_c")

        with col3:
            a = st.number_input(f"{label} Alert", minv, maxv,
                                alarm[name]["alert"], key=f"{name}_a")

        return {"warning": w, "critical": c, "alert": a}

    new_alarm = {
        "soc": input_block("soc", "SoC (%)", 0, 100),
        "soh": input_block("soh", "SoH (%)", 0, 100),
        "ir": input_block("ir", "Avg Resistance (mΩ)", 0.0, 5.0),
        "temp": input_block("temp", "Avg Temperature (°C)", -20, 100),
        "ambient": input_block("ambient", "Ambient Temp (°C)", -20, 100),
        "current": input_block("current", "String Current (A)", 0, 500),
        "voltage": input_block("voltage", "String Voltage (V)", 0, 500)
    }

    if st.button("💾 Save Alarm Setting"):
        save_alarm(new_alarm)
        st.success("Alarm setting saved!")