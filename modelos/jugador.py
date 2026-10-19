from modelos.color import Color
from modelos.ficha import Ficha


class Jugador:

    def __init__(self, nombre: str = "", color: Color = None, *args, **kwargs):
        self.nombre = nombre
        self.color = color
        self.fichas = [Ficha(color) for _ in range(4)]
        self.movimientos = 0
        self.puntaje = 0

    def asignarColor(self, color: Color) -> None:
        self.color = color
        for ficha in self.fichas:
            ficha.color = color

    def getColor(self) -> Color:
        return self.color

    def obtenerFichas(self) -> list[Ficha]:
        return self.fichas

    def seleccionarFicha(self, ficha=None) -> Ficha:
        if ficha is not None:
            if isinstance(ficha, int) and 0 <= ficha < len(self.fichas):
                return self.fichas[ficha]
            if ficha in self.fichas:
                return ficha
        return self.fichas[0] if self.fichas else None

    def tieneMovimientosValidos(self, dado: int = 0, tablero=None) -> bool:
        if tablero is not None and dado:
            return any(tablero.puedeMover(f, dado) for f in self.fichas)
        return any(not f.enMeta for f in self.fichas)

    def todasLasFichasEnMeta(self) -> bool:
        return all(ficha.enMeta for ficha in self.fichas)

    def confirmarAccion(self) -> None:
        pass

    def cancelarAccion(self) -> None:
        pass

    def visualizarEstadisticas(self) -> None:
        pass

    def __getattr__(self, name):
        if name == "es_bot":
            return "(Bot)" in self.nombre or self.nombre.startswith("Bot")
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
