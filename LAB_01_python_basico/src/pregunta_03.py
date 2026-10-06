from .lectura import cargar_registros


def pregunta_03():
    """
    Sume los valores de la segunda columna (`value`) para cada letra de la
    primera columna (`letter`). Retorne una lista de tuplas `(letra, suma)`
    ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 53), ("B", 36), ("C", 27), ...]
    """

    sumas = {}

    for letter, value, _, _, _ in cargar_registros():
        sumas[letter] = sumas.get(letter, 0) + value

    return sorted(sumas.items())
