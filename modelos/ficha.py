"""
Modulo ficha.py
Representa cada una de las fichas del juego Ludo.
Cada jugador cuenta con exactamente 4 fichas de su respectivo color.
"""

from modelos.color import Color


class Ficha:
    # La posición representa el avance de la ficha:
    # 0 -> En la base (enBase = True)
    # 1 a 52 -> Casillas del circuito principal (avance según su recorrido)
    # 53 a 57 -> Caminito final hacia la meta
    # 58 -> Meta alcanzada (enMeta = True)

    def __init__(self, id_ficha: int, color: Color):
        # Inicializa una nueva ficha con su número identificador (1 a 4) y su color.
        self.id_ficha = id_ficha
        self.color = color
        self.posicion = 0
        self.enBase = True
        self.enMeta = False

    def salirBase(self):
        # Esta función saca la ficha de la base y la coloca en la casilla de salida (paso 1).
        # Modifica los atributos enBase y posicion.
        self.enBase = False
        self.posicion = 1
        self.enMeta = False

    def volverBase(self):
        # Regresa la ficha a la base (por ejemplo cuando es capturada por un rival).
        # Restablece la posición a 0 y enBase a True.
        self.posicion = 0
        self.enBase = True
        self.enMeta = False

    def mover(self, cantidad: int):
        # Avanza la ficha una cantidad determinada de casillas.
        # Recibe la cantidad de pasos (resultado del dado).
        # Modifica la posición y verifica si alcanzó la meta.
        if self.enBase or self.enMeta:
            return

        nueva_posicion = self.posicion + cantidad
        # La meta se alcanza exactamente al llegar al paso 58
        if nueva_posicion <= 58:
            self.posicion = nueva_posicion
            if self.posicion == 58:
                self.llegarMeta()

    def llegarMeta(self):
        # Marca la ficha como finalizada en la meta.
        self.posicion = 58
        self.enBase = False
        self.enMeta = True

    def obtenerPosicion(self) -> int:
        # Devuelve el valor de la posición actual de la ficha.
        return self.posicion

    def a_diccionario(self) -> dict:
        # Convierte el estado de la ficha a un diccionario para guardar en JSON.
        return {
            "id_ficha": self.id_ficha,
            "color": self.color.name,
            "posicion": self.posicion,
            "enBase": self.enBase,
            "enMeta": self.enMeta
        }

    @classmethod
    def desde_diccionario(cls, datos: dict):
        # Reconstruye un objeto Ficha desde un diccionario guardado.
        color_enum = Color[datos["color"]]
        ficha = cls(datos["id_ficha"], color_enum)
        ficha.posicion = datos["posicion"]
        ficha.enBase = datos["enBase"]
        ficha.enMeta = datos["enMeta"]
        return ficha
