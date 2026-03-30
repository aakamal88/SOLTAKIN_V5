import streamlit as st

from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

from .location_utils import load_json, FILE_GATEWAY

# ✅ AUTOREFRESH (EXTRAS)
try:
    from streamlit_extras.autorefresh import st_autorefresh
    AUTO_REFRESH = True
except:
    AUTO_REFRESH = False


# =========================
# CONSTANT
# =========================
START_ADDR = 0
QTY = 600
TOTAL_CELL = 100

BYTE_ORDER = Endian.BIG
WORD_ORDER = Endian.BIG


# =========================
# DECODE FLOAT32
# =========================
def decode_float32(registers):
    decoder = BinaryPayloadDecoder.fromRegisters(
        registers,
        byteorder=BYTE_ORDER,
        wordorder=WORD_ORDER
    )
    return round(decoder.decode_32bit_float(), 3)


# =========================
# READ MODBUS
# =========================
def read_modbus(ip, port, slave_id):
    try:
        client = ModbusTcpClient(ip, port=port, timeout=2)

        if not client.connect():
            return None, "❌ No Connection"

        all_data = []
        max_read = 120

        for start in range(START_ADDR, START_ADDR + QTY, max_read):
            qty = min(max_read, START_ADDR + QTY - start)

            rr = client.read_holding_registers(start, qty, slave=slave_id)

            if rr.isError():
                client.close()
                return None, f"❌ Read Error @ {start}"

            all_data.extend(rr.registers)

        client.close()
        return all_data, "✅ Connected"

    except Exception as e:
        return None, f"❌ {str(e)}"


# =========================
# PARSE DATA
# =========================
def parse_cells(data):
    cells = []

    for i in range(TOTAL_CELL):
        base = i * 6

        try:
            v = decode_float32([data[base], data[base + 1]])
            t = decode_float32([data[base + 2], data[base + 3]])
            l = decode_float32([data[base + 4], data[base + 5]])
        except:
            v, t, l = None, None, None

        cells.append({
            "Cell": i + 1,
            "Vcell": v,
            "Tcell": t,
            "Lcell": l
        })

    return cells


# =========================
# LOAD GATEWAY
# =========================
def load_gateways():
    gw = load_json(FILE_GATEWAY, {"controllers": []})
    return gw.get("controllers", [])


# =========================
# UI
# =========================
def render_gateway_native():
    st.subheader("🧩 Gateway Native (Cell Monitor)")

    controllers = load_gateways()

    if not controllers:
        st.warning("⚠️ Tidak ada Gateway di system_gateway")
        return

    # =========================
    # SELECT GATEWAY
    # =========================
    gateway_names = [c.get("name", f"Gateway {i}") for i, c in enumerate(controllers)]

    selected_name = st.selectbox("🔽 Select Gateway", gateway_names)

    selected_gateway = next(
        (c for c in controllers if c.get("name") == selected_name),
        None
    )

    if not selected_gateway:
        st.error("❌ Gateway tidak ditemukan")
        return

    # =========================
    # CONFIG
    # =========================
    ip = selected_gateway.get("ip", "")
    port = selected_gateway.get("port", 502)
    slave_id = selected_gateway.get("slave_id", 1)

    try:
        port = int(port)
    except:
        port = 502

    try:
        slave_id = int(slave_id)
    except:
        slave_id = 1

    st.caption(f"{selected_name} → {ip}:{port} | Slave: {slave_id} | FC03 | 100 Cell")

    # =========================
    # STATE
    # =========================
    if "gn_running" not in st.session_state:
        st.session_state.gn_running = False

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🟢 Online"):
            st.session_state.gn_running = True

    with col2:
        if st.button("🔴 Offline"):
            st.session_state.gn_running = False

    status_box = st.empty()
    table_box = st.empty()

    # =========================
    # RUN
    # =========================
    if st.session_state.gn_running:

        data, status = read_modbus(ip, port, slave_id)

        # =========================
        # STATUS
        # =========================
        if "❌" in status:
            status_box.error(status)
        else:
            status_box.success(status)

        # =========================
        # DEBUG INFO (WAJIB)
        # =========================
        st.write(f"DEBUG → Data length: {len(data) if data else 'None'}")

        # =========================
        # TABLE
        # =========================
        if data and len(data) > 0:
            cells = parse_cells(data)
            table_box.dataframe(cells, use_container_width=True)
        else:
            table_box.warning("⚠️ Data kosong / tidak terbaca")

        # =========================
        # AUTO REFRESH (PINDAH KE BAWAH)
        # =========================
        if AUTO_REFRESH:
            st_autorefresh(interval=1000, key="gn_refresh")
        else:
            import time
            time.sleep(1)
            st.rerun()