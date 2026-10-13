"""Tests unitarios para las métricas de ventas."""
import pandas as pd

from ventas_app.metrics import SalesMetrics


def test_metrics_agregaciones_conocidas(sample_ventas_df: pd.DataFrame) -> None:
    """AAA: Agregación por región y top productos con resultado conocido."""
    metrics = SalesMetrics()

    por_region = metrics.total_by_region(sample_ventas_df)
    top_prod = metrics.top_products(sample_ventas_df, n=2)

    assert por_region["Este"] == 400.0
    assert por_region["Norte"] == 50.0
    assert len(top_prod) == 2
    assert "Gateway" in top_prod


def test_metrics_summary(sample_ventas_df: pd.DataFrame) -> None:
    """Verifica el cálculo del resumen de calidad y facturación total."""
    metrics = SalesMetrics()
    resumen = metrics.summary(sample_ventas_df, total_raw=6)

    assert resumen["filas_totales"] == 6
    assert resumen["filas_validas"] == 4
    assert resumen["filas_invalidas"] == 2
    assert resumen["importe_total"] == 500.0
