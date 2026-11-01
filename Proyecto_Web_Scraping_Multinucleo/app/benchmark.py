"""Herramientas de medición para el proyecto de scraping multinúcleo.

Modo demo:
    python -m app.benchmark --mode demo --games 200 --repeats 3

El modo demo valida las fórmulas y el mecanismo de medición con una carga simulada.
No representa resultados reales de scraping y no debe presentarse como medición final.

Modo real:
    Requiere integrar las funciones secuencial y paralela de los scrapers reales.
    Ver docs/INTEGRACION_INTEGRANTE3.md.
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import platform
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"


def calculate_metrics(sequential_seconds: float, parallel_seconds: float,
                      workers: int) -> dict[str, float | int]:
    """Calcula speedup y eficiencia. Los tiempos deben ser positivos."""
    if sequential_seconds <= 0 or parallel_seconds <= 0:
        raise ValueError("Los tiempos deben ser mayores que cero.")
    if workers < 1:
        raise ValueError("workers debe ser al menos 1.")
    speedup = sequential_seconds / parallel_seconds
    efficiency = speedup / workers
    return {
        "sequential_seconds": sequential_seconds,
        "parallel_seconds": parallel_seconds,
        "workers": workers,
        "speedup": speedup,
        "efficiency": efficiency,
    }


def available_worker_counts() -> list[int]:
    """Devuelve 1, 2, 4 y el máximo disponible, sin repetir valores."""
    maximum = os.cpu_count() or 1
    return sorted({n for n in (1, 2, 4, maximum) if n <= maximum})


def synthetic_task(game: dict[str, Any], work_ms: int = 8) -> dict[str, Any]:
    """Carga simulada para verificar el benchmark; no consulta sitios web."""
    # Trabajo de espera simulada. No se debe usar como resultado académico final.
    time.sleep(work_ms / 1000)
    return {"id": game["id"], "ok": True}


def time_sync_batch(games: list[dict[str, Any]], workers: int,
                    work_ms: int) -> float:
    """Mide una carga de prueba secuencial o con pool de hilos."""
    start = time.perf_counter()
    if workers == 1:
        for game in games:
            synthetic_task(game, work_ms)
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            list(executor.map(lambda game: synthetic_task(game, work_ms), games))
    return time.perf_counter() - start


def make_demo_games(count: int) -> list[dict[str, str]]:
    return [{"id": f"demo-{i:04d}", "name": f"Juego de prueba {i}"} for i in range(count)]


def run_demo(games_count: int, repeats: int, work_ms: int) -> list[dict[str, Any]]:
    """Ejecuta benchmark de demostración con carga sintética."""
    games = make_demo_games(games_count)
    worker_counts = available_worker_counts()
    sequential_samples = [time_sync_batch(games, 1, work_ms) for _ in range(repeats)]
    sequential_median = statistics.median(sequential_samples)
    rows: list[dict[str, Any]] = []

    for workers in worker_counts:
        samples = [time_sync_batch(games, workers, work_ms) for _ in range(repeats)]
        parallel_median = statistics.median(samples)
        metrics = calculate_metrics(sequential_median, parallel_median, workers)
        rows.append({
            "mode": "demo_sintetico_no_final",
            "games": games_count,
            "workers": workers,
            "sequential_seconds": round(sequential_median, 6),
            "parallel_seconds": round(parallel_median, 6),
            "speedup": round(float(metrics["speedup"]), 4),
            "efficiency": round(float(metrics["efficiency"]), 4),
            "repeats": repeats,
            "work_ms_per_game": work_ms,
            "machine_cpu_count": os.cpu_count() or 1,
            "platform": platform.platform(),
        })
    return rows


def write_results(rows: list[dict[str, Any]], output_dir: Path = RESULTS_DIR) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "benchmark_results.csv"
    json_path = output_dir / "benchmark_results.json"
    if not rows:
        raise ValueError("No hay resultados para guardar.")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return csv_path, json_path


def write_charts(rows: list[dict[str, Any]], output_dir: Path = RESULTS_DIR) -> list[Path]:
    """Genera gráficos de tiempo, speedup y eficiencia desde los resultados."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("Instala matplotlib con: pip install matplotlib") from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    workers = [row["workers"] for row in rows]
    chart_specs = [
        ("parallel_seconds", "Tiempo paralelo (segundos)", "tiempo_por_trabajadores.png"),
        ("speedup", "Speedup", "speedup_por_trabajadores.png"),
        ("efficiency", "Eficiencia", "eficiencia_por_trabajadores.png"),
    ]
    paths = []
    for key, ylabel, filename in chart_specs:
        fig, ax = plt.subplots()
        ax.plot(workers, [row[key] for row in rows], marker="o")
        ax.set_xlabel("Cantidad de trabajadores")
        ax.set_ylabel(ylabel)
        ax.set_title(ylabel + " frente a trabajadores")
        ax.set_xticks(workers)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        path = output_dir / filename
        fig.savefig(path, dpi=150)
        plt.close(fig)
        paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark del proyecto multinúcleo")
    parser.add_argument("--mode", choices=["demo"], default="demo",
                        help="demo valida las fórmulas con una carga simulada")
    parser.add_argument("--games", type=int, default=200)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--work-ms", type=int, default=8)
    args = parser.parse_args()

    if args.games < 1 or args.repeats < 1 or args.work_ms < 0:
        parser.error("games y repeats deben ser positivos; work-ms no puede ser negativo.")

    rows = run_demo(args.games, args.repeats, args.work_ms)
    csv_path, json_path = write_results(rows)
    chart_paths = write_charts(rows)
    print("Benchmark de demostración terminado.")
    print("ATENCIÓN: estos resultados son sintéticos y no son mediciones del scraping real.")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    for chart_path in chart_paths:
        print(f"Gráfico: {chart_path}")
    print()
    print(f"{'Trabajadores':>14} {'Secuencial (s)':>16} {'Paralelo (s)':>14} {'Speedup':>10} {'Eficiencia':>12}")
    for row in rows:
        print(f"{row['workers']:>14} {row['sequential_seconds']:>16.4f} "
              f"{row['parallel_seconds']:>14.4f} {row['speedup']:>10.3f} "
              f"{row['efficiency']:>12.3f}")


if __name__ == "__main__":
    main()
