import random
import time

from modelos.color import Color
from modelos.ficha import Ficha
from modelos.jugador import Jugador
from modelos.tablero import Tablero


class Partida:

    def __init__(self, datosConfiguracion: dict = None):
        self.tablero = Tablero()
        self.dado = 0                 # 0 = todavía no se tiró en este turno
        self.cantidadJugadores = 0
        self.estado = "NO_INICIADA"
        self.coloresDisponibles = list(Color)
        self.jugadores = []
        self.jugadorActual = None
        self.ganador = None
        self.turnoActual = 0
        self.turnosJugados = 0
        self.tiempoTranscurrido = 0
        self._seisConsecutivos = 0    # regla de los tres 6 seguidos (CU-08 A10)
        self._inicioTiempo = None     # momento en que se reanudó el reloj de la partida

        if datosConfiguracion:
            # DS N5: «create»(datosConfiguracion) y un Jugador por cada participante configurado.
            self.cantidadJugadores = datosConfiguracion.get("cantidadJugadores", 0)
            for datos in datosConfiguracion.get("jugadores", []):
                self.jugadores.append(Jugador((datos.get("nombre") or "").strip(), datos.get("color")))
            self.obtenerColoresDisponibles()

    # ------------------------------------------------------------------
    # Configuración (CU-01 a CU-05, DS N1, N4 y N5)
    # ------------------------------------------------------------------

    def iniciarConfiguracion(self) -> None:
        self.estado = "CONFIGURACION"
        self.jugadores = []
        self.cantidadJugadores = 0
        self.obtenerColoresDisponibles()

    def numeroJugadores(self) -> int:
        return len(self.jugadores)

    def añadirJugador(self) -> bool:
        if self.numeroJugadores() >= 4:
            return False
        self.jugadores.append(Jugador())
        self.cantidadJugadores = self.numeroJugadores()
        return True

    def eliminarJugador(self) -> bool:
        if self.numeroJugadores() <= 2:
            return False
        self.jugadores.pop()
        self.cantidadJugadores = self.numeroJugadores()
        self.obtenerColoresDisponibles()
        return True

    def configurarCantidadJugadores(self, cantidad: int) -> bool:
        # CU-02: se agregan o quitan jugadores hasta llegar a la cantidad (2 a 4).
        if not 2 <= cantidad <= 4:
            return False
        while self.numeroJugadores() < cantidad:
            self.añadirJugador()
        while self.numeroJugadores() > cantidad:
            self.eliminarJugador()
        self.cantidadJugadores = cantidad
        self.obtenerColoresDisponibles()
        return True

    def validarNombre(self, nombre: str, indice: int = None) -> bool:
        # CU-03: el nombre no puede estar vacío ni repetirse con el de otro jugador.
        if not nombre or not nombre.strip():
            return False
        otros = [j.nombre for i, j in enumerate(self.jugadores) if i != indice and j.nombre]
        return nombre.strip() not in otros

    def registrarNombre(self, nombre: str, indice: int = None) -> bool:
        # Sin índice se registra en el primer jugador que todavía no tiene nombre.
        if indice is None:
            indice = next((i for i, j in enumerate(self.jugadores) if not j.nombre), None)
        if indice is None or not 0 <= indice < len(self.jugadores) or not self.validarNombre(nombre, indice):
            return False
        self.jugadores[indice].nombre = nombre.strip()
        return True

    def registrarJugadorConsola(self, indice: int = None) -> bool:
        # CU-03 C: el jugador controlado por la consola recibe un nombre "Bot n".
        if indice is None:
            indice = next((i for i, j in enumerate(self.jugadores) if not j.nombre), None)
        if indice is None:
            return False
        return self.registrarNombre(f"Bot {indice + 1}", indice)

    def seleccionarColores(self) -> list[Color]:
        # CU-04 pasos 2 y 3: colores que todavía puede elegir un jugador.
        return self.obtenerColoresDisponibles()

    def obtenerColoresDisponibles(self) -> list[Color]:
        ocupados = [j.getColor() for j in self.jugadores]
        self.coloresDisponibles = [c for c in list(Color) if c not in ocupados]
        return self.coloresDisponibles

    def validarColor(self, color: Color) -> bool:
        return color in self.obtenerColoresDisponibles()

    def asignarColor(self, jugador: Jugador, color: Color) -> bool:
        if not self.validarColor(color):
            return False
        jugador.asignarColor(color)
        self.obtenerColoresDisponibles()
        return True

    def seleccionarColor(self, color: Color, indice: int = None) -> bool:
        # Sin índice el color es para el primer jugador que todavía no tiene uno.
        if indice is None:
            indice = next((i for i, j in enumerate(self.jugadores) if j.getColor() is None), None)
        if indice is None or not 0 <= indice < len(self.jugadores):
            return False
        jugador = self.jugadores[indice]
        return jugador.getColor() == color or self.asignarColor(jugador, color)

    def todosLosColoresAsignados(self) -> bool:
        colores = [j.getColor() for j in self.jugadores]
        return (len(self.jugadores) == self.cantidadJugadores and None not in colores
                and len(colores) == len(set(colores)))

    def cancelarSeleccionColores(self) -> None:
        for jugador in self.jugadores:
            jugador.asignarColor(None)
        self.obtenerColoresDisponibles()

    def validarConfiguracion(self) -> str:
        # DS N5: devuelve "" si la configuración es válida o el motivo si no lo es.
        nombres = [j.nombre for j in self.jugadores]
        if not 2 <= self.cantidadJugadores <= 4 or len(self.jugadores) != self.cantidadJugadores:
            return "La cantidad de participantes debe estar entre 2 y 4."
        if "" in nombres:
            return f"El nombre del Jugador {nombres.index('') + 1} no puede estar vacío."
        if len(nombres) != len(set(nombres)):
            return "No se permiten nombres repetidos."
        if None in [j.getColor() for j in self.jugadores]:
            return "Cada jugador debe tener un color asignado."
        if not self.todosLosColoresAsignados():
            return "Cada jugador debe tener un color diferente."
        return ""

    # ------------------------------------------------------------------
    # Inicio y turnos (CU-05, CU-07 a CU-09, DS N1, N5, N8 y N9)
    # ------------------------------------------------------------------

    def iniciar(self) -> None:
        # DS N1: al crear la partida se inicializa el tablero y empieza la configuración.
        # DS N5: con los jugadores ya configurados, la partida comienza.
        self.tablero = Tablero()
        self.tablero.inicializar()
        if not self.jugadores:
            self.iniciarConfiguracion()
            return
        for jugador in self.jugadores:
            jugador.movimientos = 0
            jugador.puntaje = 0
            for ficha in jugador.obtenerFichas():
                ficha.volverBase()
        self.establecerPrimerTurno()
        self.estado = "EN_CURSO"
        self.turnosJugados = 1
        self.tiempoTranscurrido = 0
        self._inicioTiempo = time.time()

    def establecerPrimerTurno(self) -> None:
        self.turnoActual = 0
        self.jugadorActual = self.jugadores[0] if self.jugadores else None
        self.dado = 0
        self._seisConsecutivos = 0

    def lanzarDado(self) -> int:
        if self.estado != "EN_CURSO" or self.dado:
            return self.dado
        valor = random.randint(1, 6)
        self.dado = valor
        jugador = self.obtenerJugadorActual()

        self._seisConsecutivos = self._seisConsecutivos + 1 if valor == 6 else 0
        if self._seisConsecutivos == 3:
            # CU-08 A10: el tercer 6 consecutivo no se usa y el turno pasa.
            self.siguienteTurno()
        elif jugador is None or not jugador.tieneMovimientosValidos(valor, self.tablero):
            # CU-08 A1: sin movimientos válidos el turno pasa al siguiente jugador.
            self.siguienteTurno()
        return valor

    def obtenerJugadorActual(self) -> Jugador:
        if 0 <= self.turnoActual < len(self.jugadores):
            self.jugadorActual = self.jugadores[self.turnoActual]
            return self.jugadorActual
        return None

    def obtenerMovimientosValidos(self) -> list[Ficha]:
        # DS N8: fichas del jugador actual que pueden moverse con el valor del dado.
        jugador = self.obtenerJugadorActual()
        if jugador is None or not self.dado:
            return []
        return self.tablero.obtenerMovimientosValidos(jugador, self.dado)

    def sacarFicha(self, ficha: Ficha) -> bool:
        # CU-07: con un 6 la ficha sale de la base a la casilla de salida de su color.
        return self.tablero.sacarFicha(ficha)

    def moverFicha(self, ficha: Ficha) -> bool:
        # DS N8 y N9: puedeMover → calcularDestino → moverFicha → verificarCaptura →
        # verificarMeta → todasLasFichasEnMeta → finalizar o administrarTurno.
        jugador = self.obtenerJugadorActual()
        if self.estado != "EN_CURSO" or jugador is None or ficha not in jugador.obtenerFichas():
            return False
        if not self.tablero.puedeMover(ficha, self.dado):
            return False

        destino = self.tablero.calcularDestino(ficha, self.dado)
        if ficha.enBase:
            self.sacarFicha(ficha)
        else:
            self.tablero.moverFicha(ficha, destino)
        self.tablero.verificarCaptura(ficha)
        self.tablero.verificarMeta(ficha)
        jugador.movimientos += 1

        if self.verificarGanador():
            self.finalizar()
        else:
            self.administrarTurno()
        return True

    def administrarTurno(self) -> None:
        # Con un 6 el mismo jugador vuelve a tirar (CU-08 A9); si no, pasa el turno.
        if self.dado == 6:
            self.dado = 0
        else:
            self.siguienteTurno()

    def siguienteTurno(self) -> None:
        if not self.jugadores:
            return
        self.turnosJugados += 1
        self.turnoActual = (self.turnoActual + 1) % len(self.jugadores)
        self.jugadorActual = self.jugadores[self.turnoActual]
        self.dado = 0
        self._seisConsecutivos = 0

    def verificarGanador(self) -> bool:
        for jugador in self.jugadores:
            if jugador.todasLasFichasEnMeta():
                self.ganador = jugador
                return True
        return False

    def finalizar(self) -> None:
        self.recopilarEstadisticas()
        self.estado = "FINALIZADA"
        self._inicioTiempo = None

    # ------------------------------------------------------------------
    # Pausa, guardado, reinicio y salida (CU-10 a CU-15)
    # ------------------------------------------------------------------

    def cancelarPartida(self) -> None:
        # CU-01 A y CU-04 B: se descarta lo configurado.
        self.descartarDatos()
        self.estado = "NO_INICIADA"

    def pausar(self) -> None:
        if self.estado == "EN_CURSO":
            self.conservarEstado()
            self.estado = "PAUSADA"

    def reanudar(self) -> None:
        if self.estado in ("PAUSADA", "EN_CURSO"):
            self.estado = "EN_CURSO"
            self._inicioTiempo = time.time()

    def conservarEstado(self) -> None:
        # CU-10: el reloj se detiene y queda acumulado el tiempo jugado hasta la pausa.
        if self._inicioTiempo:
            self.tiempoTranscurrido += int(time.time() - self._inicioTiempo)
        self._inicioTiempo = None

    def guardar(self) -> dict:
        # CU-14: estado completo de la partida que se pasa a la persistencia ("JSON Ludo").
        self.conservarEstado()
        if self.estado == "EN_CURSO":
            self._inicioTiempo = time.time()
        return {
            "cantidadJugadores": self.cantidadJugadores,
            "estado": self.estado,
            "turnoActual": self.turnoActual,
            "dado": self.dado,
            "seisConsecutivos": self._seisConsecutivos,
            "turnosJugados": self.turnosJugados,
            "tiempoTranscurrido": self.tiempoTranscurrido,
            "ganador": self.ganador.nombre if self.ganador else None,
            "jugadores": [{
                "nombre": j.nombre,
                "color": j.color.name if j.color else None,
                "movimientos": j.movimientos,
                "puntaje": j.puntaje,
                "fichas": [{"posicion": f.posicion, "enBase": f.enBase, "enMeta": f.enMeta}
                           for f in j.fichas],
            } for j in self.jugadores],
        }

    def solicitarConfirmacion(self) -> bool:
        # CU-11, CU-12 y CU-14: solo se pide confirmación si hay progreso que se perdería.
        return self.verificarPartidaActiva()

    def descartarDatos(self) -> None:
        self.jugadores = []
        self.jugadorActual = None
        self.ganador = None
        self.dado = 0
        self.tiempoTranscurrido = 0
        self._inicioTiempo = None
        self.tablero.inicializar()
        self.obtenerColoresDisponibles()

    def mantenerPartida(self) -> bool:
        # El jugador canceló la acción: la partida sigue tal como estaba.
        return self.verificarPartidaActiva()

    def verificarPartidaActiva(self) -> bool:
        return self.estado in ("EN_CURSO", "PAUSADA")

    def cerrarPartida(self) -> None:
        # CU-12 paso 4: se descartan los datos de la partida y se vuelve al menú.
        self.descartarDatos()
        self.estado = "CERRADA"

    def recopilarEstadisticas(self) -> str:
        # CU-15: tiempo, turnos y resumen de cada jugador.
        tiempo = self.tiempoTranscurrido
        if self._inicioTiempo:
            tiempo += int(time.time() - self._inicioTiempo)
        for jugador in self.jugadores:
            jugador.puntaje = sum(100 if f.enMeta else f.posicion for f in jugador.fichas)
        lineas = [
            f"Tiempo transcurrido: {tiempo // 60:02d}:{tiempo % 60:02d}",
            f"Turnos jugados: {self.turnosJugados}",
            f"Ganador: {self.ganador.nombre if self.ganador else 'En curso'}",
        ]
        lineas += [jugador.visualizarEstadisticas() for jugador in self.jugadores]
        return "\n".join(lineas)

    def cerrarPantallaEstadisticas(self) -> bool:
        # Al cerrar las estadísticas se vuelve a la partida si sigue activa.
        return self.verificarPartidaActiva()
