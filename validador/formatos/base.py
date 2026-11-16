"""Piezas comunes a todos los formatos."""
from dataclasses import dataclass

from automata import AFD

DIGITOS = "0123456789"
LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


@dataclass
class Formato:
    nombre: str
    regex: str
    afd: AFD
    ejemplos_validos: list
    ejemplos_invalidos: list


def construir(reglas, inicial, aceptacion, clases, clasificador):
    """reglas: lista de (origen, [clases], destino) -> AFD."""
    trans = {}
    for origen, cls, destino in reglas:
        for c in cls:
            trans[(origen, c)] = destino
    estados = {inicial} | {o for o, _ in trans} | set(trans.values())
    return AFD(estados, set(clases), trans, inicial, set(aceptacion), clasificador)
