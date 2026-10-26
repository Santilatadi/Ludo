"""Pruebas unitarias de Ficha y Color."""

import pytest

from modelos.color import Color
from modelos.ficha import Ficha
from conftest import ubicar


# ----------------------------- Color -----------------------------------------

def test_hay_cuatro_colores_como_en_el_diagrama():
    assert [c.name for c in Color] == ["ROJO", "AZUL", "AMARILLO", "VERDE"]


# ----------------------------- Ficha -----------------------------------------

def test_ficha_nueva_esta_en_la_base():
    f = Ficha(Color.ROJO)
    assert (f.color, f.posicion, f.enBase, f.enMeta) == (Color.ROJO, 0, True, False)


def test_salir_de_base_la_pone_en_la_posicion_1():
    f = Ficha(Color.ROJO)
    f.salirBase()
    assert f.posicion == 1 and not f.enBase and not f.enMeta


def test_una_ficha_en_base_no_avanza():
    f = Ficha(Color.ROJO)
    f.mover(5)
    assert f.posicion == 0 and f.enBase


@pytest.mark.parametrize("desde, pasos, hasta", [(1, 1, 2), (10, 6, 16), (50, 4, 54), (52, 3, 55)])
def test_mover_suma_los_pasos(desde, pasos, hasta):
    f = ubicar(Ficha(Color.AZUL), desde)
    f.mover(pasos)
    assert f.obtenerPosicion() == hasta


def test_llegar_exacto_a_58_la_pone_en_meta():
    f = ubicar(Ficha(Color.VERDE), 55)
    f.mover(3)
    assert f.posicion == 58 and f.enMeta and not f.enBase


def test_si_se_pasa_de_la_meta_no_se_mueve():
    f = ubicar(Ficha(Color.VERDE), 55)
    f.mover(4)
    assert f.posicion == 55 and not f.enMeta


def test_una_ficha_en_meta_no_se_mueve_mas():
    f = ubicar(Ficha(Color.AMARILLO), 58)
    f.mover(1)
    assert f.posicion == 58 and f.enMeta


def test_volver_a_base_reinicia_la_ficha():
    f = ubicar(Ficha(Color.ROJO), 30)
    f.volverBase()
    assert f.posicion == 0 and f.enBase and not f.enMeta


def test_llegar_meta():
    f = ubicar(Ficha(Color.ROJO), 40)
    f.llegarMeta()
    assert f.posicion == 58 and f.enMeta
