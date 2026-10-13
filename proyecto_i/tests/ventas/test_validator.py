"""Tests unitarios y de integración para el validator de ventas."""
from pathlib import Path
import pandas as pd
import pytest

from ventas_app.errors import ValidationError
from ventas_app.validator import SalesValidator


def test_validator_split_separa_validos_e_invalidos(ventas_mini: pd.DataFrame) -> None:
    """AAA: Separa correctamente válidos e inválidos sobre fixture en memoria."""
    validator = SalesValidator()
    validos, invalidos = validator.split(ventas_mini)

    assert len(validos) == 1
    assert len(invalidos) == 2
    assert "importe" in validos.columns
    assert validos.iloc[0]["importe"] == 20.0


@pytest.mark.parametrize(
    ("unidades", "precio", "esperado_valido"),
    [
        (2.0, 15.0, True),
        (-1.0, 15.0, False),
    ],
)
def test_validator_borde_numerico(unidades: float, precio: float, esperado_valido: bool) -> None:
    """Parametrize: comprueba reglas de unidades y precios válidos vs negativos."""
    df = pd.DataFrame({"unidades": [unidades], "precio_unitario": [precio]})
    validator = SalesValidator()
    validos, _ = validator.split(df)

    assert (len(validos) == 1) == esperado_valido


def test_validator_columnas_faltantes_lanza_error() -> None:
    """Verifica que un DataFrame sin las columnas requeridas lance ValidationError."""
    validator = SalesValidator()
    with pytest.raises(ValidationError):
        validator.split(pd.DataFrame({"columna_inventada": [1]}))


@pytest.mark.integration
def test_csv_curso_checkpoint_140_validas_10_invalidas(ventas_csv_path: Path) -> None:
    """Checkpoint de integración: ventas.csv debe contener 140 válidas y 10 inválidas."""
    df = pd.read_csv(ventas_csv_path)
    validator = SalesValidator()
    validos, invalidos = validator.split(df)

    assert len(validos) == 140
    assert len(invalidos) == 10
