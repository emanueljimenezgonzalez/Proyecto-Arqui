import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "games.json"


def load_repo() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def list_games() -> list[dict]:
    games = load_repo()
    for game in games:
        offers = [o for o in game.get("offers", []) if o.get("current_price") is not None]
        best = min(offers, key=lambda o: o["current_price"]) if offers else None
        game["best_price"] = best["current_price"] if best else None
        # El descuento se compara con el precio regular de la misma tienda
        regular = best.get("regular_price") if best else None
        game["discount_percent"] = round((1 - game["best_price"] / regular) * 100, 1) if (
            best is not None and regular and regular > 0 and game["best_price"] < regular
        ) else 0
    return games


def save_games(games: list[dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(games, file, ensure_ascii=False, indent=2)
