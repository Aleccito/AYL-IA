"""Teléfono de Panamá: +507 NNNN-NNNN."""
from .base import DIGITOS, Formato, construir


def clasificador(c):
    if c in "507":
        return "C" + c
    if c in DIGITOS:
        return "OTRO_DIG"
    return {"+": "MAS", " ": "ESP", "-": "-"}.get(c, "OTRO")


def _afd():
    dig = ["C5", "C0", "C7", "OTRO_DIG"]
    reglas = [("t0", ["MAS"], "t1"), ("t1", ["C5"], "t2"), ("t2", ["C0"], "t3"),
              ("t3", ["C7"], "t4"), ("t4", ["ESP"], "t5"), ("t5", dig, "a1"),
              ("a4", ["-"], "g"), ("g", dig, "b1")]
    for k in (1, 2, 3):
        reglas.append((f"a{k}", dig, f"a{k + 1}"))
        reglas.append((f"b{k}", dig, f"b{k + 1}"))
    return construir(reglas, "t0", ["b4"],
                     dig + ["MAS", "ESP", "-", "OTRO"], clasificador)


FORMATO = Formato(
    "Teléfono",
    r"\+507 [0-9]{4}-[0-9]{4}",
    _afd(),
    ["+507 6123-4567", "+507 2631-2345", "+507 0000-0000", "+507 9999-9999",
     "+507 6000-1111"],
    ["", "6123-4567", "+507 61234567", "+507 6123-456", "+507 6123-45678",
     "+507  6123-4567", "+50 6123-4567", "507 6123-4567", "+507 6123 4567",
     "+507 61a3-4567", "+507 263-1234", "+507 6123-4567 "],
)
