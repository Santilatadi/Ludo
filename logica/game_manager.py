"""
Modulo game_manager.py
Clase GameManager ("Game Manager / Dios" del diagrama de clases): recibe las
acciones del jugador desde la interfaz y las delega en la Partida y en la
PersistenciaDeDatos, como muestran los diagramas de secuencia N1, N4, N5, N8 y N9.

Los métodos que pueden fallar devuelven (exito, mensaje) para que la interfaz
muestre el mensaje que indica cada caso de uso.
"""

from modelos.ficha import Ficha
from modelos.partida import Partida
from persistencia.persistencia_de_datos import PersistenciaDeDatos


class GameManager:

    def __init__(self):
        self.partidaActual = None

    # ------------------------------------------------------------------
    # Configuración (CU-01 a CU-05)
    # ------------------------------------------------------------------

    def iniciarPartida(self, datosConfiguracion: dict = None) -> tuple[bool, str]:
        if datosConfiguracion is None:
            if self.partidaActual is None or self.partidaActual.estado != "CONFIGURACION":
                # DS N1: se crea la partida y se inicializa su tablero para configurarla.
                self.partidaActual = Partida()
                self.partidaActual.iniciar()
                return True, ""
            datosConfiguracion = {
                "cantidadJugadores": self.partidaActual.numeroJugadores(),
                "jugadores": [{"nombre": j.nombre, "color": j.getColor()} for j in self.partidaActual.jugadores],
            }

        # DS N5: la Partida se crea con los datos configurados, los valida y comienza.
        partida = Partida(datosConfiguracion)
        error = partida.validarConfiguracion()
        if error:
            return False, error
        partida.iniciar()
        self.partidaActual = partida
        # DS N4 pasos 9 y 10: con la configuración completa se guarda la partida.
        PersistenciaDeDatos().guardarPartida(partida)
        return True, "Partida iniciada correctamente."

    def configurarCantidadJugadores(self, cantidad: int) -> tuple[bool, str]:
        if self.partidaActual.configurarCantidadJugadores(cantidad):
            return True, "Cantidad registrada."
        # CU-02, alternativas A y B
        return False, "El máximo es 4 jugadores." if cantidad > 4 else "El mínimo es 2 jugadores."

    def registrarNombre(self, nombre: str, indice: int = None) -> tuple[bool, str]:
        # CU-03. Un nombre None indica un jugador controlado por la consola (alternativa C).
        partida = self.partidaActual
        if nombre is None:
            registrado = partida.registrarJugadorConsola(indice)
        else:
            registrado = partida.validarNombre(nombre, indice) and partida.registrarNombre(nombre, indice)
        if registrado:
            return True, "Nombre registrado."
        if nombre is not None and not nombre.strip():
            numero = indice + 1 if indice is not None else partida.numeroJugadores()
            return False, f"El nombre del Jugador {numero} no puede estar vacío."
        return False, "No se permiten nombres repetidos."

    def seleccionarColores(self) -> list:
        # DS N4 pasos 1 a 4: colores disponibles.
        return self.partidaActual.seleccionarColores()

    def seleccionarColor(self, color, indice: int = None) -> tuple[bool, str]:
        # DS N4 pasos 5 a 8 (alternativa A: color no disponible).
        if self.partidaActual.seleccionarColor(color, indice):
            return True, "Color asignado."
        return False, "Ese color ya está asignado: selecciona otro color."

    def cancelarSeleccionColores(self) -> None:
        # DS N4 alternativa B: se descarta la selección y se vuelve al menú principal.
        if self.partidaActual:
            self.partidaActual.cancelarSeleccionColores()
        self.cancelarPartida()

    # ------------------------------------------------------------------
    # Juego (CU-07 a CU-09 y CU-13)
    # ------------------------------------------------------------------

    def lanzarDado(self) -> int:
        return self.partidaActual.lanzarDado() if self.partidaActual else 0

    def seleccionarFicha(self, ficha: Ficha) -> bool:
        jugador = self.partidaActual.obtenerJugadorActual() if self.partidaActual else None
        if jugador is None or jugador.seleccionarFicha(ficha) is None:
            return False
        return self.moverFicha(ficha)

    def moverFicha(self, ficha: Ficha) -> bool:
        return self.partidaActual.moverFicha(ficha) if self.partidaActual else False

    def finalizarPartida(self) -> None:
        if self.partidaActual and self.partidaActual.estado != "FINALIZADA":
            self.partidaActual.finalizar()

    # ------------------------------------------------------------------
    # Pausa, reglas y estadísticas (CU-06, CU-10 y CU-15)
    # ------------------------------------------------------------------

    def pausarPartida(self) -> None:
        if self.partidaActual:
            self.partidaActual.pausar()

    def reanudarPartida(self) -> None:
        if self.partidaActual:
            self.partidaActual.reanudar()

    def consultarReglas(self) -> str:
        # CU-06: el texto se obtiene de la persistencia ("" si no se pudo cargar).
        return PersistenciaDeDatos().obtenerReglas()

    def volverDeReglas(self) -> bool:
        # Devuelve True si hay una partida activa a la que volver.
        return bool(self.partidaActual and self.partidaActual.verificarPartidaActiva())

    def verEstadisticas(self) -> str:
        return self.partidaActual.recopilarEstadisticas() if self.partidaActual else ""

    def volver(self) -> bool:
        # Cierra la pantalla de estadísticas; True si se vuelve a una partida activa.
        return bool(self.partidaActual and self.partidaActual.cerrarPantallaEstadisticas())

    # ------------------------------------------------------------------
    # Cancelar, reiniciar y salir (CU-01, CU-11 y CU-12)
    # ------------------------------------------------------------------

    def cancelarPartida(self) -> None:
        if self.partidaActual:
            self.partidaActual.cancelarPartida()
        self.partidaActual = None

    def reiniciarPartida(self) -> None:
        # CU-11: se descarta la partida y se vuelve a configurar (CU-02 a CU-04).
        if self.partidaActual:
            self.partidaActual.descartarDatos()
        self.partidaActual = None
        self.iniciarPartida()

    def confirmarReinicio(self) -> None:
        jugador = self.partidaActual.obtenerJugadorActual() if self.partidaActual else None
        if jugador is None or jugador.confirmarAccion():
            self.reiniciarPartida()

    def cancelarReinicio(self) -> None:
        # CU-11 A 3.a: la partida sigue sin modificaciones.
        if self.partidaActual:
            self.partidaActual.mantenerPartida()

    def volverAlMenuPrinicipal(self) -> bool:
        # CU-12: devuelve True si hay que pedir confirmación (partida activa).
        # Sin partida activa (A 3.b) se vuelve directamente al menú.
        if self.partidaActual and self.partidaActual.solicitarConfirmacion():
            return True
        self.partidaActual = None
        return False

    def confirmarSalida(self) -> None:
        # CU-12 paso 4: se descartan los datos de la partida.
        if self.partidaActual:
            self.partidaActual.cerrarPartida()
        self.partidaActual = None

    def cancelarSalida(self) -> None:
        if self.partidaActual:
            self.partidaActual.mantenerPartida()

    # ------------------------------------------------------------------
    # Guardar y reanudar (CU-14)
    # ------------------------------------------------------------------

    def guardarPartida(self) -> tuple[bool, str]:
        if not self.partidaActual:
            return False, "No hay ninguna partida para guardar."
        return PersistenciaDeDatos().guardarPartida(self.partidaActual)

    def guardarYSalir(self) -> tuple[bool, str]:
        exito, mensaje = self.guardarPartida()
        if exito:
            self.partidaActual = None
        return exito, mensaje

    def confirmarGuardado(self) -> tuple[bool, str]:
        return self.guardarYSalir()

    def cancelarGuardado(self) -> None:
        # CU-14 A 1.a: se descarta la solicitud y la partida sigue igual.
        if self.partidaActual:
            self.partidaActual.mantenerPartida()

    def reanudarPartidaGuardada(self, numero: int = 0) -> tuple[bool, str]:
        # CU-14: puede haber varias partidas guardadas; numero 0 es la más reciente.
        persistencia = PersistenciaDeDatos()
        if not persistencia.existePartidaGuardada():
            return False, "No existe ninguna partida guardada."
        partida, mensaje = persistencia.cargarPartida(numero)
        if partida is None:
            return False, mensaje
        self.partidaActual = partida
        return True, mensaje
