"""
SRCS Race Hub - Driver Classification Event Scoring

Step 2: Convert one Race Square race JSON into one event-level
classification row per valid driver.

This script does NOT calculate the final 100-point classification.
It calculates the automated race-data score out of 85:
- Pace: 35
- Consistency: 25
- Racecraft proxy: 25

The Ambition / Tier Fit score out of 15 is added later from driver_profiles.csv.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, Dict, Iterable, List, Optional


INVALID_DRIVER_NAMES = {
    "",
    "server - spectator",
    "backup",
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def linear_map(value: float, x1: float, x2: float, y1: float, y2: float) -> float:
    if x1 == x2:
        return y2
    t = clamp((value - x1) / (x2 - x1), 0.0, 1.0)
    return y1 + t * (y2 - y1)


def ms_to_lap_time(ms: Optional[int]) -> str:
    if not ms or ms <= 0:
        return ""
    minutes = ms // 60000
    seconds = (ms % 60000) / 1000
    return f"{minutes}:{seconds:06.3f}"


def race_id_from_filename(path: Path, data: Dict[str, Any]) -> str:
    # Prefer the filename because it is normally the stable Race Hub convention.
    stem = path.stem
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", stem).strip("_")
    return cleaned


def infer_round_from_race_id(race_id: str) -> str:
    match = re.search(r"round[_-]?(\d+)", race_id, re.IGNORECASE)
    return match.group(1) if match else ""


def is_valid_result_row(row: Dict[str, Any]) -> bool:
    name = str(row.get("DriverName", "")).strip()
    if name.lower() in INVALID_DRIVER_NAMES:
        return False
    if int(row.get("NumLaps") or 0) <= 0:
        return False
    if bool(row.get("Disqualified", False)):
        # Keep this false for now. Later we may want to include DSQ with a flag.
        return False
    return True


def valid_results(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = [r for r in data.get("Result", []) if is_valid_result_row(r)]
    # If the same driver somehow appears more than once, keep the entry with most laps.
    best_by_driver: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        name = row["DriverName"].strip()
        current = best_by_driver.get(name)
        if current is None or int(row.get("NumLaps") or 0) > int(current.get("NumLaps") or 0):
            best_by_driver[name] = row
    return list(best_by_driver.values())


def score_pace(best_lap_ms: int, field_best_ms: int) -> tuple[float, float]:
    if best_lap_ms <= 0 or field_best_ms <= 0:
        return 0.0, 999.0
    gap_pct = ((best_lap_ms - field_best_ms) / field_best_ms) * 100

    if gap_pct <= 1:
        score = linear_map(gap_pct, 0, 1, 35, 31)
    elif gap_pct <= 3:
        score = linear_map(gap_pct, 1, 3, 30, 26)
    elif gap_pct <= 6:
        score = linear_map(gap_pct, 3, 6, 25, 18)
    elif gap_pct <= 9:
        score = linear_map(gap_pct, 6, 9, 17, 10)
    elif gap_pct <= 13:
        score = linear_map(gap_pct, 9, 13, 9, 0)
    else:
        score = 0
    return round(clamp(score, 0, 35), 1), round(gap_pct, 3)


def representative_laps(laps: List[Dict[str, Any]]) -> tuple[List[int], int]:
    lap_times = [int(l.get("LapTime") or 0) for l in laps if int(l.get("LapTime") or 0) > 0]
    if len(lap_times) > 3:
        # Ignore lap 1 because starts and first-lap traffic distort consistency.
        lap_times = lap_times[1:]
    if len(lap_times) < 3:
        return lap_times, 0

    med = median(lap_times)
    # Remove obvious pit/crash/outlier laps, while keeping normal race variation.
    filtered = [x for x in lap_times if med * 0.92 <= x <= med * 1.12]
    ignored = len(lap_times) - len(filtered)
    if len(filtered) < 3:
        # If filtering leaves too little data, fall back to the unfiltered sample.
        return lap_times, 0
    return filtered, ignored


def score_consistency(laps: List[Dict[str, Any]], best_lap_ms: int) -> tuple[float, int, int, str, str, float]:
    rep_laps, ignored_laps = representative_laps(laps)
    if len(rep_laps) < 3 or best_lap_ms <= 0:
        return 0.0, len(rep_laps), ignored_laps, "", "", 0.0

    avg_ms = mean(rep_laps)
    std_ms = pstdev(rep_laps) if len(rep_laps) > 1 else 0
    cv = std_ms / avg_ms if avg_ms else 0
    avg_gap_pct = ((avg_ms - best_lap_ms) / best_lap_ms) * 100

    # Low coefficient of variation = stable lap times.
    if cv <= 0.005:
        cv_score = 25
    elif cv <= 0.015:
        cv_score = linear_map(cv, 0.005, 0.015, 25, 20)
    elif cv <= 0.030:
        cv_score = linear_map(cv, 0.015, 0.030, 20, 15)
    elif cv <= 0.060:
        cv_score = linear_map(cv, 0.030, 0.060, 15, 8)
    elif cv <= 0.100:
        cv_score = linear_map(cv, 0.060, 0.100, 8, 0)
    else:
        cv_score = 0

    # Small gap from best lap to average lap = driver can repeat pace.
    if avg_gap_pct <= 1.5:
        gap_score = 25
    elif avg_gap_pct <= 3:
        gap_score = linear_map(avg_gap_pct, 1.5, 3, 25, 20)
    elif avg_gap_pct <= 5:
        gap_score = linear_map(avg_gap_pct, 3, 5, 20, 15)
    elif avg_gap_pct <= 8:
        gap_score = linear_map(avg_gap_pct, 5, 8, 15, 8)
    elif avg_gap_pct <= 12:
        gap_score = linear_map(avg_gap_pct, 8, 12, 8, 0)
    else:
        gap_score = 0

    score = (cv_score * 0.70) + (gap_score * 0.30)
    return (
        round(clamp(score, 0, 25), 1),
        len(rep_laps),
        ignored_laps,
        ms_to_lap_time(round(avg_ms)),
        ms_to_lap_time(round(std_ms)),
        round(avg_gap_pct, 3),
    )


def cluster_driver_events(events: List[Dict[str, Any]], driver_name: str, window_seconds: int = 5) -> List[Dict[str, Any]]:
    driver_events = [
        e for e in events
        if str(e.get("Driver", {}).get("Name", "")).strip() == driver_name
        and not bool(e.get("AfterSessionEnd", False))
        and str(e.get("Type", "")).startswith("COLLISION")
    ]
    driver_events.sort(key=lambda e: int(e.get("Timestamp") or 0))

    clusters: List[Dict[str, Any]] = []
    for event in driver_events:
        ts = int(event.get("Timestamp") or 0)
        event_type = str(event.get("Type", ""))
        impact = float(event.get("ImpactSpeed") or 0.0)
        if not clusters or ts - int(clusters[-1]["last_ts"]) > window_seconds:
            clusters.append({
                "first_ts": ts,
                "last_ts": ts,
                "types": {event_type},
                "count": 1,
                "max_impact": impact,
            })
        else:
            clusters[-1]["last_ts"] = ts
            clusters[-1]["types"].add(event_type)
            clusters[-1]["count"] += 1
            clusters[-1]["max_impact"] = max(float(clusters[-1]["max_impact"]), impact)
    return clusters


def score_racecraft(events: List[Dict[str, Any]], driver_name: str, completed_laps: int, total_cuts: int = 0) -> tuple[float, int, int, int, int, float]:
    clusters = cluster_driver_events(events, driver_name)
    car_clusters = sum(1 for c in clusters if "COLLISION_WITH_CAR" in c["types"])
    env_clusters = sum(1 for c in clusters if "COLLISION_WITH_ENV" in c["types"])
    severe_clusters = sum(1 for c in clusters if float(c["max_impact"]) >= 50)
    very_severe_clusters = sum(1 for c in clusters if float(c["max_impact"]) >= 100)

    raw_penalty = (
        car_clusters * 1.20
        + env_clusters * 0.80
        + severe_clusters * 1.50
        + very_severe_clusters * 3.00
        + total_cuts * 0.25
    )
    # Normalize slightly by race distance so a 30-lap race is not treated like a 5-lap sample.
    # The 0.30 factor keeps this as a proxy/review signal rather than a harsh blame score.
    lap_factor = 20 / max(completed_laps, 1)
    adjusted_penalty = raw_penalty * lap_factor * 0.30
    score = 25 - adjusted_penalty
    return (
        round(clamp(score, 0, 25), 1),
        len(clusters),
        car_clusters,
        env_clusters,
        severe_clusters,
        round(adjusted_penalty, 2),
    )


def confidence_level(completed_laps: int, rep_lap_count: int, racecraft_score: float) -> str:
    if completed_laps >= 20 and rep_lap_count >= 10 and racecraft_score >= 10:
        return "High"
    if completed_laps >= 10 and rep_lap_count >= 5:
        return "Medium"
    if completed_laps > 0:
        return "Low"
    return "Assessment Needed"


def review_flags(racecraft_score: float, severe_clusters: int, rep_lap_count: int, completed_laps: int) -> str:
    flags = []
    if racecraft_score < 10:
        flags.append("Racecraft review")
    if severe_clusters >= 3:
        flags.append("Severe incident signal")
    if completed_laps < 10 or rep_lap_count < 5:
        flags.append("Low data")
    return "; ".join(flags)


def score_event(json_path: Path) -> List[Dict[str, Any]]:
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    race_id = race_id_from_filename(json_path, data)
    round_no = infer_round_from_race_id(race_id)
    track = str(data.get("TrackName") or "").strip()
    date = str(data.get("Date") or "").strip()
    results = valid_results(data)
    if not results:
        return []

    field_best = min(int(r.get("BestLap") or 0) for r in results if int(r.get("BestLap") or 0) > 0)

    laps_by_driver: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    cuts_by_driver: Dict[str, int] = defaultdict(int)
    for lap in data.get("Laps", []):
        name = str(lap.get("DriverName", "")).strip()
        if not name:
            continue
        laps_by_driver[name].append(lap)
        cuts_by_driver[name] += int(lap.get("Cuts") or 0)

    rows: List[Dict[str, Any]] = []
    for result in results:
        driver = result["DriverName"].strip()
        best_lap = int(result.get("BestLap") or 0)
        completed_laps = int(result.get("NumLaps") or 0)
        pace_score, pace_gap_pct = score_pace(best_lap, field_best)
        consistency_score, rep_laps, ignored_laps, avg_lap, std_lap, avg_gap_pct = score_consistency(
            laps_by_driver.get(driver, []), best_lap
        )
        racecraft_score, clusters, car_clusters, env_clusters, severe_clusters, incident_penalty = score_racecraft(
            data.get("Events", []), driver, completed_laps, cuts_by_driver.get(driver, 0)
        )
        data_score_85 = round(pace_score + consistency_score + racecraft_score, 1)
        rows.append({
            "RaceId": race_id,
            "Round": round_no,
            "Track": track,
            "Date": date,
            "Driver": driver,
            "CarId": result.get("CarId", ""),
            "CompletedLaps": completed_laps,
            "BestLapMs": best_lap,
            "BestLap": ms_to_lap_time(best_lap),
            "FieldBestLapMs": field_best,
            "GapToFieldBestPct": pace_gap_pct,
            "PaceScore": pace_score,
            "RepresentativeLapCount": rep_laps,
            "IgnoredOutlierLaps": ignored_laps,
            "RepresentativeAvgLap": avg_lap,
            "LapStdDev": std_lap,
            "AvgGapToBestPct": avg_gap_pct,
            "ConsistencyScore": consistency_score,
            "TotalCuts": cuts_by_driver.get(driver, 0),
            "IncidentClusters": clusters,
            "CarContactClusters": car_clusters,
            "EnvironmentHitClusters": env_clusters,
            "SevereImpactClusters": severe_clusters,
            "IncidentPenalty": incident_penalty,
            "RacecraftProxyScore": racecraft_score,
            "DataScore85": data_score_85,
            "Confidence": confidence_level(completed_laps, rep_laps, racecraft_score),
            "ReviewFlags": review_flags(racecraft_score, severe_clusters, rep_laps, completed_laps),
        })
    return rows


def write_csv(rows: List[Dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output_path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Score one SRCS race JSON into event-level classification rows.")
    parser.add_argument("json_file", type=Path, help="Path to the Race Square JSON file")
    parser.add_argument("--output", "-o", type=Path, default=Path("classification_events_output.csv"), help="Output CSV path")
    args = parser.parse_args()

    rows = score_event(args.json_file)
    write_csv(rows, args.output)
    print(f"Processed {args.json_file.name}: {len(rows)} driver rows written to {args.output}")


if __name__ == "__main__":
    main()
