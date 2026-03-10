import streamlit as st
import pandas as pd

st.set_page_config(page_title="Driver Performance", layout="wide")

st.title("👤 Driver Performance")

drivers = ["Driver A", "Driver B", "Driver C"]
selected_driver = st.selectbox("Select Driver", drivers)

data = pd.DataFrame({
    "Race": ["Round 1", "Round 2", "Round 3"],
    "Finishing Position": [1, 3, 2],
    "Points": [25, 15, 18]
})

st.subheader(f"Performance Summary: {selected_driver}")
st.dataframe(data, use_container_width=True)
st.bar_chart(data.set_index("Race")["Points"])
