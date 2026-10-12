"""Módulo de carga de datos para el pipeline de ventas."""
from __future__ import annotations

from pathlib import Path
import pandas as pd

from .errors import DataLoadError


class CsvSalesRepository:
    """Carga los datos de ventas desde un fichero CSV."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def load(self) -> pd.DataFrame:
        """Lee el archivo CSV y devuelve un DataFrame con los datos brutos."""
        if not self.path.exists():
            raise DataLoadError(f"No existe el fichero: {self.path}")

        if not self.path.is_file():
            raise DataLoadError(f"La ruta no corresponde a un fichero: {self.path}")

        try:
            return pd.read_csv(self.path)
        except Exception as exc:
            raise DataLoadError(f"Error al leer el fichero CSV {self.path}: {exc}") from exc


# Alias para mayor legibilidad
SalesLoader = CsvSalesRepository


def load_csv(path: Path | str) -> pd.DataFrame:
    """Función de utilidad para cargar el CSV directamente."""
    return CsvSalesRepository(path).load()