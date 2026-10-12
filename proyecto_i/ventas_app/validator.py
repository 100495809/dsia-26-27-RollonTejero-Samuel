"""Módulo de validación de registros y reglas de calidad para ventas."""
from __future__ import annotations

from dataclasses import dataclass
import pandas as pd

from .errors import ValidationError


@dataclass(frozen=True)
class SalesRecord:
    """Representa una fila de venta válida del dataset."""

    fecha: str = ""
    region: str = ""
    producto: str = ""
    unidades: float = 0.0
    precio_unitario: float = 0.0
    cliente_id: str = ""

    @property
    def importe(self) -> float:
        """Calcula el importe total de la venta (unidades * precio_unitario)."""
        return round(self.unidades * self.precio_unitario, 4)


class SalesValidator:
    """Valida las reglas de negocio sobre los datos de ventas."""

    def split(
        self,
        frame: pd.DataFrame,
    ) -> tuple[list[SalesRecord], pd.DataFrame]:
        """Separa el DataFrame en una lista de SalesRecord válidos y un DataFrame de inválidos."""
        if not isinstance(frame, pd.DataFrame):
            raise ValidationError(f"Se esperaba un DataFrame de pandas, se recibió: {type(frame)}")

        if frame.empty:
            return [], frame.copy()

        if "unidades" not in frame.columns or "precio_unitario" not in frame.columns:
            raise ValidationError("El DataFrame debe contener las columnas 'unidades' y 'precio_unitario'.")

        work = frame.copy()
        work["unidades"] = pd.to_numeric(work["unidades"], errors="coerce")
        work["precio_unitario"] = pd.to_numeric(work["precio_unitario"], errors="coerce")

        ok = (
            work["unidades"].notna()
            & (work["unidades"] > 0)
            & work["precio_unitario"].notna()
            & (work["precio_unitario"] > 0)
        )

        valid_df = work.loc[ok]
        invalid_df = work.loc[~ok].copy()

        valid_records = [
            SalesRecord(
                fecha=str(getattr(row, "fecha", "")),
                region=str(getattr(row, "region", "")),
                producto=str(getattr(row, "producto", "")),
                unidades=float(row.unidades),
                precio_unitario=float(row.precio_unitario),
                cliente_id=str(getattr(row, "cliente_id", "")),
            )
            for row in valid_df.itertuples(index=False)
        ]

        return valid_records, invalid_df


def validar_ventas(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Función de validación vista en clase: devuelve tupla (validos, errores)."""
    if not isinstance(frame, pd.DataFrame):
        raise ValidationError(f"Se esperaba un DataFrame, se recibió: {type(frame)}")

    if frame.empty:
        empty_valid = frame.copy()
        if "unidades" in empty_valid.columns and "precio_unitario" in empty_valid.columns:
            empty_valid["importe"] = pd.Series(dtype=float)
        return empty_valid, frame.copy()

    work = frame.copy()
    work["unidades"] = pd.to_numeric(work["unidades"], errors="coerce")
    work["precio_unitario"] = pd.to_numeric(work["precio_unitario"], errors="coerce")

    ok = (
        work["unidades"].notna()
        & (work["unidades"] > 0)
        & work["precio_unitario"].notna()
        & (work["precio_unitario"] > 0)
    )

    validos = work.loc[ok].copy()
    errores = work.loc[~ok].copy()
    validos["importe"] = (validos["unidades"] * validos["precio_unitario"]).round(4)

    return validos, errores