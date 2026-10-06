"""Lectura del archivo de datos de la actividad.

Se usa la misma función en las doce preguntas para no repetir el código que
abre el archivo comprimido y parte cada línea en sus cinco columnas.
"""

import gzip
from pathlib import Path

ARCHIVO = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def cargar_registros():
    """Retorna la lista de registros del archivo.

    Cada registro es una tupla `(letter, value, date, codes, metrics)` donde:

    - `value` ya viene convertido a entero,
    - `codes` es la lista de letras de la cuarta columna,
    - `metrics` es la lista de pares `(clave, valor)` de la quinta columna,
      con el valor convertido a entero.
    """

    registros = []

    with gzip.open(ARCHIVO, "rt", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.rstrip("\n")

            if not linea:
                continue

            letter, value, date, codes, metrics = linea.split("\t")

            pares = []
            for par in metrics.split(","):
                clave, _, valor = par.partition(":")
                pares.append((clave, int(valor)))

            registros.append(
                (
                    letter,
                    int(value),
                    date,
                    codes.split(","),
                    pares,
                )
            )

    return registros
