"""Pruebas unitarias para el cliente de Inteligencia Artificial"""
import pytest

from src.clients.ai_client import AIClient, AIClientError, AIResponse


def test_ai_client_mock_mode():
    """Comprueba que el modo mock devuelve un AIResponse simulado sin tocar la red"""
    client = AIClient(mock_mode=True)
    response = client.complete("Prompt de prueba para tasacion")

    assert isinstance(response, AIResponse)
    assert response.provider == "mock"
    assert "[mock]" in response.text
    assert len(response.text) > 20


# def test_ai_client_hf_missing_token_raises_error():
#     """Verifica que se lanza AIClientError si se pide Hugging Face sin token configurado"""
#     client = AIClient(provider="hf", api_key="", mock_mode=False)

#     with pytest.raises(AIClientError, match="Falta HF_TOKEN"):
#         client.complete("Generar tasacion")


def test_ai_client_unsupported_provider():
    """Verifica que un proveedor desconocido lanza AIClientError"""
    client = AIClient(provider="proveedor_inventado", mock_mode=False)

    with pytest.raises(AIClientError, match="Proveedor no soportado"):
        client.complete("Prueba")
