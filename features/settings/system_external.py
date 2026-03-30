import streamlit as st
from .location_utils import load_json, save_json, ping_ip, ROOT_DIR
import os
import time

# pymodbus
from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

FILE_MODBUS = os.path.join(ROOT_DIR, "config", "ptg_modbus.json")

# =========================
# DEFAULT CONFIG
# =========================
DEFAULT = {
    "enable": True,
    "mode": "Client",
    "timeout": 1000,
    "retry": 3,
    "port": 502,
    "scan_rate": 1000,
    "byte_order": "Big Endian",
    "word_order": "Big Endian",
    "nodes": [],
    "registers": []
}

# =========================
# DECODE
# =========================
def decode_registers(registers, dtype, byte_order, word_order):
    byte = Endian.BIG if byte_order == "Big Endian" else Endian.LITTLE
    word = Endian.BIG if word_order == "Big Endian" else Endian.LITTLE

    decoder = BinaryPayloadDecoder.fromRegisters(
        registers, byteorder=byte, wordorder=word
    )

    try:
        if dtype == "INT16":
            return decoder.decode_16bit_int()
        elif dtype == "UINT16":
            return decoder.decode_16bit_uint()
        elif dtype == "INT32":
            return decoder.decode_32bit_int()
        elif dtype == "FLOAT32":
            return round(decoder.decode_32bit_float(), 3)
        elif dtype == "BOOL":
            return bool(registers[0])
    except:
        return "Decode Err"

# =========================
# READ MODBUS
# =========================
def read_modbus(node, reg, config):
    try:
        client = ModbusTcpClient(
            node["ip"],
            port=node["port"],
            timeout=config["timeout"] / 1000
        )

        if not client.connect():
            return "No Conn"

        fc = reg["fc"]
        addr = reg["addr"]
        qty = reg["qty"]
        slave = node["slave"]

        if fc == "03":
            rr = client.read_holding_registers(addr, qty, slave=slave)
        elif fc == "04":
            rr = client.read_input_registers(addr, qty, slave=slave)
        elif fc == "01":
            rr = client.read_coils(addr, qty, slave=slave)
        elif fc == "02":
            rr = client.read_discrete_inputs(addr, qty, slave=slave)
        else:
            return "FC Not Support"

        client.close()

        if rr.isError():
            return "Read Err"

        if hasattr(rr, "registers"):
            return decode_registers(
                rr.registers,
                reg["type"],
                config["byte_order"],
                config["word_order"]
            )
        elif hasattr(rr, "bits"):
            return rr.bits[0]

        return "Unknown"

    except Exception as e:
        return f"Err: {str(e)[:25]}"

# =========================
# MAIN UI
# =========================
def render_external():
    st.subheader("🔌 Modbus TCP Configuration")

    data = load_json(FILE_MODBUS, DEFAULT)

    # STATE realtime
    if "mb_running" not in st.session_state:
        st.session_state.mb_running = False

    # ================= SETTINGS =================
    with st.expander("⚙️ Modbus Settings", expanded=True):

        col1, col2, col3 = st.columns(3)

        enable = col1.toggle("Enable Modbus", value=data["enable"], key="mb_enable")
        mode = col2.selectbox("Mode", ["Client", "Server"],
                              index=0 if data["mode"] == "Client" else 1, key="mb_mode")
        port = col3.number_input("Port", value=data["port"], key="mb_port_main")

        col4, col5, col6 = st.columns(3)

        timeout = col4.number_input("Timeout (ms)", value=data["timeout"], key="mb_timeout")
        retry = col5.number_input("Retry", value=data["retry"], key="mb_retry")
        scan_rate = col6.number_input("Scan Rate (ms)", value=data["scan_rate"], key="mb_scan")

        col7, col8 = st.columns(2)

        byte_order = col7.selectbox("Byte Order", ["Big Endian", "Little Endian"], key="mb_byte")
        word_order = col8.selectbox("Word Order", ["Big Endian", "Little Endian"], key="mb_word")

        if st.button("💾 Save Modbus Config", key="mb_save_cfg"):
            data.update({
                "enable": enable,
                "mode": mode,
                "port": port,
                "timeout": timeout,
                "retry": retry,
                "scan_rate": scan_rate,
                "byte_order": byte_order,
                "word_order": word_order
            })
            save_json(FILE_MODBUS, data)
            st.rerun()

    # ================= NODE =================
    st.divider()
    st.subheader("📡 Modbus Node List")

    if "mb_edit_idx" not in st.session_state:
        st.session_state.mb_edit_idx = None

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### ➕ Add / Edit Node")

        if st.session_state.mb_edit_idx is not None:
            n = data["nodes"][st.session_state.mb_edit_idx]
        else:
            n = {"name": "", "ip": "", "port": 502, "slave": 1}

        name = st.text_input("Node Name", value=n["name"], key="mb_name")
        ip = st.text_input("IP Address", value=n["ip"], key="mb_ip")
        port_n = st.number_input("Port", value=n["port"], key="mb_port_node")
        slave = st.number_input("Slave ID", value=n["slave"], key="mb_slave")

        if st.button("💾 Save Node", key="mb_save_node"):
            node = {
                "name": name,
                "ip": ip,
                "port": port_n,
                "slave": slave,
                "status": "-"
            }

            if st.session_state.mb_edit_idx is not None:
                data["nodes"][st.session_state.mb_edit_idx] = node
                st.session_state.mb_edit_idx = None
            else:
                data["nodes"].append(node)

            save_json(FILE_MODBUS, data)
            st.rerun()

    with col2:
        display = [{
            "Select": False,
            "Name": n["name"],
            "IP": n["ip"],
            "Port": n["port"],
            "Slave": n["slave"],
            "Status": n.get("status", "-")
        } for n in data["nodes"]]

        edited = st.data_editor(display, height=400, key="mb_table")
        selected = [i for i, r in enumerate(edited) if r["Select"]]

        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button("🔍 Test Connection", key="mb_test"):
                for i in selected:
                    node = data["nodes"][i]
                    node["status"] = "Connected" if ping_ip(node["ip"]) else "Fail"
                save_json(FILE_MODBUS, data)
                st.rerun()

        with c2:
            if st.button("✏️ Edit", key="mb_edit"):
                if len(selected) == 1:
                    st.session_state.mb_edit_idx = selected[0]
                    st.rerun()

        with c3:
            if st.button("🗑 Delete", key="mb_delete"):
                for i in sorted(selected, reverse=True):
                    data["nodes"].pop(i)
                save_json(FILE_MODBUS, data)
                st.rerun()

    # ================= REGISTER =================
    st.divider()
    st.subheader("🧪 Modbus Register Test")

    col1, col2 = st.columns([1, 2])

    # ================= FORM =================
    with col1:
        st.markdown("### ➕ Add Register")

        node_names = [n["name"] for n in data["nodes"]]

        if not node_names:
            st.warning("⚠️ Tambahkan Node terlebih dahulu")
        else:
            selected_node = st.selectbox("Select Node", node_names, key="reg_node")

            fc = st.selectbox("Function Code", ["01", "02", "03", "04"], key="reg_fc")
            addr = st.number_input("Address", value=0, key="reg_addr")
            qty = st.number_input("Quantity", value=1, key="reg_qty")
            dtype = st.selectbox(
                "Data Type",
                ["INT16", "UINT16", "INT32", "FLOAT32", "BOOL"],
                key="reg_dtype"
            )

            if st.button("💾 Add Register", key="reg_add"):
                data["registers"].append({
                    "node": selected_node,
                    "fc": fc,
                    "addr": addr,
                    "qty": qty,
                    "type": dtype,
                    "value": "-"
                })
                save_json(FILE_MODBUS, data)
                st.rerun()

    # ================= TABLE =================
    with col2:
        display = [{
            "Select": False,
            "Node": r.get("node", "-"),
            "FC": r["fc"],
            "Address": r["addr"],
            "Qty": r["qty"],
            "Type": r["type"],
            "Value": r.get("value", "-")
        } for r in data["registers"]]

        edited = st.data_editor(display, height=400, key="reg_table")

        # SELECT hanya untuk DELETE
        selected = [i for i, r in enumerate(edited) if r["Select"]]

        # ================= CONTROL BUTTON =================
        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button("🟢 Online", key="reg_online"):
                st.session_state.mb_running = True

        with c2:
            if st.button("🔴 Offline", key="reg_offline"):
                st.session_state.mb_running = False

        with c3:
            if st.button("🗑 Delete Selected", key="reg_delete"):
                for i in sorted(selected, reverse=True):
                    data["registers"].pop(i)
                save_json(FILE_MODBUS, data)
                st.rerun()

        # ================= STATUS =================
        if st.session_state.mb_running:
            st.success("🟢 STATUS: ONLINE (All Registers Realtime)")
        else:
            st.warning("🔴 STATUS: OFFLINE")

        # ================= REALTIME LOOP =================
        if st.session_state.mb_running:

            for i in range(len(data["registers"])):
                reg = data["registers"][i]
                node = next(
                    (n for n in data["nodes"] if n["name"] == reg["node"]),
                    None
                )

                if node:
                    data["registers"][i]["value"] = read_modbus(node, reg, data)
                else:
                    data["registers"][i]["value"] = "Node Not Found"

            save_json(FILE_MODBUS, data)

            time.sleep(data["scan_rate"] / 1000)
            st.rerun()