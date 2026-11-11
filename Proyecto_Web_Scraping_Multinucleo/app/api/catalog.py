"""Lógica del catálogo para la API (Integrante 2).

Lee los juegos con el contrato de docs/CONTRATO_DATOS.md, calcula los campos
derivados (mejor precio, descuento, formatos, tiendas) y aplica filtros y
ordenamiento. No modifica el archivo de datos: solo lo lee.

Fuente de datos:
- Por defecto, el REPO real: app/repo/games.json (lo escribe el scraper).
- Opcional: variable de entorno GAMES_DATA_FILE apuntando a otro JSON con el
  mismo formato (las pruebas automáticas la usan con un archivo temporal).
"""
from __future__ import annotations

import json
import logging
import os
import threading
from pathlib import Path
from typing import Any

from app.repo.repository import DATA_FILE as REPO_DATA_FILE

log = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

FORMAT_LABELS = {"digital": "Digital", "fisico": "Físico", "físico": "Físico", "otro": "Otro"}
SORT_KEYS = {"name", "price", "discount", "score"}


def data_file() -> Path:
    custom = os.environ.get("GAMES_DATA_FILE")
    if not custom:
        return REPO_DATA_FILE
    path = Path(custom)
    return path if path.is_absolute() else PROJECT_ROOT / path


# ---------------------------------------------------------------------------
# Carga con caché: se relee solo cuando el archivo cambia. Si el scraper está
# escribiendo y el JSON queda a medias, se sigue mostrando la última versión
# válida en vez de romper la página.
# ---------------------------------------------------------------------------
_cache: dict[str, Any] = {"path": None, "mtime": None, "games": []}
_lock = threading.Lock()


def load_raw_games() -> tuple[list[dict], float | None]:
    path = data_file()
    try:
        mtime = path.stat().st_mtime
    except FileNotFoundError:
        return [], None
    with _lock:
        if _cache["path"] == path and _cache["mtime"] == mtime:
            return _cache["games"], mtime
        try:
            games = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(games, list):
                raise ValueError("el archivo debe contener una lista de juegos")
        except (ValueError, OSError) as exc:
            log.warning("No se pudo leer %s (%s); se usan los datos anteriores", path, exc)
            return _cache["games"] if _cache["path"] == path else [], _cache["mtime"]
        _cache.update(path=path, mtime=mtime, games=games)
        return games, mtime


# ---------------------------------------------------------------------------
# Campos derivados
# ---------------------------------------------------------------------------
def _num(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) if value >= 0 else None


def normalize_format(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text in ("fisico", "físico", "physical"):
        return "fisico"
    if text == "digital":
        return "digital"
    return "otro"


def discount(current: float | None, regular: float | None) -> int:
    if current is None or not regular or current >= regular:
        return 0
    return round((1 - current / regular) * 100)


def enrich(game: dict) -> dict:
    """Devuelve una copia del juego con los campos que necesita la página.

    Indicador de oferta: se compara el precio actual con el precio regular que
    muestra la misma tienda. Si la tienda no da precio regular, se usa el
    precio de referencia (sugerido) del REPO.
    """
    reference = _num(game.get("reference_price"))
    offers = []
    for raw in game.get("offers") or []:
        if not isinstance(raw, dict):
            continue
        current = _num(raw.get("current_price"))
        regular = _num(raw.get("regular_price")) or reference
        offers.append({
            **raw,
            "current_price": current,
            "regular_price": regular,
            "format": normalize_format(raw.get("format")),
            "discount_percent": discount(current, regular),
            "available": current is not None,
        })
    # Lista ordenada: primero las que tienen precio (de menor a mayor)
    offers.sort(key=lambda o: (not o["available"], o["current_price"] or 0, o.get("store") or ""))

    valid = [o for o in offers if o["available"]]
    best = valid[0] if valid else None
    best_regular = best["regular_price"] if best else None

    return {
        **game,
        "platforms": list(game.get("platforms") or []),
        "offers": offers,
        "best_price": best["current_price"] if best else None,
        "best_store": best.get("store") if best else None,
        "best_url": best.get("url") if best else None,
        "regular_price": best_regular,
        "discount_percent": best["discount_percent"] if best else 0,
        "on_sale": bool(best and best["discount_percent"] > 0),
        "formats": sorted({o["format"] for o in valid}),
        "stores": sorted({o.get("store") for o in valid if o.get("store")}),
    }


def all_games() -> list[dict]:
    games, _ = load_raw_games()
    return [enrich(g) for g in games if isinstance(g, dict) and g.get("id")]


# ---------------------------------------------------------------------------
# Filtros y ordenamiento
# ---------------------------------------------------------------------------
def _matches(value: str | None, options: list[str]) -> bool:
    return not value or value.lower() in (o.lower() for o in options if o)


def _offer_matches(offer: dict, platform: str | None, fmt: str | None, store: str | None) -> bool:
    return (offer["available"]
            and (not platform or (offer.get("platform") or "").lower() == platform.lower())
            and (not fmt or offer["format"] == normalize_format(fmt))
            and (not store or (offer.get("store") or "").lower() == store.lower()))


def filter_games(games: list[dict], *, q: str | None = None, platform: str | None = None,
                 fmt: str | None = None, store: str | None = None,
                 genre: str | None = None, on_sale: bool = False) -> list[dict]:
    """Filtra juegos.

    El filtro "Tipo" de la página es el formato de la oferta (offers[].format:
    físico, digital u otro), como acordó el equipo.

    Plataforma, formato y tienda se aplican a las OFERTAS: el juego aparece si
    tiene al menos una oferta con precio que cumpla los tres filtros a la vez, y
    su mejor precio y descuento se recalculan solo con esas ofertas. Así, por
    ejemplo, "Tienda: Nintendo eShop" muestra el precio del eShop.
    """
    query = (q or "").strip().lower()
    by_offer = bool(platform or fmt or store)
    out = []
    for g in games:
        if query and query not in (g.get("name") or "").lower():
            continue
        if genre:
            game_genres = g.get("genre") or []
            if isinstance(game_genres, str):
                game_genres = [game_genres]
            elif not isinstance(game_genres, (list, tuple, set)):
                game_genres = []
            normalized_genres = {str(item).strip().casefold() for item in game_genres if item}
            if genre.strip().casefold() not in normalized_genres:
                continue
        if by_offer:
            matching = [o for o in g["offers"] if _offer_matches(o, platform, fmt, store)]
            if not matching:
                continue
            # se recalculan los derivados con las ofertas filtradas (lista completa en el detalle)
            g = {**enrich({**g, "offers": matching}), "offers": g["offers"]}
        if on_sale and not g["on_sale"]:
            continue
        out.append(g)
    return out


def sort_games(games: list[dict], sort: str = "name", order: str | None = None) -> list[dict]:
    """Los juegos sin el dato (precio o score) siempre van al final."""
    sort = sort if sort in SORT_KEYS else "name"
    default_desc = sort in ("discount", "score")
    desc = default_desc if order not in ("asc", "desc") else order == "desc"

    if sort == "name":
        return sorted(games, key=lambda g: (g.get("name") or "").lower(), reverse=desc)

    field = {"price": "best_price", "discount": "discount_percent", "score": "metacritic_score"}[sort]
    with_value = [g for g in games if _num(g.get(field)) is not None]
    without = [g for g in games if _num(g.get(field)) is None]
    with_value.sort(key=lambda g: (g.get("name") or "").lower())
    with_value.sort(key=lambda g: g[field], reverse=desc)
    return with_value + sorted(without, key=lambda g: (g.get("name") or "").lower())


# ---------------------------------------------------------------------------
# Metadatos
# ---------------------------------------------------------------------------
def catalog_meta(games: list[dict]) -> dict:
    _, mtime = load_raw_games()
    updated = [g["updated_at"] for g in games if g.get("updated_at")]
    path = data_file()
    return {
        "total_games": len(games),
        "last_updated": max(updated) if updated else None,
        "data_version": mtime,
        "currency": os.environ.get("CURRENCY", "USD"),
        "data_source": "repo" if path == REPO_DATA_FILE else path.name,
        "filters": {
            "platforms": sorted({p for g in games for p in g["platforms"] if p}),
            # Siempre las tres opciones del filtro "Tipo", aunque alguna tenga 0 juegos
            "formats": [
                {"value": f, "label": FORMAT_LABELS[f],
                 "count": sum(1 for g in games if f in g["formats"])}
                for f in ("digital", "fisico", "otro")
            ],
            "stores": sorted({s for g in games for s in g["stores"]}),
            "genres": sorted({
                str(item).strip()
                for g in games
                for item in ([g.get("genre")] if isinstance(g.get("genre"), str)
                             else (g.get("genre") or []))
                if item and str(item).strip()
            }, key=str.casefold),
        },
    }
