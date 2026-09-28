# PINTINTÍN

**Dominó dominicano para tres jugadores · reglamento, análisis y motor**

Hasta donde se pudo verificar, **no existe ningún otro análisis de este juego**: ni artículo, ni reglas publicadas, ni estudio. La única fuente escrita conocida es *El juego de dominó* de Frank Nicolás C. (Cervecería Nacional Dominicana, Santo Domingo, ~199?), que no está digitalizado.

Este repositorio reconstruye el reglamento desde la tradición oral, lo mide con simulación y entrega herramientas para jugarlo y estudiarlo.

---

## Por dónde empezar

| Si eres… | Lee |
|---|---|
| **Alguien que quiere jugar** | `reglas/pintintin-reglas.md` |
| **Alguien que quiere ganar** | `analisis/pintintin-estrategia.md` |
| **Alguien que quiere entenderlo a fondo** | `analisis/pintintin-god-mode.md` |
| **Un agente o dev que retoma el proyecto** | `analisis/pintintin-bitacora.md` ← **empieza aquí** |

---

## Contenido

```
reglas/
  pintintin-reglas.md        Reglamento v1.7, completo y cerrado.
                             Base de todo lo demás.

analisis/
  pintintin-estrategia.md    Estrategia medida: alianzas, cerco, conteo,
                             palos frágiles, administración de la mano.
  pintintin-god-mode.md      Análisis profundo en 12 partes. Todo con
                             porcentajes medidos por simulación.
  pintintin-bitacora.md      Documento de traspaso. Qué se hizo, cómo
                             funciona el motor, y los tres objetivos.

apps/
  mesa-pintintin.html        Laboratorio: arma cualquier posición, edita
                             manos y marcador, y el motor dice qué paga.
  dojo-pintintin.html        Juega contra 2 bots (5 niveles) con revisión
                             en vivo de cada jugada y análisis de mano.

motor/
  motor_pintintin.py         Implementación de referencia. Reglas, bots,
                             inferencia y arnés de simulación.
```

Los dos `.html` son autocontenidos: se abren en cualquier navegador, sin servidor ni dependencias.

---

## El motor

```bash
python3 motor/motor_pintintin.py                 # benchmark
python3 motor/motor_pintintin.py --rondas 20000  # más preciso
```

Salida típica — **el neutro es 33,3%, menos es mejor**:

```
  1 Novato   (azar)                 47,5%
  2 Casual   (suelta alto)          36,2%
  3 Jugador  (cuenta fallos)        33,9%
  4 Fogueado (+ predice)            27,7%
  5 Maestro  (+ cerco/cebo)         26,7%
```

### La métrica

> **El % de rondas en que un jugador queda ÚLTIMO.**

En pintintín **solo pierde el tercero**: primero y segundo ganan igual. Por eso nada se optimiza por puntos — se optimiza por no quedar abajo. Es la trampa más fácil de caer al programar un bot para este juego.

---

## El reglamento en 10 líneas

- Doble-seis **sin** `0/0`, `0/1`, `1/1` → **25 fichas, 165 puntos**.
- 3 jugadores, 7 fichas cada uno, **4 en la pila que no se usan**.
- Turno **a la derecha**. Primera jugada oficial: sale el **doble más alto, automático**. Después sale el ganador anterior con lo que quiera.
- **Pase:** 30 por cada cara viva. **En la salida paga cada rival que falla; en la mano hacen falta los dos.** Tope 60 por jugada.
- **Cara muerta** (todas sus fichas en la mesa) no cuenta.
- **Dominada:** suma de las fichas de los otros dos. **Capicúa:** +30.
- **Tranca:** la mano más baja gana la suma de **las tres** manos.
- **Techo:** un bono nunca lleva a 150. Desde 120 los bonos no suman.
- **Meta 150. Solo pierde el tercero.**
- **Pasar con ficha:** el infractor pierde la ronda, marcador a 0 – 0 – 0.

---

## Diez hallazgos

| | |
|---|---|
| Contar los fallos | **−14 puntos**, y cuesta dos frases por rival |
| Techo del conteo | 13,8% (ver las manos). La habilidad manda |
| Ir último tras 3 manos | 66% de perder. La trampa se cierra temprano |
| Cruzar 120 primero | 96,5% de no perder. Es ganar |
| La alianza | Hunde al descuidado al 47,1%; contra quien cuenta, 34,0% |
| Cada doble que traes | ~5 puntos menos de ganar la mano |
| Anchura vs concentración | 7 caras gana más que 4 de un palo, y llega más seguido |
| Salir de doble | Paga 4 a 25 veces más que salir de ficha de dos palos |
| La pila al final | Con 2 fichas por cabeza, **la mitad de lo que falta está fuera** |
| Predecir | No se predicen fichas (38-53%), se predice si puede jugar (**91-99%**) |

---

## Honestidad del método

- Lo que lleva **porcentaje está medido** por simulación (7.000 a 120.000 repeticiones, asientos rotados). Lo que no, está razonado desde la estructura y va marcado como tal.
- **Este proyecto ya se equivocó cuatro veces** y las correcciones están documentadas en la bitácora: un bug de asientos que hizo concluir que la habilidad no importaba, la salida con blanco, el líder congelado, y el término anti-cebo del bot maestro. Conviene leerlas antes de añadir nada.
- **El reglamento tiene una sola fuente**: un jugador habitual. Eso es un testimonio, no un estándar. Contrastarlo con otras mesas dominicanas es la mejora más valiosa que se le puede hacer a este repositorio.

---

*Reconstruido a partir de la tradición oral dominicana. Libre para usar, corregir y ampliar.*
