import streamlit as st
import pandas as pd
from pathlib import Path

from utils.data_loader import load_all_race_results
from utils.formatting import ms_to_laptime
from utils.style import apply_srcs_style

st.set_page_config(page_title="Race Archive", layout="wide")
apply_srcs_style()

st.title("📅 Race Archive")

DATA_DIR = Path("data")

if not DATA_DIR.exists():
    st.error("Data folder not found.")
    st.stop()

race_files, all_results, round_summaries, raw_race_data = load_all_race_results(DATA_DIR)

if not race_files or not all_results:
    st.warning("No race data available yet.")
    st.stop()

archive_rows = []

for results_df, round_summary in zip(all_results, round_summaries):
    if results_df.empty:
        continue

    winner_row = results_df.sort_values(["Position"]).iloc[0]
    pole_row = results_df.sort_values(["GridPosition"]).iloc[0]

    archive_rows.append({
        "Round": round_summary["Round"],
        "Grand Prix": round_summary["Grand Prix"],
        "Winner": winner_row["DriverName"],
        "Pole": pole_row["DriverName"],
        "Fastest Lap": round_summary["Fastest Lap Driver"],
        "Fastest Lap Time": round_summary["Fastest Lap Time"],
        "Classified Drivers": len(results_df)
    })

archive_df = pd.DataFrame(archive_rows)

st.subheader("Season Race Archive")
st.dataframe(archive_df, use_container_width=True, hide_index=True)
