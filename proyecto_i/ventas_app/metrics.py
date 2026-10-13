"""Módulo de cálculo de métricas para el pipeline de ventas."""
import pandas as pd


class SalesMetrics:
    """Calcula métricas de negocio agregadas sobre el DataFrame de ventas válidas."""

    def total_by_region(self, df: pd.DataFrame) -> dict[str, float]:
        """Calcula el importe total acumulado por región, ordenado de mayor a menor."""
        if df.empty or "region" not in df.columns or "importe" not in df.columns:
            return {}
        return (
            df.groupby("region")["importe"]
            .sum()
            .sort_values(ascending=False)
            .round(2)
            .to_dict()
        )

    def top_products(self, df: pd.DataFrame, n: int = 3) -> dict[str, float]:
        """Calcula los N productos con mayor importe de ventas."""
        if df.empty or "producto" not in df.columns or "importe" not in df.columns:
            return {}
        return (
            df.groupby("producto")["importe"]
            .sum()
            .nlargest(n)
            .round(2)
            .to_dict()
        )

    def total_amount(self, df: pd.DataFrame) -> float:
        """Calcula la facturación total de los datos válidos."""
        if df.empty or "importe" not in df.columns:
            return 0.0
        return round(float(df["importe"].sum()), 2)

    def summary(self, valid_df: pd.DataFrame, total_raw: int) -> dict:
        """Genera el diccionario resumen con los indicadores de calidad."""
        valid_count = len(valid_df)
        return {
            "filas_totales": int(total_raw),
            "filas_validas": int(valid_count),
            "filas_invalidas": int(total_raw - valid_count),
            "importe_total": self.total_amount(valid_df),
        }