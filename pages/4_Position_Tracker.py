import streamlit as st
import pandas as pd
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping
from utils.style import apply_srcs_style

st.set_page_config(page_title="Position Tracker", page_icon="📍", layout="wide")
apply_srcs_style()

st.markdown("""
<div class="srcs-hero">
    <div class="srcs-hero-title">POSITION TRACKER</div>
    <div class="srcs-hero-subtitle">Grid vs finish, net movement, and racecraft summary</div>
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

biggest_mover_row = selected_results_df.sort_values(
    ["Positions Gained", "Position"], ascending=[False, True]
).iloc[0]

biggest_loser_row = selected_results_df.sort_values(
    ["Positions Gained", "Position"], ascending=[True, True]
).iloc[0]

winner_row = selected_results_df.sort_values("Position").iloc[0]
pole_row = selected_results_df.sort_values("GridPosition").iloc[0]

# Header summary
st.markdown('<div class="srcs-section">Round Movement Summary</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Winner", winner_row["DriverName"])
with c2:
    st.metric("Pole", pole_row["DriverName"])
with c3:
    st.metric("Biggest Mover", biggest_mover_row["DriverName"])
with c4:
    st.metric("Biggest Loser", biggest_loser_row["DriverName"])

st.caption(
    f"{selected_summary['Round']} • {selected_summary['Grand Prix']} • "
    f"{selected_summary['Track']} • {selected_summary['Session Type']}"
)

# Racecraft spotlight
st.markdown('<div class="srcs-section">Racecraft Spotlight</div>', unsafe_allow_html=True)

spot1, spot2, spot3 = st.columns(3)
with spot1:
    st.metric(
        "Positions Gained",
        int(biggest_mover_row["Positions Gained"])
    )
with spot2:
    st.metric(
        "Positions Lost",
        abs(int(biggest_loser_row["Positions Gained"]))
    )
with spot3:
    avg_movement = round(selected_results_df["Positions Gained"].mean(), 2)
    st.metric("Average Net Movement", avg_movement)

# Main tracker table
st.markdown('<div class="srcs-section">Grid vs Finish Tracker</div>', unsafe_allow_html=True)

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

# Net movement chart
st.markdown('<div class="srcs-section">Net Position Change Chart</div>', unsafe_allow_html=True)

position_chart_df = selected_results_df[[
    "DriverName",
    "Positions Gained"
]].copy()

position_chart_df.columns = ["Driver", "Net Gain/Loss"]
position_chart_df = position_chart_df.sort_values("Net Gain/Loss", ascending=True).set_index("Driver")

st.bar_chart(position_chart_df)

# Movement distribution
st.markdown('<div class="srcs-section">Movement Distribution</div>', unsafe_allow_html=True)

movement_dist_df = (
    tracker_df.groupby("Movement", as_index=False)
    .size()
    .rename(columns={"size": "Count"})
    .sort_values(["Count", "Movement"], ascending=[False, True])
)

if not movement_dist_df.empty:
    movement_dist_chart_df = movement_dist_df.set_index("Movement")
    st.bar_chart(movement_dist_chart_df)

# Biggest movers table
st.markdown('<div class="srcs-section">Biggest Movers</div>', unsafe_allow_html=True)

movers_df = selected_results_df.sort_values(
    ["Positions Gained", "Position"], ascending=[False, True]
)[[
    "DriverName",
    "Team",
    "GridPosition",
    "Position",
    "Positions Gained",
    "Points"
]].copy()

movers_df.columns = ["Driver", "Team", "Grid", "Finish", "Net Gain/Loss", "Points"]
st.dataframe(movers_df, use_container_width=True, hide_index=True)

# Team movement summary
st.markdown('<div class="srcs-section">Team Movement Summary</div>', unsafe_allow_html=True)

team_movement_df = (
    selected_results_df.groupby("Team", as_index=False)
    .agg(
        AvgGrid=("GridPosition", "mean"),
        AvgFinish=("Position", "mean"),
        TotalPoints=("Points", "sum"),
        TotalNetMovement=("Positions Gained", "sum")
    )
    .sort_values(["TotalNetMovement", "TotalPoints", "Team"], ascending=[False, False, True])
    .reset_index(drop=True)
)

team_movement_df["Position"] = team_movement_df.index + 1
team_movement_df["AvgGrid"] = team_movement_df["AvgGrid"].round(2)
team_movement_df["AvgFinish"] = team_movement_df["AvgFinish"].round(2)

team_movement_display_df = team_movement_df[[
    "Position", "Team", "AvgGrid", "AvgFinish", "TotalNetMovement", "TotalPoints"
]].copy()

team_movement_display_df.columns = [
    "Pos", "Team", "Avg Grid", "Avg Finish", "Net Team Movement", "Points"
]

st.dataframe(team_movement_display_df, use_container_width=True, hide_index=True)

# Grid / finish comparison
st.markdown('<div class="srcs-section">Grid and Finish Comparison</div>', unsafe_allow_html=True)

comparison_df = selected_results_df[[
    "DriverName",
    "GridPosition",
    "Position",
    "Positions Gained"
]].copy()

comparison_df.columns = ["Driver", "Grid", "Finish", "Net Gain/Loss"]
comparison_df = comparison_df.sort_values(["Finish", "Driver"], ascending=[True, True])

st.dataframe(comparison_df, use_container_width=True, hide_index=True)

# Position gain banding
st.markdown('<div class="srcs-section">Position Gain Bands</div>', unsafe_allow_html=True)

def movement_band(x):
    if x >= 4:
        return "Major Gain (4+)"
    if x >= 1:
        return "Minor Gain (1-3)"
    if x == 0:
        return "No Change"
    if x <= -4:
        return "Major Loss (4+)"
    return "Minor Loss (1-3)"

band_df = selected_results_df[["DriverName", "Positions Gained"]].copy()
band_df["Movement Band"] = band_df["Positions Gained"].apply(movement_band)

band_summary_df = (
    band_df.groupby("Movement Band", as_index=False)
    .size()
    .rename(columns={"size": "Count"})
    .sort_values(["Count", "Movement Band"], ascending=[False, True])
)

if not band_summary_df.empty:
    st.dataframe(band_summary_df, use_container_width=True, hide_index=True)

# Tracker notes
st.markdown('<div class="srcs-section">Tracker Notes</div>', unsafe_allow_html=True)

st.write(
    "This page tracks grid-to-finish movement and racecraft impact for the selected round. "
    "A true lap-by-lap position trace is not yet available from the current export format, "
    "so this version focuses on official classification movement, biggest movers, and team-level racecraft trends."
)
