"""
Pruebas de integración: partidas completas jugadas por bots, sin interfaz.

En lugar de verificar un caso puntual, se juegan muchas partidas y en cada
jugada se controla que el estado del juego siga siendo coherente
(invariantes). Se usa random.seed para que los resultados sean repetibles.
"""

import random

import pytest

from modelos.tablero import Tablero
from modelos.partida import Partida

MAX_TIRADAS = 5000


def jugar_tirada(p):
    """Una tirada completa: tirar el dado y, si se puede, mover lo que elija el bot."""
    p.tirarDado()
    if p.esperando_movimiento:
        jugador = p.obtenerJugadorActual()
        movimientos = p.obtenerMovimientosValidos()
        ficha = jugador.seleccionar_mejor_movimiento(movimientos, p.tablero)
        assert ficha in movimientos
        assert p.moverFicha(ficha)


def verificar_invariantes(p):
    assert 0 <= p.turnoActual < len(p.jugadores)
    ocupadas = {}
    for j in p.jugadores:
        assert len(j.fichas) == 4
        for f in j.fichas:
            assert 0 <= f.posicion <= 58
            assert f.enBase == (f.posicion == 0)
            assert f.enMeta == (f.posicion == 58)
            assert f.color == j.color
            if 1 <= f.posicion <= 51:
                casilla = p.tablero.obtener_casilla_global(f)
                ocupadas.setdefault(casilla, set()).add(f.color)
    # Dos colores distintos solo pueden compartir casilla si es segura
    # (en cualquier otra, el que llegó último tendría que haber capturado).
    for casilla, colores in ocupadas.items():
        if len(colores) > 1:
            assert casilla in Tablero.CASILLAS_SEGURAS, f"casilla {casilla} con {colores}"


@pytest.mark.parametrize("cantidad", [2, 3, 4])
@pytest.mark.parametrize("semilla", range(10))
def test_partidas_completas_entre_bots_terminan_bien(crear_partida, cantidad, semilla):
    random.seed(semilla)
    p = crear_partida(cantidad, bots=True)
    tiradas = 0
    while p.estado == "EN_CURSO":
        jugar_tirada(p)
        verificar_invariantes(p)
        tiradas += 1
        assert tiradas < MAX_TIRADAS, "la partida no termina"
    assert p.estado == "FINALIZADA"
    assert p.ganador is not None and p.ganador.todasLasFichasEnMeta()


def test_guardar_a_mitad_de_partida_y_seguir_da_el_mismo_resultado(crear_partida):
    """Si se guarda y se carga a mitad de partida, el resto del juego no cambia."""
    random.seed(7)
    original = crear_partida(4, bots=True)
    for _ in range(150):
        jugar_tirada(original)
    cargada = Partida.desde_diccionario(original.a_diccionario())

    estado_rng = random.getstate()
    while original.estado == "EN_CURSO":
        jugar_tirada(original)
    random.setstate(estado_rng)
    while cargada.estado == "EN_CURSO":
        jugar_tirada(cargada)

    assert cargada.a_diccionario() == original.a_diccionario()
