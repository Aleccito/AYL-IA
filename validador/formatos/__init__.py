"""Registro de formatos: un módulo por formato, todos expuestos en FORMATOS."""
from . import cedula, correo, ipv4, placa, telefono
from .base import Formato

FORMATOS = {f.nombre: f for f in (correo.FORMATO, cedula.FORMATO, ipv4.FORMATO,
                                  placa.FORMATO, telefono.FORMATO)}

__all__ = ["FORMATOS", "Formato"]
