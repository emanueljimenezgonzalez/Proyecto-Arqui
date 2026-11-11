import sqlite3
from pathlib import Path
import pytest
from app import benchmark
from app.benchmark import (
    calculate_metrics, available_worker_counts, parse_scraper_output,
    count_repo_games,
)


def test_calculate_metrics():
    result = calculate_metrics(12.0, 3.0, 4)
    assert result["speedup"] == pytest.approx(4.0)
    assert result["efficiency"] == pytest.approx(1.0)


def test_calculate_metrics_rejects_zero_time():
    with pytest.raises(ValueError):
        calculate_metrics(0, 1, 2)


def test_calculate_metrics_rejects_invalid_workers():
    with pytest.raises(ValueError):
        calculate_metrics(1, 1, 0)


def test_worker_counts_include_required_values_when_available():
    counts = available_worker_counts(8)
    assert counts == [1, 2, 4, 8]


def test_worker_counts_do_not_duplicate_maximum():
    assert available_worker_counts(4) == [1, 2, 4]


def test_parse_scraper_output_reads_elapsed_time_and_errors():
    seconds, errors = parse_scraper_output(
        "Errores registrados: 7\nTiempo total: 12.345 s\n"
    )
    assert seconds == pytest.approx(12.345)
    assert errors == 7


def test_parse_scraper_output_accepts_decimal_comma():
    seconds, errors = parse_scraper_output("Tiempo total: 2,500 s")
    assert seconds == pytest.approx(2.5)
    assert errors is None


def test_parse_scraper_output_rejects_missing_time():
    with pytest.raises(RuntimeError, match="Tiempo total"):
        parse_scraper_output("El proceso terminó")


def test_count_repo_games(tmp_path):
    database = tmp_path / "repo.db"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE juegos (id TEXT)")
        connection.executemany("INSERT INTO juegos VALUES (?)", [(str(i),) for i in range(200)])
    assert count_repo_games(database) == 200


def test_count_repo_games_rejects_missing_database(tmp_path):
    with pytest.raises(FileNotFoundError):
        count_repo_games(tmp_path / "missing.db")


def test_run_levels_passes_flags_and_compares_with_full(monkeypatch):
    times = {"": 10.0, "--sin-nivel2": 30.0, "--sin-nivel3": 15.0,
             "--sin-nivel2 --sin-nivel3": 40.0}
    calls = []

    def fake_run(executable, mode, workers, timeout, extra_args):
        calls.append(extra_args)
        return {"seconds": times[" ".join(extra_args)], "errors": 0}

    monkeypatch.setattr(benchmark, "run_scraper", fake_run)
    monkeypatch.setattr(benchmark, "count_repo_games", lambda: 200)
    rows = benchmark.run_levels(Path("Scraper.exe"), workers=4, repeats=1, cooldown_seconds=0)

    assert [row["config"] for row in rows] == ["completo", "sin_nivel2", "sin_nivel3", "sin_nivel2_y_3"]
    assert rows[1]["times_slower_than_full"] == pytest.approx(3.0)
    assert ["--sin-nivel2", "--sin-nivel3"] in calls
