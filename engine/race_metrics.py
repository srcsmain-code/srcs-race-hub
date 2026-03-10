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

    df = (
        laps_df.groupby("DriverName")
        .agg(
            StdDev=("LapTime", "std"),
            MeanLap=("LapTime", "mean"),
            LapCount=("LapTime", "count")
        )
        .reset_index()
    )

    df["StdDev"] = df["StdDev"].fillna(0)
    df = df.sort_values("StdDev", ascending=True).reset_index(drop=True)
    df["Position"] = df.index + 1
    return df
