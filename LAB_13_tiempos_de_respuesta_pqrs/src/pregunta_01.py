from pathlib import Path

import numpy as np
import pandas as pd

CARPETA = Path(__file__).resolve().parents[1]
CARPETA_DATOS = CARPETA / "data"
CARPETA_SALIDA = CARPETA / "submission"

CANALES = {
    "letter": "historical_requests_letter.csv.gz",
    "web": "historical_requests_web.csv.gz",
}
PLAZO_DIAS_HABILES = 15
DIAS_SEMANA = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def cargar_solicitudes() -> pd.DataFrame:
    partes = []
    for canal, archivo in CANALES.items():
        datos = pd.read_csv(CARPETA_DATOS / archivo)
        # Las filas idénticas son la misma solicitud repetida; las que no
        # tienen record_id se conservan porque son solicitudes válidas.
        datos = datos.drop_duplicates()
        datos["channel"] = canal
        partes.append(datos)
    solicitudes = pd.concat(partes, ignore_index=True)
    solicitudes["in_date"] = pd.to_datetime(solicitudes["in_date"])
    solicitudes["out_date"] = pd.to_datetime(solicitudes["out_date"])
    return solicitudes


def calcular_tiempos(solicitudes: pd.DataFrame) -> pd.DataFrame:
    solicitudes["answered"] = solicitudes["out_date"].notna()
    respondidas = solicitudes["answered"]

    entrada = solicitudes.loc[respondidas, "in_date"].to_numpy(dtype="datetime64[D]")
    salida = solicitudes.loc[respondidas, "out_date"].to_numpy(dtype="datetime64[D]")

    # Días hábiles: de lunes a viernes después de la entrada, hasta la
    # respuesta incluida. busday_count cuenta [inicio, fin), por eso se
    # corren ambas fechas un día.
    solicitudes["business_days"] = np.nan
    solicitudes.loc[respondidas, "business_days"] = np.busday_count(
        entrada + 1, salida + 1
    )
    solicitudes["calendar_days"] = (
        solicitudes["out_date"] - solicitudes["in_date"]
    ).dt.days

    # Una pendiente no cumple: su business_days es NaN y la comparación da False.
    solicitudes["on_time"] = solicitudes["business_days"] <= PLAZO_DIAS_HABILES
    solicitudes["year"] = solicitudes["in_date"].dt.year
    return solicitudes


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una entidad pública recibe peticiones, quejas, reclamos y sugerencias
    (PQRS) por dos canales, la página web y las cartas, y la ley le da 15 días
    hábiles para responder cada una. Su tarea es medir si la entidad cumple
    ese plazo.

    Los archivos `data/historical_requests_web.csv.gz` y
    `data/historical_requests_letter.csv.gz` tienen una fila por solicitud
    recibida entre 2016 y 2021 por cada canal, con su identificador
    (`record_id`), la fecha de entrada (`in_date`), el día de la semana de
    entrada (`day_name`) y la fecha de respuesta (`out_date`). Si `out_date`
    está vacía, la solicitud todavía no ha sido respondida.

    Tenga en cuenta lo siguiente:

    - Algunas solicitudes aparecen repetidas: elimine las filas idénticas
      dentro de cada canal, para contar cada solicitud una sola vez. Las
      filas sin `record_id` son solicitudes válidas.
    - Llame `letter` al canal de las cartas y `web` al de la página web.
    - Los días hábiles de respuesta son los días de lunes a viernes
      posteriores a la fecha de entrada, hasta la fecha de respuesta
      incluida. Por ejemplo, una solicitud que entra un viernes y se responde
      el lunes siguiente tardó 1 día hábil. No considere los festivos.
    - Los días calendario de respuesta son la diferencia entre la fecha de
      respuesta y la de entrada.
    - Una solicitud cumple el plazo si fue respondida en 15 días hábiles o
      menos. Una solicitud pendiente no ha cumplido el plazo.
    - `on_time_rate` es la proporción de solicitudes que cumplen el plazo,
      sobre el total de solicitudes, incluidas las pendientes.
    - Las medianas de días se calculan solamente con las solicitudes
      respondidas.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `channel_summary.csv`, con una fila por canal, en orden alfabético:
       `channel`, `requests`, `answered`, `pending`,
       `median_business_days` y `on_time_rate`.

    2. `yearly_summary.csv`, con una fila por año de entrada y canal,
       ordenada por año y luego por canal: `year`, `channel`, `requests`,
       `pending` y `on_time_rate`.

    3. `entry_day_summary.csv`, con una fila por día de entrada, de lunes a
       domingo, con los dos canales juntos: `day_name`, `requests`,
       `median_calendar_days` y `median_business_days`.

    Observe en el tercer archivo cómo cambia la lectura del tiempo de
    respuesta según se cuenten días calendario o días hábiles.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `channel_summary.csv`:

        channel,requests,answered,pending,median_business_days,on_time_rate
        letter,28138,...
        ...
    """

    solicitudes = calcular_tiempos(cargar_solicitudes())

    # median() ignora los NaN, así que las medianas salen solo de las respondidas.
    por_canal = (
        solicitudes.groupby("channel")
        .agg(
            requests=("channel", "size"),
            answered=("answered", "sum"),
            median_business_days=("business_days", "median"),
            on_time_rate=("on_time", "mean"),
        )
        .reset_index()
        .sort_values("channel")
    )
    por_canal["pending"] = por_canal["requests"] - por_canal["answered"]
    por_canal = por_canal[
        [
            "channel",
            "requests",
            "answered",
            "pending",
            "median_business_days",
            "on_time_rate",
        ]
    ]

    por_anio = (
        solicitudes.groupby(["year", "channel"])
        .agg(
            requests=("channel", "size"),
            answered=("answered", "sum"),
            on_time_rate=("on_time", "mean"),
        )
        .reset_index()
        .sort_values(["year", "channel"])
    )
    por_anio["pending"] = por_anio["requests"] - por_anio["answered"]
    por_anio = por_anio[["year", "channel", "requests", "pending", "on_time_rate"]]

    por_dia = (
        solicitudes.groupby("day_name")
        .agg(
            requests=("day_name", "size"),
            median_calendar_days=("calendar_days", "median"),
            median_business_days=("business_days", "median"),
        )
        .reindex(DIAS_SEMANA)
        .rename_axis("day_name")
        .reset_index()
    )

    tablas = []
    for tabla in [por_canal, por_anio, por_dia]:
        tabla = tabla.reset_index(drop=True).round(4)
        tablas.append(tabla)

    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    nombres = ["channel_summary.csv", "yearly_summary.csv", "entry_day_summary.csv"]
    for tabla, nombre in zip(tablas, nombres):
        tabla.to_csv(CARPETA_SALIDA / nombre, index=False)

    return tuple(tablas)
