"""Pruebas de integracion para el pipeline completo de tasacion"""
import pytest

from src.clients.ai_client import AIClient
from src.clients.osm_client import NominatimClient
from src.models.predictor import HousePricePredictor
from src.pipeline import ValuationPipeline


@pytest.fixture
def test_pipeline(tmp_path) -> ValuationPipeline:
    """Instancia el orquestador configurando los clientes en modo simulado"""
    osm_mock = NominatimClient(cache_path=tmp_path / "cache_pipeline.json", mock_mode=True)
    ai_mock = AIClient(mock_mode=True)
    predictor = HousePricePredictor()

    return ValuationPipeline(
        osm_client=osm_mock,
        predictor=predictor,
        ai_client=ai_mock,
    )


def test_valuation_pipeline_with_coordinates(test_pipeline: ValuationPipeline):
    """Comprueba el flujo integral pasando coordenadas geograficas"""
    property_input = {
        "CONSTRUCTEDAREA": 85.0,
        "ROOMNUMBER": 3,
        "BATHNUMBER": 2,
        "LATITUDE": 40.4224,
        "LONGITUDE": -3.7107,
        "HASLIFT": 1,
        "HASAIRCONDITIONING": 1,
    }

    result = test_pipeline.evaluate_property(property_input)

    assert "location" in result
    assert result["location"]["district"] == "Centro"
    assert result["location"]["neighborhood"] == "Sol"

    assert "predicted_price" in result
    assert isinstance(result["predicted_price"], float)
    assert result["predicted_price"] > 0.0

    assert "valuation_report" in result
    assert "[mock]" in result["valuation_report"]
    assert result["ai_provider"] == "mock"


def test_valuation_pipeline_without_coordinates(test_pipeline: ValuationPipeline):
    """Comprueba el flujo integral pasando directamente el nombre del distrito"""
    property_input = {
        "CONSTRUCTEDAREA": 60.0,
        "ROOMNUMBER": 1,
        "BATHNUMBER": 1,
        "district": "Salamanca",
    }

    result = test_pipeline.evaluate_property(property_input)

    assert result["location"]["district"] == "Salamanca"
    assert result["predicted_price"] > 0.0
    assert result["ai_provider"] == "mock"
