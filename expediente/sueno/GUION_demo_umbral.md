# Guion del demo — «El umbral decide la cifra»

Archivo: `demo_umbral.py` · se corre en la carpeta `investigacion`.

```powershell
cd "$HOME\Documents\PSICOLOGIA CARLOS\investigacion"
python demo_umbral.py
```

Si salen caracteres raros, antes: `chcp 65001`.
Las librerías ya las tienes instaladas; no hace falta nada nuevo.

---

## Qué hace, en una frase

No simula datos. Toma los 57 protocolos reales y los vuelve a clasificar cambiando
una sola cosa: el número de días por semana que el criterio exige. La prevalencia
salta de 100 % a 1,8 % sin que ninguna respuesta cambie.

---

## Los cuatro bloques

El script se detiene con Enter entre bloques. Tú controlas el ritmo; nada corre solo.

### 1. El mismo dato, cinco prevalencias  (2 min)

Sale una tabla con el umbral 1 al 5 y la prevalencia de cada uno. Las dos filas
marcadas son las oficiales: umbral 3 es CIE-10 (49,1 %) y umbral 5 es DSM-IV (1,8 %).

**Lo que dices mientras aparece:** que los dos criterios no son dos instrumentos
distintos sino el mismo algoritmo con el umbral corrido, y que por eso la diferencia
entre 49,1 % y 1,8 % no habla de los estudiantes, habla del criterio.

**Luego te pide un umbral.** Escribe uno, que la clase vea el número recalcularse.
Si alguien pregunta «¿y si fuera 4?», lo tecleas y respondes con el dato: 23,2 %.

### 2. Cuánto se movería si repitiéramos el estudio  (1 min 30)

Remuestrea los 55 casos 10 000 veces y muestra cómo el intervalo se estabiliza:
con 100 remuestreos da 38,2–60,0; con 10 000 da 36,4–61,8. La fórmula de Wilson
da 36,4–61,9.

**Lo que dices:** dos caminos que no se parecen en nada llegan al mismo intervalo.
Eso es lo que significa que el intervalo no sea un adorno.

### 3. La pregunta que va a hacer el jurado  (1 min)

Los dos casos indeterminados. El script calcula los tres escenarios: 47,4 % si
ambos fueran «no», 49,1 % como se reporta, 50,9 % si ambos fueran «sí».

**Lo que dices:** la conclusión no depende de esos dos protocolos, y aquí está el
cálculo. Es la respuesta anticipada, no una defensa improvisada.

### 4. Qué dificultad sostiene el diagnóstico  (1 min)

De los 27 casos con insomnio, el sueño no reparador aparece en 21 y permanecer
dormido solo en 7. El diagrama muestra cuáles coinciden.

**Lo que dices:** esto es descriptivo y con 27 casos no sostiene inferencia. Dilo tú
antes de que lo diga él.

---

## Total

Unos cinco minutos de máquina. Con lo que hables encima, entre ocho y diez.
Si vas corto de tiempo, el bloque 4 se puede saltar sin que se note.

## Si algo falla en vivo

Cada bloque guarda su PNG en la carpeta y una copia en `respaldo\`. Abres las
imágenes y sigues la clase sin detenerte.

## Lo que este demo NO afirma

- No dice que un criterio sea mejor que el otro.
- No generaliza a los universitarios de Trujillo: describe a estos 57.
- El bloque 4 es descriptivo, no una red de síntomas con inferencia detrás.

Esas tres líneas conviene tenerlas en la cabeza, porque son exactamente las tres
cosas que un profesor con criterio va a intentar.
