import sqlite3
import pytest
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
