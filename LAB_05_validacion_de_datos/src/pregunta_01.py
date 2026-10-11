import json
import re
from pathlib import Path

import pandas as pd

ACTIVIDAD = Path(__file__).resolve().parents[1]
ARCHIVO = ACTIVIDAD / "data" / "ventas.csv.gz"
REPORTE = ACTIVIDAD / "submission" / "data_quality_report.json"

COLUMNAS_REQUERIDAS = [
    "supplier_id",
    "supplier",
    "country",
    "city",
    "purchase_date",
    "amount",
    "discount",
    "weight",
    "units",
    "unit_price",
    "contact_email",
]

# usuario@dominio.extension, sin espacios y con una extension de al menos dos
# letras.
PATRON_DE_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")

FALTANTES = ["", "N/A"]


def normalizar_encabezado(nombre):
    """Quita la marca BOM y los espacios sobrantes, y une las palabras con `_`."""

    return nombre.replace("﻿", "").strip().lower().replace(" ", "_")


def es_faltante(columna):
    """Marca como faltantes las celdas vacias y las que dicen `N/A`."""

    return columna.str.strip().isin(FALTANTES)


def es_unidad_invalida(valor):
    """Indica si el valor es numerico pero no es un entero positivo.

    Un texto que no representa un numero no cuenta aqui: el enunciado pide
    revisar solo los valores numericos.
    """

    try:
        numero = float(valor)
    except ValueError:
        return False

    return numero <= 0 or numero != int(numero)


def main():
    """
    Antes de limpiar o analizar un conjunto de datos, un analista debe
    documentar qué problemas tiene. En este laboratorio usted no va a limpiar
    `data/ventas.csv.gz`: va a construir un reporte de calidad que deje evidencia
    de sus problemas, tal como están en el archivo.

    Lea `data/ventas.csv.gz` sin modificar sus valores. Para trabajar con los
    encabezados, normalícelos: páselos a minúsculas, elimine los espacios al
    inicio y al final (y cualquier marca BOM) y reemplace los espacios
    internos por `_`. Las columnas requeridas son `supplier_id`, `supplier`,
    `country`, `city`, `purchase_date`, `amount`, `discount`, `weight`,
    `units`, `unit_price` y `contact_email`.

    Escriba el reporte en `submission/data_quality_report.json` con estas
    claves:

    - `row_count`: cantidad de filas de datos.
    - `column_count`: cantidad de columnas.
    - `missing_required_columns`: lista ordenada de columnas requeridas que no
      están en el archivo.
    - `unexpected_columns`: lista ordenada de columnas del archivo que no son
      requeridas.
    - `duplicate_row_count`: cantidad de filas idénticas a una fila anterior.
    - `duplicate_supplier_id_row_count`: cantidad de filas cuyo `supplier_id`
      aparece más de una vez (cuente todas esas filas, no solo las
      repetidas).
    - `missing_value_count_by_column`: diccionario con la cantidad de valores
      faltantes de cada columna. Considere faltantes las celdas vacías y las
      que contienen `N/A`.
    - `invalid_email_count`: cantidad de valores de `contact_email` que no
      tienen la forma `usuario@dominio.extension`.
    - `invalid_unit_count`: cantidad de valores numéricos de `units` que no son
      enteros positivos. Los valores faltantes no se cuentan aquí.
    - `country_values`: lista ordenada de los valores distintos de `country`,
      escritos exactamente como aparecen en el archivo.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "row_count": 103,
          "column_count": 11,
          "missing_required_columns": [],
          ...
          "country_values": [" Colombia ", "CO", ...]
        }
    """

    # `dtype=str` y `keep_default_na=False` dejan los valores tal como estan
    # escritos en el archivo: el proposito es diagnosticar, no limpiar.
    ventas = pd.read_csv(ARCHIVO, dtype=str, keep_default_na=False)
    ventas.columns = [normalizar_encabezado(c) for c in ventas.columns]

    columnas = list(ventas.columns)

    unidades = ventas["units"]
    unidades_presentes = unidades[~es_faltante(unidades)]

    correos = ventas["contact_email"]

    reporte = {
        "row_count": len(ventas),
        "column_count": len(columnas),
        "missing_required_columns": sorted(
            set(COLUMNAS_REQUERIDAS) - set(columnas)
        ),
        "unexpected_columns": sorted(set(columnas) - set(COLUMNAS_REQUERIDAS)),
        "duplicate_row_count": int(ventas.duplicated().sum()),
        "duplicate_supplier_id_row_count": int(
            ventas.duplicated(subset=["supplier_id"], keep=False).sum()
        ),
        "missing_value_count_by_column": {
            columna: int(es_faltante(ventas[columna]).sum()) for columna in columnas
        },
        "invalid_email_count": int(
            sum(1 for correo in correos if not PATRON_DE_CORREO.match(correo))
        ),
        "invalid_unit_count": int(
            sum(1 for valor in unidades_presentes if es_unidad_invalida(valor))
        ),
        "country_values": sorted(ventas["country"].unique()),
    }

    REPORTE.parent.mkdir(exist_ok=True)
    REPORTE.write_text(
        json.dumps(reporte, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return reporte
