import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping
from engine.race_metrics import (
    prepare_laps_dataframe,
    calculate_fastest_laps,
    calculate_average_pace,
    calculate_consistency,
)
from utils.formatting import ms_to_laptime
from utils.style import apply_srcs_style

st.set_page_config(page_title="Lap Time Lab", page_icon="⏱️", layout="wide")
apply_srcs_style()

st.markdown("""
<div class="srcs-hero">
    <div class="srcs-hero-title">LAP TIME LAB</div>
    <div class="srcs-hero-subtitle">Pace analysis, fastest laps, average pace, and driver lap traces</div>
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

laps_df = prepare_laps_dataframe(selected_race_data)

if laps_df.empty:
    st.warning("No valid lap data available for this round.")
    st.stop()

driver_team_df = selected_results_df[["DriverName", "Team"]].drop_duplicates()
laps_df = laps_df.merge(driver_team_df, on="DriverName", how="left")
laps_df["Team"] = laps_df["Team"].fillna("Unknown")

# SRCS team accent registry
team_colors = {
    "McLaren": "#FF8700",
    "Ferrari": "#C00000",
    "Mercedes": "#00A19B",
    "Red Bull": "#0B1E3C",
    "Williams": "#005AFF",
    "Aston Martin": "#006F62",
    "Alpine": "#0090FF",
    "Haas": "#8B0000",
    "Audi": "#BB0A30",
    "Racing Bulls": "#1A1F3B",
    "Unknown": "#C0C0C0",
}

teams_present = laps_df["Team"].dropna().unique().tolist()
color_domain = [t for t in team_colors.keys() if t in teams_present]
color_range = [team_colors[t] for t in color_domain]
for team in teams_present:
    if team not in color_domain:
        color_domain.append(team)
        color_range.append("#C0C0C0")

color_scale = alt.Scale(domain=color_domain, range=color_range)

# Round overview
st.markdown('<div class="srcs-section">Round Overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Grand Prix", selected_summary["Grand Prix"])
with c2:
    st.metric("Track", selected_summary["Track"])
with c3:
    st.metric("Fastest Lap", selected_summary["Fastest Lap Driver"])
with c4:
    st.metric("Fastest Time", selected_summary["Fastest Lap Time"])

# Filters
st.markdown('<div class="srcs-section">Lap Trace Filters</div>', unsafe_allow_html=True)

drivers = sorted(laps_df["DriverName"].dropna().unique().tolist())
teams = sorted(laps_df["Team"].dropna().unique().tolist())

f1, f2 = st.columns(2)
with f1:
    selected_driver_filter = st.selectbox(
        "Focus on Driver",
        ["All Drivers"] + drivers,
        key="lap_lab_driver_filter"
    )
with f2:
    selected_team_filter = st.selectbox(
        "Focus on Team",
        ["All Teams"] + teams,
        key="lap_lab_team_filter"
    )

filtered_laps_df = laps_df.copy()

if selected_driver_filter != "All Drivers":
    filtered_laps_df = filtered_laps_df[filtered_laps_df["DriverName"] == selected_driver_filter].copy()
elif selected_team_filter != "All Teams":
    filtered_laps_df = filtered_laps_df[filtered_laps_df["Team"] == selected_team_filter].copy()

# Lap time trend
st.markdown('<div class="srcs-section">Lap Time Trend by Driver</div>', unsafe_allow_html=True)

if not filtered_laps_df.empty:
    chart_df = filtered_laps_df[["LapNumber", "DriverName", "LapTime", "Team"]].copy()
    chart_df["Lap Time Label"] = chart_df["LapTime"].apply(ms_to_laptime)

    last_points_df = (
        chart_df.sort_values(["DriverName", "LapNumber"])
        .groupby("DriverName", as_index=False)
        .tail(1)
        .copy()
    )

    line_chart = alt.Chart(chart_df).mark_line(point=True).encode(
        x=alt.X("LapNumber:Q", title="Lap"),
        y=alt.Y("LapTime:Q", title="Lap Time (ms)"),
        color=alt.Color("Team:N", scale=color_scale, legend=alt.Legend(title="Team")),
        detail="DriverName:N",
        tooltip=[
            alt.Tooltip("DriverName:N", title="Driver"),
            alt.Tooltip("Team:N", title="Team"),
            alt.Tooltip("LapNumber:Q", title="Lap"),
            alt.Tooltip("Lap Time Label:N", title="Lap Time")
        ]
    )

    label_chart = alt.Chart(last_points_df).mark_text(
        align="left",
        baseline="middle",
        dx=8,
        fontSize=12,
        fontWeight="bold"
    ).encode(
        x=alt.X("LapNumber:Q"),
        y=alt.Y("LapTime:Q"),
        text="DriverName:N",
        color=alt.Color("Team:N", scale=color_scale, legend=None)
    )

    st.altair_chart((line_chart + label_chart).properties(height=520), use_container_width=True)
else:
    st.info("No lap data available for the selected filter.")

# Fastest laps
st.markdown('<div class="srcs-section">Fastest Lap Ranking</div>', unsafe_allow_html=True)

fastest_laps_df = calculate_fastest_laps(laps_df)

if not fastest_laps_df.empty:
    fastest_laps_df = fastest_laps_df.merge(driver_team_df, on="DriverName", how="left")
    fastest_laps_df["Team"] = fastest_laps_df["Team"].fillna("Unknown")
    fastest_laps_df["GapMs"] = fastest_laps_df["LapTime"] - fastest_laps_df["LapTime"].min()
    fastest_laps_df["Fastest Lap"] = fastest_laps_df["LapTime"].apply(ms_to_laptime)
    fastest_laps_df["Gap"] = fastest_laps_df["GapMs"].apply(
        lambda x: "0:00.000" if int(round(x)) == 0 else ms_to_laptime(int(round(x)))
    )
    fastest_laps_df["Fastest Lap"] = fastest_laps_df["DriverName"].apply(
        lambda x: "⭐" if x == selected_summary["Fastest Lap Driver"] else ""
    )

    fastest_display_df = fastest_laps_df[[
        "Position", "DriverName", "Team", "Fastest Lap", "Gap", "Fastest Lap"
    ]].copy()
    fastest_display_df.columns = ["Pos", "Driver", "Team", "Fastest Lap", "Gap", "Fastest Lap"]

    st.dataframe(fastest_display_df, use_container_width=True, hide_index=True)

# Average pace
st.markdown('<div class="srcs-section">Average Pace Ranking</div>', unsafe_allow_html=True)

average_pace_df = calculate_average_pace(laps_df)

if not average_pace_df.empty:
    average_pace_df = average_pace_df.merge(driver_team_df, on="DriverName", how="left")
    average_pace_df["Team"] = average_pace_df["Team"].fillna("Unknown")
    average_pace_df["Average Lap"] = average_pace_df["LapTime"].round().astype(int).apply(ms_to_laptime)

    average_display_df = average_pace_df[[
        "Position", "DriverName", "Team", "Average Lap"
    ]].copy()
    average_display_df.columns = ["Pos", "Driver", "Team", "Average Lap"]

    st.dataframe(average_display_df, use_container_width=True, hide_index=True)

# Pace delta to winner
st.markdown('<div class="srcs-section">Average Pace Delta to Race Winner</div>', unsafe_allow_html=True)

winner_name = None
if not selected_results_df.empty:
    winner_row = selected_results_df.sort_values("Position").iloc[0]
    winner_name = winner_row["DriverName"]

if not average_pace_df.empty and winner_name in average_pace_df["DriverName"].values:
    winner_avg = average_pace_df.loc[
        average_pace_df["DriverName"] == winner_name, "LapTime"
    ].iloc[0]

    delta_df = average_pace_df.copy()
    delta_df["DeltaMs"] = (delta_df["LapTime"] - winner_avg).round().astype(int)
    delta_df["Delta to Winner"] = delta_df["DeltaMs"].apply(
        lambda x: "0:00.000" if int(x) == 0 else ms_to_laptime(int(x))
    )

    delta_display_df = delta_df[[
        "Position", "DriverName", "Team", "Average Lap", "Delta to Winner"
    ]].copy()
    delta_display_df.columns = ["Pos", "Driver", "Team", "Average Lap", "Delta to Winner"]

    st.dataframe(delta_display_df, use_container_width=True, hide_index=True)

# Consistency
st.markdown('<div class="srcs-section">Consistency Ranking</div>', unsafe_allow_html=True)

consistency_df = calculate_consistency(laps_df)

if not consistency_df.empty:
    consistency_df = consistency_df.merge(driver_team_df, on="DriverName", how="left")
    consistency_df["Team"] = consistency_df["Team"].fillna("Unknown")
    consistency_df["Consistency"] = consistency_df["StdDev"].round().astype(int).apply(ms_to_laptime)

    consistency_display_df = consistency_df[[
        "Position", "DriverName", "Team", "LapCount", "Consistency"
    ]].copy()
    consistency_display_df.columns = ["Pos", "Driver", "Team", "Laps Counted", "Consistency"]

    st.dataframe(consistency_display_df, use_container_width=True, hide_index=True)

# Driver drill-down
st.markdown('<div class="srcs-section">Driver Drill-Down</div>', unsafe_allow_html=True)

selected_driver = st.selectbox("Select Driver", drivers, key="lap_lab_drilldown_driver")

driver_laps_df = laps_df[laps_df["DriverName"] == selected_driver].copy()
driver_laps_df = driver_laps_df.sort_values("LapNumber")

if driver_laps_df.empty:
    st.warning("No lap data available for the selected driver.")
    st.stop()

best_driver_lap = driver_laps_df["LapTime"].min()
avg_driver_lap = int(round(driver_laps_df["LapTime"].mean()))
driver_std = driver_laps_df["LapTime"].std()
driver_std_ms = 0 if pd.isna(driver_std) else int(round(driver_std))
driver_team = driver_laps_df["Team"].iloc[0] if "Team" in driver_laps_df.columns else "Unknown"

d1, d2, d3, d4 = st.columns(4)
with d1:
    st.metric("Driver", selected_driver)
with d2:
    st.metric("Team", driver_team)
with d3:
    st.metric("Best Lap", ms_to_laptime(best_driver_lap))
with d4:
    st.metric("Consistency", ms_to_laptime(driver_std_ms))

drilldown_chart_df = driver_laps_df[["LapNumber", "LapTime"]].copy()
drilldown_chart_df["Lap Time Label"] = drilldown_chart_df["LapTime"].apply(ms_to_laptime)
drilldown_chart_df["Fastest Lap"] = drilldown_chart_df["LapTime"].apply(
    lambda x: "⭐" if x == best_driver_lap else ""
)

driver_chart = alt.Chart(drilldown_chart_df).mark_line(point=True).encode(
    x=alt.X("LapNumber:Q", title="Lap"),
    y=alt.Y("LapTime:Q", title="Lap Time (ms)"),
    tooltip=[
        alt.Tooltip("LapNumber:Q", title="Lap"),
        alt.Tooltip("Lap Time Label:N", title="Lap Time"),
        alt.Tooltip("Fastest Lap:N", title="")
    ]
).properties(height=360)

st.altair_chart(driver_chart, use_container_width=True)

st.markdown('<div class="srcs-section">Driver Lap Table</div>', unsafe_allow_html=True)

driver_table_df = driver_laps_df[["LapNumber", "LapTime"]].copy()
driver_table_df["LapTime"] = driver_table_df["LapTime"].apply(ms_to_laptime)
driver_table_df["Fastest Lap"] = driver_laps_df["LapTime"].apply(
    lambda x: "⭐" if x == best_driver_lap else ""
)
driver_table_df.columns = ["Lap", "Lap Time", "Fastest Lap"]

st.dataframe(driver_table_df, use_container_width=True, hide_index=True)

st.caption("SRCS Lap Time Lab — pace analysis from official lap export data.")
