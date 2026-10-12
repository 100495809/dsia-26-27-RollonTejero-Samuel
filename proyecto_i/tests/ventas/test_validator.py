"""Tests unitarios y de integración para el módulo validator de ventas_app."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from ventas_app.errors import ValidationError
from ventas_app.validator import SalesRecord, SalesValidator, validar_ventas


def test_validator_split_ventas_mini_separa_validos_e_invalidos(ventas_mini: pd.DataFrame) -> None:
    """AAA: Comprueba la separación de válidos e inválidos sobre fixture en memoria ventas_mini."""
    # Arrange
    validator = SalesValidator()

    # Act
    validos, invalidos = validator.split(ventas_mini)

    # Assert
    assert len(validos) == 1
    assert len(invalidos) == 2
    assert validos[0].region == "Norte"
    assert validos[0].unidades == 2.0
    assert validos[0].precio_unitario == 10.0
    assert validos[0].importe == 20.0


@pytest.mark.parametrize(
    ("precio", "esperado_valido"),
    [
        (12.5, True),
        (0.01, True),
        (0.0, False),
        (-1.0, False),
        (-50.0, False),
        (None, False),
        ("invalido", False),
    ],
)
def test_validator_borde_precio_unitario(precio: object, esperado_valido: bool) -> None:
    """Parametrize: comprueba casos de borde para precio_unitario (ceros, negativos, nulos, texto)."""
    df = pd.DataFrame({"unidades": [1.0], "precio_unitario": [precio]})
    validator = SalesValidator()

    validos, invalidos = validator.split(df)

    if esperado_valido:
        assert len(validos) == 1
        assert len(invalidos) == 0
    else:
        assert len(validos) == 0
        assert len(invalidos) == 1


@pytest.mark.parametrize(
    ("unidades", "esperado_valido"),
    [
        (5.0, True),
        (1.0, True),
        (0.0, False),
        (-2.0, False),
        (None, False),
        ("no_es_numero", False),
    ],
)
def test_validator_borde_unidades(unidades: object, esperado_valido: bool) -> None:
    """Parametrize: comprueba casos de borde para unidades (cero, negativo, nulo, texto)."""
    df = pd.DataFrame({"unidades": [unidades], "precio_unitario": [10.0]})
    validator = SalesValidator()

    validos, invalidos = validator.split(df)

    if esperado_valido:
        assert len(validos) == 1
        assert len(invalidos) == 0
    else:
        assert len(validos) == 0
        assert len(invalidos) == 1


def test_sales_record_calculo_importe() -> None:
    """Verifica que SalesRecord calcule correctamente la propiedad importe."""
    record = SalesRecord(
        fecha="2026-01-01",
        region="Sur",
        producto="Gateway",
        unidades=3.0,
        precio_unitario=150.0,
        cliente_id="C01",
    )
    assert record.importe == 450.0
    assert record.producto == "Gateway"
    assert record.unidades == 3.0
    assert record.precio_unitario == 150.0



def test_validar_ventas_agrega_columna_importe(ventas_mini: pd.DataFrame) -> None:
    """Verifica la función funcional validar_ventas y la presencia de la columna importe."""
    validos, errores = validar_ventas(ventas_mini)

    assert len(validos) == 1
    assert len(errores) == 2
    assert "importe" in validos.columns
    assert validos.iloc[0]["importe"] == 20.0


def test_validator_input_no_dataframe_raises_validation_error() -> None:
    """Verifica que pasar un objeto no DataFrame lance ValidationError."""
    validator = SalesValidator()
    with pytest.raises(ValidationError):
        validator.split("no_soy_dataframe")  # type: ignore


def test_validator_columnas_faltantes_raises_validation_error() -> None:
    """Verifica que un DataFrame sin las columnas requeridas lance ValidationError."""
    df_sin_precio = pd.DataFrame({"unidades": [1, 2]})
    validator = SalesValidator()
    with pytest.raises(ValidationError):
        validator.split(df_sin_precio)


@pytest.mark.integration
def test_csv_curso_checkpoint_140_validas_10_invalidas(ventas_csv_path: Path) -> None:
    """Test de integración sobre el dataset del curso ventas.csv: exactamente 140 válidas y 10 inválidas."""
    df = pd.read_csv(ventas_csv_path)
    assert len(df) == 150

    validator = SalesValidator()
    validos, invalidos = validator.split(df)

    assert len(validos) == 140
    assert len(invalidos) == 10
