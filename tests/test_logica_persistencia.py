"""Pruebas de GestorPartida, Estadisticas, Reglas y Persistencia."""

import json
import os

import pytest

from logica.estadisticas import Estadisticas
from logica.gestor_partida import GestorPartida
from logica.reglas import Reglas
from modelos.color import Color
from modelos.jugador import Jugador
from modelos.partida import Partida
from persistencia.persistencia import Persistencia
from conftest import ubicar


# ============================= GestorPartida =================================

@pytest.fixture
def gestor_en_juego(crear_partida):
    g = GestorPartida()
    g.partidaActual = crear_partida(2)
    g.estado = "JUEGO"
    return g


def test_gestor_arranca_en_el_menu_sin_partida():
    g = GestorPartida()
    assert g.estado == "MENU" and g.partidaActual is None


def test_configurar_cantidad_crea_la_partida():
    g = GestorPartida()
    assert g.configurarCantidadJugadores(3)
    assert g.partidaActual.cantidadJugadores == 3
    assert not g.configurarCantidadJugadores(7)


def test_iniciar_sin_jugadores_da_error_y_no_cambia_de_estado():
    g = GestorPartida()
    assert g.iniciarPartida() is False
    assert g.estado == "MENU" and g.mensaje_error


def test_iniciar_con_jugadores_validos_pasa_al_juego():
    g = GestorPartida()
    g.configurarCantidadJugadores(2)
    g.partidaActual.jugadores = [Jugador("A", Color.ROJO), Jugador("B", Color.AZUL)]
    assert g.iniciarPartida() is True
    assert g.estado == "JUEGO" and g.partidaActual.estado == "EN_CURSO"


def test_pausar_y_reanudar(gestor_en_juego):
    g = gestor_en_juego
    g.pausar()
    assert g.estado == "PAUSA"
    g.reanudar()
    assert g.estado == "JUEGO"


def test_pausar_solo_desde_el_juego_y_reanudar_solo_desde_la_pausa():
    g = GestorPartida()
    g.pausar()
    assert g.estado == "MENU"
    g.reanudar()
    assert g.estado == "MENU"


@pytest.mark.parametrize("origen", ["MENU", "JUEGO", "PAUSA", "FINAL"])
def test_reglas_vuelve_a_la_pantalla_de_origen(origen):
    g = GestorPartida()
    g.estado = origen
    g.consultarReglas()
    assert g.estado == "REGLAS"
    g.volverDeReglas()
    assert g.estado == origen


@pytest.mark.parametrize("origen", ["JUEGO", "FINAL"])
def test_estadisticas_vuelve_a_la_pantalla_de_origen(origen):
    g = GestorPartida()
    g.estado = origen
    g.consultarEstadisticas()
    assert g.estado == "ESTADISTICAS"
    g.volverDeEstadisticas()
    assert g.estado == origen


def test_seleccionar_ficha_solo_funciona_en_el_juego(gestor_en_juego, dado):
    g = gestor_en_juego
    dado(6)
    g.partidaActual.tirarDado()
    ficha = g.partidaActual.jugadores[0].fichas[0]
    g.estado = "PAUSA"
    assert g.seleccionarFicha(ficha) is False and ficha.enBase
    g.estado = "JUEGO"
    assert g.seleccionarFicha(ficha) is True and not ficha.enBase


def test_cancelar_partida_vuelve_al_menu(gestor_en_juego):
    g = gestor_en_juego
    g.cancelarPartida()
    assert g.estado == "MENU" and g.partidaActual is None


# ============================= Estadisticas ==================================

def test_contadores_de_estadisticas():
    e = Estadisticas()
    e.registrar_movimiento("Ana")
    e.registrar_movimiento("Ana")
    e.registrar_movimiento("Beto")
    e.registrar_turno()
    e.registrar_captura()
    assert e.movimientos_por_jugador == {"Ana": 2, "Beto": 1}
    assert e.turnos_totales == 1 and e.capturas_totales == 1


def test_tiempo_formateado_en_minutos_y_segundos(monkeypatch):
    monkeypatch.setattr("logica.estadisticas.time.time", lambda: 1000.0)
    e = Estadisticas()
    monkeypatch.setattr("logica.estadisticas.time.time", lambda: 1000.0 + 342)
    assert e.obtener_tiempo_formateado() == "05:42"


def test_puntaje_base_0_camino_posicion_meta_100():
    j = Jugador("Ana", Color.ROJO)
    ubicar(j.fichas[1], 20)
    ubicar(j.fichas[2], 58)
    assert Estadisticas().calcular_puntaje(j) == 0 + 20 + 100 + 0


def test_resumen_de_estadisticas(crear_partida):
    p = crear_partida(2)
    e = Estadisticas()
    e.registrar_movimiento("J1")
    resumen = e.obtener_resumen(p)
    assert set(resumen) == {"tiempo", "turnos_totales", "jugadores", "ganador"}
    assert resumen["jugadores"][0] == {"nombre": "J1", "color": "ROJO", "movimientos": 1, "puntaje": 0}
    assert resumen["ganador"] == "Ninguno"


# ============================= Reglas ========================================

def test_las_reglas_tienen_las_seis_secciones():
    lineas = Reglas.obtener_texto_reglas()
    secciones = [l for l in lineas if l[:1].isdigit()]
    assert [s.split(".")[0] for s in secciones] == ["1", "2", "3", "4", "5", "6"]


# ============================= Persistencia ==================================

@pytest.fixture
def persistencia(tmp_path):
    """Persistencia que escribe en una carpeta temporal, no en la real."""
    return Persistencia(str(tmp_path / "guardadas" / "partida.json"))


def test_guardar_crea_la_carpeta_y_el_archivo(persistencia, crear_partida):
    ok, msg = persistencia.guardarPartida(crear_partida(2))
    assert ok and "correctamente" in msg
    assert persistencia.existe_partida_guardada()
    with open(persistencia.rutaArchivo, encoding="utf-8") as f:
        assert json.load(f)["estado"] == "EN_CURSO"


def test_guardar_y_cargar_devuelve_la_misma_partida(persistencia, crear_partida, dado):
    p = crear_partida(4)
    p.jugadores[3].es_bot = True
    ubicar(p.jugadores[1].fichas[0], 40)
    dado(5)
    p.tirarDado()
    persistencia.guardarPartida(p)
    cargada, msg = persistencia.cargarPartida()
    assert cargada is not None and "exitosamente" in msg
    assert cargada.a_diccionario() == p.a_diccionario()


def test_cargar_sin_partida_guardada(persistencia):
    assert not persistencia.existe_partida_guardada()
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
    p = Persistencia(str(archivo / "partida.json"))   # carpeta dentro de un archivo
    ok, msg = p.guardarPartida(crear_partida(2))
    assert not ok and "Error" in msg


@pytest.mark.xfail(reason="RIESGO PARA EL .EXE: la ruta por defecto es relativa, depende de "
                          "desde qué carpeta se ejecute el juego (PyInstaller lo cambia).")
def test_la_ruta_por_defecto_no_depende_de_la_carpeta_de_ejecucion():
    assert os.path.isabs(Persistencia().rutaArchivo)
