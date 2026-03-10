import streamlit as st
import pandas as pd
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping
from engine.driver_metrics import calculate_driver_standings
from engine.team_metrics import calculate_team_standings
from utils.style import apply_srcs_style

st.set_page_config(page_title="Season Impact", layout="wide")
apply_srcs_style()

st.title("📈 Season Impact")

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

season_results_df = pd.concat(all_results, ignore_index=True)

if TEAM_MAP_FILE.exists():
    season_results_df = apply_team_mapping(season_results_df, TEAM_MAP_FILE)
else:
    season_results_df["Team"] = "Unknown"

# Add numeric round sort
season_results_df["RoundSort"] = season_results_df["Round"].str.extract(r"Round (\d+)").astype(float)

selected_round_num = float(selected_round.split(" - ")[0].replace("Round ", ""))

current_df = season_results_df[season_results_df["RoundSort"] <= selected_round_num].copy()
previous_df = season_results_df[season_results_df["RoundSort"] < selected_round_num].copy()

# Current standings
current_driver_standings = calculate_driver_standings(current_df).copy()
current_team_standings = calculate_team_standings(current_df).copy()

# Previous standings
if previous_df.empty:
    previous_driver_standings = pd.DataFrame(columns=["Pos", "Driver", "Points"])
    previous_team_standings = pd.DataFrame(columns=["Pos", "Team", "Points"])
else:
    previous_driver_standings = calculate_driver_standings(previous_df).copy()
    previous_team_standings = calculate_team_standings(previous_df).copy()

# Selected round data
selected_round_df = season_results_df[season_results_df["Round"] == selected_round].copy()

# --- Drivers impact ---
driver_impact_df = current_driver_standings.copy()
driver_impact_df = driver_impact_df.rename(columns={"Pos": "Current Pos", "Points": "Current Points"})

prev_driver_lookup = previous_driver_standings.rename(
    columns={"Pos": "Previous Pos", "Points": "Previous Points"}
)

driver_impact_df = driver_impact_df.merge(
    prev_driver_lookup[["Driver", "Previous Pos", "Previous Points"]],
    on="Driver",
    how="left"
)

driver_impact_df["Previous Pos"] = driver_impact_df["Previous Pos"].fillna(driver_impact_df["Current Pos"])
driver_impact_df["Previous Points"] = driver_impact_df["Previous Points"].fillna(0)

driver_impact_df["Position Change"] = driver_impact_df["Previous Pos"] - driver_impact_df["Current Pos"]
driver_impact_df["Points Gained This Round"] = (
    driver_impact_df["Current Points"] - driver_impact_df["Previous Points"]
).astype(int)

driver_impact_df["Movement"] = driver_impact_df["Position Change"].apply(
    lambda x: "Up" if x > 0 else ("Down" if x < 0 else "No Change")
)

driver_impact_df = driver_impact_df.sort_values(
    ["Current Pos", "Driver"], ascending=[True, True]
).reset_index(drop=True)

# --- Teams impact ---
team_impact_df = current_team_standings.copy()
team_impact_df = team_impact_df.rename(columns={"Pos": "Current Pos", "Points": "Current Points"})

prev_team_lookup = previous_team_standings.rename(
    columns={"Pos": "Previous Pos", "Points": "Previous Points"}
)

team_impact_df = team_impact_df.merge(
    prev_team_lookup[["Team", "Previous Pos", "Previous Points"]],
    on="Team",
    how="left"
)

team_impact_df["Previous Pos"] = team_impact_df["Previous Pos"].fillna(team_impact_df["Current Pos"])
team_impact_df["Previous Points"] = team_impact_df["Previous Points"].fillna(0)

team_impact_df["Position Change"] = team_impact_df["Previous Pos"] - team_impact_df["Current Pos"]
team_impact_df["Points Gained This Round"] = (
    team_impact_df["Current Points"] - team_impact_df["Previous Points"]
).astype(int)

team_impact_df["Movement"] = team_impact_df["Position Change"].apply(
    lambda x: "Up" if x > 0 else ("Down" if x < 0 else "No Change")
)

team_impact_df = team_impact_df.sort_values(
    ["Current Pos", "Team"], ascending=[True, True]
).reset_index(drop=True)

# Key impacts
top_driver_gainer = driver_impact_df.sort_values(
    ["Position Change", "Points Gained This Round"], ascending=[False, False]
).iloc[0]

top_team_gainer = team_impact_df.sort_values(
    ["Position Change", "Points Gained This Round"], ascending=[False, False]
).iloc[0]

round_top_scorer = (
    selected_round_df.groupby("DriverName", as_index=False)["Points"]
    .sum()
    .sort_values(["Points", "DriverName"], ascending=[False, True])
    .iloc[0]
)

round_top_team = (
    selected_round_df.groupby("Team", as_index=False)["Points"]
    .sum()
    .sort_values(["Points", "Team"], ascending=[False, True])
    .iloc[0]
)

# Header metrics
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Round", selected_round)
with c2:
    st.metric("Top Driver Gain", top_driver_gainer["Driver"])
with c3:
    st.metric("Top Team Gain", top_team_gainer["Team"])
with c4:
    st.metric("Top Round Scorer", round_top_scorer["DriverName"])

st.subheader("Drivers' Championship Impact")

driver_display_df = driver_impact_df[[
    "Current Pos",
    "Driver",
    "Current Points",
    "Previous Pos",
    "Position Change",
    "Points Gained This Round",
    "Movement"
]].copy()

driver_display_df.columns = [
    "Pos",
    "Driver",
    "Points",
    "Prev Pos",
    "Pos Change",
    "Round Gain",
    "Movement"
]

st.dataframe(driver_display_df, use_container_width=True, hide_index=True)

st.subheader("Constructors' Championship Impact")

team_display_df = team_impact_df[[
    "Current Pos",
    "Team",
    "Current Points",
    "Previous Pos",
    "Position Change",
    "Points Gained This Round",
    "Movement"
]].copy()

team_display_df.columns = [
    "Pos",
    "Team",
    "Points",
    "Prev Pos",
    "Pos Change",
    "Round Gain",
    "Movement"
]

st.dataframe(team_display_df, use_container_width=True, hide_index=True)

st.subheader("Selected Round Championship Contribution")

contrib_col1, contrib_col2 = st.columns(2)

with contrib_col1:
    round_driver_points_df = (
        selected_round_df.groupby("DriverName", as_index=False)["Points"]
        .sum()
        .sort_values(["Points", "DriverName"], ascending=[False, True])
    )
    round_driver_points_df.columns = ["Driver", "Points"]
    st.dataframe(round_driver_points_df, use_container_width=True, hide_index=True)

with contrib_col2:
    round_team_points_df = (
        selected_round_df.groupby("Team", as_index=False)["Points"]
        .sum()
        .sort_values(["Points", "Team"], ascending=[False, True])
    )
    round_team_points_df.columns = ["Team", "Points"]
    st.dataframe(round_team_points_df, use_container_width=True, hide_index=True)

st.subheader("Round Gain Charts")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    driver_gain_chart_df = driver_impact_df[["Driver", "Points Gained This Round"]].copy()
    driver_gain_chart_df = driver_gain_chart_df.sort_values(
        ["Points Gained This Round", "Driver"], ascending=[False, True]
    ).set_index("Driver")
    st.bar_chart(driver_gain_chart_df)

with chart_col2:
    team_gain_chart_df = team_impact_df[["Team", "Points Gained This Round"]].copy()
    team_gain_chart_df = team_gain_chart_df.sort_values(
        ["Points Gained This Round", "Team"], ascending=[False, True]
    ).set_index("Team")
    st.bar_chart(team_gain_chart_df)

st.subheader("Season Impact Notes")

st.write(
    f"After {selected_round}, the biggest driver standings mover is {top_driver_gainer['Driver']}, "
    f"while the strongest team impact comes from {top_team_gainer['Team']}. "
    f"The top individual scorer this round was {round_top_scorer['DriverName']} "
    f"with {int(round_top_scorer['Points'])} point(s), and the top team haul was "
    f"{round_top_team['Team']} with {int(round_top_team['Points'])} point(s)."
)
