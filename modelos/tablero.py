from modelos.color import Color
from modelos.ficha import Ficha


class Tablero:
    """Circuito común de 52 casilleros.

    Cada ficha guarda su posición relativa a su propio recorrido (0 base, 1 a 51
    circuito, 52 a 57 pasillo de su color, 58 meta). El casillero del circuito
    donde está se calcula con la salida de su color (inicio) y el recorrido termina
    en el último casillero antes de su pasillo (fin).
    """

    def __init__(self):
        # Casilleros[i] = fichas que están en el casillero i del circuito
        self.Casilleros = [[] for _ in range(52)]
        # Una entrada por color, en el orden de Color (ROJO, AZUL, AMARILLO, VERDE)
        self.inicio = [0, 39, 26, 13]
        self.fin = [50, 37, 24, 11]

    def inicializar(self) -> None:
        self.Casilleros = [[] for _ in range(52)]
        self.inicio = [0, 39, 26, 13]
        self.fin = [(salida - 2) % 52 for salida in self.inicio]

    def obtenerMovimientosValidos(self, jugador, valorDado: int) -> list[Ficha]:
        return [ficha for ficha in jugador.obtenerFichas() if self.puedeMover(ficha, valorDado)]

    def puedeMover(self, ficha: Ficha, valorDado: int) -> bool:
        if ficha.enMeta or valorDado <= 0:
            return False
        c = list(Color).index(ficha.color)
        if ficha.enBase:
            # CU-07: se sale con 6 y solo si no hay una barrera en la casilla de salida.
            casillero = self.Casilleros[self.inicio[c]]
            return valorDado == 6 and not any(
                sum(1 for f in casillero if f.color == otro.color) >= 2 for otro in casillero)
        if self.calcularDestino(ficha, valorDado) != ficha.posicion + valorDado:
            return False    # para entrar a la meta hace falta el número exacto

        # Recorre los casilleros que pisa: ninguna ficha atraviesa ni ocupa una barrera.
        indice = (self.inicio[c] + ficha.posicion - 1) % 52
        for _ in range(valorDado):
            if ficha.posicion > 51 or indice == self.fin[c]:
                break       # entra al pasillo de su color, donde no hay barreras rivales
            indice = (indice + 1) % 52
            casillero = self.Casilleros[indice]
            if any(sum(1 for f in casillero if f.color == otro.color) >= 2 for otro in casillero):
                return False
        return True

    def calcularDestino(self, ficha: Ficha, valorDado: int) -> int:
        if ficha.enBase:
            return 1 if valorDado == 6 else 0
        return min(58, ficha.posicion + valorDado)

    def sacarFicha(self, ficha: Ficha) -> bool:
        # CU-07: con un 6 la ficha pasa de la base a la casilla de salida de su color.
        if not ficha.enBase:
            return False
        ficha.salirBase()
        self.Casilleros[self.inicio[list(Color).index(ficha.color)]].append(ficha)
        return True

    def moverFicha(self, ficha: Ficha, destino: int) -> bool:
        # CU-08: lleva la ficha a la posición destino calculada con calcularDestino.
        if ficha.enMeta:
            return False
        if ficha.enBase:
            return destino == 1 and self.sacarFicha(ficha)
        if destino <= ficha.posicion:
            return False
        ficha.mover(destino - ficha.posicion)
        self.actualizarPosiciones()
        return True

    def actualizarPosiciones(self) -> None:
        # DS N9: vuelve a ubicar cada ficha del circuito según su posición actual;
        # las que volvieron a la base o entraron al pasillo dejan el circuito.
        fichas = [f for casillero in self.Casilleros for f in casillero]
        self.Casilleros = [[] for _ in range(52)]
        for f in fichas:
            if not f.enBase and not f.enMeta and 1 <= f.posicion <= 51:
                c = list(Color).index(f.color)
                self.Casilleros[(self.inicio[c] + f.posicion - 1) % 52].append(f)

    def verificarCaptura(self, ficha: Ficha) -> bool:
        # CU-09: la ficha que llega a un casillero manda a la base a las rivales.
        if ficha.enBase or ficha.enMeta or ficha.posicion > 51:
            return False
        indice = (self.inicio[list(Color).index(ficha.color)] + ficha.posicion - 1) % 52
        rivales = [f for f in self.Casilleros[indice] if f.color != ficha.color]
        for rival in rivales:
            self.enviarFichaABase(rival)
        return bool(rivales)

    def enviarFichaABase(self, ficha: Ficha) -> None:
        ficha.volverBase()
        self.actualizarPosiciones()

    def verificarMeta(self, ficha: Ficha) -> bool:
        return ficha.enMeta
