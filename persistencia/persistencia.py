"""
Modulo persistencia.py
Encargado del guardado y carga de partidas en formato JSON (CU-14, CU-16).
Permite persistir el estado completo de la partida y recuperar partidas guardadas.
"""

import json
import os
from modelos.partida import Partida
from logica.reglas import Reglas


class Persistencia:

    def __init__(self, ruta_archivo: str = "partidas_guardadas/partida_guardada.json"):
        # Inicializa la clase con la ruta por defecto del archivo JSON.
        self.rutaArchivo = ruta_archivo

    def guardarPartida(self, partida: Partida) -> tuple[bool, str]:
        # Guarda el estado actual de la partida en un archivo JSON.
        # Devuelve una tupla (éxito: bool, mensaje: str).
        try:
            # Crear la carpeta de destino si no existe
            directorio = os.path.dirname(self.rutaArchivo)
            if directorio and not os.path.exists(directorio):
                os.makedirs(directorio, exist_ok=True)

            datos = partida.a_diccionario()
            with open(self.rutaArchivo, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)

            return True, "Partida guardada correctamente."
        except Exception as e:
            return False, f"Error al guardar la partida: {str(e)}"

    def cargarPartida(self) -> tuple[Partida, str]:
        # Carga una partida guardada previamente desde el archivo JSON.
        # Devuelve una tupla (objeto Partida o None, mensaje: str).
        if not os.path.exists(self.rutaArchivo):
            return None, "No existe ninguna partida guardada."

        try:
            with open(self.rutaArchivo, "r", encoding="utf-8") as f:
                datos = json.load(f)

            partida = Partida.desde_diccionario(datos)
            return partida, "Partida cargada exitosamente."
        except Exception as e:
            return None, f"No se pudo cargar la partida: El archivo está corrupto o es inaccesible. ({str(e)})"

    def existe_partida_guardada(self) -> bool:
        # Comprueba si existe un archivo de partida guardada.
        return os.path.exists(self.rutaArchivo)

    def obtenerReglas(self) -> list:
        # Devuelve las reglas del juego.
        return Reglas.obtener_texto_reglas()
