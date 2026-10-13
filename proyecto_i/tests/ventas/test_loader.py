"""Tests unitarios para el loader de ventas."""
from pathlib import Path
import pandas as pd
import pytest

from ventas_app.errors import DataLoadError
from ventas_app.loader import SalesLoader


def test_load_csv_exitoso(tmp_path: Path) -> None:
    """AAA: Carga correcta de un CSV válido utilizando tmp_path."""
    csv_file = tmp_path / "ventas.csv"
    csv_file.write_text("fecha,region,unidades,precio_unitario\n2026-01-01,Norte,2,10.0\n", encoding="utf-8")

    loader = SalesLoader(csv_file)
    df = loader.load()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert "region" in df.columns


def test_load_csv_inexistente_lanza_error(tmp_path: Path) -> None:
    """Verifica que intentar cargar un fichero inexistente lance DataLoadError."""
    loader = SalesLoader(tmp_path / "no_existe.csv")

    with pytest.raises(DataLoadError):
        loader.load()
