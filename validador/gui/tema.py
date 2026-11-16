"""Tema oscuro: colores, fuentes, estilos ttk e icono de la ventana."""
import math
import tkinter as tk
from tkinter import ttk

# Paleta oscura suave (inspirada en React: #20232a / #61dafb)
FONDO = "#1b1e24"
PANEL = "#23272f"
PANEL_ALT = "#292e37"
BORDE = "#3a404c"
HOVER = "#323844"
TEXTO = "#e6e9ef"
TENUE = "#8b93a5"
ACENTO = "#61dafb"
ACENTO_HOVER = "#8be4fc"
SOBRE_ACENTO = "#20232a"
VERDE = "#22c55e"
ROJO = "#ef4444"
AMBAR = "#f59e0b"
AMBAR_SUAVE = "#4a3b14"
ARISTA = "#7c8597"
ETIQUETA = "#9fe6fb"
FUENTE = "Segoe UI"
MONO = "Consolas"


def icono_react(n=64):
    """PhotoImage n x n con un átomo estilo React (núcleo + 3 órbitas)."""
    fondo, cian = SOBRE_ACENTO, ACENTO
    c = (n - 1) / 2
    a, b, grosor = n * 0.44, n * 0.16, n * 0.035
    rotaciones = [(math.cos(t), math.sin(t)) for t in (0, math.pi / 3, 2 * math.pi / 3)]
    filas = []
    for y in range(n):
        fila = []
        for x in range(n):
            dx, dy = x - c, y - c
            on = dx * dx + dy * dy <= (n * 0.09) ** 2
            for co, si in rotaciones:
                if on:
                    break
                u, v = dx * co + dy * si, -dx * si + dy * co
                r = math.sqrt((u / a) ** 2 + (v / b) ** 2)
                on = abs(r - 1) * b < grosor
            fila.append(cian if on else fondo)
        filas.append("{" + " ".join(fila) + "}")
    img = tk.PhotoImage(width=n, height=n)
    img.put(" ".join(filas))
    return img


def aplicar_estilos(raiz):
    st = ttk.Style(raiz)
    st.theme_use("clam")
    st.configure(".", background=FONDO, foreground=TEXTO, font=(FUENTE, 10),
                 bordercolor=BORDE, lightcolor=BORDE, darkcolor=BORDE,
                 troughcolor=FONDO, focuscolor=ACENTO)
    st.configure("TButton", padding=(10, 4), background=PANEL, foreground=TEXTO,
                 bordercolor=BORDE, relief="flat")
    st.map("TButton", background=[("pressed", BORDE), ("active", HOVER)],
           bordercolor=[("active", ACENTO)])
    st.configure("Acento.TButton", background=ACENTO, foreground=SOBRE_ACENTO,
                 bordercolor=ACENTO, font=(FUENTE, 10, "bold"))
    st.map("Acento.TButton", background=[("pressed", "#4fc3e6"), ("active", ACENTO_HOVER)],
           foreground=[("active", SOBRE_ACENTO)])
    st.configure("TEntry", fieldbackground=PANEL, foreground=TEXTO, insertcolor=ACENTO,
                 bordercolor=BORDE, padding=(6, 3))
    st.map("TEntry", bordercolor=[("focus", ACENTO)], lightcolor=[("focus", ACENTO)])
    st.configure("TCombobox", fieldbackground=PANEL, background=PANEL, foreground=TEXTO,
                 arrowcolor=ACENTO, bordercolor=BORDE, padding=(6, 3))
    st.map("TCombobox", fieldbackground=[("readonly", PANEL)],
           foreground=[("readonly", TEXTO)], selectbackground=[("readonly", PANEL)],
           selectforeground=[("readonly", TEXTO)], bordercolor=[("focus", ACENTO)],
           background=[("active", HOVER)])
    raiz.option_add("*TCombobox*Listbox.background", PANEL)
    raiz.option_add("*TCombobox*Listbox.foreground", TEXTO)
    raiz.option_add("*TCombobox*Listbox.selectBackground", ACENTO)
    raiz.option_add("*TCombobox*Listbox.selectForeground", SOBRE_ACENTO)
    st.configure("Treeview", rowheight=24, background=PANEL, fieldbackground=PANEL,
                 foreground=TEXTO, bordercolor=BORDE)
    st.map("Treeview", background=[("selected", HOVER)], foreground=[("selected", TEXTO)])
    st.configure("Treeview.Heading", font=(FUENTE, 10, "bold"), background=PANEL_ALT,
                 foreground=ACENTO, bordercolor=BORDE, relief="flat")
    st.map("Treeview.Heading", background=[("active", HOVER)])
    st.configure("TScrollbar", background=PANEL, arrowcolor=TENUE, bordercolor=FONDO)
    st.map("TScrollbar", background=[("active", HOVER)])
