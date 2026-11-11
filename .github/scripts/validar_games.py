"""Revisa el games.json que generó el scraper antes de publicarlo.

Si algo está mal, termina con error y el workflow NO sube el archivo, así la
página sigue mostrando los últimos datos buenos.

Uso: python .github/scripts/validar_games.py RUTA_GAMES_JSON [--max-horas 2]
"""
import json
import sys
from datetime import datetime, timedelta, timezone

MIN_JUEGOS = 200
OFERTAS = 2  # Steam y Nintendo eShop
CAMPOS = ("id", "name", "platforms", "release_date", "reference_price", "image_url",
          "metacritic_score", "hltb_main_hours", "offers", "updated_at")


def fallar(mensaje: str) -> None:
    print(f"ERROR: {mensaje}")
    sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        fallar("falta la ruta del games.json")
    ruta = sys.argv[1]
    max_horas = float(sys.argv[sys.argv.index("--max-horas") + 1]) if "--max-horas" in sys.argv else 2

    try:
        with open(ruta, encoding="utf-8") as f:
            juegos = json.load(f)
    except (OSError, ValueError) as exc:
        fallar(f"no se pudo leer {ruta}: {exc}")

    if not isinstance(juegos, list):
        fallar("el archivo debe ser una lista de juegos")
    if len(juegos) < MIN_JUEGOS:
        fallar(f"solo hay {len(juegos)} juegos (mínimo {MIN_JUEGOS})")

    ids = [g.get("id") for g in juegos]
    if len(set(ids)) != len(ids):
        fallar("hay ids repetidos")
    for g in juegos:
        faltan = [c for c in CAMPOS if c not in g]
        if faltan:
            fallar(f"al juego {g.get('id')} le faltan los campos {faltan}")
        if len(g["offers"]) != OFERTAS:
            fallar(f"el juego {g.get('id')} tiene {len(g['offers'])} ofertas (deben ser {OFERTAS})")

    # Que el scraper realmente haya corrido ahora (si no tenía claves, no escribe nada nuevo)
    fechas = [g["updated_at"] for g in juegos if g.get("updated_at")]
    if not fechas:
        fallar("ningún juego tiene updated_at")
    ultima = datetime.fromisoformat(max(fechas).replace("Z", "+00:00"))
    if datetime.now(timezone.utc) - ultima > timedelta(hours=max_horas):
        fallar(f"los datos no son recientes (última actualización {ultima.isoformat()})")

    con_precio = sum(1 for g in juegos
                     if any(o.get("current_price") is not None for o in g.get("offers", [])))
    print(f"OK: {len(juegos)} juegos, {con_precio} con precio, última actualización {ultima.isoformat()}")


if __name__ == "__main__":
    main()
