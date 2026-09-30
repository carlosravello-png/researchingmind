# -*- coding: utf-8 -*-
"""
slider_ventana.py — VERSION A: el slider en una ventana de Python

Arrastras la barra y ves, al mismo tiempo:
  - los 57 cuestionarios como puntos, pintandose segun cruzan la raya
  - la cifra grande
  - la barra de prevalencia

Se corre con:   python slider_ventana.py
La ventana se abre sola al terminar la corrida.

Prueba sin ventana (control de calidad):  python slider_ventana.py --prueba
Eso no abre nada: guarda 'slider_prueba.png' y sale.

No modifica el CSV de entrada.
"""

import sys, os

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PRUEBA = "--prueba" in sys.argv

import pandas as pd
import numpy as np
import matplotlib

if PRUEBA:
    matplotlib.use("Agg")
else:
    # Ventana. TkAgg viene con Miniconda; si falla, avisamos claro.
    try:
        matplotlib.use("TkAgg")
    except Exception:
        pass

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

ENTRADA = "cos_publico.csv"

AZUL    = "#4C6E9C"
GRIS    = "#C9D1D9"
AMBAR   = "#D9A441"
OSCURO  = "#1F2933"
FONDO   = "#FFFFFF"

RAYAS = {1: "cualquier molestia",
         2: "1 o 2 dias por semana",
         3: "3 dias por semana",
         4: "4 o 5 dias por semana",
         5: "6 o 7 dias por semana"}

OFICIAL = {3: "CIE-10  (OMS)", 5: "DSM-IV  (APA)"}


# --- algoritmo del COS, identico a los otros scripts -----------------------

def val(x):
    if pd.isna(x):
        return None
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def alguno_cumple(valores, test):
    if any(v is not None and test(v) for v in valores):
        return True
    if any(v is None for v in valores):
        return None
    return False


def combinar(*criterios):
    if any(c is False for c in criterios):
        return "No"
    if all(c is True for c in criterios):
        return "Si"
    return "Indeterminado"


def item(fila, col, test):
    v = val(fila[col])
    return None if v is None else test(v)


def insomnio_con_raya(fila, k):
    bloque2 = [val(fila[c]) for c in ("i2_1", "i2_2", "i2_3", "i2_4")]
    return combinar(alguno_cumple(bloque2, lambda v: v >= k),
                    item(fila, "i7", lambda v: v >= k))


# --- datos -----------------------------------------------------------------

def cargar():
    if not os.path.exists(ENTRADA):
        print("ERROR: no encuentro '%s' en esta carpeta." % ENTRADA)
        print("Carpeta actual:", os.getcwd())
        sys.exit(1)
    df = pd.read_csv(ENTRADA, encoding="utf-8-sig")
    print("  %d cuestionarios leidos." % len(df))
    # se calculan las cinco rayas una sola vez: arrastrar tiene que ser instantaneo
    tabla = {}
    for k in range(1, 6):
        tabla[k] = df.apply(lambda f: insomnio_con_raya(f, k), axis=1).tolist()
    codigos = [str(c).zfill(3) for c in df["codigo"]]
    return codigos, tabla


# --- figura ----------------------------------------------------------------

def construir(codigos, tabla):
    n_total = len(codigos)
    columnas = 10
    filas = int(np.ceil(n_total / columnas))
    xs, ys = [], []
    for i in range(n_total):
        xs.append(i % columnas)
        ys.append(filas - 1 - (i // columnas))

    fig = plt.figure(figsize=(13, 8.4), facecolor=FONDO)
    try:
        fig.canvas.manager.set_window_title("Donde ponemos la raya - 57 cuestionarios")
    except Exception:
        pass

    # --- cabecera: todo en coordenadas de figura, sin ejes que se pisen ---
    t_cifra = fig.text(0.06, 0.885, "", fontsize=70, fontweight="bold",
                       color=OSCURO, va="center", ha="left")
    fig.text(0.06, 0.795, "por ciento", fontsize=19, color="#5A6773",
             va="center", ha="left")
    t_frac = fig.text(0.94, 0.905, "", fontsize=24, color=OSCURO,
                      va="center", ha="right")
    t_raya = fig.text(0.94, 0.845, "", fontsize=16, color="#5A6773",
                      va="center", ha="right")
    t_ofi = fig.text(0.94, 0.795, "", fontsize=16, fontweight="bold",
                     color=AZUL, va="center", ha="right")

    fig.text(0.06, 0.725, "Cada punto es un cuestionario", fontsize=14,
             color="#5A6773", va="center", ha="left")
    fig.text(0.72, 0.725, "Con insomnio", fontsize=14,
             color="#5A6773", va="center", ha="left")

    ax_pts = fig.add_axes([0.06, 0.32, 0.58, 0.38]); ax_pts.axis("off")
    ax_bar = fig.add_axes([0.72, 0.32, 0.22, 0.38])
    ax_sld = fig.add_axes([0.14, 0.18, 0.72, 0.045], facecolor="#EEF1F4")

    puntos = ax_pts.scatter(xs, ys, s=400, c=[GRIS] * n_total,
                            edgecolors="white", linewidths=1.6)
    ax_pts.set_xlim(-0.8, columnas - 0.2)
    ax_pts.set_ylim(-0.9, filas - 0.1)

    barra = ax_bar.bar([0], [0], width=0.5, color=AZUL)
    ax_bar.set_ylim(0, 100)
    ax_bar.set_xlim(-0.6, 0.6)
    ax_bar.set_xticks([])
    ax_bar.set_yticks([0, 25, 50, 75, 100])
    ax_bar.set_yticklabels(["0 %", "25 %", "50 %", "75 %", "100 %"], fontsize=12)
    for lado in ("top", "right"):
        ax_bar.spines[lado].set_visible(False)

    slider = Slider(ax_sld, "", 1, 5, valinit=3, valstep=1, color=AZUL)
    slider.valtext.set_visible(False)
    for k in range(1, 6):
        ax_sld.text((k - 1) / 4.0, -0.9, str(k), transform=ax_sld.transAxes,
                    ha="center", va="top", fontsize=15, fontweight="bold")
    ax_sld.text(0.0, -2.4, "cualquier\nmolestia", transform=ax_sld.transAxes,
                ha="center", va="top", fontsize=12, color="#5A6773")
    ax_sld.text(1.0, -2.4, "6 o 7 dias\npor semana", transform=ax_sld.transAxes,
                ha="center", va="top", fontsize=12, color="#5A6773")
    fig.text(0.5, 0.275, "Arrastra la barra:  a partir de cuantos dias por semana "
                         "lo llamamos insomnio", fontsize=15, color=OSCURO,
             ha="center", va="center")

    def actualizar(_=None):
        k = int(round(slider.val))
        estados = tabla[k]
        colores = []
        si = no = ind = 0
        for e in estados:
            if e == "Si":
                colores.append(AZUL); si += 1
            elif e == "No":
                colores.append(GRIS); no += 1
            else:
                colores.append(AMBAR); ind += 1
        puntos.set_facecolors(colores)

        n = si + no
        pct = 100.0 * si / n if n else 0.0
        t_cifra.set_text("%d" % round(pct))
        t_frac.set_text("%d de %d" % (si, n))
        t_raya.set_text("raya en " + RAYAS[k])
        t_ofi.set_text(OFICIAL.get(k, ""))
        t_ofi.set_color("#B4413C" if k == 5 else AZUL)
        barra[0].set_height(pct)
        barra[0].set_color(AZUL if k != 5 else "#B4413C")
        fig.canvas.draw_idle()

    slider.on_changed(actualizar)
    actualizar()
    return fig, slider, actualizar


def main():
    print()
    print("  DONDE PONEMOS LA RAYA - version con slider")
    print()
    codigos, tabla = cargar()
    fig, slider, actualizar = construir(codigos, tabla)

    if PRUEBA:
        fig.savefig("slider_prueba.png", dpi=110)
        print("  Prueba sin ventana: guardado slider_prueba.png")
        return

    # OJO: TkAgg y QtAgg terminan en "agg" y SI tienen ventana.
    # Solo estos backends son de archivo, sin ventana posible.
    SIN_VENTANA = {"agg", "cairo", "pdf", "pgf", "ps", "svg", "template"}
    backend = matplotlib.get_backend()
    if backend.lower() in SIN_VENTANA:
        fig.savefig("slider_prueba.png", dpi=110)
        print("  Tu matplotlib quedo sin ventana (backend %s)." % backend)
        print("  No se puede abrir el slider en esta maquina.")
        print("  Guarde la imagen fija en slider_prueba.png.")
        print("  Dimelo y pasamos a la version web, que no depende de esto.")
        return

    print("  Abriendo la ventana...")
    print("  Arrastra la barra de abajo. Azul = con insomnio,")
    print("  gris = sin insomnio, ambar = no se puede decidir.")
    print("  Cierra la ventana para volver a la consola.")
    print()
    try:
        mng = plt.get_current_fig_manager()
        try:
            mng.window.state("zoomed")      # pantalla completa en Windows
        except Exception:
            pass
    except Exception:
        pass
    plt.show()


if __name__ == "__main__":
    main()
