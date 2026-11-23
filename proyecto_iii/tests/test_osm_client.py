"""Pruebas unitarias para el cliente de Nominatim OpenStreetMap"""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.clients.osm_client import NominatimClient, format_geo_key


def test_spatial_binning_rounding():
    """Comprueba que las coordenadas se redondean correctamente a dos decimales"""
    key1 = format_geo_key(40.422429, -3.710724)
    key2 = format_geo_key(40.421111, -3.714999)

    # Ambos puntos cercanos deben pertenecer a la misma celda espacial
    assert key1 == "40.42,-3.71"
    assert key2 == "40.42,-3.71"
    assert key1 == key2


def test_reverse_geocode_mock_mode(tmp_path: Path):
    """Comprueba que el modo mock devuelve datos simulados sin ensuciar la caché en disco"""
    cache_file = tmp_path / "test_geo_cache.json"
    client = NominatimClient(cache_path=cache_file, mock_mode=True)

    result = client.reverse_geocode(40.4224, -3.7107)

    assert result["district"] == "Centro"
    assert result["neighborhood"] == "Sol"
    assert result["postcode"] == "28013"

    # Verificar que no se ha creado ni contaminado el archivo de caché en disco
    assert not cache_file.exists()


def test_reverse_geocode_uses_existing_cache(tmp_path: Path):
    """Comprueba que si el dato ya existe en caché no se realiza petición HTTP"""
    cache_file = tmp_path / "test_geo_cache.json"
    cache_initial = {
        "40.45,-3.69": {
            "district": "Chamartín",
            "neighborhood": "Castilla",
            "postcode": "28036",
            "city": "Madrid",
        }
    }
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache_initial, f)

    # Cliente con mock_mode desactivado
    client = NominatimClient(cache_path=cache_file, mock_mode=False)

    # Con patch comprobamos que requests.get nunca es llamado
    with patch("requests.get") as mock_get:
        result = client.reverse_geocode(40.4512, -3.6899)
        assert result["district"] == "Chamartín"
        assert result["neighborhood"] == "Castilla"
        mock_get.assert_not_called()


def test_reverse_geocode_network_fallback(tmp_path: Path):
    """Comprueba que ante un fallo de red el cliente devuelve valores por defecto seguros"""
    cache_file = tmp_path / "test_geo_cache.json"
    client = NominatimClient(cache_path=cache_file, mock_mode=False)

    with patch("requests.get", side_effect=Exception("Error de conexión simulado")):
        result = client.reverse_geocode(40.50, -3.60)
        assert result["district"] == "Desconocido"
        assert result["neighborhood"] == "Desconocido"


def test_reverse_geocode_real_call_persists_to_cache(tmp_path: Path):
    """Comprueba que cuando no es mock y la API responde se guarda en memoria y en disco"""
    cache_file = tmp_path / "test_geo_cache.json"
    client = NominatimClient(cache_path=cache_file, mock_mode=False, delay=0.0)

    # Simular respuesta HTTP exitosa de OpenStreetMap
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "address": {
            "suburb": "Retiro",
            "neighbourhood": "Ibiza",
            "postcode": "28009",
            "city": "Madrid",
        }
    }

    with patch("requests.get", return_value=mock_response):
        result = client.reverse_geocode(40.418, -3.676)

        assert result["district"] == "Retiro"
        assert result["neighborhood"] == "Ibiza"
        assert result["postcode"] == "28009"

    # Verificar que ahora SI existe el archivo en disco y tiene el dato real
    assert cache_file.exists()
    with open(cache_file, "r", encoding="utf-8") as f:
        disk_data = json.load(f)

    assert "40.42,-3.68" in disk_data
    assert disk_data["40.42,-3.68"]["district"] == "Retiro"
    assert disk_data["40.42,-3.68"]["neighborhood"] == "Ibiza"
