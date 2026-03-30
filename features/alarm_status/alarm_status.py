import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


# =========================
# FUNCTION DONUT CHART
# =========================
def donut_chart(value_dict):
    labels = list(value_dict.keys())
    values = list(value_dict.values())

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.7
    )])

    fig.update_layout(
        showlegend=True,
        margin=dict(t=10, b=10, l=10, r=10),
        height=250
    )

    return fig


# =========================
# MAIN RENDER FUNCTION
# =========================
def render_alarm_status():

    st.markdown("""
    <style>
    .card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
    }
    .title {
        font-size: 16px;
        font-weight: 600;
        color: #444;
    }
    .subtitle {
        font-size: 12px;
        color: #888;
    }
    .center {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🚨 Alarm Status")

    # =========================
    # DATA (SIMULASI)
    # =========================
    active_alarm = {
        "Hi Alarm": 1,
        "Alert": 1,
        "High Humidity": 1
    }

    battery_status = {
        "Critical": 8,
        "Low": 3,
        "Good": 39,
        "Not Supported": 2
    }

    call_status = {
        "> 24 hours late": 6,
        "< 24 hours late": 2,
        "On-Time": 44
    }

    impulses = {
        "s5 (Critical)": 3,
        "s4 (Severe)": 2,
        "s3 (Major)": 2,
        "s2 (Moderate)": 2,
        "s1 (Minor)": 1,
        "None": 1
    }

    days = ["Nov 02", "Nov 03", "Nov 04", "Nov 05", "Nov 06", "Nov 07", "Nov 08"]
    alert = [1, 1, 2, 3, 3, 2, 1]
    low_alarm = [0, 1, 1, 0, 0, 0, 0]
    hi_alarm = [0, 1, 0, 0, 0, 0, 0]

    # =========================
    # LAYOUT
    # =========================
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="title">🔔 Active Alarms</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Current active alarms</div>', unsafe_allow_html=True)

        st.plotly_chart(donut_chart(active_alarm), use_container_width=True)
        st.markdown('<h2 class="center">3</h2>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="title">📊 Alarm Activation History (7 Days)</div>', unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_bar(name="Alert", x=days, y=alert)
        fig.add_bar(name="Lo Alarm", x=days, y=low_alarm)
        fig.add_bar(name="Hi Alarm", x=days, y=hi_alarm)

        fig.update_layout(barmode='stack', height=300)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    col3, col4, col5 = st.columns(3)

    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="title">🔋 Battery Status</div>', unsafe_allow_html=True)
        st.plotly_chart(donut_chart(battery_status), use_container_width=True)
        st.markdown('<h2 class="center">52</h2>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="title">📞 Call Status</div>', unsafe_allow_html=True)
        st.plotly_chart(donut_chart(call_status), use_container_width=True)
        st.markdown('<h2 class="center">52</h2>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col5:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="title">⚡ Sites With Impulses</div>', unsafe_allow_html=True)
        st.plotly_chart(donut_chart(impulses), use_container_width=True)
        st.markdown('<h2 class="center">11</h2>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)