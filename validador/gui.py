"""Interfaz Tkinter: validación, traza y diagrama animado del AFD."""
import tkinter as tk
from collections import defaultdict, deque
from tkinter import ttk

from formatos import FORMATOS
from simulador import simular

R = 18  # radio de los estados


def _distribuir(afd):
    """Posiciones (x, y) por capas BFS desde el estado inicial."""
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
        pos[q] = (50 + capa[q] * 95, 45 + filas[capa[q]] * 70)
        filas[capa[q]] += 1
    return pos, capa


class App:
    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title("Validador de formatos con AFD")
        self.resultado = None
        self.paso = 0
        self.cadena_sim = None
        self.idx_ejemplo = {"v": 0, "i": 0}

        sup = ttk.Frame(raiz, padding=6)
        sup.pack(fill="x")
        ttk.Label(sup, text="Formato:").pack(side="left")
        self.combo = ttk.Combobox(sup, values=list(FORMATOS), state="readonly", width=12)
        self.combo.current(0)
        self.combo.pack(side="left", padx=4)
        self.combo.bind("<<ComboboxSelected>>", lambda e: self._cambiar_formato())
        self.entrada = ttk.Entry(sup, width=32)
        self.entrada.pack(side="left", padx=4)
        self.entrada.bind("<Return>", lambda e: self.validar())
        for texto, cmd in [("Validar", self.validar), ("Paso siguiente", self.siguiente),
                           ("Reiniciar", self.reiniciar),
                           ("Ejemplo válido", lambda: self.ejemplo("v")),
                           ("Ejemplo inválido", lambda: self.ejemplo("i"))]:
            ttk.Button(sup, text=texto, command=cmd).pack(side="left", padx=2)

        self.veredicto = ttk.Label(raiz, text="—", font=("Segoe UI", 14, "bold"), padding=6)
        self.veredicto.pack(fill="x")
        self.detalle = ttk.Label(raiz, text="", foreground="#a00", padding=(6, 0))
        self.detalle.pack(fill="x")

        medio = ttk.Frame(raiz, padding=6)
        medio.pack(fill="both", expand=True)
        cols = ("pos", "simbolo", "desde", "hacia")
        self.tabla = ttk.Treeview(medio, columns=cols, show="headings", height=14)
        for c, t, w in zip(cols, ("Posición", "Símbolo", "Desde", "Hacia"), (70, 60, 70, 70)):
            self.tabla.heading(c, text=t)
            self.tabla.column(c, width=w, anchor="center")
        self.tabla.pack(side="left", fill="y")

        marco = ttk.Frame(medio)
        marco.pack(side="left", fill="both", expand=True, padx=(6, 0))
        self.canvas = tk.Canvas(marco, bg="white", width=760, height=420,
                                scrollregion=(0, 0, 760, 420))
        sx = ttk.Scrollbar(marco, orient="horizontal", command=self.canvas.xview)
        sy = ttk.Scrollbar(marco, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=sx.set, yscrollcommand=sy.set)
        sx.pack(side="bottom", fill="x")
        sy.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self._cambiar_formato()

    # ------------------------------------------------------------ helpers
    @property
    def formato(self):
        return FORMATOS[self.combo.get()]

    def _cambiar_formato(self):
        self.pos, _ = _distribuir(self.formato.afd)
        self.reiniciar()

    def _estado_actual(self):
        if self.resultado is None or self.paso == 0:
            return self.formato.afd.inicial
        return self.resultado.traza[self.paso - 1][3]

    def _simular(self):
        self.cadena_sim = self.entrada.get()
        self.resultado = simular(self.formato.afd, self.cadena_sim)

    # ------------------------------------------------------------ acciones
    def validar(self):
        self._simular()
        self.paso = len(self.resultado.traza)
        self._refrescar()

    def siguiente(self):
        if self.resultado is None or self.cadena_sim != self.entrada.get():
            self._simular()
            self.paso = 0
        elif self.paso < len(self.resultado.traza):
            self.paso += 1
        self._refrescar()

    def reiniciar(self):
        self.resultado = None
        self.paso = 0
        self._refrescar()

    def ejemplo(self, tipo):
        lista = self.formato.ejemplos_validos if tipo == "v" else self.formato.ejemplos_invalidos
        i = self.idx_ejemplo[tipo] % len(lista)
        self.idx_ejemplo[tipo] += 1
        self.entrada.delete(0, "end")
        self.entrada.insert(0, lista[i])
        self.validar()

    # ------------------------------------------------------------ dibujo
    def _refrescar(self):
        r = self.resultado
        self.tabla.delete(*self.tabla.get_children())
        terminado = r is not None and self.paso == len(r.traza)
        if r is not None:
            for fila in r.traza[:self.paso]:
                self.tabla.insert("", "end", values=fila)
        if terminado and r.aceptada:
            self.veredicto.config(text="✅ ACEPTADA", foreground="#080")
        elif terminado:
            self.veredicto.config(text="❌ RECHAZADA", foreground="#a00")
        else:
            self.veredicto.config(text="—", foreground="black")
        self.detalle.config(text=r.error[1] if terminado and r.error else "")
        color = "#ffd54f"
        if terminado:
            color = "#9ccc65" if r.aceptada else "#ef9a9a"
        self._dibujar(color)

    def _dibujar(self, color_actual):
        c = self.canvas
        c.delete("all")
        afd = self.formato.afd
        pos = self.pos
        actual = self._estado_actual()

        aristas = defaultdict(list)
        for (o, cls), d in sorted(afd.transiciones.items()):
            if o in pos:
                aristas[(o, d)].append(cls)
        for (o, d), clases in aristas.items():
            etiqueta = ",".join(clases)
            x1, y1 = pos[o]
            if o == d:
                c.create_arc(x1 - 12, y1 - R - 22, x1 + 12, y1 - R + 4, start=-30, extent=240,
                             style="arc")
                c.create_text(x1, y1 - R - 28, text=etiqueta, font=("Segoe UI", 7))
                continue
            x2, y2 = pos[d]
            dx, dy = x2 - x1, y2 - y1
            n = (dx * dx + dy * dy) ** 0.5
            ux, uy = dx / n, dy / n
            ax, ay, bx, by = x1 + ux * R, y1 + uy * R, x2 - ux * R, y2 - uy * R
            if (d, o) in aristas:  # par bidireccional: curvar
                mx, my = (ax + bx) / 2 - uy * 18, (ay + by) / 2 + ux * 18
                c.create_line(ax, ay, mx, my, bx, by, smooth=True, arrow="last")
            else:
                mx, my = (ax + bx) / 2, (ay + by) / 2
                c.create_line(ax, ay, bx, by, arrow="last")
            c.create_text(mx, my - 7, text=etiqueta, font=("Segoe UI", 7), fill="#235")

        for q, (x, y) in pos.items():
            relleno = color_actual if q == actual else "white"
            c.create_oval(x - R, y - R, x + R, y + R, fill=relleno, width=2 if q == actual else 1)
            if q in afd.aceptacion:
                c.create_oval(x - R + 4, y - R + 4, x + R - 4, y + R - 4)
            c.create_text(x, y, text=q, font=("Segoe UI", 8))
        x0, y0 = pos[afd.inicial]
        c.create_line(x0 - R - 25, y0, x0 - R, y0, arrow="last")
        c.configure(scrollregion=c.bbox("all") and (0, 0, c.bbox("all")[2] + 30, c.bbox("all")[3] + 30))


def main():
    raiz = tk.Tk()
    App(raiz)
    raiz.mainloop()
