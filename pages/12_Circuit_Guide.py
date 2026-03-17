import streamlit as st

from data.lap_benchmarks import get_track_options, get_track_benchmark
from utils.style import apply_srcs_style

apply_srcs_style()

st.title("🛣️ Circuit Guide")
st.caption("Real-world F1 reference data and SRCS target pace guidance for each round.")

track_options = get_track_options()
selected_track_label = st.selectbox("Select a circuit", list(track_options.keys()))
track_key = track_options[selected_track_label]

benchmark = get_track_benchmark(track_key)

if not benchmark:
    st.warning("No benchmark data found for this circuit.")
    st.stop()

st.subheader(benchmark["round_name"])
st.write(f"**Track:** {benchmark['track_name']}")
st.write(f"**Race date:** {benchmark['race_date']}")

st.markdown("---")

# SECTION 1
st.markdown("## Section 1 — Real-Life Reference (F1)")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Official Race Lap Record",
        benchmark["official_race_lap_record"]
    )
    st.write(
        f"👉 {benchmark['official_race_lap_record']} — "
        f"{benchmark['lap_record_driver']} ({benchmark['lap_record_year']})"
    )

with col2:
    st.metric(
        "Pole Position Benchmark",
        benchmark["pole_position_benchmark"]
    )
    st.write(f"👉 {benchmark['pole_position_benchmark']}")

st.markdown("---")

# SECTION 2
st.markdown("## Section 2 — SRCS Target Pace")

col3, col4 = st.columns(2)

with col3:
    st.metric("SRCS Target Lap", benchmark["srcs_target_lap_time"])
    st.write(f"🟣 **Race-winning pace:** {benchmark['srcs_race_winning_pace']}")
    st.write(f"🔵 **Podium pace:** {benchmark['srcs_podium_pace']}")

with col4:
    st.write("")
    st.write(f"🟢 **Points pace:** {benchmark['srcs_points_pace']}")
    st.write(f"🔴 **Back-markers:** {benchmark['srcs_backmarker_pace']}")

st.markdown("---")

st.info(
    "Use this page as a pre-race benchmark guide. "
    "The F1 reference gives context for the circuit, while the SRCS pace bands show "
    "the kind of lap time range drivers should be targeting for race competitiveness."
)
