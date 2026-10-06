from .lectura import cargar_registros


def pregunta_04():
    """
    Cuente cuántos registros hay en cada mes, usando la fecha de la tercera
    columna (`date`). Represente el mes como un texto de dos dígitos y retorne
    una lista de tuplas `(mes, cantidad)` ordenada por el mes.

    Ejemplo del formato de la respuesta:

        [("01", 3), ("02", 4), ("03", 2), ...]
    """

    conteo = {}

    for _, _, date, _, _ in cargar_registros():
        mes = date.split("-")[1]
        conteo[mes] = conteo.get(mes, 0) + 1

    return sorted(conteo.items())
