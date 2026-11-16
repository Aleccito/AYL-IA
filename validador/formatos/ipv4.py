"""IPv4: cuatro octetos 0-255 separados por '.', sin ceros a la izquierda."""
from .base import Formato, construir

_OCTETO = r"(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]?|0)"


def clasificador(c):
    if c == "0":
        return "C0"
    if c == "1":
        return "C1"
    if c == "2":
        return "C2"
    if c in "34":
        return "C3_4"
    if c == "5":
        return "C5"
    if c in "6789":
        return "C6_9"
    return "." if c == "." else "OTRO"


def _afd():
    dig = ["C0", "C1", "C2", "C3_4", "C5", "C6_9"]
    reglas = []
    for k in range(1, 5):
        s = lambda n: f"{n}{k}"
        reglas += [
            (s("S"), ["C0"], s("F")), (s("S"), ["C1"], s("A")),
            (s("S"), ["C2"], s("C")), (s("S"), ["C3_4", "C5", "C6_9"], s("B")),
            (s("A"), dig, s("E")), (s("E"), dig, s("F")), (s("B"), dig, s("F")),
            (s("C"), ["C0", "C1", "C2", "C3_4"], s("E")),
            (s("C"), ["C5"], s("G")), (s("C"), ["C6_9"], s("F")),
            (s("G"), ["C0", "C1", "C2", "C3_4", "C5"], s("F")),
        ]
        if k < 4:
            for n in "ABCEFG":
                reglas.append((s(n), ["."], f"S{k + 1}"))
    return construir(reglas, "S1", [f"{n}4" for n in "ABCEFG"],
                     dig + [".", "OTRO"], clasificador)


FORMATO = Formato(
    "IPv4",
    rf"{_OCTETO}(?:\.{_OCTETO}){{3}}",
    _afd(),
    ["0.0.0.0", "192.168.1.1", "255.255.255.255", "10.0.0.1", "127.0.0.1",
     "1.2.3.4", "249.250.199.99"],
    ["", "256.1.1.1", "1.2.3", "1.2.3.4.5", "01.2.3.4", "1.2.3.", ".1.2.3",
     "1..2.3", "300.1.1.1", "1.2.3.256", "a.b.c.d", "192.168.1.1 ", "00.0.0.0"],
)
