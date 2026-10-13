"""Módulo de validación de datos para el pipeline de ventas."""
import pandas as pd

from .errors import ValidationError


class SalesValidator:
    """Valida las reglas de negocio sobre los datos de ventas usando pandas."""

    def split(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Separa el DataFrame en válidos e inválidos y calcula la columna importe."""
        if not isinstance(df, pd.DataFrame):
            raise ValidationError(f"Se esperaba un DataFrame, pero se recibió: {type(df)}")

        if "unidades" not in df.columns or "precio_unitario" not in df.columns:
            raise ValidationError("El DataFrame debe contener las columnas 'unidades' y 'precio_unitario'")

        work = df.copy()
        work["unidades"] = pd.to_numeric(work["unidades"], errors="coerce")
        work["precio_unitario"] = pd.to_numeric(work["precio_unitario"], errors="coerce")

        ok = (
            work["unidades"].notna()
            & (work["unidades"] > 0)
            & work["precio_unitario"].notna()
            & (work["precio_unitario"] > 0)
        )

        validos = work.loc[ok].copy()
        invalidos = work.loc[~ok].copy()

        validos["importe"] = (validos["unidades"] * validos["precio_unitario"]).round(2)
        return validos, invalidos