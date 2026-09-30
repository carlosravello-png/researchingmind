# -*- coding: utf-8 -*-
"""
demo_cos.py — Prevalencia de trastornos del sueno (Cuestionario Oviedo del Sueno)
Estudiantes de Ciencias Biologicas, UNT. Aplicacion 14/09/2026.

Criterios (Garcia-Portilla et al., 2009, anexo 2):
  Insomnio CIE-10 : algun item 2.1-2.4 >= 3  Y  item 7 >= 3
  Insomnio DSM-IV : algun item 2.1-2.4 == 5  Y  item 7 == 5
  Hipersomnio     : items 2.1-2.4 todos == 1 Y  items 2.5, 8 y 9 todos == 5

Se corre con:   python demo_cos.py
No modifica el CSV de entrada.
"""

import sys, time, os

# --- PowerShell en Windows usa cp1252 y revienta con acentos. Esto lo evita. ---
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")          # no abre ventana: solo guarda el PNG. Mas fiable en clase.
import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportion_confint

ENTRADA = "cos_publico.csv"
SALIDA  = "prevalencia_cos.png"
RESPALDO = os.path.join("respaldo", "prevalencia_cos_respaldo.png")
PAUSA = 1.2                    # segundos entre pasos, para narrar en vivo


def paso(texto, pausa=PAUSA):
    print(texto, flush=True)
    time.sleep(pausa)


def val(x):
    """Devuelve int o None si la celda esta vacia."""
    if pd.isna(x):
        return None
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def alguno_cumple(valores, test):
    """'Al menos uno cumple' -> True / False / None (indeterminado)."""
    if any(v is not None and test(v) for v in valores):
        return True                      # ya se cumple, los faltantes no importan
    if any(v is None for v in valores):
        return None                      # ninguno cumple, pero falta informacion
    return False


def todos_cumplen(valores, test):
    """'Todos cumplen' -> True / False / None (indeterminado)."""
    if any(v is not None and not test(v) for v in valores):
        return False                     # ya se descarta, los faltantes no importan
    if any(v is None for v in valores):
        return None
    return True


def combinar(*criterios):
    if any(c is False for c in criterios):
        return "No"
    if all(c is True for c in criterios):
        return "Si"
    return "Indeterminado"


def item(fila, col, test):
    v = val(fila[col])
    return None if v is None else test(v)


def diagnosticar(fila):
    bloque2 = [val(fila[c]) for c in ("i2_1", "i2_2", "i2_3", "i2_4")]
    hiper   = [val(fila[c]) for c in ("i2_5", "i8", "i9")]

    cie10 = combinar(alguno_cumple(bloque2, lambda v: v >= 3),
                     item(fila, "i7", lambda v: v >= 3))
    dsmiv = combinar(alguno_cumple(bloque2, lambda v: v == 5),
                     item(fila, "i7", lambda v: v == 5))
    hipso = combinar(todos_cumplen(bloque2, lambda v: v == 1),
                     todos_cumplen(hiper,  lambda v: v == 5))
    return pd.Series({"CIE10": cie10, "DSMIV": dsmiv, "HIPER": hipso})


def main():
    print()
    print("=" * 62)
    print("  PREVALENCIA DE TRASTORNOS DEL SUENO - CUESTIONARIO OVIEDO")
    print("=" * 62)
    print()

    if not os.path.exists(ENTRADA):
        print("ERROR: no encuentro '%s' en esta carpeta." % ENTRADA)
        print("Carpeta actual:", os.getcwd())
        sys.exit(1)

    paso("Cargando protocolos...")
    df = pd.read_csv(ENTRADA, encoding="utf-8-sig")
    N = len(df)
    paso("  %d protocolos cargados." % N)

    paso("Aplicando criterios CIE-10...")
    paso("Aplicando criterios DSM-IV...")
    paso("Aplicando criterio de hipersomnio...")
    dx = df.apply(diagnosticar, axis=1)
    df = pd.concat([df, dx], axis=1)

    etiquetas = {"CIE10": "Insomnio (CIE-10)",
                 "DSMIV": "Insomnio (DSM-IV)",
                 "HIPER": "Hipersomnio"}

    print()
    print("-" * 72)
    print("%-22s %5s %5s %7s %8s %18s" % ("Diagnostico", "Si", "No", "Indet.", "%", "IC 95% (Wilson)"))
    print("-" * 72)

    resultados = []
    for clave, nombre in etiquetas.items():
        si    = int((df[clave] == "Si").sum())
        no    = int((df[clave] == "No").sum())
        indet = int((df[clave] == "Indeterminado").sum())
        n     = si + no                                  # los indeterminados salen del denominador
        p     = si / n if n else float("nan")
        lo, hi = proportion_confint(si, n, alpha=0.05, method="wilson") if n else (np.nan, np.nan)
        print("%-22s %5d %5d %7d %7.1f%% %8.1f%% - %.1f%%"
              % (nombre, si, no, indet, 100 * p, 100 * lo, 100 * hi))
        resultados.append({"nombre": nombre, "si": si, "n": n, "p": p,
                           "lo": lo, "hi": hi, "indet": indet})
    print("-" * 72)
    print("Los casos indeterminados quedan fuera del denominador y se listan abajo.")
    print()
    time.sleep(PAUSA)

    hay_indet = False
    for clave, nombre in etiquetas.items():
        codigos = df.loc[df[clave] == "Indeterminado", "codigo"].tolist()
        if codigos:
            hay_indet = True
            print("Indeterminados en %s: %s"
                  % (nombre, ", ".join("%03d" % int(c) for c in codigos)))
    if not hay_indet:
        print("Sin casos indeterminados.")
    print()
    time.sleep(PAUSA)

    paso("Generando el grafico...")
    graficar(resultados, N)

    print()
    print("Grafico guardado: %s" % SALIDA)
    print("Respaldo guardado: %s" % RESPALDO)
    print()


def graficar(resultados, N):
    plt.rcParams.update({
        "font.size": 15,
        "axes.titlesize": 19,
        "axes.labelsize": 16,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })

    resultados = list(reversed(resultados))       # la primera barra arriba
    nombres = [r["nombre"] for r in resultados]
    pct     = [100 * r["p"] for r in resultados]
    err_lo  = [100 * (r["p"] - r["lo"]) for r in resultados]
    err_hi  = [100 * (r["hi"] - r["p"]) for r in resultados]

    fig, ax = plt.subplots(figsize=(11, 5.6))
    y = np.arange(len(nombres))

    ax.barh(y, pct, height=0.55, color="#4C6E9C", edgecolor="#2E4763", linewidth=1.0, zorder=2)
    ax.errorbar(pct, y, xerr=[err_lo, err_hi], fmt="none",
                ecolor="#1F2933", elinewidth=2.0, capsize=8, capthick=2.0, zorder=3)

    for i, r in enumerate(resultados):
        texto = "%.1f %% (%d/%d)" % (100 * r["p"], r["si"], r["n"])
        texto = texto.replace(".", ",")
        x = 100 * r["hi"] + 2.5
        ax.text(x, i, texto, va="center", ha="left", fontsize=15, fontweight="bold",
                color="#1F2933", zorder=4)

    ax.set_yticks(y)
    ax.set_yticklabels(nombres)
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 10))
    ax.set_xlabel("Prevalencia (%)")
    ax.set_title("Prevalencia de trastornos del sueño — COS (N = %d)" % N, pad=16)
    ax.xaxis.grid(True, color="#D6DBE0", linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.spines["left"].set_color("#8A949E")
    ax.spines["bottom"].set_color("#8A949E")
    ax.tick_params(axis="y", length=0)

    fig.text(0.012, 0.025,
             "Estudiantes de Ciencias Biológicas, UNT. Aplicación 14/09/2026. IC 95 % Wilson.",
             fontsize=12, color="#4A5560")
    fig.tight_layout(rect=[0, 0.055, 1, 1])

    fig.savefig(SALIDA, dpi=300, facecolor="white")
    os.makedirs(os.path.dirname(RESPALDO), exist_ok=True)
    fig.savefig(RESPALDO, dpi=300, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
