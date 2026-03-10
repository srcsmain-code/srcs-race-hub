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

laps_df = laps_df[
    (laps_df["DriverName"].notna()) &
    (laps_df["DriverName"] != "") &
    (laps_df["DriverName"] != "Server - Spectator") &
    (laps_df["LapTime"] < 999999999) &
    (laps_df["LapTime"] > 0)
].copy()

if laps_df.empty:
    st.warning("No valid lap data available for this round.")
    st.stop()

# Build lap number from timestamp order per driver
if "Timestamp" in laps_df.columns:
    laps_df["Timestamp"] = pd.to_numeric(laps_df["Timestamp"], errors="coerce")
    laps_df = laps_df.dropna(subset=["Timestamp"])
    laps_df = laps_df.sort_values(["DriverName", "Timestamp"]).copy()
else:
    laps_df = laps_df.reset_index(drop=True).copy()

laps_df["LapNumber"] = laps_df.groupby("DriverName").cumcount() + 1

# Clean numeric types
laps_df["LapTime"] = pd.to_numeric(laps_df["LapTime"], errors="coerce")
laps_df = laps_df.dropna(subset=["LapTime"])
laps_df["LapTime"] = laps_df["LapTime"].astype(int)
laps_df["LapNumber"] = laps_df["LapNumber"].astype(int)

# Winner = P1 in selected results
winner_name = None
if not selected_results_df.empty:
    winner_row = selected_results_df.sort_values("Position").iloc[0]
    winner_name = winner_row["DriverName"]

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
fastest_laps_df["Gap to Fastest (ms)"] = fastest_laps_df["LapTime"] - fastest_laps_df["LapTime"].min()
fastest_laps_df["Fastest Lap"] = fastest_laps_df["LapTime"].apply(ms_to_laptime)
fastest_laps_df["Gap to Fastest"] = fastest_laps_df["Gap to Fastest (ms)"].apply(
    lambda x: "0:00.000" if x == 0 else ms_to_laptime(int(x))
)
fastest_laps_df["Fastest Lap Marker"] = fastest_laps_df["DriverName"].apply(
    lambda x: "⭐" if x == selected_summary["Fastest Lap Driver"] else ""
)

fastest_display_df = fastest_laps_df[[
    "Position", "DriverName", "Fastest Lap", "Gap to Fastest", "Fastest Lap Marker"
]].copy()
fastest_display_df.columns = ["Pos", "Driver", "Fastest Lap", "Gap", "Marker"]

st.dataframe(fastest_display_df, use_container_width=True, hide_index=True)

st.subheader("Average Pace by Driver")

average_pace_df = (
    laps_df.groupby("DriverName", as_index=False)["LapTime"]
    .mean()
    .sort_values("LapTime", ascending=True)
    .reset_index(drop=True)
)

average_pace_df["Position"] = average_pace_df.index + 1
average_pace_df["Average Lap"] = average_pace_df["LapTime"].round().astype(int).apply(ms_to_laptime)

st.dataframe(
    average_pace_df[["Position", "DriverName", "Average Lap"]].rename(
        columns={"Position": "Pos", "DriverName": "Driver"}
    ),
    use_container_width=True,
    hide_index=True
)

st.subheader("Pace Delta to Race Winner")

winner_avg_lap = None
if winner_name and winner_name in average_pace_df["DriverName"].values:
    winner_avg_lap = average_pace_df.loc[
        average_pace_df["DriverName"] == winner_name, "LapTime"
    ].iloc[0]

pace_delta_df = average_pace_df.copy()
if winner_avg_lap is not None:
    pace_delta_df["Delta to Winner (ms)"] = (pace_delta_df["LapTime"] - winner_avg_lap).round().astype(int)
    pace_delta_df["Delta to Winner"] = pace_delta_df["Delta to Winner (ms)"].apply(
        lambda x: "0:00.000" if x == 0 else ms_to_laptime(int(x))
    )
else:
    pace_delta_df["Delta to Winner"] = "-"

pace_delta_display_df = pace_delta_df[[
    "Position", "DriverName", "Average Lap", "Delta to Winner"
]].copy()
pace_delta_display_df.columns = ["Pos", "Driver", "Average Lap", "Delta to Winner"]

st.dataframe(pace_delta_display_df, use_container_width=True, hide_index=True)

st.subheader("Lap Consistency by Driver")

consistency_df = (
    laps_df.groupby("DriverName", as_index=False)["LapTime"]
    .agg(["std", "mean", "count"])
    .reset_index()
)

consistency_df.columns = ["DriverName", "StdDev", "MeanLap", "LapCount"]
consistency_df["StdDev"] = consistency_df["StdDev"].fillna(0)
consistency_df = consistency_df.sort_values("StdDev", ascending=True).reset_index(drop=True)
consistency_df["Position"] = consistency_df.index + 1
consistency_df["Consistency"] = consistency_df["StdDev"].round().astype(int).apply(ms_to_laptime)

consistency_display_df = consistency_df[[
    "Position", "DriverName", "LapCount", "Consistency"
]].copy()
consistency_display_df.columns = ["Pos", "Driver", "Laps Counted", "Consistency"]

st.dataframe(consistency_display_df, use_container_width=True, hide_index=True)

st.subheader("Driver Drill-Down")

drivers = sorted(laps_df["DriverName"].unique().tolist())
selected_driver = st.selectbox("Select Driver", drivers)

driver_laps_df = laps_df[laps_df["DriverName"] == selected_driver].copy()
driver_laps_df = driver_laps_df.sort_values("LapNumber")

best_driver_lap = driver_laps_df["LapTime"].min()
avg_driver_lap = int(round(driver_laps_df["LapTime"].mean()))
driver_std_dev = driver_laps_df["LapTime"].std()
driver_std_dev_ms = 0 if pd.isna(driver_std_dev) else int(round(driver_std_dev))

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Driver", selected_driver)
with col2:
    st.metric("Best Lap", ms_to_laptime(best_driver_lap))
with col3:
    st.metric("Average Lap", ms_to_laptime(avg_driver_lap))
with col4:
    st.metric("Consistency", ms_to_laptime(driver_std_dev_ms))

# Highlight fastest lap in driver table
driver_laps_df["IsFastestLap"] = driver_laps_df["LapTime"] == best_driver_lap
driver_laps_df["Fastest Marker"] = driver_laps_df["IsFastestLap"].apply(lambda x: "⭐" if x else "")

driver_chart_df = driver_laps_df[["LapNumber", "LapTime"]].copy().set_index("LapNumber")
st.line_chart(driver_chart_df)

st.subheader("Driver Lap Table")

driver_table_df = driver_laps_df[["LapNumber", "LapTime", "Fastest Marker"]].copy()
driver_table_df["LapTime"] = driver_table_df["LapTime"].apply(ms_to_laptime)
driver_table_df.columns = ["Lap", "Lap Time", "Marker"]

st.dataframe(driver_table_df, use_container_width=True, hide_index=True)
