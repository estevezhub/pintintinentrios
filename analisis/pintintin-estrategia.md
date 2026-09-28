# PINTINTÍN — Estrategia

**Cómo se gana de verdad · análisis del modelo de juego**

28 de septiembre de 2026 · complemento del reglamento v1.6

---

## 0. El hallazgo

Simulé cientos de miles de rondas enfrentando formas de jugar. Esto es lo que mide cada una, jugando una contra dos rivales al azar:

| Cómo juegas | Pierdes | Contra el azar |
|---|---|---|
| **Cuentas los fallos** | **18,7%** | **−14,3** |
| **Mantienes la mano ancha** | **21,9%** | **−11,1** |
| **Sueltas las altas primero** | **25,9%** | **−7,1** |
| Al azar | 33,0% | — |
| Guardas las bajas | 41,6% | **+8,6** |

Y la alianza, medida aparte:

| Situación | El de abajo pierde |
|---|---|
| Nadie se alía, los tres cuentan igual | 33,3% |
| **Dos aliados contra uno que no cuenta** | **47,1%** |
| **Dos aliados contra uno que sí cuenta** | **34,0%** |

> ## Contar los fallos es lo más fuerte que puede hacer un jugador solo.
> ## Y todavía queda techo: quien deduce las manos ajenas baja hasta el 13,9%.
> ## La alianza es lo más fuerte que pueden hacer dos — pero solo contra alguien que no cuenta.

Dos aliados hunden a un tercero descuidado casi la mitad de las rondas. Contra alguien que lleva la cuenta, la alianza **se desinfla casi del todo**: el objetivo vuelve a 34,0%, prácticamente su parte justa, y los aliados no ganan nada por haberse coordinado.

Todo lo que tú describes está confirmado, y con números grandes. La única que sale al revés de lo que suena es **"guardar las bajas"**: aferrarte a las fichas chicas te hace perder el 41,6% de las rondas. Se sale de las altas pronto, no se guardan las bajas — que no es lo mismo.

## 1. La ley: tu puntuación no importa

Solo pierde el tercero. El primero y el segundo ganan igual.

> ### Los puntos que te sobran por encima del último no valen nada.

Alcanzar al líder no te da absolutamente nada. Cada jugada se evalúa con una sola pregunta:

**¿Esto agranda mi distancia sobre quien va a quedar último?**

Si la respuesta es no, la jugada da igual por muchos puntos que valga.

---

## 2. El reloj: quién quiere que la ronda termine

Se deduce solo de la estructura de pagos, y conviene tenerlo clarísimo en la mesa:

| Tu posición | Qué te conviene | Por qué |
|---|---|---|
| **Primero** | Cerrar rápido | Ya ganaste; cada mano extra es riesgo gratis |
| **Segundo** | Cerrar rápido | Cada mano extra es una oportunidad de que el tercero te pase |
| **Tercero** | Alargar todo | Es tu única vía: trancas, manos largas, caos |

**Si vas segundo, ayuda al líder a llegar a 150.** Suena raro ayudar a quien va ganando, pero no te quita nada: los dos ganan igual. Lo que sí te puede costar la ronda es que el tercero te alcance, y cada mano que pasa es otra tirada de ese dado.

Al revés: **si vas último, tu enemigo es el reloj.** Trancar, ahogar palos, alargar — todo lo que impida cerrar mientras cobras.

---

## 3. La alianza

### Es automática, no se negocia

Nadie tiene que decir nada. Los dos de arriba **ya tienen intereses idénticos**: que la ronda cierre con el tercero abajo. El juego los alía solo, y por eso funciona incluso entre desconocidos.

### Cómo se ejecuta sin verse las fichas

No puedes regalar fichas y no ves la mano de tu aliado. Lo que sí tienen los dos es **la misma información pública**: quién ha fallado qué. Con eso basta.

- **Deja caras que el objetivo ya falló.** Sus pases son certeza, no sospecha.
- **No dejes caras que tu aliado falló.** Si él puede jugar, la mano avanza hacia el cierre y nadie cobra de él.
- **Nunca abras un palo donde el objetivo se ve fuerte.** Eso es darle el cuadre.

### Barata, no total

Este es el matiz que la simulación dejó más claro, y va contra el instinto:

| Forma de aliarse | Objetivo flojo pierde | Objetivo que cuenta pierde | Los aliados pierden |
|---|---|---|---|
| **Total** — ahogar al objetivo por encima de todo | 44,9% | 30,1% | 27,5% / 34,9% |
| **Barata** — mi juego primero, ahogar cuando sale gratis | **48,0%** | **32,7%** | **26,0%** / 33,6% |

**Jugar primero para ti y ahogar al objetivo solo cuando no te cuesta es mejor en todos los escenarios**, tanto para hundirlo como para protegerte. Sacrificar tu propia posición para atacar al tercero es la trampa: gastas tus jugadas buenas y quedas sin munición.

> **La alianza se ejerce con las sobras, no con lo bueno.**

### Se voltea sin avisar

Dura mientras el orden esté claro. En cuanto el segundo y el tercero se acercan, los de abajo dejan de tener aliado y el de arriba pasa a espectador. **El momento más peligroso de la ronda es cuando dejas de ser aliado y pasas a ser objetivo**, y suele ocurrir una mano antes de que lo notes.

### El verdadero costo de quedar último

No son los puntos: es que **pierdes tu aliado y pasas a jugar uno contra dos**. Por eso quedarse atrás se retroalimenta. **Nunca te dejes quedar claramente último temprano** — vale la pena gastar una jugada buena solo en no serlo.


---

## 3b. El asiento: solo controlas al de tu derecha

El turno corre a la derecha, así que el de tu derecha **juega inmediatamente después de ti**. Tú le pones la mesa. El de tu izquierda juega antes que tú: **él te la pone a ti**. No puedes tener a los dos.

### El asiento no se elige: te lo asigna el marcador

Una vez empezada la partida te quedas donde estás. Lo que **sí** se mueve es el ranking — y con él, quién de tus dos vecinos es tu aliado y quién tu objetivo. **Las sillas no cambian; la configuración cambia sola.**

Solo hay dos, y conviene saber en cuál estás a cada momento:

| | Dónde está el último | Qué tienes |
|---|---|---|
| **Configuración buena** | **a tu derecha** | Control directo sobre el objetivo. Puedes ahogarlo cada turno, y como al pasar él la mesa le llega intacta a tu izquierda, una sola jugada tuya somete a los dos |
| **Configuración incómoda** | **a tu izquierda** | No puedes tocarlo. Tu aliado está a tu derecha: aliméntalo y deja que el cierre llegue rápido. Y cuidado — el desesperado es quien te pone la mesa a ti |

**Cada vez que cambie el orden del marcador, vuelve a mirar en cuál estás.** Es lo que más a menudo se juega en automático sin notar que el plan ya debería ser otro.

Como no puedes elegir, lo único accionable es **elegir hacia dónde empujas**: si los dos rivales van parejos, hunde al de tu derecha. No porque sea peor jugador, sino porque es el único que vas a poder seguir suprimiendo el resto de la ronda.

### Y dura toda la noche

Los asientos no se mueven entre rondas tampoco. Así que la relación con cada vecino es fija durante toda la sesión:

- **El de tu derecha es tu instrumento permanente.** Vale la pena aprender qué juega y cómo reacciona: lo vas a estar alimentando o ahogando toda la noche.
- **El de tu izquierda es tu amenaza permanente.** Él te pone la mesa en cada vuelta. Leerlo a él rinde más que leer a nadie.

### Repetir o variar la cara

| Lo que haces | Tú cobras | Tú pasas | Ellos cobran |
|---|---|---|---|
| **Repites la cara** | **15,1** | **0,78** | 13,8 · 13,5 |
| Juegas al azar | 14,2 | 0,86 | 14,1 · 14,1 |
| **Varías la cara** | 14,0 | 0,90 | **15,2 · 15,0** |

Tu regla es correcta: **variar la cara es llevarlo suave, y repetirla es apretar.** Pero el mecanismo no es el que uno supondría, y el matiz importa:

**Repetir no hace que el de tu derecha pase más.** Lo que hace es **mantenerte a ti jugando** — pasas 0,78 veces por mano en vez de 0,90 — y de paso subir tu ingreso y bajar el de ellos. Te quedas dentro de tu palo, siempre tienes con qué responder.

**Variar sí los alimenta, pero alimenta a los dos por igual** (15,2 y 15,0). No se puede llevar suave solo al aliado cambiando las caras: el que está al otro lado come lo mismo.

> ### Variar la cara es un regalo, pero no se puede dirigir.
> El único instrumento que sí distingue entre tu aliado y tu objetivo es **la cuenta de los fallos**: deja caras que el objetivo ya falló y que tu aliado no. Eso sí es selectivo.

**El umbral no existe.** Probé pagar por ahogar al último solo cuando se acerca —a menos de 20, 40, 60 u 80 puntos— y ninguna versión superó a la alianza barata: todas entre 32,4% y 34,4%, dentro del ruido. **No hay distancia a la que sacrificar tu juego empiece a rendir.**

**Regla práctica:** repite por defecto. Varía solo como concesión deliberada, sabiendo que también estás dando de comer al tercero.


### Desde 0 – 0 – 0: ¿a quién conviene trabajar?

Medido, presionando a uno u otro vecino desde el arranque:

| A quién presionas | Tú pierdes |
|---|---|
| **A tu derecha** | **20,0%** |
| A tu izquierda | 20,6% |

Es casi un empate, con una ventaja mínima para la derecha. Pero el empate en los números esconde una diferencia grande en lo que consigues, y ahí sí hay respuesta clara:

**Trabaja al de tu derecha. Quiere tenerlo abajo.**

Tres razones, en orden de peso:

1. **Es al único que puedes seguir suprimiendo toda la ronda.** Si tu objetivo termina siendo el de tu izquierda, tienes un objetivo que no puedes tocar y un aliado al que no hace falta ahogar: desperdicias tu único canal de control.

2. **Bloquear a tu derecha prueba también a tu izquierda, gratis.** Cuando el de tu derecha no va, **la mesa le llega a tu izquierda sin cambiar** — exactamente las mismas caras que tú pusiste. Una sola jugada tuya somete a los dos, y por eso el cobro completo depende de una decisión tuya y no de la suerte.

3. **Un desesperado a tu izquierda es lo peor que te puede pasar.** Él te pone la mesa a ti. Si es el último, quiere manos largas y caos, y tiene el canal directo para dártelos. Un último a tu derecha, en cambio, no tiene ninguna palanca sobre ti.

En corto: **el de tu izquierda como aliado, el de tu derecha como objetivo.** Es la única configuración donde tu control sirve para algo y nadie tiene control sobre ti.

### El filo de vuelta

Llevarlo suave tiene el riesgo que tú señalas, y es real: tu aliado puede jugar mal y desperdiciar lo que le diste, o peor, **puede dejar cómodo al que venía perdiendo**. Si ese pasa en puntos, la alianza se rearma entre ellos dos y **el objetivo pasas a ser tú**.

Por eso la ayuda se da con medida y con el marcador delante. En cuanto la distancia entre tu aliado y el tercero se acorta, **deja de alimentar y vuelve a repetir.**

---

## 4. Si tú eres el objetivo

Aquí es donde la habilidad rinde más de todo el juego:

| Tú, siendo el objetivo de dos aliados | Pierdes |
|---|---|
| Sin contar | **48,0%** |
| **Contando los fallos** | **32,7%** |

Contar te devuelve **más de quince puntos porcentuales** y te deja mejor que tu parte justa. Es la diferencia entre estar hundido y estar cómodo.

La razón es que los aliados gastan jugadas en atacarte, y eso les cuesta posición. Si tú juegas limpio y ellos se coordinan de más, **son ellos los que se desgastan**.

### La salida: ataca al segundo, no al líder

Para dejar de ser último no hace falta alcanzar al líder: hace falta **pasar al segundo**. Y en cuanto lo pasas, la alianza se deshace y se rearma alrededor del nuevo último, que ahora es él.

Perseguir al líder es gastar esfuerzo donde no hay premio. **Todo tu fuego contra el segundo.**

---

## 5. Los pases son información gratis

Cuando alguien dice "no va", acaba de demostrar con certeza que **no tiene ninguno de los dos números abiertos**. No es lectura ni intuición: es un dato duro, público y permanente.

Es la única ventaja de fichas que la simulación detectó, y su valor depende de la situación:

- Mesa pareja, nadie aliado: **vale poco** (−0,6 puntos).
- Mesa donde te tienen de objetivo: **vale quince**.

Cómo se usa: anota qué palos ha fallado cada quien, y elige la jugada que deja los dos extremos en palos que **ambos** rivales ya fallaron. Ese es el cobro.

### Y por eso conviene esconder los tuyos

El pase funciona en las dos direcciones: cada vez que **tú** pasas, les regalas un dato permanente que van a usar el resto de la mano. Y con dos o tres de esos ya te deducen media mano.

No puedes negarte a pasar —pasar con ficha te hace perder la ronda— pero sí puedes **retrasar el momento**. Y es justo lo que hace quedarte dentro de tu palo: repitiendo la cara pasas 0,78 veces por mano en vez de 0,90. Menos turnos perdidos, más ingreso y **menos información entregada**, todo por la misma jugada.

Cuando el pase sea inevitable, que sea lo más tarde posible: al final de la mano quedan pocas fichas y el dato ya casi no les sirve.




---

## 5b. La deducción: quién gana de verdad

Tienes razón en dónde está el techo. Medido:

| Cómo juegas | Pierdes |
|---|---|
| Al azar | 33,8% |
| Cuentas los fallos (solo los pases) | **19,4%** |
| **Sabes qué tiene cada quien** | **13,9%** |

> ### El techo del juego es perder solo el 14% de las rondas — menos de la mitad de tu parte justa.
> Llevar la cuenta de los pases te da 14 de esos puntos. **Deducir las manos te da 5,5 más.**

Eso contesta quién gana siempre en una mesa: no el que tiene mejores fichas ni el más agresivo, sino **el que reconstruye las manos ajenas mientras los demás solo miran las suyas**.

### La aritmética siempre cierra

Lo que hace esto posible en pintintín, más que en otros dominós, es que **el cálculo tiene solución exacta**:

- Son **25 fichas** y tú ves **7**.
- Ves la mesa entera: todo lo jugado está a la vista.
- **Sabes cuántas fichas tiene cada rival**, siempre: 7 menos las que ha jugado.
- Solo **4 fichas** están escondidas de verdad, en la pila.

Entonces: *sin ubicar = 25 − tus 7 − las de la mesa*. De esas, exactamente 4 están en la pila y el resto se reparte entre dos manos **de tamaño conocido**. No es intuición: es un reparto con las cuentas cuadradas.

### Los cuatro canales de información

| Canal | Qué te dice | Dureza |
|---|---|---|
| **Tamaño de las manos** | Cuántas fichas tiene cada quien | Certeza, siempre |
| **Un pase** | No tiene **ninguna** de las dos caras | Certeza |
| **Una jugada que se hace daño** | No tiene la cara que **no** usó | Casi certeza |
| **Las caras que repite** | Por dónde viene largo | Indicio |

El primero es gratis y casi nadie lo usa. Los dos del medio son los que valen los 5,5 puntos.

### La trampa de la pila al final

Aquí es donde se equivoca hasta el que cuenta bien. La proporción de lo "sin ubicar" que está en la pila **crece a medida que avanza la mano**:

| Cada rival tiene | Sin ubicar | De esas, en la pila |
|---|---|---|
| 7 fichas | 18 | 22% |
| 4 fichas | 12 | 33% |
| 2 fichas | 8 | **50%** |
| 1 ficha | 6 | **67%** |

> **Al principio, una ficha que falta casi seguro la tiene alguien. Al final, es más probable que esté en la pila que en una mano.**

Por eso el error clásico del final de mano es decir "él tiene que tener el cuatro". Cuando quedan dos fichas por cabeza, **la mitad de lo que falta está fuera del juego**. Descontar la pila antes de concluir es lo que separa al que cuenta del que cuenta bien.

### Por dónde empezar a contar

Nadie sostiene las 25 de memoria mientras juega. El orden de rendimiento:

1. **Blancos y unos.** Cinco fichas cada uno, sin doble. Son los únicos palos agotables y los más fáciles de seguir.
2. **Los fallos de cada quien.** Dos o tres anotaciones mentales por mano.
3. **El palo que cada uno repite.** Te dice por dónde vienen largos y qué van a cercar.

---

## 6. La mecánica del cobro

### La salida es el momento barato

Es el único donde **un solo rival fallando ya paga**. Medido:

| Ficha de salida | Caras | P(falla el siguiente) | Ingreso esperado |
|---|---|---|---|
| **Cualquier doble** | 1 | **~9%** | **~5,5 pts** |
| Ficha con blanco o uno | 2 | ~1,1% | ~1,2 pts |
| Dos palos gordos | 2 | ~0,2% | ~0,2 pts |

> **Sal siempre de doble.** Paga la mitad por fallo, pero el rival falla **nueve veces más seguido**, porque solo tiene que carecer de **un** número en vez de dos. En ingreso esperado el doble es de 4 a 25 veces mejor.

Eso convierte la salida obligatoria de la primera jugada oficial en **un regalo, no un castigo**: te fuerza a la mejor salida posible y de paso te quita tu ficha más pesada.

### Durante la mano hay que ahogar a los dos

Cobrar en la mano exige que **fallen los dos a la vez**. Solo pasa con la mesa estrecha, y de ahí sale la técnica central:

**El estrangulamiento de una cara.** Deja la mesa en un solo número vivo y los rivales ya solo necesitan carecer de **un** palo para fallar los dos.

| Mesa | Paga | Qué tan seguido |
|---|---|---|
| 2 caras vivas | 60 | rarísimo que fallen los dos |
| 1 cara viva | 30 | la vía práctica |

### El doble es el botón de repetir

Cuando lograste que los dos fallen, **el doble de ese palo te deja repetir el cobro**: lo juegas, el extremo no cambia, y vuelven a fallar. Es tu ejemplo del `2/3` → `3/3`.

> **El doble del palo que estás estrangulando es un arma. Todos los demás dobles son lastre.**


---

## 6b. El cerco de palo

Es la maniobra ofensiva del juego, y **te toca una de cada tres manos**: el 34,5% de las veces te reparten 4 o más fichas de un mismo palo.

Digamos que sales con cuatro cincos: `1/5`, `2/5`, `5/6` y `5/5`. Quedan tres cincos fuera — `0/5`, `3/5` y `4/5`. Tu objetivo es **poner las dos caras en 5**. Si lo logras, la mesa queda en 1 cara, tú tienes cuatro fichas para atenderla y los rivales casi seguro ninguna: fallan los dos y cobras.

### Las dos vías para poner una cara en 5

**Vía cara: gastar un cinco tuyo.** La punta muestra un 2, juegas tu `2/5`, la punta queda en 5. Funciona, pero te cuesta munición: te queda un cinco menos para sostener el cerco.

**Vía barata: el cebo.** Deja la punta en **3, en 4 o en 0** — justo los cincos que te faltan. El rival que tenga el `3/5` lo va a jugar ahí, y al hacerlo **te deja la punta en 5 él mismo**.

> ### El cebo te da la cara gratis y encima le quita el cinco al rival.
> Es la jugada más rentable del juego: no gastas nada, ganas posición y reduces la munición del contrario en el mismo movimiento.

Por eso las caras que te interesa abrir no son las de tu palo — **son las que te faltan de tu palo**.

### Cerrar la pinza

Cuando las dos caras estén en 5, el `5/5` es tu botón de repetir: lo juegas, las puntas siguen en 5, vuelven a fallar, vuelves a cobrar. Solo después sueltas un `5/x`, que abre una cara nueva — y si los rivales tampoco tienen esa, son dos caras y el pase paga **60**.

### Cuánto vale, medido

El cerco jugado sistemáticamente da una ventaja pequeña: **32,8%** de rondas perdidas contra 33,3% del azar. Del mismo orden que contar los fallos. No es la palanca grande —esa sigue siendo la alianza— pero es real y **se combina bien con ella**: el cerco es exactamente la forma de ahogar al objetivo que no te cuesta nada, y por eso encaja con la regla de aliarse barato.

---

## 6c. Leer las jugadas que se hacen daño

Los pases son información, pero hay una segunda fuente **más fina y menos conocida: las jugadas que perjudican a quien las hace.**

El caso de tu ejemplo, y es precioso:

> Un jugador viene dando cincos repetidamente — se le ve el cerco. En la otra cara alguien juega un 4. Y entonces él, en vez de arreglar esa punta, **juega otra vez por el 5** y rompe su propia pinza.
>
> **Ese hombre no tiene cuatros.**

El razonamiento: si tuviera el `4/5` lo habría jugado en la punta del 4 y habría cerrado el cerco. Si tuviera cualquier otro cuatro, habría jugado ahí antes que destruir su propia posición. **Jugó contra su propio interés, y eso solo se hace cuando no hay alternativa.**

### Por qué vale más que un pase

| Fuente | Qué te dice | Qué tan seguido aparece |
|---|---|---|
| Un pase | No tiene **ninguna** de las dos caras | Solo cuando falla del todo |
| **Una jugada que se hace daño** | No tiene la cara que **no** usó | En cualquier momento de la mano |

El pase es más contundente pero aparece poco. La jugada contra el propio interés aparece constantemente y casi nadie la mira.

### La regla general

> **Cuando alguien rompe un plan que se le venía viendo, es porque no pudo hacer otra cosa.**

No aplica solo al cerco. Sirve igual cuando alguien suelta un doble que estaba guardando, cuando abre una cara que llevaba rato evitando, o cuando gasta una ficha alta teniendo bajas. Cada una de esas es una restricción hablando en voz alta.

Y funciona al revés: **si tú estás cercando un palo, sabes que te están leyendo.** Se puede romper la propia pinza teniendo con qué, para que te crean sin cuatros.

**Pero es un farol caro.** Cobrar una vez multiplica por 3,8 tu chance de volver a cobrar (§6d): romper tu racha para mentir es pagar por perder una posición que se estaba pagando sola. **Solo sale gratis cuando vas de 120 para arriba**, porque ahí los bonos ya no te sirven de nada y la única moneda que te queda es la información.


---

## 6d. La bola de nieve

Tu observación de que el que cobra tiende a seguir cobrando es cierta, y es el efecto más fuerte que medí después de la alianza:

| | Probabilidad de cobrar en tu siguiente jugada |
|---|---|
| En una jugada cualquiera | **6,1%** |
| **Si cobraste en la anterior** | **23,4%** |

> ### Cobrar una vez multiplica por casi cuatro tu chance de volver a cobrar.

No es suerte ni racha imaginaria: es información hecha realidad. Si acabaste de hacerlos fallar a los dos, **acabas de demostrar que la mesa está en un palo que ellos no tienen y tú sí**. Mientras la mesa no se mueva de ahí, la situación se repite.

De ahí salen las dos caras de la misma regla:

**Si empiezas a cobrar, no muevas la mesa.** Repite la cara, juega el doble de ese palo, sostén la posición todo lo que puedas. Cada jugada que mantenga el cuadro vale cuatro veces lo normal.

**Si alguien empieza a cobrar, rómpelo de inmediato.** En cuanto tengas jugada, sácala de ese palo aunque te cueste una ficha que preferirías guardar. Esperar a que se enfríe solo no funciona: el proceso se alimenta a sí mismo, y cada vuelta que lo dejas correr le vale 30 o 60.

---

## 6e. El veto: una sola ficha mata el bono entero

Esta es la consecuencia más aprovechable de toda la regla del pase, y sale directo de que en la mano **tienen que fallar los dos**:

| Tras una jugada | Cuántas veces |
|---|---|
| No falla nadie | 84,6% |
| **Falla uno solo — no se paga nada** | **9,6%** |
| Fallan los dos — se cobra | 5,8% |

> ### Por cada cobro que se paga, 1,66 se caen porque UNO tenía con qué responder.
> **El 62% de los ahogos mueren por un solo defensor.**

Eso convierte tu jugada defensiva en algo mucho más grande de lo que parece. Cuando sospechas que el de tu izquierda viene cargado de cincos y tú tienes **uno solo**, esa ficha no es una ficha: **es un veto.**

Mientras la conserves, él no puede cobrar por más que estrangule el palo — porque necesita que fallen los dos y tú puedes responder. No hace falta que los dos resistan: **basta con que resista uno.**

### Cómo se juega el veto

Tu regla es exactamente la correcta: **si se abre el primer 5 y tú tienes solo uno, juega por otro lado.** Gastarlo ahí es quemar el salvavidas en agua tranquila. Guárdalo para el momento en que el 5 sea la única cara viva, que es cuando vale 30 o 60 en vez de nada.

Y como es un veto colectivo, vale la pena verlo así: **aguantar una ficha del palo cercado le está ahorrando el bono también al tercero.** Es la jugada defensiva más barata del juego y la única que protege a dos a la vez — cosa a tener en cuenta cuando ese tercero es tu aliado.

---

## 7. Los palos frágiles: blancos y unos

Quitar `0/0`, `0/1` y `1/1` deja blancos y unos con **5 fichas y sin doble**. Son los únicos palos realmente agotables:

| Palo | Fichas | Se puede agotar en |
|---|---|---|
| **Blancos, unos** | 5 | **38,3%** de las manos |
| Dos a seis | 7 | 24,2% de las manos |

*(No se puede agotar si alguna ficha del palo cayó en la pila.)*

Y si tú los acumulas, la probabilidad de que **ningún rival tenga ese palo**:

| Cuántas tienes | Blanco / uno | Palo gordo |
|---|---|---|
| 3 de 5 | 3,9% | — |
| **4 de 5** | **22,2%** | — |
| 6 de 7 | — | 22,2% |

**Tener 4 de los 5 blancos es tener una de cada cinco manos ganada de entrada.** Y es el conteo más fácil del juego: son solo cinco fichas.

**Filo de vuelta:** matar un palo también **abarata tus propios pases a la mitad**. Mátalo para ahogar; no lo mates si estás cobrando bien con dos caras.

---

## 8. El peso de la mano

La tranca cierra el **39,5%** de las manos — casi dos de cada cinco. Y el ganador se lleva **la suma de las tres manos, incluida la suya**, así que el premio es mayor que el de una dominada equivalente.

Tu regla de no cargar fichas altas al final está confirmada, y sirve dos veces: **ganas la tranca** con la mano más baja, y **no engordas el premio** que se lleva otro.

Pero la medición es honesta: **soltar alto como política general no da ventaja** (±0). Es un seguro contra accidentes, no una ventaja.

---

## 9. Las tres fases del marcador

| Fase | Qué puedes hacer |
|---|---|
| **0 – 119** | Cobrar pases. Son el **63%** de todos los puntos del juego. |
| **120 – 149** | **Tus bonos están muertos.** Solo subes dominando o trancando. |
| **Alguien en 120+** | Ese jugador está congelado. Los otros siguen cobrando. |

> ### Los últimos 30 puntos son los más caros del juego.

**Si vas subiendo: planea tu mano ganadora ANTES de cruzar 120.** Llegar a 149 sin una mano en camino es quedarte atascado mientras los otros cobran.

**Si vas atrás: el momento en que el líder cruza 120 es tu ventana.** Deja de producir y no puede volver a producir hasta ganar una mano entera. Ahí se recupera el terreno.

---

## 10. Lo que sí y lo que no

**Sí importa, y mucho** (medido, una política contra dos al azar):

| | Efecto |
|---|---|
| Contar los fallos | −14,3 puntos |
| Mano ancha: cubrir muchos números distintos | −11,1 |
| Soltar las altas primero | −7,1 |
| Aliarse contra el más flojo | −7 aprox. para cada aliado |
| **Guardar las bajas** | **+8,6 — es un error caro** |

**No importa tanto:** elegir la ficha de salida más allá de "que sea doble", y el cerco de palo como plan único (vale, pero como técnica dentro de la alianza, no como estrategia completa).

### Qué no mide esta simulación

Los bots no hablan, no leen caras, no faroleaban ni pactan en voz alta. La alianza que simulé es la mínima: dos jugadores que comparten información pública y un objetivo. En una mesa real puede ser más fuerte — o romperse por orgullo.

### Una corrección de método

La primera versión de este análisis concluía que **ninguna estrategia de fichas le ganaba al azar**. Era falso: yo rotaba los asientos para quitar el sesgo de posición pero **mapeaba mal qué política se sentaba dónde al contar los perdedores**, y eso empujaba artificialmente todos los resultados hacia 33,3%. Corregido el mapeo, las diferencias son enormes. Las tablas de arriba son las buenas.

---

## 11. Las quince reglas

1. **No juegues para ganar. Juega para no quedar tercero.** Los puntos sobre el último no valen nada.
2. **Tu aliado es quien no está en riesgo contigo.** Es automático y es lo más fuerte del juego.
3. **Aliate barato.** Tu juego primero; ahoga al tercero solo cuando te sale gratis. Sacrificarte por la alianza te hunde a ti.
4. **Cuenta los fallos.** Es el antídoto de la alianza: te lleva del 48% al 32,7% cuando te tienen de objetivo.
5. **Si eres el objetivo, ataca al segundo, no al líder.** Solo necesitas pasar a uno para que la alianza se voltee.
6. **Planea tu mano ganadora antes de cruzar 120.** Después, tus bonos no existen.
7. **Para cercar un palo, abre las caras que te faltan de ese palo.** El rival te pone la punta gratis y se queda sin munición.
8. **Mira las jugadas que se hacen daño.** Quien rompe su propio plan es porque no pudo hacer otra cosa.
9. **Repite la cara por defecto.** Te mantiene jugando, sube tu ingreso y esconde tus vacíos. Variar es un regalo que no se puede dirigir.
10. **Mira quién te tocó a la derecha.** Es el único al que puedes alimentar o ahogar directamente.
11. **Cobrar llama a cobrar.** Sostén tu racha; rompe la del otro en cuanto puedas, aunque te duela la ficha.
12. **Tu última ficha de un palo cercado es un veto, no una ficha.** Mientras la tengas, él no cobra. No la gastes en agua tranquila.
13. **Cuenta lo que falta, no lo que ves.** El techo del juego es perder solo el 14% — y se llega deduciendo manos, no jugando mejor las tuyas.
14. **Al final descuenta la pila.** Cuando quedan dos fichas por cabeza, la mitad de lo que falta está fuera del juego.
15. **No eliges asiento, pero eliges a quién hundes.** Trabaja al de tu derecha: es el único que podrás seguir suprimiendo toda la ronda. Quieres a tu aliado a la izquierda y a tu objetivo a la derecha: es la única configuración donde tú controlas y nadie te controla.


---

## 12. Administrar la mano: lo que sirve todas las noches

El cerco depende del reparto y el reparto no se controla: 4 o más fichas de un palo llegan el **34,5%** de las veces, y 5 o más solo el **3,5%**. No se puede construir un juego sobre eso.

Pero hay un recurso que llega **casi siempre**:

| Caras distintas en una mano de 7 | Frecuencia |
|---|---|
| 7 caras | 44,4% |
| 6 caras | 46,0% |
| 5 caras | 9,3% |
| 4 caras | 0,3% |

> ### El 90% de las manos ya nacen anchas.
> No hay que conseguir la mano ancha. Hay que **no destruirla**.

Ese es el giro: la mano concentrada es un regalo ocasional, la mano ancha es el estado normal. Casi todo el daño que se hace un jugador a sí mismo es **estrechar su propia mano sin darse cuenta**, gastando su última ficha de un número porque en ese momento le convenía.

### Por qué la anchura vale tanto

Porque en la mano **tienen que fallar los dos** para que se pague. Mientras tú puedas responder, nadie cobra — da igual lo bien que esté jugando el otro. Medimos que **el 62% de los ahogos mueren por un solo defensor** (§6e).

Una mano ancha no cobra mucho. **Veta**. Y vetar es una renta que se cobra todas las manos, tengas lo que tengas.

### La regla de administración

> ## Juega la ficha más alta que no te quite una cara.

Combina las dos cosas que hay que hacer con la mano: aligerarla para la tranca y no perder cobertura. Medido:

| | Pierde |
|---|---|
| Al azar | 33,2% |
| Soltar la más alta, sin más | 25,0% |
| Mano ancha | 21,8% |
| **La más alta que no cueste cara** | **21,5%** |
| Contar los fallos | **19,4%** |

Y algo que conviene saber: **contar manda sobre administrar.** Cuando forcé que la anchura decidiera primero y el ahogo después, el resultado empeoró (20,5%). La cuenta va al frente; la administración es el desempate.

---

## 13. Una forma de contar que no confunde

Nadie sostiene 25 fichas de memoria mientras conversa y juega. No hace falta. Esto es lo mínimo que produce casi toda la ventaja, en orden de rendimiento por esfuerzo:

### Nivel 1 · El tamaño de las manos — gratis

Está a la vista. **Siempre sabes cuántas fichas tiene cada quien**: 7 menos las que ha jugado. No cuesta memoria y es la base de cualquier deducción posterior.

### Nivel 2 · La lista de los dos — dos datos por rival

Es el nivel que vale los **14 puntos**, y es más barato de lo que parece.

Cada jugador pasa unas **0,85 veces por mano**, y cada pase te revela como mucho dos números. Eso son **unos dos datos por rival en toda la mano**. No es un conteo: son dos frases.

> *"El de la derecha no tiene treses ni seises. El de la izquierda no tiene blancos."*

Y de ahí sale lo único que necesitas mirar:

> ## Los números que fallaron **los dos**.
> Esa es tu lista de cobro. Cuando puedas dejar las dos puntas ahí, cobras.

Si la lista está vacía, no hay dinero en la mesa y juegas a administrar. Si tiene un número, llevas la mesa hacia él. Es una sola cosa que recordar.

### Nivel 3 · Blancos y unos — dos contadores

Solo si te sobra cabeza. Son **cinco fichas cada uno y sin doble**: los únicos palos que pueden morir. Dos contadores de 0 a 5. Cuando uno llega a 5, ese extremo queda muerto para siempre y la mesa pasa a valer 30 en vez de 60.

### Nivel 4 · Lo que falta — solo al final

Cuando queden pocas fichas, *sin ubicar = 25 − tus 7 − la mesa*. Y **descuenta siempre la pila**: con dos fichas por cabeza, la mitad de lo que falta está fuera del juego (§5b).

### El resumen del método

| Nivel | Qué recuerdas | Cuesta |
|---|---|---|
| 1 | Cuántas fichas tiene cada uno | Nada, está a la vista |
| **2** | **Quién falló qué** | **~2 frases por rival** |
| 3 | Cuántos blancos y unos han salido | 2 contadores |
| 4 | Qué fichas faltan, menos la pila | Solo al final |

**Con el nivel 2 solo ya pasas de perder el 33% a perder el 19%.** Todo lo demás son mejoras sobre eso.

---

## Nota sobre el método

Los porcentajes salen de simular el reglamento v1.6 completo: 20.000 manos para el reparto de los puntos y 15.000 a 25.000 rondas por cada enfrentamiento, con los asientos rotados para eliminar el sesgo de posición. Margen de error típico ±0,4 puntos porcentuales.

Las afirmaciones **medidas** son las de las tablas. Las **razonadas** —el reloj, atacar al segundo, cuándo se voltea la alianza— se deducen de la estructura de pagos y no están simuladas. Son justo las que más conviene contrastar en la mesa.
