from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def scrape_store(game: dict, store_name: str) -> dict:
    \"\"\"Plantilla de scraper. Implementar una fuente real y respetar sus reglas de acceso.\"\"\"
    raise NotImplementedError(f"Falta implementar el scraper para {store_name}")


async def scrape_metacritic(game: dict) -> dict:
    \"\"\"Devolver metacritic_score u otro resultado acordado para el juego.\"\"\"
    raise NotImplementedError("Falta implementar la consulta a Metacritic")


async def scrape_hltb(game: dict) -> dict:
    \"\"\"Devolver hltb_main_hours u otro resultado acordado para el juego.\"\"\"
    raise NotImplementedError("Falta implementar la consulta a HowLongToBeat")
