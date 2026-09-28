# PINTINTÍN

**Dominó dominicano para tres jugadores · reglamento, análisis, bots y motor**

Hasta donde se pudo verificar, **no existe ningún otro análisis de este juego**: ni artículo, ni reglas publicadas, ni estudio. La única fuente escrita conocida es *El juego de dominó* de Frank Nicolás C. (Cervecería Nacional Dominicana, Santo Domingo, ~199?), que no está digitalizado.

Este repositorio reconstruye el reglamento desde la tradición oral, lo mide con simulación —**más de 3 millones de rondas simuladas**— y entrega bots de seis niveles, herramientas para jugarlo y estudiarlo, y un método reproducible para seguir investigándolo.

---

## Por dónde empezar

| Si eres… | Lee |
|---|---|
| **Alguien que quiere jugar** | [`reglas/pintintin-reglas.md`](reglas/pintintin-reglas.md) |
| **Alguien que quiere ganar** | [`analisis/pintintin-estrategia.md`](analisis/pintintin-estrategia.md) y el §5 de la [auditoría](analisis/pintintin-auditoria.md) |
| **Alguien que quiere entenderlo a fondo** | [`analisis/pintintin-god-mode.md`](analisis/pintintin-god-mode.md) → [`analisis/pintintin-auditoria.md`](analisis/pintintin-auditoria.md) |
| **Alguien que va a programar un juego** | [`analisis/pintintin-bots.md`](analisis/pintintin-bots.md) y [`motor/`](motor/) |
| **Alguien que quiere investigar** | [`analisis/pintintin-metodologia.md`](analisis/pintintin-metodologia.md) |
| **Un agente o dev que retoma el proyecto** | [`analisis/pintintin-bitacora.md`](analisis/pintintin-bitacora.md) ← **empieza aquí** |

---

## El reglamento en 10 líneas

- Doble-seis **sin** `0/0`, `0/1`, `1/1` → **25 fichas, 165 puntos**.
- 3 jugadores, 7 fichas cada uno, **4 en la pila que no se usan**.
- Turno **a la derecha**. Primera jugada oficial: sale el **doble más alto, automático**. Después sale el ganador anterior con lo que quiera.
- **Pase:** 30 por cada cara viva. **En la salida paga cada rival que falla; en la mano hacen falta los dos.** Tope 60 por jugada.
- **Cara muerta** (nadie puede jugarla: todo en la mesa o lo que falta en la pila) no cuenta.
- **Dominada:** suma de las fichas de los otros dos. **Capicúa:** +30.
- **Tranca:** se canta al instante, sin pase. La mano más baja gana la suma de **las tres** manos.
- **Techo:** un bono nunca lleva a 150. Desde 120 los bonos no suman.
- **Meta 150. Solo pierde el tercero.**
- **Pasar con ficha:** el infractor pierde la ronda, marcador a 0 – 0 – 0.

**Reglamento v1.8:** dos preguntas que el código obligó a decidir ya las resolvió el informante (tranca sin pase, la pila mata la cara); otras dos siguen abiertas. Ver reglamento §12.

---

## Los bots

| Nivel | Nombre | Idea | Pierde vs 2 Maestros | Elo |
|---|---|---|---|---|
| 1 | Novato | Azar | 53,4% | 850 |
| 2 | Casual | Suelta alto sin estrecharse | 42,1% | 933 |
| 3 | Jugador | **Cuenta los fallos** | 37,8% | 957 |
| 4 | Fogueado | + **cierra la mesa** | 33,7% | 1000 |
| 5 | Maestro | + cerco y cebo | 33,3% | 1000 |
| 5b | **Balance** | Ahoga; después, puntas donde **tú** respondes más que ellos | **31,6%** (v1.8: 30,4%) | 1017 |
| 6 | **Sabio** | Simula el resto de la mano sobre repartos posibles | **28,3–30,4%** | — |

Neutro = 33,3% (solo pierde uno de tres). Detalles, costos y recomendaciones de dificultad para un juego en [`analisis/pintintin-bots.md`](analisis/pintintin-bots.md).

---

## Los hallazgos

### Estructura del juego

| | |
|---|---|
| **Solo pierde el tercero** | Tu puntuación no importa; importa tu distancia sobre el último |
| **La mano típica no da nada** | Media 20 pts por jugador y mano, **mediana 0**: el 57% de las manos no anotas (v1.8) |
| **Salir vale 20 puntos** | El que sale gana la mano el 47%; los otros, ~26%. Y sale el que ganó la anterior |
| **La primera mano vale una ronda** | Ganarla → pierdes 14%. No anotar en ella → 48% |
| **La distancia manda más que el puesto** | Último a <20 del segundo: ~50%. A 60+: ~80% |
| **Cruzar 120 primero** | 96,8% de no perder |
| **El reloj lo pone el líder** | Con el líder en 100 quedan ~2 manos; en 120+, la próxima puede ser la última |

### Lo que funciona (medido contra rivales buenos)

| | |
|---|---|
| **Contar los fallos** | La técnica más rentable por esfuerzo: dos frases por rival |
| **Cerrar la mesa** | Dejar puntas a las que responden pocas fichas que no ves |
| **Balance de respuestas** | …pero sin cerrártela a ti: −1,8 puntos sobre el Maestro |
| **Salir de doble, con compañeras** | Doble + 3 del palo: la mejor salida el 83% de las veces. Doble solo: da igual |
| **Mirar hacia adelante** | Simular la mano (Sabio): −3 a −5 puntos |

### Lo que no funciona (refutado)

| Idea | Costo |
|---|---|
| Guardar las fichas bajas | **+17,5** puntos de perder |
| Soltar peso antes que ahogar | +11,9 |
| Hacerse cómplice del único líder para forzar muerte súbita | +8 a +10 |
| "Repite, mata y tranca" como regla fija | +5 a +10 |
| Farolear rompiendo tu pinza | +5 |
| Mantener dos caras vivas mientras cobras | +5,4 |
| Apostar a la tranca o a dominar cuando vas abajo | +2 a +6 |

Todo, con intervalos de confianza, en la [auditoría](analisis/pintintin-auditoria.md).

---

## Contenido

```
reglas/
  pintintin-reglas.md          Reglamento v1.7 + preguntas abiertas (§12).

analisis/
  pintintin-estrategia.md      Estrategia para jugadores: alianzas, conteo,
                               cerco, palos frágiles, administración.
  pintintin-god-mode.md        Análisis profundo en 12 partes.
  pintintin-auditoria.md       Revisión y extensión: pruebas, remediciones,
                               Sabio, salida, riesgo, cómplice, remontada,
                               tácticas de mesa, campaña de 2,8M rondas.
  pintintin-bots.md            Los seis niveles de bot: algoritmo, fuerza,
                               costo y dificultades para un juego.
  pintintin-metodologia.md     Cómo se mide todo, errores cometidos y cómo
                               reproducir cada cifra.
  pintintin-bitacora.md        Documento de traspaso.
  datos/                       Salidas crudas de cada experimento.

motor/                         Python 3.9+, sin dependencias.
  motor_pintintin.py           Implementación de referencia: reglas, bots
                               1–5b, inferencia, rondas.
  test_motor.py                21 pruebas contra el reglamento.
  laboratorio.py               Torneos paralelos con IC 95%, Sabio (nivel 6),
                               simulador de rollouts, tabla de valor.
  campana.py                   Tribunal de hipótesis, búsqueda evolutiva,
                               imitación del Sabio, liga con Elo.
  perfil.py                    Puntos por mano y situaciones de riesgo.
  complice.py                  ¿Ayudar al único líder? Dura vs suave.
  remontada.py                 Ir abajo: el reloj y los planes alternativos.
  tacticas.py                  Farol de la pinza; repite, mata y tranca.
  tabla_valor.json             P(quedar último) según el marcador.

apps/                          HTML autocontenido, sin servidor.
  mesa-pintintin.html          Laboratorio: arma una posición y el motor
                               dice qué paga.
  dojo-pintintin.html          Juega contra 2 bots (niveles 1–5) con
                               revisión de cada jugada.
```

---

## Uso rápido

```bash
python3 -m unittest motor/test_motor.py                                   # reglas
python3 motor/motor_pintintin.py                                          # benchmark clásico
python3 motor/laboratorio.py bench balance fogueado --rival maestro --rondas 12000
python3 motor/perfil.py --ejemplo                                         # media por mano y riesgo
```

Todo corre en paralelo con todos los núcleos disponibles. Lista completa de comandos en la [metodología](analisis/pintintin-metodologia.md#7-reproducir-cada-cifra).

### La métrica

> **El % de rondas en que un jugador queda ÚLTIMO.** Neutro 33,3%, menos es mejor.

En pintintín **solo pierde el tercero**: primero y segundo ganan igual. Por eso nada se optimiza por puntos — se optimiza por no quedar abajo. Es la trampa más fácil de caer al programar un bot para este juego.

---

## Honestidad del método

- Lo que lleva **porcentaje está medido** por simulación, con intervalo de confianza del 95%. Lo que no, está razonado desde la estructura y va marcado como tal.
- **Este proyecto se equivocó siete veces**, y todas las correcciones están documentadas en la [metodología](analisis/pintintin-metodologia.md#6-los-errores-que-ya-se-cometieron). Conviene leerlas antes de añadir nada.
- **Los bots no hablan, no leen caras ni pactan en voz alta.** El meta-juego social de una mesa real no está medido.
- **Las mediciones se hicieron con la lectura anterior de dos reglas** (tranca con pase, cara viva si lo que falta está en la pila). Con el reglamento v1.8 la escalera de bots mantiene su orden y Balance se separa más del Maestro; los pases valen casi la mitad. Detalle y cómo reproducir cada versión: [auditoría §4.12](analisis/pintintin-auditoria.md).
- **El reglamento tiene una sola fuente**: un jugador habitual. Eso es un testimonio, no un estándar. Contrastarlo con otras mesas dominicanas es la mejora más valiosa que se le puede hacer a este repositorio.

---

*Reconstruido a partir de la tradición oral dominicana. Libre para usar, corregir y ampliar.*
