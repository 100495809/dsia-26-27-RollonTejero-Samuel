"""Pruebas unitarias para el punto de entrada unificado main.py"""
import sys
from pathlib import Path

from main import main


def test_main_no_command_shows_help(monkeypatch, capsys):
    """Comprueba que ejecutar main sin argumentos muestra el mensaje de ayuda"""
    monkeypatch.setattr(sys, "argv", ["main.py"])
    main()

    captured = capsys.readouterr()
    assert "Comandos disponibles" in captured.out or "usage:" in captured.out


def test_main_evaluate_mock(monkeypatch, capsys):
    """Comprueba que el subcomando evaluate ejecuta la tasacion en modo mock"""
    monkeypatch.setattr(sys, "argv", ["main.py", "evaluate", "--mock-ai"])
    main()

    captured = capsys.readouterr()
    assert "RESULTADO DE LA TASACION" in captured.out
    assert "Proveedor de IA: mock" in captured.out


def test_main_preprocess_sample(monkeypatch, tmp_path):
    """Comprueba que el subcomando preprocess genera los archivos de salida simulados"""
    directorio_salida = str(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "preprocess", "--sample", "10", "--mock-geo", "--output-dir", directorio_salida],
    )
    main()

    archivo_csv = tmp_path / "madrid_mock_limpio.csv"
    archivo_json = tmp_path / "data_quality_report_mock.json"

    assert archivo_csv.exists()
    assert archivo_json.exists()
