import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="Championship Dashboard", layout="wide")

st.title("🏆 Championship Dashboard")

DATA_DIR = Path("data")
TEAM_MAP_FILE = DATA_DIR / "driver_team_map.csv"

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

def parse_round_label(filename):
    name = filename.stem
    parts = name.split("_")
    if len(parts) >= 3 and parts[1].startswith("round"):
        round_part = parts[1].replace("round", "Round ")
        gp_part = " ".join(parts[2:]).replace("-", " ").title()
        return f"{round_part} - {gp_part}"
    return filename.stem

def load_race_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        race_data = json.load(f)

    results = race_data.get("Result", [])
    laps = race_data.get("Laps", [])

    results_df = pd.DataFrame(results)

    if results_df.empty:
        return None, None, None

    results_df = results_df[
        (results_df["DriverName"].notna()) &
        (results_df["DriverName"] != "") &
        (results_df["DriverName"] != "Server - Spectator") &
        (results_df["NumLaps"] > 0)
    ].copy()

    if results_df.empty:
        return None, None, None

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

    round_label = parse_round_label(file_path)
    grand_prix = " ".join(file_path.stem.split("_")[2:]).replace("-", " ").title()

    results_df["Round"] = round_label
    results_df["Grand Prix"] = grand_prix

    round_summary = {
        "Round": round_label,
        "Grand Prix": grand_prix,
        "Track": race_data.get("TrackName", "-"),
        "Session Type": race_data.get("Type", "-"),
        "Fastest Lap Driver": fastest_lap_driver or "-",
        "Fastest Lap Time": ms_to_laptime(fastest_lap_time)
    }

    return results_df, round_summary, race_data

if not DATA_DIR.exists():
    st.error("Data folder not found. Please create a data folder and upload race JSON files.")
    st.stop()

race_files = sorted(DATA_DIR.glob("*.json"))

if not race_files:
    st.warning("No race JSON files found in the data folder yet.")
    st.stop()

all_results = []
round_summaries = []

for race_file in race_files:
    results_df, round_summary, race_data = load_race_file(race_file)
    if results_df is not None:
        all_results.append(results_df)
        round_summaries.append(round_summary)

if not all_results:
    st.warning("No usable race result data found.")
    st.stop()

season_results_df = pd.concat(all_results, ignore_index=True)

# Add team mapping by Round + Driver
if TEAM_MAP_FILE.exists():
    team_map_df = pd.read_csv(TEAM_MAP_FILE)

    season_results_df = season_results_df.merge(
        team_map_df,
        how="left",
        left_on=["Round", "DriverName"],
        right_on=["Round", "Driver"]
    )
    season_results_df["Team"] = season_results_df["Team"].fillna("Unknown")
    season_results_df = season_results_df.drop(columns=["Driver"], errors="ignore")
else:
    season_results_df["Team"] = "Unknown"

# Drivers' standings
drivers_standings_df = (
    season_results_df.groupby("DriverName", as_index=False)["Points"]
    .sum()
    .sort_values(["Points", "DriverName"], ascending=[False, True])
    .reset_index(drop=True)
)

drivers_standings_df["Position"] = drivers_standings_df.index + 1
drivers_standings_df = drivers_standings_df[["Position", "DriverName", "Points"]]
drivers_standings_df.columns = ["Pos", "Driver", "Points"]

# Constructors' standings
teams_standings_df = (
    season_results_df.groupby("Team", as_index=False)["Points"]
    .sum()
    .sort_values(["Points", "Team"], ascending=[False, True])
    .reset_index(drop=True)
)

teams_standings_df["Position"] = teams_standings_df.index + 1
teams_standings_df = teams_standings_df[["Position", "Team", "Points"]]
teams_standings_df.columns = ["Pos", "Team", "Points"]

latest_round_df = all_results[-1].copy()
latest_summary = round_summaries[-1]

# Add team mapping to latest round too
if TEAM_MAP_FILE.exists():
    latest_round_df = latest_round_df.merge(
        team_map_df,
        how="left",
        left_on=["Round", "DriverName"],
        right_on=["Round", "Driver"]
    )
    latest_round_df["Team"] = latest_round_df["Team"].fillna("Unknown")
    latest_round_df = latest_round_df.drop(columns=["Driver"], errors="ignore")
else:
    latest_round_df["Team"] = "Unknown"

latest_display_df = latest_round_df[[
    "Position", "DriverName", "Team", "GridPosition", "NumLaps", "BestLap", "TotalTime", "Points"
]].copy()

latest_display_df.columns = ["Pos", "Driver", "Team", "Grid", "Laps", "Best Lap", "Race Time", "Points"]
latest_display_df["Best Lap"] = latest_display_df["Best Lap"].apply(ms_to_laptime)
latest_display_df["Race Time"] = latest_display_df["Race Time"].apply(ms_to_racetime)

top_col1, top_col2 = st.columns([2, 1])

with top_col1:
    st.subheader("Season Summary")
    stat1, stat2, stat3 = st.columns(3)
    with stat1:
        st.metric("Rounds Loaded", len(race_files))
    with stat2:
        st.metric("Latest Round", latest_summary["Round"])
    with stat3:
        st.metric("Latest GP", latest_summary["Grand Prix"])

with top_col2:
    st.subheader("Latest Fastest Lap")
    st.metric("Driver", latest_summary["Fastest Lap Driver"])
    st.caption(f"Time: {latest_summary['Fastest Lap Time']}")

stand_col1, stand_col2 = st.columns(2)

with stand_col1:
    st.subheader("Drivers' Championship")
    st.dataframe(drivers_standings_df, use_container_width=True, hide_index=True)

with stand_col2:
    st.subheader("Constructors' Championship")
    st.dataframe(teams_standings_df, use_container_width=True, hide_index=True)

st.subheader(f"Latest Round Results — {latest_summary['Round']}")
st.dataframe(latest_display_df, use_container_width=True, hide_index=True)

st.subheader("Drivers' Points Progression")
driver_progression_df = season_results_df.pivot_table(
    index="Round",
    columns="DriverName",
    values="Points",
    aggfunc="sum",
    fill_value=0
).cumsum()

st.line_chart(driver_progression_df)

st.subheader("Teams' Points Progression")
team_progression_df = season_results_df.pivot_table(
    index="Round",
    columns="Team",
    values="Points",
    aggfunc="sum",
    fill_value=0
).cumsum()

st.line_chart(team_progression_df)

st.subheader("Latest Round Summary")
summary_df = pd.DataFrame([latest_summary])
st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.subheader("Round-by-Round Points")
round_points_df = season_results_df[["Round", "DriverName", "Team", "Points"]].copy()
round_points_df.columns = ["Round", "Driver", "Team", "Points"]
st.dataframe(round_points_df, use_container_width=True, hide_index=True)
