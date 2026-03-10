import streamlit as st

st.set_page_config(
    page_title="SRCS Race Hub",
    page_icon="🏁",
    layout="wide"
)

st.title("🏁 SRCS Race Hub")
st.subheader("Sim Racing Championship Series – Race Analytics")

st.markdown("""
## Home

Welcome to the SRCS Race Hub.

Use the sidebar to navigate between pages:
- Championship Dashboard
- Race Analysis
- Driver Performance
- Team Battle
- Race Archive
""")

st.info("This is the home page of the SRCS analytics platform.")

st.sidebar.title("Home")
