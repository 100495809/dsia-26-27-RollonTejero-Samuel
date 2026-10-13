import os
import rdata
import warnings
import pandas as pd


# Adaptacion del script en el proyecto de ML para convertir archivos .rda a .csv y combinarlos en un solo conjunto de datos



file_names = [
    "Barcelona_POIS.rda",
    "Barcelona_Polygons.rda",
    "Barcelona_Sale.rda",
    "Madrid_POIS.rda",
    "Madrid_Polygons.rda",
    "Madrid_Sale.rda",
    "Valencia_POIS.rda",
    "Valencia_Polygons.rda",
    "Valencia_Sale.rda",
    "properties_by_district.rda"
]


python_path = os.path.dirname(__file__)
r_data_path = os.path.join(python_path, "..", "data")


def convert_to_csv(rda_path_folder):
    output_path = os.path.join(python_path, "..", "data-clean")
    os.makedirs(output_path, exist_ok=True)

    for rda_file in file_names:
        if not rda_file.endswith("_Sale.rda"):
            continue

        rda_path = os.path.join(rda_path_folder, rda_file)

        if not os.path.isfile(rda_path):
            print(f"File not found: {rda_path}")
            continue

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            data = rdata.read_rda(rda_path, default_encoding="utf8")

        object_name = os.path.splitext(rda_file)[0]
        df = data[object_name]

        csv_file = os.path.join(
            output_path,
            object_name.lower() + ".csv"
        )

        df.to_csv(csv_file, index=False)
        print(f"Created: {csv_file}")








python_path = os.path.dirname(__file__)


def merge_sales():
    files = {
        "Barcelona": os.path.join(
            python_path, "..", "data-clean", "barcelona_sale.csv"
        ),
        "Madrid": os.path.join(
            python_path, "..", "data-clean", "madrid_sale.csv"
        ),
        "Valencia": os.path.join(
            python_path, "..", "data-clean", "valencia_sale.csv"
        ),
    }

    dataframes = []

    for city, file_path in files.items():
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            continue

        df = pd.read_csv(file_path)
        df["CITY"] = city

        dataframes.append(df)

        print(f"{city}: {len(df)} rows")

    if not dataframes:
        print("No CSV files found.")
        return

    merged_df = pd.concat(dataframes, ignore_index=True)
    output_path = os.path.join(
        python_path, "..", "data-clean", "inmuebles_combined.csv"
    )
    merged_df.to_csv(output_path, index=False)

    print("\nCombined dataset:")
    print(f"Rows: {len(merged_df)}")
    print(f"Columns: {len(merged_df.columns)}")
    print(f"Saved to: {output_path}")



convert_to_csv(r_data_path)
merge_sales()