"""
Pruebas unitarias de Tablero: recorrido, barreras y capturas.

Recordatorio de la numeración:
- Cada ficha tiene una posición relativa a su propio recorrido (0 base, 1-51
  circuito, 52-57 pasillo, 58 meta).
- El tablero la traduce a un casillero del circuito (0 a 51) con la salida de su
  color (atributo inicio): ROJO 0, VERDE 13, AMARILLO 26, AZUL 39.
"""

import pytest

from modelos.color import Color
from modelos.ficha import Ficha
from modelos.tablero import Tablero
from conftest import ubicar, posicion_para_casilla, salida


# ----------------------------- Recorrido -------------------------------------

def test_salidas_de_cada_color():
    assert {c: salida(c) for c in Color} == {Color.ROJO: 0, Color.VERDE: 13, Color.AMARILLO: 26, Color.AZUL: 39}


def test_fin_es_el_casillero_anterior_a_la_salida():
    t = Tablero()
    t.inicializar()
    assert t.fin == [(s - 2) % 52 for s in t.inicio]


@pytest.mark.parametrize("color", list(Color))
def test_sacar_ficha_la_pone_en_su_casillero_de_salida(tablero, color):
    f = Ficha(color)
    assert tablero.sacarFicha(f)
    assert f in tablero.Casilleros[salida(color)] and f.posicion == 1


def test_actualizar_posiciones_saca_del_circuito_a_las_fichas_del_pasillo(tablero):
    f = ubicar(Ficha(Color.ROJO), 51)
    assert f in tablero.Casilleros[50]
    f.mover(2)                                       # entra al pasillo (53)
    tablero.actualizarPosiciones()
    assert all(f not in casillero for casillero in tablero.Casilleros)


# ----------------------------- Movimientos válidos ---------------------------

def jugar(tablero, ficha, valor):
    """Lo que hace Partida.moverFicha en el CU-08: valida, calcula el destino, mueve
    y verifica captura y meta. Devuelve (se_movio, capturo, llego_a_meta)."""
    if not tablero.puedeMover(ficha, valor):
        return False, False, False
    destino = tablero.calcularDestino(ficha, valor)
    se_movio = tablero.moverFicha(ficha, destino)
    return se_movio, tablero.verificarCaptura(ficha), tablero.verificarMeta(ficha)


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
    assert jugar(tablero, f, 4) == (False, False, False)
    assert f.enBase


def test_sacar_ficha_con_6_la_pone_en_la_salida(rojo, tablero):
    f = rojo.fichas[0]
    assert jugar(tablero, f, 6) == (True, False, False)
    assert f.posicion == 1 and not f.enBase


def test_llegar_a_58_marca_la_meta(rojo, tablero):
    f = ubicar(rojo.fichas[0], 56)
    assert jugar(tablero, f, 2) == (True, False, True)
    assert f.enMeta and tablero.verificarMeta(f)


# ----------------------------- Barreras --------------------------------------

def _barrera_azul_en_casilla(azul, casilla):
    pos = posicion_para_casilla(Color.AZUL, casilla)
    ubicar(azul.fichas[0], pos)
    ubicar(azul.fichas[1], pos)


def test_no_se_puede_salir_de_la_base_si_hay_una_barrera_en_la_salida(rojo, azul, tablero):
    _barrera_azul_en_casilla(azul, salida(Color.ROJO))
    assert not tablero.puedeMover(rojo.fichas[0], 6)


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


def test_tampoco_se_puede_atravesar_una_barrera_propia(rojo, tablero):
    ubicar(rojo.fichas[0], 20)
    ubicar(rojo.fichas[1], 20)                       # barrera roja
    f = ubicar(rojo.fichas[2], 18)
    assert not tablero.puedeMover(f, 4)


# ----------------------------- Capturas --------------------------------------

def test_caer_sobre_una_rival_la_manda_a_su_base(rojo, azul, tablero):
    victima = ubicar(azul.fichas[0], posicion_para_casilla(Color.AZUL, 19))
    f = ubicar(rojo.fichas[0], 17)                   # casilla 16
    assert jugar(tablero, f, 3) == (True, True, False)   # llega a la 19
    assert victima.enBase and victima.posicion == 0
    assert f.posicion == 20


def test_no_hay_casillas_seguras(rojo, azul, tablero):
    rival = ubicar(azul.fichas[0], posicion_para_casilla(Color.AZUL, 21))
    f = ubicar(rojo.fichas[0], 19)                   # casilla 18
    jugar(tablero, f, 3)                             # llega a la 21
    assert rival.enBase


def test_al_salir_de_la_base_captura_a_la_rival_de_la_salida(rojo, azul, tablero):
    rival = ubicar(azul.fichas[0], posicion_para_casilla(Color.AZUL, 0))
    jugar(tablero, rojo.fichas[0], 6)
    assert rival.enBase


def test_no_se_capturan_fichas_propias(rojo, tablero):
    propia = ubicar(rojo.fichas[0], 20)
    f = ubicar(rojo.fichas[1], 17)
    jugar(tablero, f, 3)
    assert propia.posicion == 20 and not propia.enBase


def test_las_fichas_en_el_pasillo_no_se_pueden_capturar(rojo, azul, tablero):
    en_pasillo = ubicar(azul.fichas[0], 54)
    f = ubicar(rojo.fichas[0], 17)
    jugar(tablero, f, 3)
    assert en_pasillo.posicion == 54


def test_mover_ficha_lleva_a_la_posicion_destino(rojo, tablero):
    f = ubicar(rojo.fichas[0], 10)
    assert tablero.moverFicha(f, 14) and f.posicion == 14
    assert not tablero.moverFicha(f, 12)             # no retrocede


def test_enviar_ficha_a_base(rojo, tablero):
    f = ubicar(rojo.fichas[0], 33)
    tablero.enviarFichaABase(f)
    assert f.enBase
