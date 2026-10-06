from .lectura import cargar_registros


def pregunta_11():
    """
    La cuarta columna (`codes`) contiene letras minúsculas separadas por
    comas. Para cada una de esas letras, sume los valores de la segunda
    columna (`value`) de los registros en los que aparece. Retorne un
    diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"a": 122, "b": 49, "c": 91, ...}
    """

    sumas = {}

    for _, value, _, codes, _ in cargar_registros():
        for codigo in codes:
            sumas[codigo] = sumas.get(codigo, 0) + value

    return {codigo: sumas[codigo] for codigo in sorted(sumas)}
