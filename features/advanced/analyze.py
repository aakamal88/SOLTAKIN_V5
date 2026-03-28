import streamlit as st
import json
import os
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
TOPIC = "soltakin/battery"

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
def save(data):
    settings = load()
    settings["data"] = data
    with open(FILE, "w") as f:
        json.dump(settings, f, indent=4)


# =========================
# MQTT
# =========================
def publish_mqtt(payload):
    try:
        client = mqtt.Client()
        client.connect(BROKER, 1883, 60)
        client.publish(TOPIC, json.dumps(payload))
        client.disconnect()
    except:
        pass


# =========================
# HELPER
# =========================
def avg(arr, default=0):
    return sum(arr) / len(arr) if len(arr) > 0 else default


# =========================
# MAIN
# =========================
def render_analyze():

    st.title("🧠 Analyze Input (Realtime Mode)")

    settings = load()
    data = settings.get("data", {})
    config = settings.get("battery_config", {})

    series = config.get("series", 10)

    # =========================
    # 🔥 COMPUTE FROM SAVED DATA
    # =========================
    soc = avg(data.get("table_soc", []), data.get("soc", 65))
    soh = avg(data.get("table_soh", []), data.get("soh", 92))
    ir = avg(data.get("table_rint", []), data.get("ir", 1.1))
    temp = avg(data.get("table_temp", []), data.get("temp", 32))

    # =========================
    # 🎯 FORMAT FOR DISPLAY
    # =========================
    display_soc = int(round(soc))
    display_soh = int(round(soh))
    display_ir = round(ir, 2)
    display_temp = round(temp, 1)

    # =========================
    # 🔝 TOP DISPLAY
    # =========================
    st.subheader("📈 Battery System Performance")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("SOC (Avg)", display_soc)
    col2.metric("SOH (Avg)", display_soh)
    col3.metric("IR (Avg)", display_ir)
    col4.metric("Temp (Avg)", display_temp)

    st.markdown("---")

    # =========================
    # GLOBAL PARAMETER
    # =========================
    ambient = st.slider("Ambient", 0, 50, data.get("ambient", 28))
    pressure = st.slider("Pressure", 700, 800, data.get("pressure", 760))

    st.subheader("Additional Parameters")

    capacity = st.number_input("Remaining Capacity (Ah)", value=float(data.get("capacity", 21.64)))
    cycle = st.number_input("Cycle Count", value=int(data.get("cycle", 1)), step=1)
    current = st.number_input("Current (A)", value=float(data.get("current", 0.00)), format="%.2f")

    status = st.selectbox(
        "Status",
        ["Idle", "Charging", "Discharging"],
        index=["Idle", "Charging", "Discharging"].index(data.get("status", "Idle"))
    )

    # =========================
    # CELL PARAMETER
    # =========================
    st.markdown("---")
    st.subheader("🔋 Cell Parameters")

    voltages, temps, liquids = [], [], []

    old_v = data.get("cell_voltage", [])
    old_t = data.get("cell_temperature", [])
    old_l = data.get("cell_liquid", [])

    for i in range(series):
        col1, col2, col3 = st.columns(3)

        with col1:
            v = st.number_input(f"Cell {i+1} Voltage", 0.0, 2.0,
                                old_v[i] if i < len(old_v) else 1.4,
                                key=f"cell_v_{i}")

        with col2:
            t = st.number_input(f"Cell {i+1} Temp", -10, 80,
                                old_t[i] if i < len(old_t) else 30,
                                key=f"cell_t_{i}")

        with col3:
            l = st.number_input(f"Cell {i+1} Liquid (%)", 0, 100,
                                old_l[i] if i < len(old_l) else 80,
                                key=f"cell_l_{i}")

        voltages.append(v)
        temps.append(t)
        liquids.append(l)

    # =========================
    # TABLE INPUT
    # =========================
    st.markdown("---")
    st.subheader("📊 Table Parameter Input")

    table_soc, table_soh, table_rint, table_temp, table_lvl = [], [], [], [], []

    old_soc = data.get("table_soc", [])
    old_soh = data.get("table_soh", [])
    old_rint = data.get("table_rint", [])
    old_temp = data.get("table_temp", [])
    old_lvl = data.get("table_lvl", [])

    for i in range(series):
        st.markdown(f"### Cell {i+1}")
        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            soc_val = st.number_input(f"SoC {i+1}", 0, 100,
                                      old_soc[i] if i < len(old_soc) else 50,
                                      key=f"table_soc_{i}")

        with c2:
            soh_val = st.number_input(f"SoH {i+1}", 0, 100,
                                      old_soh[i] if i < len(old_soh) else 90,
                                      key=f"table_soh_{i}")

        with c3:
            rint_val = st.number_input(f"Rint {i+1}", 0.0, 2.0,
                                       old_rint[i] if i < len(old_rint) else 1.0,
                                       key=f"table_rint_{i}")

        with c4:
            temp_val = st.number_input(f"Temp {i+1}", -10, 80,
                                       old_temp[i] if i < len(old_temp) else 30,
                                       key=f"table_temp_{i}")

        with c5:
            lvl_val = st.number_input(f"Level {i+1}", 0, 100,
                                      old_lvl[i] if i < len(old_lvl) else 80,
                                      key=f"table_lvl_{i}")

        table_soc.append(soc_val)
        table_soh.append(soh_val)
        table_rint.append(rint_val)
        table_temp.append(temp_val)
        table_lvl.append(lvl_val)

    # =========================
    # SAVE UPDATED DATA
    # =========================
    soc = avg(table_soc, soc)
    soh = avg(table_soh, soh)
    ir = avg(table_rint, ir)
    temp = avg(table_temp, temp)

    new_data = {
        "soc": soc,
        "soh": soh,
        "ir": ir,
        "temp": temp,
        "ambient": ambient,
        "pressure": pressure,
        "capacity": capacity,
        "cycle": cycle,
        "current": current,
        "status": status,

        "cell_voltage": voltages,
        "cell_temperature": temps,
        "cell_liquid": liquids,

        "table_soc": table_soc,
        "table_soh": table_soh,
        "table_rint": table_rint,
        "table_temp": table_temp,
        "table_lvl": table_lvl,
    }

    save(new_data)

    payload = {
        "data": new_data,
        "battery_config": load().get("battery_config", {})
    }

    publish_mqtt(payload)