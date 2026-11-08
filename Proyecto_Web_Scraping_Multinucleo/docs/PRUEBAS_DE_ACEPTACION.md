# Pruebas de aceptación del equipo

Marcar cada punto cuando esté implementado y probado. La plantilla inicial no cumple todavía todos estos puntos.

## Datos y scraping
- [ ] El REPO tiene al menos 200 juegos y puede editarse sin cambiar el código.
- [ ] Cada juego incluye nombre, plataformas, fecha y precio de referencia.
- [ ] Se consultan al menos dos tiendas por juego.
- [ ] Se obtiene score de Metacritic.
- [ ] Se obtiene tiempo de HowLongToBeat.
- [ ] El nivel 1 procesa juegos en paralelo.
- [ ] El nivel 2 consulta fuentes de un juego en paralelo.
- [ ] El nivel 3 consulta tiendas en paralelo.
- [ ] Hay timeout, registro de fallos y reintentos controlados.
- [ ] Una fuente caída no detiene toda la ejecución.

## Página web
- [ ] Sitio accesible por URL pública.
- [ ] Tarjetas con imagen, título, mejor precio, precio regular, descuento, plataforma y score.
- [ ] Filtros por tipo, plataforma, formato y tienda.
- [ ] Ordenamiento por nombre, precio, descuento y score.
- [ ] Vista de detalle con precios y enlaces.
- [ ] Se muestra fecha y hora de actualización.
- [ ] La actualización recurrente funciona.

## Rendimiento
- [ ] Versión secuencial de referencia.
- [ ] Mediciones con 1, 2, 4 y máximo de trabajadores o núcleos disponibles.
- [ ] Se usa la misma carga de trabajo para comparar.
- [ ] Se calcula speedup = tiempo secuencial / tiempo paralelo.
- [ ] Se calcula eficiencia = speedup / cantidad de trabajadores usada.
- [ ] Se presentan gráficos y análisis de cuellos de botella y Ley de Amdahl.

## Entrega
- [ ] Código fuente en repositorio.
- [ ] URL pública funcional.
- [ ] Documento técnico con arquitectura y tres niveles.
- [ ] Instrucciones de instalación y ejecución.
- [ ] Demostración ensayada por los tres integrantes.
