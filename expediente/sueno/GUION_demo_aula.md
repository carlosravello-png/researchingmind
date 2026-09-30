# Guion — «Dónde ponemos la raya» (versión para proyectar)

```powershell
cd "$HOME\Documents\PSICOLOGIA CARLOS\investigacion"
chcp 65001
python demo_aula.py
```

Antes de empezar, agranda la letra de la consola. En Windows Terminal, Ctrl + rueda
del mouse. En la consola clásica, clic derecho en la barra de título → Propiedades →
Fuente. Pruébalo el día anterior, no en el aula.

---

## La idea que sostiene todo

Una sola, y se dice en la primera línea: **la cifra de un diagnóstico no sale sola de
la gente; sale de la gente y de la raya que alguien decidió**.

Todo lo demás está al servicio de eso.

---

## Los siete bloques

Se avanza con Enter. Nada corre solo.

### 1. Dónde ponemos la raya
Presentación. Cinco líneas escribiéndose. Dices que hoy no van a ver si los alumnos
de Biológicas duermen bien, sino algo más incómodo.

### 2. Primero, algo que ya conocen — **el bloque clave**
La analogía de la nota aprobatoria. Si apruebas con 11 aprueba media clase, si
apruebas con 18 aprueban dos, y nadie estudió distinto.

**No lo leas de la pantalla: pregúntaselos.** «¿Cuántos aprobarían este curso si la
nota mínima fuera 18?» Que ellos digan «menos». Ya entendieron todo el trabajo; lo
que sigue es aplicarlo.

### 3. Lo que les preguntamos
La pregunta del cuestionario, literal, y las cinco respuestas posibles en palabras.
Después salen tres cuestionarios reales con lo que contestaron. Aquí dejas claro que
nada está inventado.

### 4. Ahora movemos la raya
Sale **49** en letras grandes, y debajo «27 de cada 55 personas». Enter. Sale **2**,
y debajo «1 de cada 57». Enter. Y el recuadro: nadie durmió distinto.

Recién entonces dices de dónde salen esas dos rayas: la de 3 días es de la CIE-10, la
de 6 es del DSM-IV. Las dos son oficiales, las dos se usan, y dan resultados que no
se parecen.

Al final te pide un número. Pídeselo a la clase: «díganme uno». Tecleas el que digan.

### 5. Y si preguntáramos a otras 55 personas
Aquí explicas el intervalo sin nombrarlo. La bolsa con 55 papelitos, sacar y
devolver. Salen tres sorteos, uno por uno, y cada uno da distinto. Después 10 000 de
golpe y el rango se estabiliza entre 36 % y 62 %.

La frase para decir encima: «por eso la cifra nunca va sola, va con su rango». La
palabra *intervalo de confianza* aparece al final, entre paréntesis, solo por si
alguien la busca después.

### 6. Los dos cuestionarios incompletos
La objeción anticipada. Peor caso 47 %, mejor caso 51 %, lo reportado 49 %. La
conclusión no se mueve. Si el profesor iba a preguntarlo, ya se lo respondiste.

### 7. Qué les pasa, exactamente
De las 27 personas con insomnio, 21 duermen y no descansan; solo 7 se despiertan de
noche. Barras de texto, se lee de lejos.

Dices tú la limitación antes que nadie: son 27 personas, esto describe, no concluye.

### Cierre
Tres frases y se acabó.

---

## Tiempo

Ocho a diez minutos con las pausas. Si vas corto, el bloque 7 se salta sin que se
note. Si te sobra, el bloque 4 aguanta todas las preguntas que quieran.

## Si algo falla

Las tres imágenes quedan guardadas en la carpeta y en `respaldo\`. Las abres y sigues.

## Lo que no debes decir

- Que un criterio es mejor que el otro. No lo sabemos y el demo no lo muestra.
- Que el 49 % vale para los universitarios de Trujillo. Vale para estos 57.
- Que el bloque 7 explica por qué duermen mal. Solo describe qué marcaron.

---

## Los dos scripts anteriores siguen ahí

- `demo_cos.py` — la tabla completa de los tres diagnósticos, con hipersomnio. Es el
  que sostiene los resultados del informe.
- `demo_umbral.py` — la versión técnica de este mismo demo, con los intervalos y el
  bootstrap explícitos. Sirve si algún día lo presentas ante alguien con estadística.

`demo_aula.py` es el de la clase.
