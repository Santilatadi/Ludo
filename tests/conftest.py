"""
conftest.py
Configuración y herramientas compartidas por todas las pruebas.

pytest carga este archivo automáticamente. Todo lo que se define con
@pytest.fixture queda disponible como parámetro en cualquier prueba.
"""

import os
import sys

import pytest

# Raíz del proyecto (la carpeta que contiene main.py) para poder importar
# modelos, logica, persistencia e interfaz igual que lo hace main.py.
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from modelos.color import Color
from modelos.jugador import Jugador
from modelos.partida import Partida
from modelos.tablero import Tablero

# Tablero sobre el que ubicar() acomoda las fichas (lo fijan las fixtures).
_tablero_activo = None


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def ubicar(ficha, posicion, tablero=None):
    """Pone una ficha en una posición de su recorrido sin pasar por las reglas.

    0 = base, 1 a 51 = circuito, 52 a 57 = pasillo final, 58 = meta.
    Si hay un tablero activo, la ficha queda también en su casillero.
    """
    ficha.posicion = posicion
    ficha.enBase = posicion == 0
    ficha.enMeta = posicion == 58
    tablero = tablero or _tablero_activo
    if tablero is not None:
        for casillero in tablero.Casilleros:
            if ficha in casillero:
                casillero.remove(ficha)
        if 1 <= posicion <= 51:
            tablero.Casilleros[casilla_global(ficha.color, posicion)].append(ficha)
    return ficha


def salida(color):
    """Casillero de salida (posición 1) de un color."""
    return Tablero().inicio[list(Color).index(color)]


def casilla_global(color, posicion):
    """Casilla del circuito (0 a 51) donde cae una ficha de ese color en esa posición."""
    return (salida(color) + posicion - 1) % 52


def posicion_para_casilla(color, casilla):
    """Inverso de casilla_global: qué posición tiene que tener una ficha de ese
    color para estar parada en esa casilla del circuito."""
    return (casilla - salida(color)) % 52 + 1


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def rojo():
    return Jugador("Rojo", Color.ROJO)


@pytest.fixture
def azul():
    return Jugador("Azul", Color.AZUL)


@pytest.fixture
def tablero():
    """Tablero vacío (todas las fichas en la base); ubicar() pone fichas en él."""
    global _tablero_activo
    t = Tablero()
    t.inicializar()
    _tablero_activo = t
    yield t
    _tablero_activo = None


@pytest.fixture
def crear_partida():
    """Fábrica de partidas iniciadas (DS N5: Partida(datosConfiguracion) e iniciar()).

    Uso: crear_partida(2) o crear_partida(4, bots=True). Los bots se llaman "Bot n".
    """
    def _crear(cantidad=2, bots=False):
        global _tablero_activo
        datos = {"cantidadJugadores": cantidad,
                 "jugadores": [{"nombre": f"Bot {i + 1}" if bots else f"J{i + 1}", "color": color}
                               for i, color in enumerate(list(Color)[:cantidad])]}
        partida = Partida(datos)
        assert partida.validarConfiguracion() == ""
        partida.iniciar()
        _tablero_activo = partida.tablero
        return partida
    yield _crear
    _tablero_activo = None


@pytest.fixture
def dado(monkeypatch):
    """Hace que el dado saque los valores que le indiquemos, en orden.

    Uso: dado(6, 6, 3)  -> las próximas tiradas serán 6, 6 y 3.
    Reemplaza random.randint solo dentro de modelos.partida y solo
    durante la prueba (monkeypatch lo restaura al terminar).
    """
    def _fijar(*valores):
        cola = list(valores)

        def falso_randint(a, b):
            if not cola:
                raise AssertionError("La prueba tiró el dado más veces de las previstas")
            return cola.pop(0)

        monkeypatch.setattr("modelos.partida.random.randint", falso_randint)
    return _fijar


@pytest.fixture(autouse=True)
def guardado_en_carpeta_temporal(monkeypatch, tmp_path):
    """El GameManager guarda la partida al iniciarla (CU-04): en las pruebas
    ese guardado va a una carpeta temporal para no tocar partidas_guardadas/."""
    from persistencia.persistencia_de_datos import PersistenciaDeDatos
    import logica.game_manager as game_manager

    ruta = str(tmp_path / "partidas_guardadas" / "partidas.json")

    class PersistenciaTemporal(PersistenciaDeDatos):
        def __init__(self, rutaArchivo=None):
            super().__init__(rutaArchivo or ruta)

    monkeypatch.setattr(game_manager, "PersistenciaDeDatos", PersistenciaTemporal)
