import pytest
from app.benchmark import calculate_metrics, available_worker_counts, make_demo_games


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
    counts = available_worker_counts()
    assert 1 in counts
    assert counts == sorted(set(counts))
    assert all(value >= 1 for value in counts)


def test_make_demo_games_count_and_ids():
    games = make_demo_games(200)
    assert len(games) == 200
    assert games[0]["id"] == "demo-0000"
    assert games[-1]["id"] == "demo-0199"
