"""
preparar_datos_publicos.py
==========================

Genera la version publica de los datos del Cuestionario Oviedo de Sueno (COS)
aplicado el 14/09/2026 a 58 estudiantes de Ciencias Biologicas (UNT); N = 57.

Que hace:
  1. Lee los datos crudos, que NO estan en este repositorio.
  2. Quita lo que un participante escribio con sus propias palabras
     (texto libre de los items 11 y "ayuda para dormir"), el nombre del
     escaneo de cada protocolo y las fechas.
  3. Reasigna los codigos al azar. Los codigos originales se entregaron a
     cada participante para que pudiera pedir su devolucion; publicarlos
     permitiria a cualquiera que conozca un codigo ver esos datos. La tabla
     de correspondencia no se guarda en ningun lado.
  4. Conserva los items, las puntuaciones, los diagnosticos y las notas de
     codificacion, que son el rastro de auditoria.
  5. Comprueba que las prevalencias publicas coinciden con las del informe
     y solo entonces escribe los archivos. Si algo no cuadra, no escribe nada.

Uso (PowerShell, desde la raiz del repositorio):
    python site\\datos\\preparar_datos_publicos.py

Solo usa la biblioteca estandar de Python: no hay que instalar nada.
"""

import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path

# --- Rutas ------------------------------------------------------------------
# argv[1] = carpeta de salida (por defecto, la carpeta de este script)
# argv[2] = carpeta con los datos crudos (por defecto, Documentos\PSICOLOGIA CARLOS)
DESTINO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
ORIGEN = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.home() / "Documents" / "PSICOLOGIA CARLOS"

CSV_IN = ORIGEN / "investigacion" / "cos_codificado.csv"
JSON_IN = ORIGEN / "cos_datos.json"
CSV_OUT = DESTINO / "cos_publico.csv"
JSON_OUT = DESTINO / "cos_publico.json"

# --- Lo que sale ------------------------------------------------------------
FUERA_CSV = {"i11_texto", "fecha"}
FUERA_JSON = {"archivo", "codigo_manuscrito", "fecha_manuscrita",
              "fecha_registrada", "ayuda_para_dormir_texto"}

# --- Lo que tiene que dar, segun el informe -----------------------------------
ESPERADO = {"n": 57, "cie10_si": 27, "cie10_indet": 2, "dsmiv_si": 1, "hiper_si": 0}


def fallar(msg):
    print("\n  ERROR: " + msg)
    print("  No se escribio ningun archivo.\n")
    sys.exit(1)


def main():
    for f in (CSV_IN, JSON_IN):
        if not f.exists():
            fallar("no encuentro %s" % f)

    filas = list(csv.DictReader(open(CSV_IN, encoding="utf-8-sig")))
    crudo = json.load(open(JSON_IN, encoding="utf-8"))
    participantes = crudo["participantes"]

    if len(filas) != ESPERADO["n"] or len(participantes) != ESPERADO["n"]:
        fallar("esperaba %d casos y hay %d en el CSV y %d en el JSON"
               % (ESPERADO["n"], len(filas), len(participantes)))

    # 1. Codigos nuevos al azar, sin semilla: la correspondencia no se puede reconstruir
    originales = [int(f["codigo"]) for f in filas]
    if sorted(originales) != sorted(int(p["codigo"]) for p in participantes):
        fallar("el CSV y el JSON no tienen los mismos codigos")
    barajados = originales[:]
    random.SystemRandom().shuffle(barajados)
    nuevo = {viejo: i + 1 for i, viejo in enumerate(barajados)}

    # 2. CSV publico
    columnas = [c for c in filas[0].keys() if c not in FUERA_CSV]
    filas_pub = []
    for f in filas:
        g = {c: f[c] for c in columnas}
        g["codigo"] = "%03d" % nuevo[int(f["codigo"])]
        filas_pub.append(g)
    filas_pub.sort(key=lambda g: g["codigo"])

    # 3. JSON publico
    part_pub = []
    for p in participantes:
        q = {k: v for k, v in p.items() if k not in FUERA_JSON}
        q["codigo"] = "%03d" % nuevo[int(p["codigo"])]
        part_pub.append(q)
    part_pub.sort(key=lambda q: q["codigo"])
    publico = {
        "instrumento": crudo.get("instrumento"),
        "fecha_aplicacion": crudo.get("fecha_aplicacion"),
        "n": ESPERADO["n"],
        "nota_muestra": "58 protocolos aplicados; uno se excluyo porque su escaneo "
                        "resulto identico al de otro protocolo. N = 57.",
        "nota_publica": "Version publica. Se retiraron el texto libre escrito por los "
                        "participantes, el nombre del escaneo y las fechas, y los codigos "
                        "se reasignaron al azar. Items, puntuaciones, diagnosticos y notas "
                        "de codificacion se conservan sin cambios.",
        "reglas": crudo.get("reglas"),
        "participantes": part_pub,
    }

    # 4. Comprobaciones
    for g in filas_pub:
        if FUERA_CSV & set(g):
            fallar("quedo una columna prohibida en el CSV")
    for q in part_pub:
        if FUERA_JSON & set(q):
            fallar("quedo un campo prohibido en el JSON")

    cie = Counter(g["dx_insomnio_cie10"] for g in filas_pub)
    dsm = Counter(g["dx_insomnio_dsmiv"] for g in filas_pub)
    hip = Counter(g["dx_hipersomnio"] for g in filas_pub)
    obtenido = {"n": len(filas_pub), "cie10_si": cie["Si"], "cie10_indet": cie["Indeterminado"],
                "dsmiv_si": dsm["Si"], "hiper_si": hip["Si"]}
    if obtenido != ESPERADO:
        fallar("las prevalencias no coinciden con el informe: %s" % obtenido)

    json_por_codigo = {q["codigo"]: q["puntuacion"] for q in part_pub}
    for g in filas_pub:
        pj = json_por_codigo[g["codigo"]]
        if (pj["dx_insomnio_CIE10"], pj["dx_insomnio_DSMIV"], pj["dx_hipersomnio"]) != \
           (g["dx_insomnio_cie10"], g["dx_insomnio_dsmiv"], g["dx_hipersomnio"]):
            fallar("el CSV y el JSON no coinciden en el caso %s" % g["codigo"])

    # 5. Recien ahora se escribe
    DESTINO.mkdir(parents=True, exist_ok=True)
    with open(CSV_OUT, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas)
        w.writeheader()
        w.writerows(filas_pub)
    with open(JSON_OUT, "w", encoding="utf-8") as fh:
        json.dump(publico, fh, ensure_ascii=False, indent=2)

    n_cie = ESPERADO["n"] - ESPERADO["cie10_indet"]
    pct = lambda a, b: ("%.1f" % (100 * a / b)).replace(".", ",")
    print("\n  Datos publicos generados y comprobados:")
    print("    Insomnio CIE-10 : %d/%d = %s %%" % (obtenido["cie10_si"], n_cie, pct(obtenido["cie10_si"], n_cie)))
    print("    Insomnio DSM-IV : %d/%d = %s %%" % (obtenido["dsmiv_si"], ESPERADO["n"], pct(obtenido["dsmiv_si"], ESPERADO["n"])))
    print("    Hipersomnio     : %d/%d = %s %%" % (obtenido["hiper_si"], ESPERADO["n"], pct(obtenido["hiper_si"], ESPERADO["n"])))
    print("\n    %s" % CSV_OUT)
    print("    %s\n" % JSON_OUT)


if __name__ == "__main__":
    main()
