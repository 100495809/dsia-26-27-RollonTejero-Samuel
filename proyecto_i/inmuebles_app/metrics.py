"""Módulo de cálculo de métricas de negocio para el pipeline inmobiliario."""
import pandas as pd


class InmueblesMetrics:
    """Calcula métricas agregadas sobre las ofertas inmobiliarias válidas usando pandas."""

    def precio_medio_por_ciudad(self, df: pd.DataFrame) -> dict[str, float]:
        """Calcula el precio medio agrupado por ciudad."""
        if df.empty or "ciudad" not in df.columns or "precio" not in df.columns:
            return {}
        return df.groupby("ciudad")["precio"].mean().round(2).to_dict()

    def precio_m2_por_ciudad(self, df: pd.DataFrame) -> dict[str, float]:
        """Calcula el precio medio por metro cuadrado agrupado por ciudad."""
        if df.empty or "ciudad" not in df.columns or "precio_m2" not in df.columns:
            return {}
        return df.groupby("ciudad")["precio_m2"].mean().round(2).to_dict()

    def precio_por_habitaciones(self, df: pd.DataFrame) -> dict[int, float]:
        """Calcula el precio medio de los inmuebles según el número de habitaciones."""
        if df.empty or "habitaciones" not in df.columns or "precio" not in df.columns:
            return {}
        return df.groupby("habitaciones")["precio"].mean().round(2).to_dict()

    def summary(self, valid_df: pd.DataFrame, total_raw: int) -> dict:
        """Genera el resumen de calidad y volumen del proceso inmobiliario."""
        valid_count = len(valid_df)
        precio_medio = round(float(valid_df["precio"].mean()), 2) if not valid_df.empty else 0.0
        precio_m2_medio = round(float(valid_df["precio_m2"].mean()), 2) if not valid_df.empty else 0.0

        return {
            "filas_totales": int(total_raw),
            "filas_validas": int(valid_count),
            "filas_invalidas": int(total_raw - valid_count),
            "precio_medio_global": precio_medio,
            "precio_m2_medio_global": precio_m2_medio,
        }
