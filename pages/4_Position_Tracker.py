import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping
from engine.race_metrics import (
    prepare_laps_dataframe,
    build_estimated_position_by_lap,
    build_estimated_overtake_summary,
)
from utils.style import apply_srcs_style

st.set_page_config(page_title="Position Tracker", page_icon="📍", layout="wide")
apply_srcs_style()

st.markdown("""
<div class="srcs-hero">
    <div class="srcs-hero-title">POSITION TRACKER</div>
    <div class="srcs-hero-subtitle">Estimated lap-end running order, net movement, and race evolution</div>
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

round_options = [summary["Round"] for summary in round_summaries]
selected_round = st.selectbox("Select Round", round_options, index=len(round_options) - 1)

selected_index = round_options.index(selected_round)
selected_results_df = all_results[selected_index].copy()
selected_summary = round_summaries[selected_index]
selected_race_data = raw_race_data[selected_index]

if TEAM_MAP_FILE.exists():
    selected_results_df = apply_team_mapping(selected_results_df, TEAM_MAP_FILE)
else:
    selected_results_df["Team"] = "Unknown"

selected_results_df = selected_results_df.sort_values("Position").reset_index(drop=True)
selected_results_df["Positions Gained"] = (
    selected_results_df["GridPosition"] - selected_results_df["Position"]
)
selected_results_df["Movement"] = selected_results_df["Positions Gained"].apply(
    lambda x: "Gained" if x > 0 else ("Lost" if x < 0 else "No Change")
)

biggest_mover_row = selected_results_df.sort_values(
    ["Positions Gained", "Position"], ascending=[False, True]
).iloc[0]

biggest_loser_row = selected_results_df.sort_values(
    ["Positions Gained", "Position"], ascending=[True, True]
).iloc[0]

winner_row = selected_results_df.sort_values("Position").iloc[0]
pole_row = selected_results_df.sort_values("GridPosition").iloc[0]

laps_df = prepare_laps_dataframe(selected_race_data)
position_df = build_estimated_position_by_lap(laps_df)
changes_df = build_estimated_overtake_summary(position_df)

st.markdown('<div class="srcs-section">Round Movement Summary</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Winner", winner_row["DriverName"])
    st.caption(f"Team: {winner_row['Team']}")

with c2:
    pole_lap = pole_row["BestLap"] if "BestLap" in pole_row.index else None
    st.metric("Pole", "Pole Sitter")
    st.caption(
        f"{pole_row['DriverName']}"
        + (f" • {pole_lap}" if pole_lap is not None else "")
    )

with c3:
    mover_gain = int(biggest_mover_row["Positions Gained"])
    st.metric("Biggest Mover", f"+{mover_gain}" if mover_gain >= 0 else str(mover_gain))
    st.caption(biggest_mover_row["DriverName"])

with c4:
    loser_gain = int(biggest_loser_row["Positions Gained"])
    st.metric("Biggest Loser", str(loser_gain))
    st.caption(biggest_loser_row["DriverName"])

st.caption(
    f"{selected_summary['Round']} • {selected_summary['Grand Prix']} • "
    f"{selected_summary['Track']} • {selected_summary['Session Type']}"
)

st.markdown('<div class="srcs-section">Grid vs Finish Tracker</div>', unsafe_allow_html=True)

tracker_df = selected_results_df[[
    "DriverName",
    "Team",
    "GridPosition",
    "Position",
    "Positions Gained",
    "Movement",
    "Points"
]].copy()

tracker_df.columns = [
    "Driver",
    "Team",
    "Grid",
    "Finish",
    "Net Gain/Loss",
    "Movement",
    "Points"
]

st.dataframe(tracker_df, use_container_width=True, hide_index=True)

st.markdown('<div class="srcs-section">Net Position Change Chart</div>', unsafe_allow_html=True)

position_chart_df = selected_results_df[[
    "DriverName",
    "Positions Gained"
]].copy()

position_chart_df.columns = ["Driver", "Net Gain/Loss"]
position_chart_df = position_chart_df.sort_values("Net Gain/Loss", ascending=True).set_index("Driver")
st.bar_chart(position_chart_df)

st.markdown('<div class="srcs-section">Estimated Position by Lap</div>', unsafe_allow_html=True)

if not position_df.empty:
    pos_chart_df = position_df.pivot_table(
        index="LapNumber",
        columns="DriverName",
        values="EstimatedPosition",
        aggfunc="first"
    ).sort_index()

    driver_team_df = selected_results_df[["DriverName", "Team"]].drop_duplicates()
    drivers = sorted(driver_team_df["DriverName"].dropna().unique().tolist())
    teams = sorted(driver_team_df["Team"].dropna().unique().tolist())

    f1, f2 = st.columns(2)

    with f1:
        selected_driver_filter = st.selectbox(
            "Focus on Driver",
            ["All Drivers"] + drivers,
            key="position_tracker_driver_filter"
        )

    with f2:
        selected_team_filter = st.selectbox(
            "Focus on Team",
            ["All Teams"] + teams,
            key="position_tracker_team_filter"
        )

    filtered_chart_df = pos_chart_df.copy()

    if selected_driver_filter != "All Drivers":
        if selected_driver_filter in filtered_chart_df.columns:
            filtered_chart_df = filtered_chart_df[[selected_driver_filter]]
    elif selected_team_filter != "All Teams":
        team_drivers = driver_team_df[
            driver_team_df["Team"] == selected_team_filter
        ]["DriverName"].tolist()

        team_drivers = [d for d in team_drivers if d in filtered_chart_df.columns]

        if team_drivers:
            filtered_chart_df = filtered_chart_df[team_drivers]

    # Build long dataframe for Altair
    chart_df = filtered_chart_df.reset_index().melt(
        "LapNumber",
        var_name="Driver",
        value_name="Position"
    )

    chart_df = chart_df.merge(
        driver_team_df,
        left_on="Driver",
        right_on="DriverName",
        how="left"
    )

    chart_df = chart_df.drop(columns=["DriverName"], errors="ignore")
    chart_df = chart_df.dropna(subset=["Position"]).copy()

    # SRCS team accent registry
    team_colors = {
        "McLaren": "#FF8700",
        "Ferrari": "#C00000",
        "Mercedes": "#00A19B",
        "Red Bull": "#0B1E3C",
        "Williams": "#005AFF",
        "Aston Martin": "#006F62",
        "Alpine": "#0090FF",
        "Haas": "#8B0000",
        "Audi": "#BB0A30",
        "Racing Bulls": "#1A1F3B",
        "Unknown": "#C0C0C0",
    }

    # End-of-line labels
    last_points_df = chart_df.sort_values(["Driver", "LapNumber"]).groupby("Driver", as_index=False).tail(1).copy()

    # Dynamic color domain/range based on filtered teams actually present
    teams_present = chart_df["Team"].fillna("Unknown").unique().tolist()
    domain = [t for t in team_colors.keys() if t in teams_present]
    range_colors = [team_colors[t] for t in domain]

    # fallback if something unexpected appears
    for team in teams_present:
        if team not in domain:
            domain.append(team)
            range_colors.append("#C0C0C0")
import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

from engine.parser import load_all_race_results
from engine.team_metrics import apply_team_mapping
from engine.race_metrics import (
    prepare_laps_dataframe,
    build_estimated_position_by_lap,
    build_estimated_overtake_summary,
)
from utils.style import apply_srcs_style

st.set_page_config(page_title="Position Tracker", page_icon="📍", layout="wide")
apply_srcs_style()

st.markdown("""
<div class="srcs-hero">
    <div class="srcs-hero-title">POSITION TRACKER</div>
    <div class="srcs-hero-subtitle">Estimated lap-end running order, net movement, and race evolution</div>
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

round_options = [summary["Round"] for summary in round_summaries]
selected_round = st.selectbox("Select Round", round_options, index=len(round_options) - 1)

selected_index = round_options.index(selected_round)
selected_results_df = all_results[selected_index].copy()
selected_summary = round_summaries[selected_index]
selected_race_data = raw_race_data[selected_index]

if TEAM_MAP_FILE.exists():
    selected_results_df = apply_team_mapping(selected_results_df, TEAM_MAP_FILE)
else:
    selected_results_df["Team"] = "Unknown"

selected_results_df = selected_results_df.sort_values("Position").reset_index(drop=True)
selected_results_df["Positions Gained"] = (
    selected_results_df["GridPosition"] - selected_results_df["Position"]
)
selected_results_df["Movement"] = selected_results_df["Positions Gained"].apply(
    lambda x: "Gained" if x > 0 else ("Lost" if x < 0 else "No Change")
)

biggest_mover_row = selected_results_df.sort_values(
    ["Positions Gained", "Position"], ascending=[False, True]
).iloc[0]

biggest_loser_row = selected_results_df.sort_values(
    ["Positions Gained", "Position"], ascending=[True, True]
).iloc[0]

winner_row = selected_results_df.sort_values("Position").iloc[0]
pole_row = selected_results_df.sort_values("GridPosition").iloc[0]

laps_df = prepare_laps_dataframe(selected_race_data)
position_df = build_estimated_position_by_lap(laps_df)
changes_df = build_estimated_overtake_summary(position_df)

st.markdown('<div class="srcs-section">Round Movement Summary</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Winner", winner_row["DriverName"])
with c2:
    st.metric("Pole", pole_row["DriverName"])
with c3:
    st.metric("Biggest Mover", biggest_mover_row["DriverName"])
with c4:
    st.metric("Biggest Loser", biggest_loser_row["DriverName"])

st.caption(
    f"{selected_summary['Round']} • {selected_summary['Grand Prix']} • "
    f"{selected_summary['Track']} • {selected_summary['Session Type']}"
)

st.markdown('<div class="srcs-section">Grid vs Finish Tracker</div>', unsafe_allow_html=True)

tracker_df = selected_results_df[[
    "DriverName",
    "Team",
    "GridPosition",
    "Position",
    "Positions Gained",
    "Movement",
    "Points"
]].copy()

tracker_df.columns = [
    "Driver",
    "Team",
    "Grid",
    "Finish",
    "Net Gain/Loss",
    "Movement",
    "Points"
]

st.dataframe(tracker_df, use_container_width=True, hide_index=True)

st.markdown('<div class="srcs-section">Net Position Change Chart</div>', unsafe_allow_html=True)

position_chart_df = selected_results_df[[
    "DriverName",
    "Positions Gained"
]].copy()

position_chart_df.columns = ["Driver", "Net Gain/Loss"]
position_chart_df = position_chart_df.sort_values("Net Gain/Loss", ascending=True).set_index("Driver")
st.bar_chart(position_chart_df)

st.markdown('<div class="srcs-section">Estimated Position by Lap</div>', unsafe_allow_html=True)

if not position_df.empty:
    pos_chart_df = position_df.pivot_table(
        index="LapNumber",
        columns="DriverName",
        values="EstimatedPosition",
        aggfunc="first"
    ).sort_index()

    driver_team_df = selected_results_df[["DriverName", "Team"]].drop_duplicates()
    drivers = sorted(driver_team_df["DriverName"].dropna().unique().tolist())
    teams = sorted(driver_team_df["Team"].dropna().unique().tolist())

    f1, f2 = st.columns(2)

    with f1:
        selected_driver_filter = st.selectbox(
            "Focus on Driver",
            ["All Drivers"] + drivers,
            key="position_tracker_driver_filter"
        )

    with f2:
        selected_team_filter = st.selectbox(
            "Focus on Team",
            ["All Teams"] + teams,
            key="position_tracker_team_filter"
        )

    filtered_chart_df = pos_chart_df.copy()

    if selected_driver_filter != "All Drivers":
        if selected_driver_filter in filtered_chart_df.columns:
            filtered_chart_df = filtered_chart_df[[selected_driver_filter]]
    elif selected_team_filter != "All Teams":
        team_drivers = driver_team_df[
            driver_team_df["Team"] == selected_team_filter
        ]["DriverName"].tolist()

        team_drivers = [d for d in team_drivers if d in filtered_chart_df.columns]

        if team_drivers:
            filtered_chart_df = filtered_chart_df[team_drivers]

    # Build long dataframe for Altair
    chart_df = filtered_chart_df.reset_index().melt(
        "LapNumber",
        var_name="Driver",
        value_name="Position"
    )

    chart_df = chart_df.merge(
        driver_team_df,
        left_on="Driver",
        right_on="DriverName",
        how="left"
    )

    chart_df = chart_df.drop(columns=["DriverName"], errors="ignore")
    chart_df = chart_df.dropna(subset=["Position"]).copy()

    # SRCS team accent registry
    team_colors = {
        "McLaren": "#FF8700",
        "Ferrari": "#C00000",
        "Mercedes": "#00A19B",
        "Red Bull": "#0B1E3C",
        "Williams": "#005AFF",
        "Aston Martin": "#006F62",
        "Alpine": "#0090FF",
        "Haas": "#8B0000",
        "Audi": "#BB0A30",
        "Racing Bulls": "#1A1F3B",
        "Unknown": "#C0C0C0",
    }

    # End-of-line labels
    last_points_df = chart_df.sort_values(["Driver", "LapNumber"]).groupby("Driver", as_index=False).tail(1).copy()

    # Dynamic color domain/range based on filtered teams actually present
    teams_present = chart_df["Team"].fillna("Unknown").unique().tolist()
    domain = [t for t in team_colors.keys() if t in teams_present]
    range_colors = [team_colors[t] for t in domain]

    # fallback if something unexpected appears
    for team in teams_present:
        if team not in domain:
            domain.append(team)
            range_colors.append("#C0C0C0")

    color_scale = alt.Scale(domain=domain, range=range_colors)

    line_chart = alt.Chart(chart_df).mark_line(point=True).encode(
        x=alt.X("LapNumber:Q", title="Lap"),
        y=alt.Y(
            "Position:Q",
            title="Position",
            scale=alt.Scale(reverse=True, zero=False)
        ),
        color=alt.Color(
            "Team:N",
            scale=color_scale,
            legend=alt.Legend(title="Team")
        ),
        detail="Driver:N",
        tooltip=[
            alt.Tooltip("Driver:N"),
            alt.Tooltip("Team:N"),
            alt.Tooltip("LapNumber:Q", title="Lap"),
            alt.Tooltip("Position:Q", title="Estimated Position")
        ]
    )

    label_chart = alt.Chart(last_points_df).mark_text(
        align="left",
        baseline="middle",
        dx=8,
        fontSize=12,
        fontWeight="bold"
    ).encode(
        x=alt.X("LapNumber:Q"),
        y=alt.Y("Position:Q", scale=alt.Scale(reverse=True, zero=False)),
        text="Driver:N",
        color=alt.Color("Team:N", scale=color_scale, legend=None),
        tooltip=[
            alt.Tooltip("Driver:N"),
            alt.Tooltip("Team:N"),
            alt.Tooltip("LapNumber:Q", title="Lap"),
            alt.Tooltip("Position:Q", title="Estimated Position")
        ]
    )

    chart = (line_chart + label_chart).properties(height=520)

    st.altair_chart(chart, use_container_width=True)

    st.caption(
        "Estimated lap-end position based on cumulative lap time after each completed lap. "
        "This is a reconstruction, not official running-order timing."
    )
else:
    st.info("Not enough lap data available to build an estimated position-by-lap chart.")

st.markdown('<div class="srcs-section">Race Evolution Heatmap Table</div>', unsafe_allow_html=True)

if not position_df.empty:
    heatmap_df = position_df.pivot_table(
        index="DriverName",
        columns="LapNumber",
        values="EstimatedPosition",
        aggfunc="first"
    )

    heatmap_df = heatmap_df.sort_index()
    st.dataframe(heatmap_df, use_container_width=True)
else:
    st.info("No estimated lap-by-lap position table available.")

st.markdown('<div class="srcs-section">Estimated Position Change Summary</div>', unsafe_allow_html=True)

if not changes_df.empty:
    gain_summary_df = (
        changes_df.groupby("DriverName", as_index=False)["PositionDelta"]
        .sum()
        .sort_values(["PositionDelta", "DriverName"], ascending=[False, True])
        .reset_index(drop=True)
    )

    gain_summary_df["Position"] = gain_summary_df.index + 1
    gain_summary_df = gain_summary_df[["Position", "DriverName", "PositionDelta"]]
    gain_summary_df.columns = ["Pos", "Driver", "Net Estimated Change"]

    st.dataframe(gain_summary_df, use_container_width=True, hide_index=True)
else:
    st.info("No estimated lap-to-lap position changes available.")

st.markdown('<div class="srcs-section">Estimated Overtake Activity</div>', unsafe_allow_html=True)

if not changes_df.empty:
    overtakes_df = changes_df[changes_df["PositionDelta"] > 0].copy()
    overtakes_df["Estimated Moves"] = overtakes_df["PositionDelta"]

    if not overtakes_df.empty:
        overtakes_summary_df = (
            overtakes_df.groupby("DriverName", as_index=False)["Estimated Moves"]
            .sum()
            .sort_values(["Estimated Moves", "DriverName"], ascending=[False, True])
            .reset_index(drop=True)
        )

        overtakes_summary_df.columns = ["Driver", "Estimated Moves Gained"]
        st.dataframe(overtakes_summary_df, use_container_width=True, hide_index=True)

        overtakes_chart_df = overtakes_summary_df.set_index("Driver")
        st.bar_chart(overtakes_chart_df)
    else:
        st.info("No positive lap-end position changes detected.")
else:
    st.info("No estimated overtake activity available.")

st.markdown('<div class="srcs-section">Team Movement Summary</div>', unsafe_allow_html=True)

team_movement_df = (
    selected_results_df.groupby("Team", as_index=False)
    .agg(
        AvgGrid=("GridPosition", "mean"),
        AvgFinish=("Position", "mean"),
        TotalPoints=("Points", "sum"),
        TotalNetMovement=("Positions Gained", "sum")
    )
    .sort_values(["TotalNetMovement", "TotalPoints", "Team"], ascending=[False, False, True])
    .reset_index(drop=True)
)

team_movement_df["Position"] = team_movement_df.index + 1
team_movement_df["AvgGrid"] = team_movement_df["AvgGrid"].round(2)
team_movement_df["AvgFinish"] = team_movement_df["AvgFinish"].round(2)

team_movement_display_df = team_movement_df[[
    "Position", "Team", "AvgGrid", "AvgFinish", "TotalNetMovement", "TotalPoints"
]].copy()

team_movement_display_df.columns = [
    "Pos", "Team", "Avg Grid", "Avg Finish", "Net Team Movement", "Points"
]

st.dataframe(team_movement_display_df, use_container_width=True, hide_index=True)

st.markdown('<div class="srcs-section">Position Gain Bands</div>', unsafe_allow_html=True)

def movement_band(x):
    if x >= 4:
        return "Major Gain (4+)"
    if x >= 1:
        return "Minor Gain (1-3)"
    if x == 0:
        return "No Change"
    if x <= -4:
        return "Major Loss (4+)"
    return "Minor Loss (1-3)"

band_df = selected_results_df[["DriverName", "Positions Gained"]].copy()
band_df["Movement Band"] = band_df["Positions Gained"].apply(movement_band)

band_summary_df = (
    band_df.groupby("Movement Band", as_index=False)
    .size()
    .rename(columns={"size": "Count"})
    .sort_values(["Count", "Movement Band"], ascending=[False, True])
)

st.dataframe(band_summary_df, use_container_width=True, hide_index=True)

st.markdown('<div class="srcs-section">Tracker Notes</div>', unsafe_allow_html=True)

st.write(
    "This page now includes an estimated lap-end running order built from cumulative completed lap times. "
    "It is suitable for race-story analysis and movement trends, but it is not an official timing feed."
)
    color_scale = alt.Scale(domain=domain, range=range_colors)

    line_chart = alt.Chart(chart_df).mark_line(point=True).encode(
        x=alt.X("LapNumber:Q", title="Lap"),
        y=alt.Y(
            "Position:Q",
            title="Position",
            scale=alt.Scale(reverse=True, zero=False)
        ),
        color=alt.Color(
            "Team:N",
            scale=color_scale,
            legend=alt.Legend(title="Team")
        ),
        detail="Driver:N",
        tooltip=[
            alt.Tooltip("Driver:N"),
            alt.Tooltip("Team:N"),
            alt.Tooltip("LapNumber:Q", title="Lap"),
            alt.Tooltip("Position:Q", title="Estimated Position")
        ]
    )

    label_chart = alt.Chart(last_points_df).mark_text(
        align="left",
        baseline="middle",
        dx=8,
        fontSize=12,
        fontWeight="bold"
    ).encode(
        x=alt.X("LapNumber:Q"),
        y=alt.Y("Position:Q", scale=alt.Scale(reverse=True, zero=False)),
        text="Driver:N",
        color=alt.Color("Team:N", scale=color_scale, legend=None),
        tooltip=[
            alt.Tooltip("Driver:N"),
            alt.Tooltip("Team:N"),
            alt.Tooltip("LapNumber:Q", title="Lap"),
            alt.Tooltip("Position:Q", title="Estimated Position")
        ]
    )

    chart = (line_chart + label_chart).properties(height=520)

    st.altair_chart(chart, use_container_width=True)

    st.caption(
        "Estimated lap-end position based on cumulative lap time after each completed lap. "
        "This is a reconstruction, not official running-order timing."
    )
else:
    st.info("Not enough lap data available to build an estimated position-by-lap chart.")

st.markdown('<div class="srcs-section">Race Evolution Heatmap Table</div>', unsafe_allow_html=True)

if not position_df.empty:
    heatmap_df = position_df.pivot_table(
        index="DriverName",
        columns="LapNumber",
        values="EstimatedPosition",
        aggfunc="first"
    )

    heatmap_df = heatmap_df.sort_index()
    st.dataframe(heatmap_df, use_container_width=True)
else:
    st.info("No estimated lap-by-lap position table available.")

st.markdown('<div class="srcs-section">Estimated Position Change Summary</div>', unsafe_allow_html=True)

if not changes_df.empty:
    gain_summary_df = (
        changes_df.groupby("DriverName", as_index=False)["PositionDelta"]
        .sum()
        .sort_values(["PositionDelta", "DriverName"], ascending=[False, True])
        .reset_index(drop=True)
    )

    gain_summary_df["Position"] = gain_summary_df.index + 1
    gain_summary_df = gain_summary_df[["Position", "DriverName", "PositionDelta"]]
    gain_summary_df.columns = ["Pos", "Driver", "Net Estimated Change"]

    st.dataframe(gain_summary_df, use_container_width=True, hide_index=True)
else:
    st.info("No estimated lap-to-lap position changes available.")

st.markdown('<div class="srcs-section">Estimated Overtake Activity</div>', unsafe_allow_html=True)

if not changes_df.empty:
    overtakes_df = changes_df[changes_df["PositionDelta"] > 0].copy()
    overtakes_df["Estimated Moves"] = overtakes_df["PositionDelta"]

    if not overtakes_df.empty:
        overtakes_summary_df = (
            overtakes_df.groupby("DriverName", as_index=False)["Estimated Moves"]
            .sum()
            .sort_values(["Estimated Moves", "DriverName"], ascending=[False, True])
            .reset_index(drop=True)
        )

        overtakes_summary_df.columns = ["Driver", "Estimated Moves Gained"]
        st.dataframe(overtakes_summary_df, use_container_width=True, hide_index=True)

        overtakes_chart_df = overtakes_summary_df.set_index("Driver")
        st.bar_chart(overtakes_chart_df)
    else:
        st.info("No positive lap-end position changes detected.")
else:
    st.info("No estimated overtake activity available.")

st.markdown('<div class="srcs-section">Team Movement Summary</div>', unsafe_allow_html=True)

team_movement_df = (
    selected_results_df.groupby("Team", as_index=False)
    .agg(
        AvgGrid=("GridPosition", "mean"),
        AvgFinish=("Position", "mean"),
        TotalPoints=("Points", "sum"),
        TotalNetMovement=("Positions Gained", "sum")
    )
    .sort_values(["TotalNetMovement", "TotalPoints", "Team"], ascending=[False, False, True])
    .reset_index(drop=True)
)

team_movement_df["Position"] = team_movement_df.index + 1
team_movement_df["AvgGrid"] = team_movement_df["AvgGrid"].round(2)
team_movement_df["AvgFinish"] = team_movement_df["AvgFinish"].round(2)

team_movement_display_df = team_movement_df[[
    "Position", "Team", "AvgGrid", "AvgFinish", "TotalNetMovement", "TotalPoints"
]].copy()

team_movement_display_df.columns = [
    "Pos", "Team", "Avg Grid", "Avg Finish", "Net Team Movement", "Points"
]

st.dataframe(team_movement_display_df, use_container_width=True, hide_index=True)

st.markdown('<div class="srcs-section">Position Gain Bands</div>', unsafe_allow_html=True)

def movement_band(x):
    if x >= 4:
        return "Major Gain (4+)"
    if x >= 1:
        return "Minor Gain (1-3)"
    if x == 0:
        return "No Change"
    if x <= -4:
        return "Major Loss (4+)"
    return "Minor Loss (1-3)"

band_df = selected_results_df[["DriverName", "Positions Gained"]].copy()
band_df["Movement Band"] = band_df["Positions Gained"].apply(movement_band)

band_summary_df = (
    band_df.groupby("Movement Band", as_index=False)
    .size()
    .rename(columns={"size": "Count"})
    .sort_values(["Count", "Movement Band"], ascending=[False, True])
)

st.dataframe(band_summary_df, use_container_width=True, hide_index=True)

st.markdown('<div class="srcs-section">Tracker Notes</div>', unsafe_allow_html=True)

st.write(
    "This page now includes an estimated lap-end running order built from cumulative completed lap times. "
    "It is suitable for race-story analysis and movement trends, but it is not an official timing feed."
)
