"""Módulo de carga de datos para inmuebles."""
from pathlib import Path
import pandas as pd

from .errors import InmuebleLoadError


class InmueblesLoader:
    """Carga los datos de inmuebles desde un fichero CSV."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def load(self) -> pd.DataFrame:
        """Lee el fichero CSV y devuelve un DataFrame de pandas."""
        if not self.path.exists():
            raise InmuebleLoadError(f"No existe el fichero: {self.path}")

        if not self.path.is_file():
            raise InmuebleLoadError(f"La ruta no corresponde a un fichero: {self.path}")

        try:
            return pd.read_csv(self.path)
        except Exception as exc:
            raise InmuebleLoadError(f"Error al leer el fichero CSV: {exc}") from exc
