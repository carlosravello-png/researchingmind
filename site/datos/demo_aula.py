# -*- coding: utf-8 -*-
"""
demo_aula.py — version para proyectar en clase
Prevalencia de insomnio en 57 protocolos del Cuestionario Oviedo del Sueno.
Estudiantes de Ciencias Biologicas, UNT. Aplicacion 14/09/2026.

Misma matematica que demo_umbral.py, contada para gente que no sabe
estadistica. Lineas cortas, un dato a la vez, numeros grandes.

Se corre con:   python demo_aula.py
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
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportion_confint

ENTRADA  = "cos_publico.csv"
RESPALDO = "respaldo"
SEMILLA  = 2026
ANCHO    = 62                # ancho de pantalla pensado para proyector
LENTO    = 0.022             # segundos por caracter en el teletipo
PAUSA    = 0.9

# --- digitos grandes, solo ASCII: en proyector se leen desde el fondo -------
DIGITOS = {
    "0": ["  ###  ", " #   # ", " #   # ", " #   # ", "  ###  "],
    "1": ["   #   ", "  ##   ", "   #   ", "   #   ", "  ###  "],
    "2": [" ####  ", "     # ", "  ###  ", " #     ", " ##### "],
    "3": [" ####  ", "     # ", "  ###  ", "     # ", " ####  "],
    "4": " #   # ; #   # ; ##### ;     # ;     # ".split(";"),
    "5": [" ##### ", " #     ", " ####  ", "     # ", " ####  "],
    "6": ["  ###  ", " #     ", " ####  ", " #   # ", "  ###  "],
    "7": [" ##### ", "     # ", "    #  ", "   #   ", "   #   "],
    "8": ["  ###  ", " #   # ", "  ###  ", " #   # ", "  ###  "],
    "9": ["  ###  ", " #   # ", "  #### ", "     # ", "  ###  "],
    "%": [" ##  # ", " ##  # ", "    #  ", " #  ## ", " #  ## "],
    " ": ["       ", "       ", "       ", "       ", "       "],
    ",": ["       ", "       ", "       ", "   ##  ", "  #    "],
    "d": ["     # ", "     # ", "  #### ", " #   # ", "  #### "],
    "e": ["       ", "  ###  ", " #### ", " #     ", "  ###  "],
}


def grande(texto, centrado=True):
    """Dibuja un numero en letras grandes de cinco lineas."""
    filas = ["", "", "", "", ""]
    for ch in texto:
        patron = DIGITOS.get(ch, DIGITOS[" "])
        for i in range(5):
            filas[i] += patron[i]
    for f in filas:
        print(("   " + f.center(ANCHO - 6)) if centrado else ("   " + f))


def teletipo(texto, vel=LENTO):
    for ch in texto:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(vel)
    print()


def linea(car="-"):
    print("  " + car * (ANCHO - 4))


def titulo(txt):
    print()
    print("  " + "=" * (ANCHO - 4))
    print("  " + txt.center(ANCHO - 4))
    print("  " + "=" * (ANCHO - 4))
    print()


def enter(txt="        [ Enter ]"):
    try:
        input(txt)
    except EOFError:
        pass
    print()


def marco(lineas):
    """Un recuadro para el dato que importa."""
    ancho = max(len(l) for l in lineas) + 6
    print("   +" + "-" * ancho + "+")
    for l in lineas:
        print("   |" + l.center(ancho) + "|")
    print("   +" + "-" * ancho + "+")


# ---------------------------------------------------------------------------
# algoritmo del COS (identico a demo_cos.py y demo_umbral.py)
# ---------------------------------------------------------------------------

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


def contar(serie):
    si = int((serie == "Si").sum())
    no = int((serie == "No").sum())
    ind = int((serie == "Indeterminado").sum())
    n = si + no
    return si, no, ind, n, (si / n if n else float("nan"))


def wilson(si, n):
    return proportion_confint(si, n, alpha=0.05, method="wilson")


PALABRAS = {1: "ningun dia", 2: "1 o 2 dias", 3: "3 dias",
            4: "4 o 5 dias", 5: "6 o 7 dias"}

RAYAS = {1: "cualquier molestia", 2: "1 o 2 dias por semana",
         3: "3 dias por semana", 4: "4 o 5 dias por semana",
         5: "6 o 7 dias por semana"}


def guardar(fig, nombre):
    fig.savefig(nombre, dpi=140, bbox_inches="tight")
    if not os.path.isdir(RESPALDO):
        os.makedirs(RESPALDO)
    fig.savefig(os.path.join(RESPALDO, nombre), dpi=140, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 0. DE QUE VA ESTO
# ---------------------------------------------------------------------------

def bloque_inicio():
    titulo("DONDE PONEMOS LA RAYA")
    teletipo("  57 estudiantes de Ciencias Biologicas contestaron")
    teletipo("  un cuestionario sobre como duermen.")
    print()
    teletipo("  Hoy no vamos a ver si duermen bien o mal.")
    print()
    teletipo("  Vamos a ver algo mas incomodo:")
    teletipo("  que la cifra depende de donde ponemos la raya.")
    print()

    if not os.path.exists(ENTRADA):
        print("  ERROR: no encuentro '%s' aqui." % ENTRADA)
        print("  Carpeta actual:", os.getcwd())
        sys.exit(1)
    df = pd.read_csv(ENTRADA, encoding="utf-8-sig")
    print()
    for i in range(0, len(df) + 1, 3):
        n = min(i, len(df))
        print("\r   Leyendo cuestionarios...  %d de %d" % (n, len(df)),
              end="", flush=True)
        time.sleep(0.03)
    print("\r   Leyendo cuestionarios...  %d de %d" % (len(df), len(df)))
    print()
    return df


# ---------------------------------------------------------------------------
# 1. LA ANALOGIA
# ---------------------------------------------------------------------------

def bloque_analogia():
    titulo("PRIMERO, ALGO QUE YA CONOCEN")
    teletipo("  Imaginen un examen que rindio todo el salon.")
    print()
    teletipo("  Si la nota minima para aprobar es 11,")
    teletipo("  aprueba mucha gente.")
    print()
    teletipo("  Si la subimos a 18, aprueban dos.")
    print()
    time.sleep(PAUSA)
    marco(["Nadie estudio mas ni menos.",
           "Lo unico que se movio fue la nota minima."])
    print()
    teletipo("  Con el insomnio pasa exactamente lo mismo.")
    teletipo("  Y ahora lo vamos a ver con nuestros datos.")


# ---------------------------------------------------------------------------
# 2. LA PREGUNTA, TAL COMO SE HIZO
# ---------------------------------------------------------------------------

def bloque_pregunta(df):
    titulo("LO QUE LES PREGUNTAMOS")
    teletipo("  El cuestionario pregunta, por cada molestia:")
    print()
    marco(["\"Cuantos dias por semana le paso?\""])
    print()
    print("   Las cinco respuestas posibles:")
    print()
    for k in range(1, 6):
        print("      %d  =  %s" % (k, PALABRAS[k]))
        time.sleep(0.25)
    print()
    teletipo("  Asi contestaron tres de ellos, de verdad:")
    print()
    completos = df[df["i2_1"].notna() & df["i2_3"].notna()]
    muestra = completos.head(3)
    for _, f in muestra.iterrows():
        cod = str(f["codigo"]).zfill(3)
        v = val(f["i2_1"])
        v3 = val(f["i2_3"])
        print("   Cuestionario %s" % cod)
        print("      Le costo dormirse .......... %s" % PALABRAS.get(v, "sin dato"))
        print("      No descanso al despertar ... %s" % PALABRAS.get(v3, "sin dato"))
        print()
        time.sleep(0.5)


# ---------------------------------------------------------------------------
# 3. MOVEMOS LA RAYA
# ---------------------------------------------------------------------------

def bloque_raya(df):
    titulo("AHORA MOVEMOS LA RAYA")
    teletipo("  Pregunta: a partir de cuantos dias por semana")
    teletipo("  decimos que alguien tiene insomnio?")
    print()
    time.sleep(PAUSA)

    resultados = {}
    for k in range(1, 6):
        dx = df.apply(lambda f: insomnio_con_raya(f, k), axis=1)
        resultados[k] = contar(dx)

    for k in (3, 5):
        si, no, ind, n, p = resultados[k]
        print()
        print("   Si la raya esta en %s:" % RAYAS[k])
        print()
        grande("%d" % round(100 * p))
        print()
        print("por ciento".center(ANCHO))
        print()
        print(("%d de cada %d personas" % (si, n)).center(ANCHO))
        print()
        time.sleep(1.4)
        if k == 3:
            print("   Esa raya la puso la CIE-10, de la OMS.")
        else:
            print("   Esa raya la puso el DSM-IV, de los psiquiatras")
            print("   de Estados Unidos.")
        time.sleep(1.2)
        enter()

    linea("=")
    print()
    marco(["Nadie durmio distinto.",
           "Son los mismos 57 cuestionarios.",
           "Lo unico que cambio fue la raya."])
    print()
    time.sleep(PAUSA)

    print("   Y si la ponemos en otro lado, pasa esto:")
    print()
    print("      %-24s %s" % ("Raya", "Con insomnio"))
    linea()
    for k in range(1, 6):
        si, no, ind, n, p = resultados[k]
        marca = ""
        if k == 3:
            marca = "   <- CIE-10"
        if k == 5:
            marca = "   <- DSM-IV"
        print("      %-24s %3d de %-3d = %3d %%%s"
              % (RAYAS[k], si, n, round(100 * p), marca))
        time.sleep(0.45)
    linea()
    print()
    teletipo("  Del 100 % al 2 %, con las mismas respuestas.")
    print()

    grafico_raya(resultados)
    print("   (imagen guardada: 01_raya.png)")
    print()
    print("   Prueben ustedes. Escriban un numero del 1 al 5.")
    print("   (Enter vacio para seguir.)")
    while True:
        try:
            r = input("   Raya > ").strip()
        except EOFError:
            break
        if r == "":
            break
        if r not in list("12345"):
            print("   Un numero del 1 al 5.")
            continue
        k = int(r)
        si, no, ind, n, p = resultados[k]
        print("   Raya en %s  ->  %d de %d  =  %d %%"
              % (RAYAS[k], si, n, round(100 * p)))
    return resultados


def grafico_raya(resultados):
    plt.rcParams.update({"font.size": 16, "axes.titlesize": 21,
                         "axes.labelsize": 17, "figure.facecolor": "white"})
    fig, ax = plt.subplots(figsize=(11.5, 6.2))
    ks = list(range(1, 6))
    ps = [100 * resultados[k][4] for k in ks]
    colores = ["#B9C6D6"] * 5
    colores[2] = "#4C6E9C"
    colores[4] = "#B4413C"
    ax.bar(ks, ps, color=colores, width=0.62, zorder=2)
    for k, p in zip(ks, ps):
        ax.text(k, p + 2.5, "%d %%" % round(p), ha="center",
                fontsize=18, fontweight="bold")
    ax.text(3, -14, "CIE-10", ha="center", color="#4C6E9C",
            fontsize=15, fontweight="bold")
    ax.text(5, -14, "DSM-IV", ha="center", color="#B4413C",
            fontsize=15, fontweight="bold")
    ax.set_xticks(ks)
    ax.set_xticklabels(["cualquier\nmolestia", "1 o 2\ndias", "3\ndias",
                        "4 o 5\ndias", "6 o 7\ndias"])
    ax.set_ylim(0, 115)
    ax.set_yticks([])
    ax.set_xlabel("\nA partir de cuantos dias por semana lo llamamos insomnio")
    ax.set_title("Los mismos 57 cuestionarios, cinco resultados", pad=18)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    guardar(fig, "01_raya.png")


# ---------------------------------------------------------------------------
# 4. Y SI PREGUNTARAMOS A OTROS
# ---------------------------------------------------------------------------

def bloque_repetir(df):
    titulo("Y SI PREGUNTARAMOS A OTRAS 55 PERSONAS")
    dx = df.apply(lambda f: insomnio_con_raya(f, 3), axis=1)
    si, no, ind, n, p = contar(dx)
    lo, hi = wilson(si, n)

    teletipo("  Nos salio 49 %. Pero medimos a 55 personas,")
    teletipo("  no a todas las del pais.")
    print()
    teletipo("  Si repitieramos el estudio con otras 55,")
    teletipo("  saldria lo mismo? Casi seguro que no exactamente.")
    print()
    teletipo("  Podemos ver cuanto se moveria. Vamos a meter")
    teletipo("  los 55 resultados en una bolsa y sacar 55 al azar,")
    teletipo("  devolviendolos cada vez. Miles de veces.")
    print()
    time.sleep(PAUSA)

    datos = np.array([1] * si + [0] * (n - si))
    rng = np.random.default_rng(SEMILLA)

    print("   Tres sorteos, para que vean como funciona:")
    print()
    for i in range(1, 4):
        m = rng.choice(datos, size=n, replace=True)
        print("      Sorteo %d  ->  %d con insomnio de %d  =  %d %%"
              % (i, int(m.sum()), n, round(100 * m.mean())))
        time.sleep(0.8)
    print()
    teletipo("  Cada sorteo da algo distinto. Ahora 10 000.")
    print()

    muestras = rng.choice(datos, size=(10000, n), replace=True).mean(axis=1)
    for hecho in (2000, 4000, 6000, 8000, 10000):
        arr = muestras[:hecho]
        p_lo, p_hi = np.percentile(arr, [2.5, 97.5])
        print("\r      %5d sorteos  ->  entre %d %% y %d %%      "
              % (hecho, round(100 * p_lo), round(100 * p_hi)), end="", flush=True)
        time.sleep(0.6)
    print()
    print()

    p_lo, p_hi = np.percentile(muestras, [2.5, 97.5])
    marco(["De cada 100 veces que repitieramos el estudio,",
           "en 95 la cifra caeria entre %d %% y %d %%." % (round(100 * p_lo),
                                                           round(100 * p_hi))])
    print()
    teletipo("  Por eso la cifra nunca va sola. Va con ese rango.")
    print()
    print("   (en los libros ese rango se llama intervalo de")
    print("    confianza del 95 por ciento; la formula da %.1f %% - %.1f %%)"
          % (100 * lo, 100 * hi))
    grafico_repetir(muestras, p, lo, hi, n)
    print()
    print("   (imagen guardada: 02_repetir.png)")


def grafico_repetir(muestras, p, lo, hi, n):
    plt.rcParams.update({"font.size": 16, "axes.titlesize": 21,
                         "axes.labelsize": 17, "figure.facecolor": "white"})
    fig, ax = plt.subplots(figsize=(11.5, 6.2))
    bordes = (np.arange(0, n + 2) - 0.5) / n * 100
    ax.hist(100 * muestras, bins=bordes, color="#B9C6D6",
            edgecolor="white", linewidth=0.4, zorder=2)
    ax.axvspan(100 * lo, 100 * hi, color="#4C6E9C", alpha=0.18, zorder=1)
    ax.axvline(100 * p, color="#1F2933", linewidth=3, zorder=3)
    ax.set_xlim(20, 80)
    ax.set_yticks([])
    ax.set_xlabel("\nResultado de cada repeticion del estudio (%)")
    ax.set_title("10 000 repeticiones: casi todas entre 36 %% y 62 %%", pad=18)
    ax.text(100 * p + 1, ax.get_ylim()[1] * 0.9,
            "lo que nos salio\n49 %", fontsize=15, fontweight="bold")
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    guardar(fig, "02_repetir.png")


# ---------------------------------------------------------------------------
# 5. LOS DOS INCOMPLETOS
# ---------------------------------------------------------------------------

def bloque_incompletos(df):
    titulo("LOS DOS CUESTIONARIOS INCOMPLETOS")
    dx = df.apply(lambda f: insomnio_con_raya(f, 3), axis=1)
    si, no, ind, n, p = contar(dx)
    total = si + no + ind

    teletipo("  Dos personas dejaron preguntas sin contestar.")
    teletipo("  Con lo que escribieron no se puede decidir.")
    print()
    teletipo("  Alguien podria decir: 'las sacaron para que")
    teletipo("  les salga mejor la cifra'. Veamos.")
    print()
    time.sleep(PAUSA)

    esc = [("Si las dos tuvieran insomnio", si + ind, total),
           ("Como lo reportamos", si, n),
           ("Si las dos NO tuvieran", si, total)]
    for nombre, a, b in esc:
        print("      %-32s %3d de %-3d = %3d %%"
              % (nombre, a, b, round(100 * a / b)))
        time.sleep(0.8)
    print()
    valores = [100 * a / b for _, a, b in esc]
    marco(["En el peor caso %d %%, en el mejor %d %%." % (round(min(valores)),
                                                          round(max(valores))),
           "La conclusion no cambia."])
    grafico_incompletos(esc)
    print()
    print("   (imagen guardada: 03_incompletos.png)")


def grafico_incompletos(esc):
    plt.rcParams.update({"font.size": 16, "axes.titlesize": 21,
                         "figure.facecolor": "white"})
    fig, ax = plt.subplots(figsize=(11.5, 4.8))
    nombres = [e[0] for e in esc][::-1]
    vals = [100 * e[1] / e[2] for e in esc][::-1]
    y = np.arange(len(nombres))
    colores = ["#B9C6D6", "#4C6E9C", "#B9C6D6"]
    ax.barh(y, vals, color=colores, height=0.55, zorder=2)
    for yy, v in zip(y, vals):
        ax.text(v + 1.5, yy, "%d %%" % round(v), va="center",
                fontsize=18, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels(nombres, fontsize=15)
    ax.set_xlim(0, 70)
    ax.set_xticks([])
    ax.set_title("Los dos casos dudosos no cambian la respuesta", pad=16)
    for lado in ("top", "right", "bottom"):
        ax.spines[lado].set_visible(False)
    guardar(fig, "03_incompletos.png")


# ---------------------------------------------------------------------------
# 6. QUE LES PASA
# ---------------------------------------------------------------------------

def bloque_que_pasa(df):
    titulo("QUE LES PASA, EXACTAMENTE")
    dx = df.apply(lambda f: insomnio_con_raya(f, 3), axis=1)
    casos = df.loc[dx == "Si"]
    etiquetas = [("i2_3", "No descansan al despertar"),
                 ("i2_4", "Se despiertan antes de la hora"),
                 ("i2_1", "Les cuesta quedarse dormidos"),
                 ("i2_2", "Se despiertan en la noche")]
    teletipo("  De las %d personas con insomnio:" % len(casos))
    print()
    for col, texto in etiquetas:
        cuenta = int(casos[col].apply(lambda v: (val(v) or 0) >= 3).sum())
        barra = "#" * int(round(24 * cuenta / len(casos)))
        print("      %-32s %-26s %2d" % (texto, barra, cuenta))
        time.sleep(0.6)
    print()
    marco(["Lo mas frecuente no es no poder dormirse.",
           "Es dormir y no descansar."])
    print()
    print("   Ojo: esto describe a estas 27 personas.")
    print("   Con 27 casos no alcanza para concluir mas.")


# ---------------------------------------------------------------------------

def cierre():
    titulo("EN UNA FRASE")
    teletipo("  La cifra de un diagnostico no sale sola de la gente.")
    print()
    teletipo("  Sale de la gente y de la raya que alguien decidio.")
    print()
    teletipo("  Por eso el metodo se escribe: para que se vea")
    teletipo("  donde pusimos la raya, y cualquiera pueda moverla.")
    print()
    linea("=")
    print()
    print("   Imagenes guardadas en esta carpeta y en respaldo\\ :")
    for n in ("01_raya.png", "02_repetir.png", "03_incompletos.png"):
        print("      - " + n)
    print()


def main():
    df = bloque_inicio()
    enter()
    bloque_analogia()
    enter()
    bloque_pregunta(df)
    enter()
    bloque_raya(df)
    enter()
    bloque_repetir(df)
    enter()
    bloque_incompletos(df)
    enter()
    bloque_que_pasa(df)
    enter()
    cierre()


if __name__ == "__main__":
    main()
