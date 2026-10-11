from pathlib import Path

import pandas as pd

ACTIVIDAD = Path(__file__).resolve().parents[1]
ARCHIVO = ACTIVIDAD / "data" / "solicitudes_de_credito.csv.gz"
ENTREGA = ACTIVIDAD / "submission" / "solicitudes_de_credito.csv"

COLUMNAS = [
    "sexo",
    "tipo_de_emprendimiento",
    "idea_negocio",
    "barrio",
    "estrato",
    "comuna_ciudadano",
    "fecha_de_beneficio",
    "monto_del_credito",
    "línea_credito",
]

COLUMNAS_DE_TEXTO = [
    "sexo",
    "tipo_de_emprendimiento",
    "idea_negocio",
    "barrio",
    "línea_credito",
]

# La comuna es la unica columna donde un faltante es parte del dato y no un
# error de captura.
COLUMNAS_OBLIGATORIAS = [c for c in COLUMNAS if c != "comuna_ciudadano"]

# El archivo trae las fechas de dos maneras; se prueban en este orden.
FORMATOS_DE_FECHA = ["%d/%m/%Y", "%Y/%m/%d"]


def limpiar_texto(columna):
    """Pasa a minusculas y deja las palabras separadas por un solo espacio.

    En el archivo sucio las palabras vienen unidas con guiones (`soli-diaria`,
    `manrique-central-no.-1`), asi que el guion se vuelve espacio.
    """

    return (
        columna.str.lower()
        .str.replace("-", " ", regex=False)
        .str.replace("_", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


def limpiar_monto(columna):
    """Convierte montos como `$ 1,200,000.00` en el entero 1200000."""

    return (
        columna.astype(str)
        .str.replace(r"[$,\s]", "", regex=True)
        .str.replace(r"\.00$", "", regex=True)
        .astype(float)
        .astype(int)
    )


def unificar_fechas(columna):
    """Lleva las fechas de todos los formatos del archivo a `AAAA-MM-DD`."""

    textos = columna.astype(str)

    fechas = pd.to_datetime(textos, format=FORMATOS_DE_FECHA[0], errors="coerce")

    for formato in FORMATOS_DE_FECHA[1:]:
        fechas = fechas.fillna(
            pd.to_datetime(textos, format=formato, errors="coerce")
        )

    return fechas.dt.strftime("%Y-%m-%d")


def pregunta_01():
    """
    El archivo `data/solicitudes_de_credito.csv.gz` contiene las solicitudes de
    un programa de crédito, pero llegó sucio: tiene una columna de índice que
    no pertenece a los datos, registros duplicados, registros incompletos y
    valores que representan lo mismo escritos de formas distintas en los
    campos de texto, las fechas, el estrato y el monto.

    Su tarea es limpiarlo y guardar el resultado en
    `submission/solicitudes_de_credito.csv`, usando punto y coma (`;`) como
    separador y sin el índice de Pandas.

    El archivo limpio debe cumplir lo siguiente:

    - Contiene solamente las nueve columnas `sexo`, `tipo_de_emprendimiento`,
      `idea_negocio`, `barrio`, `estrato`, `comuna_ciudadano`,
      `fecha_de_beneficio`, `monto_del_credito` y `línea_credito`, en ese
      orden.
    - Los campos de texto están en minúsculas y sus palabras separadas por
      espacios.
    - `estrato` y `monto_del_credito` son números enteros, sin símbolos ni
      separadores de miles.
    - Todas las fechas de `fecha_de_beneficio` usan un mismo formato, por
      ejemplo `AAAA-MM-DD`.
    - No hay registros incompletos. La única excepción es
      `comuna_ciudadano`: sus valores faltantes son parte de los datos
      originales y deben conservarse.
    - No hay registros duplicados.

    Ejemplo del formato del archivo:

        sexo;tipo_de_emprendimiento;idea_negocio;barrio;estrato;...
        femenino;comercio;almacen de ropa en;los cerros el vergel;2;...
        ...
    """

    # `index_col=0` descarta la columna de indice que no pertenece a los datos.
    solicitudes = pd.read_csv(ARCHIVO, sep=";", index_col=0)

    solicitudes = solicitudes.dropna(subset=COLUMNAS_OBLIGATORIAS)

    for columna in COLUMNAS_DE_TEXTO:
        solicitudes[columna] = limpiar_texto(solicitudes[columna])

    solicitudes["estrato"] = solicitudes["estrato"].astype(int)
    solicitudes["comuna_ciudadano"] = solicitudes["comuna_ciudadano"].astype("Int64")
    solicitudes["monto_del_credito"] = limpiar_monto(solicitudes["monto_del_credito"])
    solicitudes["fecha_de_beneficio"] = unificar_fechas(
        solicitudes["fecha_de_beneficio"]
    )

    # Los duplicados se quitan al final: dos filas que solo se diferenciaban
    # en mayusculas, guiones o formato de fecha ya quedaron identicas.
    solicitudes = solicitudes[COLUMNAS].drop_duplicates()

    ENTREGA.parent.mkdir(exist_ok=True)
    solicitudes.to_csv(ENTREGA, sep=";", index=False, encoding="utf-8")

    return solicitudes
