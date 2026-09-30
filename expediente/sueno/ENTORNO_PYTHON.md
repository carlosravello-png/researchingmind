# Cómo correr la demo del COS en tu PC (PowerShell)

Todo esto lo corres **tú**. Yo no ejecuto nada en tu máquina.

> **Tu máquina concreta:** tienes **Miniconda con Python 3.13.5** instalado en
> `C:\Users\RAVELLO CAMACHO\miniconda3`. Por eso el comando es **`python`**, no `py`.
> Miniconda no instala el lanzador `py`; en un Python bajado de python.org sí existe.
> Si alguna vez copias una guía de internet que use `py`, en tu PC va a fallar:
> cámbialo por `python` y funciona.

---

## Paso 0 — Abrir PowerShell en la carpeta correcta

Abre el Explorador, entra a `Documentos\PSICOLOGIA CARLOS\investigacion`,
haz clic en la barra de dirección, escribe `powershell` y pulsa Enter.

Para confirmar dónde estás:

```powershell
pwd
```

Debe terminar en `...\PSICOLOGIA CARLOS\investigacion`. Si estás un nivel arriba:

```powershell
cd investigacion
```

---

## Paso 1 — Confirmar Python

```powershell
python --version
```

Debe responder `Python 3.13.5`. Si responde eso, no instales nada más.

Si alguna vez quieres saber **cuál** de los Python instalados se está usando:

```powershell
where.exe python
```

El primero de la lista es el que gana. En tu PC es el de `miniconda3`. El segundo,
el de `WindowsApps`, es un atajo falso que trae Windows y que abre la Microsoft Store;
no lo uses nunca.

---

## Paso 2 — Instalar las librerías (una sola vez, con internet)

```powershell
python -m pip install --upgrade pip
python -m pip install pandas numpy matplotlib scipy statsmodels
```

Escribe `python -m pip`, no `pip` a secas. Tienes dos Python en el PATH; `pip` solo
podría instalar en el que no estás usando, y después el script te diría que falta una
librería que juraste haber instalado. `python -m pip` instala siempre en el mismo
Python que ejecuta tus scripts. Es la causa número uno de "pero si ya lo instalé".

*(Alternativa, si alguna vez prefieres el gestor nativo de Miniconda:
`conda install -c conda-forge pandas numpy matplotlib scipy statsmodels`.
Hace lo mismo; con pip son menos pasos y no necesitas activar ningún entorno.)*

---

## Paso 3 — Comprobar que quedó bien

```powershell
python prueba_entorno.py
```

Imprime la versión de cada librería, hace una prueba real de cada una (un DataFrame,
una correlación, un intervalo de confianza) y guarda `prueba_grafico.png`.

Si termina en **ENTORNO LISTO**, ya está.
Si alguna dice `FALTA`, el propio script te imprime el comando para instalarla.

---

## Paso 4 — Comprobar que funciona sin internet

En clase puede no haber wifi, así que pruébalo antes:

1. Desactiva el wifi o pon modo avión.
2. Vuelve a correr `python prueba_entorno.py`.
3. Debe dar exactamente lo mismo.
4. Reactiva el wifi.

Las librerías ya están en tu disco y ninguna sale a internet para trabajar. El único
momento que necesitó red fue el Paso 2.

---

## Paso 5 — Correr la demo

```powershell
python demo_cos.py
```

Un solo comando, sin editar nada. Imprime los pasos con pausas para que narres,
saca la tabla de prevalencias y guarda `prevalencia_cos.png` más una copia en
`respaldo\prevalencia_cos_respaldo.png`.

Para abrirlo desde la misma consola:

```powershell
start prevalencia_cos.png
```

---

## Si salen caracteres raros (Ã±, â€”)

Es la consola, no el script. Antes de correr:

```powershell
chcp 65001
```

Pone la consola en UTF-8 para esa sesión. El PNG nunca se ve afectado.

---

## Chuleta para el aula

```powershell
cd "$HOME\Documents\PSICOLOGIA CARLOS\investigacion"
python demo_cos.py
start prevalencia_cos.png
```

Tres líneas. Si algo falla en vivo, abre directamente
`respaldo\prevalencia_cos_respaldo.png` y sigue con la clase sin detenerte.

---

## Qué hace cada librería, por si preguntan

| Librería | Para qué la usa el script |
|---|---|
| **pandas** | Leer el CSV y recorrer los 57 protocolos fila por fila |
| **numpy** | Posiciones de las barras y cálculo de los bigotes |
| **matplotlib** | Dibujar y guardar el gráfico |
| **statsmodels** | El intervalo de confianza de Wilson |
| **scipy** | No la usa la demo; queda lista para las correlaciones (Spearman) del análisis |

---

## Un apunte sobre el intervalo de Wilson

Con muestras chicas el intervalo clásico (Wald) se rompe: en el hipersomnio, donde
0 de 57 dieron positivo, Wald daría de 0 % a 0 %, como si tuvieras certeza absoluta.
Wilson devuelve **0 % – 6,3 %**, que es lo honesto: con 57 personas no puedes descartar
una prevalencia real de hasta 6 %. Ese es el argumento si alguien pregunta por qué no
usaste la fórmula del libro.
