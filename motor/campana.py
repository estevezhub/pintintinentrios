"""
CAMPAÑA — búsqueda y juicio masivo de estrategias
==================================================

Cuatro enfoques, todos contra la misma vara (dos Maestros, neutro 33,3%):

  tribunal   Cada afirmación de los documentos y de la mesa, codificada como
             variante del Maestro y juzgada con muchas rondas.
  cem        Búsqueda evolutiva (entropía cruzada) sobre ~30 rasgos de jugada
             y de marcador: encuentra combinaciones que nadie propuso.
  imitar     Graba decisiones del Sabio y ajusta un modelo de elección
             (logit condicional): qué valora quien mira hacia adelante.
  liga       Todas contra todas en mesas mezcladas; fuerza de cada una por
             máxima verosimilitud (modelo de "quién queda último").

    python3 motor/campana.py tribunal --rondas 18000
    python3 motor/campana.py cem --gen 14 --pob 16 --rondas 4000
    python3 motor/campana.py imitar --rondas 1200
    python3 motor/campana.py liga --rondas 36000
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
import laboratorio as L  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(AQUI, "..", "analisis", "datos")
PROCESOS = os.cpu_count()


# ═════════════════════════════ RASGOS ═════════════════════════════

def contexto(st, i):
    s = st.marcador
    o = L.rivales(i)
    sig, ter = (i + 1) % 3, (i + 2) % 3
    bajo = min(s)
    abajo = [j for j in range(3) if s[j] == bajo]
    ult = abajo[0] if (len(abajo) == 1 and abajo[0] != i) else None
    lid = max(o, key=lambda j: s[j])
    N, largo = M.palo_largo(st.manos[i])
    su = st.sin_ubicar(i)
    muertos = {n for n in range(7) if not any(M.tiene(x, n) for x in M.FICHAS if x not in st.mesa)}
    ult_expuesto = {j: (st.expuso[j][-1] if st.expuso[j] else None) for j in o}
    # ¿racha de otro? el que jugó último es un rival y el otro rival ya falló alguna punta
    racha = None
    if st.izq is not None and st.ultimo is not None and st.ultimo != i:
        k = o[0] if st.ultimo == o[1] else o[1]
        racha = k
    return dict(
        o=o, sig=sig, ter=ter, ult=ult, lid=lid, N=N, largo=largo, su=su,
        sueltas={x for x in su if M.tiene(x, N)} if largo >= 4 else set(),
        muertos=muertos, ult_exp=ult_expuesto, racha=racha,
        frozen=int(s[i] >= 120), soy_ult=int(len(abajo) == 1 and abajo[0] == i),
        bola=int(st.izq is not None and st.ultimo == i),
        salida=int(st.izq is None),
    )


def _ahj(v, ni, nd):
    return 2 if (ni in v and nd in v) else (1 if (ni in v or nd in v) else 0)


def rasgos(st, i, m, c):
    t, lado = m
    ni, nd = st.extremos_tras(t, lado)
    vac = st.vacios
    o = c["o"]
    f = {}
    ahs = {j: _ahj(vac[j], ni, nd) for j in o}
    f["ah"] = ahs[o[0]] + ahs[o[1]]
    # una punta está viva si queda alguna ficha de ese número fuera de la mesa (sin contar t)
    vivas_n = [n for n in {ni, nd}
               if any(M.tiene(x, n) for x in M.FICHAS if x not in st.mesa and x != t)]
    f["vivas"] = len(vivas_n)
    f["cobro2"] = int(bool(vivas_n) and all(all(n in vac[j] for n in vivas_n) for j in o))
    sirven = [x for x in c["su"] if M.tiene(x, ni) or M.tiene(x, nd)]
    f["amen"] = len(sirven)
    f["amen_sig"] = sum(1 for x in sirven if x[0] not in vac[c["sig"]] and x[1] not in vac[c["sig"]])
    f["amen_ter"] = sum(1 for x in sirven if x[0] not in vac[c["ter"]] and x[1] not in vac[c["ter"]])
    resto = st.manos[i] - {t}
    f["cob"] = sum(1 for x in resto if M.tiene(x, ni) or M.tiene(x, nd))
    f["respondo"] = int(f["cob"] > 0)
    pierde = 0
    if st.izq is not None:
        for n in {st.izq, st.der}:
            if any(M.tiene(x, n) for x in st.manos[i]) and not any(M.tiene(x, n) for x in resto):
                pierde += 1
    f["pierde"] = pierde
    f["caras"] = len({n for x in resto for n in x})
    f["pts"] = M.PUNTOS[t]
    f["doble"] = int(M.es_doble(t))
    f["doble_N"] = int(M.es_doble(t) and t[0] == c["N"] and c["largo"] >= 4)
    f["dobles_rest"] = sum(1 for x in resto if M.es_doble(x))
    f["peso_mano"] = sum(M.PUNTOS[x] for x in resto)
    N, largo = c["N"], c["largo"]
    f["cerco"] = ((ni == N) + (nd == N)) if largo >= 4 else 0
    f["cebo"] = sum(1 for q in (ni, nd) if largo >= 4 and q != N and (min(q, N), max(q, N)) in c["sueltas"])
    f["una_cara"] = int(len(vivas_n) == 1)
    f["muertas"] = sum(1 for n in {ni, nd} if n not in vivas_n)
    f["frag"] = sum(1 for n in (ni, nd) if n in (0, 1))
    f["ah_sig"] = ahs[c["sig"]]
    f["ah_ter"] = ahs[c["ter"]]
    f["ah_ult"] = ahs[c["ult"]] if c["ult"] is not None else 0
    f["ah_lid"] = ahs[c["lid"]]
    f["ah_aliado"] = ahs[[j for j in o if j != c["ult"]][0]] if c["ult"] is not None else 0
    # exposición: repite / mata
    if st.izq is None:
        f["repite"] = f["mata"] = f["sostener"] = f["romper"] = 0
        f["tranca"] = 0
    else:
        expone = ni if lado == 'i' else nd
        tapa = st.izq if lado == 'i' else st.der
        f["repite"] = int(bool(st.expuso[i]) and expone == st.expuso[i][-1])
        f["mata"] = int(expone != tapa and any(c["ult_exp"][j] == tapa for j in o))
        f["sostener"] = int({ni, nd} == {st.izq, st.der})
        k = c["racha"]
        f["romper"] = int(k is not None and tapa in vac[k] and expone != tapa)
        nadie = all(all(x[0] in vac[j] or x[1] in vac[j] for j in o) for x in sirven)
        yo_no = f["cob"] == 0
        if nadie and yo_no:
            mias = len(resto)
            otras = min(len(st.manos[j]) for j in o)
            f["tranca"] = 1 if mias < otras else (-1 if mias > otras else 0)
        else:
            f["tranca"] = 0
    return f


MAESTRO = ("ah", "-amen", "cerco", "cebo", "cob", "pts")


def llave(f, campos):
    return tuple(-f[c[1:]] if c[0] == "-" else f[c] for c in campos)


# ═════════════════════════ POLÍTICAS POR ESPECIFICACIÓN ═════════════════════════
# Una especificación es un dict:
#   {"lex": [campos]}                         orden lexicográfico
#   {"lex": [...], "si": "frozen", "sino": [...]}   cambia de orden según el contexto
#   {"lin": {rasgo: peso, "rasgo*ctx": peso}} suma ponderada
#   {"salida": "comp" | "comp1"}              regla aparte para la salida libre

def hacer(spec):
    def elegir_salida(st, i, mv, modo):
        mano = st.manos[i]
        dobles = [t for t in mano if M.es_doble(t)]
        comp = {d: sum(1 for x in mano if x != d and M.tiene(x, d[0])) for d in dobles}
        if modo == "comp" and dobles:
            d = max(dobles, key=lambda d: (comp[d], d[0]))
            return (d, 'd')
        if modo == "comp1":
            buenos = [d for d in dobles if comp[d] >= 1]
            if buenos:
                d = max(buenos, key=lambda d: (comp[d], d[0]))
                return (d, 'd')
            sin_doble = [m for m in mv if not M.es_doble(m[0])]
            if sin_doble:
                return None, sin_doble
        return None

    def pol(st, i, mv):
        c = contexto(st, i)
        opciones = mv
        if c["salida"] and "salida" in spec:
            r = elegir_salida(st, i, mv, spec["salida"])
            if r is not None:
                if r[0] is not None:
                    return r
                opciones = r[1]
        if "lin" in spec:
            w = spec["lin"]

            def v(m):
                f = rasgos(st, i, m, c)
                tot = 0.0
                for k, p in w.items():
                    if "*" in k:
                        a, b = k.split("*")
                        tot += p * f[a] * c[b]
                    else:
                        tot += p * f[k]
                return (tot, f["pts"])
            return max(opciones, key=v)
        campos = spec["lex"]
        if "si" in spec and c[spec["si"]]:
            campos = spec["sino"]
        return max(opciones, key=lambda m: llave(rasgos(st, i, m, c), campos))
    return pol


def P(*campos, si=None, sino=None, salida=None):
    d = {"lex": list(campos)}
    if si:
        d["si"], d["sino"] = si, list(sino)
    if salida:
        d["salida"] = salida
    return d


# ═════════════════════════════ EL TRIBUNAL ═════════════════════════════
# (nombre, fuente, afirmación, especificación)

M_ = list(MAESTRO)
HIPOTESIS = [
    ("control: Maestro", "—", "La vara", P(*M_)),
    ("Maestro en 3 términos", "auditoría §4.1", "cobra → cierra → peso basta", P("ah", "-amen", "pts")),
    ("sin 'cerrar la mesa'", "God Mode 3.3", "cerrar la mesa es el corazón", P("ah", "cerco", "cebo", "cob", "pts")),
    ("cobro cierto primero", "God Mode 3.3", "si puedes cobrar seguro, hazlo", P("cobro2", *M_)),
    ("guardar las bajas", "God Mode 3.1", "el peor error del juego", P("ah", "-pts", "-amen", "cerco", "cebo", "cob")),
    ("soltar las altas primero", "God Mode 3.1", "−6,9 contra el azar", P("ah", "pts", "-amen", "cerco", "cebo", "cob")),
    ("peso antes que ahogo", "Reglamento §9.1", "ahogar palos vale más que descargar altas", P("pts", "ah", "-amen", "cerco", "cebo", "cob")),
    ("mano ancha (prioridad)", "Estrategia §12", "no destruir la anchura", P("ah", "caras", "-amen", "cerco", "cebo", "cob", "pts")),
    ("mano ancha (desempate)", "Estrategia §12", "", P("ah", "-amen", "caras", "cerco", "cebo", "cob", "pts")),
    ("guardar el veto (prioridad)", "Estrategia §6e", "tu última de una cara es un veto", P("ah", "-pierde", "-amen", "cerco", "cebo", "cob", "pts")),
    ("guardar el veto (desempate)", "Estrategia §6e", "", P("ah", "-amen", "-pierde", "cerco", "cebo", "cob", "pts")),
    ("siempre poder responder", "Estrategia §12", "no quedarte sin respuesta", P("ah", "respondo", "-amen", "cerco", "cebo", "cob", "pts")),
    ("soltar dobles (prioridad)", "God Mode 2.3", "los dobles son lastre", P("ah", "doble", "-amen", "cerco", "cebo", "cob", "pts")),
    ("soltar dobles (desempate)", "God Mode 2.3", "", P("ah", "-amen", "doble", "cerco", "cebo", "cob", "pts")),
    ("soltar dobles salvo el del cerco", "God Mode 4.4", "el doble del cerco es un arma", P("ah", "-doble_N", "doble", "-amen", "cerco", "cebo", "cob", "pts")),
    ("dos caras vivas mientras cobras", "Reglamento §9.2", "un palo muerto parte el cobro", P("ah", "vivas", "-amen", "cerco", "cebo", "cob", "pts")),
    ("estrangular a una cara", "Estrategia §6", "una cara viva es la vía práctica", P("ah", "una_cara", "-amen", "cerco", "cebo", "cob", "pts")),
    ("matar palos (dejar puntas muertas)", "Reglamento §9.3", "matar un lado para ahogar", P("ah", "muertas", "-amen", "cerco", "cebo", "cob", "pts")),
    ("no matar palos", "Reglamento §9.3", "matar abarata tus pases", P("ah", "-muertas", "-amen", "cerco", "cebo", "cob", "pts")),
    ("puntas en blanco/uno", "Reglamento §9.3", "los frágiles son cuchillo", P("ah", "frag", "-amen", "cerco", "cebo", "cob", "pts")),
    ("bola de nieve: no muevas la mesa", "Estrategia §6d", "si cobraste, sostén", P(*M_, si="bola", sino=("ah", "sostener", "-amen", "cerco", "cebo", "cob", "pts"))),
    ("romper la racha del otro", "Estrategia §6d", "rómpelo ya aunque duela", P("ah", "romper", "-amen", "cerco", "cebo", "cob", "pts")),
    ("alianza barata (ahoga al último)", "Estrategia §3", "tu juego primero", P("ah", "-amen", "ah_ult", "cerco", "cebo", "cob", "pts")),
    ("alianza total (ahoga al último)", "Estrategia §3", "ahogar por encima de todo", P("ah_ult", "ah", "-amen", "cerco", "cebo", "cob", "pts")),
    ("objetivo sí, aliado no", "Estrategia §3", "caras que el objetivo falló y el aliado no", P("ah", "-amen", "ah_ult", "-ah_aliado", "cerco", "cebo", "cob", "pts")),
    ("trabaja al de tu derecha", "Estrategia §3b", "es tu instrumento", P("ah", "ah_sig", "-amen", "cerco", "cebo", "cob", "pts")),
    ("trabaja al de tu izquierda", "Estrategia §3b", "contraste", P("ah", "ah_ter", "-amen", "cerco", "cebo", "cob", "pts")),
    ("cierra al de tu derecha", "nueva", "puntas difíciles para el siguiente", P("ah", "-amen_sig", "-amen", "cerco", "cebo", "cob", "pts")),
    ("cierra al de tu izquierda", "nueva", "puntas difíciles para el tercero", P("ah", "-amen_ter", "-amen", "cerco", "cebo", "cob", "pts")),
    ("frena al líder", "Estrategia §2", "el último quiere alargar", P("ah", "ah_lid", "-amen", "cerco", "cebo", "cob", "pts")),
    ("repite la cara (desempate)", "Estrategia §3b / mesa", "repite por defecto", P("ah", "-amen", "repite", "cerco", "cebo", "cob", "pts")),
    ("mata la cara del rival (desempate)", "mesa", "evita que cuadre", P("ah", "-amen", "mata", "cerco", "cebo", "cob", "pts")),
    ("tranca segura con menos fichas", "mesa", "tranca si vas con menos", P("tranca", *M_)),
    ("en 120+: cobertura y peso", "Estrategia §9 / Reglamento §9.5", "desde 120 juega a ganar la mano", P(*M_, si="frozen", sino=("cob", "caras", "pts", "ah", "-amen"))),
    ("en 120+: suelta peso", "Reglamento §9.5", "guarda bajas: suelta altas", P(*M_, si="frozen", sino=("pts", "ah", "-amen", "cob"))),
    ("en 120+: igual que siempre", "auditoría §4.5", "control del anterior", P(*M_, si="frozen", sino=M_)),
    ("yendo último: cerco primero", "auditoría §4.9", "cobrar grande para remontar", P(*M_, si="soy_ult", sino=("ah", "cerco", "cebo", "-amen", "cob", "pts"))),
    ("yendo último: suelta peso", "auditoría §4.9", "apostar a la tranca", P(*M_, si="soy_ult", sino=("ah", "pts", "-amen", "cob"))),
    ("salida: doble con más compañeras", "auditoría §4.4", "sal de doble acompañado", P(*M_, salida="comp")),
    ("salida: doble solo si tiene compañera", "God Mode 12.7", "el doble solo es mala salida", P(*M_, salida="comp1")),
    ("cerco antes que cerrar", "God Mode 12.5", "con palo largo, ataca", P("ah", "cerco", "cebo", "-amen", "cob", "pts")),
    ("cebo antes que cerco", "God Mode 4.2", "el cebo es lo más rentable", P("ah", "-amen", "cebo", "cerco", "cob", "pts")),
    ("aligerar la mano", "nueva", "mano liviana para la tranca", P("ah", "-amen", "-peso_mano", "cob")),
    ("quedarse con menos dobles", "nueva", "", P("ah", "-amen", "-dobles_rest", "cerco", "cebo", "cob", "pts")),
]


def _pol_nombre(nombre):
    """Resuelve nombres de todas las familias de políticas."""
    if nombre.startswith("hip:"):
        return hacer(next(h[3] for h in HIPOTESIS if h[0] == nombre[4:]))
    if nombre.startswith("spec:"):
        return hacer(json.loads(nombre[5:]))
    if nombre.startswith(("rmt:", "farol:", "lector")):
        import tacticas
        return tacticas._pol(nombre)
    return L.politica(nombre)


def _trabajo_torneo(args):
    nombre, rival, k0, n, semilla = args
    random.seed(semilla)
    pol, riv = _pol_nombre(nombre), _pol_nombre(rival)
    perd = 0
    for k in range(k0, k0 + n):
        rot = k % 3
        pols = [pol if j == rot else riv for j in range(3)]
        p, _ = M.jugar_ronda(pols)
        perd += p == rot
    return perd


def tareas_torneo(nombre, rival, rondas, semilla, trozo=None):
    trozo = trozo or max(3, -(-rondas // PROCESOS))
    trozo += (-trozo) % 3
    return [(nombre, rival, k, min(trozo, rondas - k), semilla * 100003 + k) for k in range(0, rondas, trozo)]


def tribunal(rondas):
    """Todas las hipótesis contra dos Maestros, mismas semillas, en un solo Pool."""
    nombres = [f"hip:{h[0]}" for h in HIPOTESIS]
    tareas, idx = [], []
    for q, n in enumerate(nombres):
        t = tareas_torneo(n, "maestro", rondas, 1, trozo=-(-rondas // 24))
        tareas += t
        idx += [q] * len(t)
    t0 = time.time()
    with Pool(PROCESOS) as p:
        res = p.map(_trabajo_torneo, tareas, chunksize=1)
    perd = [0] * len(nombres)
    for q, r in zip(idx, res):
        perd[q] += r
    base = perd[0] / rondas
    filas = []
    for (nom, fuente, afirm, _), k in zip(HIPOTESIS, perd):
        lo, hi = L.wilson(k, rondas)
        d = 100 * (k / rondas - base)
        # diferencia contra el control: error de dos proporciones independientes
        se = 100 * math.sqrt(base * (1 - base) / rondas + (k / rondas) * (1 - k / rondas) / rondas)
        if nom.startswith("control"):
            ver = "—"
        elif d <= -1.96 * se:
            ver = "MEJORA ✔"
        elif d >= 1.96 * se:
            ver = "EMPEORA ✘"
        else:
            ver = "neutra"
        filas.append((d, nom, fuente, afirm, 100 * k / rondas, lo, hi, ver, se))
    filas.sort()
    out = [f"TRIBUNAL · {len(HIPOTESIS)} hipótesis × {rondas} rondas contra dos Maestros · {time.time() - t0:.0f} s\n",
           f"{'Δ':>6}  {'veredicto':<10} {'hipótesis':<38} {'pierde':>24}  fuente"]
    for d, nom, fuente, afirm, pct, lo, hi, ver, se in filas:
        out.append(f"{d:+6.1f}  {ver:<10} {nom:<38} {pct:5.1f}% [{lo:4.1f} – {hi:4.1f}]  {fuente}")
    out.append(f"\n(±{1.96 * filas[0][8]:.1f} puntos = umbral de significancia al 95% para Δ)")
    return "\n".join(out)


# ═════════════════════════════ CEM ═════════════════════════════

RASGOS_CEM = ["ah", "cobro2", "amen", "amen_sig", "amen_ter", "cob", "pierde", "caras", "pts", "doble",
              "doble_N", "cerco", "cebo", "vivas", "muertas", "frag", "repite", "mata", "sostener",
              "romper", "tranca", "ah_sig", "ah_ter", "ah_ult", "ah_lid", "peso_mano",
              "pts*frozen", "cob*frozen", "ah*frozen", "cerco*soy_ult", "pts*soy_ult", "sostener*bola"]
INICIO = {"ah": 10.0, "amen": -1.0, "cerco": 0.5, "cebo": 0.3, "cob": 0.1, "pts": 0.05}


def _eval_pesos(args):
    pesos, k0, n, semilla = args
    random.seed(semilla)
    pol = hacer({"lin": pesos})
    riv = L.politica("maestro")
    perd = 0
    for k in range(k0, k0 + n):
        rot = k % 3
        pols = [pol if j == rot else riv for j in range(3)]
        p, _ = M.jugar_ronda(pols)
        perd += p == rot
    return perd


def cem(generaciones, poblacion, rondas, elite_frac=0.25, semilla=5):
    rng = random.Random(semilla)
    mu = {r: INICIO.get(r, 0.0) for r in RASGOS_CEM}
    sd = {r: (3.0 if r == "ah" else 0.6) for r in RASGOS_CEM}
    historia = []
    mejor_global = None
    trozo = -(-rondas // 6)
    trozo += (-trozo) % 3
    t0 = time.time()
    for g in range(generaciones):
        cands = [dict(mu)] + [{r: mu[r] + sd[r] * rng.gauss(0, 1) for r in RASGOS_CEM} for _ in range(poblacion - 1)]
        tareas, idx = [], []
        for q, w in enumerate(cands):
            for k in range(0, rondas, trozo):
                tareas.append((w, k, min(trozo, rondas - k), 7000 + g * 1000 + k))   # mismas semillas en la generación
                idx.append(q)
        with Pool(PROCESOS) as p:
            res = p.map(_eval_pesos, tareas, chunksize=1)
        perd = [0] * len(cands)
        for q, r in zip(idx, res):
            perd[q] += r
        orden = sorted(range(len(cands)), key=lambda q: perd[q])
        ne = max(2, int(elite_frac * len(cands)))
        elite = [cands[q] for q in orden[:ne]]
        for r in RASGOS_CEM:
            vals = [e[r] for e in elite]
            m = sum(vals) / ne
            v = sum((x - m) ** 2 for x in vals) / ne
            mu[r] = 0.7 * m + 0.3 * mu[r]
            sd[r] = max(0.05, 0.7 * math.sqrt(v) + 0.3 * sd[r])
        linea = (f"gen {g + 1:2d}  media actual {100 * perd[0] / rondas:5.1f}%  mejor {100 * perd[orden[0]] / rondas:5.1f}%"
                 f"  peor {100 * perd[orden[-1]] / rondas:5.1f}%  ({time.time() - t0:.0f} s)")
        print(linea, flush=True)
        historia.append(dict(gen=g + 1, media=perd[0] / rondas, mejor=perd[orden[0]] / rondas, mu=dict(mu), sd=dict(sd)))
        if mejor_global is None or perd[orden[0]] < mejor_global[0]:
            mejor_global = (perd[orden[0]], cands[orden[0]])
        with open(os.path.join(DATOS, "cem_historia.json"), "w") as f:
            json.dump(dict(historia=historia, mu=mu, sd=sd, mejor=mejor_global[1]), f, indent=1)
    return mu, mejor_global[1]


# ═════════════════════════════ IMITAR AL SABIO ═════════════════════════════

RASGOS_IMIT = [r for r in RASGOS_CEM]


def _vec(f, c):
    out = []
    for k in RASGOS_IMIT:
        if "*" in k:
            a, b = k.split("*")
            out.append(float(f[a] * c[b]))
        else:
            out.append(float(f[k]))
    return out


def _trabajo_imitar(args):
    n, semilla, muestras = args
    random.seed(semilla)
    sab = L.hacer_sabio(muestras)
    datos = []

    def espia(st, i, mv):
        a = sab(st, i, mv)
        c = contexto(st, i)
        vistas, cand = {}, []
        for m in mv:
            e = (m[0], tuple(sorted(st.extremos_tras(*m))))
            if e not in vistas:
                vistas[e] = len(cand)
                cand.append(m)
        if len(cand) >= 2:
            X = [_vec(rasgos(st, i, m, c), c) for m in cand]
            ea = (a[0], tuple(sorted(st.extremos_tras(*a))))
            datos.append((X, vistas[ea]))
        return a
    mae = L.politica("maestro")
    for k in range(n):
        rot = k % 3
        pols = [espia if j == rot else mae for j in range(3)]
        M.jugar_ronda(pols)
    return datos


def ajustar_logit(datos, iters=300, l2=1e-3, lr=0.5):
    d = len(RASGOS_IMIT)
    # estandarizar
    todas = [x for X, _ in datos for x in X]
    med = [sum(x[j] for x in todas) / len(todas) for j in range(d)]
    des = [math.sqrt(sum((x[j] - med[j]) ** 2 for x in todas) / len(todas)) or 1.0 for j in range(d)]
    Z = [([[(x[j] - med[j]) / des[j] for j in range(d)] for x in X], y) for X, y in datos]
    w = [0.0] * d
    m1, m2 = [0.0] * d, [0.0] * d
    for it in range(1, iters + 1):
        g = [0.0] * d
        ll = 0.0
        for X, y in Z:
            u = [sum(wj * xj for wj, xj in zip(w, x)) for x in X]
            mx = max(u)
            e = [math.exp(v - mx) for v in u]
            s = sum(e)
            p = [v / s for v in e]
            ll += math.log(max(p[y], 1e-12))
            for q, x in enumerate(X):
                coef = (1.0 if q == y else 0.0) - p[q]
                if coef:
                    for j in range(d):
                        g[j] += coef * x[j]
        n = len(Z)
        for j in range(d):
            gj = g[j] / n - l2 * w[j]
            m1[j] = 0.9 * m1[j] + 0.1 * gj
            m2[j] = 0.999 * m2[j] + 0.001 * gj * gj
            w[j] += lr * 0.1 * (m1[j] / (1 - 0.9 ** it)) / (math.sqrt(m2[j] / (1 - 0.999 ** it)) + 1e-8)
        if it % 50 == 0:
            print(f"   iter {it}  log-verosimilitud media {ll / n:.4f}", flush=True)
    # acierto
    ok = 0
    for X, y in Z:
        u = [sum(wj * xj for wj, xj in zip(w, x)) for x in X]
        ok += max(range(len(u)), key=lambda q: u[q]) == y
    pesos = {RASGOS_IMIT[j]: w[j] / des[j] for j in range(d)}
    importancia = {RASGOS_IMIT[j]: w[j] for j in range(d)}   # en desviaciones estándar
    return pesos, importancia, ok / len(Z)


# ═════════════════════════════ LIGA ═════════════════════════════

def _trabajo_liga(args):
    pool, n, semilla = args
    random.seed(semilla)
    cache = {}
    registros = []
    for _ in range(n):
        mesa = random.sample(range(len(pool)), 3)
        pols = []
        for q in mesa:
            if q not in cache:
                cache[q] = _pol_nombre(pool[q])
            pols.append(cache[q])
        p, _ = M.jugar_ronda(pols)
        registros.append((tuple(mesa), mesa[p]))
    return registros


def fuerza_mle(pool_n, registros, iters=500):
    """P(pierde i | mesa T) = w_i / Σ_T w. Algoritmo MM (Hunter 2004)."""
    w = [1.0] * pool_n
    perdidas = [0] * pool_n
    for T, l in registros:
        perdidas[l] += 1
    for _ in range(iters):
        den = [0.0] * pool_n
        for T, _l in registros:
            s = sum(w[q] for q in T)
            for q in T:
                den[q] += 1.0 / s
        w = [max(perdidas[q], 0.5) / den[q] for q in range(pool_n)]
        g = math.exp(sum(math.log(x) for x in w) / pool_n)
        w = [x / g for x in w]
    return w


def liga(pool, rondas):
    tareas = [(pool, -(-rondas // (PROCESOS * 4)), 900 + k) for k in range(PROCESOS * 4)]
    with Pool(PROCESOS) as p:
        partes = p.map(_trabajo_liga, tareas, chunksize=1)
    reg = [r for q in partes for r in q]
    w = fuerza_mle(len(pool), reg)
    i_m = pool.index("maestro")
    jugadas = [0] * len(pool)
    perd = [0] * len(pool)
    for T, l in reg:
        for q in T:
            jugadas[q] += 1
        perd[l] += 1
    # Puntuación: 1000 + 400·log10(w_maestro / w_i)  (estilo Elo: +400 = 10× menos probable perder)
    filas = []
    for q, nom in enumerate(pool):
        pts = 1000 + 400 * math.log10(w[i_m] / w[q])
        filas.append((pts, nom, 100 * perd[q] / jugadas[q], jugadas[q]))
    filas.sort(reverse=True)
    out = [f"LIGA · {len(pool)} estrategias · {len(reg)} rondas en mesas de 3 al azar",
           "Puntuación estilo Elo: Maestro = 1000; +400 = diez veces menos probable quedar último en la misma mesa\n",
           f"  {'#':>2} {'estrategia':<44}{'puntos':>8}{'pierde':>9}{'rondas':>9}"]
    for r, (pts, nom, pct, n) in enumerate(filas, 1):
        out.append(f"  {r:>2} {nom:<44}{pts:>8.0f}{pct:>8.1f}%{n:>9}")
    return "\n".join(out)


# ═════════════════════════════ CLI ═════════════════════════════

def _arg(n, d):
    return type(d)(sys.argv[sys.argv.index(n) + 1]) if n in sys.argv else d


if __name__ == "__main__":
    cmd = sys.argv[1]
    t0 = time.time()
    if cmd == "tribunal":
        txt = tribunal(_arg("--rondas", 18000))
        print(txt)
        open(os.path.join(DATOS, "campana_tribunal.txt"), "w").write(txt + "\n")
    elif cmd == "cem":
        mu, mejor = cem(_arg("--gen", 14), _arg("--pob", 16), _arg("--rondas", 4000))
        print("media final:", json.dumps({k: round(v, 3) for k, v in mu.items()}))
    elif cmd == "imitar":
        n = _arg("--rondas", 1200)
        with Pool(PROCESOS) as p:
            partes = p.map(_trabajo_imitar, [(-(-n // PROCESOS), 4400 + k, _arg("--muestras", 96)) for k in range(PROCESOS)])
        datos = [d for q in partes for d in q]
        print(f"{len(datos)} decisiones del Sabio grabadas ({time.time() - t0:.0f} s); ajustando…", flush=True)
        pesos, imp, acierto = ajustar_logit(datos)
        print(f"acierto del modelo al predecir al Sabio: {100 * acierto:.1f}%")
        json.dump(dict(pesos=pesos, importancia=imp, acierto=acierto, n=len(datos)),
                  open(os.path.join(DATOS, "imitar_sabio.json"), "w"), indent=1)
        for k, v in sorted(imp.items(), key=lambda kv: -abs(kv[1])):
            print(f"  {k:<16}{v:+7.3f}")
    elif cmd == "validar":
        # valida especificaciones con más rondas: nombres separados por espacios
        rondas = _arg("--rondas", 24000)
        rival = _arg("--rival", "maestro")
        banderas = {q + 1 for q, a in enumerate(sys.argv) if a.startswith("--")}
        for nombre in [a for q, a in enumerate(sys.argv) if q >= 2 and not a.startswith("--") and q not in banderas]:
            with Pool(PROCESOS) as p:
                k = sum(p.map(_trabajo_torneo, tareas_torneo(nombre, rival, rondas, _arg("--semilla", 3)), chunksize=1))
            print(f"  {nombre[:70]:<72} {L.fmt(k, rondas)}", flush=True)
    elif cmd == "liga":
        pool = json.load(open(_arg("--pool", os.path.join(DATOS, "liga_pool.json"))))
        txt = liga(pool, _arg("--rondas", 36000))
        print(txt)
        open(os.path.join(DATOS, "campana_liga.txt"), "w").write(txt + "\n")
    print(f"({time.time() - t0:.0f} s)")
