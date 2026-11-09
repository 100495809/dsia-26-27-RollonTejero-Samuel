"""Configuración del proyecto mediante variables de entorno"""
from pathlib import Path
from typing import Optional
import os
from dotenv import load_dotenv

# Cargar archivo .env local si existe
_base_dir = Path(__file__).resolve().parent.parent
load_dotenv(_base_dir / ".env")


class Settings:
    # Entorno general
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Rutas base del proyecto
    BASE_DIR: Path = _base_dir
    DATA_PATH: Path = Path(os.getenv("DATA_PATH", "data/madrid.csv"))
    GEO_CACHE_PATH: Path = Path(os.getenv("GEO_CACHE_PATH", "data/geo_cache.json"))
    MODEL_PATH: Path = Path(os.getenv("MODEL_PATH", "models/house_pricing_model.joblib"))
    METRICS_PATH: Path = Path(os.getenv("METRICS_PATH", "models/metrics.json"))

    # Configuración de Nominatim para OpenStreetMap
    NOMINATIM_USER_AGENT: str = os.getenv("NOMINATIM_USER_AGENT", "dsia_madrid_real_estate_valuation_v1")
    NOMINATIM_RATE_LIMIT_DELAY: float = float(os.getenv("NOMINATIM_RATE_LIMIT_DELAY", "1.0"))
    NOMINATIM_MOCK: bool = os.getenv("NOMINATIM_MOCK", "false").lower() in ("true", "1", "yes")

    # Token oficial de Hugging Face requerido por rúbrica
    HF_TOKEN: Optional[str] = os.getenv("HF_TOKEN")

    # Configuración del servicio LLM remoto vía Tailscale o servidor compatible
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:8000")
    LLM_MODEL_ID: Optional[str] = os.getenv("LLM_MODEL_ID")
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY")

    # Modo mock para pruebas y CI sin requerir conexión externa
    LLM_MOCK: bool = os.getenv("LLM_MOCK", "true").lower() in ("true", "1", "yes")

    def get_absolute_path(self, relative_or_abs_path: Path | str) -> Path:
        """Devuelve la ruta absoluta referenciada a la raíz del proyecto"""
        p = Path(relative_or_abs_path)
        return p if p.is_absolute() else self.BASE_DIR / p


settings = Settings()
