"""
Modulo persistencia_de_datos.py
Clase PersistenciaDeDatos del diagrama de clases: guarda y recupera partidas en
JSON (CU-14) y obtiene el texto de las reglas (CU-06).

Se pueden guardar varias partidas al mismo tiempo. cargarPartida(numero) devuelve
la partida guardada número `numero` (0 = la más reciente). Volver a guardar una
partida que se cargó o que ya se guardó actualiza su misma entrada del archivo.
"""

import json
import os
import time
import weakref
from datetime import datetime

from modelos.color import Color
from modelos.jugador import Jugador
from modelos.partida import Partida

_CARPETA = os.path.dirname(os.path.abspath(__file__))

# Entrada del archivo que corresponde a cada partida ya guardada o cargada en esta
# ejecución (así no se agrega ningún atributo a Partida que no esté en el diagrama).
_ENTRADAS = weakref.WeakKeyDictionary()


class PersistenciaDeDatos:

    def __init__(self, rutaArchivo: str = None):
        self.rutaArchivo = rutaArchivo or os.path.join(
            os.path.dirname(_CARPETA), "partidas_guardadas", "partidas.json")

    def guardarPartida(self, partida: Partida) -> tuple[bool, str]:
        if partida is None:
            return False, "Error al guardar la partida: no hay partida activa."
        try:
            with open(self.rutaArchivo, "r", encoding="utf-8") as archivo:
                partidas = json.load(archivo).get("partidas") or {}
        except (OSError, ValueError, AttributeError):
            partidas = {}

        ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        clave = _ENTRADAS.get(partida) or f"partida_{time.time_ns()}"
        datos = partida.guardar()
        datos["fecha_guardado"] = ahora
        datos["momento_guardado"] = time.time()
        partidas[clave] = datos
        contenido = {"version": 2, "ultima_actualizacion": ahora, "partidas": partidas}
        try:
            os.makedirs(os.path.dirname(self.rutaArchivo), exist_ok=True)
            with open(self.rutaArchivo, "w", encoding="utf-8") as archivo:
                json.dump(contenido, archivo, indent=4, ensure_ascii=False)
        except OSError as error:
            # CU-14 A 4.a: se informa el error y la partida sigue en curso.
            return False, f"Error al guardar la partida: {error}"
        _ENTRADAS[partida] = clave
        return True, "Partida guardada correctamente."

    def cargarPartida(self, numero: int = 0) -> tuple[Partida, str]:
        # numero 0 = la última guardada. CU-14 A 7.a (no hay) y 8.a (archivo dañado).
        if not os.path.exists(self.rutaArchivo):
            return None, "No existe ninguna partida guardada."
        try:
            with open(self.rutaArchivo, "r", encoding="utf-8") as archivo:
                contenido = json.load(archivo)
            partidas = contenido.get("partidas") or {}
            if contenido.get("partida"):            # archivo de una sola partida (versión 1)
                partidas = {"partida_guardada": contenido["partida"], **partidas}
            claves = sorted(partidas, key=lambda k: partidas[k].get("momento_guardado")
                            or partidas[k].get("timestamp_guardado", 0), reverse=True)
            if not 0 <= numero < len(claves):
                return None, "No existe ninguna partida guardada."
            datos = partidas[claves[numero]]

            partida = Partida()
            partida.tablero.inicializar()
            partida.cantidadJugadores = datos["cantidadJugadores"]
            partida.estado = datos.get("estado", "EN_CURSO")
            partida.turnoActual = datos.get("turnoActual", 0)
            partida.dado = datos.get("dado", 0)
            partida._seisConsecutivos = datos.get("seisConsecutivos", datos.get("consecutivoSeis", 0))
            partida.turnosJugados = datos.get("turnosJugados", 1)
            partida.tiempoTranscurrido = datos.get("tiempoTranscurrido", 0)

            for datos_jugador in datos["jugadores"]:
                jugador = Jugador(datos_jugador["nombre"], Color[datos_jugador["color"]])
                jugador.movimientos = datos_jugador.get("movimientos", 0)
                jugador.puntaje = datos_jugador.get("puntaje", 0)
                # Cada ficha vuelve a su lugar con los mismos pasos del juego:
                # sale de la base y avanza hasta la posición guardada.
                for ficha, datos_ficha in zip(jugador.obtenerFichas(), datos_jugador["fichas"]):
                    if datos_ficha["posicion"] >= 1:
                        partida.tablero.sacarFicha(ficha)
                        partida.tablero.moverFicha(ficha, datos_ficha["posicion"])
                partida.jugadores.append(jugador)

            partida.obtenerColoresDisponibles()
            partida.obtenerJugadorActual()
            partida.ganador = next((j for j in partida.jugadores if j.nombre == datos.get("ganador")), None)
            # Se guarda desde la pausa: al cargarla el juego se retoma.
            if partida.estado in ("PAUSADA", "EN_CURSO"):
                partida.reanudar()
            _ENTRADAS[partida] = claves[numero]
            return partida, "Partida cargada exitosamente."
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            return None, "No se pudo cargar la partida: el archivo está corrupto o es inaccesible."

    def obtenerReglas(self) -> str:
        # CU-06: las reglas se leen de persistencia/reglas.txt (A: error al cargarlas).
        try:
            with open(os.path.join(_CARPETA, "reglas.txt"), "r", encoding="utf-8") as archivo:
                return archivo.read()
        except OSError:
            return ""

    def existePartidaGuardada(self) -> bool:
        # Un archivo que existe pero no se puede leer cuenta como guardado:
        # cargarPartida() informa luego que está dañado (CU-14 A 8.a).
        if not os.path.exists(self.rutaArchivo):
            return False
        try:
            with open(self.rutaArchivo, "r", encoding="utf-8") as archivo:
                contenido = json.load(archivo)
            return bool(contenido.get("partidas") or contenido.get("partida"))
        except (OSError, ValueError, AttributeError):
            return True
