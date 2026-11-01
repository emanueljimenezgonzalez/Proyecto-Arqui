import asyncio
from app.repo.repository import load_repo, save_games
from app.scrapers.base import scrape_store, scrape_metacritic, scrape_hltb, utc_now_iso

STORES = ["TiendaA", "TiendaB"]
MAX_GAMES_IN_FLIGHT = 4


async def safe_call(coro, fallback):
    try:
        return await asyncio.wait_for(coro, timeout=20)
    except Exception as exc:
        # Registrar el error en una versión final, sin detener el lote completo.
        return {**fallback, "error": str(exc)}


async def scrape_one_game(game: dict) -> dict:
    # Nivel 2: fuentes distintas para un mismo juego se consultan en paralelo.
    tasks = [
        safe_call(scrape_metacritic(game), {"metacritic_score": None}),
        safe_call(scrape_hltb(game), {"hltb_main_hours": None}),
    ]
    # Nivel 3: al menos dos tiendas se consultan en paralelo.
    tasks.extend(
        safe_call(scrape_store(game, store), {"store": store, "current_price": None})
        for store in STORES
    )
    results = await asyncio.gather(*tasks)
    merged = dict(game)
    offers = []
    for result in results:
        if "store" in result:
            offers.append(result)
        else:
            merged.update(result)
    merged["offers"] = offers
    merged["updated_at"] = utc_now_iso()
    return merged


async def run_parallel_scraping() -> list[dict]:
    games = load_repo()
    semaphore = asyncio.Semaphore(MAX_GAMES_IN_FLIGHT)

    async def limited(game):
        async with semaphore:
            return await scrape_one_game(game)

    # Nivel 1: procesar varios juegos del REPO concurrentemente.
    results = await asyncio.gather(*(limited(game) for game in games), return_exceptions=True)
    cleaned = []
    for game, result in zip(games, results):
        if isinstance(result, Exception):
            cleaned.append({**game, "updated_at": utc_now_iso(), "scrape_error": str(result)})
        else:
            cleaned.append(result)
    save_games(cleaned)
    return cleaned
