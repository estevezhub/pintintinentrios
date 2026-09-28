# PINTINTÍN — Auditoría del motor y de las estrategias

**Revisión independiente: pruebas, remediciones y propuestas nuevas**

28 de septiembre de 2026 · reglamento v1.7

---

## 0. Resumen

| | |
|---|---|
| **El motor** | Correcto. 21 pruebas contra los casos del reglamento, todas pasan. Python y los dos JS dan lo mismo |
| **Lo publicado** | Se reproduce casi todo. Tres cifras estaban mal y ya se corrigieron en los documentos |
| **La escalera de bots** | Por encima del nivel 4 no hay escalera: Fogueado, Maestro y ~20 variantes suyas empatan entre sí |
| **La mejor regla simple** | "Balance de respuestas": ahoga; después deja las puntas donde tú respondes más que ellos. **31,6%** contra dos Maestros (−1,8), descubierta por búsqueda y confirmada imitando al Sabio |
| **El salto real** | Un bot que **simula el resto de la mano** (nivel 6, "Sabio") le gana al Maestro: **28,3%** contra 33,3%, y mejora con más cálculo |
| **Techo** | Viendo las manos de verdad y simulando, se baja a **15,5%** contra dos Maestros |
| **La salida** | "Sal de doble" queda confirmado, con un matiz nuevo: **cuenta cuántas del palo traes** |
| **Reglamento v1.8** | Dos reglas resueltas: la tranca no paga pase y la pila mata la cara. Los pases valen casi la mitad; Balance se separa más (−2,6) |

Todo lo que lleva porcentaje aquí está **medido**, con intervalo de confianza del 95% entre corchetes. Lo razonado va marcado.

---

## 1. Método

- **Pruebas unitarias** (`motor/test_motor.py`): los casos de referencia del reglamento, uno por uno, más invariantes sobre 400 rondas completas (nadie cruza 150 con bonos, nunca dos a la vez, las 25 fichas siempre cuadran).
- **Laboratorio** (`motor/laboratorio.py`): torneos en paralelo, con semilla y con **intervalo de Wilson al 95%**. Se usan los mismos asientos rotados y la misma métrica del proyecto: *% de rondas en que la política queda última, neutro 33,3%*.
- **Tamaño**: 12.000 rondas por medición de bots heurísticos (±0,85 puntos), 3.000 para los bots que simulan (±1,7), 30.000 para las verificaciones.
- **Rival de referencia nuevo**: dos **Maestros**, no dos Jugadores. Medir contra rivales flojos infla todas las diferencias (§3.2 del God Mode ya lo mostraba).

```bash
python3 -m unittest motor/test_motor.py -v
python3 motor/laboratorio.py verificar
python3 motor/laboratorio.py bench maestro fogueado sabio96 --rival maestro --rondas 3000
```

---

## 2. El motor

### 2.1 Lo que está bien

- **Las reglas están implementadas correctamente.** Las 17 situaciones del reglamento (pase en la salida y en la mano, cara muerta, tope de 60, repetir con el doble, techo de 149 y de 120, dominada, capicúa, los tres desempates de la tranca, primera jugada oficial) dan exactamente lo que dice el texto.
- **Los motores JS del Dojo y de la Mesa son la misma lógica** que el Python, línea por línea en las funciones de reglas.
- **El simulador rápido** que usa el bot nuevo reproduce al motor en **6.000 de 6.000 manos**, marcador por marcador.

### 2.2 Lo que se corrigió

| Qué | Antes | Ahora |
|---|---|---|
| Muerte súbita sin dobles repartidos | El Python dejaba salir a cualquiera con cualquier ficha | Sale la ficha más alta, como en los JS (`salida_subita`) |
| Reproducibilidad | Sin semilla | `--semilla N` en el motor; el laboratorio siempre la usa |
| Regla abierta de la tranca | Implícita | Interruptor explícito `PASE_EN_TRANCA` (§6) |

### 2.3 Lo que se corrigió en los documentos

| Documento | Error | Corrección |
|---|---|---|
| Reglamento §9 | *"Salir con blanco o con uno es el mejor compromiso"* — la conclusión que la bitácora ya daba por refutada seguía escrita en el reglamento | Reescrito: sal de doble, con el dato medido |
| Estrategia §6 | Ingreso esperado de la salida: 5,5 / 1,2 / 0,2 pts | **2,8 / 0,6 / 0,1**. Estaban duplicados; la proporción entre filas se mantiene |
| Bitácora | El Maestro llevaba un término "−ajeno / anti-cebo" | Ese término se probó y se descartó; no está en ningún código |
| Estrategia | "complemento del reglamento v1.6" | v1.7 |
| God Mode | Dos secciones numeradas 11.6 | La segunda es 11.10 |

---

## 3. Lo publicado, remedido

30.000 rondas de tres Jugadores (nivel 3), el mismo escenario del God Mode:

| Hallazgo | Publicado | Remedido | |
|---|---|---|---|
| Manos por ronda | 4,94 | 4,96 | ✔ |
| Manos que trancan | 39,5% | 39,2% [39,0 – 39,5] | ✔ |
| La mano final es tranca | 50,4% | 49,9% [49,3 – 50,4] | ✔ |
| Muerte súbita | 7,1% | 7,5% [7,2 – 7,8] | ✔ |
| Último tras la 1ª mano pierde | 56,2% | 56,6% [55,6 – 57,6] | ✔ |
| Último tras la 3ª mano pierde | 65,8% | **70,8%** [70,2 – 71,4] | ⚠ más fuerte de lo publicado |
| Primero en cruzar 120 no pierde | 96,5% | 96,8% [96,6 – 97,0] | ✔ |
| Salida de doble: falla el siguiente | ~9% | 9,3% [9,1 – 9,5] | ✔ |
| Salida con blanco o uno | ~1,1% | 1,0% [1,0 – 1,1] | ✔ |
| Ingreso esperado de la salida de doble | ~5,5 pts | **2,84 pts** | ✘ corregido |

**La conclusión de "la trampa del último" sale reforzada:** tras tres manos, el que va último pierde siete de cada diez rondas, no dos de cada tres.

### La escalera, contra rivales de verdad

El benchmark del README mide contra dos Jugadores (nivel 3). Contra dos **Maestros**, 12.000 rondas:

| Política | Queda última |
|---|---|
| 1 Novato | 53,4% [52,5 – 54,3] |
| 2 Casual | 42,1% [41,2 – 43,0] |
| 3 Jugador | 37,8% [36,9 – 38,7] |
| 4 Fogueado | **33,7%** [32,8 – 34,5] |
| 5 Maestro | 33,3% (por definición) |

> ### Fogueado y Maestro son el mismo bot en la práctica.
> El cerco y el cebo, que son lo que el Maestro añade, **no se ven** contra rivales buenos.

---

## 4. Hallazgos nuevos

### 4.1 El Maestro cabe en tres palabras

Probé ~20 variantes del Maestro — órdenes lexicográficos distintos y sumas ponderadas — contra dos Maestros:

| Variante | Queda última |
|---|---|
| Maestro completo (6 términos) | 32,6% [31,8 – 33,5] |
| **Solo `ahogo → −amenaza → peso`** | **33,5%** [32,7 – 34,4] |
| Con "no perder cara" antes que "cerrar la mesa" | 37,1% [36,2 – 38,0] ❌ |
| "No perder cara" antes que "cerrar", sin cerco | 36,9% ❌ |
| Cobertura antes que "cerrar la mesa" | 39,6% ❌ |
| Penalizar soltar dobles (guardarlos) | 34,0 – 36,3% ❌ |
| Premiar soltar dobles | 32,5 – 33,6% (≈) |
| Todas las sumas ponderadas probadas | 32,5 – 34,7% (≈) |

Tres conclusiones:

1. **Todo el Maestro es: cobra si puedes; si no, cierra la mesa; si no, suelta peso.** Cerco, cebo y cobertura son desempates que no mueven nada medible.
2. **"Cerrar la mesa" va antes que "no perder cara".** Invertirlas cuesta 4 puntos. Esto matiza la regla de administración (§12 de la estrategia): la anchura vale contra rivales flojos, pero entre buenos manda dejar puntas a las que responden pocas fichas.
3. **Hay una meseta.** Ninguna reordenación ni pesos le ganan al Maestro por más del ruido. Las reglas de una sola jugada ya dieron lo que tenían: **lo que queda se gana mirando hacia adelante**.

### 4.2 El Sabio: mirar hacia adelante sí rinde

El bot nuevo de nivel 6 hace lo que hace un jugador fuerte cuando piensa en el turno ajeno:

1. **Reparte** las fichas que no ve entre las dos manos rivales y la pila, respetando lo que se sabe: cuántas tiene cada quien y qué palos ha fallado.
2. **Juega el resto de la mano** en la cabeza, una vez por cada jugada posible, sobre el mismo reparto.
3. Repite con muchos repartos y **juzga cada final por el marcador**: no por los puntos, sino por la probabilidad de no quedar último, leída de una tabla medida en 60.000 rondas (`motor/tabla_valor.json`).

| Bot, contra dos Maestros | Queda último |
|---|---|
| Sabio con 24 repartos | 33,6% [31,9 – 35,3] — no mejora: demasiado ruido |
| Sabio con 24 repartos, **juzgando por puntos** | **35,8%** [34,1 – 37,6] — peor |
| **Sabio con 96 repartos** | **30,4%** [28,8 – 32,1] |
| **Sabio con 192 repartos** | **28,3%** [26,7 – 29,9] |
| *Omnisciente: ve las manos y simula* | *15,5%* [14,9 – 16,2] |

Lo que dice esta tabla:

- **Es la primera mejora sobre el Maestro que sale del ruido**: tres a cinco puntos, contra rivales buenos.
- **El número de repartos importa, y la curva no se ha aplanado.** 24 → 33,6%, 96 → 30,4%, 192 → 28,3%. Con 24 elige casi al azar entre jugadas parecidas; cada duplicación gana unos dos puntos. En el navegador, con JavaScript, se pueden usar bastantes más.
- **Juzgar por puntos es peor que juzgar por el marcador**, también cuando se mira hacia adelante. La advertencia central del proyecto — *no optimizar por puntos* — se confirma con un método completamente distinto.
- **Queda mucho techo.** Entre 28,3% y 15,5% hay 13 puntos, y todos son información: lo que se gana deduciendo mejor las manos ajenas.

Contra dos Jugadores (nivel 3), el Sabio de 96 queda último el **21,5%** [19,5 – 23,6] de las rondas, contra 27,0% del Maestro en el mismo escenario.

### 4.3 Qué hace distinto el Sabio

En 30.391 decisiones reales, el Sabio eligió otra jugada que el Maestro el **26,7%** de las veces. Dónde:

| Momento | Difiere |
|---|---|
| Con 7 fichas en mano | 45% |
| Con 5 | 29% |
| Con 3 | 14% |
| Con 1–2 | 2–5% |
| **Salida libre** | **49%** |

> ### Las decisiones que el Maestro juega en automático son las del principio de la mano.
> Al final casi no hay opciones; al principio es donde mirar hacia adelante cambia la jugada.

Cuando difieren, el Sabio **pierde menos caras** (0,24 contra 0,32 por jugada) y **suelta algo más de peso** (6,7 contra 6,4). Otras diferencias de la tabla (que cierra menos la mesa, que cobra menos) son sesgo de selección: el Maestro elige por esos mismos criterios, así que cualquier desacuerdo los empeora por construcción. **No son reglas y no se deben leer como tales.**

### 4.4 La salida libre, jugada por jugada

Para aislar la salida usé al Sabio como oráculo: 2.400 manos al azar, cada una de las 7 fichas simulada 150 veces como salida. "Ventaja" es cuánto sube la probabilidad de no quedar último respecto de salir con una ficha media de esa mano.

| Salir con… | Ventaja | Es la mejor salida de la mano |
|---|---|---|
| **Doble** | **+2,3** | **54%** |
| · doble solo, sin otra del palo | +0,4 | 15% |
| · doble + 1 del palo | +1,9 | 44% |
| · doble + 2 del palo | +2,9 | 68% |
| · doble + 3 del palo | +3,8 | 83% |
| · doble + 4 del palo | +4,7 | 97% |
| No doble | −0,6 | 4% |
| · con blanco o uno | −0,6 | 5% |
| · de dos palos gordos | −0,6 | 4% |
| · **que te quita una cara** | **−1,5** | **0,5%** |

> ### Sal de doble. Y el doble vale tanto como las compañeras que traes de su palo.
> Con tres o más, es la mejor salida más de cuatro de cada cinco veces. **Solo**, apenas vale lo que una ficha cualquiera.
> ### La única salida claramente mala es la que te deja sin un número.

Esto confirma el §12.7 del God Mode con un método independiente y le pone cifras.

Nota: el Maestro ya sale de doble casi siempre (lo prefiere porque le responden menos fichas), por eso añadirle una regla de salida explícita no cambió su resultado (33,3%).

### 4.5 Leer el marcador no le sirvió a ningún bot

Probé un Maestro que (a) al cruzar 120 deja de perseguir pases y juega a ganar la mano, y (b) cuando no va último, desempata ahogando al que va último — la "alianza barata" del §3 de la estrategia.

| | Queda último |
|---|---|
| Maestro que lee el marcador | 33,6% [32,8 – 34,5] |
| El mismo, con salida de doble | 33,6% [32,7 – 34,4] |

**Empate con el Maestro.** Encaja con el patrón que el God Mode ya encontró (*nunca pagues con tu juego por un objetivo estratégico*): como desempate no cambia casi ninguna jugada, y como prioridad cuesta más de lo que da. Lo que sí lee el marcador con provecho es el Sabio, porque lo usa para **juzgar finales**, no para **elegir jugadas**.

### 4.6 Cuánto se anota por mano

`motor/perfil.py` · 20.000 rondas de tres Maestros (77.731 manos) y 18.000 de mesa mixta Novato–Jugador–Maestro, asientos rotados. Salidas completas en `analisis/datos/perfil_*.txt`.

| Tres Maestros | Por jugador y mano |
|---|---|
| **Media** | **26,3 pts** — 15,0 de pases (con capicúa) y 11,3 de cierre |
| **Mediana** | **0**: el 52% de las manos no anotas nada |
| Reparto | p75 48 · p90 79 · p99 137 |
| Toda la mano | ~79 pts entre los tres · 3,9 manos por ronda |
| Cierres | dominada 48% · tranca 52% |

> ### La mano típica no te da nada. La ronda se decide en una o dos manos grandes.
> Hay manos de 150: un jugador en 0 puede cobrar 149 de pases y dominar en la misma mano.

**Por asiento, respecto a quien sale:**

| | Media | Pases | Cierre | Gana la mano |
|---|---|---|---|---|
| **El que sale** | **30,7** | 13,7 | 17,0 | **47,4%** |
| El de su derecha (juega segundo) | 23,0 | 14,1 | 8,9 | 27,3% |
| El tercero | 25,2 | **17,1** | 8,1 | 25,3% |

> ### Salir vale unos 20 puntos de probabilidad de ganar la mano.
> Y como sale el que ganó la anterior, **el que gana una mano gana la siguiente el 49,5% de las veces**. Es la bola de nieve de la ronda. *(medido)*

El que juega justo después del que sale es el peor asiento de la mano: anota menos y cobra menos pases que el tercero, porque es el primero que tiene que responder a la salida.

**Por nivel, en la mesa mixta:** Maestro 28,9 pts por mano · Jugador 25,0 · Novato 17,0. El Novato queda último el 51,6% de las rondas; el Jugador 27,5%; el Maestro 20,9%.

**Por la mano que te reparten** (tres Maestros):

| | Media por mano | Gana la mano |
|---|---|---|
| 0 dobles | 31,3 | 44,9% |
| 2 dobles | 23,8 | 27,8% |
| 4 dobles | 13,9 | 13,6% |
| Palo largo de 3 | 22,8 | 30,7% |
| Palo largo de 5 | 50,4 | 53,5% |
| 5 caras distintas | 23,0 | 19,4% |
| 7 caras distintas | 28,1 | 39,5% |
| Mano de ≤35 puntos | 36,4 | 45,0% |
| Mano de 46–55 puntos | 23,6 | 29,7% |

Una mano ligera gana casi tanto como una con cinco de un palo, y llega igual de poco. El palo largo es lo que más pases produce (32 por mano con 5).

**En 120+** la media cae a 12,8 por mano: los pases valen 0, pero **gana la mano el 36%** — más que el segundo o el tercero. Congelado no es quieto.

### 4.7 Cuándo se pierde la ronda

Probabilidad de quedar tercero, tres Maestros (neutro 33,3%). En la mesa mixta los números son casi iguales (±3).

| Situación | Pierde la ronda |
|---|---|
| Último tras la 3ª mano, a más de 90 del segundo | **84%** |
| Último tras la 1ª mano, a 61–90 del segundo | 81% |
| Último tras la 3ª mano, a 61–90 del segundo | 79% |
| Último tras la 3ª mano, a 41–60 | 71% |
| **Último tras la 3ª mano** | **68%** |
| Último tras la 2ª mano | 65% |
| **No anota nada en las dos primeras manos** | **64%** |
| **No gana ninguna mano en toda la ronda** | **64%** |
| Otro cruza 120 y tú estás por debajo de 60 | 63% |
| Último tras la 1ª mano | 59% |
| Último tras la 3ª mano, a menos de 20 del segundo | 55% |
| Último tras la 1ª mano, a menos de 20 | 49% |
| No anota nada en la 1ª mano | 48% |
| Cede 60+ de pases en la 1ª mano | 43% |
| Pasa 3+ veces en la 1ª mano | 42% |
| 4 dobles en la 1ª mano | 41% |
| 3 dobles en la 1ª mano | 38% |
| Juega justo después del que sale en la 1ª | 35% |
| *— neutro —* | *33%* |
| Tiene el doble más alto (sale en la 1ª) | 32% |
| Otro cruza 120 y tú estás entre 60 y 119 | 30% |
| 0 dobles en la 1ª mano | 30% |
| Segundo tras la 3ª mano | 24% |
| 5 de un palo en la 1ª mano | 23% |
| Llega a 120+ pero no es quien cierra | 18% |
| **Gana la 1ª mano** | **14%** |
| Primero tras la 1ª mano | 13% |
| Llega a 120+ cuando otro ya está ahí | 10% |
| Primero tras la 3ª mano | 8% |

Lo que dice la tabla, en orden de peso:

1. **La distancia manda más que el puesto.** Ir último a menos de 20 del segundo es casi una moneda (49–55%); a más de 60 es perder cuatro de cada cinco. *Lo que hay que vigilar no es si vas último, sino por cuánto.*
2. **La primera mano vale una ronda entera.** Ganarla te deja en 14%; no anotar nada en ella, en 48%. Es la misma diferencia que hay entre el Maestro y el Novato.
3. **No ganar nunca una mano es perder** (64%), aunque cobres pases. Los pases te mantienen cerca; los cierres te sacan de abajo, y además te dan la salida.
4. **Cuando otro cruza 120, la línea está en 60.** Por debajo pierdes el 63%; entre 60 y 119, el 30%.
5. **El reparto de la 1ª mano mueve poco**: entre el mejor caso (5 de un palo, 23%) y el peor (4 dobles, 41%) hay 18 puntos, pero los casos extremos son raros. Lo común (1–2 dobles, palo de 3) queda entre 32% y 35%.

> **Cuidado al leer esta tabla.** Es **observacional**: dice qué les pasó a los jugadores que estuvieron en cada situación, no qué pasa si alguien *decide* ponerse en ella. "Ganar la 1ª mano" viene con los puntos de haberla ganado. Por eso no se puede concluir de aquí que convenga arriesgar para ganarla; el §4.5 y el God Mode (Parte 7) ya mostraron que sacrificar tu jugada por un objetivo de posición no rinde.

### 4.8 La estrategia del cómplice: ayudar al único que tiene puntos

**La idea de campo:** si solo uno tiene puntos y yo voy empatado con el otro (normalmente los dos en 0), ayudo al líder a cerrar y no dejo que el otro anote. Si la ronda cierra con los dos de abajo empatados hay muerte súbita (50%), y me evito quedar solo en el último lugar, que es donde se pierde (§4.7).

**El experimento** (`motor/complice.py`): rondas que arrancan desde un marcador fijo `[líder, 0, 0]`, con el líder saliendo. Líder en 30, 60, 90, 120 y 140; a mi derecha y a mi izquierda; 6.000 rondas por casilla. Solo cambio yo; los otros dos juegan como Maestros. Salidas en `analisis/datos/complice*.txt`.

| Líder en | Yo juego normal | Cómplice: alimento al líder | Solo veto al otro de abajo |
|---|---|---|---|
| 30 | 40–41% | 49–50% | 42–43% |
| 60 | 44% | 53–54% | 46–47% |
| 90 | 46% | 56% | 49% |
| 120 | 46–47% | 56–57% | 50% |
| 140 | 48–49% | **59%** | 51% |

> ### Ayudar al líder te hunde a ti: +8 a +10 puntos de perder, en todos los casos.
> Ni siquiera funciona si eres más flojo que el otro de abajo (Jugador contra Maestros: +7 a +9), ni si los dos de abajo se hacen cómplices a la vez (empate con jugar normal).

**¿Dura o suave al líder?** Probé las dos formas de "ayudar":

| Líder en 90, a mi derecha | Pierdo |
|---|---|
| Juego normal (Maestro) | 46,0% |
| **Suave**: le dejo puntas que puede jugar, para que siga cobrando y cierre | **59,4%** ❌ |
| **Dura**: le dejo puntas que le cuestan, para que gaste sus propios números | 46,0% |
| Suave o dura, pero solo como desempate de mi mejor jugada | 46,0% |

El patrón se repite en las 12 combinaciones de marcador, lado y nivel:

- **Darle la suave cuesta de 10 a 14 puntos.** Mientras el líder puede jugar, nunca fallan los dos, así que yo no cobro; y cuando él cobra, su siguiente ficha suele dejarle la mesa fácil al otro de abajo. La estrategia se vuelve en tu contra justo por el mecanismo que se ve en la mesa.
- **Darle la dura es exactamente jugar bien**: ahogarlo es lo mismo que ya hace el Maestro. No gana nada extra porque ya estaba incluido.
- **Como desempate, cualquiera de las dos da igual.** Ayudar "gratis" casi nunca cambia la jugada.

**Por qué no puede funcionar (razonado, y lo confirma la tabla).** La muerte súbita te deja en **50%**, y ese es su mejor caso. Jugando normal, los dos de abajo se reparten lo que no pierde el líder: con el líder en 90 él pierde ~6%, así que a cada uno le toca ~47% — **ya mejor que la muerte súbita**. Forzar el empate solo puede convenir si tu chance normal es peor que 50%, es decir, si eres claramente más flojo que el otro de abajo **y** el líder está a punto de cerrar. Y aun ahí el margen es de 1–3 puntos, que la ayuda se come con creces porque para ayudar tienes que dejar de jugar tu jugada.

> **Regla:** con un solo líder y tú empatado abajo, **no lo ayudes: ahógalo**. Tu rival real es el otro de abajo, pero la forma de ganarle es cobrar tú, no dejar que el líder cobre.

*Advertencia de método:* en una primera versión, la ayuda "barata" parecía mejorar a un jugador flojo en 2–3 puntos. El control mostró que esa mejora venía de haberle añadido "cerrar la mesa", no de ayudar. Por eso cada variante se compara contra un control con el mismo juego sin los términos de ayuda.

### 4.9 Ir abajo: ¿cambiar de estrategia? ¿cuánto se aguanta?

`motor/remontada.py` · rondas que arrancan desde marcadores fijos donde yo voy último; los rivales juegan como Maestro; quien sale, rotado; el segundo a mi derecha o izquierda, alternando. Salidas en `analisis/datos/remontada_*.txt`.

#### El reloj: cuántas manos quedan

| Situación (yo · segundo · líder) | Pierdo jugando normal | Manos que quedan | Cierra en la próxima | En ≤2 | En ≤3 |
|---|---|---|---|---|---|
| Temprano, 40 abajo (0 · 40 · 70) | 60% | 2,8 | 15% | 45% | 72% |
| Medio, 20 abajo (50 · 70 · 100) | 55% | 2,0 | 36% | 73% | 91% |
| **Medio, 40 abajo (30 · 70 · 100)** | **65%** | **2,1** | **33%** | **69%** | **89%** |
| Medio, 60 abajo (10 · 70 · 100) | 71% | 2,2 | 32% | 65% | 86% |
| Tarde, 40 abajo, líder 125 (60 · 100 · 125) | 66% | 1,75 | 49% | 82% | 95% |
| Tarde, 70 abajo, líder 125 (30 · 100 · 125) | 73% | 1,9 | 44% | 77% | 93% |

> ### El reloj lo pone el líder, no tú.
> Con el líder en 70 te quedan unas tres manos; con el líder en 100, dos; con el líder en 120+, la mitad de las veces la próxima mano es la última.

**Supervivencia** (medio, 40 abajo):

| | Pierdo |
|---|---|
| Salgo del último en la **próxima** mano | **16%** |
| Sigo último tras 1 mano y la ronda sigue | 68% |
| Sigo último tras 2 manos | 67% |
| Sigo último tras 3 manos | 64% |

Dos lecturas:

1. **Todo se juega en salir del último cuanto antes.** Salir en la próxima mano te lleva de 65% a 16%.
2. **Mientras la ronda siga, nunca estás muerto.** Seguir último no empeora tu chance mano a mano: se queda en ~65%. No hay un momento a partir del cual "ya perdí" y convenga jugar a la desesperada. Lo que se acaba no es tu chance: **se acaba el tiempo**.

#### Cambiar de plan mientras voy último

Cinco planes alternativos, activos solo mientras voy último; el resto del tiempo, Maestro.

| Plan (Δ contra jugar normal) | 20 abajo | 40 abajo | 60 abajo | 40 abajo, tarde | 70 abajo, tarde |
|---|---|---|---|---|---|
| Todo el fuego contra el segundo | +0,1 | +0,2 | 0,0 | +0,2 | +0,3 |
| Frenar al líder (alargar la ronda) | +0,1 | +0,2 | −0,1 | +0,1 | +0,2 |
| **Apostar a la tranca** (soltar peso) | **+6,4** | **+5,0** | **+4,5** | **+4,7** | **+4,4** |
| **Apostar a dominar** (guardar respuestas) | **+5,5** | **+2,2** | **+3,8** | **+3,9** | **+4,7** |
| Cercar el palo largo (cobrar grande) | +0,1 | −0,4 | −1,1 | −0,3 | −0,3 |

*(IC de cada casilla ±1,2 puntos.)*

> ### No hay plan de remontada que le gane a jugar bien.
> Los dos planes "de apuesta" (tranca, dominar) **te hunden** 2 a 6 puntos más. Atacar al segundo o frenar al líder da exactamente lo mismo que jugar normal, porque el Maestro ya ahoga a quien puede. El cerco es lo único que no empeora, y solo lejos de abajo, dentro del ruido.

**¿Y si el cerco se activa a partir de cierta distancia?** Rondas completas desde 0-0-0 contra dos Maestros, 18.000 cada una:

| Activar el cerco yendo último a… | Pierdo |
|---|---|
| cualquier distancia | 32,8% |
| 20+ | 33,1% |
| 40+ | 32,8% |
| 60+ | 33,1% |
| 90+ | 32,9% |
| nunca | 32,7% |

No hay umbral que rinda.

**La referencia del Sabio** (1.500 rondas por casilla): yendo 40 abajo pierde 59% / 62% / 62% contra 60% / 65% / 65% del Maestro (temprano / medio / tarde). Son los mismos ~3 puntos que le saca en cualquier situación (§4.2). **El que mira hacia adelante no juega distinto por ir abajo: juega mejor siempre.**

#### El plan

Lo que sale de los datos no es un cambio de estrategia: es **un cambio de atención**.

| Momento | Qué mirar | Qué hacer |
|---|---|---|
| **Mano 1** | Nada: todavía no hay marcador | Jugarla como la más importante de la ronda (§4.7: ganarla → 14%; no anotar → 48%) |
| **Tras cada mano** | Tu **distancia al segundo** | <20: estás en la pelea (~50–55%). 40: ~65%. 60+: ~71%+ |
| | **El marcador del líder** = tu reloj | <80: ~3 manos. ~100: ~2. 120+: puede ser la última |
| **Yendo último** | Nada nuevo | **El mismo juego**: cobra si puedes, cierra la mesa, suelta peso. No apuestes a la tranca ni a dominar |
| | Oportunidades gratis | Si traes palo largo, el cerco no cuesta; si no, no lo fuerces |
| **Nunca** | — | Jugar a la desesperada: tu chance no cae mano a mano, solo se acaba el tiempo |

*Razonado a partir de lo medido:* la única "reacción" que rinde es **preventiva**. Como el daño se decide en si sales del último en la mano siguiente, y ningún cambio de plan aumenta esa probabilidad, lo que queda es jugar cada mano lo mejor posible desde el principio. Llegar 40 abajo ya es la consecuencia; la reacción útil es la de la primera mano.

### 4.10 Tácticas de mesa: el farol, y "repite, mata y tranca"

`motor/tacticas.py` · 12.000 rondas por variante contra dos Maestros (neutro 33,3%). El motor ahora registra qué número deja expuesto cada jugador (`Mano.expuso`) y el historial de jugadas (`Mano.jugadas`). Salidas en `analisis/datos/tacticas_*.txt`.

#### El farol de la pinza rota

Para medir un farol hace falta alguien que lea. Construí un **Lector**: un Maestro que, cuando alguien que venía repitiendo un número juega sobre su propia punta y rompe la pinza, anota que no tiene el número de la otra punta.

| | Pierde | La lectura acierta |
|---|---|---|
| Lector contra dos Maestros | 32,9% | **85%** |
| Maestro contra dos Lectores | 33,7% | 85% |
| **Faroleador** (rompe su pinza teniendo el número) contra dos Lectores | **38,3%** | **70%** — el farol engaña |
| Faroleador, solo si no pierde un cobro | 35,7% | 77% |
| Faroleador, solo en 120+ | 34,0% | 82% |
| Faroleador contra dos Maestros (que no leen) | 38,1% | — |

- **La lectura es buena (85%) pero no da ventaja medible.** Saber que alguien no tiene un número por una pinza rota vale poco más que lo que ya dicen sus pases.
- **El farol engaña de verdad** (baja la lectura de 85% a 70%) **pero cuesta 5 puntos**, y contra rivales que leen cuesta exactamente lo mismo que contra rivales que no leen: el engaño vale cero, el costo es todo.
- **En 120+ sale gratis**, como razonaba la estrategia (§6c), pero tampoco gana nada.

> **No farolees rompiendo tu pinza.** Y si te lo hacen, no importa mucho: tu lectura tampoco valía tanto.

#### Repite, mata y tranca

| Variante | Pierde | Δ |
|---|---|---|
| Maestro (control) | 32,8% | — |
| Repite, por encima de cerrar la mesa | 35,4% | +2,6 |
| Repite, como desempate | 33,2% | +0,4 |
| Mata, por encima de cerrar la mesa | 37,8% | +5,0 |
| Mata, como desempate | 33,8% | +1,0 |
| Tranca segura si tengo menos fichas (o menos puntos) | 33,3% | +0,5 |
| Las tres, por encima de cerrar la mesa | 38,0% | +5,2 |
| Las tres, como desempate | 34,2% | +1,4 |
| **La regla tal cual** (sin "cerrar la mesa") | **42,8%** | **+10,0** |
| La regla tal cual, contra dos Jugadores | 39,5% | +13,2 vs Maestro |

- **Mata** es la peor parte: tapar la cara del rival te obliga a jugar donde él quiere que juegues.
- **Tranca** no cambia nada porque casi nunca se da: una tranca **segura** (sabida por los pases) está disponible en el **1%** de los turnos.
- **Repite** es la interesante, y se explica abajo.

#### ¿Qué pasa después de repetir la cara?

300.000 jugadas de un Maestro, observando las dos acciones siguientes. "El siguiente" es el de tu derecha; "el tercero", el de tu izquierda.

| Mi jugada | Frecuencia | Pasa el siguiente | Cobro | El siguiente pasa y el tercero me salva la mano |
|---|---|---|---|---|
| No repito | 87% | 17% | 9% | 60% |
| Repito y aún tengo esa cara | 9% | **41%** | 17% | 54% |
| **Repito y ya no tengo esa cara** | 4% | **53%** | **29%** | 44% |
| · …y el tercero guarda la última | 1,3% | 66% | **9%** | **100%** |
| · …y el tercero no la tiene | 2,9% | 47% | **38%** | 9% |

> ### Repetir funciona: el siguiente pasa 2 a 3 veces más.
> Y repetir hasta quedarte sin la cara, solo para forzarlo, es lo que más cobra (29%).
> ### Pero si el tercero guarda la última, el cobro vuelve al 9%, igual que no repetir.
> El siguiente falla, pero el tercero responde siempre, y en la mano hacen falta los dos. Es el veto (§6e de la estrategia) visto desde el otro lado.

**Entonces, ¿por qué "repite" como regla empeora?** Porque el Maestro **ya repite cuando conviene**: su "cerrar la mesa" prefiere las puntas a las que responden pocas fichas, y la cara que vienes repitiendo es justamente la que se está agotando. Cuando repetir es bueno, ya lo hace. Forzar la repetición cuando no sale natural (la política "repite") baja el cobro de esas jugadas de 29% a 22% y el pase del siguiente de 53% a 43%: son repeticiones peores.

> **Regla:** repite cuando esa cara es de las que quedan pocas; no repitas por repetir. Y antes de repetir hasta vaciarte, pregúntate si **el de tu izquierda puede tener la última**: si ya falló ese número, repite sin miedo (38% de cobro); si no ha dado señales, la última puede ser su veto.

### 4.11 La campaña: 2,5 millones de rondas buscando lo que no habíamos visto

`motor/campana.py` · cuatro enfoques con los 12 núcleos, ~2 horas de cómputo. Salidas en `analisis/datos/campana_*`.

#### a) El tribunal: 44 afirmaciones juzgadas

Cada afirmación de los documentos (y de la mesa) codificada como variante del Maestro; 18.000 rondas cada una contra dos Maestros, mismas semillas. Umbral de significancia: ±1,0 puntos.

| Veredicto | Afirmación | Δ | Fuente |
|---|---|---|---|
| ✘ **refutada** | Guardar las bajas | **+17,5** | God Mode 3.1 (ya se sabía: confirmada como el peor error) |
| ✘ refutada | Soltar peso **antes** que ahogar | +11,9 | confirma Reglamento §9.1: ahogar vale más |
| ✘ refutada | Dejar puntas en blanco o uno | +8,5 | Reglamento §9.3 |
| ✘ refutada | Soltar las altas **por encima** de cerrar la mesa | +8,5 | God Mode 3.1 (vale contra el azar, no entre buenos) |
| ✘ refutada | Mantener dos caras vivas mientras cobras | +5,4 | Reglamento §9.2 |
| ✘ refutada | Quitar "cerrar la mesa" | +4,2 | confirma que es el corazón del Maestro |
| ✘ refutada | Guardar el veto como prioridad | +3,1 | Estrategia §6e |
| ✘ refutada | Soltar dobles como prioridad (con o sin excepción del cerco) | +1,0 / +1,4 | God Mode 2.3, 4.4 |
| ✘ refutada | Mano ancha como prioridad | +1,1 | Estrategia §12 |
| ✘ refutada | Yendo último, soltar peso | +1,2 | §4.9 |
| ○ neutra | Las otras 33: alianza barata o total, derecha o izquierda, bola de nieve, romper la racha, repite, mata, tranca segura, reglas de 120+, salida con compañeras, cebo antes que cerco, cobro cierto primero… | −0,9 a +0,5 | — |

> ### Ninguna regla de una sola prioridad le gana al Maestro. Diez lo empeoran.
> La lista completa, con intervalos, está en `analisis/datos/campana_tribunal.txt`.

#### b) La búsqueda automática

Un optimizador evolutivo (entropía cruzada: 14 generaciones × 16 candidatos × 4.000 rondas) buscó **pesos** para 32 rasgos de jugada y de marcador, empezando desde el Maestro. Converge a:

| Rasgo | Peso | Lectura |
|---|---|---|
| Ahogo (puntas que los rivales ya fallaron) | +10,5 | manda |
| Fichas que no veo que responden a las puntas | −1,26 | cerrar la mesa |
| **Mis fichas que responden a las puntas** | **+1,00** | **conservar respuesta, casi igual de importante** |
| Cobro cierto | +0,69 | |
| Tranca segura | −0,50 | |
| Puntas en blanco o uno | −0,47 | evitarlas |
| Ahogo cuando voy en 120+ | −0,46 | en 120+ ahogar vale menos |
| Cebo | +0,38 | |
| Perder una cara | −0,35 | |
| Romper la racha del otro | −0,32 | **al revés** de la Estrategia §6d |
| Peso de la ficha | +0,31 | |

#### c) Lo que valora el Sabio

15.445 decisiones del Sabio (96 repartos) ajustadas con un modelo de elección (logit condicional). El modelo predice la jugada del Sabio el **58%** de las veces. En desviaciones estándar:

| Rasgo | Peso |
|---|---|
| Números distintos que me quedan en la mano | **+0,59** |
| Fichas que no veo que responden (cerrar la mesa) | −0,58 |
| **Que el de mi izquierda pueda responder** | **+0,44** |
| **Que el de mi derecha pueda responder** | **−0,40** |
| Jugar un doble | +0,39 |
| Mis fichas que responden | +0,31 |

El Sabio **cierra al de su derecha y le deja juego al de su izquierda**: quiere que el siguiente falle, pero que el tercero mueva la mesa antes de volver a él. Es la misma dirección que la mejor hipótesis del tribunal ("cierra al de tu derecha", −0,9, no significativa sola).

#### d) Validación: tres juegos de semillas, contra un control con las mismas semillas

30.000 rondas por casilla contra dos Maestros:

| | Semillas 3 | 11 | 29 | **Media** | **Δ** |
|---|---|---|---|---|---|
| Control: Maestro | 33,0% | 33,7% | 33,4% | 33,4% | — |
| **Balance de respuestas** (4 términos) | 31,3% | 31,8% | 31,7% | **31,6%** | **−1,8** |
| Optimizador (32 rasgos) | 31,2% | 31,7% | 31,3% | 31,4% | −2,0 |
| Imitador del Sabio | 31,6% | 31,5% | 31,8% | 31,6% | −1,7 |

Contra dos Jugadores también mejoran (25–26% contra 26–27% del Maestro): no es sobreajuste al rival.

**Ablación** — qué término explica la mejora (misma semilla, control 33,0%):

| Versión | Pierde |
|---|---|
| 6 términos | 31,7% |
| sin "mis fichas que responden" | **32,6%** ← la pieza clave |
| sin peso de la ficha | 32,4% |
| sin cobro cierto / sin evitar blanco-uno | 31,7% / 31,5% (no aportan) |
| **ahogo · −amenaza · +respuesta · 0,3 × peso** (balance 1:1) | **31,3%** |

> ## La estrategia descubierta: el balance de respuestas
> **Primero ahoga. Después, deja las puntas donde tú tienes más respuestas que ellos.**
>
> Cada jugada vale: *(mis fichas que sirven a las puntas) − (fichas que no veo que sirven a las puntas)*, y entre parecidas, la más pesada.
>
> El Maestro solo miraba la segunda mitad (cerrar la mesa). Cerrar la mesa **para ti también** es el error que corrige: una punta difícil para ellos y para ti es una punta que te va a hacer pasar.

Está en el motor como **nivel 5b "Balance"** (`nivel5b_balance`). Cuesta lo mismo que el Maestro y es más fuerte: el candidato natural a bot rápido del juego, con el Sabio por encima.

#### e) La liga: todas contra todas

21 estrategias en 120.000 rondas de mesas de tres al azar. Fuerza por máxima verosimilitud del modelo *P(pierde i en la mesa T) = wᵢ / Σ w*. Puntos estilo Elo: Maestro = 1000; +400 = diez veces menos probable quedar último en la misma mesa.

| # | Estrategia | Puntos | Pierde |
|---|---|---|---|
| 1 | **Imitador del Sabio** | **1022** | 26,9% |
| 2 | **Balance de respuestas** | **1017** | 27,4% |
| 3 | **Optimizador (32 rasgos)** | **1013** | 27,9% |
| 4 | Alianza total (ahoga al último) | 1006 | 28,8% |
| 5 | Cierra al de tu derecha | 1005 | 29,0% |
| 6 | Lector de pinzas | 1002 | 29,2% |
| 7–8 | Fogueado · **Maestro** | 1000 | 29,5% |
| 9 | Maestro que lee el marcador | 999 | 29,7% |
| 10 | Maestro en 3 términos | 998 | 29,8% |
| 11–12 | Mano ancha (prioridad) · Repite-mata-tranca como desempate | 994 | 30,2% |
| 13 | Guardar el veto (prioridad) | 976 | 32,6% |
| 14 | Faroleador | 963 | 34,3% |
| 15 | Jugador (nivel 3) | 957 | 35,2% |
| 16 | Dos caras vivas mientras cobras | 952 | 35,8% |
| 17 | Soltar las altas primero | 940 | 37,5% |
| 18 | Casual (nivel 2) | 933 | 38,6% |
| 19 | Repite, mata y tranca (la regla tal cual) | 928 | 39,2% |
| 20 | Guardar las bajas | 873 | 47,4% |
| 21 | Novato (azar) | 850 | 50,9% |

*(Cada estrategia jugó ~17.000 rondas; diferencias de menos de ~8 puntos de Elo entre vecinos están dentro del ruido.)*

Las tres descubiertas quedan arriba, separadas del pelotón del Maestro. Nota: en mesas mezcladas con jugadores flojos, la **alianza total** sube (4º), coherente con la Estrategia §3: la alianza destroza al descuidado; entre Maestros no rinde (§4.11a).

### 4.12 Reglamento v1.8 y v1.9: las reglas resueltas y su efecto

El 28-sep-2026 el informante resolvió dos preguntas abiertas (reglamento §12):

1. **La tranca se canta al instante: no paga pase.**
2. **Una cara cuyas fichas restantes están en la pila está muerta.**

El motor Python las adopta por defecto (`PASE_EN_TRANCA = False`, `CARA_EN_PILA_VIVA = False`). **Todo lo medido antes en este documento usa la lectura anterior** (las dos en `True`). Se reproduce con las variables de entorno `PINTINTIN_PASE_EN_TRANCA=1 PINTINTIN_CARA_EN_PILA_VIVA=1`, o poniendo las dos constantes en `True`.

**Qué cambia** (20.000 rondas de tres Maestros, `datos/perfil_maestros_v18.txt`):

| | Lectura anterior | **v1.8** |
|---|---|---|
| Puntos por jugador y mano | 26,3 | **19,6** |
| · de pases | 15,0 | **8,2** |
| · de cierre | 11,3 | 11,4 |
| No anota nada en la mano | 52% | 57% |
| Manos por ronda | 3,9 | **5,1** |
| El que sale gana la mano | 47,4% | 47,9% |
| Gana la 1ª mano → pierde la ronda | 14,1% | 14,1% |
| Último tras la 3ª mano → pierde | 68% | 68% |
| **No gana ninguna mano → pierde** | 64% | **71%** |

**La escalera de bots** (30.000 rondas contra dos Maestros, semillas 11, control en las mismas semillas; `datos/reglas_v18_escalera.txt`):

| | Lectura anterior | **v1.8** |
|---|---|---|
| Control (Maestro) | 33,7% | 33,0% |
| Jugador | 37,8% | 39,8% |
| Fogueado | 33,7% | 33,4% |
| **Balance** | 31,8% (Δ −1,9) | **30,4% (Δ −2,6)** |

> ### Con las reglas oficiales, los pases valen casi la mitad y ganar manos pesa más.
> El orden de los bots no cambia, y **Balance se separa más del Maestro**: con menos dinero en los pases, conservar respuestas (y así ganar la mano) vale todavía más.

#### v1.9: en la mano, el pase es 30 aunque haya dos caras

El informante aclaró con una partida real que **los 60 por dos caras solo existen en la salida**: durante la mano, cuando fallan los dos, se cobran 30. Motor: `PASE_MANO_POR_CARA = False` (en `True` se reproduce la lectura anterior). La partida del informante quedó como prueba (`EjemploDelInformante`).

| | v1.8 | **v1.9** |
|---|---|---|
| Pases por jugador y mano | 8,2 | **7,8** |
| Manos por ronda | 5,1 | 5,2 |
| Control (Maestro) · Balance, 30.000 rondas, semillas 11 | 33,0% · 30,4% | 33,3% · **30,8%** (Δ −2,5) |
| Jugador · Fogueado | 39,8% · 33,4% | 39,9% · 33,5% |

El efecto es pequeño porque que fallen los dos con dos caras vivas durante la mano es raro. Salidas en `datos/perfil_maestros_v19.txt` y `datos/reglas_v19_escalera.txt`.

Lo demás del documento —la estructura, las tácticas refutadas, el Sabio— **no se volvió a medir** con v1.8 ni v1.9; los órdenes de magnitud deberían mantenerse, pero cualquier cifra nueva debe medirse con las reglas oficiales. La tabla de valor del Sabio (`motor/tabla_valor.json`) ya está regenerada con v1.9, y el simulador rápido del laboratorio respeta las dos reglas (4.000/4.000 manos idénticas al motor en cada lectura).

---

## 5. Propuestas de estrategia

Marcadas como **medidas** o **razonadas**.

### Para jugadores humanos

1. **Ahoga; después, balance de respuestas.** *(medida, la mejor regla de una jugada encontrada)* Si puedes dejar las puntas donde los dos fallaron, hazlo. Si no, elige la jugada que deja más fichas **tuyas** que respondan a las puntas y menos fichas **que no ves**. Entre parecidas, la más pesada. −1,8 puntos contra el Maestro.
1b. **Cobra, cierra, suelta.** *(medida; la regla 1 la mejora)* Es todo el Maestro. Antes de cada jugada: ¿puedo dejar las puntas donde los dos fallaron? Si no, ¿qué jugada deja las puntas a las que responden menos fichas que no veo? Entre las que quedan, la más pesada.
2. **Cerrar la mesa manda sobre conservar caras.** *(medida)* Entre rivales buenos, dejar puntas "difíciles" vale más que proteger tu anchura. La anchura desempata.
3. **En la salida, cuenta las compañeras del doble.** *(medida)* Doble con 3+ del palo: casi siempre la mejor. Doble solo: da casi igual. Nunca salgas con una ficha que te deja sin un número.
4. **Piensa el principio de la mano, juega rápido el final.** *(medida)* Con 6–7 fichas la jugada "obvia" es la equivocada casi la mitad de las veces; con 1–3 casi nunca. Gasta tu tiempo de pensar en las primeras dos vueltas.
5. **Mira hacia adelante una vuelta.** *(razonada desde §4.2)* Lo que separa al Sabio del Maestro no es una regla nueva: es preguntarse *"si juego esto, ¿qué le queda al de mi derecha, y qué me devuelve el de mi izquierda?"*.
6. **Juega la primera mano como si fuera la ronda.** *(medida la correlación; la recomendación es razonada)* Ganarla te deja en 14% de perder; no anotar en ella, en 48%.
7. **Mide tu distancia al segundo, no tu puesto.** *(medida)* A menos de 20 estás vivo (≈50%); a más de 60, casi muerto (≈80%). *(razonado)* La remontada hay que buscarla antes de que el hueco pase de 40.
8. **Gana manos, no solo pases.** *(medida la correlación y la ventaja de salir)* Quien no gana ninguna mano pierde el 64% aunque cobre. Ganar la mano te da la salida, y el que sale gana la siguiente el 47%.
9. **Con un solo líder y tú empatado abajo, ahoga al líder; no lo alimentes.** *(medida)* Darle puntas fáciles para forzar la muerte súbita cuesta 10–14 puntos; la muerte súbita (50%) es peor que lo que ya tienes jugando normal (~40–49%).
10. **Yendo abajo, no cambies de plan: cambia de atención.** *(medida)* Apostar a la tranca o a dominar cuesta 2–6 puntos; atacar al segundo, frenar al líder o cercar dan lo mismo que jugar normal. Mira tu distancia al segundo y el marcador del líder (tu reloj), y sigue jugando igual de bien.
11. **No farolees rompiendo tu pinza.** *(medida)* Engaña (baja la lectura del rival de 85% a 70%) pero cuesta 5 puntos; solo en 120+ sale gratis, y aun ahí no gana nada.
12. **Repite cuando la cara se está agotando, no por regla.** *(medida)* Repetir hace pasar al siguiente 2–3 veces más, y vaciarte de la cara cobra el 29%; pero si el de tu izquierda guarda la última, cobras lo mismo que sin repetir. "Mata" y la regla completa "repite, mata y tranca" cuestan de 5 a 10 puntos.

### Para los bots y el juego

13. **Nivel 6 "Sabio" en el juego.** *(medida)* Es el único bot que supera al Maestro, y la dificultad se regula sola con el número de repartos (24 ≈ Maestro, 96, 192…). *(razonado)* En JavaScript debería correr bastante más rápido que en Python, así que 200+ repartos por jugada deberían caber en menos de un segundo en el navegador; hay que medirlo al portarlo.
14. **Benchmark contra dos Maestros, no contra dos Jugadores.** *(medida)* Contra rivales flojos todo parece funcionar; contra buenos, solo funciona lo que funciona.
15. **Cualquier bot nuevo con intervalo de confianza.** Una diferencia de 0,6 puntos con 9.000 rondas es ruido (±1).

---

## 6. Preguntas para la segunda fuente

Las preguntas 1 (¿la tranca paga pase?) y 2 (¿la pila mata la cara?) quedaron **resueltas por el informante** en el reglamento v1.8: no, y sí (§4.12). Siguen abiertas:

3. **"La ficha más alta" en la muerte súbita sin dobles:** ¿por cara (6/2 antes que 5/4) o por puntos (5/4 = 9 antes que 6/2 = 8)? El código usa la cara, como los JS.
4. **Capicúa con las dos puntas iguales:** si las puntas son 5 y 5 y cierras con `5/x`, ¿es capicúa? El código dice que no.

Y la que más valor tendría: **una segunda mesa** que confirme o discuta todo el reglamento.

---

## 7. Archivos

| Archivo | Qué es |
|---|---|
| `motor/test_motor.py` | 21 pruebas del reglamento |
| `motor/laboratorio.py` | Torneos paralelos con IC, verificación, políticas nuevas, Sabio, estudios |
| `motor/campana.py` | Tribunal de 44 afirmaciones, búsqueda evolutiva, imitación del Sabio, liga (§4.11) |
| `motor/tacticas.py` | El farol de la pinza, "repite, mata y tranca", qué pasa al repetir (§4.10) |
| `motor/remontada.py` | Ir abajo: el reloj, planes alternativos, umbrales (§4.9) |
| `motor/complice.py` | La estrategia del cómplice, dura vs suave (§4.8) |
| `motor/perfil.py` | Puntos por mano y situaciones de riesgo (§4.6–4.7) |
| `motor/tabla_valor.json` | P(quedar último) según el marcador, de 60.000 rondas de Maestros |
| `analisis/datos/` | Salidas crudas de las corridas de esta auditoría |

---

*Todas las cifras de este documento se regeneran con los comandos del §1. Las semillas son fijas.*
