import streamlit as st
import pandas as pd
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping, calculate_team_standings

st.set_page_config(page_title="Team Battle", layout="wide")

st.title("🏎️ Team Battle")

DATA_DIR = Path("data")
TEAM_MAP_FILE = DATA_DIR / "driver_team_map.csv"

if not DATA_DIR.exists():
    st.error("Data folder not found.")
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

teams = sorted(season_results_df["Team"].dropna().unique().tolist())

if not teams:
    st.warning("No team data available yet.")
    st.stop()

# Constructors standings
team_standings_df = calculate_team_standings(season_results_df)

st.subheader("Constructors' Championship")
st.dataframe(team_standings_df, use_container_width=True, hide_index=True)

# Team points progression
st.subheader("Team Points Progression")

team_progression_df = season_results_df.pivot_table(
    index="Round",
    columns="Team",
    values="Points",
    aggfunc="sum",
    fill_value=0
).cumsum()

# sort rounds properly if possible
round_sort = (
    team_progression_df.index.to_series()
    .str.extract(r"Round (\d+)")[0]
    .astype(float)
)
team_progression_df = team_progression_df.assign(_RoundSort=round_sort.values)
team_progression_df = team_progression_df.sort_values("_RoundSort").drop(columns="_RoundSort")

st.line_chart(team_progression_df)

# Team selector
selected_team = st.selectbox("Select Team", teams)

team_df = season_results_df[season_results_df["Team"] == selected_team].copy()

if team_df.empty:
    st.warning("No data available for this team.")
    st.stop()

team_df["RoundSort"] = team_df["Round"].str.extract(r"Round (\d+)").astype(float)
team_df = team_df.sort_values(["RoundSort", "Round"]).reset_index(drop=True)

# Team summary stats
team_points = int(team_df["Points"].sum())
rounds_contested = int(team_df["Round"].nunique())
best_finish = int(team_df["Position"].min())
avg_finish = round(team_df["Position"].mean(), 2)

team_champ_pos = team_standings_df.loc[
    team_standings_df["Team"] == selected_team, "Pos"
].iloc[0]

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Championship Pos", int(team_champ_pos))
with c2:
    st.metric("Total Points", team_points)
with c3:
    st.metric("Rounds Contested", rounds_contested)
with c4:
    st.metric("Best Finish", f"P{best_finish}")

st.caption(f"Average finish across all team entries: {avg_finish}")

# Team points by round
st.subheader("Points by Round")

team_points_round_df = (
    team_df.groupby("Round", as_index=False)["Points"]
    .sum()
    .copy()
)

team_points_round_df["RoundSort"] = team_points_round_df["Round"].str.extract(r"Round (\d+)").astype(float)
team_points_round_df = team_points_round_df.sort_values(["RoundSort", "Round"]).drop(columns=["RoundSort"])

points_chart_df = team_points_round_df.set_index("Round")
st.bar_chart(points_chart_df)

# Driver contribution
st.subheader("Driver Contribution")

driver_contrib_df = (
    team_df.groupby("DriverName", as_index=False)["Points"]
    .sum()
    .sort_values(["Points", "DriverName"], ascending=[False, True])
    .reset_index(drop=True)
)

driver_contrib_df.columns = ["Driver", "Points"]
st.dataframe(driver_contrib_df, use_container_width=True, hide_index=True)

driver_contrib_chart_df = driver_contrib_df.set_index("Driver")
st.bar_chart(driver_contrib_chart_df)

# Round-by-round team history
st.subheader("Round-by-Round Team History")

team_history_df = team_df[[
    "Round",
    "Grand Prix",
    "DriverName",
    "GridPosition",
    "Position",
    "Points"
]].copy()

team_history_df.columns = ["Round", "Grand Prix", "Driver", "Grid", "Finish", "Points"]
team_history_df = team_history_df.sort_values(["Round", "Driver"]).reset_index(drop=True)

st.dataframe(team_history_df, use_container_width=True, hide_index=True)

# Team average finish by round
st.subheader("Average Finish by Round")

avg_finish_round_df = (
    team_df.groupby("Round", as_index=False)["Position"]
    .mean()
    .rename(columns={"Position": "Average Finish"})
)

avg_finish_round_df["RoundSort"] = avg_finish_round_df["Round"].str.extract(r"Round (\d+)").astype(float)
avg_finish_round_df = avg_finish_round_df.sort_values(["RoundSort", "Round"]).drop(columns=["RoundSort"])

avg_finish_chart_df = avg_finish_round_df.set_index("Round")
st.line_chart(avg_finish_chart_df)

# Team notes
st.subheader("Team Notes")

top_driver = driver_contrib_df.iloc[0]["Driver"] if not driver_contrib_df.empty else "N/A"
top_driver_points = int(driver_contrib_df.iloc[0]["Points"]) if not driver_contrib_df.empty else 0

st.write(
    f"{selected_team} is currently P{int(team_champ_pos)} in the Constructors' Championship "
    f"with {team_points} point(s). Their top points contributor so far is {top_driver} "
    f"with {top_driver_points} point(s)."
)
