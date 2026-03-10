import streamlit as st
import pandas as pd
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping

st.set_page_config(page_title="Position Tracker", layout="wide")

st.title("📍 Position Tracker")

DATA_DIR = Path("data")
TEAM_MAP_FILE = DATA_DIR / "driver_team_map.csv"

if not DATA_DIR.exists():
    st.error("Data folder not found.")
    st.stop()

race_files, all_results, round_summaries, raw_race_data = load_all_race_results(DATA_DIR)

if not race_files or not all_results:
    st.warning("No race data available yet.")
    st.stop()

round_options = [summary["Round"] for summary in round_summaries]
selected_round = st.selectbox("Select Round", round_options, index=len(round_options) - 1)

selected_index = round_options.index(selected_round)
selected_results_df = all_results[selected_index].copy()
selected_summary = round_summaries[selected_index]

if TEAM_MAP_FILE.exists():
    selected_results_df = apply_team_mapping(selected_results_df, TEAM_MAP_FILE)
else:
    selected_results_df["Team"] = "Unknown"

selected_results_df = selected_results_df.sort_values("Position").reset_index(drop=True)

selected_results_df["Positions Gained"] = (
    selected_results_df["GridPosition"] - selected_results_df["Position"]
)

selected_results_df["Movement"] = selected_results_df["Positions Gained"].apply(
    lambda x: "Gained" if x > 0 else ("Lost" if x < 0 else "No Change")
)

biggest_mover_row = selected_results_df.sort_values("Positions Gained", ascending=False).iloc[0]
biggest_loser_row = selected_results_df.sort_values("Positions Gained", ascending=True).iloc[0]

# Top summary
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Round", selected_summary["Round"])
with col2:
    st.metric("Biggest Mover", biggest_mover_row["DriverName"])
with col3:
    st.metric("Positions Gained", int(biggest_mover_row["Positions Gained"]))
with col4:
    st.metric("Biggest Loser", biggest_loser_row["DriverName"])

st.caption(
    f"{selected_summary['Grand Prix']} • {selected_summary['Track']} • {selected_summary['Session Type']}"
)

# Main tracker table
st.subheader("Grid vs Finish Tracker")

tracker_df = selected_results_df[[
    "DriverName",
    "Team",
    "GridPosition",
    "Position",
    "Positions Gained",
    "Movement",
    "Points"
]].copy()

tracker_df.columns = [
    "Driver",
    "Team",
    "Grid",
    "Finish",
    "Net Gain/Loss",
    "Movement",
    "Points"
]

st.dataframe(tracker_df, use_container_width=True, hide_index=True)

# Position change chart
st.subheader("Position Change Chart")

position_chart_df = selected_results_df[[
    "DriverName",
    "Positions Gained"
]].copy()

position_chart_df.columns = ["Driver", "Net Gain/Loss"]
position_chart_df = position_chart_df.set_index("Driver")

st.bar_chart(position_chart_df)

# Movers table
st.subheader("Biggest Movers")

movers_df = selected_results_df.sort_values("Positions Gained", ascending=False)[[
    "DriverName",
    "Team",
    "GridPosition",
    "Position",
    "Positions Gained"
]].copy()

movers_df.columns = ["Driver", "Team", "Grid", "Finish", "Net Gain/Loss"]

st.dataframe(movers_df, use_container_width=True, hide_index=True)

# Grid and finish comparison
st.subheader("Grid and Finish Comparison")

comparison_df = selected_results_df[[
    "DriverName",
    "GridPosition",
    "Position"
]].copy()

comparison_df.columns = ["Driver", "Grid", "Finish"]

st.dataframe(comparison_df, use_container_width=True, hide_index=True)

# Notes
st.subheader("Tracker Notes")

st.write(
    "This page compares starting position versus finishing position for each driver, "
    "showing who moved forward through the field and who lost places during the race."
)
