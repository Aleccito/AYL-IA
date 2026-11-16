"""Regex (referencia) y AFD de cada formato."""
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


def _construir(reglas, inicial, aceptacion, clases, clasificador):
    """reglas: lista de (origen, [clases], destino) -> AFD."""
    trans = {}
    for origen, cls, destino in reglas:
        for c in cls:
            trans[(origen, c)] = destino
    estados = {inicial} | {o for o, _ in trans} | set(trans.values())
    return AFD(estados, set(clases), trans, inicial, set(aceptacion), clasificador)


# ---------------------------------------------------------------- correo
def _clasif_correo(c):
    if c in LETRAS:
        return "LETRA"
    if c in DIGITOS:
        return "DIGITO"
    return c if c in "@.-_" else "OTRO"


def _afd_correo():
    usuario = ["LETRA", "DIGITO", ".", "-", "_"]
    dom = ["LETRA", "DIGITO", "-"]
    reglas = [
        ("q0", usuario, "u"), ("u", usuario, "u"), ("u", ["@"], "a"),
        ("a", dom, "d"), ("d", dom, "d"), ("d", ["."], "p"),
        ("p", dom, "e"), ("e", dom, "e"), ("e", ["."], "p"),
    ]
    return _construir(reglas, "q0", ["e"],
                      ["LETRA", "DIGITO", "@", ".", "-", "_", "OTRO"], _clasif_correo)


# ---------------------------------------------------------------- cédula
def _clasif_cedula(c):
    if c == "0":
        return "CERO"
    if c == "1":
        return "UNO"
    if c in "23":
        return "D2_3"
    if c in "456789":
        return "D4_9"
    return c if c in "PEN-" else "OTRO"


def _afd_cedula():
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
    return _construir(reglas, "q0", [f"u{k}" for k in range(1, 7)],
                      dig + ["P", "E", "N", "-", "OTRO"], _clasif_cedula)


# ---------------------------------------------------------------- IPv4
def _clasif_ip(c):
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


def _afd_ip():
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
    return _construir(reglas, "S1", [f"{n}4" for n in "ABCEFG"],
                      dig + [".", "OTRO"], _clasif_ip)


# ---------------------------------------------------------------- placa
def _clasif_placa(c):
    if c in LETRAS:
        return "LETRA"
    if c in DIGITOS:
        return "DIGITO"
    return "-" if c == "-" else "OTRO"


def _afd_placa():
    reglas = [
        ("p0", ["LETRA"], "p1"), ("p1", ["LETRA"], "p2"),
        ("p2", ["-"], "g"), ("p2", ["DIGITO"], "d1"), ("g", ["DIGITO"], "d1"),
        ("d1", ["DIGITO"], "d2"), ("d2", ["DIGITO"], "d3"), ("d3", ["DIGITO"], "d4"),
    ]
    return _construir(reglas, "p0", ["d4"], ["LETRA", "DIGITO", "-", "OTRO"], _clasif_placa)


# ---------------------------------------------------------------- teléfono
def _clasif_tel(c):
    if c == "6":
        return "SEIS"
    if c in "2345789":
        return "FIJO"
    if c in "01":
        return "D01"
    return "-" if c == "-" else "OTRO"


def _afd_telefono():
    dig = ["SEIS", "FIJO", "D01"]
    reglas = [("t0", ["FIJO"], "f1"), ("t0", ["SEIS"], "m1"),
              ("f3", ["-"], "g"), ("m4", ["-"], "g"), ("g", dig, "h1")]
    for k in (1, 2):
        reglas.append((f"f{k}", dig, f"f{k + 1}"))
    for k in (1, 2, 3):
        reglas.append((f"m{k}", dig, f"m{k + 1}"))
        reglas.append((f"h{k}", dig, f"h{k + 1}"))
    return _construir(reglas, "t0", ["h4"], dig + ["-", "OTRO"], _clasif_tel)


# ---------------------------------------------------------------- registro
_OCTETO = r"(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]?|0)"

FORMATOS = {
    "Correo": Formato(
        "Correo",
        r"[A-Za-z0-9._-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+",
        _afd_correo(),
        ["ana@correo.com", "juan.perez@mail.example.pa", "a_b-c@x-y.org", "u1@d.co",
         "x@a.b.c.d", "A@B.C", "nombre123@dominio.net"],
        ["", "ana", "@correo.com", "ana@", "ana@correo", "ana@@correo.com",
         "ana@correo..com", "ana@correo.", "ana correo@x.com", "ana@cor_reo.com",
         "ñandú@correo.com"],
    ),
    "Cédula": Formato(
        "Cédula",
        r"(?:1[0-3]|[1-9]|PE|E|N)-[0-9]{1,4}-[0-9]{1,6}",
        _afd_cedula(),
        ["8-123-456", "1-1-1", "13-4567-123456", "10-23-4567", "PE-1-234",
         "E-8-12345", "N-12-345", "9-100-1"],
        ["", "0-1-1", "14-1-1", "8-12345-1", "8-123-1234567", "PE-12345-1",
         "X-1-1", "8-123", "8--1", "8-123-", "PE8-1-1", "8_123_456", "pe-1-234",
         "8-１23-456"],
    ),
    "IPv4": Formato(
        "IPv4",
        rf"{_OCTETO}(?:\.{_OCTETO}){{3}}",
        _afd_ip(),
        ["0.0.0.0", "192.168.1.1", "255.255.255.255", "10.0.0.1", "127.0.0.1",
         "1.2.3.4", "249.250.199.99"],
        ["", "256.1.1.1", "1.2.3", "1.2.3.4.5", "01.2.3.4", "1.2.3.", ".1.2.3",
         "1..2.3", "300.1.1.1", "1.2.3.256", "a.b.c.d", "192.168.1.1 ", "00.0.0.0"],
    ),
    "Placa": Formato(
        "Placa",
        r"[A-Za-z]{2}-?[0-9]{4}",
        _afd_placa(),
        ["AB1234", "ab1234", "XY0000", "AB-1234", "zz9999"],
        ["", "A1234", "ABC123", "AB123", "AB12345", "1234AB", "AB--1234",
         "AB 1234", "ÁB1234"],
    ),
    "Teléfono": Formato(
        "Teléfono",
        r"(?:[2-57-9][0-9]{2}|6[0-9]{3})-[0-9]{4}",
        _afd_telefono(),
        ["263-1234", "6123-4567", "300-0000", "800-1234", "6000-0000", "723-9999"],
        ["", "163-1234", "063-1234", "2631234", "63-1234", "6123-456", "263-12345",
         "6123-45678", "26a-1234", "263 1234", "123-4567"],
    ),
}
