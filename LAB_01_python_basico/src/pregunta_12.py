from .lectura import cargar_registros


def pregunta_12():
    """
    Para cada letra de la primera columna (`letter`), sume todos los valores
    numéricos de los pares `clave:valor` de la quinta columna (`metrics`).
    Retorne un diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"A": 177, "B": 187, "C": 114, ...}
    """

    sumas = {}

    for letter, _, _, _, metrics in cargar_registros():
        for _, valor in metrics:
            sumas[letter] = sumas.get(letter, 0) + valor

    return {letter: sumas[letter] for letter in sorted(sumas)}
