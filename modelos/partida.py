# Importa random para generar números al azar (tiradas de dado)
from ast import Pass
import random
# Importa time para medir el tiempo transcurrido de la partida
import time

# Importa el enum de Color
from modelos.color import Color
# Importa la clase Ficha
from modelos.ficha import Ficha
# Importa la clase Jugador
from modelos.jugador import Jugador
# Importa la clase Tablero
from modelos.tablero import Tablero


# Representa una partida completa de Ludo con sus reglas, jugadores y estado
class Partida:

    # Constructor: inicializa los datos y variables del juego
    def __init__(self, datosConfiguracion: dict = None):
        # Crea el tablero de juego
        self.tablero = Tablero()
        # Valor actual del dado (0 significa que aún no se lanzó en este turno)
        self.dado = 0
        # Número de jugadores en la partida (entre 2 y 4)
        self.cantidadJugadores = 0
        # Estado actual: NO_INICIADA, CONFIGURACION, EN_CURSO, PAUSADA, FINALIZADA, etc.
        self.estado = "NO_INICIADA"
        # Lista de colores que todavía no fueron elegidos
        self.coloresDisponibles = list(Color)
        # Lista de objetos Jugador que participan
        self.jugadores = []
        # Referencia al jugador al que le toca jugar en este turno
        self.jugadorActual = None
        # Jugador que ganó la partida (si ya terminó)
        self.ganador = None
        # Índice (posición en la lista) del jugador actual
        self.turnoActual = 0
        # Contador total de turnos que se jugaron
        self.turnosJugados = 0
        # Segundos jugados acumulados
        self.tiempoTranscurrido = 0
        # Contador de cuántas veces consecutivas salió el número 6
        self._seisConsecutivos = 0
        # Marca de tiempo en segundos para calcular el tiempo transcurrido
        self._inicioTiempo = None

        # Si se pasaron datos de configuración iniciales:
        if datosConfiguracion:
            # DS N5: «create»(datosConfiguracion) y un Jugador por cada participante configurado.
            # Lee la cantidad de jugadores configurada
            self.cantidadJugadores = datosConfiguracion.get("cantidadJugadores", 0)
            # Recorre la lista de jugadores y los agrega
            for datos in datosConfiguracion.get("jugadores", []):
                self.jugadores.append(Jugador((datos.get("nombre") or "").strip(), datos.get("color")))
            # Actualiza los colores disponibles
            self.obtenerColoresDisponibles()

    # ------------------------------------------------------------------
    # Configuración (CU-01 a CU-05, DS N1, N4 y N5)
    # ------------------------------------------------------------------

    # Pone la partida en estado de configuración y vacía los jugadores
    def iniciarConfiguracion(self) -> None:
        # Cambia el estado a configuración
        self.estado = "CONFIGURACION"
        # Vacía la lista de jugadores
        self.jugadores = []
        # Pone la cantidad de jugadores en 0
        self.cantidadJugadores = 0
        # Recalcula los colores disponibles
        self.obtenerColoresDisponibles()

    # Devuelve cuántos jugadores hay registrados actualmente
    def numeroJugadores(self) -> int:
        # Retorna el tamaño de la lista de jugadores
        return len(self.jugadores)

    # Añade un nuevo jugador vacío a la partida
    def añadirJugador(self) -> bool:
        # Si ya hay 4 jugadores, no se puede añadir más
        if self.numeroJugadores() >= 4:
            return False
        # Agrega un nuevo Jugador a la lista
        self.jugadores.append(Jugador())
        # Actualiza la cantidad total de jugadores
        self.cantidadJugadores = self.numeroJugadores()
        # Devuelve True indicando éxito
        return True

    # Quita al último jugador de la lista
    def eliminarJugador(self) -> bool:
        # Si hay 2 o menos, no se puede quitar porque el mínimo es 2
        if self.numeroJugadores() <= 2:
            return False
        # Elimina el último jugador
        self.jugadores.pop()
        # Actualiza la cantidad de jugadores
        self.cantidadJugadores = self.numeroJugadores()
        # Recalcula los colores disponibles
        self.obtenerColoresDisponibles()
        # Devuelve True indicando éxito
        return True

    # Ajusta la lista de jugadores para que coincida con la cantidad pedida (2 a 4)
    def configurarCantidadJugadores(self, cantidad: int) -> bool:
        # CU-02: se agregan o quitan jugadores hasta llegar a la cantidad (2 a 4).
        # Verifica que la cantidad esté entre 2 y 4
        if not 2 <= cantidad <= 4:
            return False
        # Si faltan jugadores, añade de a uno
        while self.numeroJugadores() < cantidad:
            self.añadirJugador()
        # Si sobran jugadores, quita de a uno
        while self.numeroJugadores() > cantidad:
            self.eliminarJugador()
        # Guarda la cantidad final
        self.cantidadJugadores = cantidad
        # Actualiza los colores disponibles
        self.obtenerColoresDisponibles()
        # Retorna True indicando que se configuró correctamente
        return True

    # Verifica que el nombre no esté vacío ni repetido entre los jugadores
    def validarNombre(self, nombre: str, indice: int = None) -> bool:
        # CU-03: el nombre no puede estar vacío ni repetirse con el de otro jugador.
        # Comprueba que el texto no sea nulo ni puros espacios
        if not nombre or not nombre.strip():
            return False
        # Obtiene los nombres de los demás jugadores (excluyendo el que se está editando)
        otros = [j.nombre for i, j in enumerate(self.jugadores) if i != indice and j.nombre]
        # Devuelve True si el nombre limpio no está repetido
        return nombre.strip() not in otros

    # Guarda el nombre en el jugador correspondiente
    def registrarNombre(self, nombre: str, indice: int = None) -> bool:
        # Sin índice se registra en el primer jugador que todavía no tiene nombre.
        if indice is None:
            # Busca el primer jugador con nombre vacío
            indice = next((i for i, j in enumerate(self.jugadores) if not j.nombre), None)
        # Si el índice no existe o el nombre no es válido, devuelve False
        if indice is None or not 0 <= indice < len(self.jugadores) or not self.validarNombre(nombre, indice):
            return False
        # Guarda el nombre sin espacios extra
        self.jugadores[indice].nombre = nombre.strip()
        # Retorna True indicando éxito
        return True

    # Registra un jugador automático controlado por la computadora
    def registrarJugadorConsola(self, indice: int = None) -> bool:
        # CU-03 C: el jugador controlado por la consola recibe un nombre "Bot n".
        # Si no se pasó índice, busca el primer jugador sin nombre
        if indice is None:
            indice = next((i for i, j in enumerate(self.jugadores) if not j.nombre), None)
        # Si no encontró ningún jugador disponible, retorna False
        if indice is None:
            return False
        # Registra el nombre con el formato "Bot 1", "Bot 2", etc.
        return self.registrarNombre(f"Bot {indice + 1}", indice)

    # Devuelve la lista de colores disponibles para seleccionar
    def seleccionarColores(self) -> list[Color]:
        # CU-04 pasos 2 y 3: colores que todavía puede elegir un jugador.
        # Retorna los colores que aún no fueron tomados
        return self.obtenerColoresDisponibles()

    # Recalcula y devuelve qué colores no han sido asignados a ningún jugador
    def obtenerColoresDisponibles(self) -> list[Color]:
        # Lista los colores que ya tienen asignados los jugadores
        ocupados = [j.getColor() for j in self.jugadores]
        # Filtra los colores del juego que no estén ocupados
        self.coloresDisponibles = [c for c in list(Color) if c not in ocupados]
        # Retorna la lista resultante
        return self.coloresDisponibles

    # Comprueba si un color específico está libre para ser elegido
    def validarColor(self, color: Color) -> bool:
        # Devuelve True si el color está en la lista de disponibles
        return color in self.obtenerColoresDisponibles()

    # Asigna un color a un jugador si el color está libre
    def asignarColor(self, jugador: Jugador, color: Color) -> bool:
        # Si el color no está disponible, devuelve False
        if not self.validarColor(color):
            return False
        # Asigna el color al jugador
        jugador.asignarColor(color)
        # Actualiza la lista de colores disponibles
        self.obtenerColoresDisponibles()
        # Retorna True
        return True

    # Elige un color para un jugador por su índice o para el primero sin color
    def seleccionarColor(self, color: Color, indice: int = None) -> bool:
        # Sin índice el color es para el primer jugador que todavía no tiene uno.
        if indice is None:
            # Encuentra el primer jugador que no tenga color
            indice = next((i for i, j in enumerate(self.jugadores) if j.getColor() is None), None)
        # Si no hay índice válido, retorna False
        if indice is None or not 0 <= indice < len(self.jugadores):
            return False
        # Obtiene al jugador
        jugador = self.jugadores[indice]
        # Si ya tiene ese color o se le pudo asignar, retorna True
        return jugador.getColor() == color or self.asignarColor(jugador, color)

    # Verifica si todos los jugadores tienen un color asignado y distinto
    def todosLosColoresAsignados(self) -> bool:
        # Obtiene la lista de colores de todos los jugadores
        colores = [j.getColor() for j in self.jugadores]
        # Comprueba que la cantidad coincida, que no haya None y que no haya colores repetidos
        return (len(self.jugadores) == self.cantidadJugadores and None not in colores
                and len(colores) == len(set(colores)))

    # Desasigna los colores de todos los jugadores y los deja disponibles
    def cancelarSeleccionColores(self) -> None:
        # Recorre cada jugador y le quita el color
        for jugador in self.jugadores:
            jugador.asignarColor(None)
        # Vuelve a marcar todos los colores como disponibles
        self.obtenerColoresDisponibles()


    # Valida que la configuración de la partida cumpla todas las reglas antes de empezar
    def validarConfiguracion(self) -> str:
        # DS N5: devuelve "" si la configuración es válida o el motivo si no lo es.
        # Lista los nombres de los jugadores
        nombres = [j.nombre for j in self.jugadores]
        # Verifica que la cantidad de jugadores esté entre 2 y 4
        if not 2 <= self.cantidadJugadores <= 4 or len(self.jugadores) != self.cantidadJugadores:
            return "La cantidad de participantes debe estar entre 2 y 4."
        # Verifica que ningún jugador tenga el nombre vacío
        if "" in nombres:
            return f"El nombre del Jugador {nombres.index('') + 1} no puede estar vacío."
        # Verifica que no haya nombres duplicados
        if len(nombres) != len(set(nombres)):
            return "No se permiten nombres repetidos."
        # Verifica que cada jugador tenga un color asignado
        if None in [j.getColor() for j in self.jugadores]:
            return "Cada jugador debe tener un color asignado."
        # Verifica que todos los colores sean distintos
        if not self.todosLosColoresAsignados():
            return "Cada jugador debe tener un color diferente."
        # Si no hubo errores, devuelve un texto vacío
        return ""

    # ------------------------------------------------------------------
    # Inicio y turnos (CU-05, CU-07 a CU-09, DS N1, N5, N8 y N9)
    # ------------------------------------------------------------------

    # Inicia la partida dejando el tablero listo y los jugadores en sus posiciones iniciales
    def iniciar(self) -> None:
        # DS N1: al crear la partida se inicializa el tablero y empieza la configuración.
        # DS N5: con los jugadores ya configurados, la partida comienza.
        # Crea una nueva instancia del tablero
        self.tablero = Tablero()
        # Inicializa las casillas del tablero
        self.tablero.inicializar()
        # Si aún no hay jugadores creados, entra en modo configuración
        if not self.jugadores:
            self.iniciarConfiguracion()
            return
        # Reinicia los contadores y fichas de cada jugador
        for jugador in self.jugadores:
            # Pone en 0 los movimientos del jugador
            jugador.movimientos = 0
            # Pone en 0 el puntaje del jugador
            jugador.puntaje = 0
            # Manda todas las fichas de vuelta a la base
            for ficha in jugador.obtenerFichas():
                ficha.volverBase()
        # Asigna el turno al primer jugador
        self.establecerPrimerTurno()
        # Cambia el estado a juego en curso
        self.estado = "EN_CURSO"
        # Empieza en el turno número 1
        self.turnosJugados = 1
        # Pone el tiempo jugado en 0 segundos
        self.tiempoTranscurrido = 0
        # Guarda la hora de inicio para el cronómetro
        self._inicioTiempo = time.time()

    # Prepara el turno para el primer jugador de la lista
    def establecerPrimerTurno(self) -> None:
        # Pone el índice de turno en 0
        self.turnoActual = 0
        # Selecciona al primer jugador de la lista
        self.jugadorActual = self.jugadores[0] if self.jugadores else None
        # Pone el dado en 0 (sin tirar)
        self.dado = 0
        # Reinicia el contador de números 6 seguidos
        self._seisConsecutivos = 0

    # Lanza el dado y determina si el jugador puede mover o si pasa el turno
    def lanzarDado(self) -> int:
        # Si el juego no está en curso o ya se tiró el dado en este turno, devuelve el valor actual
        if self.estado != "EN_CURSO" or self.dado:
            return self.dado
        # Genera un número aleatorio entre 1 y 6
        valor = random.randint(1, 6)
        # Guarda el número obtenido en el atributo dado
        self.dado = valor
        # Obtiene al jugador que está jugando actualmente
        jugador = self.obtenerJugadorActual()

        # Si salió un 6, suma al contador de 6 seguidos; si no, lo reinicia a 0
        self._seisConsecutivos = self._seisConsecutivos + 1 if valor == 6 else 0
        # Si sacó tres 6 seguidos:
        if self._seisConsecutivos == 3:
            # CU-08 A10: el tercer 6 consecutivo no se usa y el turno pasa.
            # Pasa el turno al siguiente jugador como penalización
            self.siguienteTurno()
        # Si el jugador no tiene ningún movimiento posible con ese número:
        elif jugador is None or not jugador.tieneMovimientosValidos(valor, self.tablero):
            # CU-08 A1: sin movimientos válidos el turno pasa al siguiente jugador.
            # Pasa automáticamente el turno
            self.siguienteTurno()
        # Devuelve el valor que sacó el dado
        return valor

    # Devuelve el jugador que tiene el turno actual
    def obtenerJugadorActual(self) -> Jugador:
        # Verifica que el índice de turno sea válido
        if 0 <= self.turnoActual < len(self.jugadores):
            # Asigna y devuelve el jugador correspondiente
            self.jugadorActual = self.jugadores[self.turnoActual]
            return self.jugadorActual
        # Si no hay jugador válido, devuelve None
        return None

    # Devuelve las fichas del jugador actual que pueden moverse con el valor del dado
    def obtenerMovimientosValidos(self) -> list[Ficha]:
        # DS N8: fichas del jugador actual que pueden moverse con el valor del dado.
        # Obtiene el jugador actual
        jugador = self.obtenerJugadorActual()
        # Si no hay jugador o no se tiró el dado, no hay movimientos válidos
        if jugador is None or not self.dado:
            return []
        # Le pide al tablero las fichas que pueden moverse
        return self.tablero.obtenerMovimientosValidos(jugador, self.dado)

    # Saca una ficha de la base hacia la casilla de salida
    def sacarFicha(self, ficha: Ficha) -> bool:
        # CU-07: con un 6 la ficha sale de la base a la casilla de salida de su color.
        # Delega la acción en el tablero
        return self.tablero.sacarFicha(ficha)

    # Mueve la ficha seleccionada y gestiona capturas, metas y cambios de turno
    def moverFicha(self, ficha: Ficha) -> bool:
        # DS N8 y N9: puedeMover → calcularDestino → moverFicha → verificarCaptura →
        # verificarMeta → todasLasFichasEnMeta → finalizar o administrarTurno.
        # Obtiene al jugador actual
        jugador = self.obtenerJugadorActual()
        # Verifica que el juego esté en curso, haya jugador y la ficha le pertenezca
        if self.estado != "EN_CURSO" or jugador is None or ficha not in jugador.obtenerFichas():
            return False
        # Verifica que el tablero permita mover esa ficha con el dado
        if not self.tablero.puedeMover(ficha, self.dado):
            return False

        # Calcula la casilla final del movimiento
        destino = self.tablero.calcularDestino(ficha, self.dado)
        # Si la ficha estaba en la base, la saca
        if ficha.enBase:
            self.sacarFicha(ficha)
        # Si ya estaba en juego, la mueve hasta el destino
        else:
            self.tablero.moverFicha(ficha, destino)
        # Comprueba si capturó alguna ficha rival en esa casilla
        self.tablero.verificarCaptura(ficha)
        # Comprueba si la ficha llegó a la meta
        self.tablero.verificarMeta(ficha)
        # Suma un movimiento al contador del jugador
        jugador.movimientos += 1

        # Si el jugador logró que todas sus fichas lleguen a la meta:
        if self.verificarGanador():
            # Finaliza la partida
            self.finalizar()
        # Si todavía no hay ganador, administra a quién le toca jugar
        else:
            self.administrarTurno()
        # Retorna True indicando que el movimiento fue exitoso
        return True

    # Administra los turnos: si salió 6 vuelve a tirar, si no pasa al siguiente jugador
    def administrarTurno(self) -> None:
        # Con un 6 el mismo jugador vuelve a tirar (CU-08 A9); si no, pasa el turno.
        # Si sacó un 6:
        if self.dado == 6:
            # Resetea el dado a 0 para que pueda volver a tirar
            self.dado = 0
        # Si no sacó 6:
        else:
            # Pasa el turno al siguiente jugador
            self.siguienteTurno()

    # Avanza el turno al siguiente jugador de la lista
    def siguienteTurno(self) -> None:
        # Si no hay jugadores, no hace nada
        if not self.jugadores:
            return
        # Suma uno al contador total de turnos
        self.turnosJugados += 1
        # Calcula el siguiente índice de forma circular
        self.turnoActual = (self.turnoActual + 1) % len(self.jugadores)
        # Actualiza la referencia del jugador actual
        self.jugadorActual = self.jugadores[self.turnoActual]
        # Reinicia el dado para el nuevo turno
        self.dado = 0
        # Reinicia el contador de 6 seguidos
        self._seisConsecutivos = 0

    # Comprueba si algún jugador ya tiene sus 4 fichas en la meta
    def verificarGanador(self) -> bool:
        # Revisa a cada jugador
        for jugador in self.jugadores:
            # Si tiene todas sus fichas en la meta:
            if jugador.todasLasFichasEnMeta():
                # Lo declara como ganador
                self.ganador = jugador
                # Devuelve True indicando que hay ganador
                return True
        # Si ninguno ganó todavía, devuelve False
        return False

    # Finaliza la partida, recopila estadísticas y detiene el cronómetro
    def finalizar(self) -> None:
        # Calcula las estadísticas finales
        self.recopilarEstadisticas()
        # Cambia el estado a FINALIZADA
        self.estado = "FINALIZADA"
        # Detiene el cronómetro
        self._inicioTiempo = None

    # ------------------------------------------------------------------
    # Pausa, guardado, reinicio y salida (CU-10 a CU-15)
    # ------------------------------------------------------------------

    # Cancela la partida descartando los datos y volviendo al estado inicial
    def cancelarPartida(self) -> None:
        # CU-01 A y CU-04 B: se descarta lo configurado.
        # Borra todos los datos de la partida
        self.descartarDatos()
        # Pone el estado en NO_INICIADA
        self.estado = "NO_INICIADA"

    # Pausa la partida y guarda el tiempo transcurrido
    def pausarPartida(self) -> None:
        # Solo se puede pausar si la partida está en curso
        if self.estado == "EN_CURSO":
            # Guarda los segundos jugados hasta este momento
            self.conservarEstado()
            # Cambia el estado a PAUSADA
            self.estado = "PAUSADA"

    # Alias por compatibilidad
    pausar = pausarPartida

    # Reanuda la partida pausada y reinicia el cronómetro
    def reanudarPartida(self) -> None:
        # Si está pausada o en curso:
        if self.estado in ("PAUSADA", "EN_CURSO"):
            # Cambia el estado a EN_CURSO
            self.estado = "EN_CURSO"
            # Registra la hora actual para reanudar el cronómetro
            self._inicioTiempo = time.time()

    # Alias por compatibilidad
    reanudar = reanudarPartida

    def solicitarConfiguracion(self) -> None:      
        self.iniciarConfiguracion()
        return True

    def configurarCantidad(self, cantidad: int) -> bool:  
        if cantidad in (2, 3, 4):
            self.cantidadJugadores = cantidad
            self.estado = "CONFIGURACION"
            return True
        return False

    # Guarda el tiempo transcurrido acumulado y detiene el reloj
    def conservarEstado(self) -> None:
        # CU-10: el reloj se detiene y queda acumulado el tiempo jugado hasta la pausa.
        # Si el cronómetro estaba corriendo:
        if self._inicioTiempo:
            # Suma los segundos transcurridos desde que se reanudó
            self.tiempoTranscurrido += int(time.time() - self._inicioTiempo)
        # Apaga la marca de tiempo
        self._inicioTiempo = None

    def guardarCantidad(self) -> dict:
        return {
            "cantidadJugadores": self.cantidadJugadores,
            "estado": self.estado,
            "turnoActual": self.turnoActual,
            "dado": self.dado,
            "seisConsecutivos": self._seisConsecutivos,
            "turnosJugados": self.turnosJugados,
            "tiempoTranscurrido": self.tiempoTranscurrido,
            "jugadores": [
                {
                    "nombre": j.nombre,
                    "color": j.color.name if j.color else None,
                    "movimientos": j.movimientos,
                    "puntaje": j.puntaje,
                    "fichas": [
                        {
                            "posicion": f.posicion,
                            "enBase": f.enBase,
                            "meta": getattr(f, "enMeta", False),
                            "color": f.color.name
                        } for f in j.obtenerFichas()
                    ]
                } for j in self.jugadores
            ]
        }

    def verificarCantidad(self) -> bool:
        if(self.cantidadJugadores in (2, 3, 4)):
            print("ya esta el minimo")
            return True
        print(" falta jugadores")
        return False

    # Empaqueta todos los datos de la partida en un diccionario para guardarlo en un archivo
    def guardar(self) -> dict:
        # CU-14: estado completo de la partida que se pasa a la persistencia ("JSON Ludo").
        # Acumula el tiempo jugado hasta el momento de guardar
        self.conservarEstado()
        # Si la partida estaba en curso, reinicia la marca de tiempo para que continúe
        if self.estado == "EN_CURSO":
            self._inicioTiempo = time.time()
        # Devuelve el diccionario completo con todos los datos
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

    # Verifica si es necesario pedir confirmación al usuario antes de salir o reiniciar
    def solicitarConfirmacion(self) -> bool:
        # CU-11, CU-12 y CU-14: solo se pide confirmación si hay progreso que se perdería.
        # Devuelve True si la partida está activa (en curso o pausada)
        return self.verificarPartidaActiva()

    # Borra todos los datos de la partida y reinicia el tablero a su estado vacío
    def descartarDatos(self) -> None:
        # Vacía la lista de jugadores
        self.jugadores = []
        # Quita al jugador actual
        self.jugadorActual = None
        # Quita al ganador
        self.ganador = None
        # Pone el dado en 0
        self.dado = 0
        # Pone el tiempo transcurrido en 0
        self.tiempoTranscurrido = 0
        # Apaga el cronómetro
        self._inicioTiempo = None
        # Reinicia el tablero
        self.tablero.inicializar()
        # Vuelve a poner todos los colores como disponibles
        self.obtenerColoresDisponibles()

    # Mantiene la partida sin cambios cuando el usuario cancela una acción
    def mantenerPartida(self) -> bool:
        # El jugador canceló la acción: la partida sigue tal como estaba.
        # Devuelve si la partida sigue activa
        return self.verificarPartidaActiva()

    # Comprueba si la partida está en curso o pausada
    def verificarPartidaActiva(self) -> bool:
        # Retorna True si el estado es EN_CURSO o PAUSADA
        return self.estado in ("EN_CURSO", "PAUSADA")

    # Cierra definitivamente la partida y borra sus datos
    def cerrarPartida(self) -> None:
        # CU-12 paso 4: se descartan los datos de la partida y se vuelve al menú.
        # Borra los datos
        self.descartarDatos()
        # Cambia el estado a CERRADA
        self.estado = "CERRADA"

    # Genera un texto resumen con las estadísticas de la partida actual
    def recopilarEstadisticas(self) -> str:
        # CU-15: tiempo, turnos y resumen de cada jugador.
        # Toma el tiempo acumulado
        tiempo = self.tiempoTranscurrido
        # Si el cronómetro estaba corriendo, suma los segundos actuales
        if self._inicioTiempo:
            tiempo += int(time.time() - self._inicioTiempo)
        # Calcula el puntaje de cada jugador (100 puntos por ficha en meta o su posición)
        for jugador in self.jugadores:
            jugador.puntaje = sum(100 if f.enMeta else f.posicion for f in jugador.fichas)
        # Arma las líneas principales del informe
        lineas = [
            f"Tiempo transcurrido: {tiempo // 60:02d}:{tiempo % 60:02d}",
            f"Turnos jugados: {self.turnosJugados}",
            f"Ganador: {self.ganador.nombre if self.ganador else 'En curso'}",
        ]
        # Agrega las estadísticas de cada jugador
        lineas += [jugador.visualizarEstadisticas() for jugador in self.jugadores]
        # Une todas las líneas separadas por un salto de línea y las devuelve
        return "\n".join(lineas)
    
    # Vuelve de las reglas a la partida
    def volverDeReglas(self) -> bool:
        # Revisa si hay una partida en curso para volver a ella.
        return self.verificarPartidaActiva()

    # Cierra la pantalla de estadísticas y comprueba si la partida sigue activa
    def cerrarPantallaEstadisticas(self) -> bool:
        # Al cerrar las estadísticas se vuelve a la partida si sigue activa.
        # Retorna True si la partida sigue en curso o pausada
        return self.verificarPartidaActiva()
