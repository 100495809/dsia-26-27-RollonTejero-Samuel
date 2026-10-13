# Proyecto I — Programación Avanzada en Python (DSIA)

[![CI](https://github.com/100495809/dsia-26-27-RollonTejero-Samuel/actions/workflows/ci.yml/badge.svg)](https://github.com/100495809/dsia-26-27-RollonTejero-Samuel/actions/workflows/ci.yml)

Práctica del Proyecto I para la asignatura DSIA. Implementa dos pipelines modulares en Python con carga de datos, validación con excepciones de dominio, métricas de negocio, interfaz de línea de comandos (CLI) y tests unitarios e integración con `pytest`.

---

## Estructura del Proyecto

```text
proyecto_i/
├── data/
│   ├── ventas.csv              # ENTRADA: Dataset de ventas del curso (150 filas)
│   ├── ventas_limpias.csv      # SALIDA: CSV limpio con columna calculada 'importe' (140 filas)
│   ├── calidad_datos.json      # SALIDA: Informe JSON con métricas de ventas
│   ├── inmuebles_sample.csv    # ENTRADA: Muestra de Idealista (3.000 filas con errores)
│   ├── inmuebles_limpios.csv   # SALIDA: CSV limpio con columna calculada 'precio_m2' (2.984 filas)
│   └── calidad_inmuebles.json  # SALIDA: Informe JSON con métricas inmobiliarias
├── ventas_app/                 # Parte A: Pipeline de ventas del curso
│   ├── __init__.py
│   ├── __main__.py             # Permite ejecutar python -m ventas_app
│   ├── errors.py               # Excepciones de dominio (SalesDomainError)
│   ├── loader.py               # Carga con SalesLoader
│   ├── validator.py            # Validación y cálculo de importe con pandas
│   ├── metrics.py              # Agregaciones (región, top productos)
│   └── cli.py                  # CLI con argparse
├── inmuebles_app/              # Parte B: Pipeline inmobiliario
│   ├── __init__.py
│   ├── __main__.py             # Permite ejecutar python -m inmuebles_app
│   ├── errors.py               # Excepciones de dominio (InmueblesDomainError)
│   ├── loader.py               # Carga con InmueblesLoader
│   ├── validator.py            # Validación y cálculo de precio_m2 con pandas
│   ├── metrics.py              # Agregaciones (ciudad, precio/m2, habitaciones)
│   ├── cli.py                  # CLI con argparse
│   └── scripts/
│       └── preparar_datos.py   # Script de preparación de la muestra
├── tests/
│   ├── conftest.py             # Fixtures en memoria para ventas e inmuebles
│   ├── ventas/                 # Tests unitarios e integración de ventas
│   │   ├── test_loader.py
│   │   ├── test_validator.py
│   │   ├── test_metrics.py
│   │   └── test_cli.py
│   └── inmuebles/              # Tests unitarios e integración de inmuebles
│       ├── test_loader.py
│       ├── test_validator.py
│       ├── test_metrics.py
│       └── test_cli.py
├── pytest.ini                  # Configuración de pytest (pythonpath y markers)
└── requirements.txt            # Dependencias (pandas, pytest, pytest-cov)
```

---

## Instalación y Ejecución

1. Activar el entorno virtual:

```bash
# Windows (PowerShell)
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

> **Importante:** Ejecutar los comandos situándose dentro de la carpeta `proyecto_i`:
> ```bash
> cd proyecto_i
> ```

---

## Parte A — Pipeline de Ventas (`ventas_app`)

Carga el fichero [`data/ventas.csv`](data/ventas.csv), valida que `unidades > 0` y `precio_unitario > 0`, genera la columna calculada `importe` y calcula métricas por región y producto.

### Ejecución

```bash
# Ejecución básica:
python -m ventas_app

# Salida:
# Procesamiento completado con éxito: 140/150 filas válidas.
# Importe total: 96598.17 €

# Especificando parámetros y guardando informe JSON:
python -m ventas_app --input data/ventas.csv --output data/ventas_limpias.csv --report data/calidad_datos.json
```

---

## Parte B — Pipeline de Inmuebles (`inmuebles_app`)

### Información del Dataset
* **Origen / URL**: URL del repositorio: [paezha/idealista18](https://github.com/paezha/idealista18)
* **Licencia**: Open Data / Uso académico y de investigación.
* **Fecha de descarga**: Octubre 2026.
* **Descripción**: Ofertas de viviendas en venta publicadas en Idealista en 2018 para Madrid, Barcelona y Valencia.
* **Muestra en el repo**: Se incluye una muestra equilibrada de **3.000 filas** ([`data/inmuebles_sample.csv`](data/inmuebles_sample.csv), 1.000 por ciudad) para evitar subir ficheros pesados (el fichero completo supera 47 MB). En [`inmuebles_app/scripts/preparar_datos.py`](inmuebles_app/scripts/preparar_datos.py) se documenta la extracción a partir de los datos originales.

### Reglas de Validación
* `precio > 10000` € (descarta precios erróneos o simbólicos).
* `superficie >= 15` m² (mínimo de habitabilidad).
* `habitaciones >= 0` y `banos >= 1`.
* Ciudad válida (`Madrid`, `Barcelona` o `Valencia`).
* Control de duplicados por identificador (`ASSETID`).
* Columna calculada: `precio_m2 = precio / superficie`.

### Métricas
1. Precio medio por ciudad.
2. Precio medio por m² por ciudad.
3. Precio medio por número de habitaciones.
4. Resumen global de calidad (total, válidas, descartadas).

### Ejecución

```bash
# 1. Ejecución con la muestra por defecto (3.000 filas):
python -m inmuebles_app

# Salida:
# Procesamiento completado con éxito: 2984/3000 válidas.
# Precio medio global: 322003.02 €

# Con parámetros y reporte JSON:
python -m inmuebles_app --input data/inmuebles_sample.csv --output data/inmuebles_limpios.csv --report data/calidad_inmuebles.json

# 2. (Opcional) Ejecución sobre el dataset completo si se dispone de él localmente (ignorado en git):
python -m inmuebles_app --input data/inmuebles_combined.csv --output data/inmuebles_limpios.csv --report data/calidad_inmuebles.json

# Salida esperada con el dataset completo:
# Procesamiento completado con éxito: 149760/189923 válidas.
# Precio medio global: 354832.18 €
```

---

## Tests Unitarios e Integración (`pytest`)

El proyecto cuenta con **22 tests** repartidos equilibradamente entre ambas aplicaciones (11 para `ventas` y 11 para `inmuebles`).

### Cobertura por módulo

| Módulo | Tests Ventas | Tests Inmuebles | Qué evalúa |
| :--- | :---: | :---: | :--- |
| `loader` | 2 | 2 | Carga correcta con `tmp_path` y excepción de dominio (`pytest.raises`) |
| `validator` | 5 | 5 | Separación con `fixture`, `@pytest.mark.parametrize` con casos borde, columnas requeridas y `@pytest.mark.integration` |
| `metrics` | 2 | 2 | Agregaciones con pandas sobre fixtures y cálculo de resumen |
| `cli` | 2 | 2 | Smoke test end-to-end (código 0) y error de fichero inexistente (código 1) |
| **Total** | **11** | **11** | **22 tests (100 % pass)** |

### Comandos de Ejecución

```bash
# Ejecutar todos los tests:
pytest -q

# Ejecutar solo tests unitarios (sin los datasets reales):
pytest -q -m "not integration"

# Ejecutar solo tests de integración:
pytest -q -m "integration"

# Medir cobertura de código con el umbral mínimo del 60 %:
pytest --cov=ventas_app --cov=inmuebles_app --cov-report=term-missing --cov-fail-under=60
```

> **Cobertura actual:** **86.61 %** (superando el 60 % obligatorio de la rúbrica).

---

## Integración Continua (CI)

El proyecto cuenta con un workflow automatizado de CI en GitHub Actions configurado en [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

En cada `push` o `pull_request` sobre la rama `main`, el workflow ejecuta:
1. Configuración del entorno con Ubuntu y Python 3.12.
2. Instalación de dependencias del proyecto ([`requirements.txt`](requirements.txt)).
3. Ejecución de los tests unitarios e integración validando el umbral de cobertura mínimo del 60 %:

```bash
pytest -q --cov=ventas_app --cov=inmuebles_app --cov-report=term-missing --cov-fail-under=60
```

