"""Configuración global y fixtures compartidas para la suite de tests."""
from pathlib import Path
import pandas as pd
import pytest


@pytest.fixture
def ventas_mini() -> pd.DataFrame:
    """Fixture con 3 filas: 1 válida y 2 inválidas."""
    return pd.DataFrame({
        "fecha": ["2026-01-01", "2026-01-02", "2026-01-03"],
        "region": ["Norte", "Sur", "Norte"],
        "producto": ["A", "B", "A"],
        "unidades": [2, None, 5],
        "precio_unitario": [10.0, 20.0, -1.0],
        "cliente_id": ["C1", "C2", "C1"],
    })


@pytest.fixture
def sample_ventas_df() -> pd.DataFrame:
    """Fixture con ventas válidas calculadas en memoria para métricas."""
    return pd.DataFrame({
        "fecha": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
        "region": ["Norte", "Sur", "Norte", "Este"],
        "producto": ["Sensor A", "Hub IoT", "Sensor A", "Gateway"],
        "unidades": [2.0, 1.0, 3.0, 4.0],
        "precio_unitario": [10.0, 50.0, 10.0, 100.0],
        "cliente_id": ["C01", "C02", "C01", "C03"],
        "importe": [20.0, 50.0, 30.0, 400.0],
    })


@pytest.fixture
def ventas_csv_path() -> Path:
    """Ruta al dataset ventas.csv del curso."""
    p = Path(__file__).resolve().parent.parent / "data" / "ventas.csv"
    if p.exists():
        return p
    return Path(__file__).resolve().parent.parent.parent / "ejercicios" / "data" / "ventas.csv"


@pytest.fixture
def inmuebles_mini() -> pd.DataFrame:
    """Fixture con 4 inmuebles: 1 válido y 3 inválidos."""
    return pd.DataFrame({
        "ASSETID": ["A1", "A2", "A3", "A4"],
        "CITY": ["Madrid", "Barcelona", "Valencia", "Sevilla"],
        "PRICE": [200000.0, 5000.0, 150000.0, 300000.0],
        "CONSTRUCTEDAREA": [80.0, 50.0, 10.0, 90.0],
        "ROOMNUMBER": [3, 2, 1, 3],
        "BATHNUMBER": [2, 1, 1, 2],
    })


@pytest.fixture
def sample_inmuebles_df() -> pd.DataFrame:
    """Fixture con inmuebles válidos en memoria para métricas."""
    return pd.DataFrame({
        "ciudad": ["Madrid", "Madrid", "Barcelona", "Valencia"],
        "precio": [300000.0, 200000.0, 400000.0, 150000.0],
        "superficie": [100.0, 50.0, 80.0, 75.0],
        "habitaciones": [3, 1, 2, 2],
        "banos": [2, 1, 1, 1],
        "precio_m2": [3000.0, 4000.0, 5000.0, 2000.0],
    })


@pytest.fixture
def inmuebles_sample_path() -> Path:
    """Ruta al dataset de muestra de inmuebles."""
    return Path(__file__).resolve().parent.parent / "data" / "inmuebles_sample.csv"
