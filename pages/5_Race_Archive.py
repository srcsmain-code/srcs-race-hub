import streamlit as st
import pandas as pd

st.set_page_config(page_title="Race Archive", layout="wide")

st.title("📅 Race Archive")

archive = pd.DataFrame({
    "Round": ["Round 1", "Round 2", "Round 3"],
    "Grand Prix": ["Australia", "Bahrain", "Miami"],
    "Winner": ["Driver A", "Driver B", "Driver C"],
    "Fastest Lap": ["Driver C", "Driver A", "Driver B"]
})

st.dataframe(archive, use_container_width=True)
