from .lectura import cargar_registros


def pregunta_09():
    """
    Cuente cuántas veces aparece cada clave en la quinta columna (`metrics`)
    de todo el archivo. Retorne un diccionario `{clave: cantidad}` con las
    claves en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"aaa": 13, "bbb": 16, "ccc": 23, ...}
    """

    conteo = {}

    for _, _, _, _, metrics in cargar_registros():
        for clave, _ in metrics:
            conteo[clave] = conteo.get(clave, 0) + 1

    return {clave: conteo[clave] for clave in sorted(conteo)}
