"""Pruebas unitarias de Jugador, incluida la elección de jugada del bot."""

import pytest

from modelos.color import Color
from modelos.ficha import Ficha
from modelos.jugador import Jugador
from conftest import ubicar, posicion_para_casilla, casilla_global


def test_jugador_nuevo_tiene_cuatro_fichas_de_su_color():
    j = Jugador("Ana", Color.VERDE)
    assert [f.id_ficha for f in j.obtenerFichas()] == [1, 2, 3, 4]
    assert all(f.color == Color.VERDE and f.enBase for f in j.fichas)
    assert j.getColor() == Color.VERDE and not j.es_bot


def test_asignar_color_cambia_tambien_las_fichas():
    j = Jugador("Ana", Color.VERDE)
    j.asignarColor(Color.ROJO)
    assert j.color == Color.ROJO
    assert all(f.color == Color.ROJO for f in j.fichas)


def test_gana_solo_con_las_cuatro_fichas_en_meta():
    j = Jugador("Ana", Color.ROJO)
    for f in j.fichas[:3]:
        ubicar(f, 58)
    assert not j.todasLasFichasEnMeta()
    ubicar(j.fichas[3], 58)
    assert j.todasLasFichasEnMeta()


@pytest.mark.parametrize("valor", [1, 2, 3, 4, 5, 6])
def test_desde_la_base_solo_se_sale_con_6(valor):
    j = Jugador("Ana", Color.ROJO)
    assert j.puedeMover(j.fichas[0], valor) == (valor == 6)


def test_no_puede_mover_una_ficha_ajena():
    j = Jugador("Ana", Color.ROJO)
    ajena = ubicar(Ficha(1, Color.AZUL), 10)
    assert not j.puedeMover(ajena, 3)


def test_no_puede_mover_ficha_en_meta_ni_pasarse():
    j = Jugador("Ana", Color.ROJO)
    ubicar(j.fichas[0], 58)
    ubicar(j.fichas[1], 56)
    assert not j.puedeMover(j.fichas[0], 1)
    assert not j.puedeMover(j.fichas[1], 3)
    assert j.puedeMover(j.fichas[1], 2)


def test_tiene_movimientos_validos():
    j = Jugador("Ana", Color.ROJO)
    assert not j.tieneMovimientosValidos(3)   # todas en base y no sacó 6
    assert j.tieneMovimientosValidos(6)


def test_seleccionar_ficha_por_indice_u_objeto():
    j = Jugador("Ana", Color.ROJO)
    assert j.seleccionarFicha(2) is j.fichas[2]
    assert j.seleccionarFicha(j.fichas[1]) is j.fichas[1]
    assert j.seleccionarFicha(9) is None
    assert j.seleccionarFicha(Ficha(1, Color.AZUL)) is None


def test_jugador_se_guarda_y_recupera_igual():
    j = Jugador("Bot 2", Color.AZUL, es_bot=True)
    ubicar(j.fichas[0], 20)
    ubicar(j.fichas[1], 58)
    copia = Jugador.desde_diccionario(j.a_diccionario())
    assert copia.a_diccionario() == j.a_diccionario()


# ----------------------------- Bot -------------------------------------------

def test_bot_sin_movimientos_devuelve_none(tablero):
    bot = Jugador("Bot", Color.ROJO, es_bot=True)
    assert bot.seleccionar_mejor_movimiento([], tablero) is None


def test_bot_prefiere_sacar_ficha_de_la_base(rojo, tablero):
    ubicar(rojo.fichas[1], 30)
    movimientos = [rojo.fichas[0], rojo.fichas[1]]  # una en base, otra en camino
    assert rojo.seleccionar_mejor_movimiento(movimientos, tablero) is rojo.fichas[0]


def test_bot_prefiere_la_ficha_que_esta_en_el_pasillo(rojo, tablero):
    ubicar(rojo.fichas[0], 53)
    ubicar(rojo.fichas[1], 40)
    movimientos = [rojo.fichas[1], rojo.fichas[0]]
    assert rojo.seleccionar_mejor_movimiento(movimientos, tablero) is rojo.fichas[0]


def test_bot_por_defecto_avanza_la_ficha_mas_adelantada(rojo, tablero):
    ubicar(rojo.fichas[0], 10)
    ubicar(rojo.fichas[1], 25)
    ubicar(rojo.fichas[2], 18)
    movimientos = rojo.fichas[:3]
    assert rojo.seleccionar_mejor_movimiento(movimientos, tablero) is rojo.fichas[1]


@pytest.mark.xfail(reason="BUG: el bot no conoce el dado (calcula posicion + 1 - 1), "
                          "así que nunca elige capturar. La firma esperada es "
                          "seleccionar_mejor_movimiento(movimientos, tablero, dado).")
def test_bot_elige_capturar_si_el_dado_se_lo_permite(rojo, azul, tablero):
    # La ficha roja 1 está a 3 casillas de una azul; la ficha roja 2 está más adelantada.
    ubicar(rojo.fichas[0], 13)                              # casilla 12
    ubicar(rojo.fichas[1], 30)
    ubicar(azul.fichas[0], posicion_para_casilla(Color.AZUL, 15))
    assert casilla_global(Color.ROJO, 16) == 15             # 13 + 3 cae sobre la azul
    movimientos = [rojo.fichas[0], rojo.fichas[1]]
    elegida = rojo.seleccionar_mejor_movimiento(movimientos, tablero, 3)
    assert elegida is rojo.fichas[0]
