from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.catalog import all_games, catalog_meta, filter_games, sort_games

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Hottest Deals - Videojuegos")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    # La página es un "cascarón": las tarjetas las arma app/static/app.js con la API.
    return templates.TemplateResponse(request=request, name="index.html", context={})


@app.get("/api/games")
def games_api(q: str | None = None, platform: str | None = None, format: str | None = None,
              store: str | None = None, genre: str | None = None, on_sale: bool = False,
              sort: str = "name", order: str | None = None):
    """Lista de juegos (contrato + campos derivados), con filtros y orden opcionales.

    Ejemplo: /api/games?platform=PS5&format=fisico&sort=discount
    """
    games = filter_games(all_games(), q=q, platform=platform, fmt=format, store=store,
                         genre=genre, on_sale=on_sale)
    return sort_games(games, sort, order)


@app.get("/api/games/{game_id}")
def game_detail_api(game_id: str):
    for game in all_games():
        if game["id"] == game_id:
            return game
    raise HTTPException(status_code=404, detail="Juego no encontrado")


@app.get("/api/meta")
def meta_api():
    """Última actualización, moneda y opciones disponibles para los filtros."""
    return catalog_meta(all_games())


@app.get("/health")
def health():
    return {"status": "ok"}
