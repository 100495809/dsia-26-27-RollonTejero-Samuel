"""Cliente para la API de geocodificación inversa de Nominatim OpenStreetMap"""
import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional
import requests

from config.settings import settings

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)


def format_geo_key(lat: float, lon: float) -> str:
    """Aplica  agrupación espacial redondeando coordenadas a 2 decimales y devuelve la clave"""
    return f"{round(lat, 2):.2f},{round(lon, 2):.2f}"


class NominatimClient:
    """Cliente para obtener barrio y distrito a partir de coordenadas geográficas"""

    BASE_URL = "https://nominatim.openstreetmap.org/reverse"

    def __init__(
        self,
        cache_path: Optional[Path] = None,
        user_agent: Optional[str] = None,
        delay: Optional[float] = None,
        mock_mode: Optional[bool] = None,
    ):
        # Ruta del archivo JSON para almacenar la cache geográfica en disco
        if cache_path is not None:
            self.cache_path = cache_path
        else:
            self.cache_path = settings.get_absolute_path(settings.GEO_CACHE_PATH)

        # Identificador de aplicacion requerido por los terminos de servicio de OpenStreetMap
        if user_agent is not None:
            self.user_agent = user_agent
        else:
            self.user_agent = settings.NOMINATIM_USER_AGENT

        # Retardo en segundos entre peticiones consecutivas para no saturar la API
        if delay is not None:
            self.delay = delay
        else:
            self.delay = settings.NOMINATIM_RATE_LIMIT_DELAY

        # Indicador para usar respuestas simuladas en pruebas unitarias y entornos sin red
        if mock_mode is not None:
            self.mock_mode = mock_mode
        else:
            self.mock_mode = settings.NOMINATIM_MOCK

        # Marca de tiempo de la ultima peticion HTTP realizada para calcular las esperas
        self.last_request_time = 0.0

        # Diccionario en memoria que contiene las coordenadas ya procesadas
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, dict]:
        """Carga el archivo de caché si existe o inicializa un diccionario vacío"""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info("Caché geográfica cargada con %d entradas", len(data))
                    return data
            except Exception as e:
                logger.warning("Error al leer la caché geográfica: %s", e)
                return {}
        return {}

    def _save_cache(self) -> None:
        """Guarda la caché actual en el archivo JSON"""
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
            logger.debug("Caché geográfica guardada con éxito")
        except Exception as e:
            logger.error("No se pudo guardar la caché geográfica: %s", e)

    def _apply_rate_limit(self) -> None:
        """Asegura un intervalo mínimo entre peticiones para respetar la política de OSM"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()

    def _mock_response(self, lat_bin: float, lon_bin: float) -> dict:
        """Devuelve datos geográficos simulados para pruebas y tests unitarios"""
        return {
            "district": "Centro",
            "neighborhood": "Sol",
            "postcode": "28013",
            "city": "Madrid",
        }

    def reverse_geocode(self, lat: float, lon: float) -> dict:
        """Obtiene distrito y barrio para unas coordenadas mediante agrupación y caché"""
        lat_bin = round(lat, 2)
        lon_bin = round(lon, 2)
        key = format_geo_key(lat, lon)

        # Paso 1: Comprobar si ya existe en la caché local
        if key in self.cache:
            logger.debug("Coordenada %s encontrada en caché", key)
            return self.cache[key]

        # Paso 2: Si el modo mock está activo se devuelve respuesta simulada sin alterar la caché persistente
        if self.mock_mode:
            logger.debug("Modo mock activo para la coordenada %s", key)
            return self._mock_response(lat_bin, lon_bin)

        # Paso 3: Petición real a Nominatim respetando rate limiting
        self._apply_rate_limit()

        params = {
            "lat": lat_bin,
            "lon": lon_bin,
            "format": "json",
            "addressdetails": 1,
        }
        headers = {
            "User-Agent": self.user_agent,
        }

        try:
            logger.info("Consultando Nominatim OSM para la coordenada %s", key)
            response = requests.get(
                self.BASE_URL,
                params=params,
                headers=headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            address = data.get("address", {})
            district = (
                address.get("suburb")
                or address.get("city_district")
                or address.get("district")
                or "Desconocido"
            )
            neighborhood = (
                address.get("neighbourhood")
                or address.get("quarter")
                or district
            )
            postcode = address.get("postcode", "Desconocido")
            city = address.get("city") or address.get("town") or "Madrid"

            location = {
                "district": district,
                "neighborhood": neighborhood,
                "postcode": postcode,
                "city": city,
            }

            # Guardar en memoria y persistir en disco
            self.cache[key] = location
            self._save_cache()
            return location

        except Exception as e:
            logger.error("Error al consultar Nominatim para %s: %s", key, e)
            # En caso de fallo de red devolvemos un valor seguro sin romper el flujo
            return {
                "district": "Desconocido",
                "neighborhood": "Desconocido",
                "postcode": "Desconocido",
                "city": "Madrid",
            }
