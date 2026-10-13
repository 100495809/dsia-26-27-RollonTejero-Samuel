"""Módulo CLI para la ejecución del pipeline inmobiliario."""
import argparse
import json
import sys
from pathlib import Path

from .errors import InmueblesDomainError
from .loader import InmueblesLoader
from .metrics import InmueblesMetrics
from .validator import InmueblesValidator


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Pipeline de calidad y análisis de datos inmobiliarios (Idealista 2018)"
    )
    parser.add_argument(
        "--input",
        "-i",
        default="data/inmuebles_sample.csv",
        help="Ruta al fichero CSV de entrada",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="data/inmuebles_limpios.csv",
        help="Ruta al fichero CSV de salida limpio",
    )
    parser.add_argument(
        "--report",
        "-r",
        default=None,
        help="Ruta opcional para guardar el informe de calidad en JSON",
    )
    return parser.parse_args(argv)


def run_pipeline(
    input_path: Path | str,
    output_path: Path | str,
    report_path: Path | str | None = None,
) -> dict:
    """Ejecuta secuencialmente el pipeline: carga, validación, exportación y métricas."""
    loader = InmueblesLoader(input_path)
    validator = InmueblesValidator()
    metrics = InmueblesMetrics()

    raw_df = loader.load()
    valid_df, _ = validator.split(raw_df)

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    valid_df.to_csv(out_file, index=False)

    summary = metrics.summary(valid_df, len(raw_df))
    summary["precio_por_ciudad"] = metrics.precio_medio_por_ciudad(valid_df)
    summary["precio_m2_por_ciudad"] = metrics.precio_m2_por_ciudad(valid_df)
    summary["precio_por_habitaciones"] = metrics.precio_por_habitaciones(valid_df)

    if report_path:
        rep_file = Path(report_path)
        rep_file.parent.mkdir(parents=True, exist_ok=True)
        rep_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    return summary


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada principal del CLI."""
    args = parse_args(argv)

    try:
        results = run_pipeline(args.input, args.output, args.report)
    except InmueblesDomainError as err:
        print(f"Error en inmuebles_app: {err}", file=sys.stderr)
        return 1
    except Exception as err:
        print(f"Error inesperado: {err}", file=sys.stderr)
        return 2

    print(f"Procesamiento completado con éxito: {results['filas_validas']}/{results['filas_totales']} válidas.")
    print(f"Precio medio global: {results['precio_medio_global']:.2f} €")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
