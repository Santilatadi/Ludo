from modelos.color import Color


class Ficha:

    def __init__(self, color: Color = None):
        self.color = color
        self.posicion = 0
        self.enBase = True
        self.enMeta = False

    def obtenerPosicion(self) -> int:
        return self.posicion

    def salirBase(self) -> None:
        self.enBase = False
        self.posicion = 1
        self.enMeta = False

    def mover(self, cantidad: int) -> None:
        if self.enBase or self.enMeta:
            return
        nueva_posicion = self.posicion + cantidad
        if nueva_posicion <= 58:
            self.posicion = nueva_posicion
            if self.posicion == 58:
                self.llegarMeta()

    def volverBase(self) -> None:
        self.posicion = 0
        self.enBase = True
        self.enMeta = False

    def llegarMeta(self) -> None:
        self.posicion = 58
        self.enBase = False
        self.enMeta = True
