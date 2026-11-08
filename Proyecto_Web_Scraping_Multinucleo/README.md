# Proyecto Web Scraping Multinúcleo

Proyecto académico para recolectar información de videojuegos, procesarla con tres niveles de concurrencia/paralelismo y publicarla en un catálogo web.

## Requisitos
- Python 3.11 o superior
- pip

## Instalación
```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

## Ejecutar la aplicación
```bash
uvicorn app.main:app --reload
```
Abrir http://127.0.0.1:8000

## Ejecutar pruebas de rendimiento
```bash
python -m app.benchmark
```

## Ejecutar el scraper (C#)
El scraper está en `Scraper/` (raíz del repositorio). Es una aplicación de consola .NET Framework 4.8.1 y se abre con `Scraper/Scraper.sln` en Visual Studio.

Lee el REPO de la base de datos SQLite `app/repo/repo.db` (tabla `juegos`, se puede editar con DB Browser for SQLite) y escribe los resultados en `app/repo/games.json`, que es el archivo que lee la web.

Antes de ejecutarlo hay que copiar `.env.example` como `.env` en la raíz y llenar `ESHOP_APP_ID` y `ESHOP_API_KEY` (pedir los valores al Integrante 1). El `.env` no se sube a GitHub.

Desde la raíz del repositorio:
```bash
dotnet build Scraper/Scraper.sln
Scraper/Scraper/bin/Debug/net481/Scraper.exe --generar-repo # arma el REPO (solo si no existe)
Scraper/Scraper/bin/Debug/net481/Scraper.exe                # paralelo con todos los núcleos
Scraper/Scraper/bin/Debug/net481/Scraper.exe --workers 4    # paralelo con 4 hilos
Scraper/Scraper/bin/Debug/net481/Scraper.exe --secuencial   # versión secuencial de referencia
```
`--limite K` procesa solo los primeros K juegos. Al final se imprime `Tiempo total: X s`. Los errores de cada fuente quedan en `Scraper/logs/errores.csv`.

## Reparto sugerido
- Integrante 1: `app/repo/`, `Scraper/` (C#)
- Integrante 2: `app/main.py`, `app/api/`, `app/templates/`, `app/static/`
- Integrante 3: `app/benchmark.py`, `app/services/`, pruebas, integración y documentación

## Acuerdos de integración
1. Los datos de un juego usan el esquema definido en `app/models.py`.
2. Las funciones de scraping devuelven diccionarios con claves estables y no modifican la interfaz web.
3. Ningún scraper debe detener toda la ejecución si una fuente falla.
4. Respetar términos de uso, límites y frecuencia de las páginas consultadas.
5. Las fuentes son Steam y Nintendo eShop (precios en USD), Metacritic (score de PC o, si no hay, de Switch) y HowLongToBeat.

## Estado
Esta plantilla contiene la estructura inicial y funciones de ejemplo. El equipo debe completar las fuentes de datos, la lógica de persistencia, los tres niveles y las pruebas.

## Benchmark real (Integrante 3)

Compilar `Scraper/Scraper.sln` en Visual Studio, configuración Debug, y comprobar que el archivo `.env` está en la raíz del repositorio. Desde la raíz:

```powershell
pip install -r Proyecto_Web_Scraping_Multinucleo/requirements-dev.txt
cd Proyecto_Web_Scraping_Multinucleo
python -m app.benchmark --mode real --repeats 3
```

El benchmark ejecuta el `Scraper.exe` real con modo secuencial y paralelo para 1, 2, 4 y el máximo de trabajadores. Requiere al menos 200 juegos en `app/repo/repo.db`. Los resultados y gráficos quedan en `results/`. Consultar `docs/INTEGRACION_INTEGRANTE3.md` para requisitos, interpretación y análisis.
