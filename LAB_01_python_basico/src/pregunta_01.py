from .lectura import cargar_registros


def pregunta_01():
    """
    Calcule la suma de los valores de la segunda columna (`value`) del
    archivo `data/data.csv.gz` y retorne el resultado como un número entero.

    Ejemplo del formato de la respuesta:

        214
    """

    registros = cargar_registros()

    return sum(value for _, value, _, _, _ in registros)
