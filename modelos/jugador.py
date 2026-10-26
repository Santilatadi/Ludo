# Importa el tipo Color para asignárselo al jugador
from modelos.color import Color
# Importa la clase Ficha para crear las fichas que le pertenecen al jugador
from modelos.ficha import Ficha


# Representa a un jugador de la partida (humano o computadora)
class Jugador:

    # Constructor: inicializa el nombre, el color y las 4 fichas del jugador
    def __init__(self, nombre: str = "", color: Color = None):
        # Guarda el nombre del jugador
        self.nombre = nombre
        # Guarda el color elegido por el jugador
        self.color = color
        # Crea una lista con las 4 fichas del jugador con su respectivo color
        self.fichas = [Ficha(color) for _ in range(4)]
        # Contador de movimientos realizados durante la partida
        self.movimientos = 0
        # Puntos acumulados en la partida
        self.puntaje = 0

    # Asigna un nuevo color al jugador y actualiza el color de sus 4 fichas
    def asignarColor(self, color: Color) -> None:
        # Cambia el color del jugador
        self.color = color
        # Recorre cada una de sus fichas
        for ficha in self.fichas:
            # Le asigna el nuevo color a la ficha
            ficha.color = color

    # Devuelve el color actual del jugador
    def getColor(self) -> Color:
        # Retorna el color
        return self.color

    # Devuelve la lista con las 4 fichas del jugador
    def obtenerFichas(self) -> list[Ficha]:
        # Retorna la lista de fichas
        return self.fichas

    # Permite elegir una ficha asegurándose de que le pertenezca a este jugador
    def seleccionarFicha(self, ficha: Ficha) -> Ficha:
        # CU-08 A3: solo se puede elegir una ficha propia.
        # Si la ficha está en su lista la devuelve, si no devuelve None
        return ficha if ficha in self.fichas else None

    # Comprueba si el jugador tiene al menos una ficha que pueda moverse con el dado
    def tieneMovimientosValidos(self, valorDado: int, tablero) -> bool:
        # Revisa si alguna ficha puede moverse en el tablero con el valor sacado
        return any(tablero.puedeMover(ficha, valorDado) for ficha in self.fichas)

    # Comprueba si las 4 fichas del jugador ya llegaron a la meta
    def todasLasFichasEnMeta(self) -> bool:
        # Devuelve True solo si todas las fichas tienen enMeta en True
        return all(ficha.enMeta for ficha in self.fichas)

    # Simula la confirmación de una acción por parte del jugador
    def confirmarAccion(self) -> bool:
        # CU-11, CU-12 y CU-14: el jugador acepta la acción que se le consultó.
        # Devuelve True indicando que acepta
        return True

    # Simula la cancelación o rechazo de una acción
    def cancelarAccion(self) -> bool:
        # El jugador rechaza la acción: la partida sigue sin cambios.
        # Devuelve False indicando que rechaza
        return False

    # Genera un texto con las estadísticas de la partida de este jugador
    def visualizarEstadisticas(self) -> str:
        # CU-15: resumen de un jugador para la pantalla de estadísticas.
        # Cuenta cuántas fichas del jugador están actualmente en la meta
        en_meta = sum(1 for ficha in self.fichas if ficha.enMeta)
        # Arma y devuelve una cadena de texto con el resumen
        return f"{self.nombre}: {self.movimientos} movimientos, {self.puntaje} puntos, {en_meta}/4 fichas en meta"

