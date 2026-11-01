# Integración, pruebas y rendimiento. Integrante 3

## Responsabilidad
Preparar pruebas de integración, medir la versión secuencial y la paralela con la misma carga, calcular speedup y eficiencia, generar gráficos y documentar los resultados reales.

## Estado de esta entrega
`app/benchmark.py` contiene un benchmark de demostración con una carga sintética. Sirve para verificar el cálculo y la exportación de resultados. No consulta tiendas ni representa el rendimiento final del scraping.

## Métricas exigidas
Tiempo secuencial: `T_seq`, duración total de la versión secuencial.

Tiempo paralelo: `T_par`, duración total de la versión paralela usando N trabajadores.

Speedup:
`S = T_seq / T_par`

Eficiencia:
`E = S / N`

Usar la misma lista de videojuegos, mismas fuentes, mismos criterios y condiciones comparables. Hacer varias repeticiones y reportar la mediana. Anotar la máquina, cantidad de núcleos lógicos, configuración, fecha, errores y cantidad de registros procesados.

La eficiencia puede ser mayor que 1 en algunos escenarios por variabilidad de medidas o por diferencias de implementación. Investigar y documentar esos casos en vez de ocultarlos.

## Cómo ejecutar las pruebas de demostración
Desde la carpeta que contiene `app/` y `tests/`:

```bash
python -m app.benchmark --mode demo --games 200 --repeats 3
```

Se generan:
- `results/benchmark_results.csv`
- `results/benchmark_results.json`

Los resultados de demostración no se deben incluir como resultados finales del scraping real.

## Integración requerida con el integrante 1
Antes de medir el rendimiento real, el equipo debe acordar dos funciones que reciban la misma lista de juegos:

1. Una función secuencial que consulte cada juego y cada fuente de manera secuencial.
2. Una función paralela que implemente los tres niveles solicitados.

Ambas deben devolver resultados equivalentes con el mismo esquema de datos. El benchmark debe medir la ejecución completa, no una función diferente en cada modo.

No es válido llamar a una función que ya ejecuta scraping paralelo para representar la versión secuencial.

## Pruebas de integración mínimas
- REPO con al menos 200 juegos.
- Identificadores de juegos únicos.
- Campos obligatorios presentes.
- Cada juego contiene ofertas de al menos dos tiendas cuando las fuentes están disponibles.
- Un fallo de una tienda no detiene el resto de los juegos.
- Los datos se guardan con el esquema acordado.
- La API devuelve JSON con los mismos campos.
- La página presenta precios, descuentos, plataforma, Metacritic y última actualización.
- Los filtros y ordenamientos funcionan con registros con datos faltantes.
- La versión secuencial y la paralela procesan la misma carga.
- Los archivos de resultados conservan configuración, tiempos y métricas.

## Gráficos y análisis
Cuando existan mediciones reales, generar como mínimo:
1. Barras de tiempo total frente al número de trabajadores.
2. Barras de speedup frente al número de trabajadores.
3. Barras de eficiencia frente al número de trabajadores.

Explicar los efectos de latencia de red, límites de las fuentes, número de trabajadores, tareas que no se paralelizan y posibles cuellos de botella. Relacionar el análisis con la Ley de Amdahl.

## Ley de Amdahl
`Speedup_max = 1 / (s + (1 - s) / N)`

`s` es la fracción secuencial del trabajo y `N` la cantidad de procesadores o trabajadores considerados. La fórmula estima el speedup teórico bajo sus supuestos; no sustituye las mediciones.

## Qué documentar en el informe
- Equipo y entorno de pruebas.
- Versión del código y fuentes consultadas.
- Tamaño de la carga.
- Número de repeticiones.
- Tiempos obtenidos y método de agregación.
- Tabla con tiempos, speedup y eficiencia.
- Gráficos y explicación de resultados.
- Errores, datos faltantes y amenazas a la validez.
- Conclusiones sustentadas en mediciones reales.
