"""
Modulo persistencia.py
Sistema centralizado de persistencia de partidas en formato JSON (CU-14, CU-16).
Gestiona almacenamiento organizado, IDs únicos persistentes, actualización automática
sin duplicados y migración de versiones anteriores.
"""

import json
import os
import uuid
import time
from datetime import datetime
from modelos.partida import Partida
from logica.reglas import Reglas


class Persistencia:

    def __init__(self, ruta_archivo: str = None):
        # Directorio base y archivo centralizado de partidas
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if ruta_archivo is None:
            self.directorio_guardado = os.path.join(base_dir, "partidas_guardadas")
            self.rutaArchivo = os.path.join(self.directorio_guardado, "partidas.json")
        else:
            self.rutaArchivo = os.path.abspath(ruta_archivo)
            self.directorio_guardado = os.path.dirname(self.rutaArchivo)

        # Migrar automáticamente archivos sueltos anteriores al formato centralizado
        self._migrar_archivos_antiguos()

    def _cargar_contenedor(self) -> dict:
        # Lee el contenedor centralizado de partidas desde el archivo JSON
        if not os.path.exists(self.rutaArchivo):
            return {"version": 1, "ultima_actualizacion": "", "partidas": {}}

        try:
            with open(self.rutaArchivo, "r", encoding="utf-8") as f:
                datos = json.load(f)

            if isinstance(datos, dict) and "partidas" in datos:
                return datos
            # Retrocompatibilidad si el archivo contenía una partida suelta
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
        # Serializa y escribe el contenedor centralizado en el archivo JSON
        try:
            if not os.path.exists(self.directorio_guardado):
                os.makedirs(self.directorio_guardado, exist_ok=True)

            with open(self.rutaArchivo, "w", encoding="utf-8") as f:
                json.dump(contenedor, f, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False

    def _migrar_archivos_antiguos(self):
        # Migra archivos individuales previos (partida_*.json) al contenedor centralizado
        if not os.path.exists(self.directorio_guardado):
            return

        archivos = [
            f for f in os.listdir(self.directorio_guardado)
            if f.endswith(".json") and f != os.path.basename(self.rutaArchivo)
        ]
        if not archivos:
            return

        contenedor = self._cargar_contenedor()
        partidas_dict = contenedor.setdefault("partidas", {})
        migrados = False

        for arch in archivos:
            ruta = os.path.join(self.directorio_guardado, arch)
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    datos = json.load(f)

                if isinstance(datos, dict) and "partidas" in datos:
                    for k, v in datos["partidas"].items():
                        if k not in partidas_dict:
                            partidas_dict[k] = v
                            migrados = True
                elif isinstance(datos, dict) and "jugadores" in datos:
                    id_p = datos.get("id_partida") or arch.replace(".json", "")
                    datos["id_partida"] = id_p
                    if id_p not in partidas_dict:
                        partidas_dict[id_p] = datos
                        migrados = True

                # Eliminar archivo suelto migrado para mantener la carpeta limpia
                os.remove(ruta)
            except Exception:
                continue

        if migrados:
            contenedor["ultima_actualizacion"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self._guardar_contenedor(contenedor)

    def guardarPartida(self, partida: Partida, nombre_archivo: str = None) -> tuple[bool, str]:
        # Guarda o actualiza la partida en el almacén centralizado JSON.
        # Si la partida ya existe (mismo id_partida), se sobrescriben sus datos evitando duplicados.
        if not partida:
            return False, "No hay partida activa para guardar."

        try:
            contenedor = self._cargar_contenedor()
            partidas_dict = contenedor.setdefault("partidas", {})

            # Garantizar ID único y persistente
            if not getattr(partida, "id_partida", None):
                partida.id_partida = f"partida_{int(time.time())}_{uuid.uuid4().hex[:6]}"

            id_p = partida.id_partida
            ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            datos_partida = partida.a_diccionario()
            datos_partida["id_partida"] = id_p
            datos_partida["fecha_guardado"] = ahora_str

            # Si ya existía, preservar la fecha original de creación
            if id_p in partidas_dict and "fecha_creacion" in partidas_dict[id_p]:
                datos_partida["fecha_creacion"] = partidas_dict[id_p]["fecha_creacion"]
                mensaje_retorno = "Partida actualizada con el estado más reciente."
            else:
                datos_partida["fecha_creacion"] = ahora_str
                mensaje_retorno = "Partida guardada exitosamente."

            # Sobrescribe el registro existente o crea uno nuevo bajo su ID único
            datos_partida["timestamp_guardado"] = time.time()
            partidas_dict[id_p] = datos_partida
            contenedor["ultima_actualizacion"] = ahora_str

            if self._guardar_contenedor(contenedor):
                return True, mensaje_retorno
            else:
                return False, "Error al escribir en el archivo de guardado."

        except Exception as e:
            return False, f"Error al guardar la partida: {str(e)}"

    def listar_partidas_guardadas(self) -> list[dict]:
        # Devuelve la lista de partidas guardadas ordenadas de más reciente a más antigua
        contenedor = self._cargar_contenedor()
        partidas_dict = contenedor.get("partidas", {})
        if not partidas_dict:
            return []

        lista_info = []
        for id_p, datos in partidas_dict.items():
            fecha = datos.get("fecha_guardado", "")
            if not fecha:
                fecha = datos.get("fecha_creacion", "")

            lista_info.append({
                "id": id_p,
                "id_partida": id_p,
                "archivo": id_p,  # Retrocompatibilidad con selectores de UI
                "ruta": self.rutaArchivo,
                "fecha": fecha,
                "timestamp": datos.get("timestamp_guardado", 0),
                "jugadores": datos.get("jugadores", []),
                "turnoActual": datos.get("turnoActual", 0),
                "estado": datos.get("estado", "EN_CURSO"),
                "turnos_totales": datos.get("turnos_totales", 1),
                "datos": datos
            })

        # Ordenar cronológicamente por timestamp o fecha de guardado (más reciente primero)
        def obtener_clave_orden(item):
            ts = item.get("timestamp", 0)
            if ts:
                return ts
            f_str = item.get("fecha", "")
            try:
                return datetime.strptime(f_str, "%d/%m/%Y %H:%M:%S").timestamp()
            except Exception:
                return 0

        lista_info.sort(key=obtener_clave_orden, reverse=True)
        return lista_info

    def cargarPartida(self, identificador: str = None) -> tuple[Partida, str]:
        # Carga una partida del archivo centralizado según su id_partida o devuelve la más reciente
        contenedor = self._cargar_contenedor()
        partidas_dict = contenedor.get("partidas", {})

        if not partidas_dict:
            return None, "No existe ninguna partida guardada."

        datos_partida = None

        if not identificador:
            # Cargar la más reciente
            lista = self.listar_partidas_guardadas()
            if lista:
                datos_partida = lista[0]["datos"]
        else:
            # Buscar por ID único directamente
            if identificador in partidas_dict:
                datos_partida = partidas_dict[identificador]
            else:
                # Búsqueda por coincidencia de atributos internos o nombres
                for id_p, d in partidas_dict.items():
                    if id_p == identificador or d.get("id_partida") == identificador or d.get("archivo_guardado") == identificador:
                        datos_partida = d
                        break

        # Como respaldo secundario para archivos sueltos externos
        if not datos_partida and identificador and os.path.exists(identificador):
            try:
                with open(identificador, "r", encoding="utf-8") as f:
                    datos_partida = json.load(f)
            except Exception:
                pass

        if not datos_partida:
            return None, f"No se encontró la partida con identificador: {identificador}"

        try:
            partida = Partida.desde_diccionario(datos_partida)
            return partida, "Partida cargada exitosamente."
        except Exception as e:
            return None, f"No se pudo cargar la partida: {str(e)}"

    def existe_partida_guardada(self) -> bool:
        # Comprueba si hay al menos una partida guardada en el sistema
        return len(self.listar_partidas_guardadas()) > 0

    def eliminarPartida(self, identificador: str) -> tuple[bool, str]:
        # Elimina una partida del registro centralizado por su id_partida
        if not identificador:
            return False, "Identificador de partida no especificado."

        contenedor = self._cargar_contenedor()
        partidas_dict = contenedor.get("partidas", {})

        id_encontrado = None
        if identificador in partidas_dict:
            id_encontrado = identificador
        else:
            for id_p, d in partidas_dict.items():
                if id_p == identificador or d.get("id_partida") == identificador or d.get("archivo_guardado") == identificador:
                    id_encontrado = id_p
                    break

        if not id_encontrado:
            # Verificación de respaldo para archivo físico si fuese el caso
            ruta_suelta = os.path.join(self.directorio_guardado, identificador) if not os.path.isabs(identificador) else identificador
            if os.path.exists(ruta_suelta):
                try:
                    os.remove(ruta_suelta)
                    return True, "Partida eliminada correctamente."
                except Exception as e:
                    return False, f"Error al eliminar partida: {str(e)}"
            return False, "La partida no existe o ya fue eliminada."

        del partidas_dict[id_encontrado]
        contenedor["ultima_actualizacion"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if self._guardar_contenedor(contenedor):
            return True, "Partida eliminada correctamente del registro central."
        else:
            return False, "Error al actualizar el almacén de partidas."

    def obtener_info_partida(self, identificador: str = None) -> dict:
        # Devuelve la información cruda de una partida o la más reciente
        if identificador:
            contenedor = self._cargar_contenedor()
            return contenedor.get("partidas", {}).get(identificador)
        partidas = self.listar_partidas_guardadas()
        return partidas[0]["datos"] if partidas else None

    def obtenerReglas(self) -> list:
        # Devuelve las reglas del juego
        return Reglas.obtener_texto_reglas()
