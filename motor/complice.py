"""
LA ESTRATEGIA DEL CÓMPLICE — ¿conviene ayudar al único que tiene puntos?
=========================================================================

Estrategia de campo: si solo uno tiene puntos y yo voy empatado (normalmente
en 0) con el otro, ayudo al líder a cerrar y no dejo que el otro anote. Si la
ronda cierra con los dos de abajo empatados, hay muerte súbita (50%) en vez
de arriesgarme a quedar solo en el último lugar.

Experimento controlado: rondas que arrancan desde un marcador fijo
[líder, 0, 0], con el líder saliendo (ganó la mano anterior). Se compara MI
probabilidad de perder jugando normal contra jugando de cómplice, con los
mismos rivales y el mismo marcador.

    python3 motor/complice.py
    python3 motor/complice.py --rondas 12000
"""

import os
import random
import sys
import time
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motor_pintintin as M  # noqa: E402
from laboratorio import fmt, politica, rivales  # noqa: E402


def situacion(st, i, margen=0, desde=0):
    """(líder, otro) si hay un único líder y yo voy empatado con el otro.
    `margen`: tolerancia del empate. `desde`: puntos mínimos del líder."""
    s = st.marcador
    o = rivales(i)
    lider = max(o, key=lambda j: s[j])
    otro = o[0] if lider == o[1] else o[1]
    if s[lider] > s[i] and s[lider] > s[otro] and abs(s[i] - s[otro]) <= margen and s[lider] >= desde:
        return lider, otro
    return None


def hacer_complice(base="maestro", modo="alimentar", desde=0, margen=0):
    """modo:
       'alimentar' → no bloqueo al líder, ahogo al otro, conservo respuesta
       'barato'    → juego como Maestro y solo desempato a favor del líder
       'veto'      → solo me ocupo de que el otro no cobre: conservo respuesta
                     y ahogo al otro; el líder me da igual
    """
    pol_base = politica(base)

    def pol(st, i, mv):
        sit = situacion(st, i, margen, desde)
        if sit is None:
            return pol_base(st, i, mv)
        lider, otro = sit
        vL, vO = st.vacios[lider], st.vacios[otro]
        su = st.sin_ubicar(i)

        def k(m):
            t, lado = m
            ni, nd = st.extremos_tras(t, lado)
            resto = st.manos[i] - {t}
            cob = sum(1 for x in resto if M.tiene(x, ni) or M.tiene(x, nd))
            ah_L = (ni in vL) + (nd in vL)
            ah_O = (ni in vO) + (nd in vO)
            # cuántas fichas sin ubicar le sirven al líder (no descartadas por sus vacíos)
            para_L = sum(1 for x in su if (M.tiene(x, ni) or M.tiene(x, nd))
                         and x[0] not in vL and x[1] not in vL)
            if modo == "alimentar":
                return (-ah_L, ah_O, int(cob > 0), para_L, M.PUNTOS[t])
            ah = 0
            for j in (lider, otro):
                v = st.vacios[j]
                ah += 2 if (ni in v and nd in v) else (1 if (ni in v or nd in v) else 0)
            amen = sum(1 for x in su if M.tiene(x, ni) or M.tiene(x, nd))
            if modo == "barato":
                # mi juego primero (ahogo, cerrar la mesa); ayudar solo como desempate
                return (ah, -amen, -ah_L, ah_O, para_L, cob, M.PUNTOS[t])
            if modo == "control":
                # lo mismo sin términos de ayuda: aísla el efecto de "ayudar"
                return (ah, -amen, cob, M.PUNTOS[t])
            # SUAVE: puntas que el líder puede jugar (sigue cobrando y cierra)
            # DURA:  puntas que al líder le cuestan (gasta sus propias caras)
            if modo == "suave":
                return (-ah_L, para_L, ah, -amen, cob, M.PUNTOS[t])
            if modo == "dura":
                return (ah_L, -para_L, ah, -amen, cob, M.PUNTOS[t])
            if modo == "suave_barato":
                return (ah, -amen, -ah_L, para_L, cob, M.PUNTOS[t])
            if modo == "dura_barato":
                return (ah, -amen, ah_L, -para_L, cob, M.PUNTOS[t])
            return (int(cob > 0), ah_O, cob, M.PUNTOS[t])
        return max(mv, key=k)
    pol.__name__ = f"complice-{modo}-{base}-{desde}"
    return pol


def ronda_desde(marcador, salidor, pols):
    """Como M.jugar_ronda pero desde un marcador dado. Devuelve (perdedor, subita)."""
    marcador = list(marcador)
    ganador = salidor
    for _ in range(40):
        if max(marcador) >= M.META:
            break
        h = M.Mano(marcador, ganador, pols)
        _, w = h.correr()
        marcador, ganador = h.marcador, w
    bajo = min(marcador)
    abajo = [j for j in range(3) if marcador[j] == bajo]
    if len(abajo) == 1:
        return abajo[0], False
    duo = abajo[:2]
    h = M.Mano(marcador, duo[0], pols, modo="subita", duo=duo)
    M.salida_subita(h, duo)
    _, salvado = h.correr()
    return (duo[1] if salvado == duo[0] else duo[0]), True


def _pol(nombre):
    if nombre.startswith("complice"):
        _, modo, base, desde = nombre.split(":")
        return hacer_complice(base, modo, int(desde))
    return politica(nombre)


def _trabajo(args):
    yo, otro, lider, L, lado, n, semilla = args
    random.seed(semilla)
    # asientos: yo = 0. lado 'derecha' → el líder juega justo después de mí (asiento 1)
    sL, sO = (1, 2) if lado == "derecha" else (2, 1)
    pols = [None, None, None]
    pols[0], pols[sL], pols[sO] = _pol(yo), _pol(lider), _pol(otro)
    marc = [0, 0, 0]
    marc[sL] = L
    pierdo = subita = lider_pierde = 0
    for _ in range(n):
        p, s = ronda_desde(marc, sL, pols)
        pierdo += p == 0
        subita += s
        lider_pierde += p == sL
    return pierdo, subita, lider_pierde, n


def medir(yo, otro, lider, L, lado, rondas, semilla=1):
    procesos = os.cpu_count()
    n = -(-rondas // procesos)
    tareas = [(yo, otro, lider, L, lado, n, semilla * 1000 + k) for k in range(procesos)]
    with Pool(procesos) as p:
        r = p.map(_trabajo, tareas)
    tot = [sum(x[c] for x in r) for c in range(4)]
    return tot


def dura_o_suave(rondas):
    print("── ¿Dura o suave al líder?  Marcador inicial [líder, 0, 0], yo empatado con el otro")
    print("   control = mi juego sin ningún término de ayuda (aísla el efecto)")
    print(f"   {'líder':>6} {'lado':<10} {'estrategia':<28}{'pierdo':>24}{'súbita':>9}{'líder pierde':>14}")
    for yo in ("maestro", "jugador"):
        for L in (30, 90, 140):
            for lado in ("derecha", "izquierda"):
                casos = [("normal", yo)] + [(m, f"complice:{m}:{yo}:0") for m in
                                            ("control", "suave", "dura", "suave_barato", "dura_barato")]
                for nombre, pol in casos:
                    k, s_, lp, n = medir(pol, "maestro", "maestro", L, lado, rondas)
                    print(f"   {L:>6} {lado:<10} {yo + ' · ' + nombre:<28}{fmt(k, n):>24}{100*s_/n:>8.1f}%{100*lp/n:>13.1f}%")
                print()


def solo_barato(rondas):
    print("── Cómplice BARATO: juego como Maestro y ayudo al líder solo como desempate")
    print(f"   {'líder':>6} {'lado':<10} {'estrategia':<34}{'pierdo':>24}{'súbita':>9}{'líder pierde':>14}")
    for yo_base, otro in (("maestro", "maestro"), ("jugador", "maestro")):
        for L in (30, 90, 140):
            for lado in ("derecha", "izquierda"):
                for nombre, yo in ((f"normal ({yo_base})", yo_base),
                                   (f"cómplice barato ({yo_base})", f"complice:barato:{yo_base}:0")):
                    k, s_, lp, n = medir(yo, otro, "maestro", L, lado, rondas)
                    print(f"   {L:>6} {lado:<10} {nombre:<34}{fmt(k, n):>24}{100*s_/n:>8.1f}%{100*lp/n:>13.1f}%")
        print()


if __name__ == "__main__" and "--dura" in sys.argv:
    dura_o_suave(int(sys.argv[sys.argv.index("--rondas") + 1]) if "--rondas" in sys.argv else 6000)
    sys.exit()

if __name__ == "__main__" and "--barato" in sys.argv:
    solo_barato(int(sys.argv[sys.argv.index("--rondas") + 1]) if "--rondas" in sys.argv else 6000)
    sys.exit()

if __name__ == "__main__":
    rondas = int(sys.argv[sys.argv.index("--rondas") + 1]) if "--rondas" in sys.argv else 6000
    t0 = time.time()
    print(f"LA ESTRATEGIA DEL CÓMPLICE · {rondas} rondas por casilla · marcador inicial [líder, 0, 0]")
    print("El líder sale (ganó la mano anterior). 'pierdo' = yo quedo tercero. Neutro para los dos de abajo ≈ la mitad de lo que no pierde el líder.\n")

    def bloque(titulo, casos, Ls=(30, 60, 90, 120, 140), lados=("derecha", "izquierda")):
        print(f"── {titulo}")
        print(f"   {'líder':>6} {'lado':<10} {'estrategia':<34}{'pierdo':>24}{'súbita':>9}{'líder pierde':>14}")
        for L in Ls:
            for lado in lados:
                for nombre, (yo, otro, lider) in casos:
                    k, s, lp, n = medir(yo, otro, lider, L, lado, rondas)
                    print(f"   {L:>6} {lado:<10} {nombre:<34}{fmt(k, n):>24}{100*s/n:>8.1f}%{100*lp/n:>13.1f}%")
            print()

    bloque("Los tres juegan como Maestro; solo cambio yo", [
        ("normal (Maestro)", ("maestro", "maestro", "maestro")),
        ("cómplice: alimento al líder", ("complice:alimentar:maestro:0", "maestro", "maestro")),
        ("cómplice: solo veto al otro", ("complice:veto:maestro:0", "maestro", "maestro")),
    ])
    bloque("Soy más flojo que el otro de abajo (yo Jugador, ellos Maestros)", [
        ("normal (Jugador)", ("jugador", "maestro", "maestro")),
        ("cómplice: alimento al líder", ("complice:alimentar:jugador:0", "maestro", "maestro")),
    ], Ls=(30, 90, 140))
    bloque("Soy más fuerte que el otro de abajo (yo Maestro, el otro Jugador)", [
        ("normal (Maestro)", ("maestro", "jugador", "maestro")),
        ("cómplice: alimento al líder", ("complice:alimentar:maestro:0", "jugador", "maestro")),
    ], Ls=(30, 90, 140))
    bloque("Los dos de abajo juegan de cómplice", [
        ("los dos normales", ("maestro", "maestro", "maestro")),
        ("los dos cómplices", ("complice:alimentar:maestro:0", "complice:alimentar:maestro:0", "maestro")),
    ], Ls=(30, 90, 140), lados=("derecha",))
    print(f"({time.time() - t0:.0f} s)")
