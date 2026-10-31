"""
Modulo game_manager.py
Clase GameManager ("Game Manager / Dios" del diagrama de clases): recibe las
acciones del jugador desde la interfaz y las delega en la Partida y en la
PersistenciaDeDatos, como muestran los diagramas de secuencia N1, N4, N5, N8 y N9.

Los métodos que pueden fallar devuelven (exito, mensaje) para que la interfaz
muestre el mensaje que indica cada caso de uso.
"""

# Importa la clase Ficha para interactuar con las fichas elegidas por el usuario
from modelos.ficha import Ficha
# Importa la clase Partida para crear y controlar el estado del juego
from modelos.partida import Partida
# Importa PersistenciaDeDatos para guardar y cargar archivos de partidas
from persistencia.persistencia_de_datos import PersistenciaDeDatos


# Clase principal que coordina la lógica del juego con la interfaz visual
class GameManager:

    # Constructor: inicializa el gestor con la partida actual vacía
    def __init__(self):
        # Guarda la referencia a la partida que se está jugando o configurando
        self.partidaActual = None

    # ------------------------------------------------------------------
    # Configuración (CU-01 a CU-05)
    # ------------------------------------------------------------------

    # Inicia una partida nueva o prepara la configuración inicial
    def iniciarPartida(self, datosConfiguracion: dict = None) -> tuple[bool, str]:
        # Si no se enviaron datos de configuración:
        if datosConfiguracion is None:
            # Si no hay partida o no está en configuración:
            if self.partidaActual is None or self.partidaActual.estado != "CONFIGURACION":
                # DS N1: se crea la partida y se inicializa su tablero para configurarla.
                # Crea una nueva partida
                self.partidaActual = Partida()
                # Inicia la partida vacía para entrar en modo configuración
                self.partidaActual.iniciar()
                # Devuelve True con texto vacío indicando éxito
                return True, ""
            # Si ya había una partida configurándose, extrae los datos configurados
            datosConfiguracion = {
                "cantidadJugadores": self.partidaActual.numeroJugadores(),
                "jugadores": [{"nombre": j.nombre, "color": j.getColor()} for j in self.partidaActual.jugadores],
            }

        # DS N5: la Partida se crea con los datos configurados, los valida y comienza.
        # Crea la partida con la configuración proporcionada
        partida = Partida(datosConfiguracion)
        # Revisa si la configuración es válida (nombres, colores, cantidad)
        error = partida.validarConfiguracion()
        # Si hubo algún error, devuelve False con el mensaje de error
        if error:
            return False, error
        # Inicia la partida formalmente (pone fichas en base y reloj en marcha)
        partida.iniciar()
        # Guarda la partida iniciada como la partida actual
        self.partidaActual = partida
        # DS N4 pasos 9 y 10: con la configuración completa se guarda la partida.
        # Guarda automáticamente la partida recién comenzada en el disco
        PersistenciaDeDatos().guardarPartida(partida)
        # Retorna éxito con mensaje confirmatorio
        return True, "Partida iniciada correctamente."

    # Configura cuántos jugadores van a participar (entre 2 y 4)
    def configurarCantidadJugadores(self, cantidad: int) -> tuple[bool, str]:
        # Intenta configurar la cantidad en la partida actual
        if self.partidaActual.configurarCantidadJugadores(cantidad):
            return True, "Cantidad registrada."
        # CU-02, alternativas A y B
        # Si falló, informa si se pasó del máximo (4) o no llegó al mínimo (2)
        return False, "El máximo es 4 jugadores." if cantidad > 4 else "El mínimo es 2 jugadores."

    # Registra el nombre de un jugador humano o lo marca como bot
    def registrarNombre(self, nombre: str, indice: int = None) -> tuple[bool, str]:
        # CU-03. Un nombre None indica un jugador controlado por la consola (alternativa C).
        # Toma la partida actual
        partida = self.partidaActual
        # Si el nombre es None, se registra como bot de la computadora
        if nombre is None:
            registrado = partida.registrarJugadorConsola(indice)
        # Si es un nombre humano, lo valida y lo registra
        else:
            registrado = partida.validarNombre(nombre, indice) and partida.registrarNombre(nombre, indice)
        # Si se registró exitosamente, devuelve True
        if registrado:
            return True, "Nombre registrado."
        # Si el nombre estaba en blanco, avisa cuál jugador fue
        if nombre is not None and not nombre.strip():
            numero = indice + 1 if indice is not None else partida.numeroJugadores()
            return False, f"El nombre del Jugador {numero} no puede estar vacío."
        # Si falló por repetición, avisa que no se permiten repetidos
        return False, "No se permiten nombres repetidos."

    # Devuelve la lista de colores que todavía están disponibles
    def seleccionarColores(self) -> list:
        # DS N4 pasos 1 a 4: colores disponibles.
        # Consulta los colores libres a la partida actual
        return self.partidaActual.seleccionarColores()

    # Asigna un color seleccionado a un jugador
    def seleccionarColor(self, color, indice: int = None) -> tuple[bool, str]:
        # DS N4 pasos 5 a 8 (alternativa A: color no disponible).
        # Si se pudo asignar en la partida, devuelve éxito
        if self.partidaActual.seleccionarColor(color, indice):
            return True, "Color asignado."
        # Si ya estaba ocupado, devuelve el mensaje de advertencia
        return False, "Ese color ya está asignado: selecciona otro color."

    # Cancela la elección de colores y vuelve al menú
    def cancelarSeleccionColores(self) -> None:
        # DS N4 alternativa B: se descarta la selección y se vuelve al menú principal.
        # Si hay partida, cancela la selección de colores
        if self.partidaActual:
            self.partidaActual.cancelarSeleccionColores()
        # Cancela toda la partida
        self.cancelarPartida()

    def seleccionarPausar(self) -> bool:
        if self.partidaActual:
            self.partidaActual.pausar()
            return True 
        return False

    # Cancela la partida activa y libera la memoria
    def cancelarPartida(self) -> None:
        # DS N4 alternativa B: se descarta la selección y se vuelve al menú principal.
        if self.partidaActual:
            self.partidaActual.cancelarPartida()
        self.partidaActual = None

    # ------------------------------------------------------------------
    # Juego (CU-07 a CU-09 y CU-13)
    # ------------------------------------------------------------------

    # Lanza el dado de la partida actual y devuelve el número obtenido
    def lanzarDado(self) -> int:
        # Si hay partida tira el dado, si no devuelve 0
        return self.partidaActual.lanzarDado() if self.partidaActual else 0

    # Selecciona una ficha y, si pertenece al jugador del turno, la mueve
    def seleccionarFicha(self, ficha: Ficha) -> bool:
        # Obtiene al jugador actual
        jugador = self.partidaActual.obtenerJugadorActual() if self.partidaActual else None
        # Verifica que el jugador exista y que la ficha sea de él
        if jugador is None or jugador.seleccionarFicha(ficha) is None:
            return False
        # Mueve la ficha seleccionada
        return self.moverFicha(ficha)

    # Ordena a la partida mover la ficha seleccionada
    def moverFicha(self, ficha: Ficha) -> bool:
        # Llama a moverFicha en la partida si existe
        return self.partidaActual.moverFicha(ficha) if self.partidaActual else False

    # Termina la partida actual
    def finalizarPartida(self) -> None:
        # Si hay partida y no está finalizada, la finaliza
        if self.partidaActual and self.partidaActual.estado != "FINALIZADA":
            self.partidaActual.finalizar()

    # ------------------------------------------------------------------
    # Pausa, reglas y estadísticas (CU-06, CU-10 y CU-15)
    # ------------------------------------------------------------------

    # Pausa la partida en curso
    def pausarPartida(self) -> None:
        # Si hay partida activa, llama a pausar()
        if self.partidaActual:
            self.partidaActual.pausar()

    # Reanuda la partida que estaba pausada
    def reanudarPartida(self) -> None:
        # Si hay partida, llama a reanudar()
        if self.partidaActual:
            self.partidaActual.reanudar()

    # Pide el texto de las reglas a la persistencia
    def consultarReglas(self) -> str:
        # CU-06: el texto se obtiene de la persistencia ("" si no se pudo cargar).
        # Lee las reglas desde el archivo de texto
        return PersistenciaDeDatos().obtenerReglas()

    # Comprueba si al cerrar las reglas hay una partida a la que regresar
    def volverDeReglas(self) -> bool:
        # Devuelve True si hay una partida activa a la que volver.
        # Verifica si hay partida y si está activa
        return bool(self.partidaActual and self.partidaActual.verificarPartidaActiva())

    # Devuelve el texto resumen con las estadísticas de la partida actual
    def verEstadisticas(self) -> str:
        # Si hay partida recopila estadísticas, si no devuelve vacío
        return self.partidaActual.recopilarEstadisticas() if self.partidaActual else ""

    # Cierra las estadísticas y verifica si se puede volver a la partida
    def volver(self) -> bool:
        # Cierra la pantalla de estadísticas; True si se vuelve a una partida activa.
        # Retorna True si la partida sigue en curso o pausada
        return bool(self.partidaActual and self.partidaActual.cerrarPantallaEstadisticas())


    # ------------------------------------------------------------------
    # Cancelar, reiniciar y salir (CU-01, CU-11 y CU-12)
    # ------------------------------------------------------------------

    # Cancela la partida y libera la memoria
    def cancelarPartida(self) -> None:
        # Si hay una partida activa:
        if self.partidaActual:
            # Llama a cancelar en la partida
            self.partidaActual.cancelarPartida()
        # Vuelve la referencia a None
        self.partidaActual = None

    # Reinicia la partida desde cero volviendo a la pantalla de configuración
    def reiniciarPartida(self) -> None:
        # CU-11: se descarta la partida y se vuelve a configurar (CU-02 a CU-04).
        # Si hay partida activa:
        if self.partidaActual:
            # Borra los datos de la partida
            self.partidaActual.descartarDatos()
        # Deja la partida actual vacía
        self.partidaActual = None
        # Inicia una nueva configuración
        self.iniciarPartida()

    # Confirma el reinicio consultando la acción y reiniciando
    def confirmarReinicio(self) -> None:
        # Obtiene al jugador actual
        jugador = self.partidaActual.obtenerJugadorActual() if self.partidaActual else None
        # Si no hay jugador o este confirma la acción, se reinicia
        if jugador is None or jugador.confirmarAccion():
            self.reiniciarPartida()

    # Cancela el reinicio manteniendo la partida tal como estaba
    def cancelarReinicio(self) -> None:
        # CU-11 A 3.a: la partida sigue sin modificaciones.
        # Si hay partida, mantiene su estado
        if self.partidaActual:
            self.partidaActual.mantenerPartida()

    def confirmarAbandono(self) -> None:
        # Si hay partida, la cierra
        if self.partidaActual:
            self.partidaActual.cerrarPartida()
        # Limpia la variable de la partida
        self.partidaActual = None   

    def cancelarAbandono(self):
        # Si hay partida, la pausa
        if self.partidaActual:
            self.partidaActual.pausar()
        # Vuelve la referencia a None
        self.partidaActual = None

    # Comprueba si se debe pedir confirmación antes de volver al menú principal
    def volverAlMenuPrinicipal(self) -> bool:
        # CU-12: devuelve True si hay que pedir confirmación (partida activa).
        # Sin partida activa (A 3.b) se vuelve directamente al menú.
        # Si la partida requiere confirmación, devuelve True para que la interfaz muestre el cartel
        if self.partidaActual and self.partidaActual.solicitarConfirmacion():
            return True
        # Si no había partida activa, limpia la referencia y devuelve False
        self.partidaActual = None
        return False

    # Confirma la salida al menú cerrando la partida y descartando datos
    def confirmarSalida(self) -> None:
        # CU-12 paso 4: se descartan los datos de la partida.
        # Si hay partida, la cierra
        if self.partidaActual:
            self.partidaActual.cerrarPartida()
        # Limpia la variable de la partida
        self.partidaActual = None

    # Cancela la salida al menú manteniendo la partida activa
    def cancelarSalida(self) -> None:
        # Si hay partida, mantiene el estado
        if self.partidaActual:
            self.partidaActual.mantenerPartida()

    # ------------------------------------------------------------------
    # Guardar y reanudar (CU-14)
    # ------------------------------------------------------------------

    # Guarda la partida actual en el archivo a través de la persistencia
    def guardarPartida(self) -> tuple[bool, str]:
        # Si no hay partida para guardar, devuelve False
        if not self.partidaActual:
            return False, "No hay ninguna partida para guardar."
        # Llama a guardarPartida en la clase PersistenciaDeDatos
        return PersistenciaDeDatos().guardarPartida(self.partidaActual)

    # Guarda la partida y sale de ella
    def guardarYSalir(self) -> tuple[bool, str]:
        # Intenta guardar la partida
        exito, mensaje = self.guardarPartida()
        # Si se guardó con éxito:
        if exito:
            # Quita la partida actual de la memoria
            self.partidaActual = None
        # Devuelve el resultado y el mensaje
        return exito, mensaje

    # Confirma la acción de guardar y salir
    def confirmarGuardado(self) -> tuple[bool, str]:
        # Ejecuta la función de guardar y salir
        return self.guardarYSalir()

    # Cancela la solicitud de guardado manteniendo la partida
    def cancelarGuardado(self) -> None:
        # CU-14 A 1.a: se descarta la solicitud y la partida sigue igual.
        # Si hay partida, mantiene su estado
        if self.partidaActual:
            self.partidaActual.mantenerPartida()

    # CU-02: Modifica la cantidad de jugadores según el parámetro ('+' o '-'), como indica el diagrama modificarCantidad(+ / -)
    def modificarCantidad(self, signo: str = "+", *args) -> int:
        # Si se pasa primero una cantidad numérica y luego el signo
        if len(args) >= 1 and isinstance(signo, (int, float)):
            cantidad = int(signo)
            op = str(args[0]).strip()
        else:
            # Obtiene la cantidad actual de jugadores de la partida (mínimo 2 por defecto)
            actual = 2
            if hasattr(self, 'partidaActual') and self.partidaActual:
                cant_attr = getattr(self.partidaActual, 'cantidadJugadores', 0)
                num_jug = self.partidaActual.numeroJugadores() if hasattr(self.partidaActual, 'numeroJugadores') else 0
                if cant_attr in (2, 3, 4):
                    actual = cant_attr
                elif num_jug in (2, 3, 4):
                    actual = num_jug
            cantidad = actual
            op = str(signo).strip()

        # Determina si suma o resta según el parámetro ('+' o '-')
        if op in ("-", "_", "-1", -1):
            delta = -1
        else:
            delta = 1

        # Calcula la nueva cantidad de jugadores
        cantidad_nueva = cantidad + delta

        # Valida que la cantidad se mantenga entre 2 y 4 jugadores
        if 2 <= cantidad_nueva <= 4:
            resultado = cantidad_nueva
        else:
            resultado = cantidad

        # Si hay una partida en configuración, sincroniza la cantidad
        if hasattr(self, 'partidaActual') and self.partidaActual and hasattr(self.partidaActual, 'configurarCantidadJugadores'):
            self.partidaActual.configurarCantidadJugadores(resultado)

        return resultado

    # Alias por compatibilidad
    modificarCantuidad = modificarCantidad


    # Reanuda una partida guardada previamente en el archivo JSON
    def reanudarPartidaGuardada(self, numero: int = 0) -> tuple[bool, str]:
        # CU-14: puede haber varias partidas guardadas; numero 0 es la más reciente.
        # Crea la instancia de PersistenciaDeDatos
        persistencia = PersistenciaDeDatos()
        # Comprueba si existe alguna partida guardada
        if not persistencia.existePartidaGuardada():
            return False, "No existe ninguna partida guardada."
        # Intenta cargar la partida guardada
        partida, mensaje = persistencia.cargarPartida(numero)
        # Si no se pudo cargar, devuelve el error
        if partida is None:
            return False, mensaje
        # Asigna la partida cargada como la partida actual
        self.partidaActual = partida
        # Retorna éxito con su mensaje
        return True, mensaje

   



#init(): Prepara el gestor y deja la partida actual vacía.
#iniciarPartida(): Crea una partida nueva, revisa los datos, la inicia y la guarda.
#configurarCantidadJugadores(): Elige cuántos jugadores participan. Deben ser entre 2 y 4.
#registrarNombre(): Guarda el nombre de un jugador o indica que lo controla la computadora. También revisa que el nombre no esté vacío ni repetido.
#seleccionarColores(): Muestra los colores disponibles.
#seleccionarColor(): Le da un color a un jugador y revisa que no esté ocupado.
#cancelarSeleccionColores(): Cancela la elección de colores y termina la configuración.
#lanzarDado(): Tira el dado y devuelve el número que salió.
#seleccionarFicha(): Revisa si se puede elegir una ficha y, si se puede, la mueve.
#moverFicha(): Mueve una ficha por el tablero.
#finalizarPartida(): Termina la partida.
#pausarPartida(): Detiene la partida por un momento.
#reanudarPartida(): Continúa la partida pausada.
#consultarReglas(): Busca y devuelve las reglas del juego.
#volverDeReglas(): Revisa si hay una partida en curso para volver a ella.
#verEstadisticas(): Muestra los datos de la partida, como los movimientos y los resultados.
#volver(): Cierra las estadísticas y permite volver a la partida si sigue activa.
#cancelarPartida(): Cancela la partida actual.
#reiniciarPartida(): Borra los datos de la partida actual y permite empezar de nuevo.
#confirmarReinicio(): Confirma el reinicio y comienza la configuración de una nueva partida.
#cancelarReinicio(): Cancela el reinicio y deja la partida como estaba.
#volverAlMenuPrinicipal(): Comprueba si hay que confirmar antes de volver al menú principal.
#confirmarSalida(): Cierra la partida y descarta sus datos actuales.
#cancelarSalida(): Cancela la salida y deja la partida como estaba.
#guardarPartida(): Guarda la partida actual.
#guardarYSalir(): Guarda la partida y, si se guarda correctamente, sale de ella.
#confirmarGuardado(): Confirma el guardado y la salida.
#cancelarGuardado(): Cancela el guardado y mantiene la partida como estaba.
#reanudarPartidaGuardada(): Busca una partida guardada, la carga y permite continuar jugando.
#En resumen: game_manager.py controla las acciones principales del juego. Se encarga de iniciar partidas, mover fichas, pausar, guardar, reiniciar y volver a jugar partidas guardadas.