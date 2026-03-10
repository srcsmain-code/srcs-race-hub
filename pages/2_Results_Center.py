import streamlit as st
import pandas as pd
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping
from utils.formatting import ms_to_laptime, ms_to_racetime
from utils.style import apply_srcs_style

st.set_page_config(page_title="Results Center", layout="wide")
apply_srcs_style()

st.title("🏁 Results Center")

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

winner_row = selected_results_df.iloc[0]
pole_row = selected_results_df.sort_values("GridPosition").iloc[0]
fastest_lap_driver = selected_summary["Fastest Lap Driver"]

# Summary strip
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Winner", winner_row["DriverName"])
with col2:
    st.metric("Pole", pole_row["DriverName"])
with col3:
    st.metric("Fastest Lap", fastest_lap_driver)
with col4:
    st.metric("Classified Drivers", len(selected_results_df))

st.caption(
    f"{selected_summary['Round']} • {selected_summary['Grand Prix']} • "
    f"{selected_summary['Track']} • {selected_summary['Session Type']}"
)

# Official classification
st.subheader("Official Classification")

classification_df = selected_results_df[[
    "Position",
    "DriverName",
    "Team",
    "GridPosition",
    "NumLaps",
    "BestLap",
    "TotalTime",
    "Points",
    "Positions Gained"
]].copy()

classification_df.columns = [
    "Pos",
    "Driver",
    "Team",
    "Grid",
    "Laps",
    "Best Lap",
    "Race Time",
    "Points",
    "Pos Gained"
]

classification_df["Best Lap"] = classification_df["Best Lap"].apply(ms_to_laptime)
classification_df["Race Time"] = classification_df["Race Time"].apply(ms_to_racetime)

st.dataframe(classification_df, use_container_width=True, hide_index=True)

# Result summary cards
st.subheader("Race Result Summary")

summary_col1, summary_col2 = st.columns(2)

with summary_col1:
    summary_table = pd.DataFrame([
        {"Item": "Winner", "Value": winner_row["DriverName"]},
        {"Item": "Pole", "Value": pole_row["DriverName"]},
        {"Item": "Fastest Lap Driver", "Value": selected_summary["Fastest Lap Driver"]},
        {"Item": "Fastest Lap Time", "Value": selected_summary["Fastest Lap Time"]},
    ])
    st.dataframe(summary_table, use_container_width=True, hide_index=True)

with summary_col2:
    top3_df = selected_results_df.head(3)[["Position", "DriverName", "Team", "Points"]].copy()
    top3_df.columns = ["Pos", "Driver", "Team", "Points"]
    st.dataframe(top3_df, use_container_width=True, hide_index=True)

# Grid vs Finish
st.subheader("Grid vs Finish")

grid_finish_df = selected_results_df[[
    "DriverName", "GridPosition", "Position", "Positions Gained"
]].copy()

grid_finish_df.columns = ["Driver", "Grid", "Finish", "Net Gain/Loss"]
st.dataframe(grid_finish_df, use_container_width=True, hide_index=True)

# Points awarded
st.subheader("Points Awarded")

points_df = selected_results_df[selected_results_df["Points"] > 0][[
    "DriverName", "Points"
]].copy()

points_df.columns = ["Driver", "Points"]
points_df = points_df.sort_values("Points", ascending=False).set_index("Driver")

st.bar_chart(points_df)

# Team result breakdown for the round
st.subheader("Team Results This Round")

team_round_df = (
    selected_results_df.groupby("Team", as_index=False)["Points"]
    .sum()
    .sort_values(["Points", "Team"], ascending=[False, True])
    .reset_index(drop=True)
)

team_round_df["Pos"] = team_round_df.index + 1
team_round_df = team_round_df[["Pos", "Team", "Points"]]

st.dataframe(team_round_df, use_container_width=True, hide_index=True)

# Movers
st.subheader("Positions Gained / Lost")

movers_df = selected_results_df[[
    "DriverName", "Team", "GridPosition", "Position", "Positions Gained"
]].copy()

movers_df.columns = ["Driver", "Team", "Grid", "Finish", "Net Gain/Loss"]
movers_df = movers_df.sort_values("Net Gain/Loss", ascending=False)

st.dataframe(movers_df, use_container_width=True, hide_index=True)
