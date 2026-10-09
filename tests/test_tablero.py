"""
Pruebas unitarias de Tablero: recorrido, casillas seguras, barreras y capturas.

Recordatorio de la numeración:
- Cada ficha tiene una posición relativa a su propio recorrido (0 base, 1-51
  circuito, 52-57 pasillo, 58 meta).
- El tablero la traduce a una casilla global del circuito (0 a 51) sumando la
  salida de su color: ROJO 0, AZUL 13, AMARILLO 26, VERDE 39.
"""

import pytest

from modelos.color import Color
from modelos.tablero import Tablero
from conftest import ubicar, posicion_para_casilla


# ----------------------------- Recorrido -------------------------------------

@pytest.mark.parametrize("color", Color.obtener_todos())
def test_la_posicion_1_es_la_casilla_de_salida_del_color(color):
    t = Tablero()
    f = ubicar(t_ficha(color), 1)
    assert t.obtener_casilla_global(f) == Tablero.SALIDA_COLOR[color]


@pytest.mark.parametrize("color", Color.obtener_todos())
def test_la_posicion_51_es_la_casilla_anterior_a_la_salida(color):
    t = Tablero()
    f = ubicar(t_ficha(color), 51)
    assert t.obtener_casilla_global(f) == (Tablero.SALIDA_COLOR[color] - 2) % 52


def test_valores_especiales_de_casilla_global():
    t = Tablero()
    assert t.obtener_casilla_global(ubicar(t_ficha(Color.ROJO), 0)) == -1
    assert t.obtener_casilla_global(ubicar(t_ficha(Color.ROJO), 58)) == 999
    assert t.obtener_casilla_global(ubicar(t_ficha(Color.ROJO), 54)) == 154


def test_las_salidas_son_casillas_seguras():
    for salida in Tablero.SALIDA_COLOR.values():
        assert salida in Tablero.CASILLAS_SEGURAS


def test_cada_color_tiene_una_salida_distinta():
    assert sorted(Tablero.SALIDA_COLOR.values()) == [0, 13, 26, 39]


# ----------------------------- Movimientos válidos ---------------------------

def test_desde_la_base_solo_con_6(rojo, tablero):
    f = rojo.fichas[0]
    assert not tablero.puedeMover(f, 5)
    assert tablero.puedeMover(f, 6)


def test_para_entrar_a_la_meta_hace_falta_el_numero_exacto(rojo, tablero):
    f = ubicar(rojo.fichas[0], 55)
    assert tablero.puedeMover(f, 3)
    assert not tablero.puedeMover(f, 4)


def test_ficha_en_meta_no_puede_moverse(rojo, tablero):
    assert not tablero.puedeMover(ubicar(rojo.fichas[0], 58), 1)


def test_obtener_movimientos_validos_filtra_las_fichas(rojo, tablero):
    ubicar(rojo.fichas[0], 10)
    ubicar(rojo.fichas[1], 56)       # con 3 se pasaría
    movimientos = tablero.obtenerMovimientosValidos(rojo, 3)
    assert movimientos == [rojo.fichas[0]]


def test_mover_una_ficha_invalida_no_la_cambia(rojo, tablero):
    f = rojo.fichas[0]                # en base
    assert tablero.moverFicha(f, 4) is False
    assert f.enBase


def test_sacar_ficha_con_6_la_pone_en_la_salida(rojo, tablero):
    f = rojo.fichas[0]
    assert tablero.moverFicha(f, 6) is True
    assert f.posicion == 1 and not f.enBase


def test_llegar_a_58_marca_la_meta(rojo, tablero):
    f = ubicar(rojo.fichas[0], 56)
    tablero.moverFicha(f, 2)
    assert f.enMeta and tablero.verificarMeta(f)


# ----------------------------- Barreras --------------------------------------

def _barrera_azul_en_casilla(azul, casilla):
    pos = posicion_para_casilla(Color.AZUL, casilla)
    ubicar(azul.fichas[0], pos)
    ubicar(azul.fichas[1], pos)


def test_no_se_puede_caer_sobre_una_barrera_rival(rojo, azul, tablero):
    _barrera_azul_en_casilla(azul, 20)
    f = ubicar(rojo.fichas[0], 19)                   # casilla 18
    assert not tablero.puedeMover(f, 2)              # caería en la 20


def test_no_se_puede_atravesar_una_barrera_rival(rojo, azul, tablero):
    _barrera_azul_en_casilla(azul, 20)
    f = ubicar(rojo.fichas[0], 19)
    assert not tablero.puedeMover(f, 5)              # pasaría por la 20
    assert tablero.puedeMover(f, 1)                  # se queda antes


def test_una_sola_ficha_rival_no_es_barrera(rojo, azul, tablero):
    ubicar(azul.fichas[0], posicion_para_casilla(Color.AZUL, 20))
    f = ubicar(rojo.fichas[0], 19)
    assert tablero.puedeMover(f, 5)


@pytest.mark.xfail(reason="INCONSISTENCIA: las reglas dicen que ninguna ficha (propia o rival) "
                          "atraviesa una barrera, pero el código solo bloquea barreras rivales. "
                          "Definir cuál de los dos se corrige.")
def test_tampoco_se_puede_atravesar_una_barrera_propia(rojo, tablero):
    ubicar(rojo.fichas[0], 20)
    ubicar(rojo.fichas[1], 20)                       # barrera roja
    f = ubicar(rojo.fichas[2], 18)
    assert not tablero.puedeMover(f, 4)


# ----------------------------- Capturas --------------------------------------

def test_caer_sobre_una_rival_la_manda_a_su_base(rojo, azul, tablero):
    victima = ubicar(azul.fichas[0], posicion_para_casilla(Color.AZUL, 19))
    f = ubicar(rojo.fichas[0], 17)                   # casilla 16
    tablero.moverFicha(f, 3)                         # llega a la 19
    assert victima.enBase and victima.posicion == 0
    assert f.posicion == 20


def test_en_casilla_segura_no_hay_captura(rojo, azul, tablero):
    assert 21 in Tablero.CASILLAS_SEGURAS
    rival = ubicar(azul.fichas[0], posicion_para_casilla(Color.AZUL, 21))
    f = ubicar(rojo.fichas[0], 19)                   # casilla 18
    tablero.moverFicha(f, 3)                         # llega a la 21
    assert not rival.enBase


def test_al_salir_de_la_base_no_captura_porque_la_salida_es_segura(rojo, azul, tablero):
    rival = ubicar(azul.fichas[0], posicion_para_casilla(Color.AZUL, 0))
    tablero.moverFicha(rojo.fichas[0], 6)
    assert not rival.enBase


def test_no_se_capturan_fichas_propias(rojo, tablero):
    propia = ubicar(rojo.fichas[0], 20)
    f = ubicar(rojo.fichas[1], 17)
    tablero.moverFicha(f, 3)
    assert propia.posicion == 20 and not propia.enBase


def test_las_fichas_en_el_pasillo_no_se_pueden_capturar(rojo, azul, tablero):
    en_pasillo = ubicar(azul.fichas[0], 54)
    f = ubicar(rojo.fichas[0], 17)
    tablero.moverFicha(f, 3)
    assert en_pasillo.posicion == 54


def test_enviar_ficha_a_base(rojo, tablero):
    f = ubicar(rojo.fichas[0], 33)
    tablero.enviarFichaABase(f)
    assert f.enBase


# ----------------------------- Auxiliar --------------------------------------

def t_ficha(color):
    from modelos.ficha import Ficha
    return Ficha(1, color)
