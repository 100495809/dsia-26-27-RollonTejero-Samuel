"""Tests unitarios para el loader de inmuebles."""
from pathlib import Path
import pandas as pd
import pytest

from inmuebles_app.errors import InmuebleLoadError
from inmuebles_app.loader import InmueblesLoader


def test_load_csv_exitoso(tmp_path: Path) -> None:
    """AAA: Carga correcta de un CSV válido utilizando tmp_path."""
    csv_file = tmp_path / "inmuebles.csv"
    csv_file.write_text("CITY,PRICE,CONSTRUCTEDAREA\nMadrid,200000,70\n", encoding="utf-8")

    loader = InmueblesLoader(csv_file)
    df = loader.load()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert "CITY" in df.columns


def test_load_csv_inexistente_lanza_error(tmp_path: Path) -> None:
    """Verifica que intentar cargar un fichero inexistente lance InmuebleLoadError."""
    loader = InmueblesLoader(tmp_path / "no_existe.csv")

    with pytest.raises(InmuebleLoadError):
        loader.load()
