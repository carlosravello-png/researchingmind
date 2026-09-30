# -*- coding: utf-8 -*-
"""
demo_umbral.py — El umbral decide la cifra
Prevalencia de insomnio en 57 protocolos del Cuestionario Oviedo del Sueno (COS).
Estudiantes de Ciencias Biologicas, UNT. Aplicacion 14/09/2026.

Que hace, en una linea: no simula nada. Recalcula TUS datos bajo distintos
criterios diagnosticos y muestra que la cifra depende del umbral, no de la gente.

Criterios (Garcia-Portilla et al., 2009, anexo 2):
  Insomnio CIE-10 : algun item 2.1-2.4 >= 3  Y  item 7 >= 3
  Insomnio DSM-IV : algun item 2.1-2.4 == 5  Y  item 7 == 5
Los dos son el mismo algoritmo con un umbral distinto. De ahi sale el demo.

Se corre con:   python demo_umbral.py
No modifica el CSV de entrada.
"""

import sys, os, time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")          # sin ventanas: guarda PNG. En clase no falla.
import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportion_confint

ENTRADA  = "cos_publico.csv"
RESPALDO = "respaldo"
SEMILLA  = 2026                # el bootstrap da lo mismo en tu maquina y en la mia

ETIQUETAS_I2 = {
    "i2_1": "Conciliar el sueno",
    "i2_2": "Permanecer dormido",
    "i2_3": "Sueno reparador",
    "i2_4": "Despertar a la hora habitual",
}

# ----------------------------------------------------------------------------
# utilidades de presentacion
# ----------------------------------------------------------------------------

def titulo(txt):
    print()
    print("=" * 70)
    print("  " + txt)
    print("=" * 70)
    print()


def enter(txt="   [Enter para continuar]"):
    try:
        input(txt)
    except EOFError:
        print(txt + "  (sin consola interactiva: sigo)")
    print()


def barra(frac, ancho=40):
    lleno = int(round(frac * ancho))
    return "[" + "#" * lleno + "." * (ancho - lleno) + "]"


# ----------------------------------------------------------------------------
# algoritmo del COS  (identico al de demo_cos.py: las cifras no se recalculan)
# ----------------------------------------------------------------------------

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


def insomnio_con_umbral(fila, k):
    """El algoritmo del COS parametrizado por el umbral k (1 a 5).

    k = 3 reproduce exactamente el criterio CIE-10.
    k = 5 reproduce exactamente el criterio DSM-IV, porque la escala llega a 5
          y '>= 5' es lo mismo que '== 5'.
    """
    bloque2 = [val(fila[c]) for c in ("i2_1", "i2_2", "i2_3", "i2_4")]
    return combinar(alguno_cumple(bloque2, lambda v: v >= k),
                    item(fila, "i7", lambda v: v >= k))


def contar(serie_dx):
    si = int((serie_dx == "Si").sum())
    no = int((serie_dx == "No").sum())
    ind = int((serie_dx == "Indeterminado").sum())
    n = si + no
    p = si / n if n else float("nan")
    return si, no, ind, n, p


def wilson(si, n):
    if n == 0:
        return float("nan"), float("nan")
    return proportion_confint(si, n, alpha=0.05, method="wilson")


def guardar(fig, nombre):
    fig.savefig(nombre, dpi=140, bbox_inches="tight")
    if not os.path.isdir(RESPALDO):
        os.makedirs(RESPALDO)
    fig.savefig(os.path.join(RESPALDO, nombre), dpi=140, bbox_inches="tight")
    plt.close(fig)
    print("   Guardado: %s  (copia en %s\\)" % (nombre, RESPALDO))


ESTILO = {
    "font.size": 14,
    "axes.titlesize": 18,
    "axes.labelsize": 15,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
}
AZUL = "#4C6E9C"
OSCURO = "#1F2933"
ROJO = "#B4413C"


# ----------------------------------------------------------------------------
# BLOQUE 0 — carga
# ----------------------------------------------------------------------------

def bloque_carga():
    titulo("EL UMBRAL DECIDE LA CIFRA")
    print("  Cuestionario Oviedo del Sueno - 57 protocolos - UNT, 14/09/2026")
    print("  Nada de lo que sigue esta simulado: todo se recalcula sobre los")
    print("  mismos protocolos que aplicamos en el aula.")
    print()

    if not os.path.exists(ENTRADA):
        print("ERROR: no encuentro '%s' en esta carpeta." % ENTRADA)
        print("Carpeta actual:", os.getcwd())
        sys.exit(1)

    df = pd.read_csv(ENTRADA, encoding="utf-8-sig")
    for i in range(1, len(df) + 1, 6):
        print("\r   Cargando protocolos  %s  %d/%d" % (barra(i / len(df)), i, len(df)),
              end="", flush=True)
        time.sleep(0.02)
    print("\r   Cargando protocolos  %s  %d/%d" % (barra(1.0), len(df), len(df)))
    print()
    print("   %d protocolos. Edades de %d a %d anos." %
          (len(df), int(df["edad"].min()), int(df["edad"].max())))
    return df


# ----------------------------------------------------------------------------
# BLOQUE 1 — el barrido del umbral
# ----------------------------------------------------------------------------

def bloque_umbral(df):
    titulo("1. EL MISMO DATO, CINCO PREVALENCIAS")
    print("  El COS pregunta cuantos dias por semana aparece cada dificultad.")
    print("  1 = ninguno   2 = 1-2 dias   3 = 3 dias   4 = 4-5 dias   5 = 6-7 dias")
    print()
    print("  CIE-10 exige que la dificultad llegue al nivel 3. DSM-IV, al 5.")
    print("  Es el mismo algoritmo con el umbral corrido. Vamos a correrlo entero.")
    print()

    filas = []
    for k in range(1, 6):
        dx = df.apply(lambda f: insomnio_con_umbral(f, k), axis=1)
        si, no, ind, n, p = contar(dx)
        lo, hi = wilson(si, n)
        filas.append({"k": k, "si": si, "n": n, "ind": ind, "p": p, "lo": lo, "hi": hi})

    print("   %-7s %-26s %7s %7s %9s %20s" %
          ("Umbral", "Significa", "Casos", "n", "Prev.", "IC 95% (Wilson)"))
    print("   " + "-" * 79)
    sentido = {1: "cualquier respuesta", 2: "al menos 1-2 dias/sem",
               3: "al menos 3 dias/sem", 4: "al menos 4-5 dias/sem",
               5: "6-7 dias/sem"}
    for f in filas:
        marca = ""
        if f["k"] == 3:
            marca = "  <- CIE-10"
        if f["k"] == 5:
            marca = "  <- DSM-IV"
        print("   %-7d %-26s %7d %7d %8.1f%% %9.1f%% - %-6.1f%%%s" %
              (f["k"], sentido[f["k"]], f["si"], f["n"],
               100 * f["p"], 100 * f["lo"], 100 * f["hi"], marca))
        time.sleep(0.35)
    print("   " + "-" * 79)
    print()
    print("   Mismos 57 protocolos. Mismas respuestas. Mismo evaluador.")
    print("   Lo unico que se movio fue el numero que exige el criterio.")

    fig, ax = plt.subplots(figsize=(11, 6))
    plt.rcParams.update(ESTILO)
    ks = [f["k"] for f in filas]
    ps = [100 * f["p"] for f in filas]
    lo = [100 * (f["p"] - f["lo"]) for f in filas]
    hi = [100 * (f["hi"] - f["p"]) for f in filas]

    ax.plot(ks, ps, "-o", color=AZUL, linewidth=2.6, markersize=9, zorder=3)
    ax.errorbar(ks, ps, yerr=[lo, hi], fmt="none", ecolor=OSCURO,
                elinewidth=1.6, capsize=6, zorder=2)
    for f in filas:
        ax.annotate(("%.1f %%" % (100 * f["p"])).replace(".", ","),
                    (f["k"], 100 * f["p"]), textcoords="offset points",
                    xytext=(0, 14), ha="center", fontsize=13, fontweight="bold")
    ax.axvline(3, color=ROJO, linestyle="--", linewidth=1.4, zorder=1)
    ax.axvline(5, color=ROJO, linestyle="--", linewidth=1.4, zorder=1)
    ax.text(3, 108, " CIE-10", color=ROJO, fontsize=13, fontweight="bold", va="top")
    ax.text(5, 108, " DSM-IV", color=ROJO, fontsize=13, fontweight="bold",
            va="top", ha="right")
    ax.set_xticks(ks)
    ax.set_xticklabels(["1\ncualquiera", "2\n1-2 d", "3\n3 d", "4\n4-5 d", "5\n6-7 d"])
    ax.set_xlabel("Umbral exigido a la dificultad nocturna y a la repercusión diurna")
    ax.set_ylabel("Prevalencia de insomnio (%)")
    ax.set_ylim(0, 112)
    ax.set_yticks(range(0, 101, 20))
    ax.set_title("La prevalencia depende del umbral, no de la muestra", pad=16)
    ax.grid(True, color="#D6DBE0", linewidth=0.9)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    print()
    guardar(fig, "01_umbral.png")

    print()
    print("   Ahora pruebalo tu. Escribe un umbral del 1 al 5 y lo recalculo.")
    print("   (Enter vacio para seguir.)")
    while True:
        try:
            r = input("   Umbral > ").strip()
        except EOFError:
            break
        if r == "":
            break
        if r not in list("12345"):
            print("   Escribe un numero del 1 al 5.")
            continue
        k = int(r)
        dx = df.apply(lambda f: insomnio_con_umbral(f, k), axis=1)
        si, no, ind, n, p = contar(dx)
        lo_, hi_ = wilson(si, n)
        print("   Umbral %d  ->  %d de %d  =  %.1f %%   (IC 95%%: %.1f%% - %.1f%%)"
              % (k, si, n, 100 * p, 100 * lo_, 100 * hi_))
    return filas


# ----------------------------------------------------------------------------
# BLOQUE 2 — bootstrap
# ----------------------------------------------------------------------------

def bloque_bootstrap(df):
    titulo("2. CUANTO SE MUEVE ESA CIFRA SI REPITIERAMOS EL ESTUDIO")
    dx = df.apply(lambda f: insomnio_con_umbral(f, 3), axis=1)
    si, no, ind, n, p = contar(dx)
    lo, hi = wilson(si, n)

    print("  Prevalencia observada con CIE-10: %d de %d = %.1f %%" % (si, n, 100 * p))
    print("  Intervalo de Wilson: %.1f %% - %.1f %%" % (100 * lo, 100 * hi))
    print()
    print("  El intervalo sale de una formula. Vamos a llegar al mismo sitio por")
    print("  el camino largo: remuestreando estos %d casos miles de veces." % n)
    print()

    datos = np.array([1] * si + [0] * (n - si))
    rng = np.random.default_rng(SEMILLA)

    hitos = [100, 500, 1000, 5000, 10000]
    muestras = []
    hecho = 0
    print("   %-9s %-44s %s" % ("Remuestreos", "", "Percentiles 2,5 - 97,5"))
    for B in hitos:
        faltan = B - hecho
        nuevas = rng.choice(datos, size=(faltan, n), replace=True).mean(axis=1)
        muestras.extend(nuevas.tolist())
        hecho = B
        arr = np.array(muestras)
        p_lo, p_hi = np.percentile(arr, [2.5, 97.5])
        print("   %-9d %-44s %.1f %% - %.1f %%" %
              (B, barra(B / hitos[-1], 40), 100 * p_lo, 100 * p_hi))
        time.sleep(0.45)

    arr = np.array(muestras)
    p_lo, p_hi = np.percentile(arr, [2.5, 97.5])
    print()
    print("   Bootstrap (10 000): %.1f %% - %.1f %%" % (100 * p_lo, 100 * p_hi))
    print("   Wilson  (formula) : %.1f %% - %.1f %%" % (100 * lo, 100 * hi))
    print()
    print("   Dos metodos distintos, el mismo intervalo. Eso es lo que significa")
    print("   que el intervalo no sea un adorno: es la variacion que tendria la")
    print("   cifra si volvieramos a tomar la muestra.")

    plt.rcParams.update(ESTILO)
    fig, ax = plt.subplots(figsize=(11, 6))
    bordes = (np.arange(0, n + 2) - 0.5) / n * 100      # un bin por valor alcanzable
    ax.hist(100 * arr, bins=bordes, color=AZUL, edgecolor="white",
            linewidth=0.4, zorder=2)
    ax.axvline(100 * p, color=OSCURO, linewidth=2.4, zorder=3)
    ax.axvspan(100 * lo, 100 * hi, color=ROJO, alpha=0.15, zorder=1)
    ax.axvline(100 * lo, color=ROJO, linestyle="--", linewidth=1.8, zorder=3)
    ax.axvline(100 * hi, color=ROJO, linestyle="--", linewidth=1.8, zorder=3)
    ax.set_xlim(max(0, 100 * arr.min() - 6), min(100, 100 * arr.max() + 6))
    ax.set_xlabel("Prevalencia de insomnio CIE-10 en cada remuestreo (%)")
    ax.set_ylabel("Frecuencia")
    ax.set_title("10 000 remuestreos de los mismos %d casos" % n, pad=16)
    ax.text(100 * hi + 1, ax.get_ylim()[1] * 0.92,
            ("banda roja = IC de Wilson\nlinea negra = %.1f %%" % (100 * p)).replace(".", ","),
            fontsize=12, va="top")
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    print()
    guardar(fig, "02_bootstrap.png")


# ----------------------------------------------------------------------------
# BLOQUE 3 — sensibilidad de los indeterminados
# ----------------------------------------------------------------------------

def bloque_sensibilidad(df):
    titulo("3. LA PREGUNTA QUE VA A HACER EL JURADO")
    dx = df.apply(lambda f: insomnio_con_umbral(f, 3), axis=1)
    si, no, ind, n, p = contar(dx)
    codigos = df.loc[dx == "Indeterminado", "codigo"].tolist()

    print("  'Sacaron %d casos del denominador. Eso infla la cifra.'" % ind)
    print()
    print("  Indeterminados: %s" % ", ".join("%03d" % int(c) for c in codigos))
    print("  Les faltan items que podrian cambiar el resultado, asi que no se")
    print("  clasifican. La respuesta no es discutir: es calcular los extremos.")
    print()

    total = si + no + ind
    escenarios = [
        ("Ambos fueran NO insomnio", si, total),
        ("Como se reporta (fuera del denominador)", si, n),
        ("Ambos fueran SI insomnio", si + ind, total),
    ]
    print("   %-42s %9s %10s" % ("Escenario", "Casos/n", "Prevalencia"))
    print("   " + "-" * 65)
    valores = []
    for nombre, a, b in escenarios:
        pp = a / b
        valores.append(100 * pp)
        print("   %-42s %6d/%-3d %9.1f %%" % (nombre, a, b, 100 * pp))
        time.sleep(0.4)
    print("   " + "-" * 65)
    print()
    print("   El resultado se mueve entre %.1f %% y %.1f %%: menos de cuatro puntos."
          % (min(valores), max(valores)))
    print("   La conclusion no depende de esos dos protocolos. Eso es lo que hay")
    print("   que poder decir cuando lo pregunten.")

    plt.rcParams.update(ESTILO)
    fig, ax = plt.subplots(figsize=(11, 4.6))
    nombres = [e[0] for e in escenarios]
    y = np.arange(len(nombres))[::-1]
    colores = [AZUL, OSCURO, AZUL]
    ax.barh(y, valores, height=0.5, color=colores, zorder=2)
    for yy, v in zip(y, valores):
        ax.text(v + 1.2, yy, ("%.1f %%" % v).replace(".", ","),
                va="center", fontsize=14, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels(nombres, fontsize=13)
    ax.set_xlim(0, 70)
    ax.set_xlabel("Prevalencia de insomnio CIE-10 (%)")
    ax.set_title("Analisis de sensibilidad de los casos indeterminados", pad=14)
    ax.xaxis.grid(True, color="#D6DBE0", linewidth=0.9, zorder=0)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    print()
    guardar(fig, "03_sensibilidad.png")


# ----------------------------------------------------------------------------
# BLOQUE 4 — que dificultad sostiene el diagnostico
# ----------------------------------------------------------------------------

def bloque_red(df):
    titulo("4. QUE DIFICULTAD SOSTIENE EL DIAGNOSTICO")
    dx = df.apply(lambda f: insomnio_con_umbral(f, 3), axis=1)
    casos = df.loc[dx == "Si"]
    print("  Entre los %d casos con insomnio CIE-10, cuales de las cuatro" % len(casos))
    print("  dificultades nocturnas llegan al umbral, y cuales aparecen juntas.")
    print("  Esto es descriptivo: con %d casos no sostiene inferencia." % len(casos))
    print()

    cols = list(ETIQUETAS_I2.keys())
    pres = {c: casos[c].apply(lambda v: (val(v) or 0) >= 3) for c in cols}
    print("   %-32s %8s %8s" % ("Dificultad", "Casos", "%"))
    print("   " + "-" * 50)
    for c in cols:
        cuenta = int(pres[c].sum())
        print("   %-32s %8d %7.1f%%" %
              (ETIQUETAS_I2[c], cuenta, 100 * cuenta / len(casos)))
        time.sleep(0.3)
    print("   " + "-" * 50)

    co = np.zeros((len(cols), len(cols)), dtype=int)
    for i, a in enumerate(cols):
        for j, b in enumerate(cols):
            co[i, j] = int((pres[a] & pres[b]).sum())

    print()
    print("   Cuantos casos comparten cada par:")
    for i, a in enumerate(cols):
        for j, b in enumerate(cols):
            if j > i and co[i, j] > 0:
                print("     %-28s + %-28s %3d" %
                      (ETIQUETAS_I2[a], ETIQUETAS_I2[b], co[i, j]))

    plt.rcParams.update(ESTILO)
    fig, ax = plt.subplots(figsize=(9.5, 8.5))
    ang = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, len(cols), endpoint=False)
    xs, ys = np.cos(ang), np.sin(ang)
    maximo = max(1, co.max())
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            if co[i, j] == 0:
                continue
            ancho = 1.0 + 7.0 * co[i, j] / maximo
            ax.plot([xs[i], xs[j]], [ys[i], ys[j]], color=AZUL,
                    alpha=0.45, linewidth=ancho, zorder=1, solid_capstyle="round")
            ax.text((xs[i] + xs[j]) / 2, (ys[i] + ys[j]) / 2, str(co[i, j]),
                    ha="center", va="center", fontsize=12, fontweight="bold",
                    color=OSCURO, zorder=3,
                    bbox=dict(boxstyle="circle,pad=0.22", fc="white", ec="none"))
    for i, c in enumerate(cols):
        tam = 700 + 2600 * int(pres[c].sum()) / max(1, len(casos))
        ax.scatter(xs[i], ys[i], s=tam, color=OSCURO, zorder=2)
        if abs(xs[i]) > 0.5:                      # nodos laterales: etiqueta afuera
            ha = "left" if xs[i] > 0 else "right"
            ax.text(xs[i] * 1.30, ys[i],
                    "%s\n%d casos" % (ETIQUETAS_I2[c], int(pres[c].sum())),
                    ha=ha, va="center", fontsize=13, fontweight="bold")
        else:                                     # arriba y abajo
            ax.text(xs[i], ys[i] + (0.42 if ys[i] > 0 else -0.42),
                    "%s\n%d casos" % (ETIQUETAS_I2[c], int(pres[c].sum())),
                    ha="center", va="bottom" if ys[i] > 0 else "top",
                    fontsize=13, fontweight="bold")
    ax.set_xlim(-2.9, 2.9)
    ax.set_ylim(-1.95, 1.95)
    ax.axis("off")
    ax.set_title("Dificultades nocturnas que coinciden\nen los %d casos con insomnio CIE-10"
                 % len(casos), pad=10)
    print()
    guardar(fig, "04_red.png")


# ----------------------------------------------------------------------------

def main():
    df = bloque_carga()
    enter()
    bloque_umbral(df)
    enter()
    bloque_bootstrap(df)
    enter()
    bloque_sensibilidad(df)
    enter()
    bloque_red(df)

    titulo("FIN")
    print("  Cuatro imagenes guardadas en esta carpeta y en respaldo\\ :")
    for n in ("01_umbral.png", "02_bootstrap.png", "03_sensibilidad.png", "04_red.png"):
        print("    - " + n)
    print()
    print("  Si algo falla en vivo, abre las de respaldo\\ y sigue la clase.")
    print()


if __name__ == "__main__":
    main()
