"""Placa: 2 letras, '-' opcional, 4 dígitos."""
from .base import DIGITOS, LETRAS, Formato, construir


def clasificador(c):
    if c in LETRAS:
        return "LETRA"
    if c in DIGITOS:
        return "DIGITO"
    return "-" if c == "-" else "OTRO"


def _afd():
    reglas = [
        ("p0", ["LETRA"], "p1"), ("p1", ["LETRA"], "p2"),
        ("p2", ["-"], "g"), ("p2", ["DIGITO"], "d1"), ("g", ["DIGITO"], "d1"),
        ("d1", ["DIGITO"], "d2"), ("d2", ["DIGITO"], "d3"), ("d3", ["DIGITO"], "d4"),
    ]
    return construir(reglas, "p0", ["d4"], ["LETRA", "DIGITO", "-", "OTRO"], clasificador)


FORMATO = Formato(
    "Placa",
    r"[A-Za-z]{2}-?[0-9]{4}",
    _afd(),
    ["AB1234", "ab1234", "XY0000", "AB-1234", "zz9999"],
    ["", "A1234", "ABC123", "AB123", "AB12345", "1234AB", "AB--1234",
     "AB 1234", "ÁB1234"],
)
