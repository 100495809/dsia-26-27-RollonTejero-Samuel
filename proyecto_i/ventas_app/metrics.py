"""Módulo de cálculo de métricas de negocio para el pipeline de ventas."""
from __future__ import annotations

from typing import Any
from .validator import SalesRecord


class SalesMetrics:
    """Calcula métricas agregadas sobre la lista de ventas válidas."""

    def total_by_region(
        self,
        records: list[SalesRecord],
    ) -> dict[str, float]:
        """Calcula el importe total acumulado por región, ordenado de mayor a menor importe."""
        totals: dict[str, float] = {}

        for record in records:
            region = record.region if record.region else "Sin Region"
            totals[region] = totals.get(region, 0.0) + record.importe

        return dict(
            sorted(
                {k: round(v, 2) for k, v in totals.items()}.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )

    def top_products(
        self,
        records: list[SalesRecord],
        n: int = 3,
    ) -> dict[str, float]:
        """Calcula los N productos con mayor importe de ventas."""
        totals: dict[str, float] = {}

        for record in records:
            producto = record.producto if record.producto else "Sin Producto"
            totals[producto] = totals.get(producto, 0.0) + record.importe

        sorted_items = sorted(
            {k: round(v, 2) for k, v in totals.items()}.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        return dict(sorted_items[:n])

    def total_amount(self, records: list[SalesRecord]) -> float:
        """Calcula la facturación total acumulada de todos los registros válidos."""
        return round(sum(r.importe for r in records), 2)

    def summary(
        self,
        records: list[SalesRecord],
        total_raw: int,
    ) -> dict[str, Any]:
        """Genera el diccionario resumen con los indicadores de calidad y negocio."""
        valid_count = len(records)
        invalid_count = max(0, total_raw - valid_count)
        return {
            "filas_totales": int(total_raw),
            "filas_validas": int(valid_count),
            "filas_invalidas": int(invalid_count),
            "importe_total": self.total_amount(records),
        }