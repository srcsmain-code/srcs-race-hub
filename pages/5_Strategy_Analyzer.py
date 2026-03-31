import math
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_all_race_results
from utils.style import apply_srcs_style


# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(page_title="Strategy Analyzer", layout="wide")
apply_srcs_style()

st.title("🧠 STRATEGY ANALYZER")
st.caption("Pit windows, stint phases, position swings, and race strategy outcomes")


# =========================================================
# HELPERS
# =========================================================

TEAM_ID_TO_NAME = {
    "483068": "Ferrari",
    "483069": "Red Bull",
    "483070": "Mercedes",
    "483071": "McLaren",
    "483072": "Aston Martin",
    "483073": "Racing Bulls",
    "483074": "Haas F1",
    "483075": "Williams",
    "483076": "Audi",
    "483077": "Alpine",
    "483078": "Ferrari",
    "483079": "Red Bull",
    "483080": "Mercedes",
    "483081": "McLaren",
    "483082": "Aston Martin",
    "483083": "Racing Bulls",
    "483084": "Haas F1",
    "483085": "Williams",
    "483086": "Audi",
    "483087": "Alpine",
}

def normalize_team_name(team_value):
    if team_value is None or team_value == "":
        return "Unknown"
    team_value = str(team_value).strip()
    return TEAM_ID_TO_NAME.get(team_value, team_value)

DATA_DIR = Path("data")


def ms_to_laptime(ms):
    if ms is None or pd.isna(ms):
        return "-"
    ms = int(ms)
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    millis = ms % 1000
    return f"{minutes}:{seconds:02d}.{millis:03d}"


def ms_to_seconds_str(ms):
    if ms is None or pd.isna(ms):
        return "-"
    return f"{ms / 1000:.1f}s"


def safe_int(value, default=None):
    try:
        if value is None or value == "":
            return default
        return int(value)
    except Exception:
        return default


def safe_float(value, default=None):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def normalize_driver_name(name):
    if name is None:
        return "Unknown"
    name = str(name).strip()
    return name if name else "Unknown"


def get_driver_name_from_car(car):
    driver = car.get("Driver", {}) if isinstance(car, dict) else {}
    return normalize_driver_name(driver.get("Name"))


def get_team_from_car(car):
    driver = car.get("Driver", {}) if isinstance(car, dict) else {}
    team = driver.get("Team")
    return normalize_team_name(team)


def build_car_lookup(selected_race_data):
    cars = selected_race_data.get("Cars", [])
    rows = []
    for car in cars:
        if not isinstance(car, dict):
            continue
        car_id = safe_int(car.get("CarId"))
        driver_name = get_driver_name_from_car(car)
        if driver_name in {"", "Unknown", "Server - Spectator"}:
            continue
        rows.append(
            {
                "CarId": car_id,
                "Driver": driver_name,
                "Team": get_team_from_car(car),
                "Skin": car.get("Skin", ""),
                "Model": car.get("Model", ""),
            }
        )
    if not rows:
        return pd.DataFrame(columns=["CarId", "Driver", "Team", "Skin", "Model"])
    return pd.DataFrame(rows).drop_duplicates(subset=["CarId"])


def find_laps_list(selected_race_data):
    """
    Tries a few common shapes used by race JSON exports.
    """
    if "Laps" in selected_race_data and isinstance(selected_race_data["Laps"], list):
        return selected_race_data["Laps"]

    if "Result" in selected_race_data and isinstance(selected_race_data["Result"], dict):
        result = selected_race_data["Result"]
        if "Laps" in result and isinstance(result["Laps"], list):
            return result["Laps"]

    if "Sessions" in selected_race_data and isinstance(selected_race_data["Sessions"], list):
        for sess in selected_race_data["Sessions"]:
            if not isinstance(sess, dict):
                continue
            if "Laps" in sess and isinstance(sess["Laps"], list):
                return sess["Laps"]

    return []


def extract_lap_rows(selected_race_data):
    """
    Converts the raw lap objects into a driver-lap table.
    Supports SRCS / Race Square race JSON where Laps is a top-level list and
    lap rows contain fields like DriverName, DriverGuid, CarId, LapTime, Timestamp, Tyre, Sectors.
    """
    laps = find_laps_list(selected_race_data)
    car_lookup = build_car_lookup(selected_race_data)
    car_map = {
        row["CarId"]: {"Driver": row["Driver"], "Team": row["Team"]}
        for _, row in car_lookup.iterrows()
    }

    rows = []

    # Per-driver lap counter because the JSON lap rows do not contain LapNumber
    lap_counter = {}

    for lap in laps:
        if not isinstance(lap, dict):
            continue

        car_id = safe_int(lap.get("CarId"))

        # Driver name is directly on the lap row in this export
        driver_name = normalize_driver_name(
            lap.get("DriverName")
            if "DriverName" in lap
            else lap.get("Driver", {}).get("Name") if isinstance(lap.get("Driver"), dict) else None
        )

        if not driver_name or driver_name in {"Unknown", "Server - Spectator"}:
            continue

        # Team is usually not on lap rows, so infer from Cars via CarId
        team = "Unknown"
        if car_id in car_map:
           team = normalize_team_name(car_map[car_id]["Team"])

        lap_time_ms = safe_int(
            lap.get("LapTime")
            if "LapTime" in lap
            else lap.get("LapTimeMs")
            if "LapTimeMs" in lap
            else None
        )

        timestamp = safe_int(
            lap.get("Timestamp")
            if "Timestamp" in lap
            else lap.get("TimeStamp")
            if "TimeStamp" in lap
            else None
        )

        tyre = lap.get("Tyre") if "Tyre" in lap else "Unknown"
        sectors = lap.get("Sectors", [])
        cuts = safe_int(lap.get("Cuts"), 0)

        if lap_time_ms is not None and lap_time_ms <= 0:
            lap_time_ms = None

        s1 = s2 = s3 = None
        if isinstance(sectors, list) and len(sectors) >= 3:
            s1 = safe_int(sectors[0])
            s2 = safe_int(sectors[1])
            s3 = safe_int(sectors[2])

        # Since no lap number exists, derive it by counting laps per driver in timestamp order
        lap_counter[driver_name] = lap_counter.get(driver_name, 0) + 1
        lap_no = lap_counter[driver_name]

        rows.append(
            {
                "CarId": car_id,
                "Driver": driver_name,
                "Team": str(team),
                "Lap": lap_no,
                "LapTimeMs": lap_time_ms,
                "Timestamp": timestamp,
                "Position": None,   # not present in this JSON lap row
                "Tyre": tyre if tyre not in ["", None] else "Unknown",
                "Cuts": cuts,
                "S1": s1,
                "S2": s2,
                "S3": s3,
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=[
                "CarId",
                "Driver",
                "Team",
                "Lap",
                "LapTimeMs",
                "Timestamp",
                "Position",
                "Tyre",
                "Cuts",
                "S1",
                "S2",
                "S3",
            ]
        )

    df = pd.DataFrame(rows)

    # Sort correctly before deduping / later logic
    df = df.sort_values(["Driver", "Lap", "Timestamp"], na_position="last").reset_index(drop=True)

    # Keep one row per driver/lap if duplicates ever occur
    df = (
        df.sort_values(["Driver", "Lap", "LapTimeMs"], na_position="last")
        .drop_duplicates(subset=["Driver", "Lap"], keep="first")
        .reset_index(drop=True)
    )

    return df 


def derive_position_trace(driver_laps_df):
    """
    Uses explicit position if present.
    If not present, builds a simple lap-rank from cumulative time.
    """
    df = driver_laps_df.copy()

    if df.empty:
        return df

    if df["Position"].notna().any():
        df["DerivedPosition"] = df["Position"]
        return df

    # Fallback: cumulative time ranking by lap
    valid = df.copy()
    valid["LapTimeMsFilled"] = valid["LapTimeMs"].fillna(valid["LapTimeMs"].median())
    valid["CumMs"] = valid.groupby("Driver")["LapTimeMsFilled"].cumsum()

    positions = []
    for lap_no, grp in valid.groupby("Lap"):
        grp = grp.sort_values("CumMs").copy()
        grp["DerivedPosition"] = range(1, len(grp) + 1)
        positions.append(grp[["Driver", "Lap", "DerivedPosition"]])

    pos_df = pd.concat(positions, ignore_index=True)
    df = df.merge(pos_df, on=["Driver", "Lap"], how="left")
    return df


def mark_clean_laps(df):
    """
    Flags obvious outliers and creates rolling pace.
    """
    out = df.copy()
    out["RollingMedianMs"] = (
        out.groupby("Driver")["LapTimeMs"]
        .transform(lambda s: s.rolling(window=3, min_periods=1).median())
    )

    baseline_by_driver = (
        out.groupby("Driver")["LapTimeMs"]
        .median()
        .rename("DriverMedianMs")
        .reset_index()
    )
    out = out.merge(baseline_by_driver, on="Driver", how="left")

    out["IsOutlier"] = False
    out.loc[
        (out["Lap"] == 1)
        | (out["LapTimeMs"].isna())
        | (out["LapTimeMs"] > out["DriverMedianMs"] * 1.35),
        "IsOutlier",
    ] = True

    out["RollingAvgMs"] = (
        out.groupby("Driver")["LapTimeMs"]
        .transform(lambda s: s.rolling(window=3, min_periods=1).mean())
    )

    return out


def detect_driver_pit(driver_df):
    """
    Returns one dict for strategy summary + one dataframe of all pit candidates.
    """
    driver_df = driver_df.sort_values("Lap").copy()
    driver = driver_df["Driver"].iloc[0]
    team = driver_df["Team"].iloc[0] if "Team" in driver_df.columns else "Unknown"

    clean_baseline_candidates = driver_df[
        (driver_df["Lap"] > 1)
        & driver_df["LapTimeMs"].notna()
        & (~driver_df["IsOutlier"])
    ]["LapTimeMs"]

    if clean_baseline_candidates.empty:
        clean_baseline_candidates = driver_df["LapTimeMs"].dropna()

    baseline_ms = clean_baseline_candidates.median() if not clean_baseline_candidates.empty else None

    if pd.isna(baseline_ms):
        baseline_ms = None

    candidate_rows = []

    driver_df["PrevTyre"] = driver_df["Tyre"].shift(1)
    driver_df["NextTyre"] = driver_df["Tyre"].shift(-1)

    driver_df["PrevTimestamp"] = driver_df["Timestamp"].shift(1)
    driver_df["TsGap"] = driver_df["Timestamp"] - driver_df["PrevTimestamp"]

    for _, row in driver_df.iterrows():
        lap = row["Lap"]
        lap_time = row["LapTimeMs"]
        tyre_before = row["PrevTyre"]
        tyre_after = row["Tyre"]
        ts_gap = row["TsGap"]

        if lap_time is None or pd.isna(lap_time) or baseline_ms is None:
            continue

        delta_ms = lap_time - baseline_ms
        tyre_changed = (
            pd.notna(tyre_before)
            and pd.notna(tyre_after)
            and str(tyre_before) != "Unknown"
            and str(tyre_after) != "Unknown"
            and str(tyre_before) != str(tyre_after)
        )

        big_lap_spike = (delta_ms > 18000) or (lap_time > baseline_ms * 1.18)
        big_ts_gap = pd.notna(ts_gap) and ts_gap > 95

        if tyre_changed or big_lap_spike or big_ts_gap:
            confidence = "Low"
            score = 1
            if big_lap_spike:
                score += 2
            if tyre_changed:
                score += 3
            if big_ts_gap:
                score += 1

            if score >= 5:
                confidence = "High"
            elif score >= 3:
                confidence = "Medium"

            candidate_rows.append(
                {
                    "Driver": driver,
                    "Team": team,
                    "Lap": lap,
                    "LapTimeMs": lap_time,
                    "BaselineLapMs": baseline_ms,
                    "DeltaMs": delta_ms,
                    "TyreBefore": tyre_before if pd.notna(tyre_before) else "Unknown",
                    "TyreAfter": tyre_after if pd.notna(tyre_after) else "Unknown",
                    "TsGap": ts_gap if pd.notna(ts_gap) else None,
                    "BigLapSpike": big_lap_spike,
                    "TyreChanged": tyre_changed,
                    "BigTsGap": big_ts_gap,
                    "Confidence": confidence,
                    "Score": score,
                }
            )

    candidates_df = pd.DataFrame(candidate_rows)

    pit_detected = False
    pit_lap = None
    pit_confidence = "None"
    pit_lap_time_ms = None
    pit_loss_ms = None
    tyre_before = "Unknown"
    tyre_after = "Unknown"

    if not candidates_df.empty:
        selected = (
            candidates_df.sort_values(["Score", "DeltaMs", "Lap"], ascending=[False, False, True])
            .iloc[0]
        )
        pit_detected = True
        pit_lap = int(selected["Lap"])
        pit_confidence = selected["Confidence"]
        pit_lap_time_ms = selected["LapTimeMs"]
        pit_loss_ms = selected["DeltaMs"]
        tyre_before = selected["TyreBefore"]
        tyre_after = selected["TyreAfter"]

        candidates_df["SelectedAsPitLap"] = candidates_df["Lap"] == pit_lap
    else:
        candidates_df["SelectedAsPitLap"] = False

    # Stint averages
    if pit_detected:
        stint1 = driver_df[
            (driver_df["Lap"] < pit_lap)
            & driver_df["LapTimeMs"].notna()
            & (~driver_df["IsOutlier"])
        ]["LapTimeMs"]
        stint2 = driver_df[
            (driver_df["Lap"] > pit_lap)
            & driver_df["LapTimeMs"].notna()
            & (~driver_df["IsOutlier"])
        ]["LapTimeMs"]
    else:
        stint1 = driver_df[
            driver_df["LapTimeMs"].notna() & (~driver_df["IsOutlier"])
        ]["LapTimeMs"]
        stint2 = pd.Series(dtype=float)

    stint1_avg = stint1.mean() if not stint1.empty else None
    stint2_avg = stint2.mean() if not stint2.empty else None

    # Positions around pit
    position_before_pit = None
    position_after_cycle = None
    net_strategy_gain = None

    if "DerivedPosition" in driver_df.columns and driver_df["DerivedPosition"].notna().any():
        if pit_detected:
            before_rows = driver_df[driver_df["Lap"] == max(1, pit_lap - 1)]
            after_rows = driver_df[driver_df["Lap"] == min(driver_df["Lap"].max(), pit_lap + 2)]

            if not before_rows.empty:
                position_before_pit = safe_int(before_rows["DerivedPosition"].iloc[0])
            if not after_rows.empty:
                position_after_cycle = safe_int(after_rows["DerivedPosition"].iloc[0])

        if position_before_pit is not None and position_after_cycle is not None:
            net_strategy_gain = position_before_pit - position_after_cycle

    finish_position = None
    if "DerivedPosition" in driver_df.columns and not driver_df.empty:
        last_pos_row = driver_df.sort_values("Lap").iloc[-1]
        finish_position = safe_int(last_pos_row.get("DerivedPosition"))

    strategy_type = "No Confirmed Stop"
    if pit_detected:
        strategy_type = "1-stop"
        if pit_confidence == "High":
            strategy_type = "1-stop | High confidence"
        elif pit_confidence == "Medium":
            strategy_type = "1-stop | Medium confidence"
        else:
            strategy_type = "1-stop | Low confidence"

    summary = {
        "Driver": driver,
        "Team": team,
        "FinishPosition": finish_position,
        "TotalLaps": int(driver_df["Lap"].max()) if not driver_df.empty else None,
        "PitDetected": pit_detected,
        "PitLap": pit_lap,
        "PitConfidence": pit_confidence,
        "PitLapTimeMs": pit_lap_time_ms,
        "BaselineLapMs": baseline_ms,
        "PitLossMs": pit_loss_ms,
        "Stint1AvgMs": stint1_avg,
        "Stint2AvgMs": stint2_avg,
        "TyreBefore": tyre_before,
        "TyreAfter": tyre_after,
        "StrategyType": strategy_type,
        "PositionBeforePit": position_before_pit,
        "PositionAfterCycle": position_after_cycle,
        "NetStrategyGain": net_strategy_gain,
    }

    return summary, candidates_df


def build_strategy_outputs(driver_laps_df):
    if driver_laps_df.empty:
        return (
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
        )

    driver_laps_df = mark_clean_laps(driver_laps_df)
    driver_laps_df = derive_position_trace(driver_laps_df)

    summaries = []
    candidates = []

    for driver_name, grp in driver_laps_df.groupby("Driver"):
        summary, cand_df = detect_driver_pit(grp)
        summaries.append(summary)
        if not cand_df.empty:
            candidates.append(cand_df)

    strategy_df = pd.DataFrame(summaries)
    pit_candidates_df = pd.concat(candidates, ignore_index=True) if candidates else pd.DataFrame()

    position_trace_df = driver_laps_df[
        ["Driver", "Team", "Lap", "DerivedPosition", "LapTimeMs", "RollingAvgMs", "Tyre"]
    ].copy()

    if not strategy_df.empty:
        position_trace_df = position_trace_df.merge(
            strategy_df[["Driver", "PitLap"]],
            on="Driver",
            how="left",
        )

    return strategy_df, pit_candidates_df, position_trace_df, driver_laps_df


def assign_relative_strategy_labels(strategy_df):
    if strategy_df.empty:
        return strategy_df

    out = strategy_df.copy()
    pit_laps = out.loc[out["PitDetected"] & out["PitLap"].notna(), "PitLap"]

    if pit_laps.empty:
        return out

    q1 = pit_laps.quantile(0.25)
    q3 = pit_laps.quantile(0.75)

    def classify(row):
        if not row["PitDetected"] or pd.isna(row["PitLap"]):
            return "No Confirmed Stop"
        lap = row["PitLap"]
        base = row["StrategyType"]
        if lap <= q1:
            return f"{base} | Early Stop"
        if lap >= q3:
            return f"{base} | Late Stop"
        return f"{base} | Standard Window"

    out["StrategyType"] = out.apply(classify, axis=1)
    return out


def make_pit_window_timeline(strategy_df, highlight_driver=None):
    if strategy_df.empty:
        return None

    chart_rows = []
    for _, row in strategy_df.sort_values(["PitLap", "Driver"], na_position="last").iterrows():
        driver = row["Driver"]
        total_laps = safe_int(row["TotalLaps"], 0) or 0
        pit_lap = safe_int(row["PitLap"])

        if pit_lap is None or pit_lap <= 1:
            chart_rows.append(
                {"Driver": driver, "Phase": "Race", "StartLap": 1, "EndLap": max(total_laps, 1)}
            )
        else:
            chart_rows.append(
                {"Driver": driver, "Phase": "Stint 1", "StartLap": 1, "EndLap": max(pit_lap - 1, 1)}
            )
            chart_rows.append(
                {"Driver": driver, "Phase": "Stint 2", "StartLap": pit_lap + 1, "EndLap": max(total_laps, pit_lap + 1)}
            )

    timeline_df = pd.DataFrame(chart_rows)
    if timeline_df.empty:
        return None

    fig = go.Figure()

    phases = ["Stint 1", "Stint 2", "Race"]
    phase_color = {
        "Stint 1": "#7F8EA3",
        "Stint 2": "#00A3FF",
        "Race": "#AEB6C2",
    }

    drivers = list(
        strategy_df.sort_values(["PitLap", "Driver"], na_position="last")["Driver"].tolist()
    )

    for driver in drivers:
        driver_rows = timeline_df[timeline_df["Driver"] == driver]
        for _, r in driver_rows.iterrows():
            color = phase_color.get(r["Phase"], "#7F8EA3")
            opacity = 1.0 if highlight_driver and driver == highlight_driver else 0.45 if highlight_driver else 0.85

            fig.add_trace(
                go.Bar(
                    x=[r["EndLap"] - r["StartLap"] + 1],
                    y=[driver],
                    base=[r["StartLap"]],
                    orientation="h",
                    marker=dict(color=color),
                    opacity=opacity,
                    name=r["Phase"],
                    hovertemplate=f"{driver}<br>{r['Phase']}<br>Laps {r['StartLap']} - {r['EndLap']}<extra></extra>",
                    showlegend=False,
                )
            )

    # Add pit markers
    for _, row in strategy_df.iterrows():
        if pd.notna(row["PitLap"]):
            driver = row["Driver"]
            opacity = 1.0 if highlight_driver and driver == highlight_driver else 0.8
            fig.add_trace(
                go.Scatter(
                    x=[row["PitLap"]],
                    y=[driver],
                    mode="markers",
                    marker=dict(size=10, color="#C0C0C0", symbol="diamond"),
                    opacity=opacity,
                    hovertemplate=f"{driver}<br>Pit lap: {int(row['PitLap'])}<extra></extra>",
                    showlegend=False,
                )
            )

    fig.update_layout(
        barmode="overlay",
        height=max(500, len(drivers) * 26 + 180),
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="Lap",
        yaxis_title="Driver",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
    )

    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(categoryorder="array", categoryarray=drivers[::-1])

    return fig


def make_position_trace_chart(position_trace_df, highlight_driver=None):
    if position_trace_df.empty:
        return None

    df = position_trace_df.copy()
    df = df[df["DerivedPosition"].notna()]
    if df.empty:
        return None

    fig = go.Figure()

    for driver, grp in df.groupby("Driver"):
        grp = grp.sort_values("Lap")
        width = 4 if driver == highlight_driver else 1.6
        opacity = 1.0 if (highlight_driver is None or driver == highlight_driver) else 0.28

        fig.add_trace(
            go.Scatter(
                x=grp["Lap"],
                y=grp["DerivedPosition"],
                mode="lines+markers",
                name=driver,
                line=dict(width=width),
                opacity=opacity,
                hovertemplate=f"{driver}<br>Lap %{ '{x}' }<br>Pos %{ '{y}' }<extra></extra>",
            )
        )

        pit_lap = grp["PitLap"].dropna().iloc[0] if "PitLap" in grp.columns and grp["PitLap"].notna().any() else None
        if pit_lap is not None:
            pit_point = grp[grp["Lap"] == pit_lap]
            if not pit_point.empty:
                fig.add_trace(
                    go.Scatter(
                        x=pit_point["Lap"],
                        y=pit_point["DerivedPosition"],
                        mode="markers",
                        marker=dict(size=10, symbol="diamond"),
                        opacity=opacity,
                        showlegend=False,
                        hovertemplate=f"{driver}<br>Pit lap %{ '{x}' }<br>Pos %{ '{y}' }<extra></extra>",
                    )
                )

    max_pos = int(df["DerivedPosition"].max())

    fig.update_layout(
        height=560,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="Lap",
        yaxis_title="Position",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        legend_title_text="Driver",
    )

    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(
        autorange="reversed",
        dtick=1,
        range=[max_pos + 0.5, 0.5],
        showgrid=True,
        gridcolor="rgba(255,255,255,0.08)",
    )

    return fig


def make_selected_driver_laptime_chart(driver_laps_df, selected_driver):
    if selected_driver in [None, "All Drivers"]:
        return None

    df = driver_laps_df[driver_laps_df["Driver"] == selected_driver].copy()
    if df.empty:
        return None

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Lap"],
            y=df["LapTimeMs"] / 1000,
            mode="lines+markers",
            name="Lap Time",
            hovertemplate="Lap %{x}<br>%{y:.3f}s<extra></extra>",
        )
    )

    if df["RollingAvgMs"].notna().any():
        fig.add_trace(
            go.Scatter(
                x=df["Lap"],
                y=df["RollingAvgMs"] / 1000,
                mode="lines",
                name="Rolling Avg",
                line=dict(dash="dash"),
                hovertemplate="Lap %{x}<br>Rolling %{y:.3f}s<extra></extra>",
            )
        )

    pit_lap = None
    pit_candidates = df["PitCandidate"] if "PitCandidate" in df.columns else None
    if "PitLap" in df.columns and df["PitLap"].notna().any():
        pit_lap = int(df["PitLap"].dropna().iloc[0])

    if pit_lap is not None:
        fig.add_vline(
            x=pit_lap,
            line_width=2,
            line_dash="dot",
            line_color="#C0C0C0",
        )

    fig.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="Lap",
        yaxis_title="Lap Time (s)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
    )

    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")

    return fig


def generate_insights(strategy_df):
    insights = []

    if strategy_df.empty:
        return insights

    pit_rows = strategy_df[strategy_df["PitDetected"] & strategy_df["PitLap"].notna()].copy()

    if not pit_rows.empty:
        earliest = pit_rows.sort_values("PitLap").iloc[0]
        latest = pit_rows.sort_values("PitLap", ascending=False).iloc[0]
        insights.append(f"**Earliest stop:** {earliest['Driver']} on lap {int(earliest['PitLap'])}.")
        insights.append(f"**Latest stop:** {latest['Driver']} on lap {int(latest['PitLap'])}.")

        best_loss = pit_rows.dropna(subset=["PitLossMs"]).sort_values("PitLossMs").head(1)
        if not best_loss.empty:
            row = best_loss.iloc[0]
            insights.append(
                f"**Smallest estimated pit loss:** {row['Driver']} with {ms_to_seconds_str(row['PitLossMs'])}."
            )

    gain_rows = strategy_df.dropna(subset=["NetStrategyGain"]).copy()
    if not gain_rows.empty:
        best_gain = gain_rows.sort_values("NetStrategyGain", ascending=False).iloc[0]
        worst_gain = gain_rows.sort_values("NetStrategyGain", ascending=True).iloc[0]
        insights.append(
            f"**Biggest strategy gain:** {best_gain['Driver']} gained {int(best_gain['NetStrategyGain'])} place(s) across the pit phase."
        )
        insights.append(
            f"**Biggest strategy loss:** {worst_gain['Driver']} lost {abs(int(worst_gain['NetStrategyGain']))} place(s) across the pit phase."
        )

    return insights[:5]


def format_strategy_table(df):
    out = df.copy()

    out["Pit Loss"] = out["PitLossMs"].apply(ms_to_seconds_str)
    out["Baseline"] = out["BaselineLapMs"].apply(ms_to_laptime)
    out["Stint 1 Avg"] = out["Stint1AvgMs"].apply(ms_to_laptime)
    out["Stint 2 Avg"] = out["Stint2AvgMs"].apply(ms_to_laptime)

    cols = [
        "FinishPosition",
        "Driver",
        "Team",
        "PitLap",
        "PitConfidence",
        "Pit Loss",
        "Baseline",
        "Stint 1 Avg",
        "Stint 2 Avg",
        "TyreBefore",
        "TyreAfter",
        "StrategyType",
        "PositionBeforePit",
        "PositionAfterCycle",
        "NetStrategyGain",
    ]

    existing_cols = [c for c in cols if c in out.columns]
    out = out[existing_cols].sort_values(
        by=["FinishPosition", "PitLap"],
        na_position="last",
    )
    return out


def format_candidates_table(df):
    if df.empty:
        return df

    out = df.copy()
    out["Lap Time"] = out["LapTimeMs"].apply(ms_to_laptime)
    out["Baseline"] = out["BaselineLapMs"].apply(ms_to_laptime)
    out["Delta"] = out["DeltaMs"].apply(ms_to_seconds_str)

    cols = [
        "Driver",
        "Lap",
        "Lap Time",
        "Baseline",
        "Delta",
        "TyreBefore",
        "TyreAfter",
        "Confidence",
        "SelectedAsPitLap",
    ]
    existing_cols = [c for c in cols if c in out.columns]
    return out[existing_cols].sort_values(["Driver", "Lap"])

def render_kpi_card(title, value, delta=None):
    value = "-" if value is None or value == "" else str(value)
    delta_html = ""
    if delta not in [None, ""]:
        delta_html = f"""
        <div style="
            display:inline-block;
            margin-top:10px;
            padding:4px 10px;
            border-radius:999px;
            background:rgba(50, 205, 50, 0.16);
            color:#66E08A;
            font-size:0.95rem;
            font-weight:600;
        ">
            {delta}
        </div>
        """

    st.markdown(
        f"""
        <div style="
            background:linear-gradient(180deg, rgba(10,26,102,0.55) 0%, rgba(5,10,25,0.88) 100%);
            border:1px solid rgba(255,255,255,0.10);
            border-radius:18px;
            padding:20px 18px 18px 18px;
            min-height:150px;
            box-shadow:0 6px 18px rgba(0,0,0,0.18);
        ">
            <div style="
                color:#FFFFFF;
                font-size:1.05rem;
                font-weight:700;
                line-height:1.2;
                margin-bottom:12px;
                white-space:nowrap;
                overflow:hidden;
                text-overflow:ellipsis;
            ">
                {title}
            </div>

            <div style="
                color:#FFFFFF;
                font-size:2.2rem;
                font-weight:800;
                line-height:1.05;
                letter-spacing:-0.02em;
                white-space:normal;
                overflow-wrap:anywhere;
                word-break:break-word;
            ">
                {value}
            </div>

            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# LOAD DATA
# =========================================================

if not DATA_DIR.exists():
    st.error("Data folder not found.")
    st.stop()

race_files, all_results, round_summaries, raw_race_data = load_all_race_results(DATA_DIR)

if not race_files or not raw_race_data:
    st.warning("No race data available yet.")
    st.stop()

round_options = [summary["Round"] for summary in round_summaries]
selected_round = st.selectbox("Select Round", round_options, index=len(round_options) - 1)

selected_index = round_options.index(selected_round)
selected_summary = round_summaries[selected_index]
selected_race_data = raw_race_data[selected_index]


# =========================================================
# BUILD DATAFRAMES
# =========================================================

driver_laps_df = extract_lap_rows(selected_race_data)

if driver_laps_df.empty:
    st.warning("No lap data available for this round. This page needs lap-by-lap data in the race JSON.")
    st.stop()

strategy_df, pit_candidates_df, position_trace_df, driver_laps_df = build_strategy_outputs(driver_laps_df)
strategy_df = assign_relative_strategy_labels(strategy_df)

if strategy_df.empty:
    st.warning("Strategy analysis could not be generated from this round.")
    st.stop()

driver_laps_df = driver_laps_df.merge(
    strategy_df[["Driver", "PitLap"]],
    on="Driver",
    how="left",
)


# =========================================================
# FILTERS
# =========================================================

driver_options = ["All Drivers"] + sorted(strategy_df["Driver"].dropna().unique().tolist())
team_options = ["All Teams"] + sorted(strategy_df["Team"].dropna().unique().tolist())

c1, c2, c3, c4 = st.columns(4)
with c1:
    selected_driver = st.selectbox("Driver", driver_options, index=0)
with c2:
    selected_team = st.selectbox("Team", team_options, index=0)
with c3:
    classified_only = st.checkbox("Show only classified finishers", value=False)
with c4:
    highlight_selected = st.checkbox("Highlight selected driver", value=True)

filtered_strategy_df = strategy_df.copy()
filtered_position_df = position_trace_df.copy()
filtered_driver_laps_df = driver_laps_df.copy()
filtered_candidates_df = pit_candidates_df.copy()

if selected_team != "All Teams":
    filtered_strategy_df = filtered_strategy_df[filtered_strategy_df["Team"] == selected_team]
    filtered_position_df = filtered_position_df[filtered_position_df["Team"] == selected_team]
    filtered_driver_laps_df = filtered_driver_laps_df[filtered_driver_laps_df["Team"] == selected_team]
    if not filtered_candidates_df.empty:
        filtered_candidates_df = filtered_candidates_df[filtered_candidates_df["Team"] == selected_team]

if selected_driver != "All Drivers":
    filtered_position_df = filtered_position_df[
        filtered_position_df["Driver"].eq(selected_driver) | True
    ]  # keep full field for chart; highlight will handle focus
    filtered_driver_laps_df = filtered_driver_laps_df[
        filtered_driver_laps_df["Driver"] == selected_driver
    ]
    if not filtered_candidates_df.empty:
        filtered_candidates_df = filtered_candidates_df[
            filtered_candidates_df["Driver"] == selected_driver
        ]

if classified_only:
    filtered_strategy_df = filtered_strategy_df[filtered_strategy_df["FinishPosition"].notna()]

highlight_driver = selected_driver if (highlight_selected and selected_driver != "All Drivers") else None


# =========================================================
# KPI CARDS
# =========================================================

st.subheader("Strategy Headlines")

pit_rows = filtered_strategy_df[
    filtered_strategy_df["PitDetected"] & filtered_strategy_df["PitLap"].notna()
].copy()

card1, card2, card3, card4, card5, card6 = st.columns(6)

with card1:
    if not pit_rows.empty:
        earliest = pit_rows.sort_values("PitLap").iloc[0]
        render_kpi_card("Earliest Stop", earliest["Driver"], f"Lap {int(earliest['PitLap'])}")
    else:
        render_kpi_card("Earliest Stop", "-", "-")

with card2:
    if not pit_rows.empty:
        latest = pit_rows.sort_values("PitLap", ascending=False).iloc[0]
        render_kpi_card("Latest Stop", latest["Driver"], f"Lap {int(latest['PitLap'])}")
    else:
        render_kpi_card("Latest Stop", "-", "-")

with card3:
    best_loss_rows = pit_rows.dropna(subset=["PitLossMs"]).sort_values("PitLossMs").head(1)
    if not best_loss_rows.empty:
        row = best_loss_rows.iloc[0]
        render_kpi_card("Lowest Pit Loss", row["Driver"], ms_to_seconds_str(row["PitLossMs"]))
    else:
        render_kpi_card("Lowest Pit Loss", "-", "-")

with card4:
    gain_rows = filtered_strategy_df.dropna(subset=["NetStrategyGain"]).sort_values(
        "NetStrategyGain", ascending=False
    )
    if not gain_rows.empty:
        row = gain_rows.iloc[0]
        render_kpi_card("Biggest Gain", row["Driver"], f"+{int(row['NetStrategyGain'])}")
    else:
        render_kpi_card("Biggest Gain", "-", "-")

with card5:
    loss_rows = filtered_strategy_df.dropna(subset=["NetStrategyGain"]).sort_values(
        "NetStrategyGain", ascending=True
    )
    if not loss_rows.empty:
        row = loss_rows.iloc[0]
        render_kpi_card("Biggest Loss", row["Driver"], str(int(row["NetStrategyGain"])))
    else:
        render_kpi_card("Biggest Loss", "-", "-")

with card6:
    if not pit_rows.empty:
        lap_counts = pit_rows["PitLap"].value_counts().sort_index()
        common_lap = int(lap_counts.idxmax())
        render_kpi_card("Common Stop Window", f"Lap {common_lap}", f"{int(lap_counts.max())} driver(s)")
    else:
        render_kpi_card("Common Stop Window", "-", "-")


# =========================================================
# PIT WINDOW TIMELINE
# =========================================================

st.subheader("Pit Window Timeline")
st.caption("Estimated pitstop lap and stint split for each driver")

timeline_fig = make_pit_window_timeline(filtered_strategy_df, highlight_driver=highlight_driver)
if timeline_fig is not None:
    st.plotly_chart(timeline_fig, use_container_width=True)
else:
    st.info("No pit timeline could be rendered for this round.")


# =========================================================
# POSITION TRACE
# =========================================================

st.subheader("Position Trace")
st.caption("Track how strategy and incidents changed the running order across the race")

position_fig = make_position_trace_chart(position_trace_df, highlight_driver=highlight_driver)
if position_fig is not None:
    st.plotly_chart(position_fig, use_container_width=True)
else:
    st.info("No position trace could be rendered for this round.")


# =========================================================
# SELECTED DRIVER PACE PROFILE
# =========================================================

st.subheader("Selected Driver Pace Profile")
st.caption("Lap-by-lap pace with the estimated pit phase highlighted")

if selected_driver == "All Drivers":
    st.info("Select a driver above to see a detailed pace and strategy view.")
else:
    driver_fig = make_selected_driver_laptime_chart(driver_laps_df, selected_driver)
    if driver_fig is not None:
        st.plotly_chart(driver_fig, use_container_width=True)
    else:
        st.info("Not enough lap data to render the selected driver chart.")


# =========================================================
# TABLES
# =========================================================

left, right = st.columns([1.25, 1])

with left:
    st.subheader("Strategy Summary")
    st.dataframe(
        format_strategy_table(filtered_strategy_df),
        use_container_width=True,
        hide_index=True,
    )

with right:
    st.subheader("Pit Detection Detail")
    if filtered_candidates_df.empty:
        st.info("No pit candidates were detected for the current filter.")
    else:
        st.dataframe(
            format_candidates_table(filtered_candidates_df),
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# DRIVER DEBRIEF
# =========================================================

st.subheader("Driver Debrief")

if selected_driver == "All Drivers":
    st.info("Select a driver above to generate a driver-specific strategy debrief.")
else:
    row_df = strategy_df[strategy_df["Driver"] == selected_driver]
    if row_df.empty:
        st.info("No strategy summary is available for the selected driver.")
    else:
        row = row_df.iloc[0]

        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.metric("Likely Pit Lap", "-" if pd.isna(row["PitLap"]) else int(row["PitLap"]))
        with d2:
            st.metric("Estimated Stop Loss", ms_to_seconds_str(row["PitLossMs"]))
        with d3:
            st.metric("Position Before Pit", "-" if pd.isna(row["PositionBeforePit"]) else int(row["PositionBeforePit"]))
        with d4:
            st.metric("Position After Cycle", "-" if pd.isna(row["PositionAfterCycle"]) else int(row["PositionAfterCycle"]))

        d5, d6, d7, d8 = st.columns(4)
        with d5:
            st.metric("Stint 1 Avg", ms_to_laptime(row["Stint1AvgMs"]))
        with d6:
            st.metric("Stint 2 Avg", ms_to_laptime(row["Stint2AvgMs"]))
        with d7:
            val = "-" if pd.isna(row["NetStrategyGain"]) else int(row["NetStrategyGain"])
            st.metric("Net Strategy Gain", val)
        with d8:
            st.metric("Finish Position", "-" if pd.isna(row["FinishPosition"]) else int(row["FinishPosition"]))

        summary_text = (
            f"**{row['Driver']}** stopped on "
            f"{'an estimated lap ' + str(int(row['PitLap'])) if pd.notna(row['PitLap']) else 'no confidently detected pit lap'}. "
            f"Their estimated stop loss was **{ms_to_seconds_str(row['PitLossMs'])}**. "
            f"Strategy classification: **{row['StrategyType']}**. "
            f"Pre-stop average: **{ms_to_laptime(row['Stint1AvgMs'])}**. "
            f"Post-stop average: **{ms_to_laptime(row['Stint2AvgMs'])}**. "
        )

        if pd.notna(row["NetStrategyGain"]):
            if int(row["NetStrategyGain"]) > 0:
                summary_text += f"They gained **{int(row['NetStrategyGain'])}** place(s) across the pit phase. "
            elif int(row["NetStrategyGain"]) < 0:
                summary_text += f"They lost **{abs(int(row['NetStrategyGain']))}** place(s) across the pit phase. "
            else:
                summary_text += "They broke even across the pit phase. "

        if pd.notna(row["FinishPosition"]):
            summary_text += f"Final classification: **P{int(row['FinishPosition'])}**."

        if row["PitConfidence"] == "Low":
            summary_text += " Pit detection confidence is low, so treat the stop window as approximate."

        st.markdown(summary_text)


# =========================================================
# INSIGHTS
# =========================================================

st.subheader("Race Strategy Insights")

insights = generate_insights(filtered_strategy_df)
if not insights:
    st.info("No automated strategy insights could be generated for this round.")
else:
    for insight in insights:
        st.markdown(f"- {insight}")
