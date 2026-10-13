"""Smoke tests para el CLI de inmuebles."""
from pathlib import Path
from inmuebles_app.cli import main, parse_args


def test_cli_smoke_ejecucion(tmp_path: Path) -> None:
    """Smoke test del punto de entrada: genera salida limpia y reporte JSON."""
    in_file = tmp_path / "in.csv"
    in_file.write_text("CITY,PRICE,CONSTRUCTEDAREA,ROOMNUMBER,BATHNUMBER\nMadrid,200000,70,2,1\n", encoding="utf-8")
    out_file = tmp_path / "out.csv"
    rep_file = tmp_path / "report.json"

    assert parse_args([]).input == "data/inmuebles_sample.csv"
    code = main(["--input", str(in_file), "--output", str(out_file), "--report", str(rep_file)])

    assert code == 0
    assert out_file.exists()
    assert rep_file.exists()


def test_cli_error_fichero_inexistente(tmp_path: Path) -> None:
    """Verifica que el CLI devuelva código 1 si el fichero de entrada no existe."""
    code = main(["--input", str(tmp_path / "fantasma.csv"), "--output", str(tmp_path / "out.csv")])
    assert code == 1
