"""Tests unitarios para las métricas de inmuebles."""
import pandas as pd

from inmuebles_app.metrics import InmueblesMetrics


def test_metrics_precio_medio_por_ciudad_y_habitaciones(sample_inmuebles_df: pd.DataFrame) -> None:
    """AAA: Agregación de precios por ciudad y por habitaciones."""
    metrics = InmueblesMetrics()

    por_ciudad = metrics.precio_medio_por_ciudad(sample_inmuebles_df)
    por_m2 = metrics.precio_m2_por_ciudad(sample_inmuebles_df)
    por_habs = metrics.precio_por_habitaciones(sample_inmuebles_df)

    assert por_ciudad["Madrid"] == 250000.0
    assert por_m2["Barcelona"] == 5000.0
    assert por_habs[1] == 200000.0


def test_metrics_summary(sample_inmuebles_df: pd.DataFrame) -> None:
    """Verifica el cálculo del resumen de calidad y precio medio global."""
    metrics = InmueblesMetrics()
    resumen = metrics.summary(sample_inmuebles_df, total_raw=6)

    assert resumen["filas_totales"] == 6
    assert resumen["filas_validas"] == 4
    assert resumen["filas_invalidas"] == 2
    assert resumen["precio_medio_global"] == 262500.0
