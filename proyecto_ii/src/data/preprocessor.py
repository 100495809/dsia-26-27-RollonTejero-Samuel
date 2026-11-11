"""Módulo de preprocesamiento, enriquecimiento geográfico y limpieza de datos"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import sys
from typing import Optional, Tuple
import pandas as pd

# Asegurar que la raiz del proyecto se encuentra en sys path para ejecucion directa
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from config.settings import settings
from src.clients.osm_client import NominatimClient, format_geo_key

# Columnas mínimas que deben estar presentes en el dataset de entrada
REQUIRED_COLUMNS = {
    "PRICE",
    "CONSTRUCTEDAREA",
    "ROOMNUMBER",
    "BATHNUMBER",
    "LATITUDE",
    "LONGITUDE",
}

# Columnas binarias de comodidades del inmueble a normalizar
AMENITY_COLUMNS = [
    "HASLIFT",
    "HASAIRCONDITIONING",
    "HASTERRACE",
    "HASSWIMMINGPOOL",
    "HASPARKINGSPACE",
    "HASBOXROOM",
    "HASGARDEN",
]


def setup_logging(log_file: Optional[Path] = None) -> logging.Logger:
    """Configura el sistema de logs para consola y opcionalmente archivo"""
    logger = logging.getLogger("preprocessor")
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)

    return logger


def load_raw_data(
    file_path: Optional[Path] = None,
    sample_size: Optional[int] = None,
    logger: Optional[logging.Logger] = None,
) -> pd.DataFrame:
    """Carga el archivo CSV crudo y valida que contenga las columnas obligatorias"""
    log = logger or logging.getLogger("preprocessor")
    path = file_path or settings.get_absolute_path(settings.DATA_PATH)

    log.info("Cargando datos desde %s", path)
    if not path.exists():
        log.error("El archivo de datos no existe: %s", path)
        raise FileNotFoundError(f"No se encontro el archivo: {path}")

    df = pd.read_csv(path)
    log.info("Dataset cargado con %d filas y %d columnas", len(df), len(df.columns))

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        log.error("Faltan columnas requeridas en el CSV: %s", sorted(missing))
        raise ValueError(f"Faltan columnas obligatorias: {sorted(missing)}")

    if sample_size is not None and sample_size < len(df):
        log.info("Extrayendo muestra representativa de %d filas", sample_size)
        df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)

    return df


def enrich_with_geodata(
    df: pd.DataFrame,
    osm_client: Optional[NominatimClient] = None,
    logger: Optional[logging.Logger] = None,
) -> pd.DataFrame:
    """Añade distrito, barrio y codigo postal redondeando decimales y con la cache de OSM"""
    log = logger or logging.getLogger("preprocessor")
    client = osm_client or NominatimClient()

    work = df.copy()

    # Generar la clave geoespacial redondeando coordenadas a 2 decimales
    log.info("Calculando claves geoespaciales con  agrupamiaento espacial (spatial binning)")
    work["lat_bin"] = work["LATITUDE"].round(2)
    work["lon_bin"] = work["LONGITUDE"].round(2)
    
    def construir_clave(fila):
        return format_geo_key(fila["LATITUDE"], fila["LONGITUDE"])

    work["geo_key"] = work.apply(construir_clave, axis=1)

    unique_keys = work[["geo_key", "lat_bin", "lon_bin"]].drop_duplicates()
    log.info("Total de celdas espaciales unicas a resolver: %d", len(unique_keys))

    # Diccionarios para guardar la correspondencia de cada coordenada
    district_map = {}
    neighborhood_map = {}
    postcode_map = {}

    # Consultar cada coordenada unica y rellenar los diccionarios en un solo bucle
    for _, row in unique_keys.iterrows():
        key = row["geo_key"]
        info = client.reverse_geocode(row["lat_bin"], row["lon_bin"])
        
        district_map[key] = info.get("district", "Desconocido")
        neighborhood_map[key] = info.get("neighborhood", "Desconocido")
        postcode_map[key] = info.get("postcode", "Desconocido")

    # Mapear los resultados al DataFrame completo usando los diccionarios
    work["district"] = work["geo_key"].map(district_map).fillna("Desconocido")
    work["neighborhood"] = work["geo_key"].map(neighborhood_map).fillna("Desconocido")
    work["postcode"] = work["geo_key"].map(postcode_map).fillna("Desconocido")

    log.info("Enriquecimiento geografico completado con exito")
    return work


def clean_and_transform(
    df: pd.DataFrame,
    logger: Optional[logging.Logger] = None,
) -> Tuple[pd.DataFrame, dict]:
    """Limpia tipos de datos, elimina outliers extremos y genera reporte de transformacion"""
    log = logger or logging.getLogger("preprocessor")
    work = df.copy()

    rows_in = len(work)

    # Coerción numérica de variables críticas
    work["PRICE"] = pd.to_numeric(work["PRICE"], errors="coerce")
    work["CONSTRUCTEDAREA"] = pd.to_numeric(work["CONSTRUCTEDAREA"], errors="coerce")
    work["ROOMNUMBER"] = pd.to_numeric(work["ROOMNUMBER"], errors="coerce")
    work["BATHNUMBER"] = pd.to_numeric(work["BATHNUMBER"], errors="coerce")

    # Tratamiento de comodidades binarias opcionales
    for col in AMENITY_COLUMNS:
        if col in work.columns:
            work[col] = pd.to_numeric(work[col], errors="coerce").fillna(0).astype(int)
        else:
            work[col] = 0

    # Filtro de registros validos para tasacion inmobiliaria
    # Se descartan precios no razonables (menores a 30.000 o mayores a 5.000.000) y areas nulas
    valid_mask = (
        work["PRICE"].notna()
        & (work["PRICE"] >= 30000)
        & (work["PRICE"] <= 5000000)
        & work["CONSTRUCTEDAREA"].notna()
        & (work["CONSTRUCTEDAREA"] >= 15)
        & (work["CONSTRUCTEDAREA"] <= 800)
        & work["ROOMNUMBER"].notna()
        & (work["ROOMNUMBER"] >= 0)
        & work["BATHNUMBER"].notna()
        & (work["BATHNUMBER"] >= 1)
        & work["LATITUDE"].notna()
        & work["LONGITUDE"].notna()
    )

    clean_df = work.loc[valid_mask].copy().reset_index(drop=True)
    rows_out = len(clean_df)
    rows_dropped = rows_in - rows_out
    error_rate = float(rows_dropped / rows_in) if rows_in > 0 else 0.0

    report = {
        "rows_in": rows_in,
        "rows_out": rows_out,
        "rows_dropped": rows_dropped,
        "error_rate": round(error_rate, 4),
        "avg_price": round(float(clean_df["PRICE"].mean()), 2) if rows_out > 0 else 0.0,
        "avg_constructed_area": round(float(clean_df["CONSTRUCTEDAREA"].mean()), 2) if rows_out > 0 else 0.0,
        "unique_districts": int(clean_df["district"].nunique()) if "district" in clean_df.columns else 0,
    }

    log.info("Transformacion finalizada: %d filas de entrada, %d validas (descartadas: %d)", rows_in, rows_out, rows_dropped)
    return clean_df, report


def save_processed_data(
    df: pd.DataFrame,
    report: dict,
    output_dir: Path,
    is_mock: bool = False,
    logger: Optional[logging.Logger] = None,
) -> Tuple[Path, Path]:
    """Guarda el DataFrame limpio en CSV y el reporte de calidad en JSON diferenciando ejecuciones mock"""
    log = logger or logging.getLogger("preprocessor")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Separar archivos para que las ejecuciones de prueba con mock nunca sobrescriban los datos reales
    data_filename = "madrid_mock_limpio.csv" if is_mock else "madrid_limpio.csv"
    report_filename = "data_quality_report_mock.json" if is_mock else "data_quality_report.json"

    data_output = output_dir / data_filename
    report_output = output_dir / report_filename

    df.to_csv(data_output, index=False)
    report_output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    log.info("Datos limpios guardados en %s", data_output)
    log.info("Reporte de calidad guardado en %s", report_output)

    return data_output, report_output


def run_pipeline(
    input_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    sample_size: Optional[int] = None,
    osm_client: Optional[NominatimClient] = None,
) -> Tuple[pd.DataFrame, dict]:
    """Orquesta la carga, enriquecimiento y limpieza completa de datos"""
    logger = setup_logging()
    logger.info("Iniciando pipeline de preprocesamiento de datos")

    client = osm_client or NominatimClient()
    is_mock = bool(client.mock_mode)

    df_raw = load_raw_data(input_path, sample_size=sample_size, logger=logger)
    df_enriched = enrich_with_geodata(df_raw, osm_client=client, logger=logger)
    df_clean, report = clean_and_transform(df_enriched, logger=logger)

    if output_dir is not None:
        save_processed_data(df_clean, report, output_dir, is_mock=is_mock, logger=logger)

    logger.info("Pipeline de preprocesamiento completado con exito")
    return df_clean, report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline de preprocesamiento de inmuebles de Madrid")
    parser.add_argument("--input", type=Path, default=None, help="Ruta al CSV de entrada")
    parser.add_argument("--output-dir", type=Path, default=Path("data"), help="Directorio para guardar resultados")
    parser.add_argument("--sample", type=int, default=None, help="Numero de filas para muestra rapida")
    parser.add_argument("--mock-geo", action="store_true", help="Forzar modo mock en geocodificacion")
    args = parser.parse_args()

    client = NominatimClient(mock_mode=True) if args.mock_geo else None

    run_pipeline(
        input_path=args.input,
        output_dir=args.output_dir,
        sample_size=args.sample,
        osm_client=client,
    )
