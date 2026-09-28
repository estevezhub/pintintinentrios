"""
LA REMONTADA — ¿conviene cambiar de estrategia cuando vas abajo?
=================================================================

Tres preguntas:

  1. EL RELOJ: yendo último, ¿cuántas manos quedan y cómo cae tu chance?
  2. CAMBIAR O NO: desde marcadores fijos donde voy último, ¿algún plan
     alternativo rinde más que jugar normal (Maestro)?
  3. CUÁNDO: si algún plan rinde, ¿a partir de qué distancia activarlo?

    python3 motor/remontada.py reloj
    python3 motor/remontada.py planes  --rondas 6000
    python3 motor/remontada.py sabio   --rondas 1500
    python3 motor/remontada.py cuando  --plan tranca --rondas 12000
"""

import os
import random
import sys
import time
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motor_pintintin as M  # noqa: E402
from laboratorio import fmt, politica, rivales  # noqa: E402

# Escenarios: (nombre, mi marcador, el segundo, el líder)
ESCENARIOS = [
    ("temprano · 40 abajo",       0,  40,  70),
    ("medio · 20 abajo",         50,  70, 100),
    ("medio · 40 abajo",         30,  70, 100),
    ("medio · 60 abajo",         10,  70, 100),
    ("tarde · 40 abajo, líder 125", 60, 100, 125),
    ("tarde · 70 abajo, líder 125", 30, 100, 125),
]


# ───────────────────────────── PLANES ─────────────────────────────

def estado(st, i):
    s = st.marcador
    o = rivales(i)
    if not all(s[i] < s[j] for j in o):
        return None
    seg = min(o, key=lambda j: s[j])
    lid = o[0] if seg == o[1] else o[1]
    return seg, lid, s[seg] - s[i]


def hacer_plan(plan, umbral=1, base="maestro"):
    """Juega `base` salvo cuando voy último a `umbral`+ puntos del segundo."""
    pol_base = politica(base)
    if plan == "normal":
        return pol_base

    def pol(st, i, mv):
        e = estado(st, i)
        if e is None or e[2] < umbral:
            return pol_base(st, i, mv)
        seg, lid, _ = e
        su = st.sin_ubicar(i)
        N, largo = M.palo_largo(st.manos[i])
        sueltas = {x for x in su if M.tiene(x, N)} if largo >= 4 else set()

        def k(m):
            t, lado = m
            ni, nd = st.extremos_tras(t, lado)
            resto = st.manos[i] - {t}

            def ah(j):
                v = st.vacios[j]
                return 2 if (ni in v and nd in v) else (1 if (ni in v or nd in v) else 0)
            a = ah(seg) + ah(lid)
            amen = sum(1 for x in su if M.tiene(x, ni) or M.tiene(x, nd))
            cob = sum(1 for x in resto if M.tiene(x, ni) or M.tiene(x, nd))
            caras = len({n for x in resto for n in x})
            pts = M.PUNTOS[t]
            cerco = ((ni == N) + (nd == N)) if largo >= 4 else 0
            cebo = sum(1 for c in (ni, nd) if largo >= 4 and c != N and (min(c, N), max(c, N)) in sueltas)
            if plan == "segundo":      # todo el fuego contra el segundo
                return (ah(seg), a, -amen, cob, pts)
            if plan == "lider":        # frenar al líder: alargar la ronda
                return (ah(lid), a, -amen, cob, pts)
            if plan == "tranca":       # soltar peso: apostar a ganar la tranca
                return (a, pts, -amen, cob)
            if plan == "dominar":      # conservar respuestas: apostar a dominar
                return (a, cob, caras, -amen, pts)
            if plan == "cerco":        # cobrar grande: cercar el palo largo
                return (a, cerco, cebo, -amen, cob, pts)
            raise KeyError(plan)
        return max(mv, key=k)
    pol.__name__ = f"{plan}@{umbral}"
    return pol


def _pol(nombre):
    """'plan:umbral:base' o un nombre del laboratorio."""
    if ":" in nombre and nombre.split(":")[0] in ("normal", "segundo", "lider", "tranca", "dominar", "cerco"):
        plan, umbral, base = nombre.split(":")
        return hacer_plan(plan, int(umbral), base)
    return politica(nombre)


# ─────────────────────── RONDA DESDE UN MARCADOR ───────────────────────

def ronda_desde(marcador, salidor, pols, yo=0):
    """Juega hasta 150. Devuelve (perdedor, manos jugadas, mano en que dejé de ir último o 0)."""
    marcador = list(marcador)
    ganador, manos, escape = salidor, 0, 0
    for _ in range(40):
        if max(marcador) >= M.META:
            break
        h = M.Mano(marcador, ganador, pols)
        _, w = h.correr()
        marcador, ganador = h.marcador, w
        manos += 1
        if not escape and any(marcador[j] < marcador[yo] for j in range(3) if j != yo):
            escape = manos
    bajo = min(marcador)
    abajo = [j for j in range(3) if marcador[j] == bajo]
    if len(abajo) == 1:
        return abajo[0], manos, escape
    duo = abajo[:2]
    h = M.Mano(marcador, duo[0], pols, modo="subita", duo=duo)
    M.salida_subita(h, duo)
    _, salvado = h.correr()
    return (duo[1] if salvado == duo[0] else duo[0]), manos, escape


def _trabajo(args):
    yo, esc, n, semilla, seg_derecha_alterna = args
    random.seed(semilla)
    _, mi, sg, ld = esc
    res = []
    for k in range(n):
        # yo = 0; el segundo a mi derecha o a mi izquierda, alternando
        sS, sL = (1, 2) if k % 2 == 0 else (2, 1)
        pols = [None] * 3
        pols[0], pols[sS], pols[sL] = _pol(yo), politica("maestro"), politica("maestro")
        marc = [0] * 3
        marc[0], marc[sS], marc[sL] = mi, sg, ld
        salidor = (sL, sS, 0)[k % 3]          # sale cualquiera: rotado
        res.append(ronda_desde(marc, salidor, pols))
    return res


def correr(yo, esc, rondas, semilla=7):
    procesos = os.cpu_count()
    n = -(-rondas // procesos)
    with Pool(procesos) as p:
        partes = p.map(_trabajo, [(yo, esc, n, semilla * 1000 + k, True) for k in range(procesos)])
    return [r for q in partes for r in q]


# ─────────────────────────────── INFORMES ───────────────────────────────

def reloj(rondas):
    print("1 · EL RELOJ — jugando normal (Maestro) desde cada marcador; yo voy último\n")
    print(f"  {'escenario':<30}{'pierdo':>24}{'manos que':>11}{'la ronda cierra en ≤k manos':>34}{'salgo del':>11}")
    print(f"  {'':<30}{'':>24}{'quedan':>11}{'k=1':>8}{'k=2':>8}{'k=3':>8}{'k=4':>8}   {'último':>9}")
    for esc in ESCENARIOS:
        r = correr("maestro", esc, rondas)
        n = len(r)
        k = sum(p == 0 for p, _, _ in r)
        man = sum(m for _, m, _ in r) / n
        cum = [100 * sum(m <= c for _, m, _ in r) / n for c in (1, 2, 3, 4)]
        esc_ = 100 * sum(e > 0 for _, _, e in r) / n
        print(f"  {esc[0]:<30}{fmt(k, n):>24}{man:>11.2f}" + "".join(f"{c:>7.0f}%" for c in cum) + f"{esc_:>11.0f}%")
    print("\n  Supervivencia: si sigo último tras cada mano, ¿cuánto pierdo?  (escenario 'medio · 40 abajo')")
    r = correr("maestro", ESCENARIOS[2], rondas)
    for m in (1, 2, 3):
        sub = [x for x in r if x[1] >= m + 1 and (x[2] == 0 or x[2] > m)]
        esc_temprano = [x for x in r if x[2] and x[2] <= m]
        if sub:
            print(f"    sigo último tras {m} mano(s) y la ronda sigue: pierdo {fmt(sum(p == 0 for p, _, _ in sub), len(sub))}  (n={len(sub)})")
        if esc_temprano:
            print(f"    ya salí del último en ≤{m} mano(s):              pierdo {fmt(sum(p == 0 for p, _, _ in esc_temprano), len(esc_temprano))}  (n={len(esc_temprano)})")


PLANES = ["normal", "segundo", "lider", "tranca", "dominar", "cerco"]


def planes(rondas):
    print("2 · CAMBIAR O NO — los rivales juegan como Maestro; yo cambio de plan SOLO mientras voy último\n")
    print(f"  {'escenario':<30}{'plan':<10}{'pierdo':>24}{'Δ vs normal':>13}{'salgo del último':>18}")
    for esc in ESCENARIOS:
        base = None
        for plan in PLANES:
            r = correr(f"{plan}:1:maestro", esc, rondas)
            n = len(r)
            k = sum(p == 0 for p, _, _ in r)
            if base is None:
                base = 100 * k / n
            esc_ = 100 * sum(e > 0 for _, _, e in r) / n
            print(f"  {esc[0]:<30}{plan:<10}{fmt(k, n):>24}{100 * k / n - base:>+12.1f}{esc_:>17.0f}%")
        print()


def sabio(rondas):
    print("2b · REFERENCIA — el Sabio (simula la mano y juzga por el marcador) en los mismos escenarios\n")
    for esc in (ESCENARIOS[0], ESCENARIOS[2], ESCENARIOS[4]):
        for yo in ("maestro", "sabio96"):
            r = correr(yo, esc, rondas)
            n = len(r)
            k = sum(p == 0 for p, _, _ in r)
            print(f"  {esc[0]:<30}{yo:<10}{fmt(k, n):>24}")
        print()


def _trabajo_cuando(args):
    nombre, k0, n, semilla = args
    random.seed(semilla)
    pol, riv = _pol(nombre), politica("maestro")
    perd = 0
    for k in range(k0, k0 + n):
        rot = k % 3
        pols = [pol if j == rot else riv for j in range(3)]
        p, _ = M.jugar_ronda(pols)
        perd += p == rot
    return perd


def cuando(plan, rondas):
    print(f"3 · CUÁNDO — rondas completas desde 0-0-0 contra dos Maestros; activo '{plan}' solo si voy último a U+ del segundo\n")
    procesos = os.cpu_count()
    trozo = -(-rondas // procesos)
    trozo += (-trozo) % 3
    for u in (1, 20, 40, 60, 90):
        nombre = f"{plan}:{u}:maestro"
        tareas = [(nombre, k, min(trozo, rondas - k), 99 + k) for k in range(0, rondas, trozo)]
        with Pool(procesos) as p:
            k = sum(p.map(_trabajo_cuando, tareas))
        print(f"  umbral {u:>3}  {fmt(k, rondas)}")
    tareas = [("maestro", k, min(trozo, rondas - k), 99 + k) for k in range(0, rondas, trozo)]
    with Pool(procesos) as p:
        k = sum(p.map(_trabajo_cuando, tareas))
    print(f"  nunca       {fmt(k, rondas)}   (Maestro puro, mismas semillas)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "planes"
    rondas = int(sys.argv[sys.argv.index("--rondas") + 1]) if "--rondas" in sys.argv else 6000
    t0 = time.time()
    if cmd == "reloj":
        reloj(rondas)
    elif cmd == "planes":
        planes(rondas)
    elif cmd == "sabio":
        sabio(rondas)
    elif cmd == "cuando":
        plan = sys.argv[sys.argv.index("--plan") + 1] if "--plan" in sys.argv else "tranca"
        cuando(plan, rondas)
    print(f"\n({time.time() - t0:.0f} s)")
