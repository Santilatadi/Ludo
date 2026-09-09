"""
Modulo color.py
Representa los colores disponibles para los jugadores en el juego Ludo.
"""

from enum import Enum


class Color(Enum):
    # Definición de los cuatro colores principales del Ludo
    ROJO = "ROJO"
    AZUL = "AZUL"
    VERDE = "VERDE"
    AMARILLO = "AMARILLO"

    @classmethod
    def obtener_todos(cls):
        # Esta función devuelve la lista de todos los colores del juego.
        return [cls.ROJO, cls.AZUL, cls.VERDE, cls.AMARILLO]

    def obtener_rgb(self):
        # Devuelve el valor del color en formato RGB (Rojo, Verde, Azul)
        # para ser utilizado por Pygame al dibujar en la pantalla.
        valores_rgb = {
            Color.ROJO: (220, 50, 50),       # Rojo vibrante
            Color.AZUL: (40, 120, 220),      # Azul cobalto
            Color.VERDE: (40, 180, 80),      # Verde esmeralda
            Color.AMARILLO: (240, 190, 40)   # Amarillo dorado
        }
        return valores_rgb[self]

    def obtener_rgb_claro(self):
        # Devuelve una versión más clara del color, útil para bases y caminitos.
        valores_rgb_claro = {
            Color.ROJO: (255, 200, 200),
            Color.AZUL: (200, 225, 255),
            Color.VERDE: (200, 245, 210),
            Color.AMARILLO: (255, 245, 190)
        }
        return valores_rgb_claro[self]

    def obtener_nombre_mostrable(self):
        # Devuelve el nombre del color como una cadena legible.
        return self.value
