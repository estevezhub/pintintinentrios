# PINTINTÍN — Bitácora del proyecto

**Documento de traspaso. Léelo primero.**

28 de septiembre de 2026

---

## Qué es esto

**Pintintín** es una variante dominicana de dominó para tres jugadores. **No existe ningún otro análisis de este juego** — ni artículo, ni reglas publicadas, ni estudio. Lo comprobé buscando a fondo: la única fuente escrita conocida es *El juego de dominó* de Frank Nicolás C. (Cervecería Nacional Dominicana, Santo Domingo, ~199?), que **no está digitalizado** y solo está en la Biblioteca Nacional.

Este proyecto reconstruyó el reglamento desde la tradición oral, lo midió con simulación, y construyó herramientas para jugarlo y estudiarlo.

**Fuente del reglamento: un solo informante**, jugador habitual. Eso es un testimonio, no un estándar. Otras mesas dominicanas pueden jugar variantes.

---

## Lo que existe hoy

| Pieza | Qué es |
|---|---|
| `pintintin-reglas.md` | **El reglamento, v1.7.** Reconstruido y cerrado. Base de todo lo demás |
| `pintintin-estrategia.md` | Estrategia medida: alianzas, cerco, conteo, palos frágiles |
| `pintintin-god-mode.md` | **El análisis profundo.** 12 partes, todo con porcentajes medidos |
| **Mesa de Pintintín** (artifact) | Laboratorio: armas cualquier posición y el motor te dice qué paga |
| **Dojo de Pintintín** (artifact) | Juegas contra 2 bots, con revisión de cada jugada y análisis de mano |

---

## Cómo se llegó aquí (y qué aprender del proceso)

El reglamento salió de conversación, pero **la conversación sola no bastó**. Tres reglas quedaron mal escritas hasta que una máquina tuvo que implementarlas:

1. **El pase.** Tres explicaciones sucesivas se contradecían. La regla real —*en la salida paga cada rival que falla; durante la mano hacen falta los dos*— solo apareció cuando el simulador obligó a distinguir "30 por rival" de "30 por jugada". En la mesa nunca hace falta separarlas: se juega y ya.
2. **El techo de 120** no era una regla, era una consecuencia: *un bono nunca puede llevarte a 150*. Con el bono mínimo de 30, eso hace que desde 120 los bonos no sirvan.
3. **La curva de la mesa** son dos fichas, no una, y un doble nunca hace el giro.

> **Lección de método:** las reglas orales viven bien en la mesa y mal en el papel. Implementarlas fuerza una precisión que preguntar no consigue.

**Errores míos que hubo que corregir** (para que no se repitan):

- Un bug de mapeo de asientos en las simulaciones hizo concluir que *ninguna técnica le ganaba al azar*. Era falso: corregido, contar los fallos vale **−14 puntos**.
- Afirmé que convenía salir con blanco o uno. Es al revés: **doble siempre**, paga 4-25× más.
- Afirmé que el líder congelado en 120 quedaba vulnerable. Queda **96,5% seguro**.
- El evaluador de jugadas usaba **un solo orden de prioridades** y marcaba como errores jugadas buenas de otro plan. Ver "los tres planes" abajo.

---

## El reglamento en 10 líneas

- Doble-seis **sin** `0/0`, `0/1`, `1/1` → **25 fichas, 165 puntos**.
- 3 jugadores, 7 fichas cada uno, **4 en la pila que no se usan**.
- Turno **a la derecha**. Primera jugada oficial: sale el **doble más alto, automático**. Después sale el ganador anterior con lo que quiera.
- **Pase:** 30 por cada cara viva. **En la salida paga cada rival que falla; en la mano hacen falta los dos.** Tope 60 por jugada.
- **Cara muerta** (todas sus fichas en la mesa) no cuenta.
- **Dominada:** suma de las fichas de los otros dos. **Capicúa:** +30.
- **Tranca:** la mano más baja gana la suma de **las tres** manos. Empate → preferencia del que trancó.
- **Techo:** un bono nunca lleva a 150. Desde 120 los bonos no suman.
- **Meta 150. Solo pierde el tercero.** Primero y segundo ganan igual.
- **Pasar con ficha:** el infractor pierde la ronda, marcador a 0 – 0 – 0.

---

## El motor

Implementado dos veces: **Python** (para simular masivamente) y **JavaScript** (dentro de los artifacts). Misma lógica.

### Núcleo de reglas

Estado: posición de cada ficha (`mano0/1/2`, `pila`, `mesa`), cadena ordenada con sus dos extremos, marcador, turno, y **los fallos demostrados por cada jugador**.

Las dos funciones que lo deciden todo:

```
carasVivas()  = números distintos en los extremos que aún tienen fichas sin jugar
pase(i)       = 30 × carasVivas, a quien jugó de último
                · en la salida: por cada rival que falla
                · en la mano: solo cuando fallan los dos
                · recortado para que nunca alcance 150
```

### Los bots (5 niveles)

Cada nivel **añade una herramienta** a la anterior. El orden sale de lo medido, no de la intuición:

| Nivel | Añade | Pierde |
|---|---|---|
| 1 Novato | azar | 33% |
| 2 Casual | suelta alto sin estrecharse | ~26% |
| 3 Jugador | **cuenta los fallos demostrados** | **19,4%** |
| 4 Fogueado | **predice**: cuántas fichas sin ubicar sirven a las puntas | — |
| 5 Maestro | **cerco, cebo, y anti-cebo** (evita el palo que el rival repite) | **27,3%** contra dos del nivel 3 |

Función de decisión del maestro, en orden lexicográfico:

```
cobro → −amenaza → cerco → cebo → −ajeno → cobertura → peso
```

Probé cuatro ordenamientos distintos antes de fijar este. **33,3% es el punto neutro** (solo pierde uno de tres), así que menos es mejor.

### El analizador de jugadas

Lo que hace único al Dojo. Para cada jugada del humano calcula **dos evaluaciones**:

- **Con información pública** (lo que él podía saber): fallos demostrados, tamaños de mano, fichas en la mesa.
- **Con la verdad** (el motor ve las manos de los bots).

La diferencia entre ambas separa **buena decisión** de **buen resultado**:

> *"Había una jugada que los ahogaba a los dos — pero no había forma de saberlo. Buena decisión, mal resultado."*

### Los tres planes

**Corrección central, y el concepto más importante del proyecto.** No hay una jugada correcta: hay tres planes legítimos y excluyentes.

| Plan | Busca | Juega |
|---|---|---|
| **Cobro** | que fallen los dos | cerrar la mesa |
| **Tranca** | ganar el conteo | soltar peso |
| **Dominar** | salir primero | conservar respuestas |

**Una jugada es correcta si es la mejor bajo cualquiera de los tres. Solo es floja si no lo es bajo ninguno.**

Y elegir plan **es apostar**: si la mano cierra por dominada y tú jugabas a la tranca, botaste peso para nada. El Dojo da un **veredicto de plan** al final de cada mano por eso.

### El motor de inferencia

Reparte por muestreo las fichas sin ubicar entre las dos manos y la pila, respetando **tamaños de mano** y **fallos demostrados**. Resultado medido:

| | Acierto |
|---|---|
| Adivinar **dónde está** una ficha | 38–53% |
| Adivinar **si puede jugar** | **91–99%** |

**No se predicen fichas, se predice si puede jugar** — y eso es lo único que paga, porque el bono depende de si tiene *alguna* de dos números, no de cuál.

---

## Los hallazgos que mandan

| | |
|---|---|
| **Solo pierde el tercero** | Tu puntuación no importa; importa tu distancia sobre el último |
| **Ir último tras 3 manos** | 66% de perder. La trampa se cierra temprano |
| **Cruzar 120 primero** | 96,5% de no perder. Es ganar |
| **Contar los fallos** | −14 puntos. Cuesta **dos frases por rival** |
| **Techo del conteo** | 13,9% (ver las manos). Queda 5,6 de margen sobre contar |
| **La alianza** | Hunde al descuidado al 47,1%; contra quien cuenta, 34,0% |
| **Los dobles** | ~5 puntos menos de ganar la mano, cada uno |
| **Anchura vs concentración** | 7 caras gana más que 4 de un palo, y llega 44% de las veces |
| **La pila al final** | Con 2 fichas por cabeza, la mitad de lo que falta está fuera |
| **Nunca pagues con tu juego** | Toda idea de "sacrifica ahora por posición después" salió refutada |

---

# Los tres objetivos

## 1 · Biblioteca abierta del pintintín

**Meta:** que el juego exista por escrito, públicamente, por primera vez.

Contenido ya listo: reglamento v1.7, fundamentos, glosario, estrategia básica. Lo que falta:

- **Una segunda fuente.** Un reglamento con un informante es un testimonio; con dos empieza a ser un estándar. Pasar el `.md` a jugadores de otras mesas dominicanas y registrar cada discrepancia — **las discrepancias son datos, no problemas**.
- **El libro de Frank Nicolás C.** en la Biblioteca Nacional. Nadie lo ha leído en treinta años.
- Formato público: página web, o artículo de Wikipedia con las fuentes que se consigan.
- Versión corta imprimible para la mesa (el resumen de una página ya existe en el reglamento).

## 2 · Conocimiento avanzado

**Meta:** el cuerpo de estrategia medida — que es lo que ya está en el God Mode.

Lo que falta por investigar:

- **El meta-juego social**, que ninguna simulación tocó: faroleo, reputación entre rondas, alianzas habladas. Es donde el usuario dice que se juega de verdad.
- **Registro de patrones humanos**: qué errores comete la gente real, con qué frecuencia. El Dojo ya los clasifica en 7 categorías — falta acumular volumen.
- **Tiempos de reacción** como canal de información. Identificado, no medido.
- **Validar en mesa real** las afirmaciones razonadas (el reloj, atacar al segundo, cuándo se voltea la alianza). Están marcadas como razonadas, no medidas.

## 3 · Mesas de juego online

**Meta:** llevar el pintintín a mesas por invitación, con bots capaces, registro completo y análisis para todos.

### Lo que ya está resuelto

- **Reglas completas y probadas** — el motor JS del Dojo es una implementación de referencia.
- **Bots de 5 niveles**, el más alto medido como superior a un jugador que cuenta.
- **Analizador de jugadas** con los tres planes y la separación decisión/resultado.
- **Motor de inferencia** para que los bots razonen sobre lo que no ven.

### Lo que hay que construir

**Mesas e invitación.** Sala de 3 asientos, enlace de invitación. Si faltan jugadores al empezar, **se rellenan con bots** de dificultad elegida por el anfitrión. Los asientos importan (el turno corre a la derecha y solo controlas al de tu derecha), así que el orden debe ser visible y fijo.

**Estado autoritativo en el servidor.** Las manos son información oculta: el cliente **no puede** conocer las manos ajenas. El Dojo actual sí las conoce (por eso puede hacer el análisis "con la verdad"), y eso **solo funciona contra bots locales**. En línea, ese análisis se calcula **después** de la partida, cuando ya se pueden revelar.

**Registro de partidas.** Guardar la secuencia completa: reparto, cada jugada con su marca de tiempo, cada pase, cada cobro. Con eso se reconstruye todo — incluido el análisis retroactivo con información perfecta.

**Análisis para el usuario.** Al terminar: sus jugadas clasificadas, veredicto de plan por mano, decisiones reales contra decisiones forzadas, y el acumulado de aciertos. Ya existe en el Dojo; en línea solo cambia dónde se calcula.

**Bots que aprenden.** El camino realista, en orden:

1. **Recolectar** partidas humanas con su análisis. Sin volumen no hay nada.
2. **Medir contra el baseline.** Cualquier bot nuevo se enfrenta al maestro actual; si no baja de 27,3%, no mejoró. *La métrica siempre es el % de rondas en que queda último, sobre 33,3% neutro.*
3. **Ajustar los pesos** del maestro con los datos reales antes de intentar nada más complejo. El orden lexicográfico actual salió de probar cuatro variantes a mano — con datos se puede optimizar en serio.
4. **Solo después**, aprendizaje por refuerzo con auto-juego. Y aun así, medirlo contra el baseline.

> **Advertencia importante:** el bot debe aprender a **no quedar último**, no a maximizar puntos. Son objetivos distintos y es el error más fácil de cometer. Toda la estructura del juego cuelga de eso.

**Lo social, que es lo que falta de verdad.** Las alianzas son el 13,8% de efecto medido y ningún bot las usa. Un bot que lea el marcador y coordine implícitamente con el otro de arriba sería el salto grande — y es **exactamente lo que un humano hace sin pensarlo**.

---

## Para el siguiente agente

**Empieza por aquí:**

1. Lee `pintintin-reglas.md` entero. Es corto y todo lo demás depende de él.
2. Del God Mode, lee las Partes 1 (estructura), 8 (evaluar jugadas) y 11 (método de conteo). El resto es consulta.
3. Abre el Dojo y juega tres manos. Se entiende más rápido jugando que leyendo.

**Cuidados:**

- **Cualquier afirmación nueva con porcentaje debe medirse**, no razonarse. Este proyecto ya tuvo tres conclusiones razonadas que la medición refutó, y están documentadas como tales.
- **Distingue medido de razonado** en todo lo que escribas. El God Mode lo hace explícito y conviene mantenerlo.
- **El reglamento tiene una sola fuente.** Antes de tratarlo como canónico, consíguete la segunda.
- **No optimices el bot para puntos.** Solo pierde el tercero.
