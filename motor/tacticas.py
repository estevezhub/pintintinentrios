"""
TÁCTICAS DE MESA — "repite, mata y tranca" y el farol de la pinza rota
=======================================================================

Dos reglas de campo, medidas contra dos Maestros:

A. REPITE, MATA Y TRANCA (regla no escrita)
   · Repite: deja expuesto el mismo número que dejaste la vez anterior;
     el siguiente va gastando las que tiene de esa cara.
   · Mata:   juega sobre la punta que el rival acaba de exponer y cámbiala,
     para que no cuadre.
   · Tranca: si puedes trancar seguro y tienes menos fichas, tranca; los
     pases que provocaste dejaron a los otros con más puntos en mano.

B. EL FAROL DE LA PINZA ROTA
   Quien viene repitiendo un número y de pronto juega sobre su propia punta
   —rompiendo el cerco— parece no tener el número de la otra punta. El
   Lector deduce eso; el Faroleador rompe su pinza A PROPÓSITO teniendo ese
   número, para que lo crean sin él.

    python3 motor/tacticas.py rmt    --rondas 12000
    python3 motor/tacticas.py farol  --rondas 12000
"""

import os
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motor_pintintin as M  # noqa: E402
from laboratorio import fmt, politica, rivales  # noqa: E402


# ───────────────────────── rasgos comunes ─────────────────────────

def base_rasgos(st, i, m, vac=None):
    """Rasgos del Maestro para la jugada m, con vacíos opcionales (para el Lector)."""
    vac = vac or st.vacios
    t, lado = m
    ni, nd = st.extremos_tras(t, lado)
    riv = rivales(i)
    ah = 0
    for j in riv:
        v = vac[j]
        ah += 2 if (ni in v and nd in v) else (1 if (ni in v or nd in v) else 0)
    su = st.sin_ubicar(i)
    amen = sum(1 for x in su if M.tiene(x, ni) or M.tiene(x, nd))
    resto = st.manos[i] - {t}
    cob = sum(1 for x in resto if M.tiene(x, ni) or M.tiene(x, nd))
    N, largo = M.palo_largo(st.manos[i])
    cerco = ((ni == N) + (nd == N)) if largo >= 4 else 0
    sueltas = {x for x in su if M.tiene(x, N)} if largo >= 4 else set()
    cebo = sum(1 for c in (ni, nd) if largo >= 4 and c != N and (min(c, N), max(c, N)) in sueltas)
    return dict(ni=ni, nd=nd, ah=ah, amen=amen, cob=cob, cerco=cerco, cebo=cebo,
                pts=M.PUNTOS[t], resto=resto, su=su)


def llave_maestro(f):
    return (f["ah"], -f["amen"], f["cerco"], f["cebo"], f["cob"], f["pts"])


# ───────────────────── A. REPITE, MATA Y TRANCA ─────────────────────

def rasgos_rmt(st, i, m, f):
    t, lado = m
    if st.izq is None:
        return 0, 0, 0, 0
    expone = f["ni"] if lado == 'i' else f["nd"]
    tapa = st.izq if lado == 'i' else st.der
    # repite: dejo expuesto el mismo número que dejé la última vez
    repite = int(bool(st.expuso[i]) and expone == st.expuso[i][-1])
    # mata: tapo la cara que un rival acaba de exponer (2 si es el que jugó justo antes)
    previo = (i + 2) % 3
    mata = 0
    if expone != tapa:
        if st.expuso[previo] and tapa == st.expuso[previo][-1]:
            mata = 2
        elif any(st.expuso[j] and tapa == st.expuso[j][-1] for j in rivales(i)):
            mata = 1
    # tranca segura: ningún rival puede tener ficha para las puntas nuevas, y yo tampoco
    ni, nd = f["ni"], f["nd"]
    sirven = [x for x in f["su"] if M.tiene(x, ni) or M.tiene(x, nd)]
    nadie = all(all(x[0] in st.vacios[j] or x[1] in st.vacios[j] for j in rivales(i)) for x in sirven)
    yo_no = not any(M.tiene(x, ni) or M.tiene(x, nd) for x in f["resto"])
    tranca_f = tranca_p = 0
    if nadie and yo_no:
        mias = len(f["resto"])
        otras = [len(st.manos[j]) for j in rivales(i)]
        tranca_f = 1 if mias < min(otras) else (-1 if mias > min(otras) else 0)
        # versión por puntos: mi mano contra lo esperado de cada rival
        media = sum(M.PUNTOS[x] for x in f["su"]) / max(1, len(f["su"]))
        mis_pts = sum(M.PUNTOS[x] for x in f["resto"])
        tranca_p = 1 if mis_pts < media * min(otras) else -1
    return repite, mata, tranca_f, tranca_p


def hacer_rmt(variante):
    def pol(st, i, mv):
        def k(m):
            f = base_rasgos(st, i, m)
            r, mt, tf, tp = rasgos_rmt(st, i, m, f)
            b = llave_maestro(f)
            if variante == "maestro":
                return b
            if variante == "repite":            # repetir por encima de cerrar la mesa
                return (f["ah"], r) + b[1:]
            if variante == "repite_d":          # repetir como desempate
                return b[:2] + (r,) + b[2:]
            if variante == "mata":
                return (f["ah"], mt) + b[1:]
            if variante == "mata_d":
                return b[:2] + (mt,) + b[2:]
            if variante == "tranca":            # tranca segura si tengo menos fichas
                return (tf,) + b
            if variante == "tranca_pts":        # … si mi mano pesa menos de lo esperado
                return (tp,) + b
            if variante == "rmt":               # las tres, por encima de cerrar la mesa
                return (tf, f["ah"], r, mt) + b[1:]
            if variante == "rmt_d":             # tranca primero; repite y mata como desempate
                return (tf,) + b[:2] + (r, mt) + b[2:]
            if variante == "rmt_puro":          # la regla tal cual, sin "cerrar la mesa"
                return (tf, r, mt, f["ah"], f["cob"], f["pts"])
            raise KeyError(variante)
        return max(mv, key=k)
    pol.__name__ = "rmt:" + variante
    return pol


# ─────────────────────── B. EL FAROL DE LA PINZA ───────────────────────

class Lectura:
    """Deduce 'no tiene X' cuando alguien rompe su propia pinza.

    Regla: si j ya expuso N dos veces o más, y juega SOBRE su punta N
    dejándola en otro número (sin doble) mientras la otra punta muestra X≠N,
    se anota que j no tiene X (vacío blando).
    """
    aciertos = Counter()                     # por proceso: 'ok' / 'falla'

    def __init__(self):
        self.st = None
        self.vistas = 0
        self.expo = [Counter(), Counter(), Counter()]
        self.blandos = [set(), set(), set()]
        self.pend = []                        # (j, X, índice de la jugada) para auditar

    def actualizar(self, st):
        if st is not self.st:
            self.__init__()
            self.st = st
        for idx in range(self.vistas, len(st.jugadas)):
            j, t, lado, ai, ad = st.jugadas[idx]
            if ai is not None and ai != ad and not M.es_doble(t):
                tapa, otra = (ai, ad) if lado == 'i' else (ad, ai)
                if self.expo[j][tapa] >= 2 and otra != tapa:
                    if otra not in self.blandos[j]:
                        self.blandos[j].add(otra)
                        self.pend.append((j, otra, idx))
            # actualizar exposiciones de j
            if ai is None:
                for n in {t[0], t[1]}:
                    self.expo[j][n] += 1
            else:
                expone = (t[1] if t[0] == ai else t[0]) if lado == 'i' else (t[1] if t[0] == ad else t[0])
                self.expo[j][expone] += 1
        self.vistas = len(st.jugadas)
        # auditar lecturas: ¿de verdad no tenía X? (ni ahora ni jugó X después)
        for j, X, idx in self.pend:
            despues = any(jj == j and M.tiene(tt, X) for jj, tt, *_ in st.jugadas[idx + 1:])
            tiene = any(M.tiene(x, X) for x in st.manos[j])
            Lectura.aciertos["falla" if (despues or tiene) else "ok"] += 1
        self.pend = []


def hacer_lector():
    lec = Lectura()

    def pol(st, i, mv):
        lec.actualizar(st)
        vac = [st.vacios[j] | lec.blandos[j] for j in range(3)]
        return max(mv, key=lambda m: llave_maestro(base_rasgos(st, i, m, vac)))
    pol.__name__ = "lector"
    return pol


def hacer_faroleador(modo="siempre"):
    """Rompe su propia pinza teniendo el número de la otra punta."""
    def pol(st, i, mv):
        mejor = max(mv, key=lambda m: llave_maestro(base_rasgos(st, i, m)))
        if st.izq is None or st.izq == st.der or not st.expuso[i]:
            return mejor
        if modo == "120" and st.marcador[i] < 120:
            return mejor
        cuenta = Counter(st.expuso[i])
        for lado, tapa, otra in (('i', st.izq, st.der), ('d', st.der, st.izq)):
            if cuenta[tapa] < 2:
                continue
            tengo_otra = any(M.tiene(x, otra) for x in st.manos[i])
            if not tengo_otra:
                continue                       # romper sin tener X no es farol, es verdad
            rompen = [m for m in mv if m[1] == lado and not M.es_doble(m[0])]
            if not rompen:
                continue
            fr = max(rompen, key=lambda m: llave_maestro(base_rasgos(st, i, m)))
            if modo == "barato":
                a = base_rasgos(st, i, fr)
                b = base_rasgos(st, i, mejor)
                if a["ah"] < b["ah"]:
                    continue                   # no pago un cobro por el farol
            return fr
        return mejor
    pol.__name__ = "farol:" + modo
    return pol


# ─────────────────── C. ¿QUÉ PASA DESPUÉS DE REPETIR? ───────────────────

def _trabajo_repetir(args):
    politica_yo, n, semilla = args
    random.seed(semilla)
    yo = _pol(politica_yo)
    riv = politica("maestro")
    filas = []
    hay_tranca = decisiones = 0
    for _ in range(n):
        marc = [random.choice((0, 30, 60, 90)) for _ in range(3)]
        pols = [yo, riv, riv]
        h = M.Mano(marc, random.randrange(3), pols)
        pend = None
        for _paso in range(250):
            i = h.turno
            mv = h.legales(i)
            if i == 0 and mv and h.izq is not None:
                decisiones += 1
                if any(rasgos_rmt(h, 0, m, base_rasgos(h, 0, m))[2] != 0 for m in mv):
                    hay_tranca += 1
            if mv:
                m = pols[i](h, i, mv)
                if i == 0 and h.izq is not None:
                    t, lado = m
                    ni, nd = h.extremos_tras(t, lado)
                    e = ni if lado == 'i' else nd
                    repite = bool(h.expuso[0]) and e == h.expuso[0][-1]
                    resto = h.manos[0] - {t}
                    tengo = any(M.tiene(x, e) for x in resto)
                    # ¿el tercero (asiento 2) guarda la última de esa cara?
                    fuera = [x for x in M.FICHAS if x not in h.mesa and x != t and M.tiene(x, e)]
                    ultima_3o = bool(fuera) and all(x in h.manos[2] or x in resto or x in h.pila for x in fuera) \
                        and any(x in h.manos[2] for x in fuera)
                    pend = dict(repite=repite, tengo=tengo, ultima_3o=ultima_3o,
                                antes=h.marcador[0], obs=[], cobro=0)
                elif pend is not None and i != 0:
                    pend["obs"].append(0)          # jugó
                r = h.jugar(i, *m)
            else:
                if pend is not None and i != 0:
                    pend["obs"].append(1)          # pasó
                r = h.no_va(i)
            if pend is not None and (len(pend["obs"]) >= 2 or r or h.turno == 0):
                pend["cobro"] = int(h.marcador[0] > pend["antes"])
                filas.append(pend)
                pend = None
            if r:
                break
    return filas, hay_tranca, decisiones


def repetir(manos):
    print("C · ¿QUÉ PASA DESPUÉS DE REPETIR LA CARA?  (yo = asiento 0; el siguiente = asiento 1; el tercero = asiento 2)\n")
    procesos = os.cpu_count()
    for pol in ("maestro", "rmt:repite"):
        with Pool(procesos) as p:
            partes = p.map(_trabajo_repetir, [(pol, manos // procesos, 500 + k) for k in range(procesos)])
        F = [f for q in partes for f in q[0]]
        ht = sum(q[1] for q in partes)
        dec = sum(q[2] for q in partes)
        print(f"  Yo juego '{pol}'  ·  {len(F)} jugadas en la mano  ·  tranca segura disponible en {100*ht/dec:.2f}% de mis turnos")
        print(f"    {'tipo de jugada':<46}{'%':>6}{'pasa el sig.':>14}{'pasa el 3º':>12}{'cobro':>8}{'sig. pasa y el 3º salva':>25}")

        def g(nombre, sel):
            if len(sel) < 100:
                return
            sig = [f for f in sel if f["obs"]]
            p1 = 100 * sum(f["obs"][0] for f in sig) / len(sig)
            ter = [f for f in sel if len(f["obs"]) >= 2]
            p2 = 100 * sum(f["obs"][1] for f in ter) / max(1, len(ter))
            cob = 100 * sum(f["cobro"] for f in sel) / len(sel)
            salva = [f for f in ter if f["obs"][0] == 1]
            ps = 100 * sum(1 - f["obs"][1] for f in salva) / max(1, len(salva))
            print(f"    {nombre:<46}{100*len(sel)/len(F):>5.1f}%{p1:>13.1f}%{p2:>11.1f}%{cob:>7.1f}%{ps:>24.1f}%")
        g("no repito", [f for f in F if not f["repite"]])
        g("repito y aún tengo esa cara", [f for f in F if f["repite"] and f["tengo"]])
        g("repito y YA NO tengo esa cara", [f for f in F if f["repite"] and not f["tengo"]])
        g("  … y el tercero guarda la última", [f for f in F if f["repite"] and not f["tengo"] and f["ultima_3o"]])
        g("  … y el tercero no la tiene", [f for f in F if f["repite"] and not f["tengo"] and not f["ultima_3o"]])
        print()


# ─────────────────────────────── torneos ───────────────────────────────

def _pol(nombre):
    if nombre.startswith("rmt:"):
        return hacer_rmt(nombre[4:])
    if nombre == "lector":
        return hacer_lector()
    if nombre.startswith("farol:"):
        return hacer_faroleador(nombre[6:])
    return politica(nombre)


def _trabajo(args):
    nombre, rival, k0, n, semilla = args
    random.seed(semilla)
    Lectura.aciertos.clear()
    perd = 0
    for k in range(k0, k0 + n):
        rot = k % 3
        # políticas nuevas por ronda: el Lector guarda estado por mano
        pols = [_pol(nombre) if j == rot else _pol(rival) for j in range(3)]
        p, _ = M.jugar_ronda(pols)
        perd += p == rot
    return perd, dict(Lectura.aciertos)


def torneo(nombre, rival, rondas):
    procesos = os.cpu_count()
    trozo = -(-rondas // procesos)
    trozo += (-trozo) % 3
    tareas = [(nombre, rival, k, min(trozo, rondas - k), 31 + k) for k in range(0, rondas, trozo)]
    with Pool(procesos) as p:
        r = p.map(_trabajo, tareas)
    lect = Counter()
    for _, d in r:
        lect.update(d)
    return sum(x[0] for x in r), rondas, lect


def rmt(rondas):
    print("A · REPITE, MATA Y TRANCA — cada variante contra dos Maestros · neutro 33,3%\n")
    for v in ("maestro", "repite", "repite_d", "mata", "mata_d", "tranca", "tranca_pts",
              "rmt", "rmt_d", "rmt_puro"):
        k, n, _ = torneo(f"rmt:{v}", "maestro", rondas)
        print(f"  {v:<12} {fmt(k, n)}")
    print("\n  La regla tal cual, contra dos Jugadores (nivel 3):")
    for v in ("maestro", "rmt_puro", "rmt_d"):
        k, n, _ = torneo(f"rmt:{v}", "jugador", rondas)
        print(f"  {v:<12} {fmt(k, n)}")


def farol(rondas):
    print("B · EL FAROL DE LA PINZA ROTA · neutro 33,3%\n")
    casos = [
        ("¿Leer las pinzas sirve?", "lector", "maestro"),
        ("Maestro contra dos Lectores", "maestro", "lector"),
        ("Faroleador (siempre) contra dos Lectores", "farol:siempre", "lector"),
        ("Faroleador (barato) contra dos Lectores", "farol:barato", "lector"),
        ("Faroleador (solo en 120+) contra dos Lectores", "farol:120", "lector"),
        ("Faroleador (siempre) contra dos Maestros", "farol:siempre", "maestro"),
        ("Faroleador (barato) contra dos Maestros", "farol:barato", "maestro"),
    ]
    for titulo, a, b in casos:
        k, n, lect = torneo(a, b, rondas)
        tot = lect["ok"] + lect["falla"]
        extra = f"   lecturas acertadas {fmt(lect['ok'], tot)} (n={tot})" if tot else ""
        print(f"  {titulo:<48} {fmt(k, n)}{extra}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "rmt"
    rondas = int(sys.argv[sys.argv.index("--rondas") + 1]) if "--rondas" in sys.argv else 12000
    t0 = time.time()
    if cmd == "repetir":
        repetir(int(sys.argv[sys.argv.index("--manos") + 1]) if "--manos" in sys.argv else 60000)
    else:
        {"rmt": rmt, "farol": farol}[cmd](rondas)
    print(f"\n({time.time() - t0:.0f} s)")
