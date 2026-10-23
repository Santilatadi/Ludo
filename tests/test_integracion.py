"""
Pruebas de integración: partidas completas jugadas al azar, sin interfaz.

En lugar de verificar un caso puntual, se juegan muchas partidas y en cada
jugada se controla que el estado del juego siga siendo coherente
(invariantes). Se usa random.seed para que los resultados sean repetibles.
"""

import random

import pytest

from persistencia.persistencia_de_datos import PersistenciaDeDatos
from conftest import casilla_global

MAX_TIRADAS = 5000


def jugar_tirada(p):
    """Una tirada completa: tirar el dado y, si se puede, mover una ficha habilitada al azar."""
    p.lanzarDado()
    if p.dado:
        movimientos = p.obtenerMovimientosValidos()
        ficha = random.choice(movimientos)
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
                casilla = casilla_global(f.color, f.posicion)
                assert f in p.tablero.Casilleros[casilla]
                ocupadas.setdefault(casilla, set()).add(f.color)
    # Dos colores distintos no pueden compartir casilla: el que llegó último captura.
    for casilla, colores in ocupadas.items():
        assert len(colores) == 1, f"casilla {casilla} con {colores}"


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


def test_guardar_a_mitad_de_partida_y_seguir_da_el_mismo_resultado(crear_partida, tmp_path):
    """Si se guarda y se carga a mitad de partida, el resto del juego no cambia."""
    random.seed(7)
    original = crear_partida(4, bots=True)
    for _ in range(150):
        jugar_tirada(original)
    persistencia = PersistenciaDeDatos(str(tmp_path / "partida.json"))
    persistencia.guardarPartida(original)
    cargada, _ = persistencia.cargarPartida()

    estado_rng = random.getstate()
    while original.estado == "EN_CURSO":
        jugar_tirada(original)
    random.setstate(estado_rng)
    while cargada.estado == "EN_CURSO":
        jugar_tirada(cargada)

    a, b = cargada.guardar(), original.guardar()
    a.pop("tiempoTranscurrido"), b.pop("tiempoTranscurrido")
    assert a == b
