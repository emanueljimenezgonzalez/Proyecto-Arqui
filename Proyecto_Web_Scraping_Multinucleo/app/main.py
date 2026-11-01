from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.repo.repository import list_games

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Hottest Deals - Videojuegos")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request, platform: str | None = None, sort: str = "name"):
    games = list_games()
    if platform:
        games = [g for g in games if platform.lower() in [p.lower() for p in g.get("platforms", [])]]
    if sort == "price":
        games.sort(key=lambda g: g.get("best_price") if g.get("best_price") is not None else float("inf"))
    elif sort == "discount":
        games.sort(key=lambda g: g.get("discount_percent", 0), reverse=True)
    elif sort == "score":
        games.sort(key=lambda g: g.get("metacritic_score") or 0, reverse=True)
    else:
        games.sort(key=lambda g: g.get("name", "").lower())
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"games": games, "platform": platform or "", "sort": sort},
    )


@app.get("/api/games")
def games_api():
    return list_games()


@app.get("/health")
def health():
    return {"status": "ok"}
