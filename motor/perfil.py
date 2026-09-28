"""
PERFIL DE PINTINTÍN — cuánto se anota por mano y cuándo se pierde la ronda
===========================================================================

Juega rondas completas instrumentadas y responde dos preguntas:

  1. ¿Cuántos puntos anota cada jugador por mano, y de dónde salen?
  2. ¿En qué situaciones es más probable quedar tercero (perder la ronda)?

Uso:
    python3 motor/perfil.py                      # mesa de tres Maestros
    python3 motor/perfil.py --mesa mixta         # Novato, Jugador y Maestro
    python3 motor/perfil.py --rondas 30000 --ejemplo
"""

import os
import random
import sys
import time
from collections import defaultdict
from itertools import permutations
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motor_pintintin as M  # noqa: E402
from laboratorio import fmt, politica  # noqa: E402

MESAS = {
    "maestros": ("maestro", "maestro", "maestro"),
    "jugadores": ("jugador", "jugador", "jugador"),
    "mixta": ("novato", "jugador", "maestro"),
}


def rasgos_mano(mano):
    _, largo = M.palo_largo(mano)
    return dict(
        dobles=sum(1 for t in mano if M.es_doble(t)),
        largo=largo,
        caras=M.caras_distintas(mano),
        pips=sum(M.PUNTOS[t] for t in mano),
        frag=sum(1 for t in mano if t[0] in (0, 1) or t[1] in (0, 1)),
    )


def jugar_instrumentada(nombres, rid):
    """Una ronda completa. Devuelve (filas_por_mano, fila_de_ronda)."""
    pols = [politica(n) for n in nombres]
    marcador, ganador, primera = [0, 0, 0], None, True
    filas, trayectoria = [], []
    for m in range(40):
        if max(marcador) >= M.META:
            break
        antes = marcador[:]
        h = M.Mano(marcador, ganador if ganador is not None else 0, pols, primera_oficial=primera)
        dadas = [set(x) for x in h.manos]
        res, w = h.correr()
        salidor = int(h.log[0].split()[0][1:]) - 1
        for j in range(3):
            o = [x for x in range(3) if x != j]
            filas.append(dict(
                rid=rid, mano=m + 1, j=j, pol=nombres[j],
                rel=(j - salidor) % 3,               # 0 sale · 1 a su derecha · 2 el tercero
                primera=primera, antes=antes[j],
                rango=sum(1 for x in o if antes[x] > antes[j]),
                congelado=antes[j] >= 120,
                pases=h.ingreso[j][0], cierre=h.ingreso[j][1],
                total=h.marcador[j] - antes[j],
                gana=int(w == j), tipo=res,
                novas=sum(1 for l in h.log if l == f"J{j+1} no va"),
                cedido=sum(h.ingreso[x][0] for x in o),
                **rasgos_mano(dadas[j]),
            ))
        marcador, ganador, primera = h.marcador, w, False
        trayectoria.append(marcador[:])
    bajo = min(marcador)
    abajo = [j for j in range(3) if marcador[j] == bajo]
    subita = len(abajo) > 1
    if not subita:
        perdedor = abajo[0]
    else:
        duo = abajo[:2]
        h = M.Mano(marcador, duo[0], pols, modo="subita", duo=duo)
        M.salida_subita(h, duo)
        _, salvado = h.correr()
        perdedor = duo[1] if salvado == duo[0] else duo[0]
    for f in filas:
        f["pierde"] = int(f["j"] == perdedor)
    return filas, dict(rid=rid, perdedor=perdedor, final=marcador, tray=trayectoria,
                       subita=subita, pols=nombres)


def _trabajo(args):
    mesa, k0, n, semilla = args
    random.seed(semilla)
    base = MESAS[mesa]
    perms = list(permutations(base)) if len(set(base)) > 1 else [base]
    F, R = [], []
    for k in range(k0, k0 + n):
        f, r = jugar_instrumentada(list(perms[k % len(perms)]), k)
        F += f
        R.append(r)
    return F, R


def correr(mesa, rondas, procesos=None):
    procesos = procesos or os.cpu_count()
    trozo = -(-rondas // procesos)
    tareas = [(mesa, k, min(trozo, rondas - k), 4242 + k) for k in range(0, rondas, trozo)]
    with Pool(procesos) as p:
        partes = p.map(_trabajo, tareas)
    F = [f for q in partes for f in q[0]]
    R = [r for q in partes for r in q[1]]
    return F, R


# ─────────────────────────────── INFORME ───────────────────────────────

def media(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def mediana(xs):
    s = sorted(xs)
    return s[len(s) // 2] if s else float("nan")


def tabla_puntos(F, titulo, clave, orden=None, minimo=200):
    g = defaultdict(list)
    for f in F:
        g[clave(f)].append(f)
    print(f"\n  {titulo}")
    print(f"    {'':<22}{'n':>8}{'media':>8}{'pases':>8}{'cierre':>8}{'gana mano':>11}{'anota 0':>9}{'pierde ronda':>14}")
    for c in (orden or sorted(g, key=str)):
        xs = g.get(c, [])
        if len(xs) < minimo:
            continue
        print(f"    {str(c):<22}{len(xs):>8}{media([x['total'] for x in xs]):>8.1f}"
              f"{media([x['pases'] for x in xs]):>8.1f}{media([x['cierre'] for x in xs]):>8.1f}"
              f"{100 * media([x['gana'] for x in xs]):>10.1f}%{100 * media([x['total'] == 0 for x in xs]):>8.1f}%"
              f"{100 * media([x['pierde'] for x in xs]):>13.1f}%")


def informe_puntos(F, R):
    print("═" * 92)
    print(" 1 · PUNTOS POR MANO")
    print("═" * 92)
    tot = [f["total"] for f in F]
    print(f"\n  {len(F) // 3} manos · {len(R)} rondas · {len(F) // 3 / len(R):.2f} manos por ronda")
    print(f"  Media por jugador y mano: {media(tot):.1f} pts  (mediana {mediana(tot)} · "
          f"anota 0 el {100 * media([t == 0 for t in tot]):.1f}% de las manos)")
    print(f"    de pases (incluye capicúa): {media([f['pases'] for f in F]):.1f} · "
          f"de cierre (dominada/tranca): {media([f['cierre'] for f in F]):.1f}")
    print(f"  Una mano reparte en total {3 * media(tot):.1f} pts entre los tres")
    tipos = defaultdict(int)
    for f in F:
        if f["j"] == 0:
            tipos[f["tipo"]] += 1
    n = sum(tipos.values())
    print(f"  Cierres: dominada {100 * tipos['dom'] / n:.1f}% · tranca {100 * tipos['tra'] / n:.1f}%")

    cuantiles = sorted(tot)
    q = lambda p: cuantiles[int(p * (len(cuantiles) - 1))]  # noqa: E731
    print(f"  Reparto de lo anotado por mano: p25 {q(.25)} · p50 {q(.5)} · p75 {q(.75)} · p90 {q(.9)} · p99 {q(.99)}")

    tabla_puntos(F, "Por asiento respecto a quien sale", lambda f: ("sale", "a su derecha", "el tercero")[f["rel"]],
                 ["sale", "a su derecha", "el tercero"])
    tabla_puntos(F, "Primera jugada oficial vs manos siguientes",
                 lambda f: ("1ª oficial · " if f["primera"] else "siguientes · ") + ("sale", "derecha", "tercero")[f["rel"]],
                 [a + b for a in ("1ª oficial · ", "siguientes · ") for b in ("sale", "derecha", "tercero")])
    tabla_puntos(F, "Por política", lambda f: f["pol"])
    tabla_puntos(F, "Por dobles repartidos", lambda f: f["dobles"], [0, 1, 2, 3, 4])
    tabla_puntos(F, "Por palo más largo", lambda f: f["largo"], [2, 3, 4, 5, 6])
    tabla_puntos(F, "Por caras distintas", lambda f: f["caras"], [4, 5, 6, 7])
    tabla_puntos(F, "Por puntos repartidos en la mano",
                 lambda f: ("≤35", "36-45", "46-55", "≥56")[(f["pips"] > 35) + (f["pips"] > 45) + (f["pips"] > 55)],
                 ["≤35", "36-45", "46-55", "≥56"])
    tabla_puntos(F, "Por posición en el marcador al empezar la mano (desde la 2ª)",
                 lambda f: None if f["mano"] == 1 else
                 ("congelado 120+" if f["congelado"] else ("primero", "segundo", "tercero")[f["rango"]]),
                 ["primero", "segundo", "tercero", "congelado 120+"])


def riesgo(nombre, filas, total_base):
    if len(filas) < 150:
        return None
    k = sum(f["pierde"] for f in filas)
    return (100 * k / len(filas), nombre, fmt(k, len(filas)), len(filas))


def informe_riesgo(F, R):
    print("\n" + "═" * 92)
    print(" 2 · CUÁNDO SE PIERDE LA RONDA   (neutro 33,3%)")
    print("═" * 92)
    por_r = {r["rid"]: r for r in R}
    # vista por jugador y ronda
    J = []
    for r in R:
        for j in range(3):
            tray = [t[j] for t in r["tray"]]
            otros = [[t[x] for x in range(3) if x != j] for t in r["tray"]]
            J.append(dict(rid=r["rid"], j=j, pol=r["pols"][j], pierde=int(r["perdedor"] == j),
                          tray=tray, otros=otros, final=r["final"][j], subita=r["subita"]))
    F1 = {(f["rid"], f["j"]): f for f in F if f["mano"] == 1}
    Fm = defaultdict(list)
    for f in F:
        Fm[(f["rid"], f["j"])].append(f)

    filas = []

    def add(nombre, sel):
        x = riesgo(nombre, sel, None)
        if x:
            filas.append(x)

    # posición tras la mano k y distancia al de arriba
    for k in (1, 2, 3, 4):
        for pos, nom in ((0, "primero"), (1, "segundo"), (2, "último")):
            sel = []
            for p in J:
                if len(p["tray"]) < k or max(p["tray"][k - 1], *p["otros"][k - 1]) >= 150:
                    continue
                yo, ot = p["tray"][k - 1], p["otros"][k - 1]
                rango = sum(1 for x in ot if x > yo)
                empate = any(x == yo for x in ot)
                if rango == pos and not empate:
                    sel.append(p)
            add(f"{nom} tras la mano {k}", sel)
    for k in (1, 3):
        for lo, hi in ((1, 20), (21, 40), (41, 60), (61, 90), (91, 150)):
            sel = []
            for p in J:
                if len(p["tray"]) < k or max(p["tray"][k - 1], *p["otros"][k - 1]) >= 150:
                    continue
                yo, ot = p["tray"][k - 1], p["otros"][k - 1]
                if all(x > yo for x in ot) and lo <= min(ot) - yo <= hi:
                    sel.append(p)
            add(f"último tras la mano {k}, a {lo}-{hi} del segundo", sel)
    # la primera mano
    add("anota 0 en la 1ª mano", [p for p in J if F1[(p["rid"], p["j"])]["total"] == 0])
    add("anota 0 en las dos primeras manos",
        [p for p in J if len(Fm[(p["rid"], p["j"])]) >= 2 and all(f["total"] == 0 for f in Fm[(p["rid"], p["j"])][:2])])
    add("gana la 1ª mano", [p for p in J if F1[(p["rid"], p["j"])]["gana"]])
    for rel, nom in ((0, "sale en la 1ª (tiene el doble más alto)"), (1, "juega justo después del que sale"),
                     (2, "es el tercero en jugar la 1ª")):
        add(nom, [p for p in J if F1[(p["rid"], p["j"])]["rel"] == rel])
    for d in (0, 1, 2, 3, 4):
        add(f"{d} dobles en la 1ª mano", [p for p in J if F1[(p["rid"], p["j"])]["dobles"] == d])
    for lg in (2, 3, 4, 5):
        add(f"palo largo de {lg} en la 1ª mano", [p for p in J if F1[(p["rid"], p["j"])]["largo"] == lg])
    add("cede 60+ pts de pases en la 1ª mano", [p for p in J if F1[(p["rid"], p["j"])]["cedido"] >= 60])
    add("pasa 3+ veces en la 1ª mano", [p for p in J if F1[(p["rid"], p["j"])]["novas"] >= 3])
    # a lo largo de la ronda
    add("nunca gana una mano en la ronda", [p for p in J if not any(f["gana"] for f in Fm[(p["rid"], p["j"])])])
    add("congelado en 120+ sin cerrar la ronda",
        [p for p in J if any(t >= 120 for t in p["tray"]) and p["final"] < 150])
    add("va a 120+ mientras otro ya está en 120+",
        [p for p in J if any(t >= 120 for t in p["tray"])
         and any(max(o) >= 120 and t < 120 for t, o in zip(p["tray"], p["otros"]))])
    add("otro cruza 120 y yo estoy por debajo de 60",
        [p for p in J if next((t for t, o in zip(p["tray"], p["otros"]) if max(o) >= 120 and t < 120), 999) < 60])
    add("otro cruza 120 y yo estoy entre 60 y 119",
        [p for p in J if 60 <= next((t for t, o in zip(p["tray"], p["otros"]) if max(o) >= 120 and t < 120), -1) < 120])
    add("va a muerte súbita", [p for p in J if p["subita"] and p["final"] == min(por_r[p["rid"]]["final"])])
    for pol in sorted({p["pol"] for p in J}):
        add(f"política {pol}", [p for p in J if p["pol"] == pol])

    filas.sort(reverse=True)
    print(f"\n  {'situación':<52}{'pierde la ronda':>28}{'n':>9}")
    for pct, nom, s, n in filas:
        print(f"  {nom:<52}{s:>28}{n:>9}")


def ejemplo(mesa):
    random.seed(99)
    nombres = list(MESAS[mesa])
    F, r = jugar_instrumentada(nombres, 0)
    print("\nEJEMPLO DE RONDA · " + " · ".join(f"J{j+1} {n}" for j, n in enumerate(nombres)))
    for m in range(1, len(r["tray"]) + 1):
        fm = [f for f in F if f["mano"] == m]
        sale = next(f["j"] for f in fm if f["rel"] == 0)
        det = " | ".join(f"J{f['j']+1} +{f['total']:>3} ({f['pases']} pases, {f['cierre']} cierre)" for f in fm)
        g = next(f for f in fm if f["gana"])
        print(f"  mano {m} · sale J{sale+1} · {'domina' if g['tipo']=='dom' else 'tranca'} J{g['j']+1}"
              f" · {det} · marcador {r['tray'][m-1]}")
    print(f"  → pierde J{r['perdedor']+1}{' (muerte súbita)' if r['subita'] else ''}")


if __name__ == "__main__":
    mesa = sys.argv[sys.argv.index("--mesa") + 1] if "--mesa" in sys.argv else "maestros"
    rondas = int(sys.argv[sys.argv.index("--rondas") + 1]) if "--rondas" in sys.argv else 20000
    t0 = time.time()
    print(f"PERFIL · mesa '{mesa}' {MESAS[mesa]} · {rondas} rondas · asientos rotados\n")
    if "--ejemplo" in sys.argv:
        ejemplo(mesa)
    F, R = correr(mesa, rondas)
    informe_puntos(F, R)
    informe_riesgo(F, R)
    print(f"\n({time.time() - t0:.0f} s)")
