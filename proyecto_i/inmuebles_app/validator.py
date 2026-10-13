"""Módulo de validación de registros y reglas de calidad para inmuebles."""
import pandas as pd

from .errors import InmuebleValidationError


class InmueblesValidator:
    """Valida las reglas de negocio sobre el dataset de inmuebles usando pandas."""

    CIUDADES_VALIDAS = {"madrid", "barcelona", "valencia"}

    def split(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Separa el DataFrame en válidos e inválidos y calcula la columna precio_m2."""
        if not isinstance(df, pd.DataFrame):
            raise InmuebleValidationError(f"Se esperaba un DataFrame, pero se recibió: {type(df)}")

        columnas_requeridas = ["PRICE", "CONSTRUCTEDAREA", "ROOMNUMBER", "BATHNUMBER", "CITY"]
        for col in columnas_requeridas:
            if col not in df.columns:
                raise InmuebleValidationError(f"Falta la columna obligatoria: {col}")

        work = df.copy()
        work["precio"] = pd.to_numeric(work["PRICE"], errors="coerce")
        work["superficie"] = pd.to_numeric(work["CONSTRUCTEDAREA"], errors="coerce")
        work["habitaciones"] = pd.to_numeric(work["ROOMNUMBER"], errors="coerce")
        work["banos"] = pd.to_numeric(work["BATHNUMBER"], errors="coerce")
        work["ciudad"] = work["CITY"].astype(str).str.strip().str.capitalize()

        id_valido = ~work["ASSETID"].duplicated() if "ASSETID" in work.columns else True

        ok = (
            id_valido
            & (work["precio"] > 10000)
            & (work["superficie"] >= 15)
            & (work["habitaciones"] >= 0)
            & (work["banos"] >= 1)
            & work["ciudad"].str.lower().isin(self.CIUDADES_VALIDAS)
        )

        validos = work.loc[ok].copy()
        invalidos = work.loc[~ok].copy()

        validos["precio_m2"] = (validos["precio"] / validos["superficie"]).round(2)
        return validos, invalidos
