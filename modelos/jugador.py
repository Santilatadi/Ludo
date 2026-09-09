"""
Modulo jugador.py
Representa a un jugador dentro de la partida de Ludo.
Cada jugador posee un nombre, un color asignado, exactamente 4 fichas
y una marca que indica si es un Jugador Humano o un Jugador Bot (IA).
"""

from modelos.color import Color
from modelos.ficha import Ficha


class Jugador:

    def __init__(self, nombre: str, color: Color, es_bot: bool = False):
        # Inicializa un jugador con su nombre, color y tipo (Humano o Bot).
        # Crea automáticamente sus 4 fichas correspondientes.
        self.nombre = nombre
        self.color = color
        self.es_bot = es_bot
        self.fichas = [Ficha(i + 1, color) for i in range(4)]

    def obtenerFichas(self):
        # Devuelve la lista de las 4 fichas del jugador.
        return self.fichas

    def asignarColor(self, nuevo_color: Color):
        # Asigna un nuevo color al jugador y actualiza todas sus fichas.
        self.color = nuevo_color
        for ficha in self.fichas:
            ficha.color = nuevo_color

    def getColor(self) -> Color:
        # Devuelve el color asignado a este jugador.
        return self.color

    def todasLasFichasEnMeta(self) -> bool:
        # Comprueba si todas las 4 fichas del jugador han llegado a la meta.
        return all(ficha.enMeta for ficha in self.fichas)

    def puedeMover(self, ficha: Ficha, dado: int, tablero=None) -> bool:
        # Verifica si una ficha especifica del jugador se puede mover con el dado sacado.
        if ficha not in self.fichas:
            return False

        if ficha.enBase:
            return dado == 6

        if ficha.enMeta:
            return False

        if ficha.posicion + dado > 58:
            return False

        if tablero is not None:
            return tablero.puedeMover(ficha, dado)

        return True

    def tieneMovimientosValidos(self, dado: int, tablero=None) -> bool:
        # Comprueba si el jugador tiene al menos una ficha que se pueda mover.
        return any(self.puedeMover(ficha, dado, tablero) for ficha in self.fichas)

    def seleccionarFicha(self, indice_o_ficha):
        # Selecciona una ficha por su objeto o por su índice (0 a 3).
        if isinstance(indice_o_ficha, int):
            if 0 <= indice_o_ficha < len(self.fichas):
                return self.fichas[indice_o_ficha]
        elif isinstance(indice_o_ficha, Ficha):
            if indice_o_ficha in self.fichas:
                return indice_o_ficha
        return None

    def seleccionar_mejor_movimiento(self, movimientos_validos: list, tablero) -> Ficha:
        # Algoritmo de Inteligencia Artificial para los Jugadores Bot.
        # Selecciona la mejor ficha a mover evaluando prioridades estratégicas:
        # 1. Capturar ficha enemiga.
        # 2. Sacar ficha de la base si sacó un 6.
        # 3. Ingresar a la meta o al caminito final seguro.
        # 4. Avanzar la ficha más adelantada hacia la meta.
        if not movimientos_validos:
            return None

        # Prioridad 1: Captura de ficha enemiga
        if tablero is not None:
            for f in movimientos_validos:
                if not f.enBase and not f.enMeta:
                    # Simular casilla global proyectada
                    casilla_proyectada = (tablero.SALIDA_COLOR[f.color] + (f.posicion + 1 - 1)) % 52
                    if casilla_proyectada not in tablero.CASILLAS_SEGURAS:
                        # Comprobar si hay enemigo en esa casilla
                        for jug_rival in tablero.jugadores:
                            if jug_rival.color != self.color:
                                for f_rival in jug_rival.fichas:
                                    if not f_rival.enBase and not f_rival.enMeta and f_rival.posicion <= 51:
                                        c_rival = tablero.obtener_casilla_global(f_rival)
                                        if c_rival == casilla_proyectada:
                                            return f

        # Prioridad 2: Sacar ficha de la base
        for f in movimientos_validos:
            if f.enBase:
                return f

        # Prioridad 3: Ingresar a la meta
        for f in movimientos_validos:
            if f.posicion + 1 > 51:
                return f

        # Prioridad 4: Mover la ficha más avanzada
        movimientos_ordenados = sorted(movimientos_validos, key=lambda x: x.posicion, reverse=True)
        return movimientos_ordenados[0]

    def a_diccionario(self) -> dict:
        # Serializa la información del jugador incluyendo el flag es_bot.
        return {
            "nombre": self.nombre,
            "color": self.color.name,
            "es_bot": self.es_bot,
            "fichas": [ficha.a_diccionario() for ficha in self.fichas]
        }

    @classmethod
    def desde_diccionario(cls, datos: dict):
        # Deserializa un jugador desde un diccionario JSON.
        color_enum = Color[datos["color"]]
        es_bot = datos.get("es_bot", False)
        jugador = cls(datos["nombre"], color_enum, es_bot)
        jugador.fichas = [Ficha.desde_diccionario(f_datos) for f_datos in datos["fichas"]]
        return jugador
