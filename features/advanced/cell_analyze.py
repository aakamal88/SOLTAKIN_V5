import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# =========================
# DATA
# =========================
cell_no = [1, 2, 3]

soc_list = [99.1, 88.2, 76.5]
soh_list = [93.5, 90.1, 85.0]
voltage_list = [12.29, 12.10, 11.95]
current_list = [0.0, 1.2, -0.5]
temp_list = [-3.0, 25.0, 30.5]
capacity_list = [60.2, 55.0, 48.3]
uptime_list = [3, 10, 25]

history_voltage = [
    [12.1, 12.2, 12.3, 12.25, 12.29],
    [12.0, 12.1, 12.15, 12.1, 12.10],
    [11.8, 11.9, 11.95, 11.9, 11.95]
]

history_soc = [
    [98, 99, 99.1, 99.1, 99.1],
    [85, 87, 88, 88.2, 88.2],
    [70, 72, 74, 75, 76.5]
]

history_soh = [
    [95, 94, 93.5, 93.5, 93.5],
    [92, 91, 90.5, 90.1, 90.1],
    [88, 87, 86, 85.5, 85.0]
]

history_uptime = [
    [0,1,2,3],
    [0,5,8,10],
    [0,10,20,25]
]

i = 0

# =========================
# STYLE (FIX TOTAL)
# =========================
st.markdown("""
<style>

/* GLOBAL */
body {
    background-color:#dcdcdc;
}

/* CONTAINER */
.block-container {
    max-width: 1200px;
    padding-top: 5px;
}

/* MAIN CARD */
.main-card {
    background:#c9ced6;
    padding:12px;
    border-radius:12px;
    margin-bottom:12px;
}

/* MINI CARD */
.mini-card {
    background:#b8bec7;
    padding:6px;
    border-radius:10px;
}

/* TITLE */
.title {
    font-size:18px;
    font-weight:600;
    color:#1f2933;
    margin-bottom:8px;
}

/* HILANGKAN GAP STREAMLIT */
div[data-testid="stVerticalBlock"] > div {
    gap: 0.6rem;
}

/* FIX PLOTLY POSISI */
.js-plotly-plot {
    margin-top: -25px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# GAUGE FIX CENTER
# =========================
def gauge(value, title, unit, min_val, max_val, color):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,

        number={
            'suffix': f" {unit}",
            'font': {'size': 16, 'color': "#1f2933"}
        },

        title={
            'text': title,
            'font': {'size': 12, 'color': "#374151"}
        },

        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': color},
            'bgcolor': "#b8bec7",
            'borderwidth': 0,
            'steps': [
                {'range': [min_val, max_val], 'color': "#d1d5db"}
            ]
        }
    ))

    fig.update_layout(
        height=120,
        margin=dict(l=10, r=10, t=10, b=0),
        paper_bgcolor="#b8bec7",
        font=dict(color="#1f2933")
    )

    return fig

# =========================
# MINI CHART FIX
# =========================
def mini_chart(data, title, unit):

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        y=data,
        mode='lines',
        line=dict(color="#f59e0b", width=2)
    ))

    fig.update_layout(
        title=dict(
            text=f"{title}<br><b>{data[-1]} {unit}</b>",
            x=0.02
        ),
        height=160,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="#b8bec7",
        plot_bgcolor="#b8bec7",
        font=dict(color="#1f2933"),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )

    return fig

# =========================
# UI
# =========================
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.markdown(f"<div class='title'>Cell No : {cell_no[i]}</div>", unsafe_allow_html=True)

# GAUGE
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("<div class='mini-card'>", unsafe_allow_html=True)
    st.plotly_chart(gauge(soc_list[i], "Batt. SOC", "%", 0, 100, "#4caf50"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='mini-card'>", unsafe_allow_html=True)
    st.plotly_chart(gauge(soh_list[i], "Batt. SOH", "%", 0, 100, "#3b82f6"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown("<div class='mini-card'>", unsafe_allow_html=True)
    st.plotly_chart(gauge(voltage_list[i], "Batt. Volt", "Volt", 0, 15, "#22c55e"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

c4, c5, c6 = st.columns(3)

with c4:
    st.markdown("<div class='mini-card'>", unsafe_allow_html=True)
    st.plotly_chart(gauge(current_list[i], "Batt. Current", "A", -10, 10, "#60a5fa"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c5:
    st.markdown("<div class='mini-card'>", unsafe_allow_html=True)
    st.plotly_chart(gauge(temp_list[i], "Batt. Temp", "°C", -20, 60, "#60a5fa"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c6:
    st.markdown("<div class='mini-card'>", unsafe_allow_html=True)
    st.plotly_chart(gauge(capacity_list[i], "Battery Ah Left", "Ah", 0, 100, "#60a5fa"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# CHART
c7, c8 = st.columns(2)

with c7:
    st.markdown("<div class='mini-card'>", unsafe_allow_html=True)
    st.plotly_chart(mini_chart(history_voltage[i], "Battery Voltage", "Volt"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c8:
    st.markdown("<div class='mini-card'>", unsafe_allow_html=True)
    st.plotly_chart(mini_chart(history_uptime[i], "Battery Uptime", "s"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

c9, c10 = st.columns(2)

with c9:
    st.markdown("<div class='mini-card'>", unsafe_allow_html=True)
    st.plotly_chart(mini_chart(history_soc[i], "Battery SOC", "%"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c10:
    st.markdown("<div class='mini-card'>", unsafe_allow_html=True)
    st.plotly_chart(mini_chart(history_soh[i], "Batt. SOH", "%"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)