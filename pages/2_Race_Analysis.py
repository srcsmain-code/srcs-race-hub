import streamlit as st
import pandas as pd
from pathlib import Path

from utils.data_loader import load_all_race_results
from utils.formatting import ms_to_laptime

st.set_page_config(page_title="Race Analysis", layout="wide")

st.title("📊 Race Analysis")

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

laps_df = pd.DataFrame(selected_race_data.get("Laps", []))

if laps_df.empty:
    st.warning("No lap data available for this round.")
    st.stop()

# Normalize lap number column
if "LapNumber" in laps_df.columns:
    laps_df["LapNumber"] = laps_df["LapNumber"]
elif "Lap" in laps_df.columns:
    laps_df["LapNumber"] = laps_df["Lap"]
elif "CurrentLap" in laps_df.columns:
    laps_df["LapNumber"] = laps_df["CurrentLap"]
else:
    st.error(f"No lap number column found in lap data. Available columns: {list(laps_df.columns)}")
    st.stop()

laps_df = laps_df[
    (laps_df["DriverName"].notna()) &
    (laps_df["DriverName"] != "") &
    (laps_df["DriverName"] != "Server - Spectator") &
    (laps_df["LapTime"] < 999999999) &
    (laps_df["LapTime"] > 0)
].copy()

# Clean types
laps_df["LapNumber"] = pd.to_numeric(laps_df["LapNumber"], errors="coerce")
laps_df["LapTime"] = pd.to_numeric(laps_df["LapTime"], errors="coerce")

laps_df = laps_df.dropna(subset=["LapNumber", "LapTime"])
laps_df["LapNumber"] = laps_df["LapNumber"].astype(int)
laps_df["LapTime"] = laps_df["LapTime"].astype(int)

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

st.subheader("Lap Time Trend by Driver")

lap_chart_df = laps_df.pivot_table(
    index="LapNumber",
    columns="DriverName",
    values="LapTime",
    aggfunc="mean"
).sort_index()

st.line_chart(lap_chart_df)

st.subheader("Fastest Laps Ranking")

fastest_laps_df = (
    laps_df.groupby("DriverName", as_index=False)["LapTime"]
    .min()
    .sort_values("LapTime", ascending=True)
    .reset_index(drop=True)
)

fastest_laps_df["Position"] = fastest_laps_df.index + 1
fastest_laps_df["LapTimeFormatted"] = fastest_laps_df["LapTime"].apply(ms_to_laptime)

fastest_display_df = fastest_laps_df[["Position", "DriverName", "LapTimeFormatted"]].copy()
fastest_display_df.columns = ["Pos", "Driver", "Fastest Lap"]

st.dataframe(fastest_display_df, use_container_width=True, hide_index=True)

st.subheader("Average Pace by Driver")

average_pace_df = (
    laps_df.groupby("DriverName", as_index=False)["LapTime"]
    .mean()
    .sort_values("LapTime", ascending=True)
    .reset_index(drop=True)
)

average_pace_df["Position"] = average_pace_df.index + 1
average_pace_df["AverageLapFormatted"] = average_pace_df["LapTime"].round().astype(int).apply(ms_to_laptime)

average_display_df = average_pace_df[["Position", "DriverName", "AverageLapFormatted"]].copy()
average_display_df.columns = ["Pos", "Driver", "Average Lap"]

st.dataframe(average_display_df, use_container_width=True, hide_index=True)

st.subheader("Driver Drill-Down")

drivers = sorted(laps_df["DriverName"].unique().tolist())
selected_driver = st.selectbox("Select Driver", drivers)

driver_laps_df = laps_df[laps_df["DriverName"] == selected_driver].copy()
driver_laps_df = driver_laps_df.sort_values("LapNumber")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Driver", selected_driver)
with col2:
    best_driver_lap = driver_laps_df["LapTime"].min()
    st.metric("Best Lap", ms_to_laptime(best_driver_lap))
with col3:
    avg_driver_lap = int(round(driver_laps_df["LapTime"].mean()))
    st.metric("Average Lap", ms_to_laptime(avg_driver_lap))

driver_chart_df = driver_laps_df[["LapNumber", "LapTime"]].copy().set_index("LapNumber")
st.line_chart(driver_chart_df)

st.subheader("Driver Lap Table")

driver_table_df = driver_laps_df[["LapNumber", "LapTime"]].copy()
driver_table_df["LapTime"] = driver_table_df["LapTime"].apply(ms_to_laptime)
driver_table_df.columns = ["Lap", "Lap Time"]

st.dataframe(driver_table_df, use_container_width=True, hide_index=True)
