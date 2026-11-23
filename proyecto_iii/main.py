"""Punto de entrada principal y unificado para el Proyecto II"""
import argparse
import sys
from pathlib import Path

from config.settings import settings
from src.clients.ai_client import AIClient
from src.clients.osm_client import NominatimClient
from src.data.preprocessor import run_pipeline
from src.models.trainer import run_training_flow
from src.pipeline import ValuationPipeline

# Asegurar que la ruta base del proyecto esta en sys path
_base_dir = Path(__file__).resolve().parent
if str(_base_dir) not in sys.path:
    sys.path.insert(0, str(_base_dir))




def ejecutar_preprocesamiento(args):
    """Ejecuta la fase de limpieza y enriquecimiento geografico"""
    print("\n--- INICIANDO PREPROCESAMIENTO DE DATOS ---")
    if args.mock_geo:
        cliente_osm = NominatimClient(mock_mode=True)
    else:
        cliente_osm = None

    if args.input is not None:
        ruta_entrada = Path(args.input)
    else:
        ruta_entrada = settings.get_absolute_path(settings.DATA_PATH)

    if args.output_dir is not None:
        directorio_salida = Path(args.output_dir)
    else:
        directorio_salida = settings.get_absolute_path("data")

    df_limpio, reporte = run_pipeline(
        input_path=ruta_entrada,
        output_dir=directorio_salida,
        sample_size=args.sample,
        osm_client=cliente_osm,
    )
    print("\nPreprocesamiento completado:")
    print(f"- Filas procesadas: {reporte['rows_out']}")
    print(f"- Distritos unicos: {reporte['unique_districts']}")
    print(f"- Tasa de descarte: {reporte['error_rate'] * 100:.2f} %")


def ejecutar_entrenamiento(args):
    """Ejecuta el entrenamiento del modelo Scikit-Learn y genera las metricas"""
    print("\n--- INICIANDO ENTRENAMIENTO DEL MODELO ---")
    if args.data is not None:
        ruta_datos = Path(args.data)
    else:
        ruta_datos = None

    _, metricas = run_training_flow(data_path=ruta_datos, sample_size=args.sample, mock_geo=args.mock_geo)
    print("\nEntrenamiento finalizado:")
    print(f"- Muestras de test: {metricas['test_samples']}")
    print(f"- MAE: {metricas['mae']} EUR")
    print(f"- RMSE: {metricas['rmse']} EUR")
    print(f"- R2 Score: {metricas['r2_score']}")


def ejecutar_tasacion(args):
    """Ejecuta el pipeline completo de valoracion e informe con IA"""
    print("\n--- INICIANDO PIPELINE DE TASACION ---")
    if args.mock_ai:
        cliente_ai = AIClient(mock_mode=True)
    else:
        cliente_ai = None

    pipeline = ValuationPipeline(ai_client=cliente_ai)

    datos_inmueble = {
        "CONSTRUCTEDAREA": args.area,
        "ROOMNUMBER": args.rooms,
        "BATHNUMBER": args.baths,
        "LATITUDE": args.lat,
        "LONGITUDE": args.lon,
        "HASLIFT": args.lift,
    }

    resultado = pipeline.evaluate_property(datos_inmueble)

    print("\n" + "=" * 60)
    print("RESULTADO DE LA TASACION")
    print("=" * 60)
    print(f"Inmueble: {datos_inmueble['CONSTRUCTEDAREA']} m2 | {datos_inmueble['ROOMNUMBER']} habs | {datos_inmueble['BATHNUMBER']} baños | Ascensor: {datos_inmueble['HASLIFT']}")
    print(f"Distrito: {resultado['location']['district']} (Barrio: {resultado['location']['neighborhood']})")
    print(f"Precio estimado: {resultado['predicted_price']:,.2f} EUR")
    print(f"Proveedor de IA: {resultado['ai_provider']}")
    print("-" * 60)
    print(resultado["valuation_report"])
    print("=" * 60 + "\n")


def main():
    """Configura los subcomandos de la aplicacion y delega la ejecucion"""
    parser = argparse.ArgumentParser(
        description="Proyecto II: Sistema integral de tasacion inmobiliaria en Madrid",
    )
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponibles")

    # Subcomando preprocess
    parser_prep = subparsers.add_parser("preprocess", help="Limpieza y enriquecimiento de datos")
    parser_prep.add_argument("--input", type=str, default=None, help="Ruta al CSV crudo")
    parser_prep.add_argument("--output-dir", type=str, default=None, help="Directorio para guardar resultados")
    parser_prep.add_argument("--sample", type=int, default=None, help="Numero de filas para muestra rapida")
    parser_prep.add_argument("--mock-geo", action="store_true", help="Usar geocodificacion simulada sin llamar a la API")

    # Subcomando train
    parser_train = subparsers.add_parser("train", help="Entrenamiento del modelo Random Forest")
    parser_train.add_argument("--data", type=str, default=None, help="Ruta al CSV limpio")
    parser_train.add_argument("--sample", type=int, default=None, help="Numero de filas para muestra rapida")
    parser_train.add_argument("--mock-geo", action="store_true", help="Usar mock si es necesario preprocesar")

    # Subcomando evaluate con LLM
    parser_eval = subparsers.add_parser("evaluate", help="Tasacion de un inmueble e informe explicativo con IA")
    parser_eval.add_argument("--area", type=float, default=85.0, help="Superficie construida en m2")
    parser_eval.add_argument("--rooms", type=int, default=2, help="Numero de habitaciones")
    parser_eval.add_argument("--baths", type=int, default=1, help="Numero de baños")
    parser_eval.add_argument("--lat", type=float, default=40.4224, help="Latitud del inmueble")
    parser_eval.add_argument("--lon", type=float, default=-3.7107, help="Longitud del inmueble")
    parser_eval.add_argument("--lift", type=int, default=1, help="Tiene ascensor (1 o 0)")
    parser_eval.add_argument("--mock-ai", action="store_true", help="Forzar informe simulado de IA")

    args = parser.parse_args()

    if args.comando == "preprocess":
        ejecutar_preprocesamiento(args)
    elif args.comando == "train":
        ejecutar_entrenamiento(args)
    elif args.comando == "evaluate":
        ejecutar_tasacion(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
