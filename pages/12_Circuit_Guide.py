import streamlit as st
from pathlib import Path

from data.lap_benchmarks import get_track_options, get_track_benchmark
from data.driver_assistants import get_driver_assistant
from engine.circuit_metrics import build_target_vs_actual_summary
from engine.parser import load_all_race_results
from utils.style import apply_srcs_style

apply_srcs_style()

st.title("🛣️ Circuit Guide")
st.caption("Real-world F1 reference data, SRCS target pace guidance, and full driver assistant notes.")

track_options = get_track_options()
selected_track_label = st.selectbox("Select a circuit", list(track_options.keys()))
track_key = track_options[selected_track_label]
track_map_paths = {
    "melbourne": Path("assets/track_maps/melbourne.png"),
    "suzuka": Path("assets/track_maps/suzuka.png"),
    "miami": Path("assets/track_maps/miami.png"),
}

benchmark = get_track_benchmark(track_key)
assistant = get_driver_assistant(track_key)

if not benchmark:
    st.warning("No benchmark data found for this circuit.")
    st.stop()

DATA_DIR = Path("data")
raw_race_data = []

if DATA_DIR.exists():
    try:
        _, _, _, raw_race_data = load_all_race_results(DATA_DIR)
    except Exception:
        raw_race_data = []

actual_summary = build_target_vs_actual_summary(track_key, benchmark, raw_race_data)

st.subheader(benchmark["round_name"])
st.write(f"**Track:** {benchmark['track_name']}")
st.write(f"**Race date:** {benchmark['race_date']}")

st.markdown("---")

st.markdown("## Section 1 — Real-Life Reference (F1)")
col1, col2 = st.columns(2)

with col1:
    st.metric("Official Race Lap Record", benchmark["official_race_lap_record"])
    st.write(
        f"**{benchmark['official_race_lap_record']} — "
        f"{benchmark['lap_record_driver']} ({benchmark['lap_record_year']})**"
    )

with col2:
    st.metric("Pole Position Benchmark", benchmark["pole_position_benchmark"])

st.markdown("---")

st.markdown("## Section 2 — SRCS Target Pace")
col3, col4 = st.columns(2)

with col3:
    st.metric("SRCS Target Lap", benchmark["srcs_target_lap_time"])

with col4:
    st.markdown(
        f"""
<div style="padding-top: 0.5rem;">
    <div style="margin-bottom: 0.9rem; text-align: left;">
        <span style="color:#A855F7; font-size: 1.1rem;">●</span>
        <strong> Race-winning pace:</strong> {benchmark['srcs_race_winning_pace']}
    </div>
    <div style="margin-bottom: 0.9rem; text-align: left;">
        <span style="color:#3B82F6; font-size: 1.1rem;">●</span>
        <strong> Podium pace:</strong> {benchmark['srcs_podium_pace']}
    </div>
    <div style="margin-bottom: 0.9rem; text-align: left;">
        <span style="color:#22C55E; font-size: 1.1rem;">●</span>
        <strong> Points pace:</strong> {benchmark['srcs_points_pace']}
    </div>
    <div style="margin-bottom: 0.9rem; text-align: left;">
        <span style="color:#EF4444; font-size: 1.1rem;">●</span>
        <strong> Back-markers:</strong> {benchmark['srcs_backmarker_pace']}
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("---")

st.markdown("## Section 2B — Target vs Actual")
col5, col6, col7 = st.columns(3)

with col5:
    st.metric("Actual Fastest SRCS Lap", actual_summary["actual_fastest_lap"])

with col6:
    st.metric("Fastest Driver", actual_summary["actual_driver"])

with col7:
    st.metric("Delta vs Target", actual_summary["delta_to_target"])

if not actual_summary["actual_available"]:
    st.info("No SRCS race result found yet for this circuit. After the round is uploaded, this section will fill automatically.")

st.markdown("---")

st.markdown("## Circuit Map")

track_map = track_map_paths.get(track_key)

if track_map and track_map.exists():
    st.image(str(track_map), use_container_width=True)
else:
    st.info("Track map visual not yet added for this circuit.")

st.markdown("---")

st.markdown("## Section 3 — Driver Assistant")

if not assistant:
    st.info("Driver Assistant for this circuit has not been added yet.")
else:
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Overview", "Circuit", "Strategy", "Racecraft"]
    )

    with tab1:
        st.markdown("### Event Overview")
        st.markdown(assistant.get("event_overview", ""))
        st.markdown("### Championship Mindset")
        st.markdown(assistant.get("championship_mindset", ""))
        st.markdown("### Preparation Checklist")
        st.markdown(assistant.get("preparation_checklist", ""))

    with tab2:
        st.markdown("### Circuit Breakdown")
        st.markdown(assistant.get("circuit_breakdown", ""))

    with tab3:
        st.markdown("### Strategic Guidance")
        st.markdown(assistant.get("strategic_guidance", ""))
        st.markdown("### Common Mistakes")
        st.markdown(assistant.get("common_mistakes", ""))

    with tab4:
        st.markdown("### Lap 1 Survival Protocol")
        st.markdown(assistant.get("lap1_survival", ""))
        st.markdown("### Overtaking & Defensive Driving")
        st.markdown(assistant.get("overtaking_defending", ""))

st.markdown("---")

st.info(
    "Use this page as a pre-race benchmark guide. "
    "The F1 reference gives context for the circuit, the SRCS pace bands show likely competitiveness, "
    "and the target-vs-actual block updates automatically once SRCS race data exists."
)
