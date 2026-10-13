"""Tests unitarios y de integración para el validator de inmuebles."""
from pathlib import Path
import pandas as pd
import pytest

from inmuebles_app.errors import InmuebleValidationError
from inmuebles_app.validator import InmueblesValidator


def test_validator_split_separa_validos_e_invalidos(inmuebles_mini: pd.DataFrame) -> None:
    """AAA: Separa correctamente válidos e inválidos sobre fixture en memoria."""
    validator = InmueblesValidator()
    validos, invalidos = validator.split(inmuebles_mini)

    assert len(validos) == 1
    assert len(invalidos) == 3
    assert "precio_m2" in validos.columns
    assert validos.iloc[0]["precio_m2"] == 2500.0


@pytest.mark.parametrize(
    ("precio", "esperado_valido"),
    [
        (250000.0, True),
        (5000.0, False),
    ],
)
def test_validator_borde_precio(precio: float, esperado_valido: bool) -> None:
    """Parametrize: comprueba límites de precio inmobiliario (> 10000)."""
    df = pd.DataFrame({
        "CITY": ["Madrid"],
        "PRICE": [precio],
        "CONSTRUCTEDAREA": [70.0],
        "ROOMNUMBER": [2],
        "BATHNUMBER": [1],
    })
    validator = InmueblesValidator()
    validos, _ = validator.split(df)

    assert (len(validos) == 1) == esperado_valido


def test_validator_columnas_faltantes_lanza_error() -> None:
    """Verifica que un DataFrame sin columnas requeridas lance InmuebleValidationError."""
    validator = InmueblesValidator()
    with pytest.raises(InmuebleValidationError):
        validator.split(pd.DataFrame({"columna_x": [1]}))


@pytest.mark.integration
def test_dataset_inmuebles_sample_checkpoint(inmuebles_sample_path: Path) -> None:
    """Checkpoint de integración: inmuebles_sample.csv debe contener 2984 válidos y 16 descartados."""
    df = pd.read_csv(inmuebles_sample_path)
    validator = InmueblesValidator()
    validos, invalidos = validator.split(df)

    assert len(validos) == 2984
    assert len(invalidos) == 16
