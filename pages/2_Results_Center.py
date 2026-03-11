import streamlit as st
import pandas as pd
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping
from utils.formatting import ms_to_laptime, ms_to_racetime
from utils.style import apply_srcs_style

st.set_page_config(page_title="Results Center", page_icon="🏁", layout="wide")
apply_srcs_style()

st.markdown("""
<div class="srcs-hero">
    <div class="srcs-hero-title">RESULTS CENTER</div>
    <div class="srcs-hero-subtitle">Official race classification, finish gaps, and points</div>
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

winner_row = selected_results_df.iloc[0]
winner_time = int(winner_row["TotalTime"])

def ms_to_gap(ms):
    if ms is None:
        return "-"
    ms = int(ms)
    if ms == 0:
        return "WIN"
    total_seconds = ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    millis = ms % 1000
    if minutes > 0:
        return f"+{minutes}:{seconds:02d}.{millis:03d}"
    return f"+{seconds}.{millis:03d}"

selected_results_df["GapMs"] = selected_results_df["TotalTime"] - winner_time
selected_results_df["Gap"] = selected_results_df["GapMs"].apply(ms_to_gap)

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
st.markdown('<div class="srcs-section">Official Classification</div>', unsafe_allow_html=True)

classification_df = selected_results_df[[
    "Position",
    "DriverName",
    "Team",
    "GridPosition",
    "Gap",
    "BestLap",
    "Points",
    "Positions Gained"
]].copy()

classification_df.columns = [
    "Pos",
    "Driver",
    "Team",
    "Grid",
    "Gap",
    "Best Lap",
    "Pts",
    "Pos Gained"
]

classification_df["Best Lap"] = classification_df["Best Lap"].apply(ms_to_laptime)

st.dataframe(classification_df, use_container_width=True, hide_index=True)

# Finish gap chart
st.markdown('<div class="srcs-section">Finish Gap Chart</div>', unsafe_allow_html=True)

gap_chart_df = selected_results_df[["DriverName", "GapMs"]].copy()
gap_chart_df.columns = ["Driver", "Gap to Winner (ms)"]
gap_chart_df = gap_chart_df.sort_values("Gap to Winner (ms)", ascending=False).set_index("Driver")

st.bar_chart(gap_chart_df)

# Positions gained chart
st.markdown('<div class="srcs-section">Positions Gained Chart</div>', unsafe_allow_html=True)

pos_chart_df = selected_results_df[["DriverName", "Positions Gained"]].copy()
pos_chart_df.columns = ["Driver", "Positions Gained"]
pos_chart_df = pos_chart_df.sort_values("Positions Gained", ascending=True).set_index("Driver")

st.bar_chart(pos_chart_df)

# Race result summary
st.markdown('<div class="srcs-section">Race Result Summary</div>', unsafe_allow_html=True)

summary_col1, summary_col2 = st.columns(2)

with summary_col1:
    summary_table = pd.DataFrame([
        {"Item": "Winner", "Value": winner_row["DriverName"]},
        {"Item": "Winning Time", "Value": ms_to_racetime(winner_row["TotalTime"])},
        {"Item": "Pole", "Value": pole_row["DriverName"]},
        {"Item": "Fastest Lap Driver", "Value": selected_summary["Fastest Lap Driver"]},
        {"Item": "Fastest Lap Time", "Value": selected_summary["Fastest Lap Time"]},
    ])
    st.dataframe(summary_table, use_container_width=True, hide_index=True)

with summary_col2:
    top3_df = selected_results_df.head(3)[["Position", "DriverName", "Team", "Gap", "Points"]].copy()
    top3_df.columns = ["Pos", "Driver", "Team", "Gap", "Points"]
    st.dataframe(top3_df, use_container_width=True, hide_index=True)

# Team result breakdown
st.markdown('<div class="srcs-section">Team Results This Round</div>', unsafe_allow_html=True)

team_round_df = (
    selected_results_df.groupby("Team", as_index=False)["Points"]
    .sum()
    .sort_values(["Points", "Team"], ascending=[False, True])
    .reset_index(drop=True)
)

team_round_df["Pos"] = team_round_df.index + 1
team_round_df = team_round_df[["Pos", "Team", "Points"]]

st.dataframe(team_round_df, use_container_width=True, hide_index=True)

st.caption("SRCS Results Center — official classification and gap-based round analysis.")
