# Importa la clase Color para asignarle un color a cada ficha
from modelos.color import Color


# Representa una ficha individual del juego
class Ficha:

    # Inicializa una nueva ficha con su color y su estado inicial
    def __init__(self, color: Color = None):
        # Guarda el color de la ficha (Rojo, Azul, etc.)
        self.color = color
        # Posición actual: 0 es la base, 1 a 51 el circuito, 52 a 57 el pasillo final y 58 la meta
        self.posicion = 0
        # Indica si la ficha está dentro de la base (empieza siendo verdadero)
        self.enBase = True
        # Indica si la ficha ya llegó a la meta final (empieza siendo falso)
        self.enMeta = False

    # Devuelve el número de casillero donde está la ficha actualmente
    def obtenerPosicion(self) -> int:
        # Retorna el valor numérico de la posición
        return self.posicion

    # Hace que la ficha salga de la base hacia la primera casilla del recorrido
    def salirBase(self) -> None:
        # Ya no está en la base
        self.enBase = False
        # Tampoco está en la meta
        self.enMeta = False
        # Se ubica en la posición 1 (la salida de su recorrido)
        self.posicion = 1

    # Avanza la ficha una cantidad determinada de casilleros
    def mover(self, cantidad: int) -> None:
        # Si la ficha está en base, en meta o se pasaría de la casilla 58, no se puede mover
        if self.enBase or self.enMeta or self.posicion + cantidad > 58:
            # Termina la función sin hacer ningún movimiento
            return
        # Suma los casilleros del dado a la posición actual
        self.posicion += cantidad
        # Si llegó justo a la casilla 58, completa la llegada a la meta
        if self.posicion == 58:
            # Llama a la función que marca la llegada a la meta
            self.llegarMeta()

    # Envía la ficha de regreso a la base (cuando es comida o capturada)
    def volverBase(self) -> None:
        # Vuelve la posición a 0
        self.posicion = 0
        # Marca que ahora está en la base
        self.enBase = True
        # Marca que no está en la meta
        self.enMeta = False

    # Marca la ficha como llegada a la meta final
    def llegarMeta(self) -> None:
        # Fija la posición exacta de la meta (58)
        self.posicion = 58
        # Ya no está en la base
        self.enBase = False
        # Marca que está dentro de la meta
        self.enMeta = True

