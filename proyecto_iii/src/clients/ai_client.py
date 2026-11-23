"""Cliente unificado para servicios de Inteligencia Artificial y LLMs"""
from __future__ import annotations

from dataclasses import dataclass
import logging
import requests

from config.settings import settings

logger = logging.getLogger("ai_client")


@dataclass
class AIResponse:
    """Estructura tipada para la respuesta devuelta por el servicio de IA"""
    provider: str
    text: str


class AIClientError(RuntimeError):
    """Excepcion para errores en llamadas a servicios de IA"""
    pass


class AIClient:
    """Cliente para interactuar con modelos de lenguaje en modo mock o real"""

    def __init__(self, provider=None, model_id=None, base_url=None, api_key=None, mock_mode=None,):

        # Determinar si se activa el modo mock
        if mock_mode is not None:
            self.mock_mode = mock_mode
        else:
            self.mock_mode = settings.LLM_MOCK

        # Determinar el proveedor
        if provider is not None:
            self.provider = provider.lower().strip()
        else:
            if self.mock_mode:
                self.provider = "mock"
            elif settings.HF_TOKEN:
                self.provider = "hf"
            else:
                self.provider = "remote"

        # Identificador del modelo
        if model_id is not None:
            self.model_id = model_id
        else:
            self.model_id = settings.LLM_MODEL_ID

        # URL del servidor remoto
        if base_url is not None:
            self.base_url = base_url
        else:
            self.base_url = settings.LLM_BASE_URL

        # Clave o token de autorizacion
        if api_key is not None:
            self.api_key = api_key
        else:
            if settings.HF_TOKEN:
                self.api_key = settings.HF_TOKEN
            else:
                self.api_key = settings.LLM_API_KEY

    def complete(self, prompt: str) -> AIResponse:
        """Envia un prompt al proveedor seleccionado y devuelve un objeto AIResponse"""
        
        # Caso 1: modo simulado (mock) para pruebas y CI
        if self.mock_mode or self.provider == "mock":
            logger.info("Generando respuesta simulada en modo mock")
            texto_mock = (
                "[mock] Informe de Valoracion Oficial: "
                "El inmueble analizado presenta caracteristicas acordes al mercado residencial de Madrid. "
                "La tasacion estimada por el modelo refleja adecuadamente el valor de la zona "
                "y el estado general de las comodidades declaradas."
            )
            return AIResponse(provider="mock", text=texto_mock)

        # # Caso 2: Proveedor oficial Hugging Face con token
        # if self.provider == "hf" or self.provider == "huggingface":
        #     if not self.api_key:
        #         raise AIClientError("Falta HF_TOKEN en el entorno para usar el proveedor Hugging Face")

        #     try:
        #         from huggingface_hub import InferenceClient
        #     except ImportError as err:
        #         raise AIClientError("Se requiere la libreria huggingface_hub instalada") from err

        #     logger.info("Realizando llamada a Hugging Face Inference API...")
        #     client = InferenceClient(api_key=self.api_key)
        #     modelo = self.model_id
        #     if modelo is None:
        #         modelo = "meta-llama/Llama-3.2-3B-Instruct"

        #     try:
        #         resultado = client.chat_completion(
        #             messages=[{"role": "user", "content": prompt}],
        #             model=modelo,
        #             max_tokens=256,
        #         )
        #         texto = resultado.choices[0].message.content
        #         if texto is None:
        #             texto = ""
        #         return AIResponse(provider="huggingface", text=texto.strip())
        #     except Exception as err:
        #         logger.error("Error al consultar Hugging Face: %s", err)
        #         raise AIClientError(f"Fallo en la llamada a Hugging Face: {err}") from err

        # Caso 3: Servidor remoto propio (máquina con Ollama en local o vpn en servidor)
        if self.provider == "remote":
            logger.info("Realizando llamada a servidor remoto en %s...", self.base_url)
            base_url_limpia = self.base_url.rstrip("/")
            if ":11434" in base_url_limpia and not base_url_limpia.endswith("/v1"):
                base_url_limpia = base_url_limpia + "/v1"

            endpoint = f"{base_url_limpia}/chat/completions"

            headers = {
                "Content-Type": "application/json",
            }
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            if self.model_id is not None and self.model_id != "":
                modelo_remoto = self.model_id
            else:
                modelo_remoto = "gemma4:e2b"

            payload = {
                "model": modelo_remoto,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1024,
            }

            try:
                response = requests.post(endpoint, json=payload, headers=headers, timeout=60.0)
                response.raise_for_status()
                data = response.json()
                texto = data["choices"][0]["message"]["content"]
                return AIResponse(provider="remote", text=texto.strip())
            except Exception as err:
                logger.error("Error al conectar con el servidor remoto: %s", err)
                raise AIClientError(f"No se pudo conectar con {self.base_url}: {err}") from err

        raise AIClientError(f"Proveedor no soportado: {self.provider}")
