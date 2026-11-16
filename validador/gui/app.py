"""Ventana principal: construye los widgets y reacciona a los botones."""
import tkinter as tk
from tkinter import ttk

from formatos import FORMATOS
from simulador import simular

from .diagrama import Diagrama, clases_simbolo
from .tema import (AMBAR, AMBAR_SUAVE, BORDE, ACENTO, ETIQUETA, FONDO, FUENTE, MONO, PANEL,
                   PANEL_ALT, ROJO, SOBRE_ACENTO, TENUE, TEXTO, VERDE, aplicar_estilos,
                   icono_react)

TEXTO_INICIAL = "Escriba una cadena y pulse Validar o Paso siguiente"


def crear_tabla(padre, columnas, encabezados, anchos, anclas=None, **kw):
    """Treeview con columnas de ancho fijo (sin arrastre del separador) y filas alternas."""
    anclas = anclas or ["center"] * len(columnas)
    tabla = ttk.Treeview(padre, columns=columnas, show="headings", **kw)
    for c, t, w, a in zip(columnas, encabezados, anchos, anclas):
        tabla.heading(c, text=t)
        tabla.column(c, width=w, minwidth=w, anchor=a, stretch=False)
    tabla.bind("<Button-1>",
               lambda e: "break" if tabla.identify_region(e.x, e.y) == "separator" else None)
    tabla.tag_configure("par", background=PANEL)
    tabla.tag_configure("impar", background=PANEL_ALT)
    return tabla


class App:
    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title("Validador de formatos con AFD")
        raiz.configure(bg=FONDO)
        self._icono = icono_react()  # referencia para evitar GC
        raiz.iconphoto(True, self._icono)
        aplicar_estilos(raiz)

        self.resultado = None
        self.paso = 0   # filas de la tabla ya reveladas (avance de la simulación)
        self.vista = 0  # fila que se está mostrando en diagrama y lectura (clic en la tabla)
        self.cadena_sim = None
        self.idx_ejemplo = {"v": 0, "i": 0}

        self._crear_barra()
        self._crear_lectura()
        self._crear_veredicto()
        medio = ttk.Frame(raiz, padding=12)
        medio.pack(fill="both", expand=True)
        self._crear_tabla_traza(medio)
        self._crear_paneles_diagrama(medio)
        self._cambiar_formato()

    # ------------------------------------------------------------ construcción
    def _crear_barra(self):
        sup = ttk.Frame(self.raiz, padding=(12, 10))
        sup.pack(fill="x")
        ttk.Label(sup, text="Formato:").pack(side="left")
        self.combo = ttk.Combobox(sup, values=list(FORMATOS), state="readonly", width=12)
        self.combo.current(0)
        self.combo.pack(side="left", padx=6)
        self.combo.bind("<<ComboboxSelected>>", lambda e: self._cambiar_formato())
        ttk.Label(sup, text="Cadena:").pack(side="left", padx=(8, 0))
        self.entrada = ttk.Entry(sup, width=32, font=(MONO, 11))
        self.entrada.pack(side="left", padx=6)
        self.entrada.bind("<Return>", lambda e: self.validar())
        botones = [("Validar", self.validar, "Acento.TButton"),
                   ("Paso siguiente", self.siguiente, "TButton"),
                   ("Reiniciar", self.reiniciar, "TButton"),
                   ("Ejemplo válido", lambda: self.ejemplo("v"), "TButton"),
                   ("Ejemplo inválido", lambda: self.ejemplo("i"), "TButton")]
        for texto, cmd, estilo in botones:
            ttk.Button(sup, text=texto, command=cmd, style=estilo).pack(side="left", padx=3)

    def _crear_lectura(self):
        """Cadena con el símbolo actual resaltado."""
        fila = ttk.Frame(self.raiz, padding=(12, 0))
        fila.pack(fill="x")
        ttk.Label(fila, text="Lectura:").pack(side="left")
        t = self.cadena_txt = tk.Text(fila, height=1, width=60, font=(MONO, 16), bd=0,
                                      bg=FONDO, fg=TEXTO, highlightthickness=0, cursor="arrow")
        t.pack(side="left", fill="x", expand=True, padx=8, pady=4)
        t.tag_configure("leido", foreground=VERDE)
        t.tag_configure("actual", foreground=TEXTO, background=AMBAR_SUAVE)
        t.tag_configure("error", foreground="white", background=ROJO)
        t.tag_configure("resto", foreground=TENUE)

    def _crear_veredicto(self):
        self.veredicto = tk.Label(self.raiz, text=TEXTO_INICIAL, font=(FUENTE, 11, "bold"),
                                  bg=PANEL, fg=TENUE, pady=3, anchor="w", padx=10)
        self.veredicto.pack(fill="x", padx=12, pady=(4, 0))
        self.detalle = tk.Label(self.raiz, text="", font=(FUENTE, 9), bg=FONDO, fg=ROJO,
                                anchor="w", padx=10, pady=0)
        self.detalle.pack(fill="x", padx=12)

    def _crear_tabla_traza(self, padre):
        self.tabla = crear_tabla(padre, ("pos", "simbolo", "desde", "hacia"),
                                 ("Posición", "Símbolo", "Desde", "Hacia"),
                                 (75, 70, 75, 140), height=16)
        self.tabla.tag_configure("ultimo", background=AMBAR_SUAVE, font=(FUENTE, 10, "bold"))
        self.tabla.tag_configure("fallo", foreground=ROJO, font=(FUENTE, 10, "bold"))
        self.tabla.bind("<ButtonRelease-1>", self._clic_traza)
        self.tabla.pack(side="left", fill="y")

    def _crear_paneles_diagrama(self, padre):
        panel = tk.PanedWindow(padre, orient="vertical", bg=FONDO, sashwidth=6, bd=0,
                               sashrelief="flat")
        panel.pack(side="left", fill="both", expand=True, padx=(12, 0))
        panel.add(self._crear_canvas(panel), minsize=200, stretch="always")
        inf = ttk.Frame(panel)
        panel.add(inf, minsize=110, height=160, stretch="never")
        self._crear_significado(inf)
        self._crear_clases(inf)

    def _crear_canvas(self, padre):
        marco = ttk.Frame(padre)
        self.canvas = tk.Canvas(marco, bg=PANEL, width=780, height=340, highlightthickness=1,
                                highlightbackground=BORDE, scrollregion=(0, 0, 780, 340))
        sx = ttk.Scrollbar(marco, orient="horizontal", command=self.canvas.xview)
        sy = ttk.Scrollbar(marco, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=sx.set, yscrollcommand=sy.set)
        sx.pack(side="bottom", fill="x")
        sy.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.diagrama = Diagrama(self.canvas)
        return marco

    def _crear_significado(self, padre):
        """Tabla: qué símbolos lleva cada flecha numerada."""
        izq = ttk.Frame(padre)
        izq.pack(side="left", fill="y")
        ttk.Label(izq, text="Significado de las flechas", foreground=ACENTO,
                  font=(FUENTE, 9, "bold")).pack(anchor="w", pady=(4, 2))
        self.signif = crear_tabla(izq, ("n", "desde", "simbolos", "hacia"),
                                  ("Nº", "Desde", "Símbolos (clases)", "Hacia"),
                                  (40, 65, 260, 65), ("center", "center", "w", "center"),
                                  height=4)
        self.signif.tag_configure("tomada", background=AMBAR_SUAVE, foreground=AMBAR,
                                  font=(FUENTE, 10, "bold"))
        sy = ttk.Scrollbar(izq, orient="vertical", command=self.signif.yview)
        self.signif.configure(yscrollcommand=sy.set)
        sy.pack(side="right", fill="y")
        self.signif.pack(side="left", fill="y", expand=True)

    def _crear_clases(self, padre):
        """Cuadro: qué caracteres reales abarca cada clase de símbolo."""
        der = ttk.Frame(padre)
        der.pack(side="left", fill="both", expand=True, padx=(12, 0))
        ttk.Label(der, text="Clases de símbolo", foreground=ACENTO,
                  font=(FUENTE, 9, "bold")).pack(anchor="w", pady=(4, 2))
        self.clases_txt = tk.Text(der, height=5, width=30, font=(MONO, 9), bg=PANEL, fg=TEXTO,
                                  bd=0, highlightthickness=1, highlightbackground=BORDE,
                                  wrap="word", cursor="arrow")
        self.clases_txt.tag_configure("cls", foreground=ETIQUETA)
        sy = ttk.Scrollbar(der, orient="vertical", command=self.clases_txt.yview)
        self.clases_txt.configure(yscrollcommand=sy.set)
        sy.pack(side="right", fill="y")
        self.clases_txt.pack(side="left", fill="both", expand=True)

    # ------------------------------------------------------------ estado
    @property
    def formato(self):
        return FORMATOS[self.combo.get()]

    def _estado_en(self, k):
        """Estado del autómata tras k pasos reales de la traza."""
        if self.resultado is None or k == 0:
            return self.formato.afd.inicial
        return self.resultado.traza[k - 1][3]

    def _terminado(self):
        return self.resultado is not None and self.paso == len(self.resultado.traza)

    def _filas(self):
        """Filas de la tabla: pasos revelados y, al terminar rechazada, la fila del fallo."""
        r = self.resultado
        if r is None:
            return []
        filas = list(r.traza[:self.paso])
        if self._terminado() and r.error:
            pos, _ = r.error
            estado = self._estado_en(len(r.traza))
            if len(r.traza) < len(self.cadena_sim):
                filas.append((pos, self.cadena_sim[pos - 1], estado, "sin transición"))
            else:
                filas.append((pos, "(fin)", estado, "no es de aceptación"))
        return filas

    def _simular(self):
        self.cadena_sim = self.entrada.get()
        self.resultado = simular(self.formato.afd, self.cadena_sim)

    # ------------------------------------------------------------ acciones
    def _cambiar_formato(self):
        afd = self.formato.afd
        self.diagrama.cargar(afd)
        self._llenar_significado()
        self._llenar_clases(afd)
        self.entrada.delete(0, "end")
        self.reiniciar()

    def validar(self):
        self._simular()
        self.paso = len(self.resultado.traza)
        self.vista = len(self._filas())
        self._refrescar()

    def siguiente(self):
        if self.resultado is None or self.cadena_sim != self.entrada.get():
            self._simular()
            self.paso = 0
        elif self.paso < len(self.resultado.traza):
            self.paso += 1
        self.vista = len(self._filas())
        self._refrescar()

    def reiniciar(self):
        self.resultado = None
        self.paso = 0
        self.vista = 0
        self._refrescar()

    def _clic_traza(self, evento):
        """Clic en una fila: muestra ese paso en el diagrama y en la lectura (aunque falle)."""
        iid = self.tabla.identify_row(evento.y)
        if iid:
            self.vista = int(iid)
            self._refrescar()

    def ejemplo(self, tipo):
        lista = self.formato.ejemplos_validos if tipo == "v" else self.formato.ejemplos_invalidos
        i = self.idx_ejemplo[tipo] % len(lista)
        self.idx_ejemplo[tipo] += 1
        self.entrada.delete(0, "end")
        self.entrada.insert(0, lista[i])
        self.validar()

    # ------------------------------------------------------------ pantalla
    def _llenar_significado(self):
        d = self.diagrama
        self.signif.delete(*self.signif.get_children())
        for od in d.orden:
            n = d.numero[od]
            self.signif.insert("", "end", iid=str(n), tags=("par" if n % 2 else "impar",),
                               values=(n, od[0], ",".join(d.aristas[od]), od[1]))

    def _llenar_clases(self, afd):
        t = self.clases_txt
        t.config(state="normal")
        t.delete("1.0", "end")
        for cls, chars in clases_simbolo(afd).items():
            t.insert("end", cls, "cls")
            t.insert("end", f" = {chars}\n")
        t.config(state="disabled")

    def _refrescar(self):
        r = self.resultado
        terminado = self._terminado()
        filas = self._filas()
        self.vista = min(self.vista, len(filas))
        en_final = terminado and self.vista == len(filas)
        pasos = min(self.vista, len(r.traza)) if r is not None else 0  # pasos reales leídos
        self._mostrar_traza(filas)
        self._mostrar_veredicto(terminado)
        self._mostrar_cadena(terminado, en_final, pasos)
        color = (VERDE if r.aceptada else ROJO) if en_final else AMBAR
        tomada = tuple(r.traza[self.vista - 1][2:4]) if 0 < self.vista <= len(r.traza) else None
        self.diagrama.dibujar(self._estado_en(pasos), color, tomada)
        self._marcar_flecha(tomada)

    def _mostrar_traza(self, filas):
        self.tabla.delete(*self.tabla.get_children())
        for i, fila in enumerate(filas, start=1):
            if i == self.vista:
                tag = "fallo" if i > len(self.resultado.traza) else "ultimo"
            else:
                tag = "par" if i % 2 else "impar"
            self.tabla.insert("", "end", iid=str(i), values=fila, tags=(tag,))
        if self.vista:
            self.tabla.see(str(self.vista))

    def _mostrar_veredicto(self, terminado):
        r = self.resultado
        if terminado and r.aceptada:
            self.veredicto.config(text="CADENA ACEPTADA", fg=SOBRE_ACENTO, bg=VERDE)
        elif terminado:
            self.veredicto.config(text="CADENA RECHAZADA", fg="white", bg=ROJO)
        elif r is not None:
            self.veredicto.config(text=f"Simulando… paso {self.paso} de {len(r.traza)}",
                                  fg=AMBAR, bg=AMBAR_SUAVE)
        else:
            self.veredicto.config(text=TEXTO_INICIAL, fg=TENUE, bg=PANEL)
        self.detalle.config(text=("Motivo: " + r.error[1]) if terminado and r.error else "")

    def _mostrar_cadena(self, terminado, en_final, pasos):
        """Leídos en verde, siguiente en ámbar (rojo si es el que falla), resto en gris."""
        t = self.cadena_txt
        t.config(state="normal")
        t.delete("1.0", "end")
        r = self.resultado
        cadena = self.cadena_sim if r is not None else self.entrada.get()
        fallo = r.error[0] - 1 if terminado and r.error and len(r.traza) < len(cadena) else None
        for i, s in enumerate(cadena):
            if r is None:
                tag = "resto"
            elif i < pasos:
                tag = "leido"
            elif i == fallo and en_final:
                tag = "error"
            elif i == pasos and not en_final:
                tag = "actual"
            else:
                tag = "resto"
            t.insert("end", s, tag)
        t.config(state="disabled")

    def _marcar_flecha(self, tomada):
        """Resalta en la tabla de significado la fila de la flecha tomada."""
        sel = (str(self.diagrama.numero[tomada]),) if tomada in self.diagrama.numero else ()
        for iid in self.signif.get_children():
            self.signif.item(iid, tags=("tomada",) if (iid,) == sel else
                             ("par" if int(iid) % 2 else "impar",))
        self.signif.selection_set(sel)
        if sel:
            self.signif.see(sel[0])


def main():
    raiz = tk.Tk()
    App(raiz)
    raiz.mainloop()
