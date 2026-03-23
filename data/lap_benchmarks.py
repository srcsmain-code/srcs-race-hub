# data/lap_benchmarks.py

TRACK_BENCHMARKS = {
    "melbourne": {
        "round_name": "Round 1 — Australian Grand Prix",
        "track_name": "Albert Park, Melbourne",
        "race_date": "2026-03-08",

        # Section 1 — Real-Life Reference (F1)
        "official_race_lap_record": "1:19.813",
        "lap_record_driver": "Charles Leclerc",
        "lap_record_year": 2024,
        "pole_position_benchmark": "~1:15.0 – 1:16.5",

        # Section 2 — SRCS Target Pace
        "srcs_target_lap_time": "1:24.500",
        "srcs_race_winning_pace": "1:24–1:25",
        "srcs_podium_pace": "1:25–1:27",
        "srcs_points_pace": "1:27–1:29",
        "srcs_backmarker_pace": "1:29.0+",
    },

    "Japan": {
        "round_name": "Round 2 — Japan Grand Prix",
        "track_name": "Japan Circuit, Suzuka",
        "race_date": "2026-04-12",

        # Section 1 — Real-Life Reference (F1)
        "official_race_lap_record": "1:30.983",
        "lap_record_driver": "Lewis Hamilton",
        "lap_record_year": 2019,
        "pole_position_benchmark": "~1:27.0 – 1:28.0",

        # Section 2 — SRCS Target Pace
        "srcs_target_lap_time": "1:35.500",
        "srcs_race_winning_pace": "1:35–1:36",
        "srcs_podium_pace": "1:36–1:38",
        "srcs_points_pace": "1:38–1:40",
        "srcs_backmarker_pace": "1:40.0+",
    },

    "miami": {
        "round_name": "Round 3 — Miami Grand Prix",
        "track_name": "Miami International Autodrome",
        "race_date": "2026-05-03",

        # Section 1 — Real-Life Reference (F1)
        "official_race_lap_record": "1:29.708",
        "lap_record_driver": "Max Verstappen",
        "lap_record_year": 2023,
        "pole_position_benchmark": "~1:26.0 – 1:27.5",

        # Section 2 — SRCS Target Pace
        "srcs_target_lap_time": "1:35.000",
        "srcs_race_winning_pace": "1:35–1:36",
        "srcs_podium_pace": "1:36–1:38",
        "srcs_points_pace": "1:38–1:40",
        "srcs_backmarker_pace": "1:40.0+",
    },

    "monaco": {
        "round_name": "Round 4 — Monaco Grand Prix",
        "track_name": "Circuit de Monaco, Monte Carlo",
        "race_date": "2026-06-07",

        # Section 1 — Real-Life Reference (F1)
        "official_race_lap_record": "1:12.909",
        "lap_record_driver": "Lewis Hamilton",
        "lap_record_year": 2021,
        "pole_position_benchmark": "~1:10.0 – 1:11.5",

        # Section 2 — SRCS Target Pace
        "srcs_target_lap_time": "1:19.500",
        "srcs_race_winning_pace": "1:19–1:20",
        "srcs_podium_pace": "1:20–1:22",
        "srcs_points_pace": "1:22–1:24",
        "srcs_backmarker_pace": "1:24.0+",
    },

    "silverstone": {
        "round_name": "Round 5 — British Grand Prix",
        "track_name": "Silverstone Circuit",
        "race_date": "2026-07-05",

        # Section 1 — Real-Life Reference (F1)
        "official_race_lap_record": "1:27.097",
        "lap_record_driver": "Max Verstappen",
        "lap_record_year": 2020,
        "pole_position_benchmark": "~1:25.0 – 1:26.5",

        # Section 2 — SRCS Target Pace
        "srcs_target_lap_time": "1:32.500",
        "srcs_race_winning_pace": "1:32–1:33",
        "srcs_podium_pace": "1:33–1:35",
        "srcs_points_pace": "1:35–1:37",
        "srcs_backmarker_pace": "1:37.0+",
    },

    "zandvoort": {
        "round_name": "Round 6 — Dutch Grand Prix",
        "track_name": "Circuit Zandvoort",
        "race_date": "2026-08-23",

        # Section 1 — Real-Life Reference (F1)
        "official_race_lap_record": "1:11.097",
        "lap_record_driver": "Lewis Hamilton",
        "lap_record_year": 2021,
        "pole_position_benchmark": "~1:09.5 – 1:11.0",

        # Section 2 — SRCS Target Pace
        "srcs_target_lap_time": "1:16.800",
        "srcs_race_winning_pace": "1:16–1:17",
        "srcs_podium_pace": "1:17–1:19",
        "srcs_points_pace": "1:19–1:21",
        "srcs_backmarker_pace": "1:21.0+",
    },

    "monza": {
        "round_name": "Round 7 — Italian Grand Prix",
        "track_name": "Autodromo Nazionale Monza",
        "race_date": "2026-09-06",

        # Section 1 — Real-Life Reference (F1)
        "official_race_lap_record": "1:21.046",
        "lap_record_driver": "Rubens Barrichello",
        "lap_record_year": 2004,
        "pole_position_benchmark": "~1:19.5 – 1:21.0",

        # Section 2 — SRCS Target Pace
        "srcs_target_lap_time": "1:26.500",
        "srcs_race_winning_pace": "1:26–1:27",
        "srcs_podium_pace": "1:27–1:29",
        "srcs_points_pace": "1:29–1:31",
        "srcs_backmarker_pace": "1:31.0+",
    },

    "singapore": {
        "round_name": "Round 8 — Singapore Grand Prix",
        "track_name": "Marina Bay Street Circuit",
        "race_date": "2026-10-11",

        # Section 1 — Real-Life Reference (F1)
        "official_race_lap_record": "1:34.486",
        "lap_record_driver": "Daniel Ricciardo",
        "lap_record_year": 2024,
        "pole_position_benchmark": "~1:29.5 – 1:31.0",

        # Section 2 — SRCS Target Pace
        "srcs_target_lap_time": "1:41.000",
        "srcs_race_winning_pace": "1:41–1:42",
        "srcs_podium_pace": "1:42–1:44",
        "srcs_points_pace": "1:44–1:46",
        "srcs_backmarker_pace": "1:46.0+",
    },

    "interlagos": {
        "round_name": "Round 9 — Brazilian Grand Prix",
        "track_name": "Interlagos, Sao Paulo",
        "race_date": "2026-11-08",

        # Section 1 — Real-Life Reference (F1)
        "official_race_lap_record": "1:10.540",
        "lap_record_driver": "Valtteri Bottas",
        "lap_record_year": 2018,
        "pole_position_benchmark": "~1:08.0 – 1:09.5",

        # Section 2 — SRCS Target Pace
        "srcs_target_lap_time": "1:16.000",
        "srcs_race_winning_pace": "1:16–1:17",
        "srcs_podium_pace": "1:17–1:19",
        "srcs_points_pace": "1:19–1:21",
        "srcs_backmarker_pace": "1:21.0+",
    },

    "abu_dhabi": {
        "round_name": "Round 10 — Abu Dhabi Grand Prix",
        "track_name": "Yas Marina Circuit",
        "race_date": "2026-12-06",

        # Section 1 — Real-Life Reference (F1)
        "official_race_lap_record": "1:26.103",
        "lap_record_driver": "Max Verstappen",
        "lap_record_year": 2021,
        "pole_position_benchmark": "~1:22.5 – 1:24.0",

        # Section 2 — SRCS Target Pace
        "srcs_target_lap_time": "1:31.500",
        "srcs_race_winning_pace": "1:31–1:32",
        "srcs_podium_pace": "1:32–1:34",
        "srcs_points_pace": "1:34–1:36",
        "srcs_backmarker_pace": "1:36.0+",
    },
}


def get_track_benchmark(track_key: str) -> dict:
    return TRACK_BENCHMARKS.get(track_key, {})


def get_track_options() -> dict:
    return {
        "Melbourne": "melbourne",
        "Japan": "Japan",
        "Miami": "miami",
        "Monaco": "monaco",
        "Silverstone": "silverstone",
        "Zandvoort": "zandvoort",
        "Monza": "monza",
        "Singapore": "singapore",
        "Interlagos": "interlagos",
        "Abu Dhabi": "abu_dhabi",
    }
