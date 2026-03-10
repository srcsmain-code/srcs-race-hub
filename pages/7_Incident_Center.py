import streamlit as st
import pandas as pd
from pathlib import Path

from engine.parser import load_all_race_results

st.set_page_config(page_title="Incident Center", layout="wide")

st.title("🚨 Incident Center")

DATA_DIR = Path("data")
INCIDENTS_FILE = DATA_DIR / "incidents_log.csv"

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
selected_summary = round_summaries[selected_index]
selected_results_df = all_results[selected_index].copy()

st.subheader("Round Context")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Grand Prix", selected_summary["Grand Prix"])
with c2:
    st.metric("Track", selected_summary["Track"])
with c3:
    st.metric("Session Type", selected_summary["Session Type"])
with c4:
    st.metric("Classified Drivers", len(selected_results_df))

st.caption(
    f"{selected_summary['Round']} • "
    f"{selected_summary['Grand Prix']} • "
    f"{selected_summary['Track']}"
)

st.subheader("Incident Log")

if INCIDENTS_FILE.exists():
    incidents_df = pd.read_csv(INCIDENTS_FILE)

    required_columns = [
        "Round",
        "Lap",
        "Driver",
        "Team",
        "Incident Type",
        "Severity",
        "Decision",
        "Penalty",
        "Notes"
    ]

    missing_columns = [col for col in required_columns if col not in incidents_df.columns]

    if missing_columns:
        st.error(
            "The incidents_log.csv file is missing required columns: "
            + ", ".join(missing_columns)
        )
        st.stop()

    round_incidents_df = incidents_df[incidents_df["Round"] == selected_round].copy()

    if round_incidents_df.empty:
        st.info("No incidents recorded for this round yet.")
    else:
        round_incidents_df = round_incidents_df.sort_values(
            by=["Lap", "Driver"],
            ascending=[True, True]
        ).reset_index(drop=True)

        st.dataframe(round_incidents_df, use_container_width=True, hide_index=True)

        st.subheader("Penalty Summary")

        penalties_df = round_incidents_df[
            round_incidents_df["Penalty"].notna() &
            (round_incidents_df["Penalty"].astype(str).str.strip() != "")
        ].copy()

        if penalties_df.empty:
            st.info("No penalties recorded for this round.")
        else:
            penalty_summary_df = penalties_df[[
                "Lap", "Driver", "Team", "Decision", "Penalty"
            ]].copy()

            st.dataframe(penalty_summary_df, use_container_width=True, hide_index=True)

        st.subheader("Severity Breakdown")

        severity_df = (
            round_incidents_df.groupby("Severity", as_index=False)
            .size()
            .rename(columns={"size": "Count"})
            .sort_values(["Count", "Severity"], ascending=[False, True])
        )

        if not severity_df.empty:
            severity_chart_df = severity_df.set_index("Severity")
            st.bar_chart(severity_chart_df)

        st.subheader("Incident Type Breakdown")

        incident_type_df = (
            round_incidents_df.groupby("Incident Type", as_index=False)
            .size()
            .rename(columns={"size": "Count"})
            .sort_values(["Count", "Incident Type"], ascending=[False, True])
        )

        if not incident_type_df.empty:
            incident_type_chart_df = incident_type_df.set_index("Incident Type")
            st.bar_chart(incident_type_chart_df)

else:
    st.info(
        "No incidents_log.csv file found yet. Create data/incidents_log.csv to track "
        "steward notes, penalties, and incident outcomes."
    )

st.subheader("Suggested CSV Structure")

template_df = pd.DataFrame([
    {
        "Round": selected_round,
        "Lap": 1,
        "Driver": "Example Driver",
        "Team": "Example Team",
        "Incident Type": "Avoidable Contact",
        "Severity": "Medium",
        "Decision": "Warning",
        "Penalty": "",
        "Notes": "Light contact into Turn 1, no lasting damage."
    }
])

st.dataframe(template_df, use_container_width=True, hide_index=True)

st.subheader("Stewarding Notes")

st.write(
    "Use this page as the SRCS stewarding hub for incident tracking. "
    "If no CSV is present yet, this page acts as the framework for future penalties, "
    "warnings, and race review decisions."
)
