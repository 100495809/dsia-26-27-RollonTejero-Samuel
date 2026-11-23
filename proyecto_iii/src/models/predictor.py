"""Módulo de inferencia para realizar tasaciones con el modelo entrenado"""
import logging
from pathlib import Path
import joblib
import pandas as pd

from config.settings import settings

logger = logging.getLogger(__name__)


class HousePricePredictor:
    """Clase para cargar el modelo serializado y realizar predicciones de precio"""

    def __init__(self, model_path=None):
        # Determinar la ruta del archivo del modelo
        if model_path is not None:
            self.model_path = model_path
        else:
            self.model_path = settings.get_absolute_path(settings.MODEL_PATH)

        # Comprobar que el archivo existe
        if not self.model_path.exists():
            logger.error("No se encontro el archivo del modelo en: %s", self.model_path)
            raise FileNotFoundError(f"El modelo no existe en la ruta: {self.model_path}")

        # Cargar el modelo entrenado guardado con joblib
        self.model = joblib.load(self.model_path)
        logger.info("Modelo de tasacion cargado con exito desde %s", self.model_path)

    def predict_price(self, property_data: dict) -> float:
        """Recibe las caracteristicas de un inmueble y devuelve el precio estimado"""
        # Convertir el diccionario recibido en un DataFrame de una fila
        df_input = pd.DataFrame([property_data])

        # Asegurar que todas las comodidades opcionales tengan al menos un valor por defecto
        amenity_keys = [
            "HASLIFT",
            "HASAIRCONDITIONING",
            "HASTERRACE",
            "HASSWIMMINGPOOL",
            "HASPARKINGSPACE",
            "HASBOXROOM",
            "HASGARDEN",
        ]
        for key in amenity_keys:
            if key not in df_input.columns:
                df_input[key] = 0

        # Si no se proporciona el distrito, asignar un valor por defecto
        if "district" not in df_input.columns:
            df_input["district"] = "Desconocido"

        # El modelo aplica automaticamente el escalado y el OneHotEncoder antes de predecir
        predicted_array = self.model.predict(df_input)
        price_prediction = float(predicted_array[0])

        # Redondear el resultado a dos decimales
        return round(price_prediction, 2)
