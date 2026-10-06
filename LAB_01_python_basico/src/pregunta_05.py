from .lectura import cargar_registros


def pregunta_05():
    """
    Para cada letra de la primera columna (`letter`), encuentre el valor
    máximo y el valor mínimo de la segunda columna (`value`). Retorne una lista
    de tuplas `(letra, máximo, mínimo)` ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 9, 2), ("B", 9, 1), ...]
    """

    maximos = {}
    minimos = {}

    for letter, value, _, _, _ in cargar_registros():
        if letter not in maximos:
            maximos[letter] = value
            minimos[letter] = value
        else:
            maximos[letter] = max(maximos[letter], value)
            minimos[letter] = min(minimos[letter], value)

    return [(letter, maximos[letter], minimos[letter]) for letter in sorted(maximos)]
