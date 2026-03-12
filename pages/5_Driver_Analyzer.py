import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping
from engine.driver_metrics import calculate_driver_standings
from utils.formatting import ms_to_laptime
from utils.style import apply_srcs_style

st.set_page_config(page_title="Driver Analyzer", page_icon="🧑‍💼", layout="wide")
apply_srcs_style()

st.markdown("""
<div class="srcs-hero">
<div class="srcs-hero-title">DRIVER ANALYZER</div>
<div class="srcs-hero-subtitle">Season performance intelligence for every SRCS driver</div>
</div>
""", unsafe_allow_html=True)

DATA_DIR = Path("data")
TEAM_MAP_FILE = DATA_DIR / "driver_team_map.csv"

if not DATA_DIR.exists():
    st.error("Data folder not found.")
    st.stop()

race_files, all_results, round_summaries, raw_race_data = load_all_race_results(DATA_DIR)

if not race_files:
    st.warning("No race data available.")
    st.stop()

season_results_df = pd.concat(all_results, ignore_index=True)

if TEAM_MAP_FILE.exists():
    season_results_df = apply_team_mapping(season_results_df, TEAM_MAP_FILE)
else:
    season_results_df["Team"] = "Unknown"

driver_standings = calculate_driver_standings(season_results_df)

drivers = sorted(season_results_df["DriverName"].dropna().unique().tolist())

selected_driver = st.selectbox(
    "Select Driver",
    drivers
)

driver_df = season_results_df[
    season_results_df["DriverName"] == selected_driver
].copy()

if driver_df.empty:
    st.warning("No data for this driver yet.")
    st.stop()

driver_df = driver_df.sort_values("Round")

# ---------------------------------------------------
# DRIVER SUMMARY
# ---------------------------------------------------

st.markdown('<div class="srcs-section">Driver Summary</div>', unsafe_allow_html=True)

total_points = int(driver_df["Points"].sum())
races = len(driver_df)
best_finish = int(driver_df["Position"].min())
avg_finish = round(driver_df["Position"].mean(),2)

driver_position = driver_standings.loc[
    driver_standings["Driver"] == selected_driver,
    "Pos"
].iloc[0]

team = driver_df.iloc[-1]["Team"]

c1,c2,c3,c4,c5 = st.columns(5)

with c1:
    st.metric("Championship Pos", int(driver_position))

with c2:
    st.metric("Team", team)

with c3:
    st.metric("Points", total_points)

with c4:
    st.metric("Best Finish", f"P{best_finish}")

with c5:
    st.metric("Average Finish", avg_finish)

# ---------------------------------------------------
# RACE RESULTS HISTORY
# ---------------------------------------------------

st.markdown('<div class="srcs-section">Race Results</div>', unsafe_allow_html=True)

history_df = driver_df[[
    "Round",
    "Grand Prix",
    "GridPosition",
    "Position",
    "Points"
]].copy()

history_df.columns = [
    "Round",
    "Grand Prix",
    "Grid",
    "Finish",
    "Points"
]

st.dataframe(history_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------
# FINISH TREND
# ---------------------------------------------------

st.markdown('<div class="srcs-section">Finish Position Trend</div>', unsafe_allow_html=True)

trend_df = driver_df.copy()
trend_df["RoundSort"] = trend_df["Round"].str.extract(r"Round (\d+)").astype(float)
trend_df = trend_df.sort_values("RoundSort")

finish_chart = alt.Chart(trend_df).mark_line(point=True).encode(
    x=alt.X("Round:N", title="Round"),
    y=alt.Y("Position:Q", title="Finish Position", scale=alt.Scale(reverse=True)),
    tooltip=[
        "Round",
        "Grand Prix",
        "Position",
        "Points"
    ]
).properties(height=350)

st.altair_chart(finish_chart, use_container_width=True)

# ---------------------------------------------------
# GRID VS FINISH
# ---------------------------------------------------

st.markdown('<div class="srcs-section">Grid vs Finish Performance</div>', unsafe_allow_html=True)

grid_chart_df = driver_df.copy()

grid_chart = alt.Chart(grid_chart_df).mark_circle(size=120).encode(
    x=alt.X("GridPosition:Q", title="Grid Position"),
    y=alt.Y("Position:Q", title="Finish Position", scale=alt.Scale(reverse=True)),
    tooltip=[
        "Round",
        "Grand Prix",
        "GridPosition",
        "Position"
    ]
)

st.altair_chart(grid_chart.properties(height=350), use_container_width=True)

# ---------------------------------------------------
# POSITION CHANGE
# ---------------------------------------------------

st.markdown('<div class="srcs-section">Racecraft: Positions Gained/Lost</div>', unsafe_allow_html=True)

racecraft_df = driver_df.copy()
racecraft_df["PositionChange"] = racecraft_df["GridPosition"] - racecraft_df["Position"]

racecraft_chart = alt.Chart(racecraft_df).mark_bar().encode(
    x="Round",
    y="PositionChange",
    tooltip=[
        "Grand Prix",
        "GridPosition",
        "Position",
        "PositionChange"
    ]
)

st.altair_chart(racecraft_chart.properties(height=350), use_container_width=True)

# ---------------------------------------------------
# DRIVER PROFILE
# ---------------------------------------------------

st.markdown('<div class="srcs-section">Driver Profile</div>', unsafe_allow_html=True)

positions_gained = racecraft_df["PositionChange"].sum()

profile_data = pd.DataFrame({
    "Metric":[
        "Total Points",
        "Races Entered",
        "Best Finish",
        "Average Finish",
        "Positions Gained/Lost"
    ],
    "Value":[
        total_points,
        races,
        f"P{best_finish}",
        avg_finish,
        positions_gained
    ]
})

st.dataframe(profile_data, use_container_width=True, hide_index=True)

# ---------------------------------------------------
# DRIVER NOTES
# ---------------------------------------------------

st.markdown('<div class="srcs-section">Driver Insight</div>', unsafe_allow_html=True)

if positions_gained > 0:
    racecraft_comment = "gains positions on average during races."
elif positions_gained < 0:
    racecraft_comment = "tends to lose positions during races."
else:
    racecraft_comment = "typically finishes where they start."

st.write(
f"""
**{selected_driver}** is currently **P{int(driver_position)}** in the championship with **{total_points} points**.

Their best finish so far is **P{best_finish}** and they average **P{avg_finish}** across all races.

Across the season they **{racecraft_comment}**
"""
)

st.caption("SRCS Driver Analyzer — Season performance intelligence.")
