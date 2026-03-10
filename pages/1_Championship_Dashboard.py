import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="Championship Dashboard", layout="wide")

st.title("🏆 Championship Dashboard")

DATA_FILE = Path("data/round1_australia_race.json")

POINTS_MAP = {
    1: 25,
    2: 18,
    3: 15,
    4: 12,
    5: 10,
    6: 8,
    7: 6,
    8: 4,
    9: 2,
    10: 1
}

def ms_to_laptime(ms):
    if ms is None or ms == 999999999 or ms == 0:
        return "-"
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    millis = ms % 1000
    return f"{minutes}:{seconds:02d}.{millis:03d}"

def ms_to_racetime(ms):
    if ms is None or ms == 0:
        return "-"
    total_seconds = ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    millis = ms % 1000
    return f"{minutes}:{seconds:02d}.{millis:03d}"

if not DATA_FILE.exists():
    st.error("Race file not found. Please upload data/round1_australia_race.json to GitHub.")
    st.stop()

with open(DATA_FILE, "r", encoding="utf-8") as f:
    race_data = json.load(f)

results = race_data.get("Result", [])
laps = race_data.get("Laps", [])

results_df = pd.DataFrame(results)

results_df = results_df[
    (results_df["DriverName"].notna()) &
    (results_df["DriverName"] != "") &
    (results_df["DriverName"] != "Server - Spectator") &
    (results_df["NumLaps"] > 0)
].copy()

results_df = results_df.sort_values(
    by=["NumLaps", "TotalTime"],
    ascending=[False, True]
).reset_index(drop=True)

results_df["Position"] = results_df.index + 1
results_df["Points"] = results_df["Position"].map(POINTS_MAP).fillna(0).astype(int)

classified_names = set(results_df["DriverName"].tolist())
valid_laps = [
    lap for lap in laps
    if lap.get("DriverName") in classified_names and lap.get("LapTime", 999999999) < 999999999
]

fastest_lap_driver = None
fastest_lap_time = None

if valid_laps:
    fastest_lap_entry = min(valid_laps, key=lambda x: x["LapTime"])
    fastest_lap_driver = fastest_lap_entry["DriverName"]
    fastest_lap_time = fastest_lap_entry["LapTime"]

if fastest_lap_driver:
    top10_names = set(results_df.head(10)["DriverName"].tolist())
    if fastest_lap_driver in top10_names:
        results_df.loc[results_df["DriverName"] == fastest_lap_driver, "Points"] += 1

display_df = results_df[[
    "Position", "DriverName", "GridPosition", "NumLaps", "BestLap", "TotalTime", "Points"
]].copy()

display_df.columns = ["Pos", "Driver", "Grid", "Laps", "Best Lap", "Race Time", "Points"]
display_df["Best Lap"] = display_df["Best Lap"].apply(ms_to_laptime)
display_df["Race Time"] = display_df["Race Time"].apply(ms_to_racetime)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Round 1 Results")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

with col2:
    st.subheader("Round Summary")
    st.metric("Grand Prix", "Australia")
    st.metric("Track", race_data.get("TrackName", "-"))
    st.metric("Session Type", race_data.get("Type", "-"))
    st.metric("Fastest Lap", fastest_lap_driver or "-")
    st.caption(f"Time: {ms_to_laptime(fastest_lap_time)}")

st.subheader("Points Scored")
points_chart = results_df[["DriverName", "Points"]].copy()
points_chart.columns = ["Driver", "Points"]
points_chart = points_chart.sort_values("Points", ascending=False).set_index("Driver")
st.bar_chart(points_chart)

st.subheader("Notes")
st.write("This page is now reading the real SRCS Round 1 race JSON file from the data folder.")
