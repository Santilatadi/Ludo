from modelos.color import Color


class Ficha:

    def __init__(self, color: Color = None):
        self.color = color
        self.posicion = 0        # 0 base, 1 a 51 circuito, 52 a 57 pasillo, 58 meta
        self.enBase = True
        self.enMeta = False

    def obtenerPosicion(self) -> int:
        return self.posicion

    def salirBase(self) -> None:
        self.enBase = False
        self.enMeta = False
        self.posicion = 1

    def mover(self, cantidad: int) -> None:
        if self.enBase or self.enMeta or self.posicion + cantidad > 58:
            return
        self.posicion += cantidad
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
