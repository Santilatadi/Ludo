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


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def ubicar(ficha, posicion):
    """Pone una ficha en una posición de su recorrido sin pasar por las reglas.

    0 = base, 1 a 51 = circuito, 52 a 57 = pasillo final, 58 = meta.
    Sirve para armar a mano la situación del tablero que queremos probar.
    """
    ficha.posicion = posicion
    ficha.enBase = posicion == 0
    ficha.enMeta = posicion == 58
    return ficha


def casilla_global(color, posicion):
    """Casilla del circuito (0 a 51) donde cae una ficha de ese color en esa posición."""
    return (Tablero.SALIDA_COLOR[color] + posicion - 1) % 52


def posicion_para_casilla(color, casilla):
    """Inverso de casilla_global: qué posición tiene que tener una ficha de ese
    color para estar parada en esa casilla del circuito."""
    return (casilla - Tablero.SALIDA_COLOR[color]) % 52 + 1


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
def tablero(rojo, azul):
    """Tablero con dos jugadores (rojo y azul), todas las fichas en la base."""
    t = Tablero()
    t.Actualizar([rojo, azul])
    return t


@pytest.fixture
def crear_partida():
    """Fábrica de partidas iniciadas.

    Uso: crear_partida(2) o crear_partida(4, bots=True).
    """
    def _crear(cantidad=2, bots=False):
        partida = Partida()
        partida.configurarCantidadJugadores(cantidad)
        colores = Color.obtener_todos()[:cantidad]
        partida.jugadores = [
            Jugador(f"J{i + 1}", color, es_bot=bots) for i, color in enumerate(colores)
        ]
        partida.iniciar()
        return partida
    return _crear


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
