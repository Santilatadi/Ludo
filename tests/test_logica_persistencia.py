"""Pruebas de GameManager (controlador) y PersistenciaDeDatos."""

import json
import os

import pytest

from logica.game_manager import GameManager
from modelos.color import Color
from persistencia.persistencia_de_datos import PersistenciaDeDatos
from conftest import ubicar


# ============================= GameManager ==================================

@pytest.fixture
def gm_en_juego(crear_partida):
    g = GameManager()
    g.partidaActual = crear_partida(2)
    return g


def configurar(g, nombres, colores):
    """CU-01 a CU-04 a través del GameManager, como lo hace la pantalla de configuración."""
    g.iniciarPartida()
    g.configurarCantidadJugadores(len(nombres))
    for i, (nombre, color) in enumerate(zip(nombres, colores)):
        assert g.registrarNombre(nombre, i)[0]
        assert g.seleccionarColor(color, i)[0]


def test_game_manager_solo_tiene_la_partida_actual():
    g = GameManager()
    assert vars(g) == {"partidaActual": None}


def test_iniciar_partida_sin_datos_crea_la_partida_en_configuracion():
    g = GameManager()
    assert g.iniciarPartida() == (True, "")                       # DS N1
    assert g.partidaActual.estado == "CONFIGURACION"


def test_cantidad_fuera_de_rango_informa_maximo_y_minimo():
    g = GameManager()
    g.iniciarPartida()
    assert g.configurarCantidadJugadores(5) == (False, "El máximo es 4 jugadores.")
    assert g.configurarCantidadJugadores(1) == (False, "El mínimo es 2 jugadores.")
    assert g.configurarCantidadJugadores(3)[0]


def test_registrar_nombres_y_bots():
    g = GameManager()
    g.iniciarPartida()
    g.configurarCantidadJugadores(3)
    assert g.registrarNombre("Ana", 0)[0]
    exito, mensaje = g.registrarNombre("Ana", 1)
    assert not exito and "repetidos" in mensaje
    exito, mensaje = g.registrarNombre("  ", 1)
    assert not exito and "vacío" in mensaje
    assert g.registrarNombre("Beto", 1)[0]
    assert g.registrarNombre(None, 2)[0]                          # CU-03 C: jugador de la consola
    assert [j.nombre for j in g.partidaActual.jugadores] == ["Ana", "Beto", "Bot 3"]


def test_seleccionar_colores_muestra_solo_los_disponibles():
    g = GameManager()
    g.iniciarPartida()
    g.configurarCantidadJugadores(2)
    assert g.seleccionarColores() == list(Color)
    assert g.seleccionarColor(Color.VERDE, 0)[0]
    assert Color.VERDE not in g.seleccionarColores()
    exito, mensaje = g.seleccionarColor(Color.VERDE, 1)           # DS N4 A1
    assert not exito and "ya está asignado" in mensaje


def test_iniciar_con_la_configuracion_completa_empieza_y_guarda():
    g = GameManager()
    configurar(g, ["Ana", "Beto"], [Color.ROJO, Color.AZUL])
    exito, _ = g.iniciarPartida()
    assert exito and g.partidaActual.estado == "EN_CURSO"
    assert g.reanudarPartidaGuardada()[0]                          # DS N4 pasos 9 y 10


def test_iniciar_con_datos_invalidos_informa_el_motivo():
    g = GameManager()
    exito, mensaje = g.iniciarPartida({"cantidadJugadores": 2, "jugadores": [
        {"nombre": "A", "color": Color.ROJO}, {"nombre": "A", "color": Color.AZUL}]})
    assert not exito and "repetidos" in mensaje and g.partidaActual is None


def test_cancelar_la_seleccion_de_colores_descarta_la_partida():
    g = GameManager()
    g.iniciarPartida()
    g.configurarCantidadJugadores(2)
    g.cancelarSeleccionColores()
    assert g.partidaActual is None


def test_seleccionar_ficha_juega_solo_fichas_propias(gm_en_juego, dado):
    g = gm_en_juego
    dado(6)
    g.lanzarDado()
    ajena = g.partidaActual.jugadores[1].fichas[0]
    assert g.seleccionarFicha(ajena) is False
    propia = g.partidaActual.jugadores[0].fichas[0]
    assert g.seleccionarFicha(propia) is True and not propia.enBase


def test_pausar_y_reanudar(gm_en_juego):
    g = gm_en_juego
    g.pausarPartida()
    assert g.partidaActual.estado == "PAUSADA"
    g.reanudarPartida()
    assert g.partidaActual.estado == "EN_CURSO"


def test_consultar_reglas_trae_las_seis_secciones():
    texto = GameManager().consultarReglas()
    secciones = [linea.split(".")[0] for linea in texto.splitlines() if linea[:1].isdigit()]
    assert secciones == ["1", "2", "3", "4", "5", "6"]


def test_volver_de_reglas_y_de_estadisticas(gm_en_juego):
    g = gm_en_juego
    assert g.volverDeReglas() is True
    assert "Turnos jugados" in g.verEstadisticas()
    assert g.volver() is True
    assert GameManager().volverDeReglas() is False


def test_reiniciar_vuelve_a_la_configuracion(gm_en_juego):
    g = gm_en_juego
    g.confirmarReinicio()
    assert g.partidaActual.estado == "CONFIGURACION" and g.partidaActual.jugadores == []


def test_cancelar_reinicio_salida_y_guardado_no_cambian_la_partida(gm_en_juego):
    g = gm_en_juego
    partida = g.partidaActual
    g.cancelarReinicio()
    g.cancelarSalida()
    g.cancelarGuardado()
    assert g.partidaActual is partida and partida.estado == "EN_CURSO"


def test_volver_al_menu_pide_confirmacion_solo_con_partida_activa(gm_en_juego):
    g = gm_en_juego
    assert g.volverAlMenuPrinicipal() is True and g.partidaActual is not None
    g.confirmarSalida()
    assert g.partidaActual is None
    assert g.volverAlMenuPrinicipal() is False


def test_guardar_y_salir_y_reanudar_la_partida_guardada(gm_en_juego):
    g = gm_en_juego
    ubicar(g.partidaActual.jugadores[0].fichas[0], 12)
    g.pausarPartida()
    exito, mensaje = g.confirmarGuardado()
    assert exito and "correctamente" in mensaje and g.partidaActual is None
    exito, mensaje = g.reanudarPartidaGuardada()
    assert exito and g.partidaActual.estado == "EN_CURSO"
    assert g.partidaActual.jugadores[0].fichas[0].posicion == 12


def test_reanudar_una_partida_elegida_entre_varias(crear_partida):
    g = GameManager()
    g.partidaActual = crear_partida(2)
    g.guardarYSalir()
    g.partidaActual = crear_partida(4)
    g.guardarYSalir()
    exito, _ = g.reanudarPartidaGuardada(1)                         # la anterior a la última
    assert exito and len(g.partidaActual.jugadores) == 2
    assert g.reanudarPartidaGuardada(0)[0] and len(g.partidaActual.jugadores) == 4
    assert not g.reanudarPartidaGuardada(2)[0]


def test_reanudar_sin_partida_guardada():
    assert GameManager().reanudarPartidaGuardada() == (False, "No existe ninguna partida guardada.")


def test_finalizar_partida(gm_en_juego):
    g = gm_en_juego
    g.finalizarPartida()
    assert g.partidaActual.estado == "FINALIZADA"


# ============================= PersistenciaDeDatos ===========================

@pytest.fixture
def persistencia(tmp_path):
    """PersistenciaDeDatos que escribe en una carpeta temporal, no en la real."""
    return PersistenciaDeDatos(str(tmp_path / "guardadas" / "partida.json"))


def test_guardar_crea_la_carpeta_y_el_archivo(persistencia, crear_partida):
    ok, msg = persistencia.guardarPartida(crear_partida(2))
    assert ok and "correctamente" in msg
    assert persistencia.existePartidaGuardada()
    with open(persistencia.rutaArchivo, encoding="utf-8") as f:
        guardadas = json.load(f)["partidas"]
    assert [d["estado"] for d in guardadas.values()] == ["EN_CURSO"]


def test_se_pueden_guardar_varias_partidas(persistencia, crear_partida):
    persistencia.guardarPartida(crear_partida(2))
    persistencia.guardarPartida(crear_partida(3))
    assert len(persistencia.cargarPartida(0)[0].jugadores) == 3      # la más reciente primero
    assert len(persistencia.cargarPartida(1)[0].jugadores) == 2


def test_volver_a_guardar_una_partida_actualiza_su_entrada(persistencia, crear_partida):
    p = crear_partida(2)
    persistencia.guardarPartida(p)
    ubicar(p.jugadores[0].fichas[0], 9)
    persistencia.guardarPartida(p)
    assert persistencia.cargarPartida(1)[0] is None                  # sigue habiendo una sola
    cargada = persistencia.cargarPartida()[0]
    assert cargada.jugadores[0].fichas[0].posicion == 9
    ubicar(cargada.jugadores[0].fichas[1], 4)                       # una partida cargada también
    persistencia.guardarPartida(cargada)
    assert persistencia.cargarPartida(1)[0] is None


def test_cargar_un_numero_que_no_existe(persistencia, crear_partida):
    persistencia.guardarPartida(crear_partida(2))
    partida, msg = persistencia.cargarPartida(5)
    assert partida is None and "No existe" in msg


def test_guardar_y_cargar_devuelve_la_misma_partida(persistencia, crear_partida, dado):
    p = crear_partida(4)
    ubicar(p.jugadores[1].fichas[0], 40)
    ubicar(p.jugadores[2].fichas[3], 55)
    ubicar(p.jugadores[3].fichas[1], 58)
    dado(5)
    p.lanzarDado()
    persistencia.guardarPartida(p)
    cargada, msg = persistencia.cargarPartida()
    assert cargada is not None and "exitosamente" in msg
    original, copia = p.guardar(), cargada.guardar()
    original.pop("tiempoTranscurrido"), copia.pop("tiempoTranscurrido")
    assert copia == original
    # El tablero cargado tiene las mismas fichas en los mismos casilleros
    assert [len(c) for c in cargada.tablero.Casilleros] == [len(c) for c in p.tablero.Casilleros]


def test_el_ganador_se_recupera_como_el_mismo_jugador(persistencia, crear_partida):
    p = crear_partida(2)
    for f in p.jugadores[1].fichas:
        ubicar(f, 58)
    p.verificarGanador()
    p.finalizar()
    persistencia.guardarPartida(p)
    cargada, _ = persistencia.cargarPartida()
    assert cargada.ganador is cargada.jugadores[1] and cargada.estado == "FINALIZADA"


def test_cargar_sin_partida_guardada(persistencia):
    assert not persistencia.existePartidaGuardada()
    partida, msg = persistencia.cargarPartida()
    assert partida is None and "No existe" in msg


def test_cargar_un_archivo_corrupto_no_rompe(persistencia):
    os.makedirs(os.path.dirname(persistencia.rutaArchivo))
    with open(persistencia.rutaArchivo, "w", encoding="utf-8") as f:
        f.write("{esto no es json")
    partida, msg = persistencia.cargarPartida()
    assert partida is None and "corrupto" in msg


def test_guardar_en_una_ruta_imposible_informa_el_error(tmp_path, crear_partida):
    archivo = tmp_path / "soy_un_archivo"
    archivo.write_text("x")
    p = PersistenciaDeDatos(str(archivo / "partida.json"))   # carpeta dentro de un archivo
    ok, msg = p.guardarPartida(crear_partida(2))
    assert not ok and "Error" in msg


def test_la_ruta_por_defecto_no_depende_de_la_carpeta_de_ejecucion():
    assert os.path.isabs(PersistenciaDeDatos().rutaArchivo)

