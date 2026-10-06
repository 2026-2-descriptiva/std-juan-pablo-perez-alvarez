from .lectura import cargar


def pregunta_01():
    """
    ¿Cuántos registros tiene la tabla `data/tbl0.tsv`? Retorne la cantidad
    como un número entero.

    Ejemplo del formato de la respuesta:

        40
    """

    tbl0 = cargar("tbl0")

    return tbl0.shape[0]
