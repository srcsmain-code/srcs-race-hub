import json
import pandas as pd
from pathlib import Path
from utils.formatting import ms_to_laptime

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


def extract_gp_name(file_path):
    parts = file_path.stem.split("_")[2:]
    if parts and parts[-1].lower() == "race":
        parts = parts[:-1]
    return " ".join(parts).replace("-", " ").title()


def parse_round_label(filename):
    name = filename.stem
    parts = name.split("_")
    if len(parts) >= 3 and parts[1].startswith("round"):
        round_part = parts[1].replace("round", "Round ")
        gp_part = extract_gp_name(filename)
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
    grand_prix = extract_gp_name(file_path)

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


def load_all_race_results(data_dir):
    data_dir = Path(data_dir)
    race_files = sorted(data_dir.glob("*.json"))

    all_results = []
    round_summaries = []
    raw_race_data = []

    for race_file in race_files:
        results_df, round_summary, race_data = load_race_file(race_file)
        if results_df is not None:
            all_results.append(results_df)
            round_summaries.append(round_summary)
            raw_race_data.append(race_data)

    return race_files, all_results, round_summaries, raw_race_data
