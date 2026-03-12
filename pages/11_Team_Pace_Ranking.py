import streamlit as st
import pandas as pd
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping
from engine.race_metrics import prepare_laps_dataframe
from utils.formatting import ms_to_laptime
from utils.style import apply_srcs_style

st.set_page_config(page_title="Team Pace Ranking", page_icon="🏁", layout="wide")
apply_srcs_style()

st.markdown("""
<div class="srcs-hero">
    <div class="srcs-hero-title">TEAM PACE RANKING</div>
    <div class="srcs-hero-subtitle">Season-wide team pace leaderboard based on official lap data</div>
</div>
""", unsafe_allow_html=True)

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

# -----------------------------------
# Build season laps dataframe
# -----------------------------------
season_laps = []

for results_df, race_data, round_summary in zip(all_results, raw_race_data, round_summaries):
    laps_df = prepare_laps_dataframe(race_data)
    if laps_df.empty:
        continue

    round_name = round_summary["Round"]
    laps_df["Round"] = round_name

    round_team_map = season_results_df[
        season_results_df["Round"] == round_name
    ][["Round", "DriverName", "Team"]].drop_duplicates()

    laps_df = laps_df.merge(
        round_team_map,
        on=["Round", "DriverName"],
        how="left"
    )

    laps_df["Team"] = laps_df["Team"].fillna("Unknown")
    season_laps.append(laps_df)

if not season_laps:
    st.warning("No valid lap data available yet.")
    st.stop()

season_laps_df = pd.concat(season_laps, ignore_index=True)

# -----------------------------------
# Filters
# -----------------------------------
st.markdown('<div class="srcs-section">Ranking Filters</div>', unsafe_allow_html=True)

round_options = ["Full Season"] + [summary["Round"] for summary in round_summaries]
team_options = ["All Teams"] + sorted(season_laps_df["Team"].dropna().unique().tolist())

f1, f2, f3 = st.columns(3)

with f1:
    selected_round = st.selectbox("Scope", round_options)

with f2:
    selected_team_filter = st.selectbox("Team Filter", team_options)

with f3:
    min_laps = st.slider("Minimum Laps Counted", min_value=1, max_value=100, value=8)

filtered_laps_df = season_laps_df.copy()

if selected_round != "Full Season":
    filtered_laps_df = filtered_laps_df[filtered_laps_df["Round"] == selected_round].copy()

if selected_team_filter != "All Teams":
    filtered_laps_df = filtered_laps_df[filtered_laps_df["Team"] == selected_team_filter].copy()

if filtered_laps_df.empty:
    st.warning("No lap data available for the selected filters.")
    st.stop()

# -----------------------------------
# Team pace calculations
# -----------------------------------
team_pace_df = (
    filtered_laps_df.groupby("Team", as_index=False)
    .agg(
        DriversUsed=("DriverName", "nunique"),
        Rounds=("Round", "nunique"),
        LapsCounted=("LapTime", "count"),
        BestLapMs=("LapTime", "min"),
        AverageLapMs=("LapTime", "mean"),
        MedianLapMs=("LapTime", "median"),
        StdDevMs=("LapTime", "std"),
    )
)

team_pace_df["StdDevMs"] = team_pace_df["StdDevMs"].fillna(0)
team_pace_df = team_pace_df[team_pace_df["LapsCounted"] >= min_laps].copy()

if team_pace_df.empty:
    st.warning("No teams meet the minimum lap requirement.")
    st.stop()

team_pace_df = team_pace_df.sort_values(["AverageLapMs", "Team"], ascending=[True, True]).reset_index(drop=True)
team_pace_df["Pace Rank"] = team_pace_df.index + 1

bestlap_rank_df = team_pace_df.sort_values(["BestLapMs", "Team"], ascending=[True, True]).reset_index(drop=True)
bestlap_rank_df["Best Lap Rank"] = bestlap_rank_df.index + 1

consistency_rank_df = team_pace_df.sort_values(["StdDevMs", "Team"], ascending=[True, True]).reset_index(drop=True)
consistency_rank_df["Consistency Rank"] = consistency_rank_df.index + 1

team_pace_df = team_pace_df.merge(
    bestlap_rank_df[["Team", "Best Lap Rank"]],
    on="Team",
    how="left"
)

team_pace_df = team_pace_df.merge(
    consistency_rank_df[["Team", "Consistency Rank"]],
    on="Team",
    how="left"
)

fastest_avg = team_pace_df["AverageLapMs"].min()
team_pace_df["DeltaToFastestAvgMs"] = (team_pace_df["AverageLapMs"] - fastest_avg).round().astype(int)

team_pace_df["Best Lap"] = team_pace_df["BestLapMs"].round().astype(int).apply(ms_to_laptime)
team_pace_df["Average Lap"] = team_pace_df["AverageLapMs"].round().astype(int).apply(ms_to_laptime)
team_pace_df["Median Lap"] = team_pace_df["MedianLapMs"].round().astype(int).apply(ms_to_laptime)
team_pace_df["Consistency"] = team_pace_df["StdDevMs"].round().astype(int).apply(ms_to_laptime)
team_pace_df["Delta to Fastest Avg"] = team_pace_df["DeltaToFastestAvgMs"].apply(
    lambda x: "0:00.000" if int(x) == 0 else ms_to_laptime(int(x))
)

# -----------------------------------
# Headlines
# -----------------------------------
st.markdown('<div class="srcs-section">Team Pace Headlines</div>', unsafe_allow_html=True)

top_pace_team = team_pace_df.iloc[0]["Team"]
top_bestlap_team = team_pace_df.sort_values(["BestLapMs", "Team"], ascending=[True, True]).iloc[0]["Team"]
top_consistency_team = team_pace_df.sort_values(["StdDevMs", "Team"], ascending=[True, True]).iloc[0]["Team"]

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Fastest Average Pace", top_pace_team)
with c2:
    st.metric("Best One-Lap Pace", top_bestlap_team)
with c3:
    st.metric("Most Consistent", top_consistency_team)
with c4:
    st.metric("Teams Ranked", len(team_pace_df))

# -----------------------------------
# Main ranking table
# -----------------------------------
st.markdown('<div class="srcs-section">Team Pace Ranking Table</div>', unsafe_allow_html=True)

display_df = team_pace_df[[
    "Pace Rank",
    "Team",
    "DriversUsed",
    "Rounds",
    "LapsCounted",
    "Average Lap",
    "Delta to Fastest Avg",
    "Best Lap",
    "Consistency",
    "Best Lap Rank",
    "Consistency Rank",
]].copy()

display_df.columns = [
    "Pos",
    "Team",
    "Drivers Used",
    "Rounds",
    "Laps Counted",
    "Average Lap",
    "Delta",
    "Best Lap",
    "Consistency",
    "Best Lap Rank",
    "Consistency Rank",
]

st.dataframe(display_df, use_container_width=True, hide_index=True)

# -----------------------------------
# Average pace chart
# -----------------------------------
st.markdown('<div class="srcs-section">Average Pace Delta Chart</div>', unsafe_allow_html=True)

pace_chart_df = team_pace_df[["Team", "DeltaToFastestAvgMs"]].copy()
pace_chart_df.columns = ["Team", "Delta to Fastest Average (ms)"]
pace_chart_df = pace_chart_df.sort_values("Delta to Fastest Average (ms)", ascending=False).set_index("Team")

st.bar_chart(pace_chart_df)

# -----------------------------------
# Best lap chart
# -----------------------------------
st.markdown('<div class="srcs-section">Best Lap Ranking Chart</div>', unsafe_allow_html=True)

best_chart_df = team_pace_df[["Team", "BestLapMs"]].copy()
best_chart_df.columns = ["Team", "Best Lap (ms)"]
best_chart_df = best_chart_df.sort_values("Best Lap (ms)", ascending=False).set_index("Team")

st.bar_chart(best_chart_df)

# -----------------------------------
# Consistency chart
# -----------------------------------
st.markdown('<div class="srcs-section">Consistency Chart</div>', unsafe_allow_html=True)

consistency_chart_df = team_pace_df[["Team", "StdDevMs"]].copy()
consistency_chart_df.columns = ["Team", "Std Dev (ms)"]
consistency_chart_df = consistency_chart_df.sort_values("Std Dev (ms)", ascending=False).set_index("Team")

st.bar_chart(consistency_chart_df)

# -----------------------------------
# Team detail block
# -----------------------------------
st.markdown('<div class="srcs-section">Team Detail</div>', unsafe_allow_html=True)

selected_detail_team = st.selectbox(
    "Select Team for Detail",
    sorted(team_pace_df["Team"].tolist()),
    key="team_pace_detail_team"
)

team_detail_laps_df = filtered_laps_df[filtered_laps_df["Team"] == selected_detail_team].copy()

if not team_detail_laps_df.empty:
    driver_detail_df = (
        team_detail_laps_df.groupby("DriverName", as_index=False)
        .agg(
            LapsCounted=("LapTime", "count"),
            BestLapMs=("LapTime", "min"),
            AverageLapMs=("LapTime", "mean"),
            MedianLapMs=("LapTime", "median"),
            StdDevMs=("LapTime", "std"),
        )
    )

    driver_detail_df["StdDevMs"] = driver_detail_df["StdDevMs"].fillna(0)
    driver_detail_df["Best Lap"] = driver_detail_df["BestLapMs"].round().astype(int).apply(ms_to_laptime)
    driver_detail_df["Average Lap"] = driver_detail_df["AverageLapMs"].round().astype(int).apply(ms_to_laptime)
    driver_detail_df["Median Lap"] = driver_detail_df["MedianLapMs"].round().astype(int).apply(ms_to_laptime)
    driver_detail_df["Consistency"] = driver_detail_df["StdDevMs"].round().astype(int).apply(ms_to_laptime)

    driver_detail_display_df = driver_detail_df[[
        "DriverName",
        "LapsCounted",
        "Best Lap",
        "Average Lap",
        "Median Lap",
        "Consistency"
    ]].copy()

    driver_detail_display_df.columns = [
        "Driver",
        "Laps Counted",
        "Best Lap",
        "Average Lap",
        "Median Lap",
        "Consistency"
    ]

    st.dataframe(driver_detail_display_df, use_container_width=True, hide_index=True)

# -----------------------------------
# Notes
# -----------------------------------
st.markdown('<div class="srcs-section">Pace Notes</div>', unsafe_allow_html=True)

st.write(
    "This page ranks teams by pace using official lap data. "
    "Average lap time is used as the primary ranking metric, while best lap and consistency "
    "help separate one-lap speed from repeatable race pace at team level."
)

st.caption("SRCS Team Pace Ranking — team-wide pace intelligence.")
