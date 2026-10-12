"""Paquete ventas_app para el procesamiento de datos de ventas."""
from .errors import DataLoadError, SalesDomainError, ValidationError
from .loader import CsvSalesRepository, SalesLoader, load_csv
from .metrics import SalesMetrics
from .validator import SalesRecord, SalesValidator, validar_ventas

__all__ = [
    "SalesDomainError",
    "DataLoadError",
    "ValidationError",
    "CsvSalesRepository",
    "SalesLoader",
    "load_csv",
    "SalesRecord",
    "SalesValidator",
    "validar_ventas",
    "SalesMetrics",
]
