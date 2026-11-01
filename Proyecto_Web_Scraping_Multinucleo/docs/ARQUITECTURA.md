# Arquitectura propuesta

## Flujo
REPO dinámico -> scraping multinivel -> normalización de resultados -> almacenamiento -> API y página pública.

## Tres niveles requeridos
1. Nivel 1: varios videojuegos del REPO procesados concurrentemente.
2. Nivel 2: para cada videojuego, consultas a Metacritic, HowLongToBeat y otras fuentes ejecutadas concurrentemente.
3. Nivel 3: al menos dos tiendas consultadas concurrentemente para cada videojuego.

## Nota técnica
Las solicitudes HTTP suelen esperar por la red, por lo que la concurrencia asíncrona puede ser útil. Para demostrar el uso de varios núcleos, implementen una prueba con procesos para trabajo apto para CPU y documenten qué parte se ejecuta en cada proceso. No presenten el número de hilos como si fuera automáticamente el número de núcleos usados.

## Pendientes
- Implementar las fuentes reales.
- Completar el REPO con 200 o más juegos.
- Guardar errores de cada fuente y mantener datos previos válidos cuando una consulta falla.
- Definir un intervalo de actualización y desplegar la web públicamente.
- Implementar benchmark repetible y gráficos de resultados.
