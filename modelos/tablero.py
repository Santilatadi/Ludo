# Importa el tipo Color para identificar el color de casilleros y fichas
from modelos.color import Color
# Importa la clase Ficha para interactuar con las fichas en el tablero
from modelos.ficha import Ficha


# Representa el tablero de juego de Ludo con sus 52 casillas comunes
class Tablero:
    """Circuito común de 52 casilleros.

    Cada ficha guarda su posición relativa a su propio recorrido (0 base, 1 a 51
    circuito, 52 a 57 pasillo de su color, 58 meta). El casillero del circuito
    donde está se calcula con la salida de su color (inicio) y el recorrido termina
    en el último casillero antes de su pasillo (fin).
    """

    # Constructor: inicializa los casilleros y las posiciones de entrada y salida
    def __init__(self):
        # Lista de 52 casilleros; cada uno guarda las fichas que se encuentran en él
        self.Casilleros = [[] for _ in range(52)]
        # Casilla de salida del circuito para cada color: ROJO (0), AZUL (39), AMARILLO (26), VERDE (13)
        self.inicio = [0, 39, 26, 13]
        # Última casilla antes de doblar al pasillo final para cada color
        self.fin = [50, 37, 24, 11]

    # Reinicia el tablero dejándolo completamente vacío
    def inicializar(self) -> None:
        # Vuelve a crear los 52 casilleros vacíos
        self.Casilleros = [[] for _ in range(52)]
        # Reestablece los puntos de inicio
        self.inicio = [0, 39, 26, 13]
        # Calcula automáticamente el casillero final para cada color (dos antes de su salida)
        self.fin = [(salida - 2) % 52 for salida in self.inicio]

    # Devuelve la lista de fichas de un jugador que pueden moverse según el valor del dado
    def obtenerMovimientosValidos(self, jugador, valorDado: int) -> list[Ficha]:
        # Filtra y devuelve solo las fichas que cumplen la condición de poder moverse
        return [ficha for ficha in jugador.obtenerFichas() if self.puedeMover(ficha, valorDado)]

    # Comprueba si una ficha específica puede realizar un movimiento legal
    def puedeMover(self, ficha: Ficha, valorDado: int) -> bool:
        # Si la ficha ya está en la meta o el dado es 0 o negativo, no se puede mover
        if ficha.enMeta or valorDado <= 0:
            return False
        # Obtiene el índice numérico del color de la ficha (0: ROJO, 1: AZUL, etc.)
        c = list(Color).index(ficha.color)
        # Si la ficha todavía está en la base:
        if ficha.enBase:
            # CU-07: se sale con 6 y solo si no hay una barrera en la casilla de salida.
            # Obtiene las fichas presentes en la casilla de salida de su color
            casillero = self.Casilleros[self.inicio[c]]
            # Para salir se necesita un 6 y que no haya 2 o más fichas del mismo color bloqueando la salida
            return valorDado == 6 and not any(
                sum(1 for f in casillero if f.color == otro.color) >= 2 for otro in casillero)
        # Si para llegar a la meta el dado se pasa del número exacto, el movimiento no es válido
        if self.calcularDestino(ficha, valorDado) != ficha.posicion + valorDado:
            return False    # para entrar a la meta hace falta el número exacto

        # Recorre los casilleros que pisa: ninguna ficha atraviesa ni ocupa una barrera.
        # Calcula la posición actual en el circuito general (de 0 a 51)
        indice = (self.inicio[c] + ficha.posicion - 1) % 52
        # Revisa paso a paso cada casilla por la que avanzará la ficha
        for _ in range(valorDado):
            # Si ya entra al pasillo final de su color, deja de revisar casilleros generales
            if ficha.posicion > 51 or indice == self.fin[c]:
                break       # entra al pasillo de su color, donde no hay barreras rivales
            # Avanza un casillero circularmente (vuelve a 0 después del 51)
            indice = (indice + 1) % 52
            # Toma las fichas que están en esa casilla
            casillero = self.Casilleros[indice]
            # Si hay 2 o más fichas del mismo color, forman una barrera y no se puede pasar
            if any(sum(1 for f in casillero if f.color == otro.color) >= 2 for otro in casillero):
                return False
        # Si pasó todas las comprobaciones, el movimiento es totalmente válido
        return True

    # Calcula la casilla a la que llegaría la ficha con el dado
    def calcularDestino(self, ficha: Ficha, valorDado: int) -> int:
        # Si está en base, solo llega a la casilla 1 si sacó un 6; si no, queda en 0
        if ficha.enBase:
            return 1 if valorDado == 6 else 0
        # Suma los casilleros pero sin superar la meta (58)
        return min(58, ficha.posicion + valorDado)

    # Saca una ficha de la base y la coloca en la casilla de salida
    def sacarFicha(self, ficha: Ficha) -> bool:
        # CU-07: con un 6 la ficha pasa de la base a la casilla de salida de su color.
        # Si la ficha no estaba en base, no hace nada y devuelve False
        if not ficha.enBase:
            return False
        # Cambia el estado de la ficha para que salga de la base
        ficha.salirBase()
        # Agrega la ficha a la casilla de inicio que corresponde a su color
        self.Casilleros[self.inicio[list(Color).index(ficha.color)]].append(ficha)
        # Retorna True indicando que la ficha salió con éxito
        return True

    # Mueve una ficha a su casillero de destino
    def moverFicha(self, ficha: Ficha, destino: int) -> bool:
        # CU-08: lleva la ficha a la posición destino calculada con calcularDestino.
        # Si ya está en la meta, no se puede mover más
        if ficha.enMeta:
            return False
        # Si está en la base, verifica que el destino sea 1 y la saca
        if ficha.enBase:
            return destino == 1 and self.sacarFicha(ficha)
        # Si el destino no es hacia adelante, no se puede mover
        if destino <= ficha.posicion:
            return False
        # Avanza la ficha la cantidad de casilleros de diferencia
        ficha.mover(destino - ficha.posicion)
        # Reacomoda las fichas en la lista del circuito
        self.actualizarPosiciones()
        # Retorna True confirmando el movimiento
        return True

    # Actualiza la ubicación de todas las fichas en los 52 casilleros del circuito
    def actualizarPosiciones(self) -> None:
        # DS N9: vuelve a ubicar cada ficha del circuito según su posición actual;
        # las que volvieron a la base o entraron al pasillo dejan el circuito.
        # Junta todas las fichas que estaban en el circuito
        fichas = [f for casillero in self.Casilleros for f in casillero]
        # Vacía los 52 casilleros para volver a llenarlos
        self.Casilleros = [[] for _ in range(52)]
        # Revisa cada ficha
        for f in fichas:
            # Si no está en base ni en meta y está en el recorrido común (1 a 51):
            if not f.enBase and not f.enMeta and 1 <= f.posicion <= 51:
                # Obtiene el índice del color
                c = list(Color).index(f.color)
                # Calcula el casillero global donde debe colocarse y la añade
                self.Casilleros[(self.inicio[c] + f.posicion - 1) % 52].append(f)

    # Pausa las acciones del tablero
    def pausarTablero(self) -> None:
        pass

    # Reanuda las acciones del tablero
    def reanudarTablero(self) -> None:
        pass

    # Aliases de compatibilidad
    Pausar_Tablero = pausarTablero
    pausar_tablero = pausarTablero
    Reanudar_Tablero = reanudarTablero
    reanudar_tablero = reanudarTablero

    # Revisa si la ficha cayó sobre una ficha rival para capturarla (comerla)
    def verificarCaptura(self, ficha: Ficha) -> bool:
        # CU-09: la ficha que llega a un casillero manda a la base a las rivales.
        # Si está en base, en meta o en el pasillo privado, no hay capturas
        if ficha.enBase or ficha.enMeta or ficha.posicion > 51:
            return False
        # Calcula el casillero global en el que cayó la ficha
        indice = (self.inicio[list(Color).index(ficha.color)] + ficha.posicion - 1) % 52
        # Busca si en ese casillero hay fichas de un color diferente al suyo
        rivales = [f for f in self.Casilleros[indice] if f.color != ficha.color]
        # Para cada ficha rival encontrada en la misma casilla:
        for rival in rivales:
            # Envía la ficha rival de vuelta a su base
            self.enviarFichaABase(rival)
        # Devuelve True si comió al menos a una ficha rival
        return bool(rivales)

    # Manda una ficha de regreso a su base
    def enviarFichaABase(self, ficha: Ficha) -> None:
        # Llama al método de la ficha para volver a base
        ficha.volverBase()
        # Actualiza las posiciones en el tablero
        self.actualizarPosiciones()

    # Comprueba si una ficha ya llegó a la meta final
    def verificarMeta(self, ficha: Ficha) -> bool:
        # Devuelve si el atributo enMeta es True
        return ficha.enMeta

