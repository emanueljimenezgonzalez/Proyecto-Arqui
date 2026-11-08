"""Pruebas de la API del catálogo (Integrante 2).

Usan un archivo de datos temporal, así no dependen del scraper ni de internet.
"""
import json

import pytest
from fastapi.testclient import TestClient

from app.main import app

GAMES = [
    {
        "id": "g1", "name": "Bravo", "platforms": ["PC", "PS5"], "genre": "RPG",
        "release_date": "2020-01-01", "reference_price": 60, "image_url": None,
        "metacritic_score": 90, "hltb_main_hours": 30, "updated_at": "2026-11-08T10:00:00+00:00",
        "offers": [
            {"store": "Steam", "current_price": 30, "regular_price": 60, "format": "digital",
             "platform": "PC", "url": "https://example.com/a"},
            {"store": "Amazon", "current_price": 45, "regular_price": 60, "format": "fisico",
             "platform": "PS5", "url": "https://example.com/b"},
        ],
    },
    {
        "id": "g2", "name": "alfa", "platforms": ["Switch"], "genre": "Puzzle",
        "reference_price": 20, "metacritic_score": None, "updated_at": "2026-11-08T12:00:00+00:00",
        "offers": [
            # tienda caída: sin precio
            {"store": "Nintendo eShop", "current_price": None, "regular_price": None,
             "format": "digital", "platform": "Switch", "url": None},
            # sin precio regular: se usa el precio de referencia
            {"store": "Amazon", "current_price": 15, "format": "físico", "platform": "Switch"},
        ],
    },
    {   # registro casi vacío: no debe romper nada
        "id": "g3", "name": "Charlie", "platforms": [], "offers": [],
    },
]


@pytest.fixture
def client(tmp_path, monkeypatch):
    path = tmp_path / "games.json"
    path.write_text(json.dumps(GAMES), encoding="utf-8")
    monkeypatch.setenv("GAMES_DATA_FILE", str(path))
    return TestClient(app)


def names(resp):
    return [g["name"] for g in resp.json()]


def test_derived_fields(client):
    games = {g["id"]: g for g in client.get("/api/games").json()}
    g1 = games["g1"]
    assert g1["best_price"] == 30 and g1["best_store"] == "Steam"
    assert g1["regular_price"] == 60 and g1["discount_percent"] == 50 and g1["on_sale"]
    assert g1["formats"] == ["digital", "fisico"]

    g2 = games["g2"]
    assert g2["best_price"] == 15 and g2["regular_price"] == 20 and g2["discount_percent"] == 25
    assert g2["stores"] == ["Amazon"]  # la tienda sin precio no cuenta para filtros
    assert g2["offers"][0]["available"] and not g2["offers"][1]["available"]
    assert g2["offers"][0]["format"] == "fisico"  # normalizado

    g3 = games["g3"]
    assert g3["best_price"] is None and g3["discount_percent"] == 0 and not g3["on_sale"]


def test_keeps_contract_fields(client):
    game = client.get("/api/games/g1").json()
    for key in ("id", "name", "platforms", "release_date", "reference_price", "image_url",
                "metacritic_score", "hltb_main_hours", "offers", "updated_at"):
        assert key in game


def test_sorting(client):
    assert names(client.get("/api/games")) == ["alfa", "Bravo", "Charlie"]
    assert names(client.get("/api/games?sort=price")) == ["alfa", "Bravo", "Charlie"]
    assert names(client.get("/api/games?sort=price&order=desc")) == ["Bravo", "alfa", "Charlie"]
    assert names(client.get("/api/games?sort=discount")) == ["Bravo", "alfa", "Charlie"]
    # sin score va al final
    assert names(client.get("/api/games?sort=score")) == ["Bravo", "alfa", "Charlie"]


def test_filters(client):
    assert names(client.get("/api/games?platform=ps5")) == ["Bravo"]
    assert names(client.get("/api/games?format=fisico")) == ["alfa", "Bravo"]
    assert names(client.get("/api/games?format=digital")) == ["Bravo"]
    assert names(client.get("/api/games?store=Nintendo eShop")) == []
    assert names(client.get("/api/games?genre=puzzle")) == ["alfa"]
    assert names(client.get("/api/games?q=rav")) == ["Bravo"]
    assert names(client.get("/api/games?on_sale=true")) == ["alfa", "Bravo"]


def test_store_filter_recalculates_best_price(client):
    [bravo] = client.get("/api/games?store=Amazon&platform=PS5").json()
    assert bravo["best_price"] == 45 and bravo["best_store"] == "Amazon"
    assert bravo["discount_percent"] == 25
    assert len(bravo["offers"]) == 2  # el detalle conserva todas las ofertas
    # los filtros se cumplen en la MISMA oferta: Bravo es físico solo en PS5
    assert names(client.get("/api/games?platform=PC&format=fisico")) == []
    # ordenar por precio usa el precio de la tienda filtrada
    assert names(client.get("/api/games?store=Amazon&sort=price")) == ["alfa", "Bravo"]


def test_detail_sorted_offers_and_404(client):
    offers = client.get("/api/games/g1").json()["offers"]
    assert [o["current_price"] for o in offers] == [30, 45]
    assert client.get("/api/games/nope").status_code == 404


def test_meta(client):
    meta = client.get("/api/meta").json()
    assert meta["total_games"] == 3
    assert meta["last_updated"] == "2026-11-08T12:00:00+00:00"
    assert meta["filters"]["platforms"] == ["PC", "PS5", "Switch"]
    assert meta["filters"]["stores"] == ["Amazon", "Steam"]
    assert [f["value"] for f in meta["filters"]["formats"]] == ["digital", "fisico"]


def test_broken_json_keeps_last_valid_data(client, tmp_path):
    assert len(client.get("/api/games").json()) == 3
    path = tmp_path / "games.json"
    path.write_text('[{"id": "x", "na', encoding="utf-8")  # el scraper está escribiendo
    import os, time
    os.utime(path, (time.time() + 5, time.time() + 5))
    assert len(client.get("/api/games").json()) == 3


def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200 and "Hottest Deals" in resp.text
