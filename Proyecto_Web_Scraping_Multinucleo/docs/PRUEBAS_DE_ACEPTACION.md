# Pruebas de aceptación del equipo

Estado de verificación de cada requerimiento del proyecto.

## Datos y scraping
- [x] El REPO tiene al menos 200 juegos y puede editarse sin cambiar el código (`app/repo/repo.db`).
- [x] Cada juego incluye nombre, plataformas, fecha y precio de referencia.
- [x] Se consultan al menos dos tiendas por juego (Steam y Nintendo eShop).
- [x] Se obtiene score de Metacritic (score de PC o Switch, con fallback controlado).
- [x] Se obtiene tiempo de HowLongToBeat (duración de la historia principal).
- [x] El nivel 1 procesa juegos en paralelo (`Thread`s + `ConcurrentQueue`).
- [x] El nivel 2 consulta fuentes de un juego en paralelo (`Task.Run` + `Task.WhenAll`).
- [x] El nivel 3 consulta tiendas en paralelo (`Task.Run` + `Task.WhenAll`).
- [x] Hay timeout, registro de fallos y reintentos controlados (`Http.cs` con backoff y semáforos).
- [x] Una fuente caída no detiene toda la ejecución (se conservan datos previos y se registra en `errores.csv`).

## Página web
- [x] Sitio accesible por URL pública (desplegable en Render mediante `render.yaml`).
- [x] Tarjetas con imagen, título, mejor precio, precio regular, descuento, plataforma y score.
- [x] Filtros por tipo/formato, plataforma y tienda.
- [x] Ordenamiento por nombre, precio, descuento y score.
- [x] Vista de detalle con precios y enlaces a tiendas externas.
- [x] Se muestra fecha y hora de actualización.
- [x] La actualización recurrente funciona (GitHub Actions cada 6 horas).

## Rendimiento
- [x] Versión secuencial de referencia (`Scraper.exe --secuencial`).
- [x] Mediciones con 1, 2, 4 y máximo de trabajadores o núcleos disponibles (`app.benchmark`).
- [x] Se usa la misma carga de trabajo para comparar (los 200 juegos del REPO).
- [x] Se calcula speedup = tiempo secuencial / tiempo paralelo (`calculate_metrics`).
- [x] Se calcula eficiencia = speedup / cantidad de trabajadores usada.
- [x] Se presentan gráficos y análisis de cuellos de botella y Ley de Amdahl en `results/`.

## Entrega
- [x] Código fuente en repositorio.
- [x] Documento técnico con arquitectura y tres niveles (`docs/ARQUITECTURA.md`, `docs/SCRAPING_INTEGRANTE1.md`, etc.).
- [x] Instrucciones de instalación y ejecución (`README.md`).
- [ ] URL pública funcional confirmada en Render.
- [ ] Demostración ensayada por los tres integrantes.
