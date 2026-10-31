"""
Modulo persistencia_de_datos.py
Clase PersistenciaDeDatos del diagrama de clases: guarda y recupera partidas en
JSON (CU-14) y obtiene el texto de las reglas (CU-06).

Se pueden guardar varias partidas al mismo tiempo. cargarPartida(numero) devuelve
la partida guardada número `numero` (0 = la más reciente). Volver a guardar una
partida que se cargó o que ya se guardó actualiza su misma entrada del archivo.
"""

# Importa json para leer y escribir archivos en formato JSON
import json
# Importa os para manejar rutas y carpetas del sistema operativo
import os
# Importa time para medir tiempos y marcas de hora
import time
# Importa weakref para asociar objetos en memoria sin evitar que se liberen
import weakref
# Importa datetime para formatear la fecha y hora legible
from datetime import datetime

# Importa Color para reconstruir los colores de los jugadores
from modelos.color import Color
# Importa Jugador para reconstruir los objetos Jugador
from modelos.jugador import Jugador
# Importa Partida para crear y cargar la partida
from modelos.partida import Partida

# Guarda la ruta absoluta de la carpeta donde se encuentra este archivo
_CARPETA = os.path.dirname(os.path.abspath(__file__))

# Entrada del archivo que corresponde a cada partida ya guardada o cargada en esta
# ejecución (así no se agrega ningún atributo a Partida que no esté en el diagrama).
_ENTRADAS = weakref.WeakKeyDictionary()


# Clase encargada de guardar y cargar partidas en el disco, y leer las reglas
class PersistenciaDeDatos:

    # Constructor: define la ruta donde se guardará el archivo JSON
    def __init__(self, rutaArchivo: str = None):
        # Si no se indica ruta, usa por defecto "partidas_guardadas/partidas.json"
        self.rutaArchivo = rutaArchivo or os.path.join(
            os.path.dirname(_CARPETA), "partidas_guardadas", "partidas.json")

    # Guarda el estado de la partida actual en el archivo JSON
    def guardarPartida(self, partida: Partida) -> tuple[bool, str]:
        # Si no hay partida activa, no se puede guardar
        if partida is None:
            return False, "Error al guardar la partida: no hay partida activa."
        # Intenta leer las partidas existentes para no borrarlas
        try:
            # Abre el archivo en modo lectura
            with open(self.rutaArchivo, "r", encoding="utf-8") as archivo:
                # Carga el diccionario de partidas guardadas
                partidas = json.load(archivo).get("partidas") or {}
        # Si el archivo no existe o está dañado, empieza con un diccionario vacío
        except (OSError, ValueError, AttributeError):
            partidas = {}

        # Obtiene la fecha y hora actual en formato día/mes/año hora:minutos:segundos
        ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        # Obtiene o genera una clave única para esta partida
        clave = _ENTRADAS.get(partida) or f"partida_{time.time_ns()}"
        # Obtiene el diccionario con los datos del juego
        datos = partida.guardar()
        # Añade la fecha legible al diccionario
        datos["fecha_guardado"] = ahora
        # Añade la marca de tiempo numérica para ordenar cronológicamente
        datos["momento_guardado"] = time.time()
        # Guarda o actualiza los datos bajo esa clave
        partidas[clave] = datos
        # Estructura el contenido con versión y fecha de actualización
        contenido = {"version": 2, "ultima_actualizacion": ahora, "partidas": partidas}
        # Intenta escribir el archivo en el disco
        try:
            # Crea la carpeta contenedora si todavía no existe
            os.makedirs(os.path.dirname(self.rutaArchivo), exist_ok=True)
            # Abre el archivo para escribir con sangría para que sea legible
            with open(self.rutaArchivo, "w", encoding="utf-8") as archivo:
                # Escribe los datos en formato JSON
                json.dump(contenido, archivo, indent=4, ensure_ascii=False)
        # Si ocurre un error de permisos o de disco:
        except OSError as error:
            # CU-14 A 4.a: se informa el error y la partida sigue en curso.
            return False, f"Error al guardar la partida: {error}"
        # Asocia en memoria la partida con su clave
        _ENTRADAS[partida] = clave
        # Retorna True indicando éxito con su mensaje
        return True, "Partida guardada correctamente."

    # Carga una partida guardada previamente desde el archivo JSON
    def cargarPartida(self, numero: int = 0) -> tuple[Partida, str]:
        # numero 0 = la última guardada. CU-14 A 7.a (no hay) y 8.a (archivo dañado).
        # Si el archivo no existe, devuelve error
        if not os.path.exists(self.rutaArchivo):
            return None, "No existe ninguna partida guardada."
        # Intenta abrir y procesar el archivo
        try:
            # Abre el archivo JSON
            with open(self.rutaArchivo, "r", encoding="utf-8") as archivo:
                # Decodifica el JSON a un diccionario de Python
                contenido = json.load(archivo)
            # Extrae el diccionario de partidas
            partidas = contenido.get("partidas") or {}
            # Si el archivo era del formato viejo con una sola partida, la adapta:
            if contenido.get("partida"):            # archivo de una sola partida (versión 1)
                partidas = {"partida_guardada": contenido["partida"], **partidas}
            # Ordena las partidas de más nueva a más vieja según el momento de guardado
            claves = sorted(partidas, key=lambda k: partidas[k].get("momento_guardado")
                            or partidas[k].get("timestamp_guardado", 0), reverse=True)
            # Si el índice pedido está fuera de rango, no existe esa partida
            if not 0 <= numero < len(claves):
                return None, "No existe ninguna partida guardada."
            # Toma los datos de la partida seleccionada
            datos = partidas[claves[numero]]

            # Crea una nueva instancia limpia de Partida
            partida = Partida()
            # Inicializa el tablero
            partida.tablero.inicializar()
            # Restaura la cantidad de jugadores
            partida.cantidadJugadores = datos["cantidadJugadores"]
            # Restaura el estado
            partida.estado = datos.get("estado", "EN_CURSO")
            # Restaura el índice del jugador que tiene el turno
            partida.turnoActual = datos.get("turnoActual", 0)
            # Restaura el valor del dado
            partida.dado = datos.get("dado", 0)
            # Restaura el contador de 6 seguidos
            partida._seisConsecutivos = datos.get("seisConsecutivos", datos.get("consecutivoSeis", 0))
            # Restaura la cantidad de turnos jugados
            partida.turnosJugados = datos.get("turnosJugados", 1)
            # Restaura el tiempo transcurrido
            partida.tiempoTranscurrido = datos.get("tiempoTranscurrido", 0)
            if partida.estado == "EN_CURSO":
                partida._inicioTiempo = time.time()

            # Reconstruye cada jugador con sus datos y fichas
            for datos_jugador in datos["jugadores"]:
                # Crea el jugador con su nombre y su color enum
                jugador = Jugador(datos_jugador["nombre"], Color[datos_jugador["color"]])
                # Restaura la cantidad de movimientos
                jugador.movimientos = datos_jugador.get("movimientos", 0)
                # Restaura el puntaje
                jugador.puntaje = datos_jugador.get("puntaje", 0)
                # Cada ficha vuelve a su lugar con los mismos pasos del juego:
                # sale de la base y avanza hasta la posición guardada.
                for ficha, datos_ficha in zip(jugador.obtenerFichas(), datos_jugador["fichas"]):
                    # Si la ficha no estaba en la base (posición >= 1):
                    if datos_ficha["posicion"] >= 1:
                        # La saca de la base
                        partida.tablero.sacarFicha(ficha)
                        # La mueve hasta su posición guardada
                        partida.tablero.moverFicha(ficha, datos_ficha["posicion"])
                # Agrega el jugador a la partida
                partida.jugadores.append(jugador)

            # Actualiza los colores disponibles
            partida.obtenerColoresDisponibles()
            # Fija al jugador actual
            partida.obtenerJugadorActual()
            # Restaura al ganador si ya había uno
            partida.ganador = next((j for j in partida.jugadores if j.nombre == datos.get("ganador")), None)
            # Se guarda desde la pausa: al cargarla el juego se retoma.
            if partida.estado in ("PAUSADA", "EN_CURSO"):
                # Reanuda el reloj de la partida
                partida.reanudar()
            # Asocia la partida cargada con su clave
            _ENTRADAS[partida] = claves[numero]
            # Retorna la partida restaurada y el mensaje de éxito
            return partida, "Partida cargada exitosamente."
        # Si el archivo está roto o faltan campos obligatorios:
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            return None, "No se pudo cargar la partida: el archivo está corrupto o es inaccesible."

    # Lee y devuelve el texto con las reglas del juego desde reglas.txt
    def obtenerReglas(self) -> str:
        # CU-06: las reglas se leen de persistencia/reglas.txt (A: error al cargarlas).
        try:
            # Abre el archivo reglas.txt
            with open(os.path.join(_CARPETA, "reglas.txt"), "r", encoding="utf-8") as archivo:
                # Lee y retorna el contenido completo
                return archivo.read()
        # Si no lo encuentra o no se puede leer, devuelve texto vacío
        except OSError:
            return ""

    # Comprueba si existe alguna partida guardada en el archivo
    def existePartidaGuardada(self) -> bool:
        # Un archivo que existe pero no se puede leer cuenta como guardado:
        # cargarPartida() informa luego que está dañado (CU-14 A 8.a).
        # Si el archivo no existe en el disco, devuelve False
        if not os.path.exists(self.rutaArchivo):
            return False
        # Intenta abrir el archivo para verificar si contiene partidas
        try:
            with open(self.rutaArchivo, "r", encoding="utf-8") as archivo:
                contenido = json.load(archivo)
            # Retorna True si hay al menos una partida registrada
            return bool(contenido.get("partidas") or contenido.get("partida"))
        # Si está dañado pero existe, cuenta como guardada para que luego avise que está corrupta
        except (OSError, ValueError, AttributeError):
            return True

    def cargar(self):
        partida = self.cargarPartida()
        if partida:
            return partida
        return None

    def cerrarPartida(self):
        if not os.path.exists(self.rutaArchivo):
            return False, "No existe ninguna partida para cerrar."
        return True, "Partida cerrada exitosamente."

    # Solicita confirmación para realizar una acción de persistencia
    def solicitarConfirmacion(self, mensaje: str = "") -> bool:
        # Devuelve True confirmando la acción
        return True

    # Alias con el nombre exacto solicitado
    def solicitarConfimarcion(self, mensaje: str = "") -> bool:
        # Retorna confirmación
        return self.solicitarConfirmacion(mensaje)

    def verificarPartidaGuardada(self) -> bool:
        return self.existePartidaGuardada()
