# -*- coding: utf-8 -*-
"""
slider_consola.py — VERSION C: el slider dibujado en la consola

No abre ninguna ventana. La raya se mueve con las flechas izquierda y derecha
y la pantalla se redibuja en el sitio, sin parpadear.

  flecha izquierda / derecha   mover la raya
  1 a 5                        saltar directo
  Q o Esc                      salir

Se corre con:   python slider_consola.py
Un solo cuadro para revisar:  python slider_consola.py --prueba

No modifica el CSV de entrada.
"""

import sys, os

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import pandas as pd

ENTRADA = "cos_publico.csv"
PRUEBA = "--prueba" in sys.argv
ANCHO = 74

# --- color: se enciende solo si la consola lo admite ------------------------

def activar_colores():
    if os.name != "nt":
        return sys.stdout.isatty()
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.GetStdHandle(-11)
        modo = ctypes.c_uint32()
        if not k.GetConsoleMode(h, ctypes.byref(modo)):
            return False
        # 0x0004 = ENABLE_VIRTUAL_TERMINAL_PROCESSING
        return bool(k.SetConsoleMode(h, modo.value | 0x0004))
    except Exception:
        return False


COLOR = activar_colores()

def c(codigo, texto):
    if not COLOR:
        return texto
    return "\033[%sm%s\033[0m" % (codigo, texto)

AZUL   = "38;5;68"
GRIS   = "38;5;250"
AMBAR  = "38;5;179"
BLANCO = "1;37"
ROJO   = "38;5;131"
APAG   = "38;5;244"

DIGITOS = {
    "0": ["  ###  ", " #   # ", " #   # ", " #   # ", "  ###  "],
    "1": ["   #   ", "  ##   ", "   #   ", "   #   ", "  ###  "],
    "2": [" ####  ", "     # ", "  ###  ", " #     ", " ##### "],
    "3": [" ####  ", "     # ", "  ###  ", "     # ", " ####  "],
    "4": [" #   # ", " #   # ", " ##### ", "     # ", "     # "],
    "5": [" ##### ", " #     ", " ####  ", "     # ", " ####  "],
    "6": ["  ###  ", " #     ", " ####  ", " #   # ", "  ###  "],
    "7": [" ##### ", "     # ", "    #  ", "   #   ", "   #   "],
    "8": ["  ###  ", " #   # ", "  ###  ", " #   # ", "  ###  "],
    "9": ["  ###  ", " #   # ", "  #### ", "     # ", "  ###  "],
    " ": ["       ", "       ", "       ", "       ", "       "],
}


def digitos_grandes(texto):
    filas = ["", "", "", "", ""]
    for ch in texto:
        pat = DIGITOS.get(ch, DIGITOS[" "])
        for i in range(5):
            filas[i] += pat[i]
    return filas


# --- algoritmo del COS, identico a los otros scripts ------------------------

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
    if any(x is False for x in criterios):
        return "No"
    if all(x is True for x in criterios):
        return "Si"
    return "Indeterminado"


def item(fila, col, test):
    v = val(fila[col])
    return None if v is None else test(v)


def insomnio_con_raya(fila, k):
    bloque2 = [val(fila[c_]) for c_ in ("i2_1", "i2_2", "i2_3", "i2_4")]
    return combinar(alguno_cumple(bloque2, lambda v: v >= k),
                    item(fila, "i7", lambda v: v >= k))


RAYAS = {1: "cualquier molestia",
         2: "1 o 2 dias por semana",
         3: "3 dias por semana",
         4: "4 o 5 dias por semana",
         5: "6 o 7 dias por semana"}

OFICIAL = {3: "CIE-10 (OMS)", 5: "DSM-IV (APA)"}


def cargar():
    if not os.path.exists(ENTRADA):
        print("ERROR: no encuentro '%s' en esta carpeta." % ENTRADA)
        print("Carpeta actual:", os.getcwd())
        sys.exit(1)
    df = pd.read_csv(ENTRADA, encoding="utf-8-sig")
    tabla = {}
    for k in range(1, 6):
        tabla[k] = df.apply(lambda f: insomnio_con_raya(f, k), axis=1).tolist()
    return tabla


# --- el cuadro --------------------------------------------------------------

def cuadro(tabla, k):
    estados = tabla[k]
    si = sum(1 for e in estados if e == "Si")
    no = sum(1 for e in estados if e == "No")
    ind = sum(1 for e in estados if e == "Indeterminado")
    n = si + no
    pct = 100.0 * si / n if n else 0.0

    L = []
    L.append("")
    L.append("  " + c(BLANCO, "DONDE PONEMOS LA RAYA") +
             c(APAG, "     57 cuestionarios - UNT 2026"))
    L.append("  " + c(APAG, "-" * (ANCHO - 4)))
    L.append("")

    grandes = digitos_grandes("%d" % round(pct))
    lado = ["", "", "", "", ""]
    lado[1] = c(BLANCO, "%d de %d" % (si, n))
    lado[2] = c(GRIS, "raya en " + RAYAS[k])
    if k in OFICIAL:
        lado[3] = c(ROJO if k == 5 else AZUL, OFICIAL[k])
    for i in range(5):
        L.append("   " + c(AZUL, grandes[i]) + "    " + lado[i])
    L.append("      " + c(APAG, "por ciento"))
    L.append("")

    ancho_barra = 46
    lleno = int(round(ancho_barra * pct / 100.0))
    barra = c(AZUL, "#" * lleno) + c(APAG, "." * (ancho_barra - lleno))
    L.append("   " + barra + "  " + c(BLANCO, "%3d %%" % round(pct)))
    L.append("")

    L.append("   " + c(APAG, "cada casilla es un cuestionario"))
    fila = "   "
    for i, e in enumerate(estados):
        if e == "Si":
            fila += c(AZUL, "#") + " "
        elif e == "No":
            fila += c(GRIS, ".") + " "
        else:
            fila += c(AMBAR, "?") + " "
        if (i + 1) % 20 == 0:
            L.append(fila)
            fila = "   "
    if fila.strip():
        L.append(fila)
    L.append("   " + c(AZUL, "#") + c(APAG, " con insomnio   ") +
             c(GRIS, ".") + c(APAG, " sin insomnio   ") +
             c(AMBAR, "?") + c(APAG, " no se puede decidir (%d)" % ind))
    L.append("")

    pista = "   "
    for j in range(1, 6):
        marca = c(BLANCO, "[%d]" % j) if j == k else c(APAG, " %d " % j)
        pista += marca
        if j < 5:
            pista += c(APAG, "-------")
    L.append(pista)
    # la pista mide 3 + 5*3 + 4*7 = 46 caracteres visibles
    izq, der = "cualquier molestia", "6 o 7 dias/semana"
    relleno = max(1, 46 - 3 - len(izq) - len(der) + 3)
    L.append("   " + c(APAG, izq) + " " * relleno + c(APAG, der))
    L.append("")
    L.append("   " + c(BLANCO, "<-  ->") + c(APAG, "  mover la raya      ") +
             c(BLANCO, "1-5") + c(APAG, "  saltar      ") +
             c(BLANCO, "Q") + c(APAG, "  salir"))
    L.append("")
    return L


def pintar(lineas, primera_vez):
    if COLOR:
        sys.stdout.write("\033[H" if not primera_vez else "\033[2J\033[H")
    elif os.name == "nt":
        os.system("cls")
    else:
        sys.stdout.write("\n" * 3)
    for l in lineas:
        sys.stdout.write(l.ljust(ANCHO) + "\n")
    sys.stdout.write("\033[J" if COLOR else "")
    sys.stdout.flush()


# --- teclado ----------------------------------------------------------------

def leer_tecla_windows():
    import msvcrt
    ch = msvcrt.getch()
    if ch in (b"\x00", b"\xe0"):
        ch2 = msvcrt.getch()
        return {b"K": "izq", b"M": "der"}.get(ch2, "")
    if ch in (b"q", b"Q", b"\x1b"):
        return "salir"
    if ch in (b"1", b"2", b"3", b"4", b"5"):
        return ch.decode()
    return ""


def leer_tecla_unix():
    import tty, termios
    fd = sys.stdin.fileno()
    viejo = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            sig = sys.stdin.read(2)
            return {"[D": "izq", "[C": "der"}.get(sig, "salir")
        if ch in ("q", "Q"):
            return "salir"
        if ch in "12345":
            return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, viejo)
    return ""


def main():
    tabla = cargar()
    k = 3

    if PRUEBA:
        for l in cuadro(tabla, k):
            print(l)
        print("  [prueba: un solo cuadro, sin teclado]")
        return

    if os.name == "nt":
        leer = leer_tecla_windows
    else:
        if not sys.stdin.isatty():
            for l in cuadro(tabla, k):
                print(l)
            print("  (sin teclado disponible)")
            return
        leer = leer_tecla_unix

    if COLOR:
        sys.stdout.write("\033[?25l")        # esconde el cursor
    primera = True
    try:
        while True:
            pintar(cuadro(tabla, k), primera)
            primera = False
            t = leer()
            if t == "salir":
                break
            elif t == "izq":
                k = max(1, k - 1)
            elif t == "der":
                k = min(5, k + 1)
            elif t in "12345" and t:
                k = int(t)
    finally:
        if COLOR:
            sys.stdout.write("\033[?25h\n")  # devuelve el cursor
        sys.stdout.flush()
    print()


if __name__ == "__main__":
    main()
