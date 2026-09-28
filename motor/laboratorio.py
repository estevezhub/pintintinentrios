"""
LABORATORIO DE PINTINTÍN — arnés paralelo, estrategias nuevas y verificación
=============================================================================

Extiende `motor_pintintin.py` sin tocar sus reglas:

  · torneos en paralelo, con semilla y con intervalo de confianza del 95%
  · verificación de los hallazgos publicados en el God Mode
  · políticas nuevas (salida, marcador, alianza) y el bot de nivel 6
    ("Sabio"), que muestrea las manos ocultas y simula el resto de la mano

Uso:
    python3 motor/laboratorio.py tabla              # construye la tabla de valor
    python3 motor/laboratorio.py bench  --rondas 6000
    python3 motor/laboratorio.py verificar
    python3 motor/laboratorio.py duelo  sabio maestro --rondas 3000

La métrica sigue siendo la del proyecto: % de rondas en que la política
queda ÚLTIMA. Neutro 33,3%. Menos es mejor.
"""

import json
import math
import os
import random
import sys
import time
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motor_pintintin as M  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RUTA_TABLA = os.path.join(AQUI, "tabla_valor.json")


# ═══════════════════════════ ESTADÍSTICA ═══════════════════════════

def wilson(k, n, z=1.96):
    """Intervalo de Wilson al 95% para una proporción, en %."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * (c - h), 100 * (c + h))


def fmt(k, n):
    lo, hi = wilson(k, n)
    return f"{100 * k / n:5.1f}%  [{lo:4.1f} – {hi:4.1f}]"


# ═══════════════════════ UTILIDADES DE POLÍTICA ═══════════════════════

def rivales(i):
    return [j for j in range(3) if j != i]


def ultimo_en_marcador(st, i):
    """Índice del rival que va último (o None si el último soy yo o hay empate)."""
    s = st.marcador
    bajo = min(s)
    abajo = [j for j in range(3) if s[j] == bajo]
    if len(abajo) != 1 or abajo[0] == i:
        return None
    return abajo[0]


def salida_con_doble(base):
    """Envuelve una política: en una salida libre, sale del doble con más
    acompañantes. Si no tiene doble, decide la política base."""
    def pol(st, i, mv):
        if st.izq is None:
            mano = st.manos[i]
            dobles = [t for t in mano if M.es_doble(t)]
            if dobles:
                def acomp(d):
                    return (sum(1 for x in mano if x != d and M.tiene(x, d[0])), d[0])
                d = max(dobles, key=acomp)
                return (d, 'd')
        return base(st, i, mv)
    pol.__name__ = base.__name__ + "+salida"
    return pol


def maestro_marcador(st, i, mv):
    """Maestro que lee el marcador.

    · Si YO estoy en 120+, mis bonos no suman: dejo de perseguir el cobro y
      juego a ganar la mano (no perder cara → cobertura → peso).
    · Si NO voy último, desempato ahogando al que va último (alianza barata:
      solo entre jugadas que ya son las mejores para mí).
    """
    riv = rivales(i)
    congelado = st.marcador[i] >= 120
    objetivo = ultimo_en_marcador(st, i)
    N, largo = M.palo_largo(st.manos[i])
    sueltas = ({x for x in st.sin_ubicar(i) if M.tiene(x, N)} if largo >= 4 else set())
    sin_ubicar = st.sin_ubicar(i)

    def k(m):
        t, lado = m
        ni, nd = st.extremos_tras(t, lado)
        ahogo = 0
        for j in riv:
            v = st.vacios[j]
            ahogo += 2 if (ni in v and nd in v) else (1 if (ni in v or nd in v) else 0)
        amenaza = sum(1 for x in sin_ubicar if M.tiene(x, ni) or M.tiene(x, nd))
        resto = st.manos[i] - {t}
        cob = sum(1 for x in resto if M.tiene(x, ni) or M.tiene(x, nd))
        aliado = 0
        if objetivo is not None:
            v = st.vacios[objetivo]
            aliado = (ni in v) + (nd in v)
        if congelado:
            return (cob, ahogo, aliado, M.PUNTOS[t])
        cerco = ((ni == N) + (nd == N)) if largo >= 4 else 0
        cebo = 0
        if largo >= 4:
            for c in (ni, nd):
                if c != N and (min(c, N), max(c, N)) in sueltas:
                    cebo += 1
        return (ahogo, -amenaza, aliado, cerco, cebo, cob, M.PUNTOS[t])
    return max(mv, key=k)


# ═══════════════════ SIMULADOR RÁPIDO PARA ROLLOUTS ═══════════════════
# Representación compacta: fichas como índices 0..24, vacíos como bitmask.

IDX = {t: n for n, t in enumerate(M.FICHAS)}
FA = [t[0] for t in M.FICHAS]
FB = [t[1] for t in M.FICHAS]
PTS = [t[0] + t[1] for t in M.FICHAS]
TOT = [sum(1 for t in M.FICHAS if M.tiene(t, n)) for n in range(7)]
DE = [[n for n, t in enumerate(M.FICHAS) if M.tiene(t, x)] for x in range(7)]


def _toca(t, a, b):
    return FA[t] == a or FB[t] == a or FA[t] == b or FB[t] == b


def _tras(t, lado, izq, der):
    if izq is None:
        return FA[t], FB[t]
    if lado == 0:
        return (FB[t] if FA[t] == izq else FA[t]), der
    return izq, (FB[t] if FA[t] == der else FA[t])


def _legales(mano, izq, der):
    if izq is None:
        return [(t, 1) for t in mano]
    out = []
    for t in mano:
        if FA[t] == izq or FB[t] == izq:
            out.append((t, 0))
        if izq != der and (FA[t] == der or FB[t] == der):
            out.append((t, 1))
    return out


def _pol_rollout(mano, izq, der, vac, i):
    """Política de los rollouts: la de nivel 3 (ahogo → cobertura → peso)."""
    mv = _legales(mano, izq, der)
    if not mv:
        return None
    if len(mv) == 1:
        return mv[0]
    va, vb = vac[(i + 1) % 3], vac[(i + 2) % 3]
    best, bk = None, -1
    for t, lado in mv:
        ni, nd = _tras(t, lado, izq, der)
        mi, md = 1 << ni, 1 << nd
        ah = 0
        for v in (va, vb):
            a, b = bool(v & mi), bool(v & md)
            ah += 2 if (a and b) else (1 if (a or b) else 0)
        cob = 0
        for x in mano:
            if x != t and (FA[x] == ni or FB[x] == ni or FA[x] == nd or FB[x] == nd):
                cob += 1
        k = ah * 10000 + cob * 100 + PTS[t]
        if k > bk:
            bk, best = k, (t, lado)
    return best


def rollout(manos, enmesa, izq, der, marcador, turno, ultimo, fallos,
            cobrado, seguidos, nmesa, vac, primera=None):
    """Juega el resto de la mano. Devuelve (marcador, ganador).
    `primera` = (i, t, lado): una jugada forzada antes de seguir con la política."""
    manos = [list(m) for m in manos]
    marcador = list(marcador)
    enmesa = list(enmesa)            # cuántas fichas de cada número hay en la mesa
    vac = list(vac)

    def bono(j, p):
        if marcador[j] >= 120:
            return 0
        return max(0, min(p, 149 - marcador[j]))

    forz = primera
    for _ in range(80):
        i = turno
        if forz is not None:
            _, t, lado = forz
            forz = None
            mv = (t, lado)
        else:
            mv = _pol_rollout(manos[i], izq, der, vac, i)
        if mv is not None:
            t, lado = mv
            capicua = (izq is not None and izq != der and FA[t] != FB[t]
                       and {FA[t], FB[t]} == {izq, der})
            izq, der = _tras(t, lado, izq, der)
            manos[i].remove(t)
            enmesa[FA[t]] += 1
            if FB[t] != FA[t]:
                enmesa[FB[t]] += 1
            nmesa += 1
            ultimo, seguidos, fallos, cobrado = i, 0, 0, 0
            if not manos[i]:
                pts = sum(PTS[x] for j in range(3) if j != i for x in manos[j])
                marcador[i] += pts
                if capicua:
                    marcador[i] += bono(i, 30)
                return marcador, i
            turno = (i + 1) % 3
            continue
        # no va
        if izq is not None:
            vac[i] |= (1 << izq) | (1 << der)
        seguidos += 1
        if ultimo is not None and ultimo != i:
            fallos += 1
            vivas = [izq] if izq == der else [izq, der]
            nv = sum(1 for n in vivas if enmesa[n] < TOT[n])
            if nv and (nmesa == 1 or fallos >= 2):
                quiere = min(30 * nv, max(0, 60 - cobrado))
                if quiere > 0:
                    marcador[ultimo] += bono(ultimo, quiere)
                    cobrado += quiere
        if seguidos >= 3:
            s = [sum(PTS[x] for x in manos[j]) for j in range(3)]
            m = min(s)
            emp = [j for j in range(3) if s[j] == m]
            tr = ultimo if ultimo is not None else 0
            if len(emp) == 1:
                w = emp[0]
            elif tr in emp:
                w = tr
            else:
                w = next((tr + k) % 3 for k in (1, 2, 3) if (tr + k) % 3 in emp)
            marcador[w] += sum(s)
            return marcador, w
        turno = (i + 1) % 3
    return marcador, 0


# ═══════════════════════ TABLA DE VALOR DEL MARCADOR ═══════════════════════
# P(quedar último | mi marcador, los otros dos, si salgo yo en la próxima mano)
# medida en auto-juego del Maestro. Convierte "puntos" en lo único que importa.

def _cubo(s):
    return min(14, max(0, s // 10))


def _clave(me, a, b, salgo):
    lo, hi = sorted((a, b))
    return f"{_cubo(me)},{_cubo(lo)},{_cubo(hi)},{int(salgo)}"


def _trabajo_tabla(args):
    n, semilla = args
    random.seed(semilla)
    cuenta = {}
    pols = [M.nivel5_maestro] * 3
    for _ in range(n):
        marcador, ganador, primera = [0, 0, 0], None, True
        registros = []
        for _m in range(40):
            if max(marcador) >= M.META:
                break
            sal = ganador if ganador is not None else -1
            for j in range(3):
                o = rivales(j)
                registros.append((j, _clave(marcador[j], marcador[o[0]], marcador[o[1]], sal == j)))
            h = M.Mano(marcador, ganador if ganador is not None else 0, pols, primera_oficial=primera)
            _, w = h.correr()
            marcador, ganador, primera = h.marcador, w, False
        bajo = min(marcador)
        abajo = [j for j in range(3) if marcador[j] == bajo]
        for j, c in registros:
            perd = 1.0 if (len(abajo) == 1 and abajo[0] == j) else (0.5 if j in abajo else 0.0)
            tot = cuenta.setdefault(c, [0.0, 0])
            tot[0] += perd
            tot[1] += 1
    return cuenta


def construir_tabla(rondas=60000, procesos=None):
    procesos = procesos or os.cpu_count()
    trozos = [(rondas // procesos, 1000 + k) for k in range(procesos)]
    total = {}
    with Pool(procesos) as p:
        for parcial in p.map(_trabajo_tabla, trozos):
            for c, (s, n) in parcial.items():
                t = total.setdefault(c, [0.0, 0])
                t[0] += s
                t[1] += n
    with open(RUTA_TABLA, "w") as f:
        json.dump({"rondas": rondas, "celdas": total}, f)
    return total


_TABLA = None


def tabla():
    global _TABLA
    if _TABLA is None:
        with open(RUTA_TABLA) as f:
            _TABLA = json.load(f)["celdas"]
    return _TABLA


def valor(marcador, i, salgo):
    """Utilidad de un marcador para i: P(NO quedar último). Terminal si hay 150."""
    if max(marcador) >= M.META:
        bajo = min(marcador)
        abajo = [j for j in range(3) if marcador[j] == bajo]
        if i not in abajo:
            return 1.0
        return 0.5 if len(abajo) > 1 else 0.0
    o = rivales(i)
    c = tabla().get(_clave(marcador[i], marcador[o[0]], marcador[o[1]], salgo))
    # prior débil: la posición en el orden del marcador
    rango = sum(1 for j in o if marcador[j] > marcador[i])
    prior = (0.72, 0.62, 0.35)[rango]
    k = 20.0
    if c is None:
        return prior
    return 1.0 - (c[0] + k * (1 - prior)) / (c[1] + k)


# ═══════════════════════ NIVEL 6 · SABIO (PIMC) ═══════════════════════

def _muestrear(ocultas, nA, nB, vA, vB, intentos=60):
    """Reparte las ocultas entre A (nA), B (nB) y la pila, respetando vacíos."""
    okA = [t for t in ocultas if not (vA >> FA[t] & 1 or vA >> FB[t] & 1)]
    okB = set(t for t in ocultas if not (vB >> FA[t] & 1 or vB >> FB[t] & 1))
    okAs = set(okA)
    for _ in range(intentos):
        d = ocultas[:]
        random.shuffle(d)
        A, B = d[:nA], d[nA:nA + nB]
        if all(t in okAs for t in A) and all(t in okB for t in B):
            return A, B
    # respaldo: asignación restringida, las más restringidas primero
    for _ in range(intentos):
        d = ocultas[:]
        random.shuffle(d)
        d.sort(key=lambda t: (t in okAs) + (t in okB))
        A, B, P = [], [], []
        falla = False
        for t in d:
            op = []
            if t in okAs and len(A) < nA:
                op += [A] * (nA - len(A))
            if t in okB and len(B) < nB:
                op += [B] * (nB - len(B))
            if len(P) < len(ocultas) - nA - nB:
                op += [P] * (len(ocultas) - nA - nB - len(P))
            if not op:
                falla = True
                break
            random.choice(op).append(t)
        if not falla:
            return A, B
    d = ocultas[:]
    random.shuffle(d)
    return d[:nA], d[nA:nA + nB]


def hacer_sabio(muestras=24, marcador_aware=True, trampa=False):
    def sabio(st, i, mv):
        if len(mv) == 1:
            return mv[0]
        # jugadas distintas (misma ficha, mismas puntas resultantes = misma jugada)
        vistas, cand = set(), []
        for t, lado in mv:
            e = st.extremos_tras(t, lado)
            clave = (t, tuple(sorted(e)))
            if clave not in vistas:
                vistas.add(clave)
                cand.append((t, lado))
        if len(cand) == 1:
            return cand[0]
        a, b = (i + 1) % 3, (i + 2) % 3
        mia = [IDX[t] for t in st.manos[i]]
        ocultas = [IDX[t] for t in M.FICHAS if t not in st.mesa and t not in st.manos[i]]
        vac = [0, 0, 0]
        for j in range(3):
            for n in st.vacios[j]:
                vac[j] |= 1 << n
        enmesa = [0] * 7
        for t in st.mesa:
            enmesa[t[0]] += 1
            if t[1] != t[0]:
                enmesa[t[1]] += 1
        izq, der = st.izq, st.der
        nmesa = len(st.mesa)
        tot = [0.0] * len(cand)
        for _ in range(1 if trampa else muestras):
            if trampa:      # techo: ve las manos de verdad
                A, B = [IDX[t] for t in st.manos[a]], [IDX[t] for t in st.manos[b]]
            else:
                A, B = _muestrear(ocultas, len(st.manos[a]), len(st.manos[b]), vac[a], vac[b])
            manos = [None, None, None]
            manos[i], manos[a], manos[b] = mia, A, B
            for c, (t, lado) in enumerate(cand):
                lado_i = 0 if lado == 'i' else 1
                marc, w = rollout(manos, enmesa, izq, der, st.marcador, i, st.ultimo,
                                  st.fallos, st.cobrado, st.seguidos, nmesa, vac,
                                  primera=(i, IDX[t], lado_i))
                if marcador_aware:
                    tot[c] += valor(marc, i, w == i)
                else:
                    o = rivales(i)
                    tot[c] += marc[i] - min(marc[o[0]], marc[o[1]])
        k = max(range(len(cand)), key=lambda c: (tot[c], M.PUNTOS[cand[c][0]]))
        return cand[k]
    sabio.__name__ = "omnisciente" if trampa else f"sabio{muestras}"
    return sabio


# ═══════════════ POLÍTICA LEXICOGRÁFICA PARAMETRIZABLE ═══════════════
# "lex:ahogo,-pierde,-amenaza,cerco,cebo,cob,pts"  → orden de prioridades.
# Sirve para probar variantes del Maestro sin escribir una función por cada una.

def rasgos_jugada(st, i, sin_ubicar, N, largo, sueltas, m):
    t, lado = m
    ni, nd = st.extremos_tras(t, lado)
    riv = rivales(i)
    resto = st.manos[i] - {t}
    f = {}
    ah = 0
    for j in riv:
        v = st.vacios[j]
        ah += 2 if (ni in v and nd in v) else (1 if (ni in v or nd in v) else 0)
    f["ahogo"] = ah
    f["amenaza"] = sum(1 for x in sin_ubicar if M.tiene(x, ni) or M.tiene(x, nd))
    f["cob"] = sum(1 for x in resto if M.tiene(x, ni) or M.tiene(x, nd))
    pierde = 0
    if st.izq is not None:
        for n in {st.izq, st.der}:
            if any(M.tiene(x, n) for x in st.manos[i]) and not any(M.tiene(x, n) for x in resto):
                pierde += 1
    f["pierde"] = pierde
    f["caras"] = len({n for x in resto for n in x})
    f["pts"] = M.PUNTOS[t]
    f["doble"] = int(M.es_doble(t))
    f["cerco"] = ((ni == N) + (nd == N)) if largo >= 4 else 0
    cebo = 0
    if largo >= 4:
        for c in (ni, nd):
            if c != N and (min(c, N), max(c, N)) in sueltas:
                cebo += 1
    f["cebo"] = cebo
    f["respondo"] = int(f["cob"] > 0)
    return f


def hacer_lex(orden):
    campos = [(c[1:], -1) if c.startswith("-") else (c, 1) for c in orden.split(",")]

    def pol(st, i, mv):
        N, largo = M.palo_largo(st.manos[i])
        su = st.sin_ubicar(i)
        sueltas = ({x for x in su if M.tiene(x, N)} if largo >= 4 else set())

        def k(m):
            f = rasgos_jugada(st, i, su, N, largo, sueltas, m)
            return tuple(s * f[c] for c, s in campos)
        return max(mv, key=k)
    pol.__name__ = "lex:" + orden
    return pol



def hacer_lin(spec):
    """"lin:ahogo=20,amenaza=-1,pierde=-1.5,pts=0.3"  → suma ponderada de rasgos."""
    pesos = [(c.split("=")[0], float(c.split("=")[1])) for c in spec.split(",")]

    def pol(st, i, mv):
        N, largo = M.palo_largo(st.manos[i])
        su = st.sin_ubicar(i)
        sueltas = ({x for x in su if M.tiene(x, N)} if largo >= 4 else set())

        def k(m):
            f = rasgos_jugada(st, i, su, N, largo, sueltas, m)
            return sum(w * f[c] for c, w in pesos)
        return max(mv, key=k)
    pol.__name__ = "lin:" + spec
    return pol


# ═══════════════════════════ REGISTRO ═══════════════════════════

POLITICAS = {
    "novato": M.nivel1_novato,
    "casual": M.nivel2_casual,
    "jugador": M.nivel3_jugador,
    "fogueado": M.nivel4_fogueado,
    "maestro": M.nivel5_maestro,
    "balance": M.nivel5b_balance,
    "maestro+salida": salida_con_doble(M.nivel5_maestro),
    "jugador+salida": salida_con_doble(M.nivel3_jugador),
    "marcador": maestro_marcador,
    "marcador+salida": salida_con_doble(maestro_marcador),
}


def politica(nombre):
    if nombre in POLITICAS:
        return POLITICAS[nombre]
    if nombre.startswith("lex:"):
        return hacer_lex(nombre[4:])
    if nombre.startswith("lin:"):
        return hacer_lin(nombre[4:])
    if nombre.startswith("sal:"):
        return salida_con_doble(politica(nombre[4:]))
    if nombre == "omnisciente":
        return hacer_sabio(1, trampa=True)
    if nombre.startswith("sabio"):
        resto = nombre[5:]
        puntos = resto.endswith("pts")
        n = int(resto.replace("pts", "") or 24)
        return hacer_sabio(n, marcador_aware=not puntos)
    raise KeyError(nombre)


# ═══════════════════════════ TORNEOS ═══════════════════════════

def _trabajo_torneo(args):
    nombre, rival, k0, n, semilla = args
    random.seed(semilla)
    M.PASE_EN_TRANCA = os.environ.get("PINTINTIN_PASE_EN_TRANCA", "1") == "1"
    pol, riv = politica(nombre), politica(rival)
    perdidas = 0
    for k in range(k0, k0 + n):
        rot = k % 3
        pols = [pol if j == rot else riv for j in range(3)]
        perdedor, _ = M.jugar_ronda(pols)
        perdidas += (perdedor == rot)
    return perdidas


def torneo(nombre, rival, rondas=3000, semilla=1, procesos=None):
    procesos = procesos or os.cpu_count()
    trozo = -(-rondas // procesos)
    trozo += (-trozo) % 3                    # múltiplo de 3: asientos parejos
    tareas = []
    k = 0
    while k < rondas:
        n = min(trozo, rondas - k)
        tareas.append((nombre, rival, k, n, semilla * 7919 + k))
        k += n
    with Pool(procesos) as p:
        return sum(p.map(_trabajo_torneo, tareas)), rondas


# ═══════════════════════════ VERIFICACIÓN ═══════════════════════════

def _trabajo_verif(args):
    n, semilla = args
    random.seed(semilla)
    pols = [M.nivel3_jugador] * 3
    r = dict(manos=0, tranca=0, rondas=0, largo=0, subita=0,
             ult1=[0, 0], ult3=[0, 0], cruza=[0, 0], cierre_tranca=0,
             sal_doble=[0, 0, 0], sal_otra=[0, 0, 0])
    for _ in range(n):
        marcador, ganador, primera = [0, 0, 0], None, True
        cruzo, ult = None, {}
        manos = 0
        ultimo_res = None
        for _m in range(40):
            if max(marcador) >= M.META:
                break
            h = M.Mano(marcador, ganador if ganador is not None else 0, pols, primera_oficial=primera)
            res, w = h.correr()
            manos += 1
            r["manos"] += 1
            r["tranca"] += res == 'tra'
            ultimo_res = res
            marcador, ganador, primera = h.marcador, w, False
            bajo = min(marcador)
            abajo = [j for j in range(3) if marcador[j] == bajo]
            if len(abajo) == 1 and manos in (1, 3):
                ult[manos] = abajo[0]
            if cruzo is None:
                sobre = [j for j in range(3) if marcador[j] >= 120]
                if len(sobre) == 1:
                    cruzo = sobre[0]
        r["rondas"] += 1
        r["largo"] += manos
        r["cierre_tranca"] += ultimo_res == 'tra'
        bajo = min(marcador)
        abajo = [j for j in range(3) if marcador[j] == bajo]
        if len(abajo) > 1:
            r["subita"] += 1
        perdedor, _ = (abajo[0], None) if len(abajo) == 1 else (None, None)
        for m, key in ((1, "ult1"), (3, "ult3")):
            if m in ult and perdedor is not None:
                r[key][0] += ult[m] == perdedor
                r[key][1] += 1
        if cruzo is not None and perdedor is not None:
            r["cruza"][0] += cruzo != perdedor
            r["cruza"][1] += 1
    return r


def _trabajo_salida(args):
    """Salida libre: probabilidad de que falle el siguiente y bono medio del salidor."""
    n, semilla = args
    random.seed(semilla)
    out = {"doble": [0, 0, 0.0], "blanco_uno": [0, 0, 0.0], "gordas": [0, 0, 0.0]}
    for _ in range(n):
        d = M.FICHAS[:]
        random.shuffle(d)
        manos = [set(d[0:7]), set(d[7:14]), set(d[14:21])]
        for t in manos[0]:
            tipo = ("doble" if M.es_doble(t) else
                    "blanco_uno" if (t[0] in (0, 1) or t[1] in (0, 1)) else "gordas")
            cuenta = 0
            for j in (1, 2):
                if not any(M.tiene(x, t[0]) or M.tiene(x, t[1]) for x in manos[j]):
                    cuenta += 1
                else:
                    break
            falla1 = cuenta >= 1
            valor_ = 30 if M.es_doble(t) else 60
            pago = min(60, valor_ * cuenta)
            o = out[tipo]
            o[0] += falla1
            o[1] += 1
            o[2] += pago
    return out


def verificar(rondas=30000):
    procesos = os.cpu_count()
    tareas = [(rondas // procesos, 50 + k) for k in range(procesos)]
    with Pool(procesos) as p:
        partes = p.map(_trabajo_verif, tareas)
        sal = p.map(_trabajo_salida, [(4000, 90 + k) for k in range(procesos)])
    r = partes[0]
    for q in partes[1:]:
        for c, v in q.items():
            if isinstance(v, list):
                r[c] = [a + b for a, b in zip(r[c], v)]
            else:
                r[c] += v
    s = sal[0]
    for q in sal[1:]:
        for c in s:
            s[c] = [a + b for a, b in zip(s[c], q[c])]
    print(f"Verificación · {r['rondas']} rondas de tres 'Jugador' (nivel 3)\n")
    print(f"  manos por ronda .................. {r['largo'] / r['rondas']:.2f}   (publicado 4,94)")
    print(f"  manos que trancan ................ {fmt(r['tranca'], r['manos'])}   (publicado 39,5%)")
    print(f"  la mano final es tranca .......... {fmt(r['cierre_tranca'], r['rondas'])}   (publicado 50,4%)")
    print(f"  muerte súbita .................... {fmt(r['subita'], r['rondas'])}   (publicado 7,1%)")
    print(f"  último tras la 1ª mano pierde .... {fmt(*r['ult1'])}   (publicado 56,2%)")
    print(f"  último tras la 3ª mano pierde .... {fmt(*r['ult3'])}   (publicado 65,8%)")
    print(f"  primero en cruzar 120 no pierde .. {fmt(*r['cruza'])}   (publicado 96,5%)")
    print("\n  Salida libre (reparto al azar):   P(falla el siguiente)   bono esperado")
    for c, (k, n, pago) in s.items():
        print(f"    {c:<12} {fmt(k, n):>28}   {pago / n:5.2f} pts")


# ═══════════════════ QUÉ HACE EL SABIO DISTINTO AL MAESTRO ═══════════════════

def _rasgos(st, i, m):
    t, lado = m
    ni, nd = st.extremos_tras(t, lado)
    resto = st.manos[i] - {t}
    riv = rivales(i)
    pierde = 0
    if st.izq is not None:
        for n in {st.izq, st.der}:
            if any(M.tiene(x, n) for x in st.manos[i]) and not any(M.tiene(x, n) for x in resto):
                pierde += 1
    vivas = [n for n in ({ni, nd}) if any(M.tiene(x, n) for x in M.FICHAS
                                            if x not in st.mesa and x != t)]
    cobro = sum(1 for j in riv if all(n in st.vacios[j] for n in vivas)) if vivas else 0
    return dict(
        pts=M.PUNTOS[t], doble=int(M.es_doble(t)),
        cob=sum(1 for x in resto if M.tiene(x, ni) or M.tiene(x, nd)),
        caras_mano=len({n for x in resto for n in x}),
        pierde=pierde, cobro=cobro, vivas=len(vivas),
        amenaza=sum(1 for x in st.sin_ubicar(i) if M.tiene(x, ni) or M.tiene(x, nd)),
    )


def _trabajo_dif(args):
    n, semilla, muestras = args
    random.seed(semilla)
    sab = hacer_sabio(muestras)
    reg = []

    def espia(st, i, mv):
        a = sab(st, i, mv)
        b = M.nivel5_maestro(st, i, mv)
        ea = (a[0], tuple(sorted(st.extremos_tras(*a))))
        eb = (b[0], tuple(sorted(st.extremos_tras(*b))))
        o = rivales(i)
        estado = ("congelado" if st.marcador[i] >= 120 else
                  "ultimo" if st.marcador[i] < min(st.marcador[j] for j in o) else
                  "primero" if st.marcador[i] > max(st.marcador[j] for j in o) else "medio")
        reg.append(dict(igual=ea == eb, salida=st.izq is None, mano=len(st.manos[i]),
                        estado=estado, s=_rasgos(st, i, a), m=_rasgos(st, i, b)))
        return a
    for k in range(n):
        rot = k % 3
        pols = [espia if j == rot else M.nivel5_maestro for j in range(3)]
        M.jugar_ronda(pols)
    return reg


def diferencias(rondas=600, muestras=24):
    procesos = os.cpu_count()
    with Pool(procesos) as p:
        partes = p.map(_trabajo_dif, [(rondas // procesos, 300 + k, muestras) for k in range(procesos)])
    reg = [r for q in partes for r in q]
    dec = [r for r in reg if len(r) and r["s"] is not None]
    dif = [r for r in dec if not r["igual"]]
    print(f"Decisiones con ≥2 opciones reales: {len(dec)} · el Sabio difiere del Maestro en {fmt(len(dif), len(dec))}\n")

    def por(clave):
        g = {}
        for r in dec:
            v = r[clave]
            g.setdefault(v, [0, 0])
            g[v][0] += not r["igual"]
            g[v][1] += 1
        for v in sorted(g, key=str):
            print(f"    {str(v):<10} difiere {fmt(*g[v])}   (n={g[v][1]})")
    print("  Por estado del marcador:"); por("estado")
    print("  Salida libre vs en la mano:"); por("salida")
    print("  Por fichas en mano:"); por("mano")
    print("\n  Cuando difieren, el Sabio elige una ficha con…   (Sabio > Maestro · igual · Sabio < Maestro)")
    for c in ("pts", "doble", "cob", "caras_mano", "pierde", "cobro", "vivas", "amenaza"):
        mas = sum(1 for r in dif if r["s"][c] > r["m"][c])
        menos = sum(1 for r in dif if r["s"][c] < r["m"][c])
        igual = len(dif) - mas - menos
        ms = sum(r["s"][c] for r in dif) / len(dif)
        mm = sum(r["m"][c] for r in dif) / len(dif)
        print(f"    {c:<11} {100*mas/len(dif):5.1f}% · {100*igual/len(dif):5.1f}% · {100*menos/len(dif):5.1f}%"
              f"    media Sabio {ms:5.2f} vs Maestro {mm:5.2f}")
    for est in ("congelado", "ultimo", "primero", "medio"):
        sub = [r for r in dif if r["estado"] == est]
        if len(sub) < 30:
            continue
        print(f"\n  Estado '{est}' ({len(sub)} diferencias):")
        for c in ("pts", "cob", "pierde", "cobro", "amenaza", "vivas"):
            ms = sum(r["s"][c] for r in sub) / len(sub)
            mm = sum(r["m"][c] for r in sub) / len(sub)
            print(f"    {c:<11} Sabio {ms:5.2f} vs Maestro {mm:5.2f}")
    sal = [r for r in dif if r["salida"]]
    if sal:
        d1 = sum(r["s"]["doble"] for r in sal) / len(sal)
        d2 = sum(r["m"]["doble"] for r in sal) / len(sal)
        print(f"\n  Salidas libres donde difieren: {len(sal)} · sale de doble: Sabio {100*d1:.0f}% vs Maestro {100*d2:.0f}%")


# ═══════════════════ ESTUDIO DE LA SALIDA LIBRE (oráculo PIMC) ═══════════════════

def _trabajo_salida_libre(args):
    n, semilla, muestras, marc = args
    random.seed(semilla)
    filas = []
    for _ in range(n):
        d = M.FICHAS[:]
        random.shuffle(d)
        mano = d[0:7]
        mia = [IDX[t] for t in mano]
        ocultas = [IDX[t] for t in d[7:]]
        tot = {t: [0.0, 0.0] for t in mano}
        for _s in range(muestras):
            random.shuffle(ocultas)
            A, B = ocultas[:7], ocultas[7:14]
            for t in mano:
                mm, w = rollout([mia, A, B], [0] * 7, None, None, marc, 0, None, 0, 0, 0, 0,
                                [0, 0, 0], primera=(0, IDX[t], 1))
                tot[t][0] += valor(mm, 0, w == 0)
                tot[t][1] += (mm[0] - marc[0]) - ((mm[1] - marc[1]) + (mm[2] - marc[2])) / 2
        media = sum(v[0] for v in tot.values()) / 7 / muestras
        for t in mano:
            comp = sum(1 for x in mano if x != t and (M.tiene(x, t[0]) or M.tiene(x, t[1])))
            resto = [x for x in mano if x != t]
            pierde_cara = int(len({n for x in resto for n in x}) < len({n for x in mano for n in x}))
            _, largo = M.palo_largo(mano)
            N, _l = M.palo_largo(mano)
            filas.append(dict(
                doble=int(M.es_doble(t)), comp=comp, pts=M.PUNTOS[t],
                frag=int(t[0] in (0, 1) or t[1] in (0, 1)), pierde_cara=pierde_cara,
                del_largo=int(M.tiene(t, N) and largo >= 4),
                ndobles=sum(1 for x in mano if M.es_doble(x)),
                ventaja=tot[t][0] / muestras - media, margen=tot[t][1] / muestras,
                mejor=0))
        mejor = max(range(len(filas) - 7, len(filas)), key=lambda q: filas[q]["ventaja"])
        filas[mejor]["mejor"] = 1
    return filas


def estudio_salida(manos=1200, muestras=200, marc=(40, 40, 40)):
    procesos = os.cpu_count()
    with Pool(procesos) as p:
        partes = p.map(_trabajo_salida_libre,
                       [(manos // procesos, 700 + k, muestras, list(marc)) for k in range(procesos)])
    f = [r for q in partes for r in q]
    print(f"Salida libre · {len(f) // 7} manos · {muestras} simulaciones por ficha · marcador {marc}")
    print("ventaja = P(no quedar último) de salir con esa ficha menos la media de la mano, en puntos %\n")

    def grupo(nombre, filtro):
        g = [r for r in f if filtro(r)]
        if not g:
            return
        v = 100 * sum(r["ventaja"] for r in g) / len(g)
        mg = sum(r["margen"] for r in g) / len(g)
        mj = 100 * sum(r["mejor"] for r in g) / len(g)
        print(f"  {nombre:<38} n={len(g):5d}  ventaja {v:+5.2f}  margen {mg:+5.1f} pts  es la mejor {mj:4.1f}%")
    grupo("doble", lambda r: r["doble"])
    for c in range(0, 5):
        grupo(f"  doble con {c} acompañantes", lambda r, c=c: r["doble"] and r["comp"] == c)
    grupo("no doble", lambda r: not r["doble"])
    grupo("  no doble con blanco o uno", lambda r: not r["doble"] and r["frag"])
    grupo("  no doble de dos palos gordos", lambda r: not r["doble"] and not r["frag"])
    grupo("  no doble que me quita una cara", lambda r: not r["doble"] and r["pierde_cara"])
    grupo("  no doble del palo largo (4+)", lambda r: not r["doble"] and r["del_largo"])
    for lo, hi in ((0, 4), (5, 7), (8, 9), (10, 12)):
        grupo(f"peso {lo}-{hi}", lambda r, lo=lo, hi=hi: lo <= r["pts"] <= hi)
        grupo(f"  doble · peso {lo}-{hi}", lambda r, lo=lo, hi=hi: r["doble"] and lo <= r["pts"] <= hi)
        grupo(f"  no doble · peso {lo}-{hi}", lambda r, lo=lo, hi=hi: not r["doble"] and lo <= r["pts"] <= hi)
    for nd in range(0, 4):
        grupo(f"manos con {nd} dobles · sale de doble", lambda r, nd=nd: r["ndobles"] == nd and r["doble"])
        grupo(f"manos con {nd} dobles · sale de no doble", lambda r, nd=nd: r["ndobles"] == nd and not r["doble"])


# ═══════════════════════════════ CLI ═══════════════════════════════

def _arg(nombre, defecto):
    if nombre in sys.argv:
        return type(defecto)(sys.argv[sys.argv.index(nombre) + 1])
    return defecto


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "bench"
    rondas = _arg("--rondas", 3000)
    t0 = time.time()
    if cmd == "tabla":
        tb = construir_tabla(_arg("--rondas", 60000))
        print(f"tabla de valor: {len(tb)} celdas → {RUTA_TABLA}")
    elif cmd == "verificar":
        verificar(_arg("--rondas", 30000))
    elif cmd == "salida":
        estudio_salida(_arg("--manos", 1200), _arg("--muestras", 200))
    elif cmd == "diferencias":
        diferencias(_arg("--rondas", 600), _arg("--muestras", 24))
    elif cmd == "duelo":
        a, b = sys.argv[2], sys.argv[3]
        k, n = torneo(a, b, rondas)
        print(f"  {a:<18} vs 2 × {b:<14} {fmt(k, n)}")
    elif cmd == "bench":
        rival = _arg("--rival", "jugador")
        print(f"Cada política contra dos '{rival}' · {rondas} rondas · IC 95%\n")
        nombres = [a for a in sys.argv[2:] if not a.startswith("--") and not a.isdigit()
                   and a != rival] or list(POLITICAS)
        for nombre in nombres:
            k, n = torneo(nombre, rival, rondas)
            print(f"  {nombre:<18} {fmt(k, n)}")
    print(f"\n({time.time() - t0:.0f} s)")
