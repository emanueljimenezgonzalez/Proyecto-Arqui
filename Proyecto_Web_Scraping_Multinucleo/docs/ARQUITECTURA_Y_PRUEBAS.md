# Arquitectura y pruebas de integración

## Flujo de datos
REPO dinámico -> scraper -> normalización de datos -> persistencia -> API FastAPI -> interfaz web.

## Responsables de integración
- Integrante 1: garantiza que el scraper entregue el contrato de datos acordado.
- Integrante 2: consume el contrato a través de la API y presenta filtros, ordenamientos y detalles.
- Integrante 3: verifica la compatibilidad entre los módulos, documenta errores y ejecuta pruebas de rendimiento.

## Protocolo de integración
1. Fijar nombres y tipos de campos en `docs/CONTRATO_DATOS.md`.
2. Probar cada módulo con datos de ejemplo.
3. Integrar mediante ramas de Git y revisar cambios antes de fusionarlos.
4. Probar la API con un registro completo y otro con datos nulos.
5. Simular una fuente caída y confirmar que el proceso continúa.
6. Ejecutar el benchmark real cuando existan las versiones secuencial y paralela.
7. Guardar resultados y registrar la configuración exacta.
8. Hacer una prueba final de la página desplegada.

## Informe de incidencias
Para cada fallo registrar: fecha/hora, módulo, fuente, videojuego, tipo de error, acción tomada y si se conservó un dato previo válido.
