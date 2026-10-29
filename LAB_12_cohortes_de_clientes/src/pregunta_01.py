from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CARPETA = Path(__file__).resolve().parents[1]
ARCHIVO_DATOS = CARPETA / "data" / "sales.csv.gz"
CARPETA_SALIDA = CARPETA / "submission"


def dibujar_mapa(tabla: pd.DataFrame, ruta: Path) -> None:
    # Una fila por cohorte y una columna por período. Las combinaciones que no
    # existen quedan como NaN y se dibujan vacías (no como cero).
    matriz = tabla.pivot(
        index="cohort_month", columns="period_index", values="retention_rate"
    )
    valores = np.ma.masked_invalid(matriz.to_numpy(dtype=float))

    fig, ax = plt.subplots(figsize=(10, 6))
    imagen = ax.imshow(valores, cmap="Blues", vmin=0, vmax=1, aspect="auto")

    for fila in range(matriz.shape[0]):
        for columna in range(matriz.shape[1]):
            valor = matriz.iat[fila, columna]
            if pd.notna(valor):
                ax.text(
                    columna,
                    fila,
                    f"{valor:.0%}",
                    ha="center",
                    va="center",
                    color="white" if valor > 0.5 else "black",
                )

    ax.set_xticks(range(matriz.shape[1]), matriz.columns)
    ax.set_yticks(range(matriz.shape[0]), matriz.index)
    ax.set_xlabel("Meses desde la primera compra (period_index)")
    ax.set_ylabel("Cohorte (mes de la primera compra)")
    ax.set_title("Retención de clientes por cohorte")
    fig.colorbar(imagen, ax=ax, format=matplotlib.ticker.PercentFormatter(1.0))
    fig.tight_layout()
    fig.savefig(ruta, dpi=100)
    plt.close(fig)


def build_cohort_analysis() -> pd.DataFrame:
    """
    Una tienda quiere saber si sus clientes vuelven a comprar después de su
    primera compra. Para responder, agrupe a los clientes en cohortes según
    el mes de su primera compra y mida, mes a mes, qué proporción de cada
    cohorte vuelve a comprar. Use `data/sales.csv.gz`, que tiene una fila por
    orden con su cliente (`CustomerID`) y su fecha (`OrderDate`).

    Use estas definiciones:

    - `cohort_month`: el mes de la primera compra del cliente, escrito como
      `AAAA-MM`.
    - `period_index`: los meses transcurridos desde `cohort_month`; es 0 en el
      mes de la primera compra, 1 en el mes siguiente, y así sucesivamente.
    - `active_customers`: la cantidad de clientes distintos de la cohorte que
      compraron en ese período.
    - `cohort_size`: la cantidad de clientes de la cohorte, es decir, sus
      clientes activos en el período 0.
    - `retention_rate`: `active_customers` sobre `cohort_size`.

    Genere dos archivos en `submission/`:

    1. `cohort_retention.csv`, sin el índice de Pandas, con las columnas
       `cohort_month`, `period_index`, `active_customers`, `cohort_size` y
       `retention_rate`, y una fila por cada combinación cohorte–período
       observada, ordenadas por cohorte y período.

    2. `cohort_retention_heatmap.png`, un mapa de calor de `retention_rate`
       con una fila por cohorte (eje vertical) y una columna por período
       (eje horizontal). Muestre los valores como porcentajes. Los períodos
       que todavía no se pueden observar para una cohorte no significan
       retención cero: déjelos vacíos en el mapa.

    La función también debe retornar la tabla de retención.

    Ejemplo del formato de `cohort_retention.csv`:

        cohort_month,period_index,active_customers,cohort_size,retention_rate
        2022-01,0,100,100,1.0
        2022-01,1,26,100,0.26
        ...
    """

    ventas = pd.read_csv(ARCHIVO_DATOS, usecols=["CustomerID", "OrderDate"])
    ventas["mes_orden"] = pd.to_datetime(ventas["OrderDate"]).dt.to_period("M")

    # La cohorte de cada cliente es el mes de su primera compra.
    ventas["cohorte"] = ventas.groupby("CustomerID")["mes_orden"].transform("min")

    # Meses transcurridos entre la cohorte y el mes de la orden.
    ventas["period_index"] = (
        (ventas["mes_orden"].dt.year - ventas["cohorte"].dt.year) * 12
        + (ventas["mes_orden"].dt.month - ventas["cohorte"].dt.month)
    )
    ventas["cohort_month"] = ventas["cohorte"].dt.strftime("%Y-%m")

    # Clientes distintos que compraron en cada cohorte y período.
    tabla = (
        ventas.groupby(["cohort_month", "period_index"])["CustomerID"]
        .nunique()
        .reset_index(name="active_customers")
        .sort_values(["cohort_month", "period_index"])
        .reset_index(drop=True)
    )

    # El tamaño de la cohorte son sus clientes activos en el período 0.
    tamanos = tabla[tabla["period_index"] == 0].set_index("cohort_month")[
        "active_customers"
    ]
    tabla["cohort_size"] = tabla["cohort_month"].map(tamanos)
    tabla["retention_rate"] = (
        tabla["active_customers"] / tabla["cohort_size"]
    ).round(4)

    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(CARPETA_SALIDA / "cohort_retention.csv", index=False)
    dibujar_mapa(tabla, CARPETA_SALIDA / "cohort_retention_heatmap.png")

    return tabla
