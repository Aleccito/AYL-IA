"""Correo (RFC 5321/5322, sin límites de longitud): parte-local@dominio

Parte local: grupos de caracteres atext separados por '.', sin punto al inicio, al final ni doble.
Dominio: etiquetas separadas por '.', sin guion al inicio ni al final de cada etiqueta,
al menos un punto y el último nivel (TLD) con al menos una letra.
No se soportan comillas, IP literal ni Unicode.
"""
from .base import DIGITOS, LETRAS, Formato, construir

SIMBOLOS_LOCAL = "!#$%&'*+/=?^_`{|}~"


def clasificador(c):
    if c in LETRAS:
        return "LETRA"
    if c in DIGITOS:
        return "DIGITO"
    if c in SIMBOLOS_LOCAL:
        return "SIM"
    return c if c in "@.-" else "OTRO"


def _afd():
    atext = ["LETRA", "DIGITO", "-", "SIM"]
    alnum = ["LETRA", "DIGITO"]
    reglas = [
        # parte local
        ("q0", atext, "u"), ("u", atext, "u"), ("u", ["."], "v"), ("v", atext, "u"),
        ("u", ["@"], "a"),
        # primera etiqueta del dominio (no puede ser la última: falta un punto)
        ("a", alnum, "d1"), ("d1", alnum, "d1"), ("d1", ["-"], "g1"),
        ("g1", alnum, "d1"), ("g1", ["-"], "g1"), ("d1", ["."], "p"),
        # etiquetas siguientes: L = tiene letra, N = solo dígitos (y guiones internos)
        ("p", ["LETRA"], "L"), ("p", ["DIGITO"], "N"),
        ("L", alnum, "L"), ("L", ["-"], "gL"), ("L", ["."], "p"),
        ("gL", alnum, "L"), ("gL", ["-"], "gL"),
        ("N", ["DIGITO"], "N"), ("N", ["LETRA"], "L"), ("N", ["-"], "gN"), ("N", ["."], "p"),
        ("gN", ["DIGITO"], "N"), ("gN", ["LETRA"], "L"), ("gN", ["-"], "gN"),
    ]
    return construir(reglas, "q0", ["L"],
                     ["LETRA", "DIGITO", "SIM", "@", ".", "-", "OTRO"], clasificador)


_ATEXT = r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]"
_ETIQUETA = r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
_TLD = r"(?=[0-9-]*[A-Za-z])" + _ETIQUETA  # al menos una letra

FORMATO = Formato(
    "Correo",
    rf"{_ATEXT}+(?:\.{_ATEXT}+)*@(?:{_ETIQUETA}\.)+{_TLD}",
    _afd(),
    ["ana@correo.com", "juan.perez@mail.example.pa", "user+tag@example.com",
     "name/surname@example.com", "a_b-c@x-y.org", "u1@d.co", "x@a.b.c.d", "A@B.C",
     "FirstName.LastName@EasierReading.org", "mailhost!username@example.org",
     "user%example.com@example.org", "!#$%&'*+/=?^_`{|}~@example.com",
     "a@1.com", "a@b-c.d1", "nombre123@dominio.net"],
    ["", "ana", "@correo.com", "ana@", "ana@correo", "ana@@correo.com",
     "ana@correo..com", "ana@correo.", "ana correo@x.com", "ana@cor_reo.com",
     "ñandú@correo.com", "abc.example.com", "a@b@c@example.com", ".ana@x.com",
     "ana.@x.com", "a..b@x.com", "ana@-correo.com", "ana@correo-.com", "ana@a.123",
     "ana@a.-com", "ana@correo.c-", 'a"b(c)d,e:f;g<h>i[j\\k]l@example.com',
     'just"not"right@example.com', "ana@[192.168.2.1]"],
)
