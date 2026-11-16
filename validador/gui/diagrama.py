"""Diagrama del AFD: cálculo de la disposición (puro) y dibujo en un Canvas."""
from collections import defaultdict, deque

from .tema import (AMBAR, ARISTA, ACENTO, ETIQUETA, FUENTE, PANEL, PANEL_ALT, SOBRE_ACENTO,
                   TENUE, TEXTO)

R = 20  # radio de los estados
BADGE = 8  # radio de las insignias numéricas


# ---------------------------------------------------------------- cálculo
def distribuir(afd):
    """Posiciones (x, y) por capas BFS desde el estado inicial, y la capa de cada estado."""
    capa = {afd.inicial: 0}
    cola = deque([afd.inicial])
    while cola:
        q = cola.popleft()
        for (o, _), d in sorted(afd.transiciones.items()):
            if o == q and d not in capa:
                capa[d] = capa[q] + 1
                cola.append(d)
    filas = defaultdict(int)
    pos = {}
    for q in sorted(capa, key=lambda s: (capa[s], s)):
        pos[q] = (70 + capa[q] * 120, 95 + filas[capa[q]] * 95)
        filas[capa[q]] += 1
    return pos, capa


def agrupar_aristas(afd, pos, capa):
    """(aristas, numero, orden): clases por (origen, destino), nº de flecha y orden estable."""
    aristas = defaultdict(list)
    for (o, cls), d in sorted(afd.transiciones.items()):
        if o in pos:
            aristas[(o, d)].append(cls)
    orden = sorted(aristas, key=lambda od: (capa[od[0]], od[0], capa[od[1]], od[1]))
    numero = {od: i for i, od in enumerate(orden, 1)}
    return aristas, numero, orden


def _rango_compacto(chars):
    """Comprime corridas consecutivas de dígitos o letras: 0 1 2 3 -> 0-3."""
    out, i = [], 0
    while i < len(chars):
        j = i
        while (j + 1 < len(chars) and chars[i].isalnum()
               and ord(chars[j + 1]) == ord(chars[j]) + 1
               and chars[j + 1].isdigit() == chars[i].isdigit()
               and chars[j + 1].isalpha() == chars[i].isalpha()):
            j += 1
        if j - i >= 2:
            out.append(f"{chars[i]}-{chars[j]}")
        else:
            out.extend(chars[i:j + 1])
        i = j + 1
    return " ".join("espacio" if c == " " else c for c in out)


def clases_simbolo(afd):
    """Clase -> caracteres ASCII imprimibles que abarca (OTRO = cualquier otro)."""
    grupos = defaultdict(list)
    for k in range(32, 127):
        grupos[afd.clasificador(chr(k))].append(chr(k))
    return {cls: "cualquier otro" if cls == "OTRO" else _rango_compacto(grupos[cls])
            for cls in sorted(grupos, key=lambda c: (c == "OTRO", c))}


# ---------------------------------------------------------------- dibujo
class Diagrama:
    def __init__(self, canvas):
        self.canvas = canvas
        self.afd = None

    def cargar(self, afd):
        """Calcula la disposición para un AFD nuevo."""
        self.afd = afd
        self.pos, capa = distribuir(afd)
        self.aristas, self.numero, self.orden = agrupar_aristas(afd, self.pos, capa)

    def dibujar(self, actual, color_actual, tomada=None):
        """actual: estado resaltado; tomada: (origen, destino) de la flecha del último paso."""
        c = self.canvas
        c.delete("all")
        self._aristas(tomada)
        self._estados(actual, color_actual)
        x0, y0 = self.pos[self.afd.inicial]
        c.create_line(x0 - R - 30, y0, x0 - R, y0, arrow="last", fill=ACENTO, width=2)
        c.tag_raise("etiqueta")
        self._leyenda(color_actual)
        x2, y2 = c.bbox("all")[2:]
        c.configure(scrollregion=(0, 0, x2 + 30, y2 + 30))

    def _aristas(self, tomada):
        for (o, d) in self.aristas:
            n = self.numero[(o, d)]
            es = (o, d) == tomada
            if o == d:
                self._bucle(o, n, es)
            else:
                self._flecha(o, d, n, es)

    def _bucle(self, o, n, es):
        x, y = self.pos[o]
        col, ancho = (AMBAR, 3) if es else (ARISTA, 1.5)
        self.canvas.create_arc(x - 13, y - R - 24, x + 13, y - R + 4, start=-30, extent=240,
                               style="arc", outline=col, width=ancho)
        self._insignia(x, y - R - 24 - BADGE, n, es)

    def _flecha(self, o, d, n, es):
        c = self.canvas
        col, ancho = (AMBAR, 3) if es else (ARISTA, 1.5)
        x1, y1 = self.pos[o]
        x2, y2 = self.pos[d]
        dx, dy = x2 - x1, y2 - y1
        dist = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / dist, dy / dist
        ax, ay, bx, by = x1 + ux * R, y1 + uy * R, x2 - ux * R, y2 - uy * R
        off = 22 if (d, o) in self.aristas else 0
        if off:  # par bidireccional: curvar
            cx, cy = (ax + bx) / 2 - uy * off, (ay + by) / 2 + ux * off
            c.create_line(ax, ay, cx, cy, bx, by, smooth=True, arrow="last",
                          fill=col, width=ancho, arrowshape=(9, 11, 4))
        else:
            c.create_line(ax, ay, bx, by, arrow="last", fill=col, width=ancho,
                          arrowshape=(9, 11, 4))
        # desliza la insignia a lo largo de la flecha hasta que no tape un estado
        for t in (0.5, 0.4, 0.6, 0.3, 0.7, 0.2, 0.8, 0.15, 0.85, 0.1, 0.9):
            k = 2 * t * (1 - t) * off  # desplazamiento de la curva en t
            mx, my = ax + (bx - ax) * t - uy * k, ay + (by - ay) * t + ux * k
            if self._libre(mx, my):
                break
        self._insignia(mx, my, n, es)

    def _estados(self, actual, color_actual):
        c = self.canvas
        for q, (x, y) in self.pos.items():
            es_actual = q == actual
            c.create_oval(x - R, y - R, x + R, y + R, fill=color_actual if es_actual else PANEL,
                          outline=TEXTO if es_actual else ACENTO, width=3 if es_actual else 1.5)
            if q in self.afd.aceptacion:
                c.create_oval(x - R + 4, y - R + 4, x + R - 4, y + R - 4,
                              outline=SOBRE_ACENTO if es_actual else ACENTO)
            c.create_text(x, y, text=q, font=(FUENTE, 9, "bold"),
                          fill=SOBRE_ACENTO if es_actual else TEXTO)

    def _insignia(self, x, y, n, tomada):
        """Número de la flecha dentro de una pequeña insignia redondeada."""
        c = self.canvas
        rx = BADGE if n < 10 else BADGE + 3
        rid = c.create_oval(x - rx, y - BADGE, x + rx, y + BADGE,
                            fill=AMBAR if tomada else PANEL_ALT,
                            outline=AMBAR if tomada else ETIQUETA)
        tid = c.create_text(x, y, text=str(n), font=(FUENTE, 8, "bold"),
                            fill=SOBRE_ACENTO if tomada else ETIQUETA)
        for i in (rid, tid):
            c.addtag_withtag("etiqueta", i)
            c.addtag_withtag("insignia", i)

    def _libre(self, x, y):
        """True si una insignia centrada en (x, y) no toca ningún estado."""
        m = R + BADGE + 4
        return not any(abs(x - px) < m and abs(y - py) < m for px, py in self.pos.values())

    def _leyenda(self, color_actual):
        """Leyenda breve en la esquina superior izquierda del diagrama."""
        c = self.canvas
        x, y, f = 12, 10, (FUENTE, 8)
        c.create_oval(x, y, x + 12, y + 12, outline=ACENTO)
        c.create_text(x + 16, y + 6, text="estado", anchor="w", font=f, fill=TENUE)
        x += 70
        c.create_oval(x, y, x + 12, y + 12, outline=ACENTO)
        c.create_oval(x + 3, y + 3, x + 9, y + 9, outline=ACENTO)
        c.create_text(x + 16, y + 6, text="aceptación", anchor="w", font=f, fill=TENUE)
        x += 95
        c.create_line(x, y + 6, x + 18, y + 6, arrow="last", fill=ACENTO, width=2)
        c.create_text(x + 22, y + 6, text="inicial", anchor="w", font=f, fill=TENUE)
        x += 70
        c.create_oval(x, y, x + 12, y + 12, fill=color_actual, outline=TEXTO)
        c.create_text(x + 16, y + 6, text="estado actual (ámbar; verde/rojo al terminar)",
                      anchor="w", font=f, fill=TENUE)
