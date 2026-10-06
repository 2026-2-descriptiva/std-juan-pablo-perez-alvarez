"""Lectura de las tablas de la actividad.

Las tres tablas viven en `data/` y están separadas por tabulaciones, así que
se cargan todas con la misma función en lugar de repetir la ruta y el
separador en cada pregunta.
"""

from pathlib import Path

import pandas as pd

CARPETA_DATOS = Path(__file__).resolve().parents[1] / "data"


def cargar(nombre):
    """Retorna la tabla `data/<nombre>.tsv` como un DataFrame de Pandas."""

    return pd.read_csv(CARPETA_DATOS / f"{nombre}.tsv", sep="\t")
