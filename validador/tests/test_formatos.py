import re
import unittest

from automata import AFD
from formatos import FORMATOS
from simulador import simular

LIMITE = ["", " ", "  ", "\n", "ñ", "日本語", "１２３", "a" * 5000, "1" * 5000,
          "8-123-456\n", " 8-123-456", "ana@correo.com\n"]


class TestAFDJuguete(unittest.TestCase):
    """Binarios que terminan en 1."""

    def setUp(self):
        t = {("a", "0"): "a", ("a", "1"): "b", ("b", "0"): "a", ("b", "1"): "b"}
        self.afd = AFD({"a", "b"}, {"0", "1"}, t, "a", {"b"},
                       lambda c: c if c in "01" else "OTRO")

    def test_acepta(self):
        self.assertTrue(self.afd.acepta("1"))
        self.assertTrue(self.afd.acepta("0101"))
        self.assertFalse(self.afd.acepta(""))
        self.assertFalse(self.afd.acepta("10"))
        self.assertFalse(self.afd.acepta("12"))

    def test_traza(self):
        r = simular(self.afd, "01")
        self.assertTrue(r.aceptada)
        self.assertEqual(r.traza, [(1, "0", "a", "a"), (2, "1", "a", "b")])
        self.assertIsNone(r.error)

    def test_errores(self):
        r = simular(self.afd, "02")
        self.assertEqual(r.error, (2, "Posición 2: en a no hay transición con '2'"))
        r = simular(self.afd, "10")
        self.assertFalse(r.aceptada)
        self.assertIn("no es de aceptación", r.error[1])


class TestFormatos(unittest.TestCase):
    def test_afd_igual_regex(self):
        for nombre, f in FORMATOS.items():
            casos = f.ejemplos_validos + f.ejemplos_invalidos + LIMITE
            for x in casos:
                with self.subTest(formato=nombre, cadena=x[:30]):
                    esperado = bool(re.fullmatch(f.regex, x))
                    self.assertEqual(f.afd.acepta(x), esperado)
                    self.assertEqual(simular(f.afd, x).aceptada, esperado)

    def test_ejemplos_etiquetados(self):
        for nombre, f in FORMATOS.items():
            for x in f.ejemplos_validos:
                with self.subTest(formato=nombre, cadena=x):
                    self.assertTrue(re.fullmatch(f.regex, x))
            for x in f.ejemplos_invalidos:
                with self.subTest(formato=nombre, cadena=x):
                    self.assertFalse(re.fullmatch(f.regex, x))

    def test_ip_exhaustivo_octeto(self):
        f = FORMATOS["IPv4"]
        for n in range(0, 1000):
            x = f"{n}.1.1.1"
            self.assertEqual(f.afd.acepta(x), n <= 255, x)


if __name__ == "__main__":
    unittest.main()
