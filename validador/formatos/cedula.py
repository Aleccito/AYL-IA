"""Cédula panameña: provincia 1-13 o PE / E / N, luego -1 a 4 dígitos-1 a 6 dígitos."""
from .base import Formato, construir


def clasificador(c):
    if c == "0":
        return "CERO"
    if c == "1":
        return "UNO"
    if c in "23":
        return "D2_3"
    if c in "456789":
        return "D4_9"
    return c if c in "PEN-" else "OTRO"


def _afd():
    dig = ["CERO", "UNO", "D2_3", "D4_9"]
    reglas = [
        ("q0", ["UNO"], "p1"), ("q0", ["D2_3", "D4_9"], "prov"),
        ("q0", ["P"], "pe1"), ("q0", ["E", "N"], "letra"),
        ("p1", ["CERO", "UNO", "D2_3"], "prov"), ("p1", ["-"], "g1"),
        ("prov", ["-"], "g1"), ("pe1", ["E"], "letra"), ("letra", ["-"], "g1"),
        ("g1", dig, "d1"),
    ]
    for k in range(1, 5):
        if k < 4:
            reglas.append((f"d{k}", dig, f"d{k + 1}"))
        reglas.append((f"d{k}", ["-"], "g2"))
    reglas.append(("g2", dig, "u1"))
    for k in range(1, 6):
        reglas.append((f"u{k}", dig, f"u{k + 1}"))
    return construir(reglas, "q0", [f"u{k}" for k in range(1, 7)],
                     dig + ["P", "E", "N", "-", "OTRO"], clasificador)


FORMATO = Formato(
    "Cédula",
    r"(?:1[0-3]|[1-9]|PE|E|N)-[0-9]{1,4}-[0-9]{1,6}",
    _afd(),
    ["8-123-456", "1-1-1", "13-4567-123456", "10-23-4567", "PE-1-234",
     "E-8-12345", "N-12-345", "9-100-1"],
    ["", "0-1-1", "14-1-1", "8-12345-1", "8-123-1234567", "PE-12345-1",
     "X-1-1", "8-123", "8--1", "8-123-", "PE8-1-1", "8_123_456", "pe-1-234",
     "8-１23-456"],
)
