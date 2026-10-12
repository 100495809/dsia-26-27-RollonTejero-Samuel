"""Módulo CLI para la ejecución del pipeline de ventas."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from .errors import SalesDomainError
from .loader import CsvSalesRepository
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
        help="Ruta al fichero CSV de entrada (por defecto: data/ventas.csv)",
    )

    parser.add_argument(
        "--output",
        "-o",
        default="data/ventas_limpias.csv",
        help="Ruta al fichero CSV de salida limpio (por defecto: data/ventas_limpias.csv)",
    )

    parser.add_argument(
        "--report",
        "-r",
        default=None,
        help="Ruta opcional para guardar el informe de calidad y métricas en JSON",
    )

    return parser.parse_args(argv)


def run_pipeline(
    input_path: Path | str,
    output_path: Path | str,
    report_path: Path | str | None = None,
) -> dict[str, Any]:
    """Ejecuta secuencialmente el pipeline: carga, validación, exportación y métricas."""
    loader = CsvSalesRepository(input_path)
    validator = SalesValidator()
    metrics = SalesMetrics()

    # 1. Cargar datos
    raw_df = loader.load()

    # 2. Validar y separar registros
    records, invalid_df = validator.split(raw_df)

    # 3. Exportar CSV limpio con la columna 'importe'
    if records:
        clean_df = pd.DataFrame([
            {
                "fecha": r.fecha,
                "region": r.region,
                "producto": r.producto,
                "unidades": r.unidades,
                "precio_unitario": r.precio_unitario,
                "cliente_id": r.cliente_id,
                "importe": r.importe,
            }
            for r in records
        ])
    else:
        clean_df = pd.DataFrame(columns=[
            "fecha", "region", "producto", "unidades", "precio_unitario", "cliente_id", "importe"
        ])

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(out_file, index=False)

    # 4. Calcular métricas
    summary = metrics.summary(records, len(raw_df))
    summary["importe_por_region"] = metrics.total_by_region(records)
    summary["top_productos"] = metrics.top_products(records, n=3)

    # 5. Exportar reporte JSON si se solicita
    if report_path:
        rep_file = Path(report_path)
        rep_file.parent.mkdir(parents=True, exist_ok=True)
        rep_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    return summary


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada principal de la aplicación."""
    args = parse_args(argv)

    try:
        results = run_pipeline(args.input, args.output, args.report)
    except SalesDomainError as err:
        print(f"Error de dominio en el pipeline de ventas: {err}", file=sys.stderr)
        return 1
    except Exception as err:
        print(f"Error inesperado: {err}", file=sys.stderr)
        return 2

    print("Procesamiento completado con éxito:")
    print(f"  - Filas totales: {results['filas_totales']}")
    print(f"  - Registros válidos: {results['filas_validas']}")
    print(f"  - Registros inválidos: {results['filas_invalidas']}")
    print(f"  - Importe total: {results['importe_total']:.2f} €")

    print("\nImporte por región:")
    for region, total in results["importe_por_region"].items():
        print(f"  {region}: {total:.2f} €")

    print("\nTop 3 productos:")
    for prod, total in results["top_productos"].items():
        print(f"  {prod}: {total:.2f} €")

    print(f"\nDatos limpios guardados en: {args.output}")
    if args.report:
        print(f"Reporte de calidad guardado en: {args.report}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())