import weakref
from modelos.color import Color
from modelos.ficha import Ficha

_tablero_jugadores = weakref.WeakKeyDictionary()
_COLOR_IDX = {Color.ROJO: 0, Color.AZUL: 1, Color.AMARILLO: 2, Color.VERDE: 3}
_CASILLAS_SEGURAS = {0, 8, 13, 21, 26, 34, 39, 47}


class Tablero:

    def __init__(self):
        self.Casilleros = [[0 for _ in range(4)] for _ in range(52)]
        self.inicio = [0, 13, 26, 39]
        self.fin = [51, 12, 25, 38]
        _tablero_jugadores[self] = []

    def inicializar(self) -> None:
        self.Casilleros = [[0 for _ in range(4)] for _ in range(52)]
        self.inicio = [0, 13, 26, 39]
        self.fin = [51, 12, 25, 38]
        _tablero_jugadores[self] = []

    def obtenerMovimientosValidos(self, jugador, valorDado: int = 0) -> list[Ficha]:
        if not jugador:
            return []
        return [f for f in jugador.obtenerFichas() if self.puedeMover(f, valorDado)]

    def puedeMover(self, ficha: Ficha, valorDado: int = 0) -> bool:
        if ficha.enBase:
            return valorDado == 6
        if ficha.enMeta:
            return False
        if ficha.posicion + valorDado > 58:
            return False

        # Comprobación de barreras directamente en la trayectoria
        pos_actual = ficha.posicion
        idx_color = _COLOR_IDX.get(ficha.color, 0)
        salida_origen = self.inicio[idx_color]
        jugadores = _tablero_jugadores.get(self, [])

        for paso in range(1, valorDado + 1):
            pos_intermedia = pos_actual + paso
            if pos_intermedia <= 51:
                casilla_intermedia = (salida_origen + (pos_intermedia - 1)) % 52
                conteo_por_color = {}
                for jug in jugadores:
                    if jug.color != ficha.color:
                        for f in jug.fichas:
                            if not f.enBase and not f.enMeta and f.posicion <= 51:
                                idx_rival = _COLOR_IDX.get(f.color, 0)
                                c_rival = (self.inicio[idx_rival] + (f.posicion - 1)) % 52
                                if c_rival == casilla_intermedia:
                                    conteo_por_color[f.color] = conteo_por_color.get(f.color, 0) + 1
                if any(cnt >= 2 for cnt in conteo_por_color.values()):
                    return False

        return True

    def calcularDestino(self, ficha: Ficha, valorDado: int = 0) -> int:
        if ficha.enBase:
            return 1 if valorDado == 6 else 0
        return min(58, ficha.posicion + valorDado)

    def sacarFicha(self, ficha: Ficha) -> None:
        if ficha.enBase:
            ficha.salirBase()
            self.verificarCaptura(ficha)

    def moverFicha(self, ficha: Ficha, destino: int = 0) -> None:
        if not ficha:
            return
        if ficha.enBase and destino in (6, 1):
            self.sacarFicha(ficha)
            return

        pasos = destino if destino <= 6 else (destino - ficha.posicion)
        if pasos > 0 and self.puedeMover(ficha, pasos):
            ficha.mover(pasos)
            self.verificarCaptura(ficha)
            self.verificarMeta(ficha)

    def verificarCaptura(self, ficha: Ficha) -> bool:
        if ficha.enBase or ficha.enMeta or ficha.posicion > 51:
            return False

        idx_color = _COLOR_IDX.get(ficha.color, 0)
        c_global = (self.inicio[idx_color] + (ficha.posicion - 1)) % 52
        if c_global in _CASILLAS_SEGURAS:
            return False

        capturo = False
        jugadores = _tablero_jugadores.get(self, [])
        for jug in jugadores:
            if jug.color != ficha.color:
                for f_rival in jug.fichas:
                    if not f_rival.enBase and not f_rival.enMeta and f_rival.posicion <= 51:
                        idx_rival = _COLOR_IDX.get(f_rival.color, 0)
                        c_rival = (self.inicio[idx_rival] + (f_rival.posicion - 1)) % 52
                        if c_rival == c_global:
                            self.enviarFichaABase(f_rival)
                            capturo = True
        return capturo

    def enviarFichaABase(self, ficha: Ficha) -> None:
        ficha.volverBase()

    def verificarMeta(self, ficha: Ficha) -> bool:
        if ficha.posicion == 58:
            ficha.llegarMeta()
            return True
        return False

    def __setattr__(self, name, value):
        if name == "jugadores":
            _tablero_jugadores[self] = value
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name):
        if name == "jugadores":
            return _tablero_jugadores.get(self, [])
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
