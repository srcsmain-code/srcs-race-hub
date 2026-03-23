import pandas as pd

from engine.race_metrics import prepare_laps_dataframe, calculate_fastest_laps


def ms_to_laptime(ms):
    if ms is None:
        return "-"
    ms = int(ms)
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    millis = ms % 1000
    return f"{minutes}:{seconds:02d}.{millis:03d}"


def laptime_to_ms(laptime_str):
    if not laptime_str or ":" not in laptime_str:
        return None

    minutes_part, sec_part = laptime_str.split(":")
    seconds_part, millis_part = sec_part.split(".")

    return (
        int(minutes_part) * 60000
        + int(seconds_part) * 1000
        + int(millis_part)
    )


def format_delta_ms(delta_ms):
    if delta_ms is None:
        return "-"
    sign = "+" if delta_ms >= 0 else "-"
    delta_ms = abs(int(delta_ms))
    seconds = delta_ms // 1000
    millis = delta_ms % 1000
    return f"{sign}{seconds}.{millis:03d}s"


def get_actual_fastest_lap_from_race_data(race_data):
    if not race_data:
        return None

    laps_df = prepare_laps_dataframe(race_data)
    if laps_df.empty:
        return None

    fastest_df = calculate_fastest_laps(laps_df)
    if fastest_df.empty:
        return None

    top_row = fastest_df.iloc[0]

    return {
        "driver": top_row["DriverName"],
        "lap_time_ms": int(top_row["LapTime"]),
        "lap_time_str": ms_to_laptime(int(top_row["LapTime"]))
    }


def match_race_data_to_track(raw_race_data, track_key):
    """
    Tries to find the matching race JSON for the selected track.
    Adjust the keyword list if your race names differ.
    """
    if not raw_race_data:
        return None

    track_keywords = {
        "melbourne": ["melbourne", "australia", "australian"],
        "suzuka": ["suzuka", "japan", "japanese"],
        "miami": ["miami"],
        "monaco": ["monaco"],
        "silverstone": ["silverstone", "british"],
        "zandvoort": ["zandvoort", "dutch"],
        "monza": ["monza", "italian", "italy"],
        "singapore": ["singapore", "marina bay"],
        "interlagos": ["interlagos", "brazil", "brazilian", "sao paulo"],
        "abu_dhabi": ["abu dhabi", "yas marina"],
    }

    keywords = track_keywords.get(track_key, [track_key])

    for race_data in raw_race_data:
        text_to_search = " ".join(
            str(v) for v in race_data.values() if isinstance(v, (str, int, float))
        ).lower()

        if any(keyword in text_to_search for keyword in keywords):
            return race_data

    return None


def build_target_vs_actual_summary(track_key, benchmark, raw_race_data):
    race_data = match_race_data_to_track(raw_race_data, track_key)
    actual = get_actual_fastest_lap_from_race_data(race_data)

    target_ms = laptime_to_ms(benchmark.get("srcs_target_lap_time"))

    if not actual:
        return {
            "actual_available": False,
            "actual_driver": "-",
            "actual_fastest_lap": "-",
            "delta_to_target": "-",
        }

    delta_ms = None
    if target_ms is not None:
        delta_ms = actual["lap_time_ms"] - target_ms

    return {
        "actual_available": True,
        "actual_driver": actual["driver"],
        "actual_fastest_lap": actual["lap_time_str"],
        "delta_to_target": format_delta_ms(delta_ms),
    }
