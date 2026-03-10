import streamlit as st
import pandas as pd

st.set_page_config(page_title="Championship Dashboard", layout="wide")

st.title("🏆 Championship Dashboard")

drivers = pd.DataFrame({
    "Position": [1, 2, 3, 4, 5],
    "Driver": ["Driver A", "Driver B", "Driver C", "Driver D", "Driver E"],
    "Team": ["Audi", "McLaren", "Mercedes", "Ferrari", "Aston Martin"],
    "Points": [25, 18, 15, 12, 10]
})

teams = pd.DataFrame({
    "Position": [1, 2, 3, 4, 5],
    "Team": ["Audi", "McLaren", "Mercedes", "Ferrari", "Aston Martin"],
    "Points": [35, 19, 12, 2, 15]
})

col1, col2 = st.columns(2)

with col1:
    st.subheader("Drivers' Championship")
    st.dataframe(drivers, use_container_width=True)

with col2:
    st.subheader("Constructors' Championship")
    st.dataframe(teams, use_container_width=True)
