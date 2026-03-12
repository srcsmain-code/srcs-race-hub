import pandas as pd


def prepare_laps_dataframe(race_data):
    laps_df = pd.DataFrame(race_data.get("Laps", []))

    if laps_df.empty:
        return laps_df

    laps_df = laps_df[
        (laps_df["DriverName"].notna()) &
        (laps_df["DriverName"] != "") &
        (laps_df["DriverName"] != "Server - Spectator") &
        (laps_df["LapTime"] < 999999999) &
        (laps_df["LapTime"] > 0)
    ].copy()

    if laps_df.empty:
        return laps_df

    if "Timestamp" in laps_df.columns:
        laps_df["Timestamp"] = pd.to_numeric(laps_df["Timestamp"], errors="coerce")
        laps_df = laps_df.dropna(subset=["Timestamp"])
        laps_df = laps_df.sort_values(["DriverName", "Timestamp"]).copy()
    else:
        laps_df = laps_df.reset_index(drop=True).copy()

    laps_df["LapNumber"] = laps_df.groupby("DriverName").cumcount() + 1
    laps_df["LapTime"] = pd.to_numeric(laps_df["LapTime"], errors="coerce")
    laps_df = laps_df.dropna(subset=["LapTime"])
    laps_df["LapTime"] = laps_df["LapTime"].astype(int)
    laps_df["LapNumber"] = laps_df["LapNumber"].astype(int)

    return laps_df


def calculate_fastest_laps(laps_df):
    if laps_df.empty:
        return pd.DataFrame()

    df = (
        laps_df.groupby("DriverName", as_index=False)["LapTime"]
        .min()
        .sort_values("LapTime", ascending=True)
        .reset_index(drop=True)
    )
    df["Position"] = df.index + 1
    return df


def calculate_average_pace(laps_df):
    if laps_df.empty:
        return pd.DataFrame()

    df = (
        laps_df.groupby("DriverName", as_index=False)["LapTime"]
        .mean()
        .sort_values("LapTime", ascending=True)
        .reset_index(drop=True)
    )
    df["Position"] = df.index + 1
    return df


def calculate_consistency(laps_df):
    if laps_df.empty:
        return pd.DataFrame()

    std_df = laps_df.groupby("DriverName")["LapTime"].std().reset_index(name="StdDev")
    mean_df = laps_df.groupby("DriverName")["LapTime"].mean().reset_index(name="MeanLap")
    count_df = laps_df.groupby("DriverName")["LapTime"].count().reset_index(name="LapCount")

    df = std_df.merge(mean_df, on="DriverName").merge(count_df, on="DriverName")
    df["StdDev"] = df["StdDev"].fillna(0)
    df = df.sort_values("StdDev", ascending=True).reset_index(drop=True)
    df["Position"] = df.index + 1

    return df


def build_estimated_position_by_lap(laps_df):
    """
    Build an estimated lap-end running order.

    Logic:
    - sort laps per driver by timestamp
    - assign LapNumber
    - compute cumulative elapsed race time after each completed lap
    - for each lap number, rank drivers by:
        1) laps completed (all rows in that slice have completed that lap)
        2) cumulative elapsed time after completing that lap
    This produces an estimated position at the end of each lap.
    """
    if laps_df.empty:
        return pd.DataFrame()

    work_df = laps_df.copy()

    work_df = work_df.sort_values(["DriverName", "LapNumber"]).reset_index(drop=True)
    work_df["CumulativeTimeMs"] = work_df.groupby("DriverName")["LapTime"].cumsum()

    ranked_frames = []

    for lap_num, lap_slice in work_df.groupby("LapNumber"):
        lap_slice = lap_slice.copy()
        lap_slice = lap_slice.sort_values(
            ["CumulativeTimeMs", "DriverName"],
            ascending=[True, True]
        ).reset_index(drop=True)

        lap_slice["EstimatedPosition"] = lap_slice.index + 1
        ranked_frames.append(lap_slice)

    if not ranked_frames:
        return pd.DataFrame()

    result_df = pd.concat(ranked_frames, ignore_index=True)
    return result_df


def build_estimated_overtake_summary(position_df):
    """
    Estimate position changes between completed laps.
    This is not a true on-track overtake log, but a lap-end position change summary.
    """
    if position_df.empty:
        return pd.DataFrame()

    work_df = position_df[["DriverName", "LapNumber", "EstimatedPosition"]].copy()
    work_df = work_df.sort_values(["DriverName", "LapNumber"]).reset_index(drop=True)

    work_df["PrevPosition"] = work_df.groupby("DriverName")["EstimatedPosition"].shift(1)
    work_df["PositionDelta"] = work_df["PrevPosition"] - work_df["EstimatedPosition"]

    changes_df = work_df.dropna(subset=["PrevPosition"]).copy()
    changes_df["PrevPosition"] = changes_df["PrevPosition"].astype(int)
    changes_df["PositionDelta"] = changes_df["PositionDelta"].astype(int)

    return changes_df
