# Importa Enum para crear un conjunto de valores fijos o constantes
from enum import Enum


# Define la clase Color que contiene los cuatro colores del juego de Ludo
class Color(Enum):
    ROJO = "ROJO"          # Representa el color rojo
    AZUL = "AZUL"          # Representa el color azul
    AMARILLO = "AMARILLO"  # Representa el color amarillo
    VERDE = "VERDE"        # Representa el color verde

