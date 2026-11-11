"""Benchmark real del scraper C# y modo sintético de comprobación.

Ejemplo Windows, desde la raíz del repositorio:
    python -m app.benchmark --mode real --repeats 3

Efecto de cada nivel (mismos hilos en el nivel 1, apagando el nivel 2 y/o el 3):
    python -m app.benchmark --mode niveles --workers 4 --repeats 3

El modo real ejecuta Scraper.exe, que mide el trabajo dentro del proceso y muestra
"Tiempo total: X s". Se utiliza ese tiempo para excluir el arranque del proceso.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import re
import sqlite3
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
def find_default_exe() -> Path:
    mac_exe = ROOT.parent / "Scraper" / "Scraper" / "bin" / "Debug" / "net10.0" / "Scraper"
    win_exe = ROOT.parent / "Scraper" / "Scraper" / "bin" / "Debug" / "net481" / "Scraper.exe"
    if sys.platform != "win32" and mac_exe.is_file():
        return mac_exe
    return win_exe


DEFAULT_EXE = find_default_exe()
DB_PATH = ROOT / "app" / "repo" / "repo.db"
TIME_PATTERN = re.compile(r"Tiempo total:\s*([0-9]+(?:[.,][0-9]+)?)\s*s", re.IGNORECASE)
ERROR_PATTERN = re.compile(r"Errores registrados:\s*(\d+)", re.IGNORECASE)

# Configuraciones del modo "niveles": nombre y opciones extra del scraper
LEVEL_CONFIGS = [
    ("completo", []),
    ("sin_nivel2", ["--sin-nivel2"]),
    ("sin_nivel3", ["--sin-nivel3"]),
    ("sin_nivel2_y_3", ["--sin-nivel2", "--sin-nivel3"]),
]


def calculate_metrics(sequential_seconds: float, parallel_seconds: float,
                      workers: int) -> dict[str, float | int]:
    if sequential_seconds <= 0 or parallel_seconds <= 0:
        raise ValueError("Los tiempos deben ser mayores que cero.")
    if workers < 1:
        raise ValueError("workers debe ser al menos 1.")
    speedup = sequential_seconds / parallel_seconds
    return {"sequential_seconds": sequential_seconds,
            "parallel_seconds": parallel_seconds, "workers": workers,
            "speedup": speedup, "efficiency": speedup / workers}


def available_worker_counts(maximum: int | None = None) -> list[int]:
    maximum = maximum or os.cpu_count() or 1
    return sorted({n for n in (1, 2, 4, maximum) if n <= maximum})


def parse_scraper_output(output: str) -> tuple[float, int | None]:
    match = TIME_PATTERN.search(output)
    if not match:
        raise RuntimeError(
            "El scraper no reportó 'Tiempo total: X s'. Salida recibida:\n" + output[-3000:]
        )
    seconds = float(match.group(1).replace(",", "."))
    if seconds <= 0:
        raise RuntimeError("El scraper reportó un tiempo no válido.")
    error_match = ERROR_PATTERN.search(output)
    return seconds, int(error_match.group(1)) if error_match else None


def count_repo_games(db_path: Path = DB_PATH) -> int:
    if not db_path.is_file():
        raise FileNotFoundError(f"No se encontró la base REPO: {db_path}")
    with sqlite3.connect(str(db_path)) as connection:
        row = connection.execute("SELECT COUNT(*) FROM juegos").fetchone()
    return int(row[0])


def run_scraper(executable: Path, mode: str, workers: int | None = None,
                timeout_seconds: int = 7200, extra_args: list[str] | None = None) -> dict[str, Any]:
    if not executable.is_file():
        raise FileNotFoundError(
            f"No se encontró Scraper.exe en {executable}. "
            "Compila Scraper.sln en Visual Studio, configuración Debug."
        )
    if mode not in {"sequential", "parallel"}:
        raise ValueError("mode debe ser sequential o parallel.")
    command = [str(executable)]
    if mode == "sequential":
        command.append("--secuencial")
    else:
        if workers is None or workers < 1:
            raise ValueError("Indica un número válido de workers.")
        command.extend(["--workers", str(workers)])
    command.extend(extra_args or [])

    completed = subprocess.run(
        command, cwd=str(ROOT.parent), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout_seconds,
        check=False
    )
    output = (completed.stdout or "") + "\n" + (completed.stderr or "")
    if completed.returncode != 0:
        raise RuntimeError(f"Scraper terminó con código {completed.returncode}:\n{output[-3000:]}")
    if "Faltan ESHOP_APP_ID" in output:
        raise RuntimeError("Faltan ESHOP_APP_ID o ESHOP_API_KEY en el archivo .env de la raíz.")
    if "No existe el REPO" in output or "No se encontro la carpeta" in output:
        raise RuntimeError(output.strip())
    seconds, errors = parse_scraper_output(output)
    return {"seconds": seconds, "errors": errors, "output": output,
            "command": command}


def run_real(executable: Path = DEFAULT_EXE, repeats: int = 3,
             timeout_seconds: int = 7200, cooldown_seconds: float = 2.0,
             maximum_workers: int | None = None) -> list[dict[str, Any]]:
    if repeats < 1:
        raise ValueError("repeats debe ser al menos 1.")
    game_count = count_repo_games()
    if game_count < 200:
        raise ValueError(f"El REPO tiene {game_count} juegos. Se requieren al menos 200.")
    worker_counts = available_worker_counts(maximum_workers)
    seq_samples: list[dict[str, Any]] = []
    par_samples: dict[int, list[dict[str, Any]]] = {n: [] for n in worker_counts}

    # Se alterna el orden de las configuraciones entre repeticiones para reducir
    # el sesgo de ejecutar siempre una configuración primero.
    for repetition in range(repeats):
        seq_samples.append(run_scraper(executable, "sequential", timeout_seconds=timeout_seconds))
        if cooldown_seconds:
            time.sleep(cooldown_seconds)
        for workers in worker_counts:
            par_samples[workers].append(
                run_scraper(executable, "parallel", workers, timeout_seconds)
            )
            if cooldown_seconds:
                time.sleep(cooldown_seconds)

    sequential_median = statistics.median(x["seconds"] for x in seq_samples)
    rows: list[dict[str, Any]] = []
    for workers, samples in par_samples.items():
        parallel_median = statistics.median(x["seconds"] for x in samples)
        metrics = calculate_metrics(sequential_median, parallel_median, workers)
        rows.append({
            "mode": "scraping_real_csharp",
            "games": game_count,
            "workers": workers,
            "sequential_seconds": round(sequential_median, 6),
            "parallel_seconds": round(parallel_median, 6),
            "speedup": round(float(metrics["speedup"]), 6),
            "efficiency": round(float(metrics["efficiency"]), 6),
            "repeats": repeats,
            "sequential_samples": json.dumps([round(x["seconds"], 6) for x in seq_samples]),
            "parallel_samples": json.dumps([round(x["seconds"], 6) for x in samples]),
            "sequential_errors_median": statistics.median(
                x["errors"] or 0 for x in seq_samples
            ),
            "parallel_errors_median": statistics.median(
                x["errors"] or 0 for x in samples
            ),
            "machine_cpu_count": os.cpu_count() or 1,
            "platform": platform.platform(),
            "python_version": sys.version.split()[0],
            "executable": str(executable),
        })
    return rows


def run_levels(executable: Path = DEFAULT_EXE, workers: int = 4, repeats: int = 3,
               timeout_seconds: int = 7200, cooldown_seconds: float = 2.0) -> list[dict[str, Any]]:
    """Mide el efecto de los niveles 2 y 3 con la misma cantidad de hilos en el nivel 1."""
    if repeats < 1:
        raise ValueError("repeats debe ser al menos 1.")
    game_count = count_repo_games()
    samples: dict[str, list[dict[str, Any]]] = {name: [] for name, _ in LEVEL_CONFIGS}

    # Igual que en run_real, cada repetición pasa por todas las configuraciones
    for _ in range(repeats):
        for name, extra_args in LEVEL_CONFIGS:
            samples[name].append(
                run_scraper(executable, "parallel", workers, timeout_seconds, extra_args)
            )
            if cooldown_seconds:
                time.sleep(cooldown_seconds)

    full_median = statistics.median(x["seconds"] for x in samples["completo"])
    rows: list[dict[str, Any]] = []
    for name, _ in LEVEL_CONFIGS:
        median = statistics.median(x["seconds"] for x in samples[name])
        rows.append({
            "mode": "efecto_por_nivel",
            "config": name,
            "games": game_count,
            "workers": workers,
            "median_seconds": round(median, 6),
            "times_slower_than_full": round(median / full_median, 6),
            "repeats": repeats,
            "samples": json.dumps([round(x["seconds"], 6) for x in samples[name]]),
            "errors_median": statistics.median(x["errors"] or 0 for x in samples[name]),
            "machine_cpu_count": os.cpu_count() or 1,
            "platform": platform.platform(),
            "executable": str(executable),
        })
    return rows


def write_level_chart(rows: list[dict[str, Any]], output_dir: Path = RESULTS_DIR) -> Path:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("Instala matplotlib con: pip install -r requirements-dev.txt") from exc
    output_dir.mkdir(parents=True, exist_ok=True)
    labels = {"completo": "Completo", "sin_nivel2": "Sin nivel 2",
              "sin_nivel3": "Sin nivel 3", "sin_nivel2_y_3": "Sin niveles 2 y 3"}
    fig, ax = plt.subplots()
    ax.bar([labels[row["config"]] for row in rows], [float(row["median_seconds"]) for row in rows])
    ax.set_ylabel("Tiempo mediano (segundos)")
    ax.set_title(f"Efecto de cada nivel con {rows[0]['workers']} hilos en el nivel 1")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    path = output_dir / "efecto_por_nivel.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def write_results(rows: list[dict[str, Any]], output_dir: Path = RESULTS_DIR,
                  name: str = "benchmark_results") -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path, json_path = output_dir / f"{name}.csv", output_dir / f"{name}.json"
    if not rows:
        raise ValueError("No hay resultados para guardar.")
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return csv_path, json_path


def write_charts(rows: list[dict[str, Any]], output_dir: Path = RESULTS_DIR) -> list[Path]:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("Instala matplotlib con: pip install -r requirements-dev.txt") from exc
    output_dir.mkdir(parents=True, exist_ok=True)
    workers = [int(row["workers"]) for row in rows]
    specs = [
        ("parallel_seconds", "Tiempo paralelo (segundos)", "tiempo_por_trabajadores.png"),
        ("speedup", "Speedup", "speedup_por_trabajadores.png"),
        ("efficiency", "Eficiencia", "eficiencia_por_trabajadores.png"),
    ]
    paths = []
    for key, label, filename in specs:
        fig, ax = plt.subplots()
        ax.plot(workers, [float(row[key]) for row in rows], marker="o")
        ax.set_xlabel("Trabajadores del nivel 1")
        ax.set_ylabel(label)
        ax.set_title(label + " frente a trabajadores")
        ax.set_xticks(workers)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        path = output_dir / filename
        fig.savefig(path, dpi=160)
        plt.close(fig)
        paths.append(path)
    return paths


def synthetic_task(game: dict[str, Any], work_ms: int = 8) -> None:
    time.sleep(work_ms / 1000)


def run_demo(games_count: int, repeats: int, work_ms: int) -> list[dict[str, Any]]:
    """Modo de prueba sintético. No representa rendimiento del scraper."""
    from concurrent.futures import ThreadPoolExecutor
    games = [{"id": i} for i in range(games_count)]
    sequential = []
    for _ in range(repeats):
        start = time.perf_counter()
        for game in games:
            synthetic_task(game, work_ms)
        sequential.append(time.perf_counter() - start)
    seq_median = statistics.median(sequential)
    rows = []
    for workers in available_worker_counts():
        samples = []
        for _ in range(repeats):
            start = time.perf_counter()
            if workers == 1:
                for game in games:
                    synthetic_task(game, work_ms)
            else:
                with ThreadPoolExecutor(max_workers=workers) as pool:
                    list(pool.map(lambda g: synthetic_task(g, work_ms), games))
            samples.append(time.perf_counter() - start)
        par_median = statistics.median(samples)
        metrics = calculate_metrics(seq_median, par_median, workers)
        rows.append({"mode": "demo_sintetico_no_final", "games": games_count,
                     "workers": workers, "sequential_seconds": seq_median,
                     "parallel_seconds": par_median, "speedup": metrics["speedup"],
                     "efficiency": metrics["efficiency"], "repeats": repeats,
                     "machine_cpu_count": os.cpu_count() or 1, "platform": platform.platform()})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Medición del scraper multinúcleo")
    parser.add_argument("--mode", choices=["real", "demo", "niveles"], default="real")
    parser.add_argument("--workers", type=int, default=4,
                        help="Hilos del nivel 1 en el modo niveles")
    parser.add_argument("--exe", type=Path, default=DEFAULT_EXE,
                        help="Ruta a Scraper.exe compilado")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--cooldown", type=float, default=2.0)
    parser.add_argument("--max-workers", type=int, default=None,
                        help="Permite fijar el máximo para pruebas controladas")
    parser.add_argument("--games", type=int, default=200,
                        help="Cantidad para el modo demo")
    parser.add_argument("--work-ms", type=int, default=8)
    args = parser.parse_args()
    if args.repeats < 1 or args.timeout < 1 or args.cooldown < 0:
        parser.error("repeats y timeout deben ser positivos y cooldown no puede ser negativo.")

    if args.mode == "niveles":
        if args.workers < 1:
            parser.error("workers debe ser al menos 1.")
        rows = run_levels(args.exe, args.workers, args.repeats, args.timeout, args.cooldown)
        csv_path, json_path = write_results(rows, name="niveles_results")
        chart = write_level_chart(rows)
        print("Medición por niveles terminada.")
        print("CSV:", csv_path)
        print("JSON:", json_path)
        print("Gráfico:", chart)
        print(f"{'Configuración':>18} {'Mediana (s)':>12} {'Veces más lento':>16}")
        for row in rows:
            print(f"{row['config']:>18} {row['median_seconds']:>12.3f} "
                  f"{row['times_slower_than_full']:>16.2f}")
        return

    if args.mode == "real":
        rows = run_real(args.exe, args.repeats, args.timeout, args.cooldown, args.max_workers)
    else:
        if args.games < 1 or args.work_ms < 0:
            parser.error("games debe ser positivo y work-ms no puede ser negativo.")
        rows = run_demo(args.games, args.repeats, args.work_ms)

    csv_path, json_path = write_results(rows)
    charts = write_charts(rows)
    print("Medición terminada.")
    print("Tipo:", rows[0]["mode"])
    if rows[0]["mode"] == "demo_sintetico_no_final":
        print("AVISO: los datos sintéticos no son resultados académicos.")
    print("CSV:", csv_path)
    print("JSON:", json_path)
    for chart in charts:
        print("Gráfico:", chart)
    print(f"{'Workers':>8} {'Secuencial (s)':>16} {'Paralelo (s)':>14} {'Speedup':>10} {'Eficiencia':>12}")
    for row in rows:
        print(f"{row['workers']:>8} {row['sequential_seconds']:>16.4f} "
              f"{row['parallel_seconds']:>14.4f} {row['speedup']:>10.3f} "
              f"{row['efficiency']:>12.3f}")


if __name__ == "__main__":
    main()
