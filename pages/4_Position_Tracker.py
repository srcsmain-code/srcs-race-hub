import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping
from engine.race_metrics import (
    prepare_laps_dataframe,
    build_estimated_position_by_lap,
    build_estimated_overtake_summary,
)
from utils.style import apply_srcs_style
from utils.formatting import ms_to_laptime

st.set_page_config(page_title="Position Tracker", page_icon="📍", layout="wide")
apply_srcs_style()

# =========================
# HERO
# =========================
st.markdown("""
<div class="srcs-hero">
    <div class="srcs-hero-title">POSITION TRACKER</div>
    <div class="srcs-hero-subtitle">Estimated lap-end running order, net movement, and race evolution</div>
</div>
""", unsafe_allow_html=True)

# =========================
# DATA LOAD
# =========================
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

# =========================
# TEAM MAPPING
# =========================
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

# =========================
# KEY DRIVERS
# =========================
winner_row = selected_results_df.iloc[0]
pole_row = selected_results_df.sort_values("GridPosition").iloc[0]

biggest_mover_row = selected_results_df.sort_values(
    ["Positions Gained", "Position"], ascending=[False, True]
).iloc[0]

biggest_loser_row = selected_results_df.sort_values(
    ["Positions Gained", "Position"], ascending=[True, True]
).iloc[0]

# =========================
# LAP DATA
# =========================
laps_df = prepare_laps_dataframe(selected_race_data)
position_df = build_estimated_position_by_lap(laps_df)
changes_df = build_estimated_overtake_summary(position_df)

# =========================
# SUMMARY METRICS (FIXED)
# =========================
st.markdown('<div class="srcs-section">Round Movement Summary</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Winner", winner_row["DriverName"])
    st.caption(f"Team: {winner_row['Team']}")

with c2:
    pole_lap = ms_to_laptime(pole_row["BestLap"]) if "BestLap" in pole_row.index else None
    st.metric("Pole", "Pole Sitter")
    st.caption(
        f"{pole_row['DriverName']}"
        + (f" • {pole_lap}" if pole_lap else "")
    )

with c3:
    gain = int(biggest_mover_row["Positions Gained"])
    st.metric("Biggest Mover", f"+{gain}" if gain >= 0 else str(gain))
    st.caption(biggest_mover_row["DriverName"])

with c4:
    loss = int(biggest_loser_row["Positions Gained"])
    st.metric("Biggest Loser", str(loss))
    st.caption(biggest_loser_row["DriverName"])

st.caption(
    f"{selected_summary['Grand Prix']} • {selected_summary['Track']} • {selected_summary['Session Type']}"
)

# =========================
# GRID VS FINISH
# =========================
st.markdown('<div class="srcs-section">Grid vs Finish Tracker</div>', unsafe_allow_html=True)

tracker_df = selected_results_df[[
    "DriverName", "Team", "GridPosition", "Position",
    "Positions Gained", "Movement", "Points"
]].copy()

tracker_df.columns = [
    "Driver", "Team", "Grid", "Finish",
    "Net Gain/Loss", "Movement", "Points"
]

st.dataframe(tracker_df, use_container_width=True, hide_index=True)

# =========================
# POSITION CHANGE CHART
# =========================
st.markdown('<div class="srcs-section">Net Position Change Chart</div>', unsafe_allow_html=True)

chart_df = selected_results_df[["DriverName", "Positions Gained"]].copy()
chart_df.columns = ["Driver", "Net Gain/Loss"]
chart_df = chart_df.sort_values("Net Gain/Loss", ascending=True).set_index("Driver")

st.bar_chart(chart_df)

# =========================
# POSITION BY LAP
# =========================
st.markdown('<div class="srcs-section">Estimated Position by Lap</div>', unsafe_allow_html=True)

if not position_df.empty:

    pos_chart_df = position_df.pivot_table(
        index="LapNumber",
        columns="DriverName",
        values="EstimatedPosition",
        aggfunc="first"
    ).sort_index()

    chart_long = pos_chart_df.reset_index().melt(
        "LapNumber", var_name="Driver", value_name="Position"
    )

    chart_long = chart_long.dropna()

    line_chart = alt.Chart(chart_long).mark_line(point=True).encode(
        x="LapNumber:Q",
        y=alt.Y("Position:Q", scale=alt.Scale(reverse=True)),
        color="Driver:N",
        tooltip=["Driver", "LapNumber", "Position"]
    )

    st.altair_chart(line_chart.properties(height=500), use_container_width=True)

else:
    st.info("Not enough lap data available.")

# =========================
# HEATMAP TABLE
# =========================
st.markdown('<div class="srcs-section">Race Evolution Heatmap Table</div>', unsafe_allow_html=True)

if not position_df.empty:
    heatmap_df = position_df.pivot_table(
        index="DriverName",
        columns="LapNumber",
        values="EstimatedPosition",
        aggfunc="first"
    )
    st.dataframe(heatmap_df, use_container_width=True)

# =========================
# POSITION CHANGE SUMMARY
# =========================
st.markdown('<div class="srcs-section">Estimated Position Change Summary</div>', unsafe_allow_html=True)

if not changes_df.empty:
    summary_df = (
        changes_df.groupby("DriverName", as_index=False)["PositionDelta"]
        .sum()
        .sort_values("PositionDelta", ascending=False)
    )

    summary_df.columns = ["Driver", "Net Estimated Change"]
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

# =========================
# TRACKER NOTES
# =========================
st.markdown('<div class="srcs-section">Tracker Notes</div>', unsafe_allow_html=True)

st.write(
    "Estimated lap-end positions based on cumulative lap times. "
    "This is a reconstruction for analysis, not official timing."
)
