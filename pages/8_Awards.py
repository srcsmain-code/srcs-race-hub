import streamlit as st
import pandas as pd
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping
from engine.race_metrics import prepare_laps_dataframe
from utils.formatting import ms_to_laptime

st.set_page_config(page_title="Awards", layout="wide")

st.title("🏆 Awards")

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
selected_race_data = raw_race_data[selected_index]

if TEAM_MAP_FILE.exists():
    selected_results_df = apply_team_mapping(selected_results_df, TEAM_MAP_FILE)
else:
    selected_results_df["Team"] = "Unknown"

selected_results_df = selected_results_df.sort_values("Position").reset_index(drop=True)
selected_results_df["Positions Gained"] = (
    selected_results_df["GridPosition"] - selected_results_df["Position"]
)

laps_df = prepare_laps_dataframe(selected_race_data)

winner_row = selected_results_df.iloc[0]
pole_row = selected_results_df.sort_values("GridPosition").iloc[0]
biggest_mover_row = selected_results_df.sort_values("Positions Gained", ascending=False).iloc[0]

# Most consistent driver
most_consistent_driver = "-"
most_consistent_value = "-"

if not laps_df.empty:
    consistency_df = (
        laps_df.groupby("DriverName")["LapTime"]
        .std()
        .reset_index(name="StdDev")
        .fillna(0)
        .sort_values("StdDev", ascending=True)
        .reset_index(drop=True)
    )
    if not consistency_df.empty:
        most_consistent_driver = consistency_df.iloc[0]["DriverName"]
        most_consistent_value = ms_to_laptime(int(round(consistency_df.iloc[0]["StdDev"])))

# Top scoring team
team_points_df = (
    selected_results_df.groupby("Team", as_index=False)["Points"]
    .sum()
    .sort_values(["Points", "Team"], ascending=[False, True])
    .reset_index(drop=True)
)

top_team = "-"
top_team_points = 0
if not team_points_df.empty:
    top_team = team_points_df.iloc[0]["Team"]
    top_team_points = int(team_points_df.iloc[0]["Points"])

# Awards strip
st.subheader("Round Awards")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Race Winner", winner_row["DriverName"])
with c2:
    st.metric("Pole Award", pole_row["DriverName"])
with c3:
    st.metric("Fastest Lap Award", selected_summary["Fastest Lap Driver"])

c4, c5, c6 = st.columns(3)
with c4:
    st.metric("Biggest Mover", biggest_mover_row["DriverName"])
with c5:
    st.metric("Most Consistent", most_consistent_driver)
with c6:
    st.metric("Top Scoring Team", top_team)

st.caption(
    f"{selected_summary['Round']} • {selected_summary['Grand Prix']} • "
    f"{selected_summary['Track']} • {selected_summary['Session Type']}"
)

# Awards detail table
st.subheader("Awards Summary")

awards_df = pd.DataFrame([
    {
        "Award": "Race Winner",
        "Winner": winner_row["DriverName"],
        "Detail": f"P1 finish, {winner_row['Points']} point(s)"
    },
    {
        "Award": "Pole Award",
        "Winner": pole_row["DriverName"],
        "Detail": f"Started from P{int(pole_row['GridPosition'])}"
    },
    {
        "Award": "Fastest Lap Award",
        "Winner": selected_summary["Fastest Lap Driver"],
        "Detail": selected_summary["Fastest Lap Time"]
    },
    {
        "Award": "Biggest Mover",
        "Winner": biggest_mover_row["DriverName"],
        "Detail": f"{int(biggest_mover_row['Positions Gained'])} place(s) gained"
    },
    {
        "Award": "Most Consistent",
        "Winner": most_consistent_driver,
        "Detail": f"Lap-time std dev: {most_consistent_value}"
    },
    {
        "Award": "Top Scoring Team",
        "Winner": top_team,
        "Detail": f"{top_team_points} point(s)"
    },
])

st.dataframe(awards_df, use_container_width=True, hide_index=True)

# Podium spotlight
st.subheader("Podium Spotlight")

podium_df = selected_results_df.head(3)[[
    "Position", "DriverName", "Team", "Points"
]].copy()

podium_df.columns = ["Pos", "Driver", "Team", "Points"]
st.dataframe(podium_df, use_container_width=True, hide_index=True)

# Movers spotlight
st.subheader("Biggest Movers and Losers")

movers_df = selected_results_df[[
    "DriverName", "Team", "GridPosition", "Position", "Positions Gained"
]].copy()

movers_df.columns = ["Driver", "Team", "Grid", "Finish", "Net Gain/Loss"]
movers_df = movers_df.sort_values("Net Gain/Loss", ascending=False)

st.dataframe(movers_df, use_container_width=True, hide_index=True)

# Team awards breakdown
st.subheader("Team Awards Breakdown")

team_awards_df = team_points_df.copy()
team_awards_df["Position"] = team_awards_df.index + 1
team_awards_df = team_awards_df[["Position", "Team", "Points"]]
team_awards_df.columns = ["Pos", "Team", "Round Points"]

st.dataframe(team_awards_df, use_container_width=True, hide_index=True)

# Notes
st.subheader("Awards Notes")

st.write(
    "This page highlights the standout performers and team outcomes for the selected round, "
    "turning the race data into a clear post-race awards summary."
)
