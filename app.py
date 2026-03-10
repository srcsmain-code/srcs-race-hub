import streamlit as st
import pandas as pd

st.set_page_config(page_title="SRCS Race Hub", layout="wide")

st.title("🏁 SRCS Race Hub")
st.subheader("Sim Racing Championship Series – Race Analytics")

st.write("Welcome to the SRCS analytics dashboard.")

# Example standings data
data = {
    "Driver": ["Driver A", "Driver B", "Driver C"],
    "Team": ["Audi", "McLaren", "Mercedes"],
    "Points": [25, 18, 15]
}

df = pd.DataFrame(data)

st.header("Championship Standings")
st.dataframe(df)
