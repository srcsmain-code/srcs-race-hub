import pandas as pd


def apply_team_mapping(season_results_df, team_map_file):
    team_map_df = pd.read_csv(team_map_file)

    season_results_df = season_results_df.merge(
        team_map_df,
        how="left",
        left_on=["Round", "DriverName"],
        right_on=["Round", "Driver"]
    )

    season_results_df["Team"] = season_results_df["Team"].fillna("Unknown")
    season_results_df = season_results_df.drop(columns=["Driver"], errors="ignore")
    return season_results_df


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


def calculate_team_standings(season_results_df):
    df = (
        season_results_df.groupby("Team", as_index=False)["Points"]
        .sum()
        .sort_values(["Points", "Team"], ascending=[False, True])
        .reset_index(drop=True)
    )
    df["Position"] = df.index + 1
    df = df[["Position", "Team", "Points"]]
    df.columns = ["Pos", "Team", "Points"]
    return df


def calculate_driver_progression(season_results_df):
    return season_results_df.pivot_table(
        index="Round",
        columns="DriverName",
        values="Points",
        aggfunc="sum",
        fill_value=0
    ).cumsum()


def calculate_team_progression(season_results_df):
    return season_results_df.pivot_table(
        index="Round",
        columns="Team",
        values="Points",
        aggfunc="sum",
        fill_value=0
    ).cumsum()
