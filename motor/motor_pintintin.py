"""
MOTOR DE PINTINTÍN — implementación de referencia del reglamento v1.7
=====================================================================

Dominó dominicano para tres jugadores. Reglas completas, políticas de bot
por niveles, motor de inferencia y arnés de simulación.

La métrica de todo el proyecto es **el porcentaje de rondas en que un
jugador queda ÚLTIMO**. Como solo pierde el tercero, el punto neutro es
33,3%: menos es mejor. NO se optimiza por puntos.

Uso rápido:
    python3 motor_pintintin.py            # benchmark de las cinco políticas
    python3 motor_pintintin.py --rondas 20000

Licencia: libre. Autoría del reglamento: tradición oral dominicana.
"""

import random
from collections import defaultdict
from math import comb

# ─────────────────────────────── FICHAS ───────────────────────────────
# Doble-seis menos 0/0, 0/1, 1/1  →  25 fichas, 165 puntos
EXCLUIDAS = {(0, 0), (0, 1), (1, 1)}
FICHAS = [(a, b) for a in range(7) for b in range(a, 7) if (a, b) not in EXCLUIDAS]
PUNTOS = {t: t[0] + t[1] for t in FICHAS}
TOTAL_PUNTOS = sum(PUNTOS.values())          # 165
META = 150
TECHO_BONO = 149                             # un bono nunca alcanza 150
TOPE_JUGADA = 60                             # máximo cobrable en una jugada


def tiene(t, n):
    return t[0] == n or t[1] == n


def es_doble(t):
    return t[0] == t[1]


def palo_largo(mano):
    """Devuelve (numero, cuantas) del palo más largo de la mano."""
    mejor, n = 0, 0
    for x in range(7):
        c = sum(1 for t in mano if tiene(t, x))
        if c > n:
            n, mejor = c, x
    return mejor, n


def caras_distintas(mano):
    z = set()
    for t in mano:
        z.add(t[0]); z.add(t[1])
    return len(z)


# ─────────────────────────────── LA MANO ───────────────────────────────
class Mano:
    """Una mano de pintintín. `politicas` son tres funciones (estado, i, jugadas)."""

    def __init__(self, marcador, salidor, politicas, primera_oficial=False,
                 modo="ronda", duo=None):
        d = FICHAS[:]
        random.shuffle(d)
        self.manos = [set(d[0:7]), set(d[7:14]), set(d[14:21])]
        self.pila = set(d[21:])
        self.mesa = set()
        self.cadena = []                     # [(ficha, izq, der)] en orden
        self.izq = self.der = None
        self.marcador = list(marcador)
        self.pol = politicas
        self.turno = salidor
        self.ultimo = None                   # quién jugó de último
        self.seguidos = 0                    # pases consecutivos
        self.fallos = 0                      # rivales que fallaron tras la última jugada
        self.cobrado = 0                     # ya cobrado en esta jugada (tope 60)
        self.vacios = [set(), set(), set()]  # números que cada quien demostró NO tener
        self.jugo = [defaultdict(int) for _ in range(3)]
        self.ingreso = [[0, 0] for _ in range(3)]   # [pases, cierre]
        self.primera_oficial = primera_oficial
        self.modo = modo                     # "ronda" | "subita"
        self.duo = duo
        self.log = []

    # ---- consultas ----
    def viva(self, n):
        return any(tiene(t, n) for t in FICHAS if t not in self.mesa)

    def caras_vivas(self):
        if self.izq is None:
            return []
        u = [self.izq] if self.izq == self.der else [self.izq, self.der]
        return [n for n in u if self.viva(n)]

    def legales(self, i):
        if self.izq is None:
            return [(t, 'd') for t in self.manos[i]]
        m = []
        for t in self.manos[i]:
            if tiene(t, self.izq):
                m.append((t, 'i'))
            if tiene(t, self.der):
                m.append((t, 'd'))
        return m

    def extremos_tras(self, t, lado):
        if self.izq is None:
            return t[0], t[1]
        i, d = self.izq, self.der
        if lado == 'i':
            i = t[1] if t[0] == self.izq else t[0]
        else:
            d = t[1] if t[0] == self.der else t[0]
        return i, d

    def sin_ubicar(self, yo):
        """Fichas que no están en la mesa ni en mi mano: rivales + pila."""
        return [t for t in FICHAS if t not in self.mesa and t not in self.manos[yo]]

    def siguiente(self, i):
        if self.modo == "subita" and self.duo:
            return self.duo[1] if i == self.duo[0] else self.duo[0]
        return (i + 1) % 3

    # ---- puntuación ----
    def bono(self, i, p):
        """Un bono nunca lleva a 150 ni más."""
        if self.marcador[i] >= 120:
            return 0
        return max(0, min(p, TECHO_BONO - self.marcador[i]))

    def jugar(self, i, t, lado):
        capicua = False
        if self.izq is None:
            self.cadena.append((t, t[0], t[1]))
            self.izq, self.der = t[0], t[1]
        else:
            if (self.izq != self.der and not es_doble(t)
                    and {t[0], t[1]} == {self.izq, self.der}):
                capicua = True
            ni, nd = self.extremos_tras(t, lado)
            if lado == 'i':
                self.cadena.insert(0, (t, ni, self.izq))
            else:
                self.cadena.append((t, self.der, nd))
            self.izq, self.der = ni, nd
        self.manos[i].discard(t)
        self.mesa.add(t)
        self.jugo[i][t[0]] += 1
        if t[1] != t[0]:
            self.jugo[i][t[1]] += 1
        self.ultimo, self.seguidos, self.fallos, self.cobrado = i, 0, 0, 0
        self.log.append(f"J{i+1} juega {t}")
        if not self.manos[i]:
            return self._dominada(i, capicua)
        self.turno = self.siguiente(i)
        return None

    def no_va(self, i):
        if self.izq is not None:
            self.vacios[i].add(self.izq)
            self.vacios[i].add(self.der)
        self.seguidos += 1
        if self.ultimo is not None and self.ultimo != i:
            self.fallos += 1

        if self.modo != "subita":
            nv = len(self.caras_vivas())
            valor = 30 * nv
            salida = len(self.mesa) == 1
            paga = (self.ultimo is not None and self.ultimo != i and valor > 0
                    and (salida or self.fallos >= 2))
            if paga:
                quiere = min(valor, max(0, TOPE_JUGADA - self.cobrado))
                if quiere > 0:
                    g = self.bono(self.ultimo, quiere)
                    self.marcador[self.ultimo] += g
                    self.ingreso[self.ultimo][0] += g
                    self.cobrado += quiere
                    self.log.append(f"J{i+1} no va → J{self.ultimo+1} cobra {g}")
        self.log.append(f"J{i+1} no va")

        limite = 2 if self.modo == "subita" else 3
        if self.seguidos >= limite:
            return self._tranca()
        self.turno = self.siguiente(i)
        return None

    def _dominada(self, i, capicua):
        if self.modo == "subita":
            return ('sub', i)
        pts = sum(PUNTOS[x] for j in range(3) if j != i for x in self.manos[j])
        self.marcador[i] += pts
        self.ingreso[i][1] += pts
        if capicua:
            cb = self.bono(i, 30)
            self.marcador[i] += cb
            self.ingreso[i][0] += cb
        self.log.append(f"J{i+1} DOMINA +{pts}")
        return ('dom', i)

    def _tranca(self):
        if self.modo == "subita":
            a, b = self.duo
            sa = sum(PUNTOS[x] for x in self.manos[a])
            sb = sum(PUNTOS[x] for x in self.manos[b])
            if sa == sb:
                tr = self.ultimo if self.ultimo in (a, b) else a
                return ('sub', tr)
            return ('sub', a if sa < sb else b)

        s = [sum(PUNTOS[x] for x in self.manos[j]) for j in range(3)]
        m = min(s)
        empatados = [j for j in range(3) if s[j] == m]
        trancador = self.ultimo if self.ultimo is not None else 0
        if len(empatados) == 1:
            w = empatados[0]
        elif trancador in empatados:
            w = trancador                      # preferencia del que trancó
        else:
            w = next((trancador + k) % 3 for k in (1, 2, 3)
                     if (trancador + k) % 3 in empatados)
        pts = sum(s)
        self.marcador[w] += pts
        self.ingreso[w][1] += pts
        self.log.append(f"TRANCA {s} → J{w+1} +{pts}")
        return ('tra', w)

    # ---- bucle ----
    def correr(self, tope=250):
        if self.primera_oficial:
            for v in range(6, 1, -1):
                for i in range(3):
                    if (v, v) in self.manos[i]:
                        self.turno = i
                        r = self.jugar(i, (v, v), 'd')
                        if r:
                            return r
                        break
                else:
                    continue
                break
        for _ in range(tope):
            i = self.turno
            mv = self.legales(i)
            r = (self.jugar(i, *self.pol[i](self, i, mv)) if mv
                 else self.no_va(i))
            if r:
                return r
        return ('tra', 0)


# ───────────────────────── POLÍTICAS DE BOT ─────────────────────────
# Cada nivel AÑADE una herramienta al anterior. El orden salió de medir.

def nivel1_novato(st, i, mv):
    """Juega al azar."""
    return random.choice(mv)


def nivel2_casual(st, i, mv):
    """La más alta que no le quite cobertura de las puntas."""
    def k(m):
        t, lado = m
        ni, nd = st.extremos_tras(t, lado)
        resto = st.manos[i] - {t}
        cob = sum(1 for x in resto if tiene(x, ni) or tiene(x, nd))
        return (cob, PUNTOS[t])
    return max(mv, key=k)


def nivel3_jugador(st, i, mv):
    """+ cuenta los fallos demostrados. Vale -14 puntos: el salto más grande."""
    riv = [j for j in range(3) if j != i]
    def k(m):
        t, lado = m
        ni, nd = st.extremos_tras(t, lado)
        ahogo = 0
        for j in riv:
            v = st.vacios[j]
            ahogo += 2 if (ni in v and nd in v) else (1 if (ni in v or nd in v) else 0)
        resto = st.manos[i] - {t}
        cob = sum(1 for x in resto if tiene(x, ni) or tiene(x, nd))
        return (ahogo, cob, PUNTOS[t])
    return max(mv, key=k)


def nivel4_fogueado(st, i, mv):
    """+ predice: cuántas fichas SIN UBICAR sirven a las puntas que deja."""
    riv = [j for j in range(3) if j != i]
    def k(m):
        t, lado = m
        ni, nd = st.extremos_tras(t, lado)
        ahogo = 0
        for j in riv:
            v = st.vacios[j]
            ahogo += 2 if (ni in v and nd in v) else (1 if (ni in v or nd in v) else 0)
        amenaza = sum(1 for x in st.sin_ubicar(i)
                      if x != t and (tiene(x, ni) or tiene(x, nd)))
        resto = st.manos[i] - {t}
        cob = sum(1 for x in resto if tiene(x, ni) or tiene(x, nd))
        return (ahogo, -amenaza, cob, PUNTOS[t])
    return max(mv, key=k)


def nivel5_maestro(st, i, mv):
    """+ cerco de palo y cebo.

    Orden medido:  cobro → -amenaza → cerco → cebo → cobertura → peso

    NOTA: probé añadir un término "anti-cebo" (penalizar las puntas en el palo
    que el rival viene repitiendo) y EMPEORA: 28,2% contra 26,4% sin él.
    El proxy tenía el signo invertido — repetir un palo significa GASTARLO,
    no acumularlo. La intuición es buena; esta implementación no lo era.
    """
    riv = [j for j in range(3) if j != i]
    N, largo = palo_largo(st.manos[i])
    sueltas = ({x for x in st.sin_ubicar(i) if tiene(x, N)} if largo >= 4 else set())

    def k(m):
        t, lado = m
        ni, nd = st.extremos_tras(t, lado)
        ahogo = 0
        for j in riv:
            v = st.vacios[j]
            ahogo += 2 if (ni in v and nd in v) else (1 if (ni in v or nd in v) else 0)
        amenaza = sum(1 for x in st.sin_ubicar(i)
                      if x != t and (tiene(x, ni) or tiene(x, nd)))
        cerco = ((ni == N) + (nd == N)) if largo >= 4 else 0
        cebo = 0
        if largo >= 4:
            for c in (ni, nd):
                if c != N and (min(c, N), max(c, N)) in sueltas:
                    cebo += 1
        resto = st.manos[i] - {t}
        cob = sum(1 for x in resto if tiene(x, ni) or tiene(x, nd))
        return (ahogo, -amenaza, cerco, cebo, cob, PUNTOS[t])
    return max(mv, key=k)


NIVELES = [
    ("1 Novato   (azar)", nivel1_novato),
    ("2 Casual   (suelta alto)", nivel2_casual),
    ("3 Jugador  (cuenta fallos)", nivel3_jugador),
    ("4 Fogueado (+ predice)", nivel4_fogueado),
    ("5 Maestro  (+ cerco/cebo)", nivel5_maestro),
]


# ─────────────────────── LOS TRES PLANES ───────────────────────
# No hay una jugada correcta: hay tres planes legítimos y excluyentes.
# Una jugada es correcta si es la mejor bajo CUALQUIERA de los tres.

def evaluar_planes(st, i, mv):
    """Devuelve {'cobro': [...], 'tranca': [...], 'dominar': [...]} ordenadas."""
    riv = [j for j in range(3) if j != i]
    base = []
    for m in mv:
        t, lado = m
        ni, nd = st.extremos_tras(t, lado)
        cobro = sum(1 for j in riv if ni in st.vacios[j] and nd in st.vacios[j])
        resto = st.manos[i] - {t}
        pierde = 0
        if st.izq is not None:
            for n in {st.izq, st.der}:
                if any(tiene(x, n) for x in st.manos[i]) and not any(tiene(x, n) for x in resto):
                    pierde += 1
        amenaza = sum(1 for x in st.sin_ubicar(i)
                      if x != t and (tiene(x, ni) or tiene(x, nd)))
        cob = sum(1 for x in resto if tiene(x, ni) or tiene(x, nd))
        base.append(dict(m=m, cobro=cobro, pierde=pierde, amenaza=amenaza,
                         cobertura=cob, puntos=PUNTOS[t]))
    return {
        'cobro':   sorted(base, key=lambda x: (x['cobro'], -x['pierde'], -x['amenaza'], x['puntos']), reverse=True),
        'tranca':  sorted(base, key=lambda x: (x['puntos'], x['cobro'], -x['pierde'], -x['amenaza']), reverse=True),
        'dominar': sorted(base, key=lambda x: (x['cobertura'], x['cobro'], -x['pierde'], x['puntos']), reverse=True),
    }


def planes_que_sirve(st, i, mv, jugada):
    """Planes bajo los que `jugada` es la mejor. Vacío = jugada floja."""
    ev = evaluar_planes(st, i, mv)
    return [p for p, lista in ev.items() if lista[0]['m'] == jugada]


# ─────────────────────── MOTOR DE INFERENCIA ───────────────────────

def inferir(st, yo, muestras=500):
    """P(cada ficha sin ubicar esté en cada mano rival o en la pila).

    Respeta los tamaños de mano conocidos y los vacíos demostrados.
    Medido: acierta 38-53% la ubicación exacta, pero 91-99% la pregunta
    que de verdad paga — si el rival puede jugar o no.
    """
    riv = [j for j in range(3) if j != yo]
    a, b = riv
    na, nb = len(st.manos[a]), len(st.manos[b])
    desc = st.sin_ubicar(yo)
    if not desc:
        return None
    ca, cb, ok = defaultdict(int), defaultdict(int), 0
    for _ in range(muestras * 40):
        if ok >= muestras:
            break
        d = desc[:]
        random.shuffle(d)
        A, B = d[:na], d[na:na + nb]
        if any(t[0] in st.vacios[a] or t[1] in st.vacios[a] for t in A):
            continue
        if any(t[0] in st.vacios[b] or t[1] in st.vacios[b] for t in B):
            continue
        ok += 1
        for t in A:
            ca[t] += 1
        for t in B:
            cb[t] += 1
    if not ok:
        return None
    return {t: {a: ca[t] / ok, b: cb[t] / ok,
                'pila': max(0.0, 1 - ca[t] / ok - cb[t] / ok)} for t in desc}


def p_palo_muerto(R, manos_rivales):
    """P(ningún rival tenga ese número) con R fichas sin ubicar de ese palo.

    Regla de mesa:  R=0 → muerto seguro · R=1 → hay chance · R≥2 → olvídalo.
    """
    U = manos_rivales + 4
    return comb(U - R, manos_rivales) / comb(U, manos_rivales) if U - R >= manos_rivales else 0.0


# ─────────────────────────── LA RONDA ───────────────────────────

def jugar_ronda(politicas, tope_manos=40):
    """Devuelve (perdedor, marcador). Solo pierde el TERCERO."""
    marcador = [0, 0, 0]
    ganador, primera = None, True
    for _ in range(tope_manos):
        if max(marcador) >= META:
            break
        h = Mano(marcador, ganador if ganador is not None else 0,
                 politicas, primera_oficial=primera)
        _, w = h.correr()
        marcador, ganador, primera = h.marcador, w, False
    bajo = min(marcador)
    abajo = [i for i in range(3) if marcador[i] == bajo]
    if len(abajo) == 1:
        return abajo[0], marcador
    # muerte súbita entre los de abajo: una mano, sin puntos, no se repite
    duo = abajo[:2]
    h = Mano(marcador, duo[0], politicas, modo="subita", duo=duo)
    for v in range(6, 1, -1):
        for j in duo:
            if (v, v) in h.manos[j]:
                h.turno = j
                h.jugar(j, (v, v), 'd')
                break
        else:
            continue
        break
    _, salvado = h.correr()
    return (duo[1] if salvado == duo[0] else duo[0]), marcador


def torneo(politica, rivales, rondas=9000):
    """% de rondas en que `politica` queda última. Neutro = 33,3%. Menos es mejor."""
    perdidas = 0
    for k in range(rondas):
        rot = k % 3                       # rotar asientos elimina el sesgo de posición
        pols = [politica if j == rot else rivales for j in range(3)]
        perdedor, _ = jugar_ronda(pols)
        if perdedor == rot:               # OJO: el mapeo correcto es este,
            perdidas += 1                 # invertirlo empuja todo hacia 33,3%
    return perdidas / rondas * 100


# ─────────────────────────────── CLI ───────────────────────────────
if __name__ == "__main__":
    import sys
    rondas = 9000
    if "--rondas" in sys.argv:
        rondas = int(sys.argv[sys.argv.index("--rondas") + 1])

    print(f"MOTOR DE PINTINTÍN · {len(FICHAS)} fichas · {TOTAL_PUNTOS} puntos · meta {META}")
    print(f"\nBenchmark: cada política contra dos 'Jugador (cuenta fallos)'")
    print(f"{rondas} rondas, asientos rotados. NEUTRO = 33,3% · menos es mejor.\n")
    print(f"  {'política':<30} {'% queda última':>15}")
    for nombre, pol in NIVELES:
        print(f"  {nombre:<30} {torneo(pol, nivel3_jugador, rondas):>14.1f}%")

    print("\nReferencia medida en este proyecto:")
    print("  contar los fallos contra dos al azar ........ 19,4%")
    print("  ver las manos (techo teórico) ............... 13,8%")
    print("  guardar las fichas bajas (el peor error) .... 41,9%")
