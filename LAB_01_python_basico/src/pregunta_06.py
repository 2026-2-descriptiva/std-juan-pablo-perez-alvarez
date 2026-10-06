from .lectura import cargar_registros


def pregunta_06():
    """
    La quinta columna (`metrics`) contiene pares `clave:valor` separados por
    comas. Para cada clave, encuentre el valor mínimo y el valor máximo que
    aparecen en todo el archivo. Retorne una lista de tuplas
    `(clave, mínimo, máximo)` ordenada alfabéticamente por la clave.

    Observe que el orden es mínimo y luego máximo, al contrario de la
    pregunta 5.

    Ejemplo del formato de la respuesta:

        [("aaa", 1, 9), ("bbb", 1, 9), ...]
    """

    maximos = {}
    minimos = {}

    for _, _, _, _, metrics in cargar_registros():
        for clave, valor in metrics:
            if clave not in maximos:
                maximos[clave] = valor
                minimos[clave] = valor
            else:
                maximos[clave] = max(maximos[clave], valor)
                minimos[clave] = min(minimos[clave], valor)

    return [(clave, minimos[clave], maximos[clave]) for clave in sorted(maximos)]
