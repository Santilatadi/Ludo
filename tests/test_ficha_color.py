"""Pruebas unitarias de Ficha y Color."""

import pytest

from modelos.color import Color
from modelos.ficha import Ficha
from conftest import ubicar


# ----------------------------- Color -----------------------------------------

def test_hay_cuatro_colores_distintos():
    colores = Color.obtener_todos()
    assert len(colores) == 4
    assert len(set(colores)) == 4


@pytest.mark.parametrize("color", Color.obtener_todos())
def test_cada_color_tiene_rgb_valido(color):
    for rgb in (color.obtener_rgb(), color.obtener_rgb_claro()):
        assert len(rgb) == 3
        assert all(0 <= canal <= 255 for canal in rgb)


@pytest.mark.parametrize("color", Color.obtener_todos())
def test_nombre_mostrable_es_el_valor(color):
    assert color.obtener_nombre_mostrable() == color.value


# ----------------------------- Ficha -----------------------------------------

def test_ficha_nueva_esta_en_la_base():
    f = Ficha(1, Color.ROJO)
    assert (f.id_ficha, f.color, f.posicion, f.enBase, f.enMeta) == (1, Color.ROJO, 0, True, False)


def test_salir_de_base_la_pone_en_la_posicion_1():
    f = Ficha(1, Color.ROJO)
    f.salirBase()
    assert f.posicion == 1 and not f.enBase and not f.enMeta


def test_una_ficha_en_base_no_avanza():
    f = Ficha(1, Color.ROJO)
    f.mover(5)
    assert f.posicion == 0 and f.enBase


@pytest.mark.parametrize("desde, pasos, hasta", [(1, 1, 2), (10, 6, 16), (50, 4, 54), (52, 3, 55)])
def test_mover_suma_los_pasos(desde, pasos, hasta):
    f = ubicar(Ficha(1, Color.AZUL), desde)
    f.mover(pasos)
    assert f.obtenerPosicion() == hasta


def test_llegar_exacto_a_58_la_pone_en_meta():
    f = ubicar(Ficha(1, Color.VERDE), 55)
    f.mover(3)
    assert f.posicion == 58 and f.enMeta and not f.enBase


def test_si_se_pasa_de_la_meta_no_se_mueve():
    f = ubicar(Ficha(1, Color.VERDE), 55)
    f.mover(4)
    assert f.posicion == 55 and not f.enMeta


def test_una_ficha_en_meta_no_se_mueve_mas():
    f = ubicar(Ficha(1, Color.AMARILLO), 58)
    f.mover(1)
    assert f.posicion == 58 and f.enMeta


def test_volver_a_base_reinicia_la_ficha():
    f = ubicar(Ficha(1, Color.ROJO), 30)
    f.volverBase()
    assert f.posicion == 0 and f.enBase and not f.enMeta


@pytest.mark.parametrize("posicion", [0, 1, 33, 57, 58])
def test_ficha_se_guarda_y_recupera_igual(posicion):
    original = ubicar(Ficha(3, Color.AMARILLO), posicion)
    copia = Ficha.desde_diccionario(original.a_diccionario())
    assert copia.a_diccionario() == original.a_diccionario()
