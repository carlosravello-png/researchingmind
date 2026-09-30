# -*- coding: utf-8 -*-
"""
prueba_entorno.py — Fase 1. Comprueba que todo lo necesario esta instalado.
Se corre con:   python prueba_entorno.py
Si termina con "ENTORNO LISTO", la demo del COS va a funcionar.
"""
import sys, os, platform

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

print()
print("=" * 58)
print("  PRUEBA DE ENTORNO")
print("=" * 58)
print("Python   :", sys.version.split()[0])
print("Sistema  :", platform.system(), platform.release())
print("Ejecutable:", sys.executable)
print("Carpeta  :", os.getcwd())
print("-" * 58)

paquetes = ["pandas", "numpy", "matplotlib", "scipy", "statsmodels"]
faltan = []
for nombre in paquetes:
    try:
        mod = __import__(nombre)
        print("  OK    %-12s %s" % (nombre, getattr(mod, "__version__", "?")))
    except ImportError:
        print("  FALTA %-12s <-- hay que instalarlo" % nombre)
        faltan.append(nombre)

print("-" * 58)
if faltan:
    print("Faltan paquetes. Instalalos con:")
    print("   python -m pip install " + " ".join(faltan))
    sys.exit(1)

# Prueba real de cada pieza
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 5, 4, 5]})
r = stats.pearsonr(df["x"], df["y"])
lo, hi = proportion_confint(27, 55, alpha=0.05, method="wilson")

print("  pandas     -> DataFrame de %d filas" % len(df))
print("  numpy      -> media = %.2f" % np.mean(df["y"]))
print("  scipy      -> r de Pearson = %.3f (p = %.3f)" % (r[0], r[1]))
print("  statsmodels-> IC 95%% Wilson de 27/55 = %.1f%% - %.1f%%" % (100*lo, 100*hi))

fig, ax = plt.subplots(figsize=(5, 3))
ax.plot(df["x"], df["y"], marker="o")
ax.set_title("Gráfico de prueba")
fig.tight_layout()
fig.savefig("prueba_grafico.png", dpi=150)
plt.close(fig)
print("  matplotlib -> guardado 'prueba_grafico.png'")

print("-" * 58)
print("  ENTORNO LISTO")
print("=" * 58)
print()
