"""Módulo de carga de datos para el pipeline de ventas."""
from pathlib import Path
import pandas as pd

from .errors import DataLoadError


class SalesLoader:
    """Carga los datos de ventas desde un fichero CSV."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def load(self) -> pd.DataFrame:
        """Lee el archivo CSV y devuelve un DataFrame de pandas."""
        if not self.path.exists():
            raise DataLoadError(f"No existe el fichero: {self.path}")

        if not self.path.is_file():
            raise DataLoadError(f"La ruta no corresponde a un fichero: {self.path}")

        try:
            return pd.read_csv(self.path)
        except Exception as exc:
            raise DataLoadError(f"Error al leer el fichero CSV: {exc}") from exc