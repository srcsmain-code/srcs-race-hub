import pandas as pd


def prepare_events_dataframe(race_data):
    events = race_data.get("Events", [])
    events_df = pd.DataFrame(events)

    if events_df.empty:
        return events_df

    # Driver / other driver names
    if "Driver" in events_df.columns:
        events_df["DriverName"] = events_df["Driver"].apply(
            lambda x: x.get("Name", "") if isinstance(x, dict) else ""
        )
    else:
        events_df["DriverName"] = ""

    if "OtherDriver" in events_df.columns:
        events_df["OtherDriverName"] = events_df["OtherDriver"].apply(
            lambda x: x.get("Name", "") if isinstance(x, dict) else ""
        )
    else:
        events_df["OtherDriverName"] = ""

    # Clean types
    if "ImpactSpeed" in events_df.columns:
        events_df["ImpactSpeed"] = pd.to_numeric(events_df["ImpactSpeed"], errors="coerce")
    else:
        events_df["ImpactSpeed"] = 0

    if "Timestamp" in events_df.columns:
        events_df["Timestamp"] = pd.to_numeric(events_df["Timestamp"], errors="coerce")
    else:
        events_df["Timestamp"] = None

    if "AfterSessionEnd" not in events_df.columns:
        events_df["AfterSessionEnd"] = False

    if "Type" not in events_df.columns:
        events_df["Type"] = "UNKNOWN"

    # Keep only meaningful rows with a driver and event type
    events_df = events_df[
        (events_df["DriverName"].notna()) &
        (events_df["DriverName"] != "") &
        (events_df["Type"].notna()) &
        (events_df["Type"] != "")
    ].copy()

    return events_df


def filter_incident_events(events_df):
    if events_df.empty:
        return events_df

    incident_types = [
        "COLLISION_WITH_CAR",
        "COLLISION_WITH_ENV",
    ]

    df = events_df[events_df["Type"].isin(incident_types)].copy()
    df = df.sort_values(["Timestamp", "ImpactSpeed"], ascending=[True, False]).reset_index(drop=True)
    return df


def calculate_impact_speed_ranking(events_df):
    if events_df.empty:
        return pd.DataFrame()

    df = events_df.sort_values("ImpactSpeed", ascending=False).reset_index(drop=True).copy()
    df["Position"] = df.index + 1
    return df


def calculate_incident_type_breakdown(events_df):
    if events_df.empty:
        return pd.DataFrame()

    df = (
        events_df.groupby("Type", as_index=False)
        .size()
        .rename(columns={"size": "Count"})
        .sort_values(["Count", "Type"], ascending=[False, True])
        .reset_index(drop=True)
    )
    return df


def calculate_driver_incident_counts(events_df):
    if events_df.empty:
        return pd.DataFrame()

    df = (
        events_df.groupby("DriverName", as_index=False)
        .size()
        .rename(columns={"size": "IncidentCount"})
        .sort_values(["IncidentCount", "DriverName"], ascending=[False, True])
        .reset_index(drop=True)
    )
    df["Position"] = df.index + 1
    return df
