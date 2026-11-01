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

## Reparto sugerido
- Integrante 1: `app/repo/`, `app/scrapers/`, `app/services/scraping_service.py`
- Integrante 2: `app/main.py`, `app/api/`, `app/templates/`, `app/static/`
- Integrante 3: `app/benchmark.py`, `app/services/`, pruebas, integración y documentación

## Acuerdos de integración
1. Los datos de un juego usan el esquema definido en `app/models.py`.
2. Las funciones de scraping devuelven diccionarios con claves estables y no modifican la interfaz web.
3. Ningún scraper debe detener toda la ejecución si una fuente falla.
4. Respetar términos de uso, límites y frecuencia de las páginas consultadas.
5. No se incluyen scrapers específicos de tiendas en esta plantilla. Cada fuente debe implementarse y probarse con sus condiciones de acceso.

## Estado
Esta plantilla contiene la estructura inicial y funciones de ejemplo. El equipo debe completar las fuentes de datos, la lógica de persistencia, los tres niveles y las pruebas.
