"""
Modulo gestor_partida.py
Representa la clase Game Manager / Dios exigida por las especificaciones.
Se encarga de coordinar las acciones generales del sistema y administrar los estados
de la aplicación (MENU, CONFIGURACION, JUEGO, PAUSA, REGLAS, ESTADISTICAS, FINAL).
"""

from modelos.partida import Partida


class GestorPartida:

    def __init__(self):
        # Estado inicial de la aplicación: MENÚ PRINCIPAL
        self.estado = "MENU"
        self.estado_anterior = "MENU"
        self.partidaActual = None
        self.mensaje_error = ""

    def iniciarPartida(self) -> bool:
        # Inicia formalmente una nueva partida si la configuración es correcta.
        if not self.partidaActual:
            self.partidaActual = Partida()

        if self.partidaActual.todosLosColoresAsignados():
            self.partidaActual.iniciar()
            self.estado = "JUEGO"
            return True
        else:
            self.mensaje_error = "Debes asignar nombres y colores válidos a todos los jugadores."
            return False

    def configurarCantidadJugadores(self, cantidad: int) -> bool:
        # Modifica la cantidad de jugadores de la partida actual (entre 2 y 4).
        if not self.partidaActual:
            self.partidaActual = Partida()
        return self.partidaActual.configurarCantidadJugadores(cantidad)

    def seleccionarColores(self):
        # Cambia al flujo de selección de colores.
        pass

    def cancelarSeleccionColores(self):
        # Cancela la selección de colores y regresa la partida a estado inicial.
        if self.partidaActual:
            self.partidaActual.cancelarSeleccionColores()

    def cancelarPartida(self):
        # Cancela la partida activa y regresa al Menú Principal.
        if self.partidaActual:
            self.partidaActual.cancelarPartida()
        self.partidaActual = None
        self.estado = "MENU"

    def seleccionarFicha(self, ficha) -> bool:
        # Pide a la partida mover la ficha seleccionada por el usuario.
        if self.partidaActual and self.estado == "JUEGO":
            return self.partidaActual.moverFicha(ficha)
        return False

    def consultarReglas(self):
        # Guarda el estado actual y muestra la pantalla de reglas.
        self.estado_anterior = self.estado
        self.estado = "REGLAS"

    def volverDeReglas(self):
        # Regresa exactamente al estado en el que se encontraba antes de ver las reglas.
        self.estado = self.estado_anterior

    def consultarEstadisticas(self):
        # Guarda el estado actual y muestra las estadísticas.
        self.estado_anterior = self.estado
        self.estado = "ESTADISTICAS"

    def volverDeEstadisticas(self):
        # Regresa del menú de estadísticas al estado anterior.
        self.estado = self.estado_anterior

    def pausar(self):
        # Pausa la partida activa y muestra la pantalla de pausa.
        if self.estado == "JUEGO":
            self.estado = "PAUSA"

    def reanudar(self):
        # Reanuda la partida desde la pantalla de pausa.
        if self.estado == "PAUSA":
            self.estado = "JUEGO"
