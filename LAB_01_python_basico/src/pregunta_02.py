from .lectura import cargar_registros


def pregunta_02():
    """
    Cuente cuántos registros hay para cada letra de la primera columna
    (`letter`). Retorne una lista de tuplas `(letra, cantidad)` ordenada
    alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 8), ("B", 7), ("C", 5), ...]
    """

    conteo = {}

    for letter, _, _, _, _ in cargar_registros():
        conteo[letter] = conteo.get(letter, 0) + 1

    return sorted(conteo.items())
