import streamlit as st
import pandas as pd
from pathlib import Path

from utils.data_loader import load_all_race_results
from utils.standings import apply_team_mapping
from utils.formatting import ms_to_laptime

st.set_page_config(page_title="Driver Performance", layout="wide")

st.title("👤 Driver Performance")

DATA_DIR = Path("data")
TEAM_MAP_FILE = DATA_DIR / "driver_team_map.csv"

if not DATA_DIR.exists():
    st.error("Data folder not found.")
    st.stop()

race_files, all_results, round_summaries, raw_race_data = load_all_race_results(DATA_DIR)

if not race_files or not all_results:
    st.warning("No race data available yet.")
    st.stop()

season_results_df = pd.concat(all_results, ignore_index=True)

if TEAM_MAP_FILE.exists():
    season_results_df = apply_team_mapping(season_results_df, TEAM_MAP_FILE)
else:
    season_results_df["Team"] = "Unknown"

drivers = sorted(season_results_df["DriverName"].unique().tolist())
selected_driver = st.selectbox("Select Driver", drivers)

driver_results_df = season_results_df[season_results_df["DriverName"] == selected_driver].copy()
driver_results_df = driver_results_df.sort_values("Round")

if driver_results_df.empty:
    st.warning("No data available for this driver.")
    st.stop()

# Season summary calculations
championship_df = (
    season_results_df.groupby("DriverName", as_index=False)["Points"]
    .sum()
    .sort_values(["Points", "DriverName"], ascending=[False, True])
    .reset_index(drop=True)
)
championship_df["Champ Pos"] = championship_df.index + 1

driver_champ_pos = championship_df.loc[
    championship_df["DriverName"] == selected_driver, "Champ Pos"
].iloc[0]

total_points = int(driver_results_df["Points"].sum())
best_finish = int(driver_results_df["Position"].min())
avg_finish = round(driver_results_df["Position"].mean(), 2)
rounds_entered = int(driver_results_df["Round"].nunique())

# Fastest laps count
fastest_lap_count = 0
for summary in round_summaries:
    if summary["Fastest Lap Driver"] == selected_driver:
        fastest_lap_count += 1

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("Championship Pos", driver_champ_pos)
with col2:
    st.metric("Total Points", total_points)
with col3:
    st.metric("Best Finish", best_finish)
with col4:
    st.metric("Avg Finish", avg_finish)
with col5:
    st.metric("Fastest Laps", fastest_lap_count)
with col6:
    st.metric("Rounds Entered", rounds_entered)

st.subheader("Results Trend")

results_trend_df = driver_results_df[["Round", "Position", "Points"]].copy()
results_trend_df = results_trend_df.set_index("Round")
st.line_chart(results_trend_df)

st.subheader("Round-by-Round Breakdown")

breakdown_df = driver_results_df[[
    "Round", "Grand Prix", "Team", "Position", "GridPosition", "Points", "BestLap", "TotalTime"
]].copy()

breakdown_df["BestLap"] = breakdown_df["BestLap"].apply(ms_to_laptime)
breakdown_df.columns = [
    "Round", "Grand Prix", "Team", "Finish", "Grid", "Points", "Best Lap", "Race Time (raw ms)"
]

st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

st.subheader("Season Points by Round")

points_by_round_df = driver_results_df[["Round", "Points"]].copy().set_index("Round")
st.bar_chart(points_by_round_df)

st.subheader("Driver Notes")

st.write(
    f"{selected_driver} has scored {total_points} points across {rounds_entered} round(s), "
    f"with a best finish of P{best_finish} and {fastest_lap_count} fastest lap(s)."
)
