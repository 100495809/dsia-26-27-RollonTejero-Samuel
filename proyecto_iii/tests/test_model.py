"""Pruebas unitarias para el entrenamiento, persistencia e inferencia del modelo"""
from pathlib import Path
import pandas as pd
import pytest

from src.models.trainer import (
    build_pipeline,
    train_and_evaluate,
    save_model_artifacts,
)
from src.models.predictor import HousePricePredictor


@pytest.fixture
def sample_training_data() -> pd.DataFrame:
    """Genera datos sintéticos para entrenar un modelo rápido en las pruebas"""
    data = []
    # Generar 40 filas sinteticas con relaciones realistas
    for i in range(40):
        area = 40.0 + (i * 3.0)
        rooms = 1 + (i % 4)
        baths = 1 + (i % 3)
        lift = 1 if i % 2 == 0 else 0
        district = "Centro" if i % 2 == 0 else "Salamanca"
        # Precio aproximado con ruido simple
        price = 100000.0 + (area * 3000.0) + (rooms * 10000.0)

        row = {
            "PRICE": price,
            "CONSTRUCTEDAREA": area,
            "ROOMNUMBER": rooms,
            "BATHNUMBER": baths,
            "HASLIFT": lift,
            "HASAIRCONDITIONING": 1,
            "HASTERRACE": 0,
            "HASSWIMMINGPOOL": 0,
            "HASPARKINGSPACE": 0,
            "HASBOXROOM": 0,
            "HASGARDEN": 0,
            "district": district,
        }
        data.append(row)

    return pd.DataFrame(data)


def test_build_pipeline_structure():
    """Comprueba que el pipeline se construye con preprocesador y regresor"""
    pipeline = build_pipeline()
    assert "preprocessor" in pipeline.named_steps
    assert "regressor" in pipeline.named_steps


def test_train_and_evaluate_generates_metrics(sample_training_data: pd.DataFrame):
    """Verifica que el entrenamiento genera las tres metricas principales"""
    pipeline, metrics = train_and_evaluate(sample_training_data, test_size=0.25)

    assert "mae" in metrics
    assert "rmse" in metrics
    assert "r2_score" in metrics
    assert metrics["train_samples"] == 30
    assert metrics["test_samples"] == 10
    assert metrics["mae"] >= 0.0
    assert metrics["rmse"] >= 0.0


def test_save_and_load_predictor(sample_training_data: pd.DataFrame, tmp_path: Path):
    """Comprueba que el modelo se serializa en joblib y el predictor realiza inferencias"""
    pipeline, metrics = train_and_evaluate(sample_training_data)

    model_file = tmp_path / "test_model.joblib"
    metrics_file = tmp_path / "test_metrics.json"

    save_model_artifacts(pipeline, metrics, model_path=model_file, metrics_path=metrics_file)

    assert model_file.exists()
    assert metrics_file.exists()

    # Cargar el modelo con la clase de inferencia
    predictor = HousePricePredictor(model_path=model_file)

    sample_house = {
        "CONSTRUCTEDAREA": 75.0,
        "ROOMNUMBER": 2,
        "BATHNUMBER": 1,
        "district": "Centro",
        "HASLIFT": 1,
    }

    prediction = predictor.predict_price(sample_house)
    assert isinstance(prediction, float)
    assert prediction > 0.0


def test_predictor_missing_model_raises_error(tmp_path: Path):
    """Verifica que si no existe el archivo se eleva FileNotFoundError"""
    fake_path = tmp_path / "no_existe.joblib"
    with pytest.raises(FileNotFoundError):
        HousePricePredictor(model_path=fake_path)
