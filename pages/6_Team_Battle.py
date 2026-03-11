import streamlit as st
import pandas as pd
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping, calculate_team_standings
from engine.race_metrics import prepare_laps_dataframe
from utils.formatting import ms_to_laptime
from utils.style import apply_srcs_style

st.set_page_config(page_title="Team Battle", page_icon="🏎️", layout="wide")
apply_srcs_style()

st.markdown("""
<div class="srcs-hero">
    <div class="srcs-hero-title">TEAM BATTLE</div>
    <div class="srcs-hero-subtitle">Constructors' championship, driver contribution, and teammate pace comparison</div>
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

st.markdown('<div class="srcs-section">Constructors\' Championship</div>', unsafe_allow_html=True)
st.dataframe(team_standings_df, use_container_width=True, hide_index=True)

# Team points progression
st.markdown('<div class="srcs-section">Team Points Progression</div>', unsafe_allow_html=True)

team_progression_df = season_results_df.pivot_table(
    index="Round",
    columns="Team",
    values="Points",
    aggfunc="sum",
    fill_value=0
).cumsum()

round_sort = (
    team_progression_df.index.to_series()
    .str.extract(r"Round (\d+)")[0]
    .astype(float)
)
team_progression_df = team_progression_df.assign(_RoundSort=round_sort.values)
team_progression_df = team_progression_df.sort_values("_RoundSort").drop(columns="_RoundSort")

st.line_chart(team_progression_df)

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
st.markdown('<div class="srcs-section">Points by Round</div>', unsafe_allow_html=True)

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
st.markdown('<div class="srcs-section">Driver Contribution</div>', unsafe_allow_html=True)

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

# Teammate pace comparison
st.markdown('<div class="srcs-section">Teammate Pace Comparison</div>', unsafe_allow_html=True)

pace_rows = []

for round_summary, race_data in zip(round_summaries, raw_race_data):
    round_name = round_summary["Round"]

    round_team_entries = team_df[team_df["Round"] == round_name].copy()
    round_team_entries = round_team_entries.sort_values("DriverName").reset_index(drop=True)

    if len(round_team_entries) < 2:
        continue

    laps_df = prepare_laps_dataframe(race_data)
    if laps_df.empty:
        continue

    team_drivers = round_team_entries["DriverName"].dropna().unique().tolist()

    if len(team_drivers) < 2:
        continue

    driver_averages = []
    for driver in team_drivers:
        driver_laps = laps_df[laps_df["DriverName"] == driver].copy()
        if driver_laps.empty:
            continue

        avg_lap = driver_laps["LapTime"].mean()
        best_lap = driver_laps["LapTime"].min()
        lap_count = len(driver_laps)

        driver_averages.append({
            "Round": round_name,
            "Driver": driver,
            "AverageLapMs": avg_lap,
            "BestLapMs": best_lap,
            "LapCount": lap_count
        })

    if len(driver_averages) < 2:
        continue

    round_pace_df = pd.DataFrame(driver_averages).sort_values("AverageLapMs", ascending=True).reset_index(drop=True)

    fastest_avg = round_pace_df.iloc[0]["AverageLapMs"]

    for _, row in round_pace_df.iterrows():
        pace_rows.append({
            "Round": row["Round"],
            "Driver": row["Driver"],
            "AverageLapMs": row["AverageLapMs"],
            "BestLapMs": row["BestLapMs"],
            "LapCount": int(row["LapCount"]),
            "DeltaToTeammateMs": row["AverageLapMs"] - fastest_avg
        })

if pace_rows:
    teammate_pace_df = pd.DataFrame(pace_rows)

    teammate_pace_df["Average Lap"] = teammate_pace_df["AverageLapMs"].round().astype(int).apply(ms_to_laptime)
    teammate_pace_df["Best Lap"] = teammate_pace_df["BestLapMs"].round().astype(int).apply(ms_to_laptime)

    def format_delta(ms):
        ms = int(round(ms))
        if ms <= 0:
            return "0:00.000"
        return ms_to_laptime(ms)

    teammate_pace_df["Delta to Teammate"] = teammate_pace_df["DeltaToTeammateMs"].apply(format_delta)

    pace_display_df = teammate_pace_df[[
        "Round", "Driver", "LapCount", "Average Lap", "Best Lap", "Delta to Teammate"
    ]].copy()

    pace_display_df.columns = [
        "Round", "Driver", "Laps Counted", "Average Lap", "Best Lap", "Delta to Teammate"
    ]

    st.dataframe(pace_display_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="srcs-section">Teammate Average Pace Delta Chart</div>', unsafe_allow_html=True)

    pace_chart_df = teammate_pace_df[["Round", "Driver", "DeltaToTeammateMs"]].copy()
    pace_chart_df["RoundDriver"] = pace_chart_df["Round"] + " — " + pace_chart_df["Driver"]
    pace_chart_df = pace_chart_df[["RoundDriver", "DeltaToTeammateMs"]].set_index("RoundDriver")
    pace_chart_df.columns = ["Average Pace Delta to Team Benchmark (ms)"]

    st.bar_chart(pace_chart_df)

    st.caption("Delta is measured to the faster average-lap teammate entry for that team in that round.")
else:
    st.info("No teammate pace comparison available yet. This usually requires at least two mapped team drivers with valid lap data in the same round.")

# Round-by-round team history
st.markdown('<div class="srcs-section">Round-by-Round Team History</div>', unsafe_allow_html=True)

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
st.markdown('<div class="srcs-section">Average Finish by Round</div>', unsafe_allow_html=True)

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
st.markdown('<div class="srcs-section">Team Notes</div>', unsafe_allow_html=True)

top_driver = driver_contrib_df.iloc[0]["Driver"] if not driver_contrib_df.empty else "N/A"
top_driver_points = int(driver_contrib_df.iloc[0]["Points"]) if not driver_contrib_df.empty else 0

st.write(
    f"{selected_team} is currently P{int(team_champ_pos)} in the Constructors' Championship "
    f"with {team_points} point(s). Their top points contributor so far is {top_driver} "
    f"with {top_driver_points} point(s)."
)
