from modelos.color import Color
from modelos.ficha import Ficha


class Jugador:

    def __init__(self, nombre: str = "", color: Color = None):
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

    def seleccionarFicha(self, ficha: Ficha) -> Ficha:
        # CU-08 A3: solo se puede elegir una ficha propia.
        return ficha if ficha in self.fichas else None

    def tieneMovimientosValidos(self, valorDado: int, tablero) -> bool:
        return any(tablero.puedeMover(ficha, valorDado) for ficha in self.fichas)

    def todasLasFichasEnMeta(self) -> bool:
        return all(ficha.enMeta for ficha in self.fichas)

    def confirmarAccion(self) -> bool:
        # CU-11, CU-12 y CU-14: el jugador acepta la acción que se le consultó.
        return True

    def cancelarAccion(self) -> bool:
        # El jugador rechaza la acción: la partida sigue sin cambios.
        return False

    def visualizarEstadisticas(self) -> str:
        # CU-15: resumen de un jugador para la pantalla de estadísticas.
        en_meta = sum(1 for ficha in self.fichas if ficha.enMeta)
        return f"{self.nombre}: {self.movimientos} movimientos, {self.puntaje} puntos, {en_meta}/4 fichas en meta"
