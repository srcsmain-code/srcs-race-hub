import streamlit as st
import pandas as pd

st.set_page_config(page_title="Race Analysis", layout="wide")

st.title("📊 Race Analysis")

lap_data = pd.DataFrame({
    "Lap": [1, 2, 3, 4, 5],
    "Driver A": [89.2, 88.7, 88.9, 88.4, 88.6],
    "Driver B": [90.1, 89.5, 89.2, 89.0, 88.9]
})

st.subheader("Lap Time Trend")
st.line_chart(lap_data.set_index("Lap"))

st.subheader("Key Notes")
st.write("This page will later show real lap times, fastest laps, position changes, and race trends from your uploaded JSON files.")
