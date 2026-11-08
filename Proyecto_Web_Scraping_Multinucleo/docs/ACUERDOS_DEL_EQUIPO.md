# Acuerdos del equipo

## Objetivo común
Construir un catálogo web público de videojuegos que recolecte datos desde varias fuentes, implemente tres niveles de paralelismo y compare la versión paralela con una versión secuencial.

## Reglas de trabajo
1. No renombrar campos del contrato de datos sin avisar a los otros integrantes.
2. Cada integrante trabaja en una rama propia de Git.
3. Antes de modificar archivos de otra persona, consultar al responsable del módulo.
4. No subir contraseñas, tokens, claves ni archivos `.env` a GitHub.
5. Cada cambio debe incluir una prueba manual o automatizada cuando corresponda.
6. Si una fuente falla, el programa debe registrar el error y seguir procesando otros juegos.
7. No afirmar que el sistema usa varios núcleos únicamente porque tenga muchos hilos. Documentar y medir la estrategia usada.
8. Respetar las condiciones de acceso y los límites de cada sitio consultado.

## Responsables
- Integrante 1: REPO, scraping, fuentes y normalización de datos.
- Integrante 2: página web, filtros, ordenamiento, detalle y conexión con la API.
- Integrante 3: versión secuencial, pruebas de rendimiento, gráficos, documentación e integración.

## Acuerdos antes de programar
- Moneda que mostrará el catálogo.
- Tiendas que se consultarán.
- Fuentes para Metacritic y HowLongToBeat.
- Intervalo de actualización.
- Dónde se desplegará la web.
- Quién revisará y aprobará cada cambio de Git.
