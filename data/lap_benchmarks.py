# data/lap_benchmarks.py

TRACK_BENCHMARKS = {
    "melbourne": {
        "round_name": "Round 1 — Australian Grand Prix",
        "track_name": "Albert Park, Melbourne",
        "race_date": "2026-03-08",
        "real_life_lap_record": "1:19.813",
        "lap_record_driver": "Charles Leclerc",
        "lap_record_year": 2024,
        "srcs_target_lap_time": "1:24.500",
    },
    "bahrain": {
        "round_name": "Round 2 — Bahrain Grand Prix",
        "track_name": "Bahrain International Circuit, Sakhir",
        "race_date": "2026-04-12",
        "real_life_lap_record": "1:31.447",
        "lap_record_driver": "Pedro de la Rosa",
        "lap_record_year": 2005,
        "srcs_target_lap_time": "1:36.500",
    },
    "miami": {
        "round_name": "Round 3 — Miami Grand Prix",
        "track_name": "Miami International Autodrome",
        "race_date": "2026-05-03",
        "real_life_lap_record": "1:29.708",
        "lap_record_driver": "Max Verstappen",
        "lap_record_year": 2023,
        "srcs_target_lap_time": "1:35.000",
    },
    "monaco": {
        "round_name": "Round 4 — Monaco Grand Prix",
        "track_name": "Circuit de Monaco, Monte Carlo",
        "race_date": "2026-06-07",
        "real_life_lap_record": "1:12.909",
        "lap_record_driver": "Lewis Hamilton",
        "lap_record_year": 2021,
        "srcs_target_lap_time": "1:19.500",
    },
    "silverstone": {
        "round_name": "Round 5 — British Grand Prix",
        "track_name": "Silverstone Circuit",
        "race_date": "2026-07-05",
        "real_life_lap_record": "1:27.097",
        "lap_record_driver": "Max Verstappen",
        "lap_record_year": 2020,
        "srcs_target_lap_time": "1:32.500",
    },
    "zandvoort": {
        "round_name": "Round 6 — Dutch Grand Prix",
        "track_name": "Circuit Zandvoort",
        "race_date": "2026-08-23",
        "real_life_lap_record": "1:11.097",
        "lap_record_driver": "Lewis Hamilton",
        "lap_record_year": 2021,
        "srcs_target_lap_time": "1:16.800",
    },
    "monza": {
        "round_name": "Round 7 — Italian Grand Prix",
        "track_name": "Autodromo Nazionale Monza",
        "race_date": "2026-09-06",
        "real_life_lap_record": "1:21.046",
        "lap_record_driver": "Rubens Barrichello",
        "lap_record_year": 2004,
        "srcs_target_lap_time": "1:26.500",
    },
    "singapore": {
        "round_name": "Round 8 — Singapore Grand Prix",
        "track_name": "Marina Bay Street Circuit",
        "race_date": "2026-10-11",
        "real_life_lap_record": "1:34.486",
        "lap_record_driver": "Daniel Ricciardo",
        "lap_record_year": 2024,
        "srcs_target_lap_time": "1:41.000",
    },
    "interlagos": {
        "round_name": "Round 9 — Brazilian Grand Prix",
        "track_name": "Interlagos, Sao Paulo",
        "race_date": "2026-11-08",
        "real_life_lap_record": "1:10.540",
        "lap_record_driver": "Valtteri Bottas",
        "lap_record_year": 2018,
        "srcs_target_lap_time": "1:16.000",
    },
    "abu_dhabi": {
        "round_name": "Round 10 — Abu Dhabi Grand Prix",
        "track_name": "Yas Marina Circuit",
        "race_date": "2026-12-06",
        "real_life_lap_record": "1:26.103",
        "lap_record_driver": "Max Verstappen",
        "lap_record_year": 2021,
        "srcs_target_lap_time": "1:31.500",
    },
}


def get_track_benchmark(track_key: str) -> dict:
    return TRACK_BENCHMARKS.get(track_key, {})


def get_track_options() -> dict:
    return {
        "Melbourne": "melbourne",
        "Bahrain": "bahrain",
        "Miami": "miami",
        "Monaco": "monaco",
        "Silverstone": "silverstone",
        "Zandvoort": "zandvoort",
        "Monza": "monza",
        "Singapore": "singapore",
        "Interlagos": "interlagos",
        "Abu Dhabi": "abu_dhabi",
    }
