"""Pruebas unitarias de Jugador."""

from modelos.color import Color
from modelos.ficha import Ficha
from modelos.jugador import Jugador
from conftest import ubicar


def test_jugador_nuevo_tiene_cuatro_fichas_de_su_color():
    j = Jugador("Ana", Color.VERDE)
    assert len(j.obtenerFichas()) == 4
    assert all(f.color == Color.VERDE and f.enBase for f in j.fichas)
    assert j.getColor() == Color.VERDE
    assert (j.movimientos, j.puntaje) == (0, 0)


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


def test_tiene_movimientos_validos(tablero):
    j = Jugador("Ana", Color.ROJO)
    assert not j.tieneMovimientosValidos(3, tablero)   # todas en base y no sacó 6
    assert j.tieneMovimientosValidos(6, tablero)


def test_seleccionar_ficha_solo_devuelve_fichas_propias():
    j = Jugador("Ana", Color.ROJO)
    assert j.seleccionarFicha(j.fichas[1]) is j.fichas[1]
    assert j.seleccionarFicha(Ficha(Color.AZUL)) is None


def test_confirmar_y_cancelar_accion():
    j = Jugador("Ana", Color.ROJO)
    assert j.confirmarAccion() is True and j.cancelarAccion() is False


def test_visualizar_estadisticas():
    j = Jugador("Ana", Color.ROJO)
    j.movimientos, j.puntaje = 3, 120
    ubicar(j.fichas[0], 58)
    assert j.visualizarEstadisticas() == "Ana: 3 movimientos, 120 puntos, 1/4 fichas en meta"
