import streamlit as st
import pandas as pd
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping
from utils.formatting import ms_to_laptime, ms_to_racetime
from utils.style import apply_srcs_style
import streamlit as st

FAVICON = Path("../assets/SRCS_correct_favicon_256.png")

st.set_page_config(
    page_title="Overview",
    page_icon=str(FAVICON),
    layout="wide"
)
apply_srcs_style()

st.title("🏁 Overview")

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

selected_results_df["Positions Gained"] = (
    selected_results_df["GridPosition"] - selected_results_df["Position"]
)

selected_results_df = selected_results_df.sort_values("Position").reset_index(drop=True)

winner_row = selected_results_df.iloc[0]
pole_row = selected_results_df.sort_values("GridPosition").iloc[0]
podium_df = selected_results_df.head(3).copy()
biggest_mover_row = selected_results_df.sort_values("Positions Gained", ascending=False).iloc[0]

# Top summary metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Winner", winner_row["DriverName"])
with col2:
    st.metric("Pole", pole_row["DriverName"])
with col3:
    st.metric("Fastest Lap", selected_summary["Fastest Lap Driver"])
with col4:
    st.metric("Biggest Mover", biggest_mover_row["DriverName"])

st.caption(
    f"{selected_summary['Grand Prix']} • {selected_summary['Track']} • {selected_summary['Session Type']}"
)

# Podium
st.subheader("Podium")

podium_display_df = podium_df[[
    "Position", "DriverName", "Team", "Points", "BestLap", "TotalTime"
]].copy()

podium_display_df.columns = ["Pos", "Driver", "Team", "Points", "Best Lap", "Race Time"]
podium_display_df["Best Lap"] = podium_display_df["Best Lap"].apply(ms_to_laptime)
podium_display_df["Race Time"] = podium_display_df["Race Time"].apply(ms_to_racetime)

st.dataframe(podium_display_df, use_container_width=True, hide_index=True)

# Classification
st.subheader("Classification")

classification_df = selected_results_df[[
    "Position", "DriverName", "Team", "GridPosition", "NumLaps",
    "BestLap", "TotalTime", "Points", "Positions Gained"
]].copy()

classification_df.columns = [
    "Pos", "Driver", "Team", "Grid", "Laps",
    "Best Lap", "Race Time", "Points", "Pos Gained"
]
classification_df["Best Lap"] = classification_df["Best Lap"].apply(ms_to_laptime)
classification_df["Race Time"] = classification_df["Race Time"].apply(ms_to_racetime)

st.dataframe(classification_df, use_container_width=True, hide_index=True)

# Grid vs Finish
st.subheader("Grid vs Finish")

grid_finish_df = selected_results_df[[
    "DriverName", "GridPosition", "Position"
]].copy()

grid_finish_df.columns = ["Driver", "Grid", "Finish"]
st.dataframe(grid_finish_df, use_container_width=True, hide_index=True)

# Points scored this round
st.subheader("Points Scored This Round")

points_df = selected_results_df[selected_results_df["Points"] > 0][[
    "DriverName", "Points"
]].copy()

points_df.columns = ["Driver", "Points"]
points_df = points_df.sort_values("Points", ascending=False).set_index("Driver")

st.bar_chart(points_df)

# Movers
st.subheader("Positions Gained / Lost")

movers_df = selected_results_df[[
    "DriverName", "GridPosition", "Position", "Positions Gained"
]].copy()

movers_df.columns = ["Driver", "Grid", "Finish", "Net Gain/Loss"]
st.dataframe(movers_df, use_container_width=True, hide_index=True)
