import streamlit as st
import pandas as pd

st.set_page_config(page_title="Team Battle", layout="wide")

st.title("🏎 Team Battle")

team_data = pd.DataFrame({
    "Round": ["Round 1", "Round 2", "Round 3"],
    "Audi": [35, 28, 32],
    "McLaren": [19, 24, 18],
    "Mercedes": [12, 15, 20]
})

st.subheader("Team Points by Round")
st.line_chart(team_data.set_index("Round"))
