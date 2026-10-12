"""Tests unitarios para el módulo loader de ventas_app."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from ventas_app.errors import DataLoadError
from ventas_app.loader import CsvSalesRepository, load_csv


def test_load_csv_existente_retorna_dataframe(tmp_path: Path) -> None:
    """AAA: Carga correcta de un CSV válido utilizando tmp_path."""
    # Arrange
    csv_file = tmp_path / "test_ventas.csv"
    csv_file.write_text(
        "fecha,region,producto,unidades,precio_unitario,cliente_id\n"
        "2026-01-01,Norte,Sensor A,2,10.5,C01\n"
        "2026-01-02,Sur,Hub IoT,1,85.0,C02\n",
        encoding="utf-8",
    )
    repo = CsvSalesRepository(csv_file)

    # Act
    df = repo.load()

    # Assert
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["fecha", "region", "producto", "unidades", "precio_unitario", "cliente_id"]


def test_load_path_inexistente_raises_dataloaderror(tmp_path: Path) -> None:
    """Verifica que intentar cargar un fichero que no existe lance DataLoadError."""
    # Arrange
    non_existent = tmp_path / "archivo_fantasma.csv"
    repo = CsvSalesRepository(non_existent)

    # Act & Assert
    with pytest.raises(DataLoadError) as exc_info:
        repo.load()

    assert "No existe el fichero" in str(exc_info.value)


def test_load_directorio_en_vez_de_fichero_raises_dataloaderror(tmp_path: Path) -> None:
    """Verifica que pasar un directorio en vez de un fichero lance DataLoadError."""
    # Arrange
    repo = CsvSalesRepository(tmp_path)

    # Act & Assert
    with pytest.raises(DataLoadError) as exc_info:
        repo.load()

    assert "no corresponde a un fichero" in str(exc_info.value)


def test_load_csv_funcion_utilidad(tmp_path: Path) -> None:
    """Verifica que la función helper load_csv cargue correctamente."""
    # Arrange
    csv_file = tmp_path / "helper.csv"
    csv_file.write_text("unidades,precio_unitario\n5,20.0\n", encoding="utf-8")

    # Act
    df = load_csv(csv_file)

    # Assert
    assert len(df) == 1
    assert df.iloc[0]["unidades"] == 5
