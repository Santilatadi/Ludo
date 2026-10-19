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


class Persistencia:

    def __init__(self, rutaArchivo: str = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if rutaArchivo is None:
            self.rutaArchivo = os.path.join(base_dir, "partidas_guardadas", "partidas.json")
        else:
            self.rutaArchivo = os.path.abspath(rutaArchivo)

    def _get_directorio_guardado(self) -> str:
        return os.path.dirname(self.rutaArchivo)

    def _cargar_contenedor(self) -> dict:
        if not os.path.exists(self.rutaArchivo):
            return {"version": 1, "ultima_actualizacion": "", "partidas": {}}
        try:
            with open(self.rutaArchivo, "r", encoding="utf-8") as f:
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

    def _guardar_contenedor(self, contenedor: dict) -> bool:
        try:
            d_guardado = self._get_directorio_guardado()
            if not os.path.exists(d_guardado):
                os.makedirs(d_guardado, exist_ok=True)
            with open(self.rutaArchivo, "w", encoding="utf-8") as f:
                json.dump(contenedor, f, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False

    def guardarPartida(self, partida: Partida = None) -> None:
        if not partida:
            return

        try:
            contenedor = self._cargar_contenedor()
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
            self._guardar_contenedor(contenedor)
        except Exception:
            pass

    def cargarPartida(self, identificador: str = None) -> Partida:
        contenedor = self._cargar_contenedor()
        partidas_dict = contenedor.get("partidas", {})
        if not partidas_dict:
            return None

        if identificador and identificador in partidas_dict:
            datos_partida = partidas_dict[identificador]
        else:
            lista = self._listar_partidas()
            if not lista:
                return None
            datos_partida = lista[0]["datos"]
        return self._reconstruir_partida(datos_partida)

    def _reconstruir_partida(self, datos: dict) -> Partida:
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

    def obtenerReglas(self) -> str:
        lineas = Reglas.obtener_texto_reglas()
        if isinstance(lineas, list):
            return "\n".join(lineas)
        return str(lineas)

    def existePartidaGuardada(self) -> bool:
        return len(self._listar_partidas()) > 0

    def _listar_partidas(self) -> list[dict]:
        contenedor = self._cargar_contenedor()
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
                "ruta": self.rutaArchivo,
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

    def _eliminar_partida(self, identificador: str) -> bool:
        if not identificador:
            return False
        contenedor = self._cargar_contenedor()
        partidas_dict = contenedor.get("partidas", {})
        if identificador in partidas_dict:
            del partidas_dict[identificador]
            contenedor["ultima_actualizacion"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            return self._guardar_contenedor(contenedor)
        return False

    def __getattr__(self, name):
        if name == "listar_partidas_guardadas":
            return self._listar_partidas
        if name == "eliminarPartida":
            def _eliminar(identificador):
                exito = self._eliminar_partida(identificador)
                return exito, ("Partida eliminada." if exito else "Error al eliminar.")
            return _eliminar
        if name == "existe_partida_guardada":
            return self.existePartidaGuardada
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
