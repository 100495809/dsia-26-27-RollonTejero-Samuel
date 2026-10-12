"""Configuración global y fixtures compartidas para la suite de tests."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from ventas_app.validator import SalesRecord


@pytest.fixture
def ventas_mini() -> pd.DataFrame:
    """Fixture estándar del curso con 3 filas: 1 válida y 2 inválidas."""
    return pd.DataFrame({
        "fecha": ["2026-01-01", "2026-01-02", "2026-01-03"],
        "region": ["Norte", "Sur", "Norte"],
        "producto": ["A", "B", "A"],
        "unidades": [2, None, 5],
        "precio_unitario": [10.0, 20.0, -1.0],
        "cliente_id": ["C1", "C2", "C1"],
    })


@pytest.fixture
def sample_records() -> list[SalesRecord]:
    """Fixture con registros SalesRecord válidos en memoria para cálculo de métricas."""
    return [
        SalesRecord(
            fecha="2026-01-01",
            region="Norte",
            producto="Sensor A",
            unidades=2.0,
            precio_unitario=10.0,
            cliente_id="C01",
        ),  # importe: 20.0
        SalesRecord(
            fecha="2026-01-02",
            region="Sur",
            producto="Hub IoT",
            unidades=1.0,
            precio_unitario=50.0,
            cliente_id="C02",
        ),  # importe: 50.0
        SalesRecord(
            fecha="2026-01-03",
            region="Norte",
            producto="Sensor A",
            unidades=3.0,
            precio_unitario=10.0,
            cliente_id="C01",
        ),  # importe: 30.0
        SalesRecord(
            fecha="2026-01-04",
            region="Este",
            producto="Gateway",
            unidades=4.0,
            precio_unitario=100.0,
            cliente_id="C03",
        ),  # importe: 400.0
    ]


@pytest.fixture
def ventas_csv_path() -> Path:
    """Ruta al dataset ventas.csv del curso."""
    primary_path = Path(__file__).resolve().parent.parent / "data" / "ventas.csv"
    if primary_path.exists():
        return primary_path

    fallback_path = Path(__file__).resolve().parent.parent.parent / "ejercicios" / "data" / "ventas.csv"
    if fallback_path.exists():
        return fallback_path

    raise FileNotFoundError(f"No se encontró ventas.csv ni en {primary_path} ni en {fallback_path}")
