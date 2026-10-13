"""Módulo CLI para la ejecución del pipeline de ventas."""
import argparse
import json
import sys
from pathlib import Path

from .errors import SalesDomainError
from .loader import SalesLoader
from .metrics import SalesMetrics
from .validator import SalesValidator


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Pipeline de calidad y análisis de datos de ventas"
    )
    parser.add_argument(
        "--input",
        "-i",
        default="data/ventas.csv",
        help="Ruta al fichero CSV de entrada",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="data/ventas_limpias.csv",
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
    loader = SalesLoader(input_path)
    validator = SalesValidator()
    metrics = SalesMetrics()

    raw_df = loader.load()
    valid_df, _ = validator.split(raw_df)

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    valid_df.to_csv(out_file, index=False)

    summary = metrics.summary(valid_df, len(raw_df))
    summary["importe_por_region"] = metrics.total_by_region(valid_df)
    summary["top_productos"] = metrics.top_products(valid_df)

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
    except SalesDomainError as err:
        print(f"Error en ventas_app: {err}", file=sys.stderr)
        return 1
    except Exception as err:
        print(f"Error inesperado: {err}", file=sys.stderr)
        return 2

    print(f"Procesamiento completado con éxito: {results['filas_validas']}/{results['filas_totales']} filas válidas.")
    print(f"Importe total: {results['importe_total']:.2f} €")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())