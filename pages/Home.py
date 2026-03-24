import streamlit as st
import pandas as pd
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping, calculate_team_standings
from engine.driver_metrics import calculate_driver_standings
from utils.formatting import ms_to_laptime, ms_to_racetime
from utils.style import apply_srcs_style

st.set_page_config(
    page_title="SRCS Race Hub",
    page_icon="🏁",
    layout="wide"
)

apply_srcs_style()

HEADER_IMAGE = Path("assets/header_HOME.png")

if HEADER_IMAGE.exists():
    st.image(str(HEADER_IMAGE), use_container_width=True)
    
DATA_DIR = Path("data")
TEAM_MAP_FILE = DATA_DIR / "driver_team_map.csv"

st.title("🏁 SRCS Race Hub")
st.subheader("Sim Racing Championship Series — Race Hub Control Center")

st.markdown(
    """
Welcome to the official SRCS Race Hub.

Use this control center to track the championship, review the latest round,
explore pace analysis, compare drivers and teams, and monitor the season story as it unfolds.
"""
)

if not DATA_DIR.exists():
    st.error("Data folder not found. Please create the data folder and upload race files.")
    st.stop()

race_files, all_results, round_summaries, raw_race_data = load_all_race_results(DATA_DIR)

if not race_files or not all_results:
    st.warning("No race data available yet.")
    st.stop()

season_results_df = pd.concat(all_results, ignore_index=True)

if TEAM_MAP_FILE.exists():
    season_results_df = apply_team_mapping(season_results_df, TEAM_MAP_FILE)
else:
    season_results_df["Team"] = "Unknown"

driver_standings_df = calculate_driver_standings(season_results_df)
team_standings_df = calculate_team_standings(season_results_df)

latest_round_df = all_results[-1].copy()
latest_summary = round_summaries[-1]

if TEAM_MAP_FILE.exists():
    latest_round_df = apply_team_mapping(latest_round_df, TEAM_MAP_FILE)
else:
    latest_round_df["Team"] = "Unknown"

latest_round_df = latest_round_df.sort_values("Position").reset_index(drop=True)

winner_row = latest_round_df.iloc[0]
pole_row = latest_round_df.sort_values("GridPosition").iloc[0]
podium_df = latest_round_df.head(3).copy()

st.subheader("Season Snapshot")

round_label = str(latest_summary["Round"]).split("—")[0].strip()
if round_label == latest_summary["Round"]:
    round_label = str(latest_summary["Round"]).split("-")[0].strip()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Rounds Loaded", len(race_files))

with c2:
    st.metric("Latest Round", round_label)
    st.caption(latest_summary["Grand Prix"])

with c3:
    st.metric("Latest Winner", winner_row["DriverName"])
    st.caption(f"Team: {winner_row['Team']}")

with c4:
    st.metric("Fastest Lap", latest_summary["Fastest Lap Time"])
    st.caption(latest_summary["Fastest Lap Driver"])

left_col, right_col = st.columns([1.4, 1])

with left_col:
    st.subheader("Latest Round Overview")

    latest_info_df = pd.DataFrame([
        {"Item": "Grand Prix", "Value": latest_summary["Grand Prix"]},
        {"Item": "Track", "Value": latest_summary["Track"]},
        {"Item": "Session Type", "Value": latest_summary["Session Type"]},
        {"Item": "Winner", "Value": winner_row["DriverName"]},
        {"Item": "Pole", "Value": pole_row["DriverName"]},
        {"Item": "Fastest Lap", "Value": f"{latest_summary['Fastest Lap Driver']} ({latest_summary['Fastest Lap Time']})"},
    ])

    st.dataframe(latest_info_df, use_container_width=True, hide_index=True)

    st.subheader("Latest Round Podium")

    podium_display_df = podium_df[[
        "Position", "DriverName", "Team", "Points", "BestLap", "TotalTime"
    ]].copy()

    podium_display_df.columns = ["Pos", "Driver", "Team", "Points", "Best Lap", "Race Time"]
    podium_display_df["Best Lap"] = podium_display_df["Best Lap"].apply(ms_to_laptime)
    podium_display_df["Race Time"] = podium_display_df["Race Time"].apply(ms_to_racetime)

    st.dataframe(podium_display_df, use_container_width=True, hide_index=True)

with right_col:
    st.subheader("Quick Navigation")

    nav_df = pd.DataFrame([
        {"Page": "Overview", "Purpose": "Round summary and headline race story"},
        {"Page": "Results Center", "Purpose": "Official classification and points"},
        {"Page": "Lap Time Lab", "Purpose": "Pace, fastest laps, and driver drill-down"},
        {"Page": "Position Tracker", "Purpose": "Grid vs finish and positions gained/lost"},
        {"Page": "Driver Analyzer", "Purpose": "Season-long view of one driver"},
        {"Page": "Team Battle", "Purpose": "Constructors' Championship and team trends"},
        {"Page": "Incident Center", "Purpose": "Steward notes, penalties, and incidents"},
        {"Page": "Awards", "Purpose": "Round awards and standout performers"},
        {"Page": "Season Impact", "Purpose": "How a round changed both championships"},
    ])

    st.dataframe(nav_df, use_container_width=True, hide_index=True)

st.subheader("Championship Leaders")

stand_col1, stand_col2 = st.columns(2)

with stand_col1:
    st.markdown("### Drivers' Top 5")
    st.dataframe(driver_standings_df.head(5), use_container_width=True, hide_index=True)

with stand_col2:
    st.markdown("### Constructors' Top 5")
    st.dataframe(team_standings_df.head(5), use_container_width=True, hide_index=True)

st.subheader("Latest Round Points Scorers")

points_df = latest_round_df[latest_round_df["Points"] > 0][["DriverName", "Points"]].copy()
points_df.columns = ["Driver", "Points"]
points_df = points_df.sort_values("Points", ascending=False).set_index("Driver")

st.bar_chart(points_df)

st.subheader("Latest Classification Snapshot")

classification_df = latest_round_df[[
    "Position", "DriverName", "Team", "GridPosition", "NumLaps", "Points"
]].copy()

classification_df.columns = ["Pos", "Driver", "Team", "Grid", "Laps", "Points"]

st.dataframe(classification_df, use_container_width=True, hide_index=True)

st.caption(
    "SRCS Race Hub Control Center — use the left sidebar to open race analysis, team battle, "
    "awards, incidents, and season impact pages."
)
