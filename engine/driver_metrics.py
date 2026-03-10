import pandas as pd


def calculate_driver_standings(season_results_df):
    df = (
        season_results_df.groupby("DriverName", as_index=False)["Points"]
        .sum()
        .sort_values(["Points", "DriverName"], ascending=[False, True])
        .reset_index(drop=True)
    )
    df["Position"] = df.index + 1
    df = df[["Position", "DriverName", "Points"]]
    df.columns = ["Pos", "Driver", "Points"]
    return df


def calculate_driver_progression(season_results_df):
    return season_results_df.pivot_table(
        index="Round",
        columns="DriverName",
        values="Points",
        aggfunc="sum",
        fill_value=0
    ).cumsum()
