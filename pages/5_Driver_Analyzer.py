import streamlit as st
import pandas as pd
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping
from engine.driver_metrics import calculate_driver_standings
from utils.formatting import ms_to_laptime, ms_to_racetime
from utils.style import apply_srcs_style

from components.track_benchmark_cards import render_track_benchmark_compact
from data.lap_benchmarks import TRACK_BENCHMARKS

st.set_page_config(page_title="Driver Analyzer", layout="wide")
apply_srcs_style()

st.title("🧑‍💼 Driver Analyzer")

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

drivers = sorted(season_results_df["DriverName"].unique().tolist())
selected_driver = st.selectbox("Select Driver", drivers)

driver_df = season_results_df[season_results_df["DriverName"] == selected_driver].copy()

if driver_df.empty:
    st.warning("No data available for this driver.")
    st.stop()

# Sort by round number if possible
driver_df["RoundSort"] = driver_df["Round"].str.extract(r"Round (\d+)").astype(float)
driver_df = driver_df.sort_values(["RoundSort", "Round"]).reset_index(drop=True)

# Championship position
driver_standings_df = calculate_driver_standings(season_results_df)
champ_pos = driver_standings_df.loc[
    driver_standings_df["Driver"] == selected_driver, "Pos"
].iloc[0]

# Summary stats
total_points = int(driver_df["Points"].sum())
rounds_entered = int(driver_df["Round"].nunique())
best_finish = int(driver_df["Position"].min())
avg_finish = round(driver_df["Position"].mean(), 2)
best_grid = int(driver_df["GridPosition"].min())
avg_grid = round(driver_df["GridPosition"].mean(), 2)

# Fastest laps count from round summaries
fastest_lap_count = sum(
    1 for summary in round_summaries
    if summary["Fastest Lap Driver"] == selected_driver
)

# Latest team / teams used
teams_used = sorted(driver_df["Team"].dropna().unique().tolist())
teams_used_text = ", ".join(teams_used) if teams_used else "Unknown"

# Summary row
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    st.metric("Championship Pos", int(champ_pos))
with c2:
    st.metric("Total Points", total_points)
with c3:
    st.metric("Rounds Entered", rounds_entered)
with c4:
    st.metric("Best Finish", f"P{best_finish}")
with c5:
    st.metric("Avg Finish", avg_finish)
with c6:
    st.metric("Fastest Laps", fastest_lap_count)

st.caption(f"Teams represented: {teams_used_text}")

# Secondary stats
st.subheader("Qualifying vs Race Snapshot")

q1, q2, q3, q4 = st.columns(4)
with q1:
    st.metric("Best Grid", f"P{best_grid}")
with q2:
    st.metric("Avg Grid", avg_grid)
with q3:
    avg_gain = round((driver_df["GridPosition"] - driver_df["Position"]).mean(), 2)
    st.metric("Avg Pos Gain/Loss", avg_gain)
with q4:
    best_points = int(driver_df["Points"].max())
    st.metric("Best Points Haul", best_points)

# =========================
# DRIVER / ROUND SELECTION
# =========================

st.subheader("Round Analysis")

round_options = driver_df["Round"].dropna().tolist()
selected_round = st.selectbox(
    "Select Round",
    round_options,
    index=len(round_options) - 1 if round_options else 0,
    key="driver_analysis_round"
)

selected_round_df = driver_df[driver_df["Round"] == selected_round].copy()

if selected_round_df.empty:
    st.warning("No round data available.")
    st.stop()

selected_round_row = selected_round_df.iloc[0]
selected_gp = selected_round_row["Grand Prix"]

# =========================
# MAP GRAND PRIX TO TRACK KEY
# =========================

def map_grand_prix_to_track_key(grand_prix_name: str) -> str | None:
    gp = str(grand_prix_name).strip().lower()

    mapping = {
        "australian grand prix": "melbourne",
        "bahrain grand prix": "bahrain",
        "miami grand prix": "miami",
        "monaco grand prix": "monaco",
        "british grand prix": "silverstone",
        "dutch grand prix": "zandvoort",
        "italian grand prix": "monza",
        "singapore grand prix": "singapore",
        "brazilian grand prix": "interlagos",
        "abu dhabi grand prix": "abu_dhabi",
    }

    return mapping.get(gp)

selected_track_key = map_grand_prix_to_track_key(selected_gp)

# =========================
# BENCHMARK BLOCK
# =========================

st.markdown(f"#### {selected_round} • {selected_gp}")

if selected_track_key:
    render_track_benchmark_compact(selected_track_key)
else:
    st.info("No track benchmark found for this round yet.")

# =========================
# DRIVER VS BENCHMARKS
# =========================

def lap_time_to_seconds(lap_str: str) -> float | None:
    try:
        mins, secs = str(lap_str).split(":")
        return int(mins) * 60 + float(secs)
    except Exception:
        return None

driver_bestlap_ms = selected_round_row.get("BestLap", None)

if pd.notna(driver_bestlap_ms):
    driver_bestlap_str = ms_to_laptime(driver_bestlap_ms)
else:
    driver_bestlap_str = None

if selected_track_key and driver_bestlap_str and selected_track_key in TRACK_BENCHMARKS:
    benchmark = TRACK_BENCHMARKS[selected_track_key]

    real_life_lap = benchmark["real_life_lap_record"]
    srcs_target_lap = benchmark["srcs_target_lap_time"]

    driver_bestlap_sec = lap_time_to_seconds(driver_bestlap_str)
    real_life_sec = lap_time_to_seconds(real_life_lap)
    srcs_target_sec = lap_time_to_seconds(srcs_target_lap)

    if (
        driver_bestlap_sec is not None
        and real_life_sec is not None
        and srcs_target_sec is not None
    ):
        delta_to_real_life = round(driver_bestlap_sec - real_life_sec, 3)
        delta_to_srcs_target = round(driver_bestlap_sec - srcs_target_sec, 3)

        b1, b2, b3 = st.columns(3)
        with b1:
            st.metric("Driver Best Lap", driver_bestlap_str)
        with b2:
            st.metric("Vs Real Life Record", f"+{delta_to_real_life:.3f}s")
        with b3:
            st.metric("Vs SRCS Target", f"{delta_to_srcs_target:+.3f}s")

# Points trend
st.subheader("Points by Round")

points_chart_df = driver_df[["Round", "Points"]].copy().set_index("Round")
st.bar_chart(points_chart_df)

# Finish trend
st.subheader("Finish Trend by Round")

finish_chart_df = driver_df[["Round", "Position"]].copy().set_index("Round")
st.line_chart(finish_chart_df)

# Round-by-round breakdown
st.subheader("Round-by-Round Breakdown")

breakdown_df = driver_df[[
    "Round",
    "Grand Prix",
    "Team",
    "GridPosition",
    "Position",
    "Points",
    "BestLap",
    "TotalTime"
]].copy()

breakdown_df["BestLap"] = breakdown_df["BestLap"].apply(ms_to_laptime)
breakdown_df["TotalTime"] = breakdown_df["TotalTime"].apply(ms_to_racetime)

breakdown_df.columns = [
    "Round",
    "Grand Prix",
    "Team",
    "Grid",
    "Finish",
    "Points",
    "Best Lap",
    "Race Time"
]

st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

# Performance notes
st.subheader("Driver Notes")

note_parts = [
    f"{selected_driver} is currently P{int(champ_pos)} in the championship",
    f"with {total_points} point(s) from {rounds_entered} round(s)",
    f"and a best finish of P{best_finish}"
]

if fastest_lap_count > 0:
    note_parts.append(f"plus {fastest_lap_count} fastest lap(s)")

if selected_track_key and driver_bestlap_str and selected_track_key in TRACK_BENCHMARKS:
    benchmark = TRACK_BENCHMARKS[selected_track_key]
    note_parts.append(
        f"for {selected_round}, the benchmark lap record is {benchmark['real_life_lap_record']} and the SRCS target is {benchmark['srcs_target_lap_time']}"
    )

st.write(", ".join(note_parts) + ".")

# Raw results table
st.subheader("Detailed Race Results")

detail_df = driver_df[[
    "Round",
    "DriverName",
    "Team",
    "GridPosition",
    "Position",
    "NumLaps",
    "Points"
]].copy()

detail_df.columns = ["Round", "Driver", "Team", "Grid", "Finish", "Laps", "Points"]

st.dataframe(detail_df, use_container_width=True, hide_index=True)
