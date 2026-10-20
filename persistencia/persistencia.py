"""
Modulo persistencia.py
Implementa la clase Persistencia para el guardado y carga de partidas en formato JSON (CU-10, CU-11, CU-12, CU-13).
"""

import json
import os
import time
import uuid
from datetime import datetime
from modelos.color import Color
from modelos.ficha import Ficha
from modelos.jugador import Jugador
from modelos.partida import Partida
from logica.reglas import Reglas


def _cargar_contenedor(ruta: str) -> dict:
    if not os.path.exists(ruta):
        return {"version": 1, "ultima_actualizacion": "", "partidas": {}}
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
        if isinstance(datos, dict) and "partidas" in datos:
            return datos
        elif isinstance(datos, dict) and "jugadores" in datos:
            id_p = datos.get("id_partida") or "partida_importada"
            return {
                "version": 1,
                "ultima_actualizacion": datos.get("fecha_guardado", ""),
                "partidas": {id_p: datos}
            }
        return {"version": 1, "ultima_actualizacion": "", "partidas": {}}
    except Exception:
        return {"version": 1, "ultima_actualizacion": "", "partidas": {}}


def _guardar_contenedor(ruta: str, contenedor: dict) -> bool:
    try:
        directorio = os.path.dirname(ruta)
        if not os.path.exists(directorio):
            os.makedirs(directorio, exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(contenedor, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False


def _reconstruir_partida(datos: dict) -> Partida:
    try:
        partida = Partida()
        partida.id_partida = datos.get("id_partida") or f"partida_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        partida.cantidadJugadores = datos.get("cantidadJugadores", 2)
        partida.estado = datos.get("estado", "EN_CURSO")
        partida.turnoActual = datos.get("turnoActual", 0)
        partida.dado = datos.get("dado", 0)
        partida.turnosJugados = datos.get("turnosJugados", datos.get("turnos_totales", 1))
        partida.tiempoTranscurrido = datos.get("tiempoTranscurrido", 0)

        partida.jugadores = []
        for j_datos in datos.get("jugadores", []):
            color_enum = Color[j_datos["color"]]
            jugador = Jugador(j_datos["nombre"], color_enum)
            jugador.movimientos = j_datos.get("movimientos", 0)
            jugador.puntaje = j_datos.get("puntaje", 0)
            jugador.fichas = []
            for f_datos in j_datos.get("fichas", []):
                f = Ficha(Color[f_datos["color"]])
                f.posicion = f_datos.get("posicion", 0)
                f.enBase = f_datos.get("enBase", True)
                f.enMeta = f_datos.get("enMeta", False)
                jugador.fichas.append(f)
            partida.jugadores.append(jugador)

        partida.tablero.inicializar()
        partida.tablero.jugadores = partida.jugadores
        if partida.jugadores and 0 <= partida.turnoActual < len(partida.jugadores):
            partida.jugadorActual = partida.jugadores[partida.turnoActual]

        nom_ganador = datos.get("ganador")
        if nom_ganador:
            for j in partida.jugadores:
                if j.nombre == nom_ganador:
                    partida.ganador = j
                    break

        return partida
    except Exception:
        return None


def listar_partidas(ruta_archivo: str = None) -> list[dict]:
    if ruta_archivo is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ruta_archivo = os.path.join(base_dir, "partidas_guardadas", "partidas.json")

    contenedor = _cargar_contenedor(ruta_archivo)
    partidas_dict = contenedor.get("partidas", {})
    if not partidas_dict:
        return []

    lista_info = []
    for id_p, datos in partidas_dict.items():
        fecha = datos.get("fecha_guardado") or datos.get("fecha_creacion", "")
        lista_info.append({
            "id": id_p,
            "id_partida": id_p,
            "archivo": id_p,
            "ruta": ruta_archivo,
            "fecha": fecha,
            "timestamp": datos.get("timestamp_guardado", 0),
            "jugadores": datos.get("jugadores", []),
            "turnoActual": datos.get("turnoActual", 0),
            "estado": datos.get("estado", "EN_CURSO"),
            "turnos_totales": datos.get("turnosJugados", datos.get("turnos_totales", 1)),
            "datos": datos
        })

    def _orden(item):
        ts = item.get("timestamp", 0)
        if ts:
            return ts
        try:
            return datetime.strptime(item.get("fecha", ""), "%d/%m/%Y %H:%M:%S").timestamp()
        except Exception:
            return 0

    lista_info.sort(key=_orden, reverse=True)
    return lista_info


def eliminar_partida(ruta_archivo: str = None, identificador: str = None) -> tuple[bool, str]:
    if not identificador:
        return False, "Identificador no válido."
    if ruta_archivo is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ruta_archivo = os.path.join(base_dir, "partidas_guardadas", "partidas.json")

    contenedor = _cargar_contenedor(ruta_archivo)
    partidas_dict = contenedor.get("partidas", {})
    if identificador in partidas_dict:
        del partidas_dict[identificador]
        contenedor["ultima_actualizacion"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        exito = _guardar_contenedor(ruta_archivo, contenedor)
        return exito, ("Partida eliminada." if exito else "Error al guardar los cambios.")
    return False, "Partida no encontrada."


class Persistencia:

    def __init__(self, rutaArchivo: str = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if rutaArchivo is None:
            self.rutaArchivo = os.path.join(base_dir, "partidas_guardadas", "partidas.json")
        else:
            self.rutaArchivo = os.path.abspath(rutaArchivo)

    def guardarPartida(self, partida: Partida = None) -> None:
        if not partida:
            return

        try:
            contenedor = _cargar_contenedor(self.rutaArchivo)
            partidas_dict = contenedor.setdefault("partidas", {})

            id_p = getattr(partida, "id_partida", None)
            if not id_p:
                id_p = f"partida_{int(time.time())}_{uuid.uuid4().hex[:6]}"
                partida.id_partida = id_p

            ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            datos_partida = {
                "id_partida": id_p,
                "cantidadJugadores": partida.cantidadJugadores,
                "estado": partida.estado,
                "turnoActual": partida.turnoActual,
                "dado": partida.dado,
                "turnosJugados": getattr(partida, "turnosJugados", 1),
                "turnos_totales": getattr(partida, "turnosJugados", 1),
                "tiempoTranscurrido": getattr(partida, "tiempoTranscurrido", 0),
                "fecha_guardado": ahora_str,
                "timestamp_guardado": time.time(),
                "ganador": partida.ganador.nombre if partida.ganador else None,
                "jugadores": [
                    {
                        "nombre": j.nombre,
                        "color": j.color.name,
                        "movimientos": getattr(j, "movimientos", 0),
                        "puntaje": getattr(j, "puntaje", 0),
                        "fichas": [
                            {
                                "color": f.color.name,
                                "posicion": f.posicion,
                                "enBase": f.enBase,
                                "enMeta": f.enMeta
                            }
                            for f in j.fichas
                        ]
                    }
                    for j in partida.jugadores
                ]
            }

            if id_p in partidas_dict and "fecha_creacion" in partidas_dict[id_p]:
                datos_partida["fecha_creacion"] = partidas_dict[id_p]["fecha_creacion"]
            else:
                datos_partida["fecha_creacion"] = ahora_str

            partidas_dict[id_p] = datos_partida
            contenedor["ultima_actualizacion"] = ahora_str
            _guardar_contenedor(self.rutaArchivo, contenedor)
        except Exception:
            pass

    def cargarPartida(self, identificador: str = None) -> Partida:
        contenedor = _cargar_contenedor(self.rutaArchivo)
        partidas_dict = contenedor.get("partidas", {})
        if not partidas_dict:
            return None

        if identificador and identificador in partidas_dict:
            datos_partida = partidas_dict[identificador]
        else:
            lista = listar_partidas(self.rutaArchivo)
            if not lista:
                return None
            datos_partida = lista[0]["datos"]
        return _reconstruir_partida(datos_partida)

    def obtenerReglas(self) -> str:
        lineas = Reglas.obtener_texto_reglas()
        if isinstance(lineas, list):
            return "\n".join(lineas)
        return str(lineas)

    def existePartidaGuardada(self) -> bool:
        return len(listar_partidas(self.rutaArchivo)) > 0