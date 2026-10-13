"""Módulo de excepciones de dominio para el pipeline inmobiliario."""
from __future__ import annotations


class InmueblesDomainError(Exception):
    """Excepción base para todos los errores del pipeline de inmuebles."""


class InmuebleLoadError(InmueblesDomainError):
    """Error al cargar el fichero CSV de inmuebles."""


class InmuebleValidationError(InmueblesDomainError):
    """Error cuando los datos no cumplen con el formato o reglas esperadas."""

