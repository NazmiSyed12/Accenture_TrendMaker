import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="ControlPlane.ai — Consequence Layer",
    page_icon="🛡️",
    layout="wide"
)

# The actual prototype is index.html, unchanged — this file just embeds it
# so the whole thing can be hosted on Streamlit Community Cloud.
with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

components.html(html_content, height=2600, scrolling=True)
