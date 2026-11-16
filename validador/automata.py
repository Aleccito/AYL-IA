"""AFD genérico: no conoce ningún formato concreto."""


class AFD:
    def __init__(self, estados, alfabeto, transiciones, inicial, aceptacion, clasificador):
        self.estados = estados            # conjunto de nombres de estado
        self.alfabeto = alfabeto          # conjunto de clases de símbolo
        self.transiciones = transiciones  # dict (estado, clase) -> estado
        self.inicial = inicial
        self.aceptacion = aceptacion      # conjunto de estados finales
        self.clasificador = clasificador  # función símbolo -> clase

    def transicion(self, estado, simbolo):
        """Estado destino, o None si no hay transición."""
        return self.transiciones.get((estado, self.clasificador(simbolo)))

    def acepta(self, cadena):
        estado = self.inicial
        for simbolo in cadena:
            estado = self.transicion(estado, simbolo)
            if estado is None:
                return False
        return estado in self.aceptacion
