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
    p.iniciar()                                  # DS N1: sin jugadores queda en configuración
    assert p.estado == "CONFIGURACION"
    assert p.configurarCantidadJugadores(cantidad) is valida
    assert p.numeroJugadores() == (cantidad if valida else 0)


def test_anadir_y_eliminar_jugador_respetan_2_a_4():
    p = Partida()
    p.configurarCantidadJugadores(2)
    assert p.añadirJugador() and p.añadirJugador() and not p.añadirJugador()
    assert p.numeroJugadores() == 4
    assert p.eliminarJugador() and p.eliminarJugador() and not p.eliminarJugador()
    assert p.cantidadJugadores == 2


def test_registrar_nombres_valida_vacios_y_repetidos():
    p = Partida()
    p.configurarCantidadJugadores(3)
    assert p.registrarNombre("Ana", 0)
    assert not p.validarNombre("Ana", 1) and not p.registrarNombre("Ana", 1)
    assert not p.registrarNombre("   ", 1)
    assert p.registrarNombre("Beto")              # sin índice: primer jugador sin nombre
    assert p.registrarJugadorConsola()            # CU-03 C
    assert [j.nombre for j in p.jugadores] == ["Ana", "Beto", "Bot 3"]


def test_seleccionar_color_y_cancelar_seleccion():
    p = Partida()
    p.configurarCantidadJugadores(2)
    assert p.seleccionarColores() == list(Color)
    assert p.seleccionarColor(Color.VERDE)        # sin índice: primer jugador sin color
    assert not p.seleccionarColor(Color.VERDE, 1) # CU-04 A: color no disponible
    assert Color.VERDE not in p.seleccionarColores() and p.coloresDisponibles == p.seleccionarColores()
    p.cancelarSeleccionColores()
    assert p.seleccionarColores() == list(Color)


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
    assert p.dado == 0 and p.turnosJugados == 1


# ----------------------------- Dado y turnos ---------------------------------

def test_sin_movimientos_posibles_pasa_el_turno(crear_partida, dado):
    p = crear_partida(2)
    dado(3)                                    # todas en base y no sacó 6
    assert p.lanzarDado() == 3
    assert p.turnoActual == 1 and p.dado == 0


def test_con_un_6_puede_sacar_ficha(crear_partida, dado):
    p = crear_partida(2)
    dado(6)
    p.lanzarDado()
    assert p.dado == 6
    assert len(p.obtenerMovimientosValidos()) == 4


def test_no_se_puede_tirar_dos_veces_seguidas(crear_partida, dado):
    p = crear_partida(2)
    dado(6)
    p.lanzarDado()
    assert p.lanzarDado() == 6                  # devuelve el mismo, no vuelve a tirar


def test_no_se_puede_mover_una_ficha_que_no_es_valida(crear_partida, dado):
    p = crear_partida(2)
    dado(6)
    p.lanzarDado()
    ajena = p.jugadores[1].fichas[0]
    assert p.moverFicha(ajena) is False


def test_sacar_un_6_repite_el_turno(crear_partida, dado):
    p = crear_partida(2)
    dado(6)
    p.lanzarDado()
    p.moverFicha(p.jugadores[0].fichas[0])
    assert p.turnoActual == 0 and p.dado == 0     # vuelve a tirar


def test_sin_6_despues_de_mover_pasa_el_turno(crear_partida, dado):
    p = crear_partida(2)
    ubicar(p.jugadores[0].fichas[0], 10)
    dado(4)
    p.lanzarDado()
    p.moverFicha(p.jugadores[0].fichas[0])
    assert p.turnoActual == 1


def test_tres_6_seguidos_pierde_el_turno(crear_partida, dado):
    p = crear_partida(2)
    dado(6, 6, 6)
    for _ in range(2):
        p.lanzarDado()
        p.moverFicha(p.obtenerMovimientosValidos()[0])
        assert p.turnoActual == 0
    p.lanzarDado()                              # tercer 6
    assert p.turnoActual == 1 and p.dado == 0


def test_el_turno_vuelve_al_primero_despues_del_ultimo(crear_partida, dado):
    p = crear_partida(3)
    dado(1, 2, 3)
    for _ in range(3):
        p.lanzarDado()                          # nadie puede mover: pasa el turno
    assert p.turnoActual == 0


# ----------------------------- Fin de partida --------------------------------

def test_llevar_la_cuarta_ficha_a_la_meta_gana(crear_partida, dado):
    p = crear_partida(2)
    j1 = p.jugadores[0]
    for f in j1.fichas[:3]:
        ubicar(f, 58)
    ubicar(j1.fichas[3], 55)
    dado(3)
    p.lanzarDado()
    assert p.moverFicha(j1.fichas[3])
    assert p.estado == "FINALIZADA" and p.ganador is j1


def test_sin_cuatro_fichas_en_meta_no_hay_ganador(crear_partida):
    p = crear_partida(2)
    assert p.verificarGanador() is False and p.ganador is None


def test_cancelar_partida_la_reinicia(crear_partida):
    p = crear_partida(2)
    p.cancelarPartida()
    assert p.estado == "NO_INICIADA" and p.jugadores == [] and p.ganador is None


# ----------------------------- Pausa, guardado y salida ----------------------

def test_pausar_y_reanudar(crear_partida):
    p = crear_partida(2)
    p.pausar()
    assert p.estado == "PAUSADA" and p.verificarPartidaActiva()
    p.reanudar()
    assert p.estado == "EN_CURSO"


def test_guardar_devuelve_el_estado_completo(crear_partida, dado):
    p = crear_partida(2)
    ubicar(p.jugadores[1].fichas[2], 33)
    dado(6)
    p.lanzarDado()
    datos = p.guardar()
    assert datos["dado"] == 6 and datos["turnoActual"] == 0 and datos["estado"] == "EN_CURSO"
    assert datos["jugadores"][1]["fichas"][2] == {"posicion": 33, "enBase": False, "enMeta": False}


def test_solo_se_pide_confirmacion_con_una_partida_activa(crear_partida):
    p = crear_partida(2)
    assert p.solicitarConfirmacion() and p.mantenerPartida()
    p.cerrarPartida()
    assert p.estado == "CERRADA" and p.jugadores == []
    assert not p.solicitarConfirmacion()


def test_cerrar_estadisticas_dice_si_la_partida_sigue(crear_partida):
    p = crear_partida(2)
    assert p.cerrarPantallaEstadisticas()
    p.finalizar()
    assert not p.cerrarPantallaEstadisticas()


def test_puntaje_base_0_camino_posicion_meta_100(crear_partida):
    p = crear_partida(2)
    j = p.jugadores[0]
    ubicar(j.fichas[1], 20)
    ubicar(j.fichas[2], 58)
    p.recopilarEstadisticas()
    assert j.puntaje == 0 + 20 + 100 + 0


def test_resumen_de_estadisticas(crear_partida):
    p = crear_partida(2)
    resumen = p.recopilarEstadisticas()
    assert "Turnos jugados: 1" in resumen and "Ganador: En curso" in resumen
    assert "J1: 0 movimientos, 0 puntos, 0/4 fichas en meta" in resumen


# ----------------------------- Configuración (DS N5) --------------------------

def datos_configuracion(cantidad, nombres, colores):
    return {"cantidadJugadores": cantidad,
            "jugadores": [{"nombre": n, "color": c} for n, c in zip(nombres, colores)]}


@pytest.mark.parametrize("cantidad, nombres, colores, error", [
    (1, ["A"], [Color.ROJO], "entre 2 y 4"),
    (5, list("ABCDE"), [Color.ROJO] * 5, "entre 2 y 4"),
    (2, ["A", "  "], [Color.ROJO, Color.AZUL], "vacío"),
    (2, ["A", "A"], [Color.ROJO, Color.AZUL], "repetidos"),
    (2, ["A", "B"], [Color.ROJO, None], "color asignado"),
    (2, ["A", "B"], [Color.ROJO, Color.ROJO], "color diferente"),
])
def test_configuracion_invalida_informa_el_motivo(cantidad, nombres, colores, error):
    p = Partida(datos_configuracion(cantidad, nombres, colores))
    assert error in p.validarConfiguracion()


def test_configuracion_valida_crea_los_jugadores():
    p = Partida(datos_configuracion(2, ["A", "B"], [Color.ROJO, Color.AZUL]))
    assert p.validarConfiguracion() == ""
    p.iniciar()
    assert [(j.nombre, j.color) for j in p.jugadores] == [("A", Color.ROJO), ("B", Color.AZUL)]
    assert p.estado == "EN_CURSO"
