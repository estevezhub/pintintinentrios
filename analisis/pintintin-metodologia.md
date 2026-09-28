# PINTINTÍN — Metodología de pruebas

**Cómo se mide todo en este proyecto, qué errores ya se cometieron, y cómo reproducir cada cifra**

28 de septiembre de 2026 · reglamento v1.7

---

## 0. Por qué hace falta esto

Este proyecto ya se equivocó **siete veces**, y en todas la causa fue de método, no de cálculo (§6). Un juego de azar con tres jugadores produce diferencias pequeñas enterradas en mucho ruido: sin un método explícito, es fácil "descubrir" cosas que no existen o no ver las que sí.

---

## 1. La métrica única

> **% de rondas en que una política queda ÚLTIMA.** Neutro = 33,3%. Menos es mejor.

- En pintintín **solo pierde el tercero**. Primero y segundo ganan igual. Por eso **nada se optimiza por puntos**: se optimiza por no quedar abajo.
- Una ronda completa (hasta que alguien llega a 150, incluida la muerte súbita si hace falta) es **una observación**. Las manos dentro de una ronda no son independientes; no se usan como muestra para la métrica principal.
- Métricas secundarias (puntos por mano, % de trancas, probabilidad de cobrar) se usan para **explicar**, nunca para **decidir** qué estrategia es mejor.

---

## 2. El diseño de un torneo

```
para k en 0 … R−1:
    asiento = k mod 3                 ← la política probada rota por los tres asientos
    mesa    = [probada si j == asiento, si no rival]
    perdedor = jugar_ronda(mesa)
    pierde += (perdedor == asiento)
```

- **Rotación de asientos**: cada política se sienta el mismo número de veces en cada asiento. Elimina el sesgo de posición (el turno corre a la derecha y el asiento sí importa).
- **Rivales idénticos**: la política probada juega contra **dos copias** de la misma política de referencia.
- **Rival de referencia: dos Maestros.** Contra rivales flojos casi todo parece funcionar (§6, error 6). La vara histórica, dos Jugadores, se reporta aparte.
- **Paralelo**: `multiprocessing.Pool` con los 12 núcleos; cada trozo tiene su propia semilla, derivada de una semilla base.

Implementado en `laboratorio.torneo`, `campana.tareas_torneo` y equivalentes.

---

## 3. Estadística

### 3.1 Intervalo de confianza

Cada porcentaje se reporta con su **intervalo de Wilson al 95%**:

| Rondas | Margen típico (±) cerca de 33% |
|---|---|
| 3.000 | 1,7 |
| 12.000 | 0,85 |
| 18.000 | 0,70 |
| 30.000 | 0,53 |
| 90.000 | 0,31 |

**Regla práctica:** una diferencia menor que el margen **no es una diferencia**.

### 3.2 Comparar contra un control con las mismas semillas

Toda variante se compara contra el **Maestro jugado con las mismas semillas**, no contra el 33,3% teórico. Con semillas fijas y políticas deterministas, los repartos coinciden hasta que las decisiones divergen. Eso reduce la varianza de la diferencia, pero también hace que **todas las variantes compartan la misma suerte**: sin el control medido en esas mismas semillas, un lote entero puede parecer mejor o peor de lo que es (§6, error 5).

Umbral de significancia de una diferencia Δ entre dos proporciones independientes p₁, p₂ con n rondas cada una:

```
|Δ| > 1,96 · √( p₁(1−p₁)/n + p₂(1−p₂)/n )
```

Con 18.000 rondas por brazo, eso son ±1,0 puntos.

### 3.3 Replicación

Un hallazgo positivo nuevo se da por bueno solo si se repite en **al menos tres juegos de semillas independientes** contra su control. Ejemplo (Balance, auditoría §4.11): −1,7, −1,9, −1,7 puntos.

### 3.4 Muchas hipótesis a la vez

El tribunal juzga 44 hipótesis. Con un umbral de 95%, se esperan ~2 falsos positivos por azar. Por eso un "MEJORA" aislado del tribunal **no se acepta sin validar** con más rondas y otras semillas. En la práctica ninguna hipótesis mejoró; las diez que empeoraron lo hicieron por márgenes de 1 a 17 puntos, lejos del umbral.

---

## 4. Tipos de experimento

| Tipo | Pregunta | Ejemplo | Cuidado |
|---|---|---|---|
| **Torneo** | ¿Esta política pierde menos? | Balance vs dos Maestros | Control con las mismas semillas |
| **Arranque desde un marcador fijo** | ¿Qué conviene en esta situación? | `[líder, 0, 0]`, yendo 40 abajo | Es causal: solo cambia la política |
| **Observacional** | ¿Qué les pasa a quienes están en X? | "gana la 1ª mano → pierde 14%" | **No es causal**: X viene con sus puntos |
| **Oráculo** | ¿Qué jugada es mejor aquí? | Estudio de la salida con el Sabio | El oráculo tiene su propio modelo de rivales |
| **Ablación** | ¿Qué término explica la mejora? | Balance sin cobertura | Una pieza a la vez, mismas semillas |
| **Control de confusión** | ¿La mejora viene de lo que creo? | Cómplice vs "control" sin términos de ayuda | Todo lo demás idéntico |

### Búsqueda y aprendizaje

- **Tribunal** (`campana.py tribunal`): cada afirmación se codifica como una variante del Maestro (orden lexicográfico o cambio condicional según el contexto) y se juzga contra el control.
- **Búsqueda evolutiva** (`campana.py cem`): método de entropía cruzada sobre pesos de 32 rasgos. 16 candidatos por generación, 4.000 rondas cada uno, **mismas semillas dentro de una generación** para que la selección compare candidatos en igualdad. La élite (25%) actualiza media y desviación con suavizado. **Todo candidato ganador se valida después** con otras semillas y muchas más rondas.
- **Imitación** (`campana.py imitar`): se graban decisiones del Sabio con los rasgos de cada alternativa y se ajusta un **logit condicional** (máxima verosimilitud, Adam, rasgos estandarizados). Sirve para **leer** qué valora el Sabio y como política barata.
- **Liga** (`campana.py liga`): mesas de tres al azar entre N estrategias. La fuerza se estima con el modelo *P(pierde i en la mesa T) = wᵢ / Σⱼ∈T wⱼ*, por máxima verosimilitud (algoritmo MM de Hunter). Puntuación = 1000 + 400·log₁₀(w_Maestro / wᵢ).

---

## 5. Verificación del motor

Antes de medir estrategias hay que confiar en las reglas.

| Prueba | Qué garantiza |
|---|---|
| `motor/test_motor.py` · 21 pruebas | Cada caso de referencia del reglamento (pase en salida y en mano, cara muerta, tope 60, techo 149/120, dominada, capicúa, 3 desempates de tranca, primera oficial, muerte súbita) |
| Invariantes sobre 400 rondas | Nadie cruza 150 con bonos; nunca dos a la vez; las 25 fichas siempre cuadran; lo anotado = lo registrado |
| Simulador rápido vs motor | Los rollouts del Sabio reproducen al motor en 6.000/6.000 manos, marcador por marcador |
| Python vs JavaScript | Revisión línea por línea de las funciones de reglas del Dojo y de la Mesa |
| Mismo bot, dos implementaciones | Balance del motor y Balance por especificación dan cifras **idénticas** con las mismas semillas |

---

## 6. Los errores que ya se cometieron

| # | Error | Qué produjo | Cómo se evita |
|---|---|---|---|
| 1 | **Mapeo de asientos invertido** al contar perdedores | "Ninguna técnica le gana al azar" (falso) | Prueba explícita: el perdedor se compara con el asiento rotado |
| 2 | **Razonar sin medir** la salida | "Sal con blanco o uno" (falso: sal de doble) | Toda afirmación con porcentaje se mide |
| 3 | **Razonar sin medir** el líder en 120 | "El líder congelado es vulnerable" (falso: 96,5% seguro) | Ídem |
| 4 | **Evaluador de un solo plan** | Marcaba como errores jugadas buenas de otro plan | Los tres planes (cobro, tranca, dominar) |
| 5 | **Validar sin control en las mismas semillas** | Un lote de variantes parecía 1,2 puntos mejor de lo que era | §3.2: control siempre medido en las mismas semillas |
| 6 | **Rival de referencia flojo** | Diferencias infladas; Fogueado ≠ Maestro contra flojos, iguales contra buenos | Vara principal: dos Maestros |
| 7 | **Confusión en el brazo experimental** | La "ayuda barata" al líder parecía mejorar a un Jugador, pero la mejora venía de haberle añadido "cerrar la mesa" | Brazo control con el mismo cambio sin el término probado |

Y dos trampas de lectura que no llegaron a publicarse:

- **Sesgo de selección** al comparar el Sabio con el Maestro solo donde difieren: el Maestro elige por "cerrar la mesa", así que cualquier desacuerdo cierra menos **por construcción**. No es una regla del Sabio.
- **Correlación no es causa** en las tablas de riesgo: "quien gana la 1ª mano pierde el 14%" incluye los puntos de haberla ganado. Para una pregunta causal, se arranca desde un marcador fijo y se cambia solo la política.

---

## 6b. Qué versión del reglamento

Las mediciones hasta la sección 4.11 de la auditoría se hicieron con la **lectura anterior** de dos reglas (tranca con pase, cara viva si lo que falta está en la pila). El reglamento **v1.8** las resolvió al revés, y el motor usa v1.8 por defecto. Para reproducir las cifras anteriores:

```bash
PINTINTIN_PASE_EN_TRANCA=1 PINTINTIN_CARA_EN_PILA_VIVA=1 python3 motor/laboratorio.py bench balance --rival maestro
```

(o poner `PASE_EN_TRANCA = True` y `CARA_EN_PILA_VIVA = True` en `motor_pintintin.py` para los scripts que no leen el entorno). **Toda medición nueva se hace con v1.8.**

---

## 7. Reproducir cada cifra

```bash
# reglas
python3 -m unittest motor/test_motor.py -v

# escalera de bots y verificación de lo publicado
python3 motor/motor_pintintin.py --rondas 20000 --semilla 1
python3 motor/laboratorio.py bench novato casual jugador fogueado balance --rival maestro --rondas 12000
python3 motor/laboratorio.py bench sabio96 sabio192 omnisciente --rival maestro --rondas 3000
python3 motor/laboratorio.py verificar --rondas 30000
python3 motor/laboratorio.py salida --manos 2400 --muestras 150
python3 motor/laboratorio.py diferencias --rondas 1500 --muestras 96

# situaciones y tácticas
python3 motor/perfil.py --rondas 20000 --ejemplo
python3 motor/perfil.py --mesa mixta --rondas 18000
python3 motor/complice.py --rondas 6000
python3 motor/complice.py --dura --rondas 6000
python3 motor/remontada.py reloj --rondas 12000
python3 motor/remontada.py planes --rondas 6000
python3 motor/tacticas.py rmt --rondas 12000
python3 motor/tacticas.py farol --rondas 12000
python3 motor/tacticas.py repetir --manos 60000

# campaña (≈2 h con 12 núcleos)
analisis/datos/correr_campana.sh
python3 motor/campana.py validar balance maestro --rondas 30000 --semilla 11
python3 motor/campana.py liga --rondas 120000

# la tabla de valor del Sabio (se regenera; ~75 s)
python3 motor/laboratorio.py tabla --rondas 60000
```

Tiempos de referencia en una Mac de 12 núcleos: un torneo de 12.000 rondas de bots heurísticos tarda ~20–40 s; el tribunal completo, 26 min; la búsqueda evolutiva, 29 min.

---

## 8. Cómo añadir algo nuevo

1. **Escribe la hipótesis** como política: en `campana.HIPOTESIS` (una línea con `P(...)`) o como función `(estado, i, jugadas) → jugada`.
2. **Mídela contra dos Maestros** con 12.000–18.000 rondas y **su control en las mismas semillas**.
3. Si mejora: **replica** en tres juegos de semillas con 30.000 rondas, y contra dos Jugadores para descartar sobreajuste.
4. Si es una idea de situación ("cuando voy abajo…"): **arranca desde el marcador fijo**, no filtres rondas completas.
5. **Escribe el resultado con su intervalo** y marca qué es medido y qué es razonado.
6. **Guarda la salida cruda** en `analisis/datos/`.
