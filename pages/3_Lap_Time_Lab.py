import streamlit as st
import pandas as pd
from pathlib import Path

from engine.parser import load_all_race_results
from engine.race_metrics import (
    prepare_laps_dataframe,
    calculate_fastest_laps,
    calculate_average_pace,
    calculate_consistency,
)
from utils.formatting import ms_to_laptime
from utils.style import apply_srcs_style

st.set_page_config(page_title="Lap Time Lab", layout="wide")
apply_srcs_style()

st.title("⏱️ Lap Time Lab")

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
selected_results_df = all_results[selected_index].copy()
selected_summary = round_summaries[selected_index]
selected_race_data = raw_race_data[selected_index]

laps_df = prepare_laps_dataframe(selected_race_data)

if laps_df.empty:
    st.warning("No valid lap data available for this round.")
    st.stop()

# Round overview
st.subheader(f"Round Overview — {selected_summary['Round']}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Grand Prix", selected_summary["Grand Prix"])
with col2:
    st.metric("Track", selected_summary["Track"])
with col3:
    st.metric("Fastest Lap", selected_summary["Fastest Lap Driver"])
with col4:
    st.metric("Fastest Time", selected_summary["Fastest Lap Time"])

# Lap time trend
st.subheader("Lap Time Trend by Driver")

lap_chart_df = laps_df.pivot_table(
    index="LapNumber",
    columns="DriverName",
    values="LapTime",
    aggfunc="mean"
).sort_index()

st.line_chart(lap_chart_df)

# Fastest laps
st.subheader("Fastest Lap Ranking")

fastest_laps_df = calculate_fastest_laps(laps_df)

if not fastest_laps_df.empty:
    fastest_laps_df["GapMs"] = fastest_laps_df["LapTime"] - fastest_laps_df["LapTime"].min()
    fastest_laps_df["Fastest Lap"] = fastest_laps_df["LapTime"].apply(ms_to_laptime)
    fastest_laps_df["Gap"] = fastest_laps_df["GapMs"].apply(
        lambda x: "0:00.000" if x == 0 else ms_to_laptime(int(x))
    )
    fastest_laps_df["Marker"] = fastest_laps_df["DriverName"].apply(
        lambda x: "⭐" if x == selected_summary["Fastest Lap Driver"] else ""
    )

    fastest_display_df = fastest_laps_df[[
        "Position", "DriverName", "Fastest Lap", "Gap", "Marker"
    ]].copy()

    fastest_display_df.columns = ["Pos", "Driver", "Fastest Lap", "Gap", "Marker"]
    st.dataframe(fastest_display_df, use_container_width=True, hide_index=True)

# Average pace
st.subheader("Average Pace Ranking")

average_pace_df = calculate_average_pace(laps_df)

if not average_pace_df.empty:
    average_pace_df["Average Lap"] = average_pace_df["LapTime"].round().astype(int).apply(ms_to_laptime)

    average_display_df = average_pace_df[[
        "Position", "DriverName", "Average Lap"
    ]].copy()

    average_display_df.columns = ["Pos", "Driver", "Average Lap"]
    st.dataframe(average_display_df, use_container_width=True, hide_index=True)

# Consistency
st.subheader("Consistency Ranking")

consistency_df = calculate_consistency(laps_df)

if not consistency_df.empty:
    consistency_df["Consistency"] = consistency_df["StdDev"].round().astype(int).apply(ms_to_laptime)

    consistency_display_df = consistency_df[[
        "Position", "DriverName", "LapCount", "Consistency"
    ]].copy()

    consistency_display_df.columns = ["Pos", "Driver", "Laps Counted", "Consistency"]
    st.dataframe(consistency_display_df, use_container_width=True, hide_index=True)

# Pace delta to winner
st.subheader("Average Pace Delta to Race Winner")

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
    delta_df["Average Lap"] = delta_df["LapTime"].round().astype(int).apply(ms_to_laptime)
    delta_df["Delta to Winner"] = delta_df["DeltaMs"].apply(
        lambda x: "0:00.000" if x == 0 else ms_to_laptime(int(x))
    )

    delta_display_df = delta_df[[
        "Position", "DriverName", "Average Lap", "Delta to Winner"
    ]].copy()

    delta_display_df.columns = ["Pos", "Driver", "Average Lap", "Delta to Winner"]
    st.dataframe(delta_display_df, use_container_width=True, hide_index=True)

# Driver drill-down
st.subheader("Driver Drill-Down")

drivers = sorted(laps_df["DriverName"].unique().tolist())
selected_driver = st.selectbox("Select Driver", drivers)

driver_laps_df = laps_df[laps_df["DriverName"] == selected_driver].copy()
driver_laps_df = driver_laps_df.sort_values("LapNumber")

if driver_laps_df.empty:
    st.warning("No lap data available for the selected driver.")
    st.stop()

best_driver_lap = driver_laps_df["LapTime"].min()
avg_driver_lap = int(round(driver_laps_df["LapTime"].mean()))
driver_std = driver_laps_df["LapTime"].std()
driver_std_ms = 0 if pd.isna(driver_std) else int(round(driver_std))

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Driver", selected_driver)
with c2:
    st.metric("Best Lap", ms_to_laptime(best_driver_lap))
with c3:
    st.metric("Average Lap", ms_to_laptime(avg_driver_lap))
with c4:
    st.metric("Consistency", ms_to_laptime(driver_std_ms))

driver_chart_df = driver_laps_df[["LapNumber", "LapTime"]].copy().set_index("LapNumber")
st.line_chart(driver_chart_df)

st.subheader("Driver Lap Table")

driver_laps_df["Marker"] = driver_laps_df["LapTime"].apply(
    lambda x: "⭐" if x == best_driver_lap else ""
)

driver_table_df = driver_laps_df[["LapNumber", "LapTime", "Marker"]].copy()
driver_table_df["LapTime"] = driver_table_df["LapTime"].apply(ms_to_laptime)
driver_table_df.columns = ["Lap", "Lap Time", "Marker"]

st.dataframe(driver_table_df, use_container_width=True, hide_index=True)
