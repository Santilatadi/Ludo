"""
Modulo tablero.py
Representa el tablero de Ludo, administrando las posiciones de las fichas,
la lógica de casillas seguras, barreras, capturas y el cálculo de coordenadas.
"""

from modelos.color import Color
from modelos.ficha import Ficha


class Tablero:
    # El circuito principal consta de 52 casillas (0 a 51).
    TOTAL_CASILLAS_CIRCUITO = 52

    # Casillas de salida en el circuito principal para cada color
    SALIDA_COLOR = {
        Color.ROJO: 0,
        Color.AZUL: 13,
        Color.AMARILLO: 26,
        Color.VERDE: 39
    }

    # Casillas seguras globales en el circuito principal (salidas y estrellas)
    CASILLAS_SEGURAS = [0, 8, 13, 21, 26, 34, 39, 47]

    def __init__(self):
        # Inicializa el tablero preparado para una partida.
        self.inicializar()

    def inicializar(self):
        # Limpia o reinicia el estado interno del tablero.
        self.jugadores = []

    def Actualizar(self, lista_jugadores):
        # Actualiza la referencia de los jugadores activos en el tablero.
        self.jugadores = lista_jugadores

    def obtener_casilla_global(self, ficha: Ficha) -> int:
        # Convierte la posición relativa de una ficha (1 a 51) a la casilla global (0 a 51).
        # Devuelve -1 si está en base, o un valor especial >= 100 si está en el caminito a la meta.
        if ficha.enBase:
            return -1
        if ficha.enMeta:
            return 999
        if ficha.posicion <= 51:
            salida = self.SALIDA_COLOR[ficha.color]
            return (salida + (ficha.posicion - 1)) % self.TOTAL_CASILLAS_CIRCUITO
        else:
            # Posiciones 52 a 57 corresponden al caminito final específico de su color
            return 100 + ficha.posicion

    def puedeMover(self, ficha: Ficha, dado: int) -> bool:
        # Verifica si una ficha puede realizar el movimiento especificado por el dado.
        # Comprueba limites de la meta y presencia de barreras enemigas.
        if ficha.enBase:
            return dado == 6
        if ficha.enMeta:
            return False

        if ficha.posicion + dado > 58:
            return False

        # Comprobación de barreras en la trayectoria
        pos_actual = ficha.posicion
        for paso in range(1, dado + 1):
            pos_intermedia = pos_actual + paso
            if self._hay_barrera_en_posicion(ficha, pos_intermedia):
                return False

        return True

    def _hay_barrera_en_posicion(self, ficha_movida: Ficha, pos_relativa: int) -> bool:
        # Una barrera se forma por 2 o más fichas del MISMO color (distinto al de ficha_movida)
        # en la misma casilla.
        if pos_relativa > 51:
            # En el caminito final de su propio color solo están sus propias fichas, no hay barreras enemigas
            return False

        # Calcular casilla global de esa posición intermedia
        salida = self.SALIDA_COLOR[ficha_movida.color]
        casilla_intermedia = (salida + (pos_relativa - 1)) % self.TOTAL_CASILLAS_CIRCUITO

        # Contar fichas enemigas en esa casilla global
        fichas_enemigas_por_color = {}
        for jug in self.jugadores:
            if jug.color != ficha_movida.color:
                for f in jug.fichas:
                    if not f.enBase and not f.enMeta and f.posicion <= 51:
                        c_global = (self.SALIDA_COLOR[f.color] + (f.posicion - 1)) % self.TOTAL_CASILLAS_CIRCUITO
                        if c_global == casilla_intermedia:
                            fichas_enemigas_por_color[f.color] = fichas_enemigas_por_color.get(f.color, 0) + 1

        # Si algún color enemigo tiene 2 o más fichas en esa casilla, hay una barrera
        for cantidad in fichas_enemigas_por_color.values():
            if cantidad >= 2:
                return True

        return False

    def sacarFicha(self, ficha: Ficha):
        # Saca una ficha de la base colocándola en la posición inicial 1.
        if ficha.enBase:
            ficha.salirBase()
            # Verificar si al salir captura una ficha enemiga
            self.verificarCaptura(ficha)

    def moverFicha(self, ficha: Ficha, dado: int) -> bool:
        # Mueve la ficha la cantidad de casillas indicada por el dado.
        # Realiza capturas y comprobación de meta si corresponde.
        if not self.puedeMover(ficha, dado):
            return False

        if ficha.enBase and dado == 6:
            self.sacarFicha(ficha)
            return True

        ficha.mover(dado)
        self.verificarCaptura(ficha)
        self.verificarMeta(ficha)
        return True

    def verificarCaptura(self, ficha: Ficha):
        # Comprueba si la ficha movida cayó en una casilla ocupada por una ficha rival.
        # Si no es casilla segura, captura la ficha rival enviándola a la base.
        if ficha.enBase or ficha.enMeta or ficha.posicion > 51:
            return

        casilla_global = self.obtener_casilla_global(ficha)

        # Si es casilla segura (estrellas o salidas), no hay capturas
        if casilla_global in self.CASILLAS_SEGURAS:
            return

        for jug in self.jugadores:
            if jug.color != ficha.color:
                for f_rival in jug.fichas:
                    if not f_rival.enBase and not f_rival.enMeta and f_rival.posicion <= 51:
                        c_rival = self.obtener_casilla_global(f_rival)
                        if c_rival == casilla_global:
                            # ¡Captura confirmada! Se envía la ficha rival a su base.
                            self.enviarFichaABase(f_rival)

    def enviarFichaABase(self, ficha: Ficha):
        # Regresa la ficha indicada a su base.
        ficha.volverBase()

    def verificarMeta(self, ficha: Ficha) -> bool:
        # Verifica si la ficha ha llegado a la meta (paso 58).
        if ficha.posicion == 58:
            ficha.llegarMeta()
            return True
        return False

    def obtenerMovimientosValidos(self, jugador, dado: int) -> list:
        # Devuelve la lista de fichas del jugador que pueden realizar un movimiento válido.
        movimientos = []
        for ficha in jugador.obtenerFichas():
            if self.puedeMover(ficha, dado):
                movimientos.append(ficha)
        return movimientos
