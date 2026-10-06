from .lectura import cargar_registros


def pregunta_08():
    """
    Repita la pregunta 7, pero ahora cada lista de letras debe contener cada
    letra una sola vez y estar ordenada alfabéticamente. Retorne una lista de
    tuplas `(valor, letras)` ordenada por el valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["B", "E"]), (2, ["A", "E"]), ...]
    """

    letras_por_valor = {}

    for letter, value, _, _, _ in cargar_registros():
        letras_por_valor.setdefault(value, set()).add(letter)

    return [(value, sorted(letras_por_valor[value])) for value in sorted(letras_por_valor)]
