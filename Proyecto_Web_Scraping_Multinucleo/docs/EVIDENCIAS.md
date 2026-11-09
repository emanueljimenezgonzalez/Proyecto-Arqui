# Galería de Evidencias de Ejecución

Este documento recopila las capturas de pantalla de las pruebas, validaciones, interfaz gráfica y mediciones de rendimiento del proyecto.

---

## 1. Pruebas automatizadas (Pytest)
Ejecución de la suite completa de pruebas unitarias y de integración (19 tests pasando al 100%).

![Ejecución de pruebas Pytest](evidencias/01_ejecucion_pruebas_pytest.png)

---

## 2. Validación del catálogo y base de datos SQLite
Validación de integridad del archivo `games.json` (200 juegos con precios de ambas tiendas) e inspección de la base de datos `repo.db`.

![Validación de catálogo y SQLite](evidencias/02_validacion_catalogo_datos.png)

---

## 3. Ejecución del benchmark de rendimiento multinúcleo
Salida de la consola con la ejecución de las mediciones secuenciales y paralelas (1, 2, 4 y 8 trabajadores), cálculo de Speedup y Eficiencia.

![Ejecución de Benchmark](evidencias/03_ejecucion_benchmark_rendimiento.png)

---

## 4. Gráficas de rendimiento (Ley de Amdahl)
Curvas de tiempo, aceleración y eficiencia generadas a partir de las muestras de ejecución.

### Tiempo paralelo frente a trabajadores
![Tiempo por trabajadores](../results/tiempo_por_trabajadores.png)

### Speedup frente a trabajadores
![Speedup por trabajadores](../results/speedup_por_trabajadores.png)

### Eficiencia frente a trabajadores
![Eficiencia por trabajadores](../results/eficiencia_por_trabajadores.png)

---

## 5. Catálogo web en ejecución (Hottest Deals)
Página principal servida con FastAPI y Uvicorn mostrando el catálogo completo, tarjetas con precios en Steam y Nintendo eShop, badges de oferta y Metacritic.

![Catálogo Web Hottest Deals](evidencias/04_catalogo_web_hottest_deals.png)

---

## 6. Catálogo web con filtros aplicados
Filtrado reactivo en el navegador mostrando únicamente los juegos en oferta.

![Catálogo Filtrado](evidencias/05_catalogo_web_filtros_ofertas.png)

---

## 7. Vista de detalle de videojuego (Modal interactivo)
Detalle completo de un videojuego con desglose comparativo de precios por tienda, formato, horas en HowLongToBeat y enlaces directos de compra.

![Modal de Detalle](evidencias/06_detalle_juego_modal.png)
