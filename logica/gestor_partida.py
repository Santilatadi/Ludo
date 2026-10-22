import weakref
from modelos.partida import Partida
from modelos.ficha import Ficha

_gestor_state = weakref.WeakKeyDictionary()


class GestorPartida:

    def __init__(self):
        self.partidaActual = None


        _gestor_state[self] = {
            "estado": "MENU",
            "estado_anterior": "MENU",
            "mensaje_error": ""
        }

    def iniciarPartida(self):
        if not self.partidaActual:
            self.partidaActual = Partida()

        if self.partidaActual.todosLosColoresAsignados():
            self.partidaActual.iniciar()
            self.estado = "JUEGO"
            return True
        else:
            self.mensaje_error = "Debes asignar nombres y colores válidos a todos los jugadores."
            return False

    def seleccionarColor(self, color: str = None) -> None:
        if self.partidaActual:
            self.partidaActual.seleccionarColor(color)

    def seleccionarColores(self) -> list:
        if not self.partidaActual:
            self.partidaActual = Partida()
        return self.partidaActual.obtenerColoresDisponibles()

    def cancelarSeleccionColores(self) -> None:
        if self.partidaActual:
            self.partidaActual.cancelarSeleccionColores()
        self.estado = "MENU"

    def configurarCantidadJugadores(self, cantidad: int) -> None:
        if not self.partidaActual:
            self.partidaActual = Partida()
        self.partidaActual.configurarCantidadJugadores(cantidad)

    def registrarNombre(self, nombre: str) -> None:
        if not self.partidaActual:
            self.partidaActual = Partida()
        self.partidaActual.registrarNombre(nombre)

    def lanzarDado(self):
        if self.partidaActual:
            return self.partidaActual.lanzarDado()
        return 0

    def seleccionarFicha(self, ficha: Ficha):
        return self.moverFicha(ficha)

    def moverFicha(self, ficha: Ficha):
        if self.partidaActual:
            return self.partidaActual.moverFicha(ficha)
        return False

    def pausarPartida(self):
        self.estado = "PAUSA"
        if self.partidaActual:
            self.partidaActual.pausar()

    def reanudarPartida(self):
        self.estado = "JUEGO"
        if self.partidaActual:
            self.partidaActual.reanudar()

    def consultarReglas(self) -> None:
        self.estado_anterior = self.estado
        self.estado = "REGLAS"

    def volverDeReglas(self) -> None:
        self.estado = getattr(self, "estado_anterior", "MENU")

    def guardarPartida(self):
        if self.partidaActual:
            from persistencia.persistencia import Persistencia
            p = Persistencia()
            p.guardarPartida(self.partidaActual)

    def cancelarPartida(self) -> None:
        if self.partidaActual:
            self.partidaActual.cancelarPartida()
        self.partidaActual = None
        self.estado = "MENU"

    def reanudarPartidaGuardada(self):
        from persistencia.persistencia import Persistencia
        p = Persistencia()
        partida = p.cargarPartida()
        if partida:
            self.partidaActual = partida
            self.estado = "JUEGO"

    def finalizarPartida(self):
        if self.partidaActual:
            self.partidaActual.finalizar()
        self.estado = "FINAL"

    def reiniciarPartida(self) -> None:
        if self.partidaActual:
            for j in self.partidaActual.jugadores:
                for f in j.fichas:
                    f.volverBase()
                j.movimientos = 0
                j.puntaje = 0
            self.partidaActual.iniciar()
            self.estado = "JUEGO"

    def confirmarReinicio(self) -> None:
        self.reiniciarPartida()

    def cancelarReinicio(self) -> None:
        pass

    def volverAlMenuPrinicipal(self) -> None:
        self.estado = "MENU"

    def confirmarSalida(self) -> None:
        self.estado = "MENU"

    def cancelarSalida(self) -> None:
        pass

    def guardarYSalir(self) -> None:
        self.guardarPartida()
        self.volverAlMenuPrinicipal()

    def confirmarGuardado(self) -> None:
        self.guardarPartida()

    def cancelarGuardado(self) -> None:
        pass

    def verEstadisticas(self) -> None:
        if self.partidaActual:
            self.partidaActual.recopilarEstadisticas()
        self.estado_anterior = self.estado
        self.estado = "ESTADISTICAS"

    def volver(self) -> None:
        self.estado = getattr(self, "estado_anterior", "MENU")

    def __setattr__(self, name, value):
        if name == "partidaActual":
            super().__setattr__(name, value)
        else:
            state = _gestor_state.setdefault(self, {})
            state[name] = value

    def __getattr__(self, name):
        state = _gestor_state.setdefault(self, {})
        if name in state:
            return state[name]
        if name == "volverAlMenuPrincipal":
            return self.volverAlMenuPrinicipal
        if name == "pausar":
            return self.pausarPartida
        if name == "reanudar":
            return self.reanudarPartida
        if name == "consultarEstadisticas":
            return self.verEstadisticas
        if name == "volverDeEstadisticas":
            return self.volver
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
