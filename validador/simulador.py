"""Recorrido paso a paso de un AFD sobre una cadena."""
from typing import NamedTuple, Optional


class Resultado(NamedTuple):
    aceptada: bool
    traza: list                    # [(posicion, simbolo, estado_origen, estado_destino)]
    error: Optional[tuple]         # (posicion, mensaje) o None


def simular(afd, cadena):
    traza = []
    estado = afd.inicial
    for i, simbolo in enumerate(cadena, start=1):
        destino = afd.transicion(estado, simbolo)
        if destino is None:
            msg = f"Posición {i}: en {estado} no hay transición con '{simbolo}'"
            return Resultado(False, traza, (i, msg))
        traza.append((i, simbolo, estado, destino))
        estado = destino
    if estado not in afd.aceptacion:
        msg = f"Fin de cadena: terminó en {estado}, que no es de aceptación"
        return Resultado(False, traza, (len(cadena), msg))
    return Resultado(True, traza, None)
