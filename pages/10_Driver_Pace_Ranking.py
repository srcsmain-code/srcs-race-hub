import streamlit as st
import pandas as pd
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping
from engine.race_metrics import prepare_laps_dataframe
from utils.formatting import ms_to_laptime
from utils.style import apply_srcs_style

st.set_page_config(page_title="Driver Pace Ranking", page_icon="⚡", layout="wide")
apply_srcs_style()

st.markdown("""
<div class="srcs-hero">
    <div class="srcs-hero-title">DRIVER PACE RANKING</div>
    <div class="srcs-hero-subtitle">Season-wide pace leaderboard based on lap performance</div>
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

    # Add round label
    laps_df["Round"] = round_name

    # Map team by round + driver
    round_team_map = season_results_df[season_results_df["Round"] == round_name][["Round", "DriverName", "Team"]].drop_duplicates()

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
    selected_team = st.selectbox("Team Filter", team_options)

with f3:
    min_laps = st.slider("Minimum Laps Counted", min_value=1, max_value=50, value=5)

filtered_laps_df = season_laps_df.copy()

if selected_round != "Full Season":
    filtered_laps_df = filtered_laps_df[filtered_laps_df["Round"] == selected_round].copy()

if selected_team != "All Teams":
    filtered_laps_df = filtered_laps_df[filtered_laps_df["Team"] == selected_team].copy()

if filtered_laps_df.empty:
    st.warning("No lap data available for the selected filters.")
    st.stop()

# -----------------------------------
# Pace calculations
# -----------------------------------
pace_df = (
    filtered_laps_df.groupby("DriverName", as_index=False)
    .agg(
        Team=("Team", "last"),
        Rounds=("Round", "nunique"),
        LapsCounted=("LapTime", "count"),
        BestLapMs=("LapTime", "min"),
        AverageLapMs=("LapTime", "mean"),
        MedianLapMs=("LapTime", "median"),
        StdDevMs=("LapTime", "std"),
    )
)

pace_df["StdDevMs"] = pace_df["StdDevMs"].fillna(0)

# Apply minimum laps filter
pace_df = pace_df[pace_df["LapsCounted"] >= min_laps].copy()

if pace_df.empty:
    st.warning("No drivers meet the minimum lap requirement.")
    st.stop()

# Ranking positions
pace_df = pace_df.sort_values(["AverageLapMs", "DriverName"], ascending=[True, True]).reset_index(drop=True)
pace_df["Pace Rank"] = pace_df.index + 1

bestlap_rank_df = pace_df.sort_values(["BestLapMs", "DriverName"], ascending=[True, True]).reset_index(drop=True)
bestlap_rank_df["Best Lap Rank"] = bestlap_rank_df.index + 1

consistency_rank_df = pace_df.sort_values(["StdDevMs", "DriverName"], ascending=[True, True]).reset_index(drop=True)
consistency_rank_df["Consistency Rank"] = consistency_rank_df.index + 1

pace_df = pace_df.merge(
    bestlap_rank_df[["DriverName", "Best Lap Rank"]],
    on="DriverName",
    how="left"
)

pace_df = pace_df.merge(
    consistency_rank_df[["DriverName", "Consistency Rank"]],
    on="DriverName",
    how="left"
)

# Delta to quickest average
fastest_avg = pace_df["AverageLapMs"].min()
pace_df["DeltaToFastestAvgMs"] = (pace_df["AverageLapMs"] - fastest_avg).round().astype(int)

# Formatting
pace_df["Best Lap"] = pace_df["BestLapMs"].round().astype(int).apply(ms_to_laptime)
pace_df["Average Lap"] = pace_df["AverageLapMs"].round().astype(int).apply(ms_to_laptime)
pace_df["Median Lap"] = pace_df["MedianLapMs"].round().astype(int).apply(ms_to_laptime)
pace_df["Consistency"] = pace_df["StdDevMs"].round().astype(int).apply(ms_to_laptime)
pace_df["Delta to Fastest Avg"] = pace_df["DeltaToFastestAvgMs"].apply(
    lambda x: "0:00.000" if int(x) == 0 else ms_to_laptime(int(x))
)

# -----------------------------------
# Headline metrics
# -----------------------------------
st.markdown('<div class="srcs-section">Pace Headlines</div>', unsafe_allow_html=True)

top_pace_row = pace_df.sort_values(["AverageLapMs", "DriverName"], ascending=[True, True]).iloc[0]
top_bestlap_row = pace_df.sort_values(["BestLapMs", "DriverName"], ascending=[True, True]).iloc[0]
top_consistency_row = pace_df.sort_values(["StdDevMs", "DriverName"], ascending=[True, True]).iloc[0]

headline_col1, headline_col2 = st.columns(2)
headline_col3, headline_col4 = st.columns(2)

with headline_col1:
    st.metric("Fastest Average Pace", top_pace_row["Average Lap"])
    st.caption(f"{top_pace_row['DriverName']} • {top_pace_row['Team']}")

with headline_col2:
    st.metric("Best One-Lap Pace", top_bestlap_row["Best Lap"])
    st.caption(f"{top_bestlap_row['DriverName']} • {top_bestlap_row['Team']}")

with headline_col3:
    st.metric("Most Consistent", top_consistency_row["Consistency"])
    st.caption(f"{top_consistency_row['DriverName']} • {top_consistency_row['Team']}")

with headline_col4:
    st.metric("Drivers Ranked", len(pace_df))
    st.caption(f"Minimum laps counted: {min_laps}")

# -----------------------------------
# Main ranking table
# -----------------------------------
st.markdown('<div class="srcs-section">Driver Pace Ranking Table</div>', unsafe_allow_html=True)

display_df = pace_df[[
    "Pace Rank",
    "DriverName",
    "Team",
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
    "Driver",
    "Team",
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

pace_chart_df = pace_df[["DriverName", "DeltaToFastestAvgMs"]].copy()
pace_chart_df.columns = ["Driver", "Delta to Fastest Average (ms)"]
pace_chart_df = pace_chart_df.sort_values("Delta to Fastest Average (ms)", ascending=False).set_index("Driver")

st.bar_chart(pace_chart_df)

# -----------------------------------
# Best lap chart
# -----------------------------------
st.markdown('<div class="srcs-section">Best Lap Ranking Chart</div>', unsafe_allow_html=True)

best_chart_df = pace_df[["DriverName", "BestLapMs"]].copy()
best_chart_df.columns = ["Driver", "Best Lap (ms)"]
best_chart_df = best_chart_df.sort_values("Best Lap (ms)", ascending=False).set_index("Driver")

st.bar_chart(best_chart_df)

# -----------------------------------
# Consistency chart
# -----------------------------------
st.markdown('<div class="srcs-section">Consistency Chart</div>', unsafe_allow_html=True)

consistency_chart_df = pace_df[["DriverName", "StdDevMs"]].copy()
consistency_chart_df.columns = ["Driver", "Std Dev (ms)"]
consistency_chart_df = consistency_chart_df.sort_values("Std Dev (ms)", ascending=False).set_index("Driver")

st.bar_chart(consistency_chart_df)

# -----------------------------------
# Pace notes
# -----------------------------------
st.markdown('<div class="srcs-section">Pace Notes</div>', unsafe_allow_html=True)

st.write(
    "This page ranks drivers by pace using official lap data. "
    "Average lap time is used as the primary ranking metric, while best lap and consistency "
    "help distinguish one-lap speed from repeatable race pace."
)

st.caption("SRCS Driver Pace Ranking — season-wide pace intelligence.")
