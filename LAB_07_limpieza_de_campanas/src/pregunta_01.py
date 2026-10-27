from pathlib import Path

import pandas as pd

CARPETA_LAB = Path(__file__).resolve().parents[1]
CARPETA_DATOS = CARPETA_LAB / "data"
CARPETA_SALIDA = CARPETA_LAB / "submission"

MESES = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
    "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12",
}


def leer_campana() -> pd.DataFrame:
    archivos = sorted(CARPETA_DATOS.glob("bank-marketing-campaing-*.csv.gz"))
    return pd.concat([pd.read_csv(archivo) for archivo in archivos], ignore_index=True)


def indicador(columna: pd.Series, valor: str) -> pd.Series:
    return (columna == valor).astype(int)


def construir_fecha(meses: pd.Series, dias: pd.Series) -> pd.Series:
    return "2022-" + meses.map(MESES) + "-" + dias.astype(int).astype(str).str.zfill(2)


def clean_campaign_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Los datos de una campaña de mercadeo bancario llegaron repartidos en diez
    archivos comprimidos, `data/bank-marketing-campaing-*.csv.gz`, con
    información mezclada del cliente, de la campaña y del contexto económico.
    Su tarea es leerlos directamente desde los archivos comprimidos, sin
    descomprimirlos a mano, y separarlos en tres tablas limpias.

    Guarde cada tabla como un CSV sin comprimir en `submission/`, sin el índice
    de Pandas y con las columnas en el orden indicado:

    1. `client.csv`: `client_id`, `age`, `job`, `marital`, `education`,
       `credit_default` y `mortgage`.
       - En `job`, elimine los puntos y cambie los guiones por guiones bajos.
       - En `education`, cambie los puntos por guiones bajos y deje el valor
         `unknown` como faltante.
       - En `credit_default` y `mortgage`, escriba 1 si el valor es `yes` y 0
         en cualquier otro caso.

    2. `campaign.csv`: `client_id`, `number_contacts`, `contact_duration`,
       `previous_campaign_contacts`, `previous_outcome`, `campaign_outcome` y
       `last_contact_date`.
       - En `previous_outcome`, escriba 1 si el valor es `success` y 0 en
         cualquier otro caso.
       - En `campaign_outcome`, escriba 1 si el valor es `yes` y 0 en
         cualquier otro caso.
       - Construya `last_contact_date` a partir de las columnas `month` y
         `day`, usando el año 2022 y el formato `AAAA-MM-DD`.

    3. `economics.csv`: `client_id`, `cons_price_idx` y
       `euribor_three_months`.

    La función también debe retornar las tres tablas, en el orden `client`,
    `campaign` y `economics`.

    Ejemplo del formato de `campaign.csv`:

        client_id,number_contacts,contact_duration,...,last_contact_date
        0,1,261,...,2022-05-13
        ...
    """

    datos = leer_campana()

    client = datos[["client_id", "age", "job", "marital", "education", "credit_default", "mortgage"]].copy()
    client["job"] = client["job"].str.replace(".", "", regex=False).str.replace("-", "_", regex=False)
    client["education"] = client["education"].str.replace(".", "_", regex=False).replace("unknown", pd.NA)
    client["credit_default"] = indicador(client["credit_default"], "yes")
    client["mortgage"] = indicador(client["mortgage"], "yes")

    campaign = datos[["client_id", "number_contacts", "contact_duration", "previous_campaign_contacts"]].copy()
    campaign["previous_outcome"] = indicador(datos["previous_outcome"], "success")
    campaign["campaign_outcome"] = indicador(datos["campaign_outcome"], "yes")
    campaign["last_contact_date"] = construir_fecha(datos["month"], datos["day"])

    economics = datos[["client_id", "cons_price_idx", "euribor_three_months"]].copy()

    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    client.to_csv(CARPETA_SALIDA / "client.csv", index=False)
    campaign.to_csv(CARPETA_SALIDA / "campaign.csv", index=False)
    economics.to_csv(CARPETA_SALIDA / "economics.csv", index=False)

    return client, campaign, economics
