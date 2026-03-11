# components/track_benchmark_cards.py

import streamlit as st
from data.lap_benchmarks import get_track_benchmark


def _lap_to_seconds(lap_time: str) -> float:
    mins, secs = lap_time.split(":")
    return int(mins) * 60 + float(secs)


def _seconds_to_lap(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = seconds - (mins * 60)
    return f"{mins}:{secs:06.3f}"


def render_track_benchmark_cards(track_key: str, title: str = "TRACK BENCHMARKS") -> None:
    benchmark = get_track_benchmark(track_key)

    if not benchmark:
        st.warning("No benchmark data found for this track.")
        return

    real_life = benchmark["real_life_lap_record"]
    srcs_target = benchmark["srcs_target_lap_time"]

    gap_seconds = _lap_to_seconds(srcs_target) - _lap_to_seconds(real_life)
    gap_label = f"+{gap_seconds:.3f}s vs F1 record"

    st.markdown(f"### {title}")
    st.caption(f'{benchmark["round_name"]} • {benchmark["track_name"]}')

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Real Life Lap Record",
            value=real_life,
            help=f'{benchmark["lap_record_driver"]} ({benchmark["lap_record_year"]})'
        )

    with col2:
        st.metric(
            label="SRCS Target Lap Time",
            value=srcs_target,
            delta=gap_label
        )

    with col3:
        st.metric(
            label="Lap Record Holder",
            value=benchmark["lap_record_driver"],
            help=str(benchmark["lap_record_year"])
        )

    st.info(
        f'**Benchmark note:** F1 race lap record = **{real_life}** '
        f'({benchmark["lap_record_driver"]}, {benchmark["lap_record_year"]}). '
        f'SRCS target lap = **{srcs_target}**.'
    )


def render_track_benchmark_compact(track_key: str) -> None:
    benchmark = get_track_benchmark(track_key)

    if not benchmark:
        return

    st.markdown(
        f"""
        <div style="
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(0,123,255,0.25);
            border-radius: 16px;
            padding: 16px 18px;
            margin: 8px 0 16px 0;
        ">
            <div style="font-size: 0.85rem; color: #C0C0C0; margin-bottom: 8px;">
                TRACK BENCHMARK
            </div>
            <div style="font-size: 1.35rem; font-weight: 700; color: #FFFFFF;">
                {benchmark["track_name"]}
            </div>
            <div style="margin-top: 10px; color: #FFFFFF;">
                <strong>Real Life Lap Record:</strong> {benchmark["real_life_lap_record"]}<br>
                <strong>SRCS Target Lap Time:</strong> {benchmark["srcs_target_lap_time"]}
            </div>
            <div style="margin-top: 8px; color: #C0C0C0; font-size: 0.9rem;">
                Record holder: {benchmark["lap_record_driver"]} ({benchmark["lap_record_year"]})
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
