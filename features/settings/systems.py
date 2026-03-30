import streamlit as st
from .system_location import render_location
from .system_network  import render_network
from .system_gateway  import render_gateway
from .system_external import render_external
from .gateway_native import render_gateway_native

def render_system_settings():
    st.title("⚙️ System Settings")

    colL, colR = st.columns(2)

    with colL:
        render_location()

    with colR:
        render_network()

    st.divider()
    render_gateway()

    st.divider()
    render_external()

    st.divider()
    render_gateway_native()


if __name__ == "__main__":
    render_system_settings()