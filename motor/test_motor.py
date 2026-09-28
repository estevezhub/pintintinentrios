"""
Pruebas del motor contra los casos de referencia del reglamento v1.7.

    python3 -m unittest motor/test_motor.py -v
"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import motor_pintintin as M  # noqa: E402


def T(a, b):
    return (min(a, b), max(a, b))


def armar(manos, marcador=(0, 0, 0), mesa=(), izq=None, der=None,
          ultimo=None, turno=0):
    """Mano con manos, mesa y puntas puestas a mano. El resto va a la pila."""
    h = M.Mano(list(marcador), turno, [M.nivel1_novato] * 3)
    h.manos = [set(T(*t) for t in m) for m in manos]
    h.mesa = set(T(*t) for t in mesa)
    usadas = set().union(*h.manos) | h.mesa
    h.pila = set(M.FICHAS) - usadas
    h.izq, h.der = izq, der
    if izq is not None:
        h.cadena = [(None, izq, der)]
    h.ultimo, h.turno = ultimo, turno
    return h


# Todos los seises en J1; los blancos sueltos en la pila.
SEISES = [
    [(6, 6), (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6)],
    [(1, 2), (1, 3), (1, 4), (1, 5), (2, 2), (2, 3), (2, 4)],
    [(2, 5), (3, 3), (3, 4), (3, 5), (4, 4), (4, 5), (5, 5)],
]


class Material(unittest.TestCase):
    def test_fichas(self):
        self.assertEqual(len(M.FICHAS), 25)
        self.assertEqual(M.TOTAL_PUNTOS, 165)
        cuenta = {n: sum(1 for t in M.FICHAS if M.tiene(t, n)) for n in range(7)}
        self.assertEqual(cuenta, {0: 5, 1: 5, 2: 7, 3: 7, 4: 7, 5: 7, 6: 7})


class PaseEnLaSalida(unittest.TestCase):
    def test_doble_falla_uno_paga_30_fallan_dos_paga_60(self):
        manos = [list(SEISES[0]), list(SEISES[1]), list(SEISES[2])]
        h = armar(manos)
        h.jugar(0, (6, 6), 'd')
        h.no_va(1)
        self.assertEqual(h.marcador[0], 30)
        h.no_va(2)
        self.assertEqual(h.marcador[0], 60)

    def test_dos_caras_paga_60_y_topa(self):
        h = armar(SEISES)
        h.jugar(0, (0, 6), 'd')              # 0 vivo (blancos en la pila) y 6 vivo
        self.assertEqual(len(h.caras_vivas()), 2)
        h.no_va(1)
        self.assertEqual(h.marcador[0], 60)
        h.no_va(2)                           # tope de 60 por jugada
        self.assertEqual(h.marcador[0], 60)


class PaseEnLaMano(unittest.TestCase):
    def mesa_media(self, izq, der, **kw):
        # la mesa ya tiene 3 fichas: no es salida
        return armar(SEISES, mesa=[(2, 6), (3, 6), (4, 6)], izq=izq, der=der,
                     ultimo=0, turno=1, **kw)

    def test_falla_uno_no_paga(self):
        h = self.mesa_media(6, 6)
        h.no_va(1)
        self.assertEqual(h.marcador[0], 0)

    def test_fallan_los_dos_una_cara(self):
        h = self.mesa_media(6, 6)
        h.no_va(1); h.no_va(2)
        self.assertEqual(h.marcador[0], 30)

    def test_fallan_los_dos_dos_caras(self):
        h = self.mesa_media(0, 6)            # blancos vivos (están en la pila)
        h.no_va(1); h.no_va(2)
        self.assertEqual(h.marcador[0], 60)

    def test_cara_muerta_no_cuenta(self):
        manos = [
            [(6, 6), (1, 6), (5, 6), (1, 2), (1, 3), (1, 4), (1, 5)],
            [(2, 2), (2, 4), (2, 5), (3, 3), (3, 4), (3, 5), (4, 4)],
            [(4, 5), (5, 5)],
        ]
        # los 5 blancos en la mesa → el extremo 0 está muerto
        h = armar(manos,
                  mesa=[(0, 2), (0, 3), (0, 4), (0, 5), (0, 6)],
                  izq=0, der=6, ultimo=0, turno=1)
        self.assertEqual(h.caras_vivas(), [6])
        h.no_va(1); h.no_va(2)
        self.assertEqual(h.marcador[0], 30)

    def test_repetir_con_el_doble_vuelve_a_cobrar(self):
        h = self.mesa_media(6, 6)
        h.manos[0] = {(6, 6), (0, 6), (1, 6)}
        h.no_va(1); h.no_va(2)
        h.jugar(0, (6, 6), 'd')
        h.no_va(1); h.no_va(2)
        self.assertEqual(h.marcador[0], 60)


class Techo(unittest.TestCase):
    def test_bono_recortado_a_149(self):
        h = armar(SEISES, marcador=(119, 0, 0))
        self.assertEqual(h.bono(0, 60), 30)
        self.assertEqual(h.bono(0, 30), 30)

    def test_desde_120_no_suma(self):
        h = armar(SEISES, marcador=(120, 0, 0))
        self.assertEqual(h.bono(0, 30), 0)

    def test_dominada_si_cruza(self):
        h = armar([[(6, 6)], [(5, 5)], [(4, 4)]], marcador=(140, 0, 0),
                  mesa=[(2, 6)], izq=6, der=2, ultimo=2, turno=0)
        h.jugar(0, (6, 6), 'i')
        self.assertEqual(h.marcador[0], 140 + 10 + 8)


class Cierre(unittest.TestCase):
    def test_dominada_suma_de_los_otros_dos(self):
        h = armar([[(2, 6)], [(5, 5), (4, 4)], [(3, 3)]],
                  mesa=[(6, 6)], izq=6, der=6, ultimo=2, turno=0)
        r = h.jugar(0, (2, 6), 'd')
        self.assertEqual(r, ('dom', 0))
        self.assertEqual(h.marcador[0], 18 + 6)

    def test_capicua_suma_30(self):
        h = armar([[(2, 6)], [(5, 5)], [(3, 3)]],
                  mesa=[(0, 2), (0, 6)], izq=2, der=6, ultimo=2, turno=0)
        h.jugar(0, (2, 6), 'd')
        self.assertEqual(h.marcador[0], 10 + 6 + 30)

    def test_tranca_mano_mas_baja_se_lleva_las_tres(self):
        h = armar([[(2, 3)], [(5, 5)], [(4, 4)]])
        h.ultimo = 1
        self.assertEqual(h._tranca(), ('tra', 0))
        self.assertEqual(h.marcador[0], 5 + 10 + 8)

    def test_tranca_empate_preferencia_del_que_tranco(self):
        h = armar([[(2, 3)], [(1, 4)], [(6, 6)]])
        h.ultimo = 1
        self.assertEqual(h._tranca(), ('tra', 1))

    def test_tranca_empate_sin_el_que_tranco_le_sigue_en_turno(self):
        h = armar([[(2, 3)], [(6, 6)], [(1, 4)]])
        h.ultimo = 1                         # trancó J2; empatan J1 y J3
        self.assertEqual(h._tranca(), ('tra', 2))   # a la derecha de J2 va J3


class PrimeraOficial(unittest.TestCase):
    def test_sale_el_doble_mas_alto(self):
        random.seed(3)
        for _ in range(200):
            h = M.Mano([0, 0, 0], 0, [M.nivel3_jugador] * 3, primera_oficial=True)
            dobles = [(v, v) for v in range(6, 1, -1)
                      if any((v, v) in m for m in h.manos)]
            h.correr()
            self.assertEqual(h.log[0].split(" juega ")[1], str(dobles[0]))


class MuerteSubita(unittest.TestCase):
    def test_sin_dobles_sale_la_ficha_mas_alta(self):
        h = M.Mano([150, 20, 20], 1, [M.nivel1_novato] * 3, modo="subita", duo=[1, 2])
        h.manos = [set(), {(4, 6), (2, 3), (0, 2)}, {(5, 6), (1, 2), (0, 3)}]
        M.salida_subita(h, [1, 2])
        self.assertEqual(h.mesa, {(5, 6)})
        self.assertEqual(h.turno, 1)

    def test_con_doble_sale_el_doble_mas_alto(self):
        h = M.Mano([150, 20, 20], 1, [M.nivel1_novato] * 3, modo="subita", duo=[1, 2])
        h.manos = [set(), {(5, 6), (2, 2)}, {(3, 3), (0, 3)}]
        M.salida_subita(h, [1, 2])
        self.assertEqual(h.mesa, {(3, 3)})

    def test_no_se_cobran_pases(self):
        h = M.Mano([150, 20, 20], 1, [M.nivel1_novato] * 3, modo="subita", duo=[1, 2])
        h.manos = [set(), {(6, 6), (2, 2)}, {(3, 3), (0, 3)}]
        M.salida_subita(h, [1, 2])
        h.no_va(2)
        self.assertEqual(h.marcador, [150, 20, 20])


class Invariantes(unittest.TestCase):
    def test_nadie_cruza_150_con_bonos_y_nunca_dos_a_la_vez(self):
        random.seed(7)
        pols = [M.nivel3_jugador, M.nivel5_maestro, M.nivel1_novato]
        for _ in range(400):
            marcador, ganador, primera = [0, 0, 0], None, True
            while max(marcador) < M.META:
                antes = marcador[:]
                h = M.Mano(marcador, ganador or 0, pols, primera_oficial=primera)
                _, w = h.correr()
                for j in range(3):
                    self.assertEqual(h.marcador[j] - antes[j], sum(h.ingreso[j]))
                    if j != w:
                        self.assertLess(h.marcador[j], M.META)
                self.assertLessEqual(sum(1 for s in h.marcador if s >= M.META), 1)
                self.assertEqual(sum(len(m) for m in h.manos) + len(h.mesa) + len(h.pila), 25)
                marcador, ganador, primera = h.marcador, w, False


if __name__ == "__main__":
    unittest.main()
