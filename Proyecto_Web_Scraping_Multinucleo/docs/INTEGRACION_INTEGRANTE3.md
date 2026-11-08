# Rendimiento, integración y pruebas. Integrante 3

## Implementación entregada

El benchmark ejecuta el scraper real desarrollado en C# mediante `Scraper.exe`. No implementa una segunda versión del scraping ni simula las consultas en el modo real.

El programa C# ya ofrece dos modos:

- Secuencial: `Scraper.exe --secuencial`.
- Paralelo: `Scraper.exe --workers N`.

El benchmark toma el tiempo interno que imprime el programa en la línea `Tiempo total: X s`. De esta forma no incluye el tiempo de iniciar el proceso de Windows.

## Requisitos previos

1. Windows con .NET Framework 4.8.1.
2. Visual Studio con las herramientas para compilar proyectos .NET Framework 4.8.1.
3. Python 3.11 o superior.
4. Dependencias de desarrollo instaladas con `pip install -r requirements-dev.txt`.
5. Archivo `.env` en la raíz del repositorio con las claves de eShop. No subirlo a Git.
6. Base `Proyecto_Web_Scraping_Multinucleo/app/repo/repo.db` con al menos 200 juegos.
7. Compilar `Scraper/Scraper.sln` en configuración Debug. El ejecutable esperado es `Scraper/Scraper/bin/Debug/net481/Scraper.exe`.

## Ejecutar el benchmark real

Desde la raíz del repositorio:

```powershell
python -m app.benchmark --mode real --repeats 3
```

El programa comprueba que la base tenga al menos 200 juegos. Ejecuta la versión secuencial y las versiones paralelas con 1, 2, 4 y el máximo de procesadores lógicos disponibles. Si el máximo coincide con 1, 2 o 4, no repite esa configuración.

Para indicar una ruta distinta al ejecutable:

```powershell
python -m app.benchmark --mode real --exe "C:\ruta\Scraper.exe" --repeats 3
```

Para modificar el tiempo de espera máximo por ejecución o la pausa entre ejecuciones:

```powershell
python -m app.benchmark --mode real --repeats 3 --timeout 7200 --cooldown 5
```

Cada configuración procesa el REPO completo. El parámetro `--cooldown` agrega una pausa entre corridas para reducir la frecuencia de solicitudes a los sitios consultados.

## Archivos generados

Se crea la carpeta `results/` con:

- `benchmark_results.csv`: tabla de mediciones y métricas.
- `benchmark_results.json`: muestras y metadatos de las corridas.
- `tiempo_por_trabajadores.png`: tiempo paralelo frente al número de trabajadores.
- `speedup_por_trabajadores.png`: speedup frente al número de trabajadores.
- `eficiencia_por_trabajadores.png`: eficiencia frente al número de trabajadores.

El CSV incluye la mediana del tiempo secuencial, mediana del tiempo paralelo, speedup, eficiencia, cantidad de juegos, repeticiones, errores reportados, CPU lógica y sistema operativo. El JSON también conserva las muestras individuales.

## Fórmulas

Tiempo secuencial: `Tseq`.

Tiempo paralelo con N trabajadores: `Tpar`.

`Speedup = Tseq / Tpar`

`Eficiencia = Speedup / N`

Se utiliza la mediana de las repeticiones para reducir el efecto de ejecuciones atípicas. Una eficiencia superior a 1 se conserva y debe analizarse, no corregirse artificialmente.

## Interpretación y Ley de Amdahl

El primer nivel de concurrencia usa el número de hilos configurado con `--workers`. Los niveles internos crean tareas para consultar las tiendas, Metacritic y HowLongToBeat. Por esta razón, N representa los trabajadores del primer nivel, no el total de tareas activas del proceso.

La ejecución puede estar condicionada por la latencia de red, los tiempos de respuesta de cada fuente, límites de solicitudes, tareas que no se paralelizan y el costo de coordinar hilos y tareas. Aumentar N no garantiza una reducción proporcional del tiempo.

La estimación teórica de Amdahl es:

`Speedup_max = 1 / (s + (1 - s) / N)`

`s` representa la fracción secuencial del trabajo y `N` el número de trabajadores considerado. La estimación ayuda a interpretar las mediciones, pero no sustituye los resultados experimentales.

## Pruebas automatizadas

Desde la carpeta `Proyecto_Web_Scraping_Multinucleo`:

```powershell
python -m pytest -q
```

Las pruebas validan las fórmulas, selección de trabajadores, lectura del tiempo reportado por el scraper y conteo de juegos del REPO. No ejecutan consultas reales a tiendas.

## Registro de resultados para el informe

Después de ejecutar el benchmark real, incorporar al documento técnico:

1. Procesador, cantidad de procesadores lógicos, memoria y sistema operativo.
2. Fecha, versión del código y cantidad de juegos.
3. Número de repeticiones y pausas entre corridas.
4. Tabla del CSV con tiempos, speedup y eficiencia.
5. Los tres gráficos generados.
6. Errores por fuente y datos que no se pudieron obtener.
7. Explicación de los cuellos de botella observados y relación con Amdahl.

No incluir los resultados del modo `demo` como mediciones del scraping. El modo demo existe únicamente para comprobar el cálculo y la generación de archivos.
