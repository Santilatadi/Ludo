import time
import random
import uuid
import weakref
from modelos.color import Color
from modelos.ficha import Ficha
from modelos.jugador import Jugador
from modelos.tablero import Tablero

_partida_state = weakref.WeakKeyDictionary()

_PARTIDA_ATTRS = {
    "tablero", "dado", "cantidadJugadores", "estado", "coloresDisponibles",
    "jugadores", "jugadorActual", "ganador", "turnoActual", "turnosJugados", "tiempoTranscurrido"
}


class Partida:

    def __init__(self):
        self.tablero = Tablero()
        self.dado = 0
        self.cantidadJugadores = 2
        self.estado = "NO_INICIADA"
        self.coloresDisponibles = list(Color)
        self.jugadores = []
        self.jugadorActual = None
        self.ganador = None
        self.turnoActual = 0
        self.turnosJugados = 0
        self.tiempoTranscurrido = 0

        _partida_state[self] = {
            "id_partida": f"partida_{int(time.time())}_{uuid.uuid4().hex[:6]}",
            "consecutivoSeis": 0,
            "dado_lanzado": False,
            "esperando_movimiento": False,
            "tiempo_inicio": None,
            "tiempo_acumulado": 0,
            "mensaje_estado": "Lanza el dado para comenzar tu turno."
        }

    def iniciar(self):
        self.tablero.inicializar()
        self.tablero.jugadores = self.jugadores
        self.establecerPrimerTurno()
        self.estado = "EN_CURSO"
        self.turnosJugados = 1
        state = _partida_state.setdefault(self, {})
        state["tiempo_inicio"] = time.time()
        state["tiempo_acumulado"] = 0
        state["consecutivoSeis"] = 0
        state["dado_lanzado"] = False
        state["esperando_movimiento"] = False
        for j in self.jugadores:
            j.movimientos = 0
            j.puntaje = 0

    def establecerPrimerTurno(self):
        self.turnoActual = 0
        if self.jugadores:
            self.jugadorActual = self.jugadores[0]
        state = _partida_state.setdefault(self, {})
        state["consecutivoSeis"] = 0
        state["dado_lanzado"] = False
        state["esperando_movimiento"] = False

    def obtenerColoresDisponibles(self) -> list[Color]:
        ocupados = [j.color for j in self.jugadores]
        return [c for c in list(Color) if c not in ocupados]

    def seleccionarColor(self, color: str = None) -> None:
        pass

    def validarColor(self, color: Color) -> bool:
        return color in self.obtenerColoresDisponibles()

    def asignarColor(self, jugador: Jugador, color: Color) -> None:
        if self.validarColor(color):
            jugador.asignarColor(color)

    def todosLosColoresAsignados(self) -> bool:
        if len(self.jugadores) != self.cantidadJugadores:
            return False
        colores = [j.color for j in self.jugadores]
        return len(colores) == len(set(colores))

    def cancelarSeleccionColores(self) -> None:
        pass

    def configurarCantidadJugadores(self, cantidad: int) -> None:
        if 2 <= cantidad <= 4:
            self.cantidadJugadores = cantidad

    def validarNombre(self, nombre: str) -> bool:
        return bool(nombre and nombre.strip())

    def registrarNombre(self, nombre: str) -> None:
        if self.validarNombre(nombre):
            colores = self.obtenerColoresDisponibles()
            col = colores[0] if colores else Color.ROJO
            self.jugadores.append(Jugador(nombre.strip(), col))

    def registrarJugadorConsola(self):
        pass

    def lanzarDado(self) -> int:
        state = _partida_state.setdefault(self, {})
        if state.get("dado_lanzado"):
            return self.dado

        self.dado = random.randint(1, 6)
        valor_dado = self.dado
        state["dado_lanzado"] = True
        jugador = self.obtenerJugadorActual()

        if self.dado == 6:
            consecutivo = state.get("consecutivoSeis", 0) + 1
            state["consecutivoSeis"] = consecutivo
            if consecutivo == 3:
                state["consecutivoSeis"] = 0
                state["dado_lanzado"] = False
                state["esperando_movimiento"] = False
                self.siguienteTurno()
                return 6
        else:
            state["consecutivoSeis"] = 0

        movimientos = self.obtenerMovimientosValidos()
        if len(movimientos) == 0:
            state["dado_lanzado"] = False
            state["esperando_movimiento"] = False
            state["consecutivoSeis"] = 0
            self.siguienteTurno()
        else:
            state["esperando_movimiento"] = True

        return valor_dado

    def obtenerJugadorActual(self) -> Jugador:
        if 0 <= self.turnoActual < len(self.jugadores):
            self.jugadorActual = self.jugadores[self.turnoActual]
            return self.jugadorActual
        return None

    def obtenerMovimientosValidos(self):
        jugador = self.obtenerJugadorActual()
        state = _partida_state.setdefault(self, {})
        if not jugador or not state.get("dado_lanzado"):
            return []
        return self.tablero.obtenerMovimientosValidos(jugador, self.dado)

    def sacarFicha(self):
        for f in self.obtenerMovimientosValidos():
            if f.enBase:
                return self.moverFicha(f)
        return False

    def moverFicha(self, ficha: Ficha):
        jugador = self.obtenerJugadorActual()
        movimientos = self.obtenerMovimientosValidos()
        if ficha not in movimientos:
            return False

        self.tablero.moverFicha(ficha, self.dado)
        if jugador:
            jugador.movimientos = getattr(jugador, "movimientos", 0) + 1
            jugador.puntaje = getattr(jugador, "puntaje", 0) + 10

        if self.verificarGanador():
            self.finalizar()
            return True

        state = _partida_state.setdefault(self, {})
        if self.dado == 6 and state.get("consecutivoSeis", 0) < 3:
            state["dado_lanzado"] = False
            state["esperando_movimiento"] = False
        else:
            state["consecutivoSeis"] = 0
            state["dado_lanzado"] = False
            state["esperando_movimiento"] = False
            self.siguienteTurno()

        return True

    def administrarTurno(self):
        self.siguienteTurno()

    def siguienteTurno(self):
        if len(self.jugadores) > 0:
            self.turnosJugados += 1
            self.turnoActual = (self.turnoActual + 1) % len(self.jugadores)
            self.jugadorActual = self.jugadores[self.turnoActual]
            state = _partida_state.setdefault(self, {})
            state["dado_lanzado"] = False
            state["esperando_movimiento"] = False
            self.dado = 0

    def verificarGanador(self) -> bool:
        for jug in self.jugadores:
            if jug.todasLasFichasEnMeta():
                self.ganador = jug
                return True
        return False

    def finalizar(self):
        self.recopilarEstadisticas()
        self.estado = "FINALIZADA"

    def cancelarPartida(self) -> None:
        self.estado = "NO_INICIADA"
        self.jugadores = []
        self.ganador = None

    def pausar(self):
        self.estado = "PAUSADA"
        state = _partida_state.setdefault(self, {})
        t_inicio = state.get("tiempo_inicio")
        if t_inicio:
            state["tiempo_acumulado"] = state.get("tiempo_acumulado", 0) + (time.time() - t_inicio)
            state["tiempo_inicio"] = None

    def reanudar(self):
        self.estado = "EN_CURSO"
        state = _partida_state.setdefault(self, {})
        state["tiempo_inicio"] = time.time()

    def conservarEstado(self):
        pass

    def guardar(self):
        from persistencia.persistencia import Persistencia
        Persistencia().guardarPartida(self)

    def solicitarConfirmacion(self) -> None:
        pass

    def descartarDatos(self) -> None:
        self.jugadores = []

    def iniciarConfiguracion(self) -> None:
        self.estado = "CONFIGURACION"

    def mantenerPartida(self) -> None:
        pass

    def verificarPartidaActiva(self) -> bool:
        return self.estado == "EN_CURSO"

    def cerrarPartida(self) -> None:
        self.finalizar()

    def recopilarEstadisticas(self) -> str:
        state = _partida_state.setdefault(self, {})
        t_inicio = state.get("tiempo_inicio")
        if t_inicio:
            self.tiempoTranscurrido = max(0, int(time.time() - t_inicio + state.get("tiempo_acumulado", 0)))
        elif "tiempo_acumulado" in state:
            self.tiempoTranscurrido = max(0, int(state.get("tiempo_acumulado", 0)))

        for j in self.jugadores:
            pts = 0
            for f in j.fichas:
                if f.enMeta:
                    pts += 100
                elif not f.enBase:
                    pts += f.posicion
            j.puntaje = pts

        minutos = self.tiempoTranscurrido // 60
        segundos = self.tiempoTranscurrido % 60
        lineas = [
            f"Tiempo transcurrido: {minutos:02d}:{segundos:02d}",
            f"Turnos jugados: {self.turnosJugados}",
            f"Ganador: {self.ganador.nombre if self.ganador else 'En curso'}"
        ]
        for j in self.jugadores:
            lineas.append(f"{j.nombre} ({j.color.name}): {j.movimientos} movimientos, {j.puntaje} puntos")
        return "\n".join(lineas)

    def cerrarPantallaEstadisticas(self) -> None:
        pass

    def __setattr__(self, name, value):
        if name in _PARTIDA_ATTRS:
            super().__setattr__(name, value)
        else:
            state = _partida_state.setdefault(self, {})
            state[name] = value

    def __getattr__(self, name):
        state = _partida_state.setdefault(self, {})
        if name in state:
            return state[name]
        if name == "tirarDado":
            return self.lanzarDado
        if name == "identificarGanador":
            return self.verificarGanador
        if name == "reiniciar":
            def _reiniciar():
                for j in self.jugadores:
                    for f in j.fichas:
                        f.volverBase()
                    j.movimientos = 0
                    j.puntaje = 0
                self.ganador = None
                self.dado = 0
                self.iniciar()
            return _reiniciar
        if name == "turnos_totales":
            return self.turnosJugados
        if name == "SeleccionarColor":
            return self.seleccionarColor
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
