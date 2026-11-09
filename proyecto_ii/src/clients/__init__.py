"""Clientes para servicios externos como geocodificación y modelos de lenguaje"""
from src.clients.osm_client import NominatimClient, format_geo_key

__all__ = ["NominatimClient", "format_geo_key"]
