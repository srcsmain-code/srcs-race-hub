import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping
from engine.driver_metrics import calculate_driver_standings
from engine.race_metrics import prepare_laps_dataframe
from engine.incident_metrics import (
    prepare_events_dataframe,
    filter_incident_events,
    calculate_driver_incident_counts,
)
from utils.formatting import ms_to_laptime
from utils.style import apply_srcs_style

st.set_page_config(page_title="Driver Analyzer", page_icon="🧑‍💼", layout="wide")
apply_srcs_style()

st.markdown("""
<div class="srcs-hero">
    <div class="srcs-hero-title">DRIVER ANALYZER</div>
    <div class="srcs-hero-subtitle">Season performance intelligence, pace profile, and incident review</div>
</div>
""", unsafe_allow_html=True)

DATA_DIR = Path("data")
TEAM_MAP_FILE = DATA_DIR / "driver_team_map.csv"

if not DATA_DIR.exists():
    st.error("Data folder not found.")
    st.stop()

race_files, all_results, round_summaries, raw_race_data = load_all_race_results(DATA_DIR)

if not race_files or not all_results:
    st.warning("No race data available.")
    st.stop()

season_results_df = pd.concat(all_results, ignore_index=True)

if TEAM_MAP_FILE.exists():
    season_results_df = apply_team_mapping(season_results_df, TEAM_MAP_FILE)
else:
    season_results_df["Team"] = "Unknown"

driver_standings = calculate_driver_standings(season_results_df)
drivers = sorted(season_results_df["DriverName"].dropna().unique().tolist())

selected_driver = st.selectbox("Select Driver", drivers)

driver_df = season_results_df[season_results_df["DriverName"] == selected_driver].copy()

if driver_df.empty:
    st.warning("No data for this driver yet.")
    st.stop()

driver_df["RoundSort"] = driver_df["Round"].str.extract(r"Round (\d+)").astype(float)
driver_df = driver_df.sort_values(["RoundSort", "Round"]).reset_index(drop=True)

# ---------------------------------------------------
# BUILD SEASON LAPS DATASET
# ---------------------------------------------------
season_laps = []
for results_df, race_data, round_summary in zip(all_results, raw_race_data, round_summaries):
    laps_df = prepare_laps_dataframe(race_data)
    if laps_df.empty:
        continue

    round_name = round_summary["Round"]
    laps_df["Round"] = round_name

    round_team_map = season_results_df[
        season_results_df["Round"] == round_name
    ][["Round", "DriverName", "Team"]].drop_duplicates()

    laps_df = laps_df.merge(
        round_team_map,
        on=["Round", "DriverName"],
        how="left"
    )
    laps_df["Team"] = laps_df["Team"].fillna("Unknown")
    season_laps.append(laps_df)

if season_laps:
    season_laps_df = pd.concat(season_laps, ignore_index=True)
else:
    season_laps_df = pd.DataFrame()

driver_laps_df = season_laps_df[season_laps_df["DriverName"] == selected_driver].copy() if not season_laps_df.empty else pd.DataFrame()

# ---------------------------------------------------
# BUILD SEASON INCIDENT DATASET
# ---------------------------------------------------
season_incidents = []

for race_data, round_summary in zip(raw_race_data, round_summaries):
    events_df = prepare_events_dataframe(race_data)
    incident_df = filter_incident_events(events_df)

    if incident_df.empty:
        continue

    incident_df["Round"] = round_summary["Round"]
    incident_df["Grand Prix"] = round_summary["Grand Prix"]
    season_incidents.append(incident_df)

if season_incidents:
    season_incidents_df = pd.concat(season_incidents, ignore_index=True)
else:
    season_incidents_df = pd.DataFrame()

driver_incidents_df = (
    season_incidents_df[season_incidents_df["DriverName"] == selected_driver].copy()
    if not season_incidents_df.empty else pd.DataFrame()
)

# ---------------------------------------------------
# DRIVER SUMMARY
# ---------------------------------------------------
st.markdown('<div class="srcs-section">Driver Summary</div>', unsafe_allow_html=True)

total_points = int(driver_df["Points"].sum())
races = len(driver_df)
best_finish = int(driver_df["Position"].min())
avg_finish = round(driver_df["Position"].mean(), 2)
best_grid = int(driver_df["GridPosition"].min())
avg_grid = round(driver_df["GridPosition"].mean(), 2)
positions_gained_total = int((driver_df["GridPosition"] - driver_df["Position"]).sum())
positions_gained_avg = round((driver_df["GridPosition"] - driver_df["Position"]).mean(), 2)

driver_position_match = driver_standings.loc[
    driver_standings["Driver"] == selected_driver,
    "Pos"
]

if driver_position_match.empty:
    st.error("Could not determine championship position for this driver.")
    st.stop()

driver_position = int(driver_position_match.iloc[0])
team = driver_df.iloc[-1]["Team"]

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    st.metric("Championship Pos", driver_position)
with c2:
    st.metric("Team", team)
with c3:
    st.metric("Points", total_points)
with c4:
    st.metric("Best Finish", f"P{best_finish}")
with c5:
    st.metric("Average Finish", avg_finish)
with c6:
    st.metric("Avg Pos Gain/Loss", positions_gained_avg)

# ---------------------------------------------------
# STRONGER PROFILE BLOCK
# ---------------------------------------------------
st.markdown('<div class="srcs-section">Pace / Cleanliness / Racecraft Profile</div>', unsafe_allow_html=True)

# Pace metrics
if not driver_laps_df.empty:
    best_lap_ms = int(driver_laps_df["LapTime"].min())
    avg_lap_ms = int(round(driver_laps_df["LapTime"].mean()))
    std_lap_ms = driver_laps_df["LapTime"].std()
    std_lap_ms = 0 if pd.isna(std_lap_ms) else int(round(std_lap_ms))
    median_lap_ms = int(round(driver_laps_df["LapTime"].median()))
    laps_counted = int(len(driver_laps_df))
else:
    best_lap_ms = avg_lap_ms = std_lap_ms = median_lap_ms = 0
    laps_counted = 0

# Incident metrics
if not driver_incidents_df.empty:
    incident_count = int(len(driver_incidents_df))
    max_impact = float(driver_incidents_df["ImpactSpeed"].fillna(0).max())
    avg_impact = round(float(driver_incidents_df["ImpactSpeed"].fillna(0).mean()), 1)
else:
    incident_count = 0
    max_impact = 0.0
    avg_impact = 0.0

p1, p2, p3, p4, p5, p6 = st.columns(6)
with p1:
    st.metric("Best Lap", ms_to_laptime(best_lap_ms) if best_lap_ms > 0 else "-")
with p2:
    st.metric("Average Lap", ms_to_laptime(avg_lap_ms) if avg_lap_ms > 0 else "-")
with p3:
    st.metric("Median Lap", ms_to_laptime(median_lap_ms) if median_lap_ms > 0 else "-")
with p4:
    st.metric("Consistency", ms_to_laptime(std_lap_ms) if std_lap_ms >= 0 else "-")
with p5:
    st.metric("Incident Count", incident_count)
with p6:
    st.metric("Max Impact Speed", round(max_impact, 1))

profile_left, profile_right = st.columns([1.2, 1])

with profile_left:
    profile_df = pd.DataFrame([
        {"Metric": "Races Entered", "Value": races},
        {"Metric": "Laps Counted", "Value": laps_counted},
        {"Metric": "Best Grid", "Value": f"P{best_grid}"},
        {"Metric": "Average Grid", "Value": avg_grid},
        {"Metric": "Total Positions Gained/Lost", "Value": positions_gained_total},
        {"Metric": "Incident Count", "Value": incident_count},
        {"Metric": "Average Impact Speed", "Value": avg_impact},
    ])
    st.dataframe(profile_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------
# RADAR CHART
# ---------------------------------------------------
with profile_right:
    st.markdown("#### Performance Radar")

    # Build season-wide driver metrics for normalization
    all_driver_metrics = []

    for driver_name in drivers:
        d_results = season_results_df[season_results_df["DriverName"] == driver_name].copy()
        d_laps = season_laps_df[season_laps_df["DriverName"] == driver_name].copy() if not season_laps_df.empty else pd.DataFrame()
        d_incidents = season_incidents_df[season_incidents_df["DriverName"] == driver_name].copy() if not season_incidents_df.empty else pd.DataFrame()

        avg_finish_driver = d_results["Position"].mean() if not d_results.empty else None
        pos_gain_driver = (d_results["GridPosition"] - d_results["Position"]).mean() if not d_results.empty else 0

        avg_lap_driver = d_laps["LapTime"].mean() if not d_laps.empty else None
        std_driver = d_laps["LapTime"].std() if not d_laps.empty else None
        best_lap_driver = d_laps["LapTime"].min() if not d_laps.empty else None

        incident_rate_driver = (len(d_incidents) / max(len(d_results), 1)) if not d_results.empty else 0

        all_driver_metrics.append({
            "DriverName": driver_name,
            "AvgFinish": avg_finish_driver,
            "PosGainAvg": pos_gain_driver,
            "AvgLapMs": avg_lap_driver,
            "StdDevMs": 0 if pd.isna(std_driver) else std_driver if std_driver is not None else None,
            "BestLapMs": best_lap_driver,
            "IncidentRate": incident_rate_driver,
        })

    metrics_df = pd.DataFrame(all_driver_metrics)

    def normalize_inverse(series, value):
        valid = series.dropna()
        if valid.empty:
            return 50
        min_v = valid.min()
        max_v = valid.max()
        if max_v == min_v:
            return 100
        # lower is better
        return round(100 * (max_v - value) / (max_v - min_v), 1)

    def normalize_direct(series, value):
        valid = series.dropna()
        if valid.empty:
            return 50
        min_v = valid.min()
        max_v = valid.max()
        if max_v == min_v:
            return 100
        # higher is better
        return round(100 * (value - min_v) / (max_v - min_v), 1)

    selected_metric_row = metrics_df[metrics_df["DriverName"] == selected_driver].iloc[0]

    radar_values = {
        "Pace": normalize_inverse(metrics_df["AvgLapMs"], selected_metric_row["AvgLapMs"]) if pd.notna(selected_metric_row["AvgLapMs"]) else 0,
        "Consistency": normalize_inverse(metrics_df["StdDevMs"], selected_metric_row["StdDevMs"]) if pd.notna(selected_metric_row["StdDevMs"]) else 0,
        "Racecraft": normalize_direct(metrics_df["PosGainAvg"], selected_metric_row["PosGainAvg"]),
        "Cleanliness": normalize_inverse(metrics_df["IncidentRate"], selected_metric_row["IncidentRate"]),
        "Qualifying": normalize_inverse(season_results_df.groupby("DriverName")["GridPosition"].mean(), driver_df["GridPosition"].mean()),
        "Results": normalize_inverse(metrics_df["AvgFinish"], selected_metric_row["AvgFinish"]) if pd.notna(selected_metric_row["AvgFinish"]) else 0,
    }

    categories = list(radar_values.keys())
    values = list(radar_values.values())
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill="toself",
        name=selected_driver
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        margin=dict(l=30, r=30, t=30, b=30),
        height=420
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# RACE RESULTS HISTORY
# ---------------------------------------------------
st.markdown('<div class="srcs-section">Race Results</div>', unsafe_allow_html=True)

history_df = driver_df[[
    "Round",
    "Grand Prix",
    "Team",
    "GridPosition",
    "Position",
    "Points"
]].copy()

history_df.columns = [
    "Round",
    "Grand Prix",
    "Team",
    "Grid",
    "Finish",
    "Points"
]

st.dataframe(history_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------
# FINISH TREND
# ---------------------------------------------------
st.markdown('<div class="srcs-section">Finish Position Trend</div>', unsafe_allow_html=True)

trend_df = driver_df.copy()

finish_chart = alt.Chart(trend_df).mark_line(point=True).encode(
    x=alt.X("Round:N", title="Round"),
    y=alt.Y("Position:Q", title="Finish Position", scale=alt.Scale(reverse=True)),
    tooltip=["Round", "Grand Prix", "Position", "Points"]
).properties(height=350)

st.altair_chart(finish_chart, use_container_width=True)

# ---------------------------------------------------
# GRID VS FINISH
# ---------------------------------------------------
st.markdown('<div class="srcs-section">Grid vs Finish Performance</div>', unsafe_allow_html=True)

grid_chart_df = driver_df.copy()

grid_chart = alt.Chart(grid_chart_df).mark_circle(size=120).encode(
    x=alt.X("GridPosition:Q", title="Grid Position"),
    y=alt.Y("Position:Q", title="Finish Position", scale=alt.Scale(reverse=True)),
    tooltip=["Round", "Grand Prix", "GridPosition", "Position"]
).properties(height=350)

st.altair_chart(grid_chart, use_container_width=True)

# ---------------------------------------------------
# RACECRAFT
# ---------------------------------------------------
st.markdown('<div class="srcs-section">Racecraft: Positions Gained / Lost</div>', unsafe_allow_html=True)

racecraft_df = driver_df.copy()
racecraft_df["PositionChange"] = racecraft_df["GridPosition"] - racecraft_df["Position"]

racecraft_chart = alt.Chart(racecraft_df).mark_bar().encode(
    x=alt.X("Round:N", title="Round"),
    y=alt.Y("PositionChange:Q", title="Grid minus Finish"),
    tooltip=["Grand Prix", "GridPosition", "Position", "PositionChange"]
).properties(height=350)

st.altair_chart(racecraft_chart, use_container_width=True)

# ---------------------------------------------------
# INCIDENT TIMELINE
# ---------------------------------------------------
st.markdown('<div class="srcs-section">Incident Timeline</div>', unsafe_allow_html=True)

if not driver_incidents_df.empty:
    timeline_df = driver_incidents_df.copy()
    timeline_df["RoundSort"] = timeline_df["Round"].str.extract(r"Round (\d+)").astype(float)
    timeline_df = timeline_df.sort_values(["RoundSort", "Timestamp"]).reset_index(drop=True)

    # Timeline chart
    timeline_chart = alt.Chart(timeline_df).mark_circle(size=140).encode(
        x=alt.X("Round:N", title="Round"),
        y=alt.Y("ImpactSpeed:Q", title="Impact Speed"),
        color=alt.Color("Type:N", title="Incident Type"),
        tooltip=[
            alt.Tooltip("Round:N"),
            alt.Tooltip("Grand Prix:N"),
            alt.Tooltip("Type:N", title="Incident Type"),
            alt.Tooltip("OtherDriverName:N", title="Other Driver"),
            alt.Tooltip("ImpactSpeed:Q", title="Impact Speed"),
        ]
    ).properties(height=300)

    st.altair_chart(timeline_chart, use_container_width=True)

    incident_display_df = timeline_df[[
        "Round", "Grand Prix", "Type", "OtherDriverName", "ImpactSpeed", "AfterSessionEnd"
    ]].copy()

    incident_display_df.columns = [
        "Round", "Grand Prix", "Incident Type", "Other Driver", "Impact Speed", "After Session End"
    ]
    incident_display_df["Impact Speed"] = incident_display_df["Impact Speed"].round(1)

    st.dataframe(incident_display_df, use_container_width=True, hide_index=True)
else:
    st.info("No incident events recorded for this driver so far.")

# ---------------------------------------------------
# DRIVER INSIGHT
# ---------------------------------------------------
st.markdown('<div class="srcs-section">Driver Insight</div>', unsafe_allow_html=True)

if positions_gained_total > 0:
    racecraft_comment = "gains positions on average during races."
elif positions_gained_total < 0:
    racecraft_comment = "tends to lose positions during races."
else:
    racecraft_comment = "typically finishes close to where they start."

if incident_count == 0:
    cleanliness_comment = "has no recorded incident involvement so far."
elif incident_count <= races:
    cleanliness_comment = "has relatively low incident involvement across the season."
else:
    cleanliness_comment = "has been involved in incidents quite regularly."

pace_comment = (
    f"Their best lap is {ms_to_laptime(best_lap_ms)} and their average lap is {ms_to_laptime(avg_lap_ms)}."
    if best_lap_ms > 0 and avg_lap_ms > 0
    else "Pace data is still limited."
)

st.write(
    f"""
**{selected_driver}** is currently **P{driver_position}** in the championship with **{total_points} points**.

Their best finish so far is **P{best_finish}**, and they average **P{avg_finish}** across all races.

{pace_comment}

Across the season they **{racecraft_comment}**  
They also **{cleanliness_comment}**
"""
)

st.caption("SRCS Driver Analyzer — season performance intelligence.")
