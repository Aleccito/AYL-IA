"""Correo (versión base): usuario@dominio.ext"""
from .base import DIGITOS, LETRAS, Formato, construir


def clasificador(c):
    if c in LETRAS:
        return "LETRA"
    if c in DIGITOS:
        return "DIGITO"
    return c if c in "@.-_" else "OTRO"


def _afd():
    usuario = ["LETRA", "DIGITO", ".", "-", "_"]
    dom = ["LETRA", "DIGITO", "-"]
    reglas = [
        ("q0", usuario, "u"), ("u", usuario, "u"), ("u", ["@"], "a"),
        ("a", dom, "d"), ("d", dom, "d"), ("d", ["."], "p"),
        ("p", dom, "e"), ("e", dom, "e"), ("e", ["."], "p"),
    ]
    return construir(reglas, "q0", ["e"],
                     ["LETRA", "DIGITO", "@", ".", "-", "_", "OTRO"], clasificador)


FORMATO = Formato(
    "Correo",
    r"[A-Za-z0-9._-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+",
    _afd(),
    ["ana@correo.com", "juan.perez@mail.example.pa", "a_b-c@x-y.org", "u1@d.co",
     "x@a.b.c.d", "A@B.C", "nombre123@dominio.net"],
    ["", "ana", "@correo.com", "ana@", "ana@correo", "ana@@correo.com",
     "ana@correo..com", "ana@correo.", "ana correo@x.com", "ana@cor_reo.com",
     "ñandú@correo.com"],
)
