"""Módulo para entrenar, evaluar y guardar el modelo de Scikit-Learn"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import sys
from typing import Optional, Tuple

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Asegurar que la raiz del proyecto se encuentra en sys path para ejecucion directa
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from config.settings import settings
from src.data.preprocessor import AMENITY_COLUMNS, run_pipeline

logger = logging.getLogger("trainer")

# Definicion de las variables de entrada para el modelo
NUMERIC_FEATURES = ["CONSTRUCTEDAREA", "ROOMNUMBER", "BATHNUMBER"]
CATEGORICAL_FEATURES = ["district"]
BINARY_FEATURES = AMENITY_COLUMNS
TARGET_COLUMN = "PRICE"


def setup_logging() -> logging.Logger:
    """Configura el sistema de logs para el entrenamiento"""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    return logging.getLogger("trainer")


def build_pipeline() -> Pipeline:
    """Construye el pipeline con preprocesador de columnas y regresor"""
    # Escalado para variables numericas
    numeric_transformer = StandardScaler()

    # Codificacion One-Hot para distritos ignorando categorias no vistas
    categorical_transformer = OneHotEncoder(handle_unknown="ignore")

    # Unir las transformaciones segun el tipo de columna
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
            ("bin", "passthrough", BINARY_FEATURES),
        ]
    )

    # Modelo de random forest
    regressor = RandomForestRegressor(n_estimators=50, max_depth=12, min_samples_split=5, random_state=42,)

    # Crear el pipeline completo que une transformaciones y modelo
    model_pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("regressor", regressor)])

    return model_pipeline


def train_and_evaluate(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42,) -> Tuple[Pipeline, dict]:
    """Entrena el modelo, calcula metricas de evaluacion y las devuelve en un diccionario"""
    log = logging.getLogger("trainer")

    # Seleccionar las columnas que usara el modelo
    feature_columns = []
    for col in NUMERIC_FEATURES:
        feature_columns.append(col)
    for col in CATEGORICAL_FEATURES:
        feature_columns.append(col)
    for col in BINARY_FEATURES:
        feature_columns.append(col)

    X = df[feature_columns]
    y = df[TARGET_COLUMN]

    log.info("Division de datos: 80 %% entrenamiento, 20 %% test (total registros: %d)", len(df))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    pipeline = build_pipeline()

    log.info("Iniciando entrenamiento del modelo...")
    pipeline.fit(X_train, y_train)
    log.info("Entrenamiento finalizado con exito")

    log.info("Evaluando predicciones sobre el conjunto de test...")
    y_pred = pipeline.predict(X_test)

    # Calculo de las tres metricas principales requeridas
    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(root_mean_squared_error(y_test, y_pred))
    r2 = float(r2_score(y_test, y_pred))

    metrics = {
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "r2_score": round(r2, 4),
    }

    log.info("Metricas obtenidas: MAE=%.2f €, RMSE=%.2f €, R2=%.4f", mae, rmse, r2)
    return pipeline, metrics


def save_model_artifacts(pipeline: Pipeline, metrics: dict, model_path: Optional[Path] = None, metrics_path: Optional[Path] = None,) -> Tuple[Path, Path]:
    """Guarda el pipeline en formato joblib y las metricas en archivo JSON"""
    log = logging.getLogger("trainer")

    if model_path is not None:
        m_path = model_path
    else:
        m_path = settings.get_absolute_path(settings.MODEL_PATH)

    if metrics_path is not None:
        met_path = metrics_path
    else:
        met_path = settings.get_absolute_path(settings.METRICS_PATH)

    # Crear el directorio de modelos si no existe
    m_path.parent.mkdir(parents=True, exist_ok=True)
    met_path.parent.mkdir(parents=True, exist_ok=True)

    # Serializar el modelo con joblib
    joblib.dump(pipeline, m_path)
    log.info("Modelo guardado correctamente en: %s", m_path)

    # Guardar las metricas en JSON
    with open(met_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    log.info("Metricas guardadas correctamente en: %s", met_path)

    return m_path, met_path


def run_training_flow(
    data_path: Optional[Path] = None,
    model_path: Optional[Path] = None,
    metrics_path: Optional[Path] = None,
    sample_size: Optional[int] = None,
    mock_geo: bool = False,
) -> Tuple[Pipeline, dict]:
    """Orquesta la carga de datos, el entrenamiento y la persistencia de artefactos"""
    setup_logging()
    log = logging.getLogger("trainer")

    # Determinar que archivo de datos utilizar
    if data_path is not None:
        source_path = data_path
    else:
        real_path = settings.get_absolute_path("data/madrid_limpio.csv")
        mock_path = settings.get_absolute_path("data/madrid_mock_limpio.csv")
        if real_path.exists():
            source_path = real_path
        elif mock_path.exists():
            source_path = mock_path
        else:
            source_path = real_path

    # Si no existe ningun archivo limpio, lo generamos con el pipeline de preprocesamiento
    if not source_path.exists():
        log.info("No se encontro archivo limpio, ejecutando preprocesamiento...")
        from src.clients.osm_client import NominatimClient
        osm_client = NominatimClient(mock_mode=True) if mock_geo else None
        df_clean, _ = run_pipeline(
            input_path=settings.get_absolute_path(settings.DATA_PATH),
            output_dir=settings.get_absolute_path("data"),
            sample_size=sample_size,
            osm_client=osm_client,
        )
    else:
        log.info("Cargando datos limpios existentes desde %s", source_path)
        df_clean = pd.read_csv(source_path)
        if sample_size is not None and sample_size < len(df_clean):
            df_clean = df_clean.sample(n=sample_size, random_state=42).reset_index(drop=True)

    pipeline, metrics = train_and_evaluate(df_clean)
    save_model_artifacts(pipeline, metrics, model_path=model_path, metrics_path=metrics_path)

    return pipeline, metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entrenamiento del modelo de tasacion inmobiliaria")
    parser.add_argument("--data", type=Path, default=None, help="Ruta al CSV con datos limpios")
    parser.add_argument("--model-out", type=Path, default=None, help="Ruta de salida para el archivo .joblib")
    parser.add_argument("--metrics-out", type=Path, default=None, help="Ruta de salida para metrics.json")
    parser.add_argument("--sample", type=int, default=None, help="Usar muestra para entrenamiento rapido")
    parser.add_argument("--mock-geo", action="store_true", help="Forzar modo mock en geodatos si se preprocesa")
    args = parser.parse_args()

    run_training_flow(
        data_path=args.data,
        model_path=args.model_out,
        metrics_path=args.metrics_out,
        sample_size=args.sample,
        mock_geo=args.mock_geo,
    )
