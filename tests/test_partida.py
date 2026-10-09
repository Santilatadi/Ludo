"""
Pruebas unitarias de Partida: configuración, turnos, dado y fin de partida.

El dado se fija con la fixture `dado` (ver conftest.py), así cada prueba
sabe exactamente qué va a salir.
"""

import pytest

from modelos.color import Color
from modelos.jugador import Jugador
from modelos.partida import Partida
from conftest import ubicar


# ----------------------------- Configuración ---------------------------------

def test_partida_nueva_no_esta_iniciada():
    p = Partida()
    assert p.estado == "NO_INICIADA"
    assert p.jugadores == [] and p.ganador is None and p.dado == 0


@pytest.mark.parametrize("cantidad, valida", [(1, False), (2, True), (3, True), (4, True), (5, False)])
def test_cantidad_de_jugadores_entre_2_y_4(cantidad, valida):
    p = Partida()
    assert p.configurarCantidadJugadores(cantidad) is valida
    assert p.cantidadJugadores == (cantidad if valida else 2)


def test_colores_disponibles_excluye_los_ocupados():
    p = Partida()
    p.jugadores = [Jugador("A", Color.ROJO)]
    assert Color.ROJO not in p.obtenerColoresDisponibles()
    assert len(p.obtenerColoresDisponibles()) == 3
    assert not p.validarColor(Color.ROJO) and p.validarColor(Color.AZUL)


def test_asignar_color_solo_si_esta_libre():
    p = Partida()
    a, b = Jugador("A", Color.ROJO), Jugador("B", Color.AZUL)
    p.jugadores = [a, b]
    assert p.asignarColor(b, Color.ROJO) is False and b.color == Color.AZUL
    assert p.asignarColor(b, Color.VERDE) is True and b.color == Color.VERDE


def test_todos_los_colores_asignados():
    p = Partida()
    p.configurarCantidadJugadores(2)
    p.jugadores = [Jugador("A", Color.ROJO)]
    assert not p.todosLosColoresAsignados()                 # falta un jugador
    p.jugadores.append(Jugador("B", Color.ROJO))
    assert not p.todosLosColoresAsignados()                 # color repetido
    p.jugadores[1].asignarColor(Color.AZUL)
    assert p.todosLosColoresAsignados()


def test_iniciar_deja_la_partida_en_curso(crear_partida):
    p = crear_partida(3)
    assert p.estado == "EN_CURSO"
    assert p.turnoActual == 0 and p.obtenerJugadorActual().nombre == "J1"
    assert not p.dado_lanzado and p.tablero.jugadores is p.jugadores


# ----------------------------- Dado y turnos ---------------------------------

def test_sin_movimientos_posibles_pasa_el_turno(crear_partida, dado):
    p = crear_partida(2)
    dado(3)                                    # todas en base y no sacó 6
    assert p.tirarDado() == 3
    assert p.turnoActual == 1 and not p.dado_lanzado


@pytest.mark.xfail(reason="BUG: tirarDado arma el aviso 'no tiene movimientos válidos' pero "
                          "siguienteTurno() lo pisa con 'Turno de ...': el jugador no ve por qué perdió el turno.")
def test_se_avisa_que_no_habia_movimientos(crear_partida, dado):
    p = crear_partida(2)
    dado(3)
    p.tirarDado()
    assert "no tiene movimientos" in p.mensaje_estado


def test_con_un_6_puede_sacar_ficha(crear_partida, dado):
    p = crear_partida(2)
    dado(6)
    p.tirarDado()
    assert p.esperando_movimiento
    assert len(p.obtenerMovimientosValidos()) == 4


def test_no_se_puede_tirar_dos_veces_seguidas(crear_partida, dado):
    p = crear_partida(2)
    dado(6)
    p.tirarDado()
    assert p.tirarDado() == 6                  # devuelve el mismo, no vuelve a tirar


def test_no_se_puede_mover_una_ficha_que_no_es_valida(crear_partida, dado):
    p = crear_partida(2)
    dado(6)
    p.tirarDado()
    ajena = p.jugadores[1].fichas[0]
    assert p.moverFicha(ajena) is False


def test_sacar_un_6_repite_el_turno(crear_partida, dado):
    p = crear_partida(2)
    dado(6)
    p.tirarDado()
    p.moverFicha(p.jugadores[0].fichas[0])
    assert p.turnoActual == 0 and not p.dado_lanzado
    assert "vuelve a tirar" in p.mensaje_estado


def test_sin_6_despues_de_mover_pasa_el_turno(crear_partida, dado):
    p = crear_partida(2)
    ubicar(p.jugadores[0].fichas[0], 10)
    dado(4)
    p.tirarDado()
    p.moverFicha(p.jugadores[0].fichas[0])
    assert p.turnoActual == 1 and p.consecutivoSeis == 0


def test_tres_6_seguidos_pierde_el_turno(crear_partida, dado):
    p = crear_partida(2)
    dado(6, 6, 6)
    for _ in range(2):
        p.tirarDado()
        p.moverFicha(p.obtenerMovimientosValidos()[0])
        assert p.turnoActual == 0
    p.tirarDado()                              # tercer 6
    assert p.turnoActual == 1
    assert p.consecutivoSeis == 0


@pytest.mark.xfail(reason="BUG: el aviso '¡3 seis consecutivos!' lo pisa siguienteTurno() "
                          "con 'Turno de ...'.")
def test_se_avisa_que_perdio_el_turno_por_tres_6(crear_partida, dado):
    p = crear_partida(2)
    dado(6, 6, 6)
    for _ in range(2):
        p.tirarDado()
        p.moverFicha(p.obtenerMovimientosValidos()[0])
    p.tirarDado()
    assert "3 seis" in p.mensaje_estado


def test_el_turno_vuelve_al_primero_despues_del_ultimo(crear_partida, dado):
    p = crear_partida(3)
    dado(1, 2, 3)
    for _ in range(3):
        p.tirarDado()                          # nadie puede mover: pasa el turno
    assert p.turnoActual == 0


# ----------------------------- Fin de partida --------------------------------

def test_llevar_la_cuarta_ficha_a_la_meta_gana(crear_partida, dado):
    p = crear_partida(2)
    j1 = p.jugadores[0]
    for f in j1.fichas[:3]:
        ubicar(f, 58)
    ubicar(j1.fichas[3], 55)
    dado(3)
    p.tirarDado()
    assert p.moverFicha(j1.fichas[3])
    assert p.estado == "FINALIZADA" and p.ganador is j1
    assert "ganado" in p.mensaje_estado


def test_sin_cuatro_fichas_en_meta_no_hay_ganador(crear_partida):
    p = crear_partida(2)
    assert p.identificarGanador() is False and p.ganador is None


def test_cancelar_partida_la_reinicia(crear_partida):
    p = crear_partida(2)
    p.cancelarPartida()
    assert p.estado == "NO_INICIADA" and p.jugadores == [] and p.ganador is None


# ----------------------------- Guardado --------------------------------------

def test_partida_se_guarda_y_recupera_igual(crear_partida, dado):
    p = crear_partida(4)
    ubicar(p.jugadores[2].fichas[1], 33)
    dado(6)
    p.tirarDado()
    copia = Partida.desde_diccionario(p.a_diccionario())
    assert copia.a_diccionario() == p.a_diccionario()
    assert copia.tablero.jugadores is copia.jugadores


def test_el_ganador_se_recupera_como_el_mismo_jugador(crear_partida):
    p = crear_partida(2)
    for f in p.jugadores[1].fichas:
        ubicar(f, 58)
    p.identificarGanador()
    p.finalizar()
    copia = Partida.desde_diccionario(p.a_diccionario())
    assert copia.ganador is copia.jugadores[1]
