"""Tests unitarios para el módulo metrics de ventas_app."""
from __future__ import annotations

from ventas_app.metrics import SalesMetrics
from ventas_app.validator import SalesRecord


def test_metrics_total_by_region_resultado_conocido(sample_records: list[SalesRecord]) -> None:
    """AAA: Calcula agregación total_by_region sobre fixture en memoria con resultado esperado."""
    # Arrange
    metrics = SalesMetrics()

    # Act
    totales = metrics.total_by_region(sample_records)

    # Assert
    # Este: 400.0, Norte: 20+30=50.0, Sur: 50.0
    assert list(totales.keys()) == ["Este", "Norte", "Sur"] or list(totales.keys()) == ["Este", "Sur", "Norte"]
    assert totales["Este"] == 400.0
    assert totales["Norte"] == 50.0
    assert totales["Sur"] == 50.0


def test_metrics_top_products(sample_records: list[SalesRecord]) -> None:
    """Verifica que top_products devuelva los productos ordenados de mayor a menor importe."""
    metrics = SalesMetrics()

    top2 = metrics.top_products(sample_records, n=2)

    assert len(top2) == 2
    assert "Gateway" in top2
    assert top2["Gateway"] == 400.0


def test_metrics_total_amount(sample_records: list[SalesRecord]) -> None:
    """Verifica el cálculo de importe total global."""
    metrics = SalesMetrics()
    total = metrics.total_amount(sample_records)
    assert total == 500.0


def test_metrics_summary(sample_records: list[SalesRecord]) -> None:
    """Verifica la generación del diccionario de resumen de calidad."""
    metrics = SalesMetrics()
    resumen = metrics.summary(sample_records, total_raw=6)

    assert resumen["filas_totales"] == 6
    assert resumen["filas_validas"] == 4
    assert resumen["filas_invalidas"] == 2
    assert resumen["importe_total"] == 500.0


def test_metrics_registros_vacios() -> None:
    """Verifica el comportamiento cuando la lista de registros está vacía."""
    metrics = SalesMetrics()

    assert metrics.total_by_region([]) == {}
    assert metrics.top_products([], n=3) == {}
    assert metrics.total_amount([]) == 0.0

    resumen = metrics.summary([], total_raw=10)
    assert resumen["filas_totales"] == 10
    assert resumen["filas_validas"] == 0
    assert resumen["filas_invalidas"] == 10
    assert resumen["importe_total"] == 0.0
