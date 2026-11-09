# Página web y API (Integrante 2)

## Archivos
- `app/main.py`: rutas de FastAPI.
- `app/api/catalog.py`: lectura de datos, campos derivados, filtros y ordenamiento.
- `app/templates/index.html`: estructura de la página.
- `app/static/app.js`: tarjetas, filtros, orden y detalle (consume la API con `fetch`).
- `app/static/styles.css`: estilos.
- `tests/test_api.py`: pruebas de la API (usan un JSON temporal, no necesitan el scraper).

## Ejecutar
```bash
uvicorn app.main:app --reload
```
La API lee `app/repo/games.json`, el archivo que escribe el scraper. Si se vuelve a correr el scraper, la página toma los datos nuevos sin reiniciar el servidor. La variable de entorno opcional `GAMES_DATA_FILE` permite apuntar a otro JSON con el mismo formato.

```bash
python -m pytest tests/test_api.py
```

## Endpoints
| Ruta | Descripción |
|---|---|
| `GET /api/games` | Lista de juegos. Parámetros opcionales: `q`, `platform`, `format` (tipo: `fisico`, `digital`, `otro`), `store`, `on_sale=true`, `sort` (`name`, `price`, `discount`, `score`) y `order` (`asc`, `desc`). |
| `GET /api/games/{id}` | Detalle de un juego, con las ofertas ordenadas por precio. |
| `GET /api/meta` | Última actualización, moneda, total y opciones de cada filtro. |
| `GET /health` | Estado del servicio. |

Cada juego conserva todos los campos del contrato y la API agrega estos campos calculados: `best_price`, `best_store`, `best_url`, `regular_price`, `discount_percent`, `on_sale`, `formats` y `stores`. Además, a cada oferta se le agregan `discount_percent` y `available`.

## Decisiones
- **Filtro "Tipo":** el equipo acordó que el tipo de juego (físico, digital u otro) es `offers[].format`, así que en la página es un solo filtro, "Tipo / formato". Siempre muestra las tres opciones con la cantidad de juegos de cada una, por ejemplo "Físico (0)". Con las tiendas actuales (Steam y Nintendo eShop) todo es digital, pero si el scraper agrega una tienda física, el filtro funciona sin cambiar código.
- **Indicador de oferta:** se compara el precio actual del mejor precio con el **precio regular de esa misma tienda**. Si la tienda no reporta precio regular, se usa `reference_price` del REPO. Descuento = `(1 - actual / regular) * 100`.
- **Filtros por oferta:** plataforma, formato y tienda se aplican a cada oferta. Un juego aparece si **una misma oferta** cumple los tres filtros, y el mejor precio, el descuento y el orden se recalculan solo con esas ofertas. Por ejemplo, "Tienda: Nintendo eShop" muestra y ordena según el precio del eShop. El detalle siempre muestra todas las tiendas.
- **Datos faltantes:** las ofertas sin precio aparecen como "No disponible" y no cuentan para el mejor precio ni para los filtros de tienda o formato. Los juegos sin precio o sin score quedan al final cuando se ordena.
- **Robustez:** el archivo de datos se vuelve a leer solo cuando cambia. Si el scraper lo está escribiendo y el JSON queda incompleto, se siguen mostrando los últimos datos válidos.
- **Actualización:** la página revisa `/api/meta` cada 5 minutos y, si los datos cambiaron, recarga el catálogo sin perder los filtros.
- **Enlaces compartibles:** los filtros quedan en la URL (`?platform=PS5&sort=discount`) y el detalle usa `#juego/<id>`.
- **Seguridad:** todo texto que viene del scraping se escapa antes de mostrarse, y solo se aceptan enlaces absolutos `http(s)`.

## Otros acuerdos
- **Valores de `format`:** la API acepta `digital` y `fisico`/`físico`/`physical`. Cualquier otro valor lo trata como `otro`.
- **Moneda:** USD, igual que el scraper. Se puede cambiar con la variable de entorno `CURRENCY`.
- **Publicación:** está explicada en `PUBLICACION.md`.
