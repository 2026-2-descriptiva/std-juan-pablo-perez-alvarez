import re
from pathlib import Path

import pandas as pd

ARCHIVO = Path(__file__).resolve().parents[1] / "data" / "clusters_report.txt"

# Una fila nueva empieza con el numero del cluster, su cantidad y su
# porcentaje, y el resto de la linea ya son palabras clave. Las lineas que no
# coinciden con este patron son continuaciones de la fila anterior.
INICIO_DE_CLUSTER = re.compile(r"^\s*(\d+)\s+(\d+)\s+([\d,]+)\s*%\s+(.*)$")


def pregunta_01():
    """
    El archivo `data/clusters_report.txt` es un reporte de clústeres de
    palabras clave pensado para ser leído por una persona, no por un programa:
    los encabezados ocupan varias líneas, las columnas están alineadas con
    espacios y la lista de palabras clave de un clúster continúa en las líneas
    siguientes.

    Su tarea es convertir ese reporte en un DataFrame de Pandas con una fila
    por clúster y las columnas:

    - `cluster`: número del clúster, como entero.
    - `cantidad_de_palabras_clave`: como entero.
    - `porcentaje_de_palabras_clave`: como número decimal; por ejemplo, el
      texto `15,9 %` debe quedar como `15.9`.
    - `principales_palabras_clave`: todas las palabras clave del clúster en un
      solo texto, separadas por una coma y un único espacio.

    Retorne el DataFrame.

    Ejemplo del formato de la respuesta (se omite la última columna):

           cluster  cantidad_de_palabras_clave  porcentaje_de_palabras_clave
        0        1                         105                          15.9
        1        2                         102                          15.4
        ...
    """

    registros = []

    with open(ARCHIVO, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.rstrip()

            if not linea:
                continue

            encontrado = INICIO_DE_CLUSTER.match(linea)

            if encontrado:
                cluster, cantidad, porcentaje, palabras = encontrado.groups()

                registros.append(
                    {
                        "cluster": int(cluster),
                        "cantidad_de_palabras_clave": int(cantidad),
                        "porcentaje_de_palabras_clave": float(
                            porcentaje.replace(",", ".")
                        ),
                        "principales_palabras_clave": [palabras],
                    }
                )

            elif registros:
                # Linea de continuacion: pertenece al ultimo cluster leido.
                registros[-1]["principales_palabras_clave"].append(linea.strip())

    for registro in registros:
        texto = " ".join(registro["principales_palabras_clave"])

        # El reporte justifica el texto con espacios de relleno y cierra la
        # lista con un punto; ninguno de los dos hace parte del dato.
        texto = re.sub(r"\s+", " ", texto).strip().rstrip(".")

        registro["principales_palabras_clave"] = texto

    return pd.DataFrame(registros)
