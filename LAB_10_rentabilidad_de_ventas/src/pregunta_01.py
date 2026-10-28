from pathlib import Path

import pandas as pd

CARPETA_LAB = Path(__file__).resolve().parents[1]
ARCHIVO_DATOS = CARPETA_LAB / "data" / "superstore_orders.csv.gz"
CARPETA_SALIDA = CARPETA_LAB / "submission"

RANGOS_DESCUENTO = ["0%", "1%-5%", "6%-10%", "más de 10%"]
LINEAS_MINIMAS = 100


def rango_de_descuento(descuento: float) -> str:
    if descuento == 0:
        return "0%"
    if descuento <= 0.05:
        return "1%-5%"
    if descuento <= 0.10:
        return "6%-10%"
    return "más de 10%"


def resumir(grupo: pd.DataFrame) -> dict:
    """Métricas de rentabilidad de un conjunto de líneas de pedido."""
    perdidas = grupo["Profit"] < 0
    ventas = grupo["Sales"].sum()
    utilidad = grupo["Profit"].sum()
    return {
        "lines": len(grupo),
        "orders": grupo["Order ID"].nunique(),
        "sales": round(ventas, 4),
        "profit": round(utilidad, 4),
        "profit_margin": round(utilidad / ventas, 4),
        "loss_lines": int(perdidas.sum()),
        "loss_line_rate": round(perdidas.mean(), 4),
        "lost_profit": round(-grupo.loc[perdidas, "Profit"].sum(), 4),
    }


def resumir_por(datos: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    filas = []
    for claves, grupo in datos.groupby(columnas):
        filas.append({**dict(zip(columnas, claves)), **resumir(grupo)})
    return pd.DataFrame(filas)


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una cadena de suministros de oficina vende mucho, pero la gerencia
    sospecha que parte de esas ventas no deja utilidad. El archivo
    `data/superstore_orders.csv.gz` tiene una fila por línea de pedido, con
    el número de pedido (`Order ID`), las ventas (`Sales`), la utilidad
    (`Profit`), el descuento aplicado (`Discount`, como proporción), el
    segmento del cliente (`Customer Segment`) y la categoría del producto
    (`Product Category`). Una utilidad negativa significa que la línea se
    vendió con pérdida.

    Use estas definiciones:

    - Margen (`profit_margin`): utilidad sobre ventas.
    - Línea con pérdida: una línea cuya utilidad es negativa.
    - `loss_line_rate`: la proporción de líneas con pérdida.
    - `lost_profit`: la suma de las pérdidas de las líneas con pérdida,
      escrita como número positivo.
    - Rango de descuento (`discount_band`): `0%` si no hubo descuento,
      `1%-5%` si fue mayor que 0 y hasta 5 %, `6%-10%` si fue mayor que 5 % y
      hasta 10 %, y `más de 10%` en otro caso.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `profitability_summary.csv`, con una sola fila: `lines` (cantidad de
       líneas), `orders` (pedidos distintos), `sales`, `profit`,
       `profit_margin`, `loss_lines` (cantidad de líneas con pérdida),
       `loss_line_rate` y `lost_profit`.

    2. `discount_summary.csv`, con una fila por rango de descuento, en el
       orden en que se definieron arriba: `discount_band`, `lines`, `sales`,
       `profit`, `profit_margin`, `loss_line_rate` y `lost_profit`.

    3. `priority_segments.csv`, con los cinco segmentos segmento–categoría
       que más utilidad pierden: `Customer Segment`, `Product Category`,
       `lines`, `sales`, `profit`, `profit_margin` y `lost_profit`. Considere
       solamente segmentos con al menos 100 líneas y ordénelos por
       `lost_profit` de mayor a menor.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `discount_summary.csv`:

        discount_band,lines,sales,profit,profit_margin,loss_line_rate,...
        0%,166,170539.05,29472.3789,0.1728,0.488,...
        ...
    """

    datos = pd.read_csv(ARCHIVO_DATOS, sep=";", decimal=",", encoding="utf-8-sig")
    datos["discount_band"] = datos["Discount"].apply(rango_de_descuento)

    profitability = pd.DataFrame([resumir(datos)])

    discounts = resumir_por(datos, ["discount_band"])
    discounts["orden"] = discounts["discount_band"].map(RANGOS_DESCUENTO.index)
    discounts = discounts.sort_values("orden")[
        ["discount_band", "lines", "sales", "profit", "profit_margin", "loss_line_rate", "lost_profit"]
    ]

    segments = resumir_por(datos, ["Customer Segment", "Product Category"])
    segments = (
        segments[segments["lines"] >= LINEAS_MINIMAS]
        .sort_values("lost_profit", ascending=False)
        .head(5)[
            ["Customer Segment", "Product Category", "lines", "sales", "profit", "profit_margin", "lost_profit"]
        ]
    )

    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    profitability.to_csv(CARPETA_SALIDA / "profitability_summary.csv", index=False)
    discounts.to_csv(CARPETA_SALIDA / "discount_summary.csv", index=False)
    segments.to_csv(CARPETA_SALIDA / "priority_segments.csv", index=False)

    return profitability, discounts, segments
