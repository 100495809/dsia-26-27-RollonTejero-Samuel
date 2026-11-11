"""Pruebas unitarias para el módulo de preprocesamiento y limpieza de datos"""
from pathlib import Path
import pandas as pd
import pytest

from src.clients.osm_client import NominatimClient
from src.data.preprocessor import (
    REQUIRED_COLUMNS,
    load_raw_data,
    enrich_with_geodata,
    clean_and_transform,
    save_processed_data,
)


@pytest.fixture
def sample_raw_dataframe() -> pd.DataFrame:
    """Genera un DataFrame sintetico representativo del dataset de Idealista"""
    return pd.DataFrame(
        {
            "PRICE": [250000.0, 450000.0, -100.0, 150000.0, 9000000.0],
            "CONSTRUCTEDAREA": [65.0, 110.0, 50.0, 4.0, 150.0],
            "ROOMNUMBER": [2, 3, 1, 1, 4],
            "BATHNUMBER": [1, 2, 1, 1, 3],
            "LATITUDE": [40.4224, 40.4512, 40.4224, 40.4224, 40.4224],
            "LONGITUDE": [-3.7107, -3.6899, -3.7107, -3.7107, -3.7107],
            "HASLIFT": [1, 1, 0, 0, 1],
            "HASAIRCONDITIONING": [1, 0, 0, 1, 1],
        }
    )


def test_load_raw_data_missing_column(tmp_path: Path):
    """Comprueba que se eleva ValueError si falta alguna columna requerida"""
    bad_csv = tmp_path / "incompleto.csv"
    pd.DataFrame({"PRICE": [100000], "CONSTRUCTEDAREA": [50]}).to_csv(bad_csv, index=False)

    with pytest.raises(ValueError, match="Faltan columnas obligatorias"):
        load_raw_data(file_path=bad_csv)


def test_enrich_with_geodata_mapping(sample_raw_dataframe: pd.DataFrame, tmp_path: Path):
    """Verifica que el enriquecimiento añade distrito, barrio y codigo postal"""
    client = NominatimClient(cache_path=tmp_path / "geo_cache.json", mock_mode=True)
    enriched = enrich_with_geodata(sample_raw_dataframe, osm_client=client)

    assert "district" in enriched.columns
    assert "neighborhood" in enriched.columns
    assert "postcode" in enriched.columns
    assert "geo_key" in enriched.columns

    # En modo mock debe asignar el distrito por defecto Centro
    assert enriched["district"].iloc[0] == "Centro"
    assert enriched["neighborhood"].iloc[0] == "Sol"


def test_clean_and_transform_filters_invalid_rows(sample_raw_dataframe: pd.DataFrame):
    """Comprueba el filtrado de valores atipicos y la estructura del reporte"""
    clean_df, report = clean_and_transform(sample_raw_dataframe)

    # Filas descartadas esperadas: precio negativo (-100), area inviable (4m), precio excesivo (9M)
    assert report["rows_in"] == 5
    assert report["rows_out"] == 2
    assert report["rows_dropped"] == 3
    assert report["error_rate"] == 0.6
    assert report["avg_price"] == 350000.0

    # Los precios de las filas limpias deben estar en el rango valido
    assert all(clean_df["PRICE"] >= 30000)
    assert all(clean_df["PRICE"] <= 5000000)


def test_save_processed_data_creates_files(sample_raw_dataframe: pd.DataFrame, tmp_path: Path):
    """Verifica la persistencia de datos limpios diferenciando mock y produccion"""
    clean_df, report = clean_and_transform(sample_raw_dataframe)

    # Caso 1: Ejecucion real sin mock
    csv_real, json_real = save_processed_data(clean_df, report, tmp_path, is_mock=False)
    assert csv_real.exists()
    assert json_real.exists()
    assert csv_real.name == "madrid_limpio.csv"
    assert json_real.name == "data_quality_report.json"

    # Caso 2: Ejecucion simulada con mock
    csv_mock, json_mock = save_processed_data(clean_df, report, tmp_path, is_mock=True)
    assert csv_mock.exists()
    assert json_mock.exists()
    assert csv_mock.name == "madrid_mock_limpio.csv"
    assert json_mock.name == "data_quality_report_mock.json"
