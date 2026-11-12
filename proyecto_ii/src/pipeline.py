"""Pipeline de inferencia integrada para tasación y explicación con IA"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import sys

# Asegurar que la raiz del proyecto se encuentra en sys path para ejecucion directa
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from config.settings import settings
from src.clients.ai_client import AIClient, AIResponse
from src.clients.osm_client import NominatimClient
from src.models.predictor import HousePricePredictor

logger = logging.getLogger("pipeline")


def setup_logging() -> logging.Logger:
    """Configura el sistema de logs para el pipeline de inferencia"""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    return logging.getLogger("pipeline")


class ValuationPipeline:
    """Orquestador integral que une geocodificacion, prediccion sklearn y explicacion con IA"""

    def __init__(self, osm_client=None, predictor=None, ai_client=None):
        # Asignar cliente de OpenStreetMap
        if osm_client is not None:
            self.osm_client = osm_client
        else:
            self.osm_client = NominatimClient()

        # Asignar modelo de prediccion de precios
        if predictor is not None:
            self.predictor = predictor
        else:
            self.predictor = HousePricePredictor()

        # Asignar cliente de IA
        if ai_client is not None:
            self.ai_client = ai_client
        else:
            self.ai_client = AIClient()

    def _build_ai_prompt(self, property_data: dict, location: dict, price: float) -> str:
        """Construye un prompt claro y estructurado para el modelo"""
        area = property_data.get("CONSTRUCTEDAREA", 0)
        rooms = property_data.get("ROOMNUMBER", 0)
        baths = property_data.get("BATHNUMBER", 0)

        # Comprobar si dispone de ascensor
        lift_val = property_data.get("HASLIFT", 0)
        if lift_val == 1:
            tiene_ascensor = "Si"
        else:
            tiene_ascensor = "No"

        # Extraer datos de ubicacion
        district = location.get("district", "Desconocido")
        neighborhood = location.get("neighborhood", "Desconocido")
        postcode = location.get("postcode", "Desconocido")

        prompt = (
            "Actua como un perito tasador inmobiliario experto en Madrid. "
            "Redacta un informe formal y sintetico de valoracion comercial para la siguiente propiedad:\n"
            f"- Ubicacion: Distrito {district}, Barrio {neighborhood} (CP {postcode})\n"
            f"- Superficie: {area} m2 construidos\n"
            f"- Distribucion: {rooms} habitaciones y {baths} baños\n"
            f"- Ascensor: {tiene_ascensor}\n"
            f"- Valor de mercado estimado por modelo de regresion: {price:,.2f} EUR\n\n"
            "Justifica la coherencia del precio en funcion del distrito y resalta brevemente los puntos fuertes, en no más de 100 palabras."
        )
        return prompt

    def evaluate_property(self, property_data: dict) -> dict:
        """Ejecuta el flujo completo de tasación: geografia -> sklearn -> informe IA"""

        log = logging.getLogger("pipeline")
        log.info("Iniciando proceso de tasación integral del inmueble")

        # Enriquecimiento geográfico mediante coordenadas si están presentes
        lat = property_data.get("LATITUDE")
        lon = property_data.get("LONGITUDE")

        if lat is not None and lon is not None:
            log.info("Coordenadas detectadas (%.4f, %.4f), consultando cache de OSM...", lat, lon)
            location = self.osm_client.reverse_geocode(float(lat), float(lon))
        else:
            # Si no hay coordenadas, comprobar si se pasó el distrito por parametro
            log.warning("No se proporcionaron coordenadas, se usará distrito si está disponible")
            if "district" in property_data:
                distrito_usuario = property_data["district"]
            else:
                distrito_usuario = "Desconocido"

            location = {
                "district": distrito_usuario,
                "neighborhood": "Desconocido",
                "postcode": "Desconocido",
            }

        # Asegurar que el distrito obtenido se incorpore a los datos del piso
        property_copy = {}
        for clave, valor in property_data.items():
            property_copy[clave] = valor

        property_copy["district"] = location["district"]

        # Prediccion del precio con el modelo Scikit-Learn
        log.info("Calculando precio de mercado con el modelo Scikit-Learn...")
        predicted_price = self.predictor.predict_price(property_copy)
        log.info("Precio estimado: %.2f EUR", predicted_price)

        # Redaccion del informe cualitativo con el servicio de IA
        log.info("Generando informe explicativo de tasacion con IA...")
        prompt = self._build_ai_prompt(property_copy, location, predicted_price)
        ai_response = self.ai_client.complete(prompt)

        # Devolver el resultado consolidado
        resultado = {
            "property": property_copy,
            "location": location,
            "predicted_price": predicted_price,
            "valuation_report": ai_response.text,
            "ai_provider": ai_response.provider,
        }

        log.info("Proceso de tasacion completado exitosamente")
        return resultado


if __name__ == "__main__":

    setup_logging()

    parser = argparse.ArgumentParser(description="Pipeline integral de tasacion inmobiliaria en Madrid")
    parser.add_argument("--area", type=float, default=85.0, help="Superficie construida en m2")
    parser.add_argument("--rooms", type=int, default=2, help="Numero de habitaciones")
    parser.add_argument("--baths", type=int, default=1, help="Numero de baños")
    parser.add_argument("--lat", type=float, default=40.4224, help="Latitud")
    parser.add_argument("--lon", type=float, default=-3.7107, help="Longitud")
    parser.add_argument("--lift", type=int, default=1, help="Tiene ascensor (1 o 0)")
    parser.add_argument("--mock-ai", action="store_true", help="Forzar respuesta simulada de IA")
    args = parser.parse_args()

    # Si se pasa el flag mock-ai se crea cliente en modo mock
    if args.mock_ai:
        ai_cli = AIClient(mock_mode=True)
    else:
        ai_cli = None

    pipeline_service = ValuationPipeline(ai_client=ai_cli)

    datos_inmueble = {
        "CONSTRUCTEDAREA": args.area,
        "ROOMNUMBER": args.rooms,
        "BATHNUMBER": args.baths,
        "LATITUDE": args.lat,
        "LONGITUDE": args.lon,
        "HASLIFT": args.lift,
    }

    resultado_final = pipeline_service.evaluate_property(datos_inmueble)
    print("\n" + "=" * 60)
    print("RESULTADO DE LA TASACION")
    print("=" * 60)
    print(f"Inmueble: {datos_inmueble['CONSTRUCTEDAREA']} m2 | {datos_inmueble['ROOMNUMBER']} habs | {datos_inmueble['BATHNUMBER']} baños | Ascensor: {datos_inmueble['HASLIFT']}")
    print(f"Distrito: {resultado_final['location']['district']} (Barrio: {resultado_final['location']['neighborhood']})")
    print(f"Precio estimado: {resultado_final['predicted_price']:,.2f} EUR")
    print(f"Proveedor de IA: {resultado_final['ai_provider']}")
    print("-" * 60)
    print(resultado_final["valuation_report"])
    print("=" * 60 + "\n")
