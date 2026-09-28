# PINTINTÍN — Los bots y sus dificultades

**Qué hace cada nivel, cuánto juega, cuánto cuesta, y cómo usarlos en un juego**

28 de septiembre de 2026 · reglamento v1.8 (mediciones con la lectura anterior salvo donde se indica)

---

## 0. La métrica

Todo bot se mide igual: **% de rondas en que queda último** (solo pierde el tercero), con asientos rotados. Neutro = 33,3%; menos es mejor.

Se reportan dos varas:

- **Contra dos Maestros** — la vara exigente. Es la que separa de verdad a los bots buenos.
- **Contra dos Jugadores** (nivel 3) — la vara histórica del proyecto. Infla las diferencias, pero sirve para comparar con los documentos anteriores.

Metodología completa en `pintintin-metodologia.md`.

---

## 1. La escalera completa

| Nivel | Nombre | Qué añade | vs 2 Maestros | vs 2 Jugadores | Elo (liga) | Tiempo por jugada* |
|---|---|---|---|---|---|---|
| 1 | **Novato** | Juega al azar | 53,4% | 49,2% | 850 | ~0 |
| 2 | **Casual** | La más alta que no le quite cobertura | 42,1% | 38,7% | 933 | 0,02 ms |
| 3 | **Jugador** | **Cuenta los fallos**: deja puntas que los rivales ya fallaron | 37,8% | 32,9% | 957 | 0,02 ms |
| 4 | **Fogueado** | **Cierra la mesa**: puntas a las que responden pocas fichas que no ve | 33,7% | 28,0% | 1000 | 0,07 ms |
| 5 | **Maestro** | Cerco y cebo del palo largo | 33,3% | 27,0% | 1000 | 0,08 ms |
| 5b | **Balance** | **Balance de respuestas**: puntas donde él responde más que ellos | **31,6%** | **25,7%** | 1017 | 0,05 ms |
| 6 | **Sabio 24** | Simula el resto de la mano, 24 repartos | 33,6% | — | — | 9 ms |
| 6 | **Sabio 96** | … 96 repartos | **30,4%** | **21,5%** | — | 32 ms |
| 6 | **Sabio 192** | … 192 repartos | **28,3%** | — | — | 60 ms |
| — | *Omnisciente* | *Ve las manos y simula (techo, no es jugable)* | *15,5%* | *0,2%* | — | 1 ms |

\* Python 3.9 en un núcleo de una Mac de 12 núcleos. En JavaScript moderno debería ser bastante más rápido; hay que medirlo al portar.

**Fuentes**: 12.000 rondas por casilla (bots heurísticos), 3.000 (Sabio), 90.000 en tres juegos de semillas (Balance). Elo de la liga de 120.000 rondas (Maestro = 1000). Salidas en `datos/`.

**Con el reglamento v1.8** (tranca sin pase, la pila mata la cara), 30.000 rondas contra dos Maestros: control 33,0% · Jugador 39,8% · Fogueado 33,4% · **Balance 30,4%**. El orden no cambia y Balance se separa más (auditoría §4.12).

### Tres cosas que muestra la tabla

1. **El salto grande está entre el 3 y el 4.** Cerrar la mesa vale 4 puntos contra rivales buenos. Del 4 al 5 no hay diferencia medible: el cerco y el cebo no se notan entre bots competentes.
2. **Balance es el mejor bot barato.** Cuesta menos que el Maestro y le saca 1,8 puntos. Salió de una búsqueda automática y se confirmó imitando al Sabio (auditoría §4.11).
3. **El Sabio escala con el cálculo.** Con 24 repartos es ruido; con 96 y 192 baja 3 y 5 puntos. La curva todavía no se aplana.

---

## 2. Cada nivel por dentro

Todos ven solo **información pública**: su mano, la mesa, el marcador, cuántas fichas tiene cada quien y los **vacíos demostrados** (los números que cada rival mostró no tener al pasar). Ninguno mira manos ajenas, salvo el Omnisciente.

Nomenclatura:

- **ahogo** — por cada rival, 2 si ya falló las dos puntas que dejo, 1 si falló una.
- **amenaza** — cuántas fichas que no veo (manos rivales + pila) sirven a las puntas que dejo.
- **cobertura** — cuántas fichas mías sirven a las puntas que dejo.
- **peso** — puntos de la ficha que juego.

Los niveles 2 a 5 eligen por **orden lexicográfico** (el primer criterio manda; los demás desempatan). Balance usa una **suma ponderada**.

### Nivel 1 · Novato
```
elige una jugada legal al azar
```
Sirve de piso. En una mesa de buenos pierde más de la mitad de las rondas.

### Nivel 2 · Casual
```
máx (cobertura, peso)
```
Suelta la más pesada que no lo deje sin respuesta. Es lo que hace un jugador de casa que "no se estrecha".

### Nivel 3 · Jugador
```
máx (ahogo, cobertura, peso)
```
**Cuenta los fallos.** Es la técnica humana más rentable por esfuerzo: dos frases por rival (*"el de la derecha no tiene treses ni seises"*).

### Nivel 4 · Fogueado
```
máx (ahogo, −amenaza, cobertura, peso)
```
**Cierra la mesa**: entre jugadas sin cobro, deja las puntas a las que responden menos fichas que no ve.

### Nivel 5 · Maestro
```
máx (ahogo, −amenaza, cerco, cebo, cobertura, peso)
```
Con 4+ de un palo, prefiere poner puntas en su palo (**cerco**) o en los números que le faltan de su palo (**cebo**), para que el rival se los sirva. Medido: no suma sobre el Fogueado. Se mantiene como referencia histórica y como **vara** de todas las mediciones.

### Nivel 5b · Balance
```
máx  10·ahogo − amenaza + cobertura + 0,3·peso
```
**"Primero ahoga. Después, deja las puntas donde tú tienes más respuestas que ellos."**

El Maestro cerraba la mesa a los rivales sin fijarse en si también se la cerraba a sí mismo. Balance pone su cobertura casi al mismo nivel que la amenaza: una punta difícil para todos es una punta que te va a hacer pasar a ti.

Cómo se encontró: una búsqueda evolutiva sobre 32 rasgos convergió a estos pesos, y un modelo que imita las decisiones del Sabio llegó a lo mismo. La ablación mostró que la pieza clave es la cobertura (quitarla devuelve el bot al nivel del Maestro).

### Nivel 6 · Sabio
```
para cada jugada posible:
    repetir K veces:
        repartir las fichas que no veo entre las dos manos rivales y la pila,
            respetando cuántas tiene cada quien y los vacíos demostrados
        jugar el resto de la mano (todos con la política del nivel 3)
        valor += P(no quedar último | marcador final)   ← tabla medida
elegir la jugada de mayor valor
```

Es **Monte Carlo con información perfecta por muestreo** (PIMC): trata cada reparto posible como si fuera la verdad, simula, y promedia.

Dos piezas lo hacen funcionar:

- **La tabla de valor** (`motor/tabla_valor.json`): P(quedar último) según mi marcador, los otros dos, y si salgo yo en la próxima mano, medida en 60.000 rondas de Maestros. Convierte "puntos" en lo único que importa. Juzgar por puntos en vez de por la tabla lo empeora (35,8% contra 33,6% con 24 repartos).
- **Repartos compartidos**: todas las jugadas candidatas se prueban sobre los mismos K repartos, para que la comparación entre ellas no dependa de la suerte del muestreo.

**La dificultad se regula con K**: 24 ≈ Maestro, 96 ≈ fuerte, 192 ≈ muy fuerte.

### Omnisciente (solo referencia)

El Sabio, pero con las manos verdaderas en vez de repartos. No es un bot jugable: marca el **techo** de lo que se gana con información. Contra dos Maestros pierde 15,5%; contra dos Jugadores, 0,2% (porque además simula exactamente la política de sus rivales).

---

## 3. Lo que NO mejoró a ningún bot

Medido contra dos Maestros (auditoría §4.5, §4.8–4.11):

| Idea | Resultado |
|---|---|
| Leer el marcador (jugar distinto en 120+, alianza contra el último) | Empate |
| Salida con doble con más compañeras (regla explícita) | Empate (el Maestro ya lo hace) |
| Hacerse cómplice del único líder | +8 a +10 puntos **peor** |
| Planes de remontada (tranca, dominar) yendo último | +2 a +6 **peor** |
| Farolear rompiendo la pinza | +5 **peor** |
| "Repite, mata y tranca" como regla | +5 a +10 **peor** |
| Leer pinzas rotas (Lector) | Empate (lectura acertada 85%, sin ventaja) |
| 44 reglas de los documentos como prioridad única | Ninguna mejora; diez empeoran |

---

## 4. Recomendación para un juego

| Dificultad en pantalla | Bot | Pierde vs 2 Maestros | Nota |
|---|---|---|---|
| **Aprendiz** | Casual (2) | 42% | Juega "normal", sin contar. Un principiante le gana |
| **Intermedio** | Jugador (3) | 38% | Cuenta los fallos. Castiga al que no cuenta |
| **Avanzado** | Fogueado (4) o Maestro (5) | 33% | Cierra la mesa. Nivel de jugador fuerte de club |
| **Experto** | Balance (5b) | 32% | El mejor bot instantáneo |
| **Maestro** | Sabio 96–192 | 28–30% | Necesita un hilo de fondo (Web Worker) |

Recomendaciones de diseño:

- **El Novato no sirve como dificultad**: juega tan mal que se siente roto. Úsalo solo para pruebas.
- **Mesas mixtas**: dejar elegir la dificultad **por asiento**. El Elo de la liga (§1) sirve para emparejar.
- **Hacer los bots "humanos"**: tiempos de reacción variables (más rápidos cuando hay una sola jugada), y en niveles bajos, un pequeño porcentaje de jugadas del nivel inferior.
- **El Sabio necesita semillas**: para reproducir una partida, guardar la semilla de su generador de repartos.

---

## 5. Archivos

| Archivo | Contenido |
|---|---|
| `motor/motor_pintintin.py` | Niveles 1–5 y 5b (`NIVELES`) |
| `motor/laboratorio.py` | Sabio (`hacer_sabio`), Omnisciente, simulador rápido de rollouts, tabla de valor |
| `motor/campana.py` | Política por especificación (lexicográfica o lineal), búsqueda evolutiva, imitación, liga |
| `motor/tabla_valor.json` | La tabla de P(quedar último) |
| `apps/dojo-pintintin.html` | Los niveles 1–5 en JavaScript, jugables en el navegador |
