import json
from pathlib import Path

import pandas as pd

CARPETA_LAB = Path(__file__).resolve().parents[1]
ARCHIVO_DATOS = CARPETA_LAB / "data" / "insurance.csv.gz"
CARPETA_SALIDA = CARPETA_LAB / "submission"

K = 5
CUASI_ORIGINALES = ["age", "sex", "bmi", "children", "region"]
ESQUEMAS = {
    "with_children": ["age_group", "sex", "bmi_group", "children_group", "region"],
    "without_children": ["age_group", "sex", "bmi_group", "region"],
}


def generalizar(datos: pd.DataFrame) -> pd.DataFrame:
    datos = datos.copy()
    datos["age_group"] = pd.cut(
        datos["age"], bins=[17, 29, 39, 49, 64], labels=["18-29", "30-39", "40-49", "50-64"]
    ).astype(str)
    datos["bmi_group"] = pd.cut(
        datos["bmi"],
        bins=[float("-inf"), 18.5, 25, 30, float("inf")],
        labels=["bajo peso", "normal", "sobrepeso", "obesidad"],
        right=False,
    ).astype(str)
    datos["children_group"] = pd.cut(
        datos["children"], bins=[-1, 0, 2, float("inf")], labels=["0", "1-2", "3+"]
    ).astype(str)
    return datos


def tamano_de_clase(datos: pd.DataFrame, columnas: list[str]) -> pd.Series:
    """Para cada registro, cuántos registros comparten sus cuasi-identificadores."""
    return datos.groupby(columnas)[columnas[0]].transform("size")


def evaluar_esquema(datos: pd.DataFrame, columnas: list[str]) -> tuple[dict, pd.DataFrame]:
    tamanos = tamano_de_clase(datos, columnas)
    publicados = datos[tamanos >= K]

    fuma_por_clase = publicados.groupby(columnas)["smoker"].agg(["nunique", "size"])
    sin_diversidad = fuma_por_clase[fuma_por_clase["nunique"] == 1]

    resumen = {
        "quasi_identifiers": columnas,
        "equivalence_classes": int(datos.groupby(columnas).ngroups),
        "k_before_suppression": int(tamanos.min()),
        "suppressed_records": int((tamanos < K).sum()),
        "published_records": int(len(publicados)),
        "published_classes": int(len(fuma_por_clase)),
        "classes_without_smoker_diversity": int(len(sin_diversidad)),
        "records_without_smoker_diversity": int(sin_diversidad["size"].sum()),
    }
    return resumen, publicados


def tasa_de_fumadores(datos: pd.DataFrame) -> float:
    return float((datos["smoker"] == "yes").mean())


def pregunta_01():
    """
    Una aseguradora quiere publicar datos de sus afiliados para que un grupo
    de investigación estudie el costo de los seguros, sin que nadie pueda
    reconocer a una persona. El archivo `data/insurance.csv.gz` tiene una fila
    por afiliado con su edad (`age`), sexo (`sex`), índice de masa corporal
    (`bmi`), número de hijos (`children`), si fuma (`smoker`), región
    (`region`) y el costo de su seguro (`charges`).

    El archivo no tiene nombres ni documentos, pero eso no basta: la edad, el
    sexo, el índice de masa corporal, el número de hijos y la región son
    cuasi-identificadores, porque combinados pueden señalar a una persona.
    `smoker` es el atributo sensible que se quiere proteger.

    En este laboratorio usted va a medir el riesgo de reidentificación y a
    decidir qué publicar. Use estas definiciones:

    - Una clase de equivalencia es un grupo de registros con los mismos
      valores en todos los cuasi-identificadores. Un conjunto de datos cumple
      k-anonimato si toda clase tiene al menos k registros. Use k = 5.
    - `age_group`: `18-29`, `30-39`, `40-49` o `50-64`.
    - `bmi_group`: `bajo peso` (menos de 18.5), `normal` (desde 18.5 y menos
      de 25), `sobrepeso` (desde 25 y menos de 30) u `obesidad` (30 o más).
    - `children_group`: `0`, `1-2` o `3+`.

    Evalúe dos esquemas de generalización:

    - `with_children`: `age_group`, `sex`, `bmi_group`, `children_group` y
      `region`.
    - `without_children`: `age_group`, `sex`, `bmi_group` y `region`; el
      número de hijos no se publica.

    En cada esquema, suprima (no publique) los registros de las clases con
    menos de 5 registros. Luego, entre las clases publicadas, identifique las
    que no tienen diversidad en el atributo sensible, es decir, aquellas en
    las que todos los afiliados fuman o ninguno fuma: en esas clases, saber
    que alguien pertenece a ellas revela si fuma.

    Escriba `submission/privacy_report.json` con estas claves:

    - `original_k`: el menor tamaño de clase usando los cuasi-identificadores
      originales, sin generalizar.
    - `original_unique_records`: cuántos registros son los únicos de su clase
      con los cuasi-identificadores originales.
    - `schemes`: un diccionario con una entrada por esquema (`with_children` y
      `without_children`), cada una con las claves `quasi_identifiers` (la
      lista de columnas del esquema), `equivalence_classes` (clases antes de
      suprimir), `k_before_suppression`, `suppressed_records`,
      `published_records`, `published_classes`,
      `classes_without_smoker_diversity` y
      `records_without_smoker_diversity`.
    - `selected_scheme`: el esquema que suprime menos registros.
    - `mean_charges_original` y `mean_charges_published`: el costo promedio
      de todos los afiliados y el de los registros publicados con el esquema
      seleccionado.
    - `smoker_rate_original` y `smoker_rate_published`: la proporción de
      fumadores en ambos casos.

    Escriba también `submission/insurance_published.csv`, sin el índice de
    Pandas, con los registros publicados del esquema seleccionado, en el
    mismo orden del archivo original, y las columnas del esquema seguidas de
    `smoker` y `charges`.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "original_k": 1,
          "original_unique_records": 1330,
          "schemes": {
            "with_children": {
              "quasi_identifiers": ["age_group", "sex", ...],
              "equivalence_classes": 278,
              ...
            },
            ...
          },
          ...
        }
    """

    datos = generalizar(pd.read_csv(ARCHIVO_DATOS))

    tamanos_originales = tamano_de_clase(datos, CUASI_ORIGINALES)

    esquemas, publicados_por_esquema = {}, {}
    for nombre, columnas in ESQUEMAS.items():
        esquemas[nombre], publicados_por_esquema[nombre] = evaluar_esquema(datos, columnas)

    seleccionado = min(esquemas, key=lambda nombre: esquemas[nombre]["suppressed_records"])
    publicados = publicados_por_esquema[seleccionado]

    reporte = {
        "original_k": int(tamanos_originales.min()),
        "original_unique_records": int((tamanos_originales == 1).sum()),
        "schemes": esquemas,
        "selected_scheme": seleccionado,
        "mean_charges_original": float(datos["charges"].mean()),
        "mean_charges_published": float(publicados["charges"].mean()),
        "smoker_rate_original": tasa_de_fumadores(datos),
        "smoker_rate_published": tasa_de_fumadores(publicados),
    }

    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    (CARPETA_SALIDA / "privacy_report.json").write_text(
        json.dumps(reporte, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    publicados[ESQUEMAS[seleccionado] + ["smoker", "charges"]].to_csv(
        CARPETA_SALIDA / "insurance_published.csv", index=False
    )

    return reporte
