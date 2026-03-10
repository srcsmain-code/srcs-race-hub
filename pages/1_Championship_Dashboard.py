import streamlit as st
import pandas as pd
from pathlib import Path

from utils.formatting import ms_to_laptime, ms_to_racetime
from utils.data_loader import load_all_race_results
from utils.standings import (
    apply_team_mapping,
    calculate_driver_standings,
    calculate_team_standings,
    calculate_driver_progression,
    calculate_team_progression,
)

st.set_page_config(page_title="Championship Dashboard", layout="wide")

st.title("🏆 Championship Dashboard")

DATA_DIR = Path("data")
TEAM_MAP_FILE = DATA_DIR / "driver_team_map.csv"

if not DATA_DIR.exists():
    st.error("Data folder not found. Please create a data folder and upload race JSON files.")
    st.stop()

race_files, all_results, round_summaries, raw_race_data = load_all_race_results(DATA_DIR)

if not race_files:
    st.warning("No race JSON files found in the data folder yet.")
    st.stop()

if not all_results:
    st.warning("No usable race result data found.")
    st.stop()

season_results_df = pd.concat(all_results, ignore_index=True)

if TEAM_MAP_FILE.exists():
    season_results_df = apply_team_mapping(season_results_df, TEAM_MAP_FILE)
else:
    season_results_df["Team"] = "Unknown"

drivers_standings_df = calculate_driver_standings(season_results_df)
teams_standings_df = calculate_team_standings(season_results_df)

latest_round_df = season_results_df[season_results_df["Round"] == season_results_df["Round"].iloc[-1]].copy()
latest_summary = round_summaries[-1]

latest_display_df = latest_round_df[[
    "Position", "DriverName", "Team", "GridPosition", "NumLaps", "BestLap", "TotalTime", "Points"
]].copy()

latest_display_df.columns = ["Pos", "Driver", "Team", "Grid", "Laps", "Best Lap", "Race Time", "Points"]
latest_display_df["Best Lap"] = latest_display_df["Best Lap"].apply(ms_to_laptime)
latest_display_df["Race Time"] = latest_display_df["Race Time"].apply(ms_to_racetime)

top_col1, top_col2 = st.columns([2, 1])

with top_col1:
    st.subheader("Season Summary")
    stat1, stat2, stat3 = st.columns(3)
    with stat1:
        st.metric("Rounds Loaded", len(race_files))
    with stat2:
        st.metric("Latest Round", latest_summary["Round"])
    with stat3:
        st.metric("Latest GP", latest_summary["Grand Prix"])

with top_col2:
    st.subheader("Latest Fastest Lap")
    st.metric("Driver", latest_summary["Fastest Lap Driver"])
    st.caption(f"Time: {latest_summary['Fastest Lap Time']}")

stand_col1, stand_col2 = st.columns(2)

with stand_col1:
    st.subheader("Drivers' Championship")
    st.dataframe(drivers_standings_df, use_container_width=True, hide_index=True)

with stand_col2:
    st.subheader("Constructors' Championship")
    st.dataframe(teams_standings_df, use_container_width=True, hide_index=True)

st.subheader(f"Latest Round Results — {latest_summary['Round']}")
st.dataframe(latest_display_df, use_container_width=True, hide_index=True)

st.subheader("Drivers' Points Progression")
st.line_chart(calculate_driver_progression(season_results_df))

st.subheader("Teams' Points Progression")
st.line_chart(calculate_team_progression(season_results_df))

st.subheader("Latest Round Summary")
summary_df = pd.DataFrame([latest_summary])
st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.subheader("Round-by-Round Points")
round_points_df = season_results_df[["Round", "DriverName", "Team", "Points"]].copy()
round_points_df.columns = ["Round", "Driver", "Team", "Points"]
st.dataframe(round_points_df, use_container_width=True, hide_index=True)
