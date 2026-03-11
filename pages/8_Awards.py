import streamlit as st
import pandas as pd
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping
from engine.race_metrics import prepare_laps_dataframe
from engine.incident_metrics import (
    prepare_events_dataframe,
    filter_incident_events,
    calculate_driver_incident_counts,
)
from utils.formatting import ms_to_laptime
from utils.style import apply_srcs_style

st.set_page_config(page_title="Awards", page_icon="🏆", layout="wide")
apply_srcs_style()

st.markdown("""
<div class="srcs-hero">
    <div class="srcs-hero-title">AWARDS</div>
    <div class="srcs-hero-subtitle">Round highlights, standout performers, and incident-based superlatives</div>
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
events_df = prepare_events_dataframe(selected_race_data)
incident_df = filter_incident_events(events_df)

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
        .sort_values(["StdDev", "DriverName"], ascending=[True, True])
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

# Clean driver + chaos leader
clean_driver = "-"
clean_driver_note = "No incident-free ranking available"
chaos_leader = "-"
chaos_leader_note = "No incident data available"

if not incident_df.empty:
    incident_counts_df = calculate_driver_incident_counts(incident_df)

    # Chaos leader = highest incident count
    if not incident_counts_df.empty:
        chaos_row = incident_counts_df.sort_values(
            ["IncidentCount", "DriverName"], ascending=[False, True]
        ).iloc[0]
        chaos_leader = chaos_row["DriverName"]
        chaos_leader_note = f"{int(chaos_row['IncidentCount'])} incident(s)"

    # Clean driver = classified driver with zero incidents, best finish tie-break
    classified_drivers = selected_results_df[["DriverName", "Position"]].copy()

    incident_drivers = set(incident_df["DriverName"].dropna().tolist())
    clean_candidates = classified_drivers[~classified_drivers["DriverName"].isin(incident_drivers)].copy()

    if not clean_candidates.empty:
        clean_candidates = clean_candidates.sort_values(
            ["Position", "DriverName"], ascending=[True, True]
        ).reset_index(drop=True)
        clean_driver = clean_candidates.iloc[0]["DriverName"]
        clean_driver_note = "No recorded incident involvement"
else:
    # If no incidents exist at all, classify best finisher as clean driver
    if not selected_results_df.empty:
        clean_driver = winner_row["DriverName"]
        clean_driver_note = "No incidents recorded this round"

# Awards strip
st.markdown('<div class="srcs-section">Round Awards</div>', unsafe_allow_html=True)

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

c7, c8 = st.columns(2)
with c7:
    st.metric("Clean Driver", clean_driver)
with c8:
    st.metric("Chaos Leader", chaos_leader)

st.caption(
    f"{selected_summary['Round']} • {selected_summary['Grand Prix']} • "
    f"{selected_summary['Track']} • {selected_summary['Session Type']}"
)

# Awards detail table
st.markdown('<div class="srcs-section">Awards Summary</div>', unsafe_allow_html=True)

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
    {
        "Award": "Clean Driver",
        "Winner": clean_driver,
        "Detail": clean_driver_note
    },
    {
        "Award": "Chaos Leader",
        "Winner": chaos_leader,
        "Detail": chaos_leader_note
    },
])

st.dataframe(awards_df, use_container_width=True, hide_index=True)

# Podium spotlight
st.markdown('<div class="srcs-section">Podium Spotlight</div>', unsafe_allow_html=True)

podium_df = selected_results_df.head(3)[[
    "Position", "DriverName", "Team", "Points"
]].copy()

podium_df.columns = ["Pos", "Driver", "Team", "Points"]
st.dataframe(podium_df, use_container_width=True, hide_index=True)

# Movers spotlight
st.markdown('<div class="srcs-section">Biggest Movers and Losers</div>', unsafe_allow_html=True)

movers_df = selected_results_df[[
    "DriverName", "Team", "GridPosition", "Position", "Positions Gained"
]].copy()

movers_df.columns = ["Driver", "Team", "Grid", "Finish", "Net Gain/Loss"]
movers_df = movers_df.sort_values("Net Gain/Loss", ascending=False)

st.dataframe(movers_df, use_container_width=True, hide_index=True)

# Team awards breakdown
st.markdown('<div class="srcs-section">Team Awards Breakdown</div>', unsafe_allow_html=True)

team_awards_df = team_points_df.copy()
team_awards_df["Position"] = team_awards_df.index + 1
team_awards_df = team_awards_df[["Position", "Team", "Points"]]
team_awards_df.columns = ["Pos", "Team", "Round Points"]

st.dataframe(team_awards_df, use_container_width=True, hide_index=True)

# Incident-based awards context
st.markdown('<div class="srcs-section">Incident-Based Awards Context</div>', unsafe_allow_html=True)

if not incident_df.empty:
    incident_context_df = incident_df[[
        "DriverName", "OtherDriverName", "Type", "ImpactSpeed"
    ]].copy()

    incident_context_df.columns = ["Driver", "Other Driver", "Incident Type", "Impact Speed"]
    incident_context_df["Impact Speed"] = incident_context_df["Impact Speed"].round(1)

    st.dataframe(incident_context_df, use_container_width=True, hide_index=True)
else:
    st.info("No incident events recorded for this round.")

# Notes
st.markdown('<div class="srcs-section">Awards Notes</div>', unsafe_allow_html=True)

st.write(
    "This page highlights standout race performers, pace awards, team outcomes, "
    "and incident-based superlatives for the selected round."
)
