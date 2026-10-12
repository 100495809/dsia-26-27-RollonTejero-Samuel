"""Tests unitarios y funcionales para el módulo CLI de ventas_app."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from ventas_app.cli import main, parse_args, run_pipeline


def test_cli_parse_args_valores_personalizados() -> None:
    """Verifica que parse_args procese correctamente las flags de línea de comandos."""
    args = parse_args(["--input", "mi_entrada.csv", "--output", "mi_salida.csv", "--report", "reporte.json"])

    assert args.input == "mi_entrada.csv"
    assert args.output == "mi_salida.csv"
    assert args.report == "reporte.json"


def test_cli_parse_args_valores_por_defecto() -> None:
    """Verifica los valores por defecto asignados por parse_args."""
    args = parse_args([])

    assert args.input == "data/ventas.csv"
    assert args.output == "data/ventas_limpias.csv"
    assert args.report is None


def test_cli_run_pipeline_end_to_end(tmp_path: Path) -> None:
    """Ejecuta run_pipeline sobre un archivo temporal y comprueba la salida CSV y JSON."""
    # Arrange
    input_file = tmp_path / "raw.csv"
    input_file.write_text(
        "fecha,region,producto,unidades,precio_unitario,cliente_id\n"
        "2026-01-01,Norte,Sensor A,2,10.0,C01\n"
        "2026-01-02,Sur,Hub IoT,0,85.0,C02\n"  # Inválido (unidades 0)
        "2026-01-03,Norte,Gateway,1,100.0,C03\n",
        encoding="utf-8",
    )
    output_file = tmp_path / "clean.csv"
    report_file = tmp_path / "quality.json"

    # Act
    res = run_pipeline(input_file, output_file, report_file)

    # Assert en resultados en memoria
    assert res["filas_totales"] == 3
    assert res["filas_validas"] == 2
    assert res["filas_invalidas"] == 1
    assert res["importe_total"] == 120.0

    # Assert en fichero CSV limpio generado
    assert output_file.exists()
    clean_df = pd.read_csv(output_file)
    assert len(clean_df) == 2
    assert "importe" in clean_df.columns
    assert list(clean_df["importe"]) == [20.0, 100.0]

    # Assert en fichero JSON generado
    assert report_file.exists()
    quality = json.loads(report_file.read_text(encoding="utf-8"))
    assert quality["filas_totales"] == 3
    assert quality["filas_validas"] == 2
    assert quality["filas_invalidas"] == 1


def test_cli_main_ejecucion_exitosa(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Smoke test: comprueba que main() complete con código 0 e imprima métricas en stdout."""
    input_file = tmp_path / "input.csv"
    input_file.write_text(
        "fecha,region,producto,unidades,precio_unitario,cliente_id\n"
        "2026-01-01,Norte,Sensor A,5,10.0,C01\n",
        encoding="utf-8",
    )
    output_file = tmp_path / "out.csv"

    exit_code = main(["--input", str(input_file), "--output", str(output_file)])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Procesamiento completado con éxito" in captured.out
    assert "Norte: 50.00 €" in captured.out
    assert output_file.exists()


def test_cli_main_fichero_inexistente_retorna_codigo_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Smoke test: comprueba que main() capture el error de dominio y devuelva código 1."""
    fake_input = tmp_path / "fichero_que_no_existe.csv"
    fake_output = tmp_path / "out.csv"

    exit_code = main(["--input", str(fake_input), "--output", str(fake_output)])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error de dominio" in captured.err
