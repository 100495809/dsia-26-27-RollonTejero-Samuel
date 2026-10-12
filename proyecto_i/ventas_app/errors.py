"""Módulo de excepciones de dominio para el pipeline de ventas."""
from __future__ import annotations


class SalesDomainError(Exception):
    """Excepción base para todos los errores del pipeline de ventas."""


class DataLoadError(SalesDomainError):
    """Error al cargar el fichero CSV de datos."""


class ValidationError(SalesDomainError):
    """Error cuando los datos no cumplen con el formato o reglas esperadas."""
