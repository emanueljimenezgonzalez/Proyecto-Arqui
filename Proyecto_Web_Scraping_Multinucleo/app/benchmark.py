\"\"\"Plantilla de benchmark. Completar con la misma carga para modo secuencial y paralelo.\"\"\"
import time


def run_sequential():
    # TODO: implementar la versión secuencial de referencia.
    raise NotImplementedError


def run_parallel(workers: int):
    # TODO: ejecutar la misma carga con 1, 2, 4 y máximo de trabajadores disponible.
    raise NotImplementedError


def main():
    # Registrar tiempo, speedup = T_secuencial / T_paralelo
    # y eficiencia = speedup / cantidad_de_trabajadores.
    print("Completar las funciones run_sequential y run_parallel antes de medir.")


if __name__ == "__main__":
    main()
