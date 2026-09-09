"""
Modulo partida.py
Representa una partida concreta de Ludo, administrando a los jugadores, el turno actual,
el estado del dado, las reglas de lanzamientos adicionales (sacar un 6) y la regla
de penalización por obtener tres 6 consecutivos.
"""

import random
from modelos.color import Color
from modelos.jugador import Jugador
from modelos.tablero import Tablero


class Partida:

    def __init__(self):
        # Inicializa una estructura de partida vacía
        self.tablero = Tablero()
        self.dado = 0
        self.cantidadJugadores = 2
        self.estado = "NO_INICIADA"  # Estados: NO_INICIADA, EN_CURSO, PAUSADA, FINALIZADA
        self.coloresDisponibles = Color.obtener_todos()
        self.jugadores = []
        self.ganador = None
        self.turnoActual = 0
        self.consecutivoSeis = 0
        self.dado_lanzado = False
        self.esperando_movimiento = False
        self.mensaje_estado = "Lanza el dado para comenzar tu turno."

    def configurarCantidadJugadores(self, cantidad: int) -> bool:
        # Configura la cantidad de jugadores permitidos (entre 2 y 4).
        if 2 <= cantidad <= 4:
            self.cantidadJugadores = cantidad
            return True
        return False

    def obtenerColoresDisponibles(self) -> list:
        # Devuelve la lista de colores que aún no han sido asignados a un jugador.
        colores_ocupados = [j.color for j in self.jugadores]
        return [c for c in Color.obtener_todos() if c not in colores_ocupados]

    def validarColor(self, color: Color) -> bool:
        # Comprueba si un color específico está disponible para ser seleccionado.
        return color in self.obtenerColoresDisponibles()

    def asignarColor(self, jugador: Jugador, color: Color) -> bool:
        # Asigna un color al jugador si el color está disponible.
        if self.validarColor(color):
            jugador.asignarColor(color)
            return True
        return False

    def todosLosColoresAsignados(self) -> bool:
        # Comprueba si todos los jugadores creados tienen un color válido y único.
        if len(self.jugadores) != self.cantidadJugadores:
            return False
        colores = [j.color for j in self.jugadores]
        return len(colores) == len(set(colores))

    def establecerPrimerTurno(self):
        # Selecciona aleatoriamente o fija el primer jugador que comenzará la partida.
        self.turnoActual = 0
        self.consecutivoSeis = 0
        self.dado_lanzado = False
        self.esperando_movimiento = False

    def iniciar(self):
        # Inicializa la partida, coloca las fichas en la base y establece el primer turno.
        self.tablero.inicializar()
        self.tablero.Actualizar(self.jugadores)
        self.establecerPrimerTurno()
        self.estado = "EN_CURSO"
        jugador_inicial = self.obtenerJugadorActual()
        self.mensaje_estado = f"¡Comienza la partida! Turno de {jugador_inicial.nombre}."

    def obtenerJugadorActual(self) -> Jugador:
        # Devuelve el objeto Jugador al que le corresponde el turno actual.
        if 0 <= self.turnoActual < len(self.jugadores):
            return self.jugadores[self.turnoActual]
        return None

    def generarDado(self) -> int:
        # Alias para generar el número del dado.
        return random.randint(1, 6)

    def tirarDado(self) -> int:
        # Lanza el dado de forma aleatoria (1 a 6) y aplica las reglas correspondientes.
        if self.dado_lanzado:
            return self.dado

        self.dado = random.randint(1, 6)
        self.dado_lanzado = True
        jugador = self.obtenerJugadorActual()

        # Control de tres 6 consecutivos
        if self.dado == 6:
            self.consecutivoSeis += 1
            if self.consecutivoSeis == 3:
                # Regla de los 3 seis: pierde el turno inmediatamente
                self.mensaje_estado = f"¡3 seis consecutivos! {jugador.nombre} pierde el turno."
                self.consecutivoSeis = 0
                self.dado_lanzado = False
                self.esperando_movimiento = False
                self.siguienteTurno()
                return 6
        else:
            self.consecutivoSeis = 0

        # Obtener movimientos válidos para este tiro
        movimientos = self.obtenerMovimientosValidos()

        if len(movimientos) == 0:
            self.mensaje_estado = f"{jugador.nombre} sacó un {self.dado} pero no tiene movimientos válidos."
            self.dado_lanzado = False
            self.esperando_movimiento = False
            self.consecutivoSeis = 0
            self.siguienteTurno()
        else:
            self.esperando_movimiento = True
            self.mensaje_estado = f"{jugador.nombre} sacó un {self.dado}. Selecciona una ficha para mover."

        return self.dado

    def obtenerMovimientosValidos(self) -> list:
        # Devuelve la lista de fichas que el jugador actual puede mover con el resultado del dado.
        jugador = self.obtenerJugadorActual()
        if not jugador or not self.dado_lanzado:
            return []
        return self.tablero.obtenerMovimientosValidos(jugador, self.dado)

    def moverFicha(self, ficha) -> bool:
        # Ejecuta el movimiento de la ficha seleccionada por el jugador actual.
        jugador = self.obtenerJugadorActual()
        movimientos = self.obtenerMovimientosValidos()

        if ficha not in movimientos:
            return False

        # Mover la ficha en el tablero
        exito = self.tablero.moverFicha(ficha, self.dado)
        if not exito:
            return False

        # Comprobar si el jugador ha ganado la partida
        if self.identificarGanador():
            self.finalizar()
            return True

        # Determinar si el jugador repite turno (sacó un 6) o pasa al siguiente
        if self.dado == 6 and self.consecutivoSeis < 3:
            self.mensaje_estado = f"¡Sacaste un 6! {jugador.nombre} vuelve a tirar el dado."
            self.dado_lanzado = False
            self.esperando_movimiento = False
        else:
            self.consecutivoSeis = 0
            self.dado_lanzado = False
            self.esperando_movimiento = False
            self.siguienteTurno()

        return True

    def siguienteTurno(self):
        # Avanza el turno al siguiente jugador de la lista.
        if len(self.jugadores) > 0:
            self.turnoActual = (self.turnoActual + 1) % len(self.jugadores)
            jugador_siguiente = self.obtenerJugadorActual()
            self.mensaje_estado = f"Turno de {jugador_siguiente.nombre}. ¡Lanza el dado!"

    def sacarFicha(self):
        # Intenta sacar una ficha de la base si la primera ficha disponible puede salir.
        movimientos = self.obtenerMovimientosValidos()
        for f in movimientos:
            if f.enBase:
                return self.moverFicha(f)
        return False

    def identificarGanador(self) -> bool:
        # Revisa si algún jugador ha llevado sus 4 fichas a la meta.
        for jug in self.jugadores:
            if jug.todasLasFichasEnMeta():
                self.ganador = jug
                return True
        return False

    def finalizar(self):
        # Finaliza la partida estableciendo su estado como FINALIZADA.
        self.estado = "FINALIZADA"
        if self.ganador:
            self.mensaje_estado = f"¡Felicidades! {self.ganador.nombre} ha ganado el Ludo."

    def cancelarSeleccionColores(self):
        # Reinicia la selección de colores.
        pass

    def cancelarPartida(self):
        # Cancela la partida activa y restablece el estado.
        self.estado = "NO_INICIADA"
        self.jugadores = []
        self.ganador = None

    def conservarEstado(self):
        # Permite preservar el estado en memoria para pausar o consultar reglas.
        pass

    def guardar(self):
        # Delegado de guardado.
        pass

    def a_diccionario(self) -> dict:
        # Convierte el estado completo de la partida a un diccionario para guardar en JSON.
        return {
            "cantidadJugadores": self.cantidadJugadores,
            "estado": self.estado,
            "turnoActual": self.turnoActual,
            "dado": self.dado,
            "consecutivoSeis": self.consecutivoSeis,
            "dado_lanzado": self.dado_lanzado,
            "esperando_movimiento": self.esperando_movimiento,
            "mensaje_estado": self.mensaje_estado,
            "ganador": self.ganador.nombre if self.ganador else None,
            "jugadores": [j.a_diccionario() for j in self.jugadores]
        }

    @classmethod
    def desde_diccionario(cls, datos: dict):
        # Reconstruye una partida desde un diccionario de datos JSON.
        partida = cls()
        partida.cantidadJugadores = datos["cantidadJugadores"]
        partida.estado = datos["estado"]
        partida.turnoActual = datos["turnoActual"]
        partida.dado = datos["dado"]
        partida.consecutivoSeis = datos["consecutivoSeis"]
        partida.dado_lanzado = datos["dado_lanzado"]
        partida.esperando_movimiento = datos["esperando_movimiento"]
        partida.mensaje_estado = datos.get("mensaje_estado", "")

        partida.jugadores = [Jugador.desde_diccionario(j_datos) for j_datos in datos["jugadores"]]
        partida.tablero.inicializar()
        partida.tablero.Actualizar(partida.jugadores)

        nombre_ganador = datos.get("ganador")
        if nombre_ganador:
            for j in partida.jugadores:
                if j.nombre == nombre_ganador:
                    partida.ganador = j
                    break

        return partida
