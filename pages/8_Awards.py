import streamlit as st
import pandas as pd
from pathlib import Path

from engine.parser import load_all_race_results
from engine.incident_metrics import (
    prepare_events_dataframe,
    filter_incident_events,
    calculate_impact_speed_ranking,
    calculate_incident_type_breakdown,
    calculate_driver_incident_counts,
)
from utils.style import apply_srcs_style

st.set_page_config(page_title="Incident Center", page_icon="⚠️", layout="wide")
apply_srcs_style()

st.markdown("""
<div class="srcs-hero">
    <div class="srcs-hero-title">INCIDENT CENTER</div>
    <div class="srcs-hero-subtitle">Incident log, impact speed ranking, and incident type breakdown</div>
</div>
""", unsafe_allow_html=True)

DATA_DIR = Path("data")

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
selected_summary = round_summaries[selected_index]
selected_results_df = all_results[selected_index].copy()
selected_race_data = raw_race_data[selected_index]

events_df = prepare_events_dataframe(selected_race_data)
incident_df = filter_incident_events(events_df)

st.markdown('<div class="srcs-section">Round Context</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Grand Prix", selected_summary["Grand Prix"])
with c2:
    st.metric("Track", selected_summary["Track"])
with c3:
    st.metric("Session Type", selected_summary["Session Type"])
with c4:
    st.metric("Classified Drivers", len(selected_results_df))

st.caption(
    f"{selected_summary['Round']} • "
    f"{selected_summary['Grand Prix']} • "
    f"{selected_summary['Track']}"
)

if incident_df.empty:
    st.info("No incident events found in the race data for this round.")
    st.stop()

# Headline incident metrics
max_impact = float(incident_df["ImpactSpeed"].max()) if "ImpactSpeed" in incident_df.columns else 0.0
incident_count = len(incident_df)

top_impact_row = incident_df.sort_values("ImpactSpeed", ascending=False).iloc[0]
top_driver_name = top_impact_row["DriverName"]
top_incident_type = top_impact_row["Type"]

st.markdown('<div class="srcs-section">Incident Summary</div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Incident Count", incident_count)
with m2:
    st.metric("Max Impact Speed", round(max_impact, 1))
with m3:
    st.metric("Top Impact Driver", top_driver_name)
with m4:
    st.metric("Top Impact Type", top_incident_type)

# Incident log
st.markdown('<div class="srcs-section">Incident Log</div>', unsafe_allow_html=True)

incident_log_df = incident_df[[
    "Timestamp",
    "DriverName",
    "OtherDriverName",
    "Type",
    "ImpactSpeed",
    "AfterSessionEnd"
]].copy()

incident_log_df.columns = [
    "Timestamp",
    "Driver",
    "Other Driver",
    "Incident Type",
    "Impact Speed",
    "After Session End"
]

incident_log_df["Impact Speed"] = incident_log_df["Impact Speed"].round(1)

st.dataframe(incident_log_df, use_container_width=True, hide_index=True)

# Impact speed ranking
st.markdown('<div class="srcs-section">Impact Speed Ranking</div>', unsafe_allow_html=True)

impact_df = calculate_impact_speed_ranking(incident_df)

impact_display_df = impact_df[[
    "Position",
    "DriverName",
    "OtherDriverName",
    "Type",
    "ImpactSpeed"
]].copy()

impact_display_df.columns = [
    "Pos",
    "Driver",
    "Other Driver",
    "Incident Type",
    "Impact Speed"
]

impact_display_df["Impact Speed"] = impact_display_df["Impact Speed"].round(1)

st.dataframe(impact_display_df, use_container_width=True, hide_index=True)

impact_chart_df = impact_df[["DriverName", "ImpactSpeed"]].copy()
impact_chart_df.columns = ["Driver", "Impact Speed"]
impact_chart_df = impact_chart_df.sort_values("Impact Speed", ascending=False).set_index("Driver")

st.bar_chart(impact_chart_df)

# Incident type chart
st.markdown('<div class="srcs-section">Incident Type Chart</div>', unsafe_allow_html=True)

incident_type_df = calculate_incident_type_breakdown(incident_df)

if not incident_type_df.empty:
    st.dataframe(incident_type_df, use_container_width=True, hide_index=True)

    incident_type_chart_df = incident_type_df.set_index("Type")
    st.bar_chart(incident_type_chart_df)
else:
    st.info("No incident type breakdown available.")

# Driver incident counts
st.markdown('<div class="srcs-section">Driver Incident Counts</div>', unsafe_allow_html=True)

driver_incident_df = calculate_driver_incident_counts(incident_df)

if not driver_incident_df.empty:
    driver_incident_display_df = driver_incident_df[[
        "Position", "DriverName", "IncidentCount"
    ]].copy()

    driver_incident_display_df.columns = ["Pos", "Driver", "Incident Count"]

    st.dataframe(driver_incident_display_df, use_container_width=True, hide_index=True)

    driver_incident_chart_df = driver_incident_df[["DriverName", "IncidentCount"]].copy()
    driver_incident_chart_df.columns = ["Driver", "Incident Count"]
    driver_incident_chart_df = driver_incident_chart_df.set_index("Driver")

    st.bar_chart(driver_incident_chart_df)

st.caption("SRCS Incident Center — event-driven incident analysis from official race export data.")
