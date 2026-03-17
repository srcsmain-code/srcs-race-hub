import streamlit as st

from data.lap_benchmarks import get_track_options, get_track_benchmark

st.title("🛣️ Circuit Guide")
st.caption("Track benchmarks, SRCS target lap times, and future race reference data.")

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

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Real-Life Lap Record", benchmark["real_life_lap_record"])

with col2:
    st.metric("Record Holder", benchmark["lap_record_driver"])

with col3:
    st.metric("SRCS Target Lap", benchmark["srcs_target_lap_time"])

st.markdown("---")

st.write(f"**Lap Record Year:** {benchmark['lap_record_year']}")
st.info(
    "The SRCS target lap is an estimated benchmark to help drivers understand the pace "
    "they should roughly aim for before the race weekend."
)
