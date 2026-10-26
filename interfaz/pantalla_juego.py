"""
Modulo pantalla_juego.py
Frame "Partida" del Figma: tablero en el centro con el nombre de cada jugador arriba
y abajo, un dado al costado de cada base, los botones REGLAS y PAUSA arriba a la
derecha y los mensajes de la partida debajo.
"""

# Funciones matemáticas para cálculos de distancias y ángulos
import math
# Módulo de números aleatorios para simular tiradas de dados
import random
# Librería Pygame para la interfaz visual
import pygame
# Importa la clase de colores del juego
from modelos.color import Color
# Importa el sistema de partículas para efectos visuales
from interfaz.efectos import SistemaParticulas
# Importa el tema visual con estilos y colores
from interfaz import tema
# Importa el componente de botones con diseño Figma
from interfaz.componentes import BotonFigma

# Diccionario de colores RGB para las fichas y elementos
COLOR_RGB = {
    # Color rojo en formato RGB
    Color.ROJO: (220, 50, 50),
    # Color azul en formato RGB
    Color.AZUL: (40, 120, 220),
    # Color verde en formato RGB
    Color.VERDE: (40, 180, 80),
    # Color amarillo en formato RGB
    Color.AMARILLO: (240, 190, 40)
}


# Esquina del tablero de cada color: 0 arriba-izq, 1 arriba-der, 2 abajo-izq, 3 abajo-der
# Diccionario que ubica la base de cada color en una esquina del tablero
ESQUINA_COLOR = {Color.ROJO: 0, Color.VERDE: 1, Color.AZUL: 2, Color.AMARILLO: 3}


# Obtiene la tupla RGB de un color del juego
def get_rgb(col):
    # Si es una instancia de la enumeración Color
    if isinstance(col, Color):
        # Devuelve el valor RGB correspondiente o gris por defecto
        return COLOR_RGB.get(col, (200, 200, 200))
    # Si ya es una tupla, la devuelve tal cual
    return col


# Clase principal que controla la pantalla donde se juega la partida
class PantallaJuego:

    # Constructor que inicializa los elementos del juego y la pantalla
    def __init__(self, pantalla, game_manager, interfaz_padre=None):
        # Guarda la ventana gráfica donde se dibuja todo
        self.pantalla = pantalla
        # Guarda el gestor de la lógica del juego
        self.gestor = game_manager
        # Guarda la referencia a la interfaz principal
        self.interfaz_padre = interfaz_padre
        # Referencia duplicada para compatibilidad
        self.interfaz = interfaz_padre
        # Mensaje actual para mostrar al usuario
        self.mensaje = ""
        # Sistema de partículas heredado o creado de nuevo
        self.particulas = interfaz_padre.particulas if interfaz_padre else SistemaParticulas()
        # Elimina las esferas flotantes de fondo para dejarlo plano
        self.particulas.orbes_fondo = []      # el fondo del Figma es liso

        # Coordenadas (fila, columna) de las 52 casillas del circuito principal
        self.GRID_CIRCUITO_52 = [
            (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (5, 6), (4, 6), (3, 6), (2, 6), (1, 6), (0, 6), (0, 7), (0, 8),
            (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 9), (6, 10), (6, 11), (6, 12), (6, 13), (6, 14), (7, 14), (8, 14),
            (8, 13), (8, 12), (8, 11), (8, 10), (8, 9), (9, 8), (10, 8), (11, 8), (12, 8), (13, 8), (14, 8), (14, 7), (14, 6),
            (13, 6), (12, 6), (11, 6), (10, 6), (9, 6), (8, 5), (8, 4), (8, 3), (8, 2), (8, 1), (8, 0), (7, 0), (6, 0)
        ]

        # Casillas del pasillo final hacia la meta para el color rojo
        self.GRID_META_ROJO = [(7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6)]
        # Casillas del pasillo final hacia la meta para el color verde
        self.GRID_META_VERDE = [(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7)]
        # Casillas del pasillo final hacia la meta para el color amarillo
        self.GRID_META_AMARILLO = [(7, 13), (7, 12), (7, 11), (7, 10), (7, 9), (7, 8)]
        # Casillas del pasillo final hacia la meta para el color azul
        self.GRID_META_AZUL = [(13, 7), (12, 7), (11, 7), (10, 7), (9, 7), (8, 7)]

        # Centros de los círculos de cada base en la imagen del tablero del Figma (fila, columna)
        # Posiciones de los 4 huecos en la base de cada color
        self.GRID_BASE = {
            Color.ROJO: [(1.91, 1.93), (1.91, 4.11), (4.16, 1.93), (4.16, 4.12)],
            Color.VERDE: [(1.91, 10.85), (1.91, 13.05), (4.16, 10.86), (4.17, 13.04)],
            Color.AMARILLO: [(10.83, 10.85), (10.83, 13.04), (13.08, 10.85), (13.08, 13.04)],
            Color.AZUL: [(10.83, 1.93), (10.83, 4.12), (13.08, 1.92), (13.09, 4.12)]
        }

        # Indica si el dado se está animando al rodar
        self.animando_dado = False
        # Cuadros restantes de la animación del dado
        self.frames_anim_dado = 0
        # Número temporal que muestra el dado mientras rueda
        self.dado_visual_temp = 1
        # Guarda la posición visual animada de cada ficha
        self.posiciones_fichas_anim = {}
        # Cola de casillas que la ficha debe recorrer en su animación
        self.colas_anim_pasos = {}
        # Contador para el brillo intermitente de fichas válidas
        self.ticks_glow = 0
        # Temporizador para dar una pausa antes de que juegue un bot
        self.timer_bot = 0

        # Mensaje inicial del relator de la partida
        self.mensaje_relator = "¡Partida iniciada! Lanza el dado para comenzar."
        # Ficha sobre la que está el mouse actualmente
        self.ficha_hover_activa = None
        # Rectángulo clickeable para lanzar el dado
        self.btn_lanzar = pygame.Rect(-100, -100, 0, 0)

    # Calcula las dimensiones y la escala del tablero en la ventana actual
    def _calcular_geometria(self):
        # Tablero del Figma: 752x752 en (198, 104), 15x15 casilleros
        # Obtiene el rectángulo del tablero escalado a la ventana
        tablero = tema.R(self.pantalla, 198, 104, 752, 752)
        # Calcula el tamaño de cada casillero dividiendo por 15
        self.tam_celda = tablero.width / 15.0
        # Guarda el ancho y alto del tablero
        self.ancho_tablero = self.alto_tablero = tablero.width
        # Guarda la esquina superior izquierda del tablero
        self.origen_x, self.origen_y = tablero.x, tablero.y

    # Dibuja todos los componentes visuales de la pantalla de juego
    def dibujar(self):
        # Obtiene la partida actual del gestor
        partida_actual = self.gestor.partidaActual
        # Si la partida cambió o es nueva
        if getattr(self, '_partida_ref', None) is not partida_actual:
            # Actualiza la referencia interna
            self._partida_ref = partida_actual
            # Limpia el mensaje
            self.mensaje = ""
            # Limpia las posiciones de animación de fichas
            self.posiciones_fichas_anim.clear()
            # Limpia las colas de animación
            self.colas_anim_pasos.clear()
            # Reinicia el temporizador de bots
            self.timer_bot = 0
            # Detiene la animación del dado
            self.animando_dado = False
            # Quita la ficha seleccionada con el cursor
            self.ficha_hover_activa = None

        # Incrementa el contador de brillo intermitente
        self.ticks_glow += 1
        # Calcula la escala y posición del tablero
        self._calcular_geometria()
        # Pinta el fondo oscuro de la pantalla
        self.pantalla.fill(tema.FONDO)

        # Actualiza y dibuja las partículas en pantalla
        self.particulas.actualizar_y_dibujar(self.pantalla)
        # Ejecuta la lógica del turno si le toca a un bot
        self._actualizar_turno_bot()
        # Dibuja la imagen del tablero con su borde
        self._dibujar_tablero_ludo()
        # Dibuja las etiquetas con nombres de los jugadores
        self._dibujar_etiquetas_jugadores()
        # Dibuja los dados indicadores al lado de cada base
        self._dibujar_dados_indicadores_jugadores()
        # Dibuja todas las fichas en sus posiciones actuales
        self._dibujar_fichas()
        # Dibuja el panel lateral con botones y mensajes
        self._dibujar_panel_derecho()

    # Controla automáticamente el turno cuando juega la computadora
    def _actualizar_turno_bot(self):
        # Obtiene la partida actual
        partida = self.gestor.partidaActual
        # Si no hay partida o no está en curso, no hace nada
        if not partida or partida.estado != "EN_CURSO":
            # Sale de la función
            return

        # Si alguna ficha todavía se está animando, espera a que termine
        if any(len(cola) > 0 for cola in self.colas_anim_pasos.values()):
            # Sale de la función
            return

        # Obtiene el jugador que tiene el turno actual
        jugador_act = partida.obtenerJugadorActual()
        # Si no hay jugador o no es un bot
        if not jugador_act or not tema.es_bot(jugador_act):
            # Reinicia el temporizador del bot
            self.timer_bot = 0
            # Sale de la función
            return

        # Avanza el reloj del bot para simular que piensa
        self.timer_bot += 1

        # Si aún no tiró el dado y no se está animando
        if not partida.dado and not self.animando_dado:
            # Espera 25 cuadros antes de tirar
            if self.timer_bot >= 25:
                # Inicia la animación de tirar el dado
                self.animando_dado = True
                # Configura 12 cuadros de giro
                self.frames_anim_dado = 12
                # Reinicia el temporizador
                self.timer_bot = 0

        # Si ya tiró el dado y no se está animando
        elif partida.dado and not self.animando_dado:
            # Espera 35 cuadros antes de mover la ficha
            if self.timer_bot >= 35:
                # Consulta qué movimientos válidos tiene disponibles
                movimientos_validos = partida.obtenerMovimientosValidos()
                # Si puede mover alguna ficha
                if movimientos_validos:
                    # Elige la mejor ficha con la lógica inteligente del bot
                    ficha_elegida = self._seleccionar_mejor_movimiento_bot(jugador_act, movimientos_validos, partida.tablero)
                    # Si eligió una ficha
                    if ficha_elegida:
                        # Realiza el movimiento de la ficha
                        self._jugar_ficha(ficha_elegida)
                # Reinicia el temporizador del bot
                self.timer_bot = 0

    # Lanza el dado a través del gestor y genera el mensaje explicativo
    def _lanzar_dado(self):
        # CU-07/CU-08: el mensaje se arma con lo que devolvió el GameManager.
        # Obtiene la partida actual
        partida = self.gestor.partidaActual
        # Guarda el jugador que está tirando
        jugador = partida.obtenerJugadorActual()
        # Pide al gestor lanzar el dado
        valor = self.gestor.lanzarDado()
        # Si el turno cambió de jugador automáticamente
        if partida.obtenerJugadorActual() is not jugador:
            # Si sacó tres 6 seguidos
            if valor == 6:
                # Muestra mensaje de penalización
                self.mensaje = f"¡3 seis seguidos! {jugador.nombre} pierde el turno."
            # Si sacó un número sin jugadas posibles
            else:
                # Muestra mensaje de que no puede mover
                self.mensaje = f"{jugador.nombre} sacó {valor} y no tiene movimientos válidos."
        # Si conserva el turno para mover ficha
        else:
            # Muestra el número obtenido e invita a elegir ficha
            self.mensaje = f"{jugador.nombre} sacó {valor}: elige una ficha."
        # Devuelve el valor numérico obtenido
        return valor

    # Mueve la ficha seleccionada y gestiona el resultado de la jugada
    def _jugar_ficha(self, ficha):
        # CU-08 y CU-09 (DS N8 y N9): el GameManager mueve la ficha elegida.
        # Obtiene la partida actual
        partida = self.gestor.partidaActual
        # Guarda el jugador actual
        jugador = partida.obtenerJugadorActual()
        # Guarda la posición donde estaba la ficha antes de mover
        pos_ant = ficha.posicion
        # Intenta mover la ficha en el gestor
        if not self.gestor.seleccionarFicha(ficha):
            # Si no era válida, sale retornando falso
            return False
        # Prepara la animación paso a paso entre la posición anterior y la nueva
        self._generar_pasos_animacion(ficha, pos_ant, ficha.posicion)
        # Si la partida terminó con este movimiento
        if partida.estado == "FINALIZADA":
            # CU-13: hay ganador, se muestra la pantalla de victoria
            # Finaliza la partida en el gestor
            self.gestor.finalizarPartida()
            # Lanza confeti en el centro del tablero para festejar
            self.particulas.emitir_confeti(self.origen_x + self.ancho_tablero // 2, self.origen_y + self.alto_tablero // 2, 120)
            # Cambia a la pantalla final de victoria
            self.interfaz.ir_a("FINAL")
        # Si el jugador sigue con el turno (por ejemplo por sacar 6)
        elif partida.obtenerJugadorActual() is jugador:
            # Muestra aviso de que vuelve a tirar
            self.mensaje = f"{jugador.nombre} sacó 6: vuelve a tirar."
        # Si el turno pasó al siguiente jugador
        else:
            # Muestra de quién es el nuevo turno
            self.mensaje = f"Turno de {partida.obtenerJugadorActual().nombre}."
        # Devuelve verdadero indicando jugada exitosa
        return True

    # Elige la jugada más conveniente para el bot (comer rivales, salir de base, avanzar)
    def _seleccionar_mejor_movimiento_bot(self, jugador, movimientos_validos: list, tablero):
        # Si no hay movimientos posibles, devuelve None
        if not movimientos_validos:
            # Sale sin ficha
            return None
        # Casilla de salida al circuito para cada color
        salida_colores = {Color.ROJO: 0, Color.VERDE: 13, Color.AMARILLO: 26, Color.AZUL: 39}
        # Obtiene la partida actual
        partida = self.gestor.partidaActual
        # Si la partida existe, busca primero si puede comer a un rival
        if partida:
            # Revisa cada ficha que se puede mover
            for f in movimientos_validos:
                # Si está en el circuito común
                if not f.enBase and not f.enMeta and f.posicion <= 51:
                    # Calcula la casilla donde caería
                    casilla_proy = (salida_colores.get(f.color, 0) + (f.posicion + 1 - 1)) % 52
                    # Revisa a los jugadores rivales
                    for jug_rival in partida.jugadores:
                        # Si no es del mismo color
                        if jug_rival.color != jugador.color:
                            # Revisa cada ficha rival
                            for f_rival in jug_rival.fichas:
                                # Si la ficha rival está en el circuito común
                                if not f_rival.enBase and not f_rival.enMeta and f_rival.posicion <= 51:
                                    # Calcula la casilla del rival
                                    c_rival = (salida_colores.get(f_rival.color, 0) + (f_rival.posicion - 1)) % 52
                                    # Si caería encima del rival
                                    if c_rival == casilla_proy:
                                        # Prioridad 1: come la ficha rival
                                        return f
        # Prioridad 2: sacar ficha de la base si sacó 6
        for f in movimientos_validos:
            # Si la ficha está en base
            if f.enBase:
                # Elige sacarla al tablero
                return f
        # Prioridad 3: entrar a la zona de meta
        for f in movimientos_validos:
            # Si entra a las casillas finales
            if f.posicion + 1 > 51:
                # Elige esa ficha
                return f
        # Prioridad 4: mover la ficha que esté más avanzada
        return sorted(movimientos_validos, key=lambda x: x.posicion, reverse=True)[0]

    # Crea la lista de posiciones intermedias para que la ficha camine casilla por casilla
    def _generar_pasos_animacion(self, ficha, pos_inicio, pos_fin):
        # Si no cambió de posición, no anima nada
        if pos_inicio == pos_fin:
            # Sale de la función
            return

        # Lista de coordenadas para cada paso
        pasos_coords = []
        # Si sale de la base a la primera casilla
        if pos_inicio == 0:
            # Obtiene las coordenadas de la casilla 1
            px, py = self._obtener_px_posicion(ficha, 1)
            # Agrega ese único paso
            pasos_coords.append((px, py))
        # Si avanza por el circuito
        else:
            # Recorre una a una las casillas intermedias
            for p in range(pos_inicio + 1, pos_fin + 1):
                # Obtiene las coordenadas de la casilla
                px, py = self._obtener_px_posicion(ficha, p)
                # Agrega el paso a la lista
                pasos_coords.append((px, py))
        # Para almacenar los pasos de una animación.
        #durante la animación, va tomando las posiciones en orden para mostrar cómo avanza la ficha.
        #1. La ficha aparece en la posición 1.
        #2. Avanza a la posición 2.
        #3. Avanza a la posición 3.
        #Así, el movimiento se muestra progresivamente,
        #en lugar de hacer que la ficha aparezca directamente en el destino. 
        
        # Guarda la lista de pasos para esta ficha
        self.colas_anim_pasos[ficha] = pasos_coords

    # Dibuja la imagen del tablero con su marco negro
    def _dibujar_tablero_ludo(self):
        # Imagen del tablero exportada del Figma, con su borde negro de 10
        # Crea el rectángulo del tamaño del tablero
        r = pygame.Rect(self.origen_x, self.origen_y, self.ancho_tablero, self.alto_tablero)
        # Dibuja la imagen del tablero en pantalla
        self.pantalla.blit(tema.imagen("tablero.png", r.size), r.topleft)
        # Calcula el grosor del marco exterior
        g = tema.T(self.pantalla, 10)
        # Dibuja el marco negro alrededor del tablero
        pygame.draw.rect(self.pantalla, tema.NEGRO, r.inflate(g, g), width=g)

    # Dibuja los nombres de los jugadores en las cuatro esquinas
    def _dibujar_etiquetas_jugadores(self):
        # Píldoras 303x61 con el borde del color de la esquina; la del turno se rellena de amarillo
        # Obtiene la partida actual
        partida = self.gestor.partidaActual
        # Si no hay partida, no dibuja nada
        if not partida:
            # Sale de la función
            return
        # Referencia a la pantalla
        p = self.pantalla
        # Coordenadas de las 4 esquinas del tablero
        posiciones = {0: (198, 26), 1: (647, 26), 2: (198, 873), 3: (647, 873)}
        # Obtiene el jugador que tiene el turno actual
        jug_act = partida.obtenerJugadorActual()
        # Recorre los jugadores activos
        for jug in partida.jugadores[:4]:
            # Obtiene la posición X e Y de su esquina
            x, y = posiciones[ESQUINA_COLOR.get(jug.color, 0)]
            # Crea el rectángulo redondeado de la etiqueta
            r = tema.R(p, x, y, 303, 61)
            # Rellena de amarillo si es su turno, o blanco si no
            relleno = (245, 223, 52) if jug is jug_act else tema.BLANCO   # #ffe100 al 76 % (Figma)
            # Dibuja el fondo de la píldora
            pygame.draw.rect(p, relleno, r, border_radius=r.height // 2)
            # Dibuja el borde con el color del jugador
            pygame.draw.rect(p, tema.COLOR_DADO[jug.color], r, width=tema.T(p, 6), border_radius=r.height // 2)
            # Escribe el nombre del jugador centrado en la píldora
            tema.texto_figma(p, jug.nombre, 0, 0, 40, trazo=6, centrado_en=(x + 151.5, y + 30.5))

    # Dibuja los dados situados al lado de cada base de jugador
    def _dibujar_dados_indicadores_jugadores(self):
        # Un dado de 95x95 al costado de cada base; el del jugador con el turno es el que
        # se lanza (CU-07), se pinta de naranja y muestra el valor obtenido.
        # Obtiene la partida actual
        partida = self.gestor.partidaActual
        # Referencia a la pantalla
        p = self.pantalla
        # Posiciones de los dados para cada esquina
        posiciones = {0: (86, 214), 1: (967, 214), 2: (86, 667), 3: (967, 667)}
        # Obtiene el jugador actual
        jug_act = partida.obtenerJugadorActual() if partida else None
        # Reinicia el botón clickeable del dado fuera de pantalla
        self.btn_lanzar = pygame.Rect(-100, -100, 0, 0)
        # Recorre los jugadores de la partida
        for jug in (partida.jugadores[:4] if partida else []):
            # Obtiene las coordenadas del dado
            x, y = posiciones[ESQUINA_COLOR.get(jug.color, 0)]
            # Crea el rectángulo del dado
            r = tema.R(p, x, y, 95, 95)
            # Valor por defecto a mostrar
            valor = 1
            # Color de fondo blanco por defecto
            fondo = tema.BLANCO
            # Si es el jugador que tiene el turno
            if jug is jug_act:
                # Hace clickeable este dado para tirar
                self.btn_lanzar = r
                # Si el dado está girando animado
                if self.animando_dado:
                    # Descuenta un cuadro de animación
                    self.frames_anim_dado -= 1
                    # Genera un número al azar para el efecto visual
                    self.dado_visual_temp = random.randint(1, 6)
                    # Si terminó la animación de giro
                    if self.frames_anim_dado <= 0:
                        # Detiene la animación
                        self.animando_dado = False
                        # Lanza formalmente el dado en el juego
                        self._lanzar_dado()
                        # Si sacó 6 emite estrellas brillantes
                        if partida.dado == 6:
                            self.particulas.emitir_estrellas(r.centerx, r.centery, 20)
                # Determina el número a dibujar en la cara del dado
                valor = self.dado_visual_temp if self.animando_dado else (partida.dado or 1)
                # Si aún no tiró el dado o está girando
                if not partida.dado or self.animando_dado:
                    # Resalta el dado en color naranja llamativo
                    fondo = tema.DADO_ACTIVO        # falta tirar: el dado se resalta
            # Dibuja el fondo del dado
            pygame.draw.rect(p, fondo, r)
            # Dibuja el borde con el color del jugador
            pygame.draw.rect(p, tema.COLOR_DADO[jug.color], r, width=tema.T(p, 6))
            # Dibuja los puntos negros según el número del dado
            self._dibujar_puntos_dado(r, valor)

    # Convierte una posición lógica del juego a coordenadas en píxeles de pantalla
    def _obtener_px_posicion(self, ficha, pos: int) -> tuple[float, float]:
        # Obtiene la partida actual
        partida = self.gestor.partidaActual
        # Obtiene la esquina del tablero
        ox, oy = self.origen_x, self.origen_y
        # Obtiene el tamaño de cada casillero
        cs = self.tam_celda

        # Si la ficha está en la base (posición 0)
        if pos == 0:
            # Obtiene los 4 huecos de la base de su color
            spots = self.GRID_BASE[ficha.color]
            # Busca al jugador dueño de esta ficha
            jugador = next((j for j in partida.jugadores if ficha in j.fichas), None) if partida else None
            # Encuentra qué número de ficha es (de 0 a 3)
            idx = jugador.fichas.index(ficha) if (jugador and ficha in jugador.fichas) else 0
            # Toma el hueco correspondiente a esta ficha
            spot = spots[idx % 4]
            # Separa fila y columna
            r, c = spot
            # Calcula las coordenadas en píxeles
            return ox + c * cs, oy + r * cs
        # Si la ficha llegó a la meta final
        elif pos == 58 or ficha.enMeta:
            # Devuelve el centro exacto del tablero
            return ox + 7.5 * cs, oy + 7.5 * cs
        # Si la ficha está en el recorrido común (1 a 51)
        elif pos <= 51:
            # Casilla de salida al circuito para cada color
            salida_colores = {Color.ROJO: 0, Color.VERDE: 13, Color.AMARILLO: 26, Color.AZUL: 39}
            # Calcula el índice global de la casilla sumando el desfase del color
            c_global = (salida_colores.get(ficha.color, 0) + (pos - 1)) % 52
            # Obtiene la fila y columna del circuito
            r, c = self.GRID_CIRCUITO_52[c_global]
            # Devuelve las coordenadas centradas en esa casilla
            return ox + (c + 0.5) * cs, oy + (r + 0.5) * cs
        # Si la ficha está en el pasillo final hacia su meta (52 a 57)
        else:
            # Calcula el índice dentro del pasillo
            idx = pos - 52
            # Obtiene la cuadrícula de llegada de su color
            grid_meta = {
                Color.ROJO: self.GRID_META_ROJO,
                Color.VERDE: self.GRID_META_VERDE,
                Color.AMARILLO: self.GRID_META_AMARILLO,
                Color.AZUL: self.GRID_META_AZUL
            }[ficha.color]
            # Obtiene la fila y columna en la meta
            r, c = grid_meta[idx]
            # Devuelve las coordenadas centradas en esa casilla de meta
            return ox + (c + 0.5) * cs, oy + (r + 0.5) * cs

    # Dibuja todas las fichas en el tablero con sus efectos de movimiento y brillo
    def _dibujar_fichas(self):
        # Obtiene la partida actual
        partida = self.gestor.partidaActual
        # Si no hay partida, no hace nada
        if not partida:
            # Sale de la función
            return

        # Obtiene qué fichas pueden moverse legalmente este turno
        movimientos_validos = partida.obtenerMovimientosValidos()
        # Calcula el radio visual de la ficha
        radio_ficha = int(self.tam_celda * 0.36)
        # Obtiene la posición del cursor del mouse
        pos_mouse = pygame.mouse.get_pos()

        # Recorre cada jugador de la partida
        for jug in partida.jugadores:
            # Recorre las 4 fichas de cada jugador
            for f in jug.fichas:
                # Calcula las coordenadas donde debe estar la ficha
                target_x, target_y = self._obtener_px_posicion(f, f.posicion)

                # Si la ficha tiene una cola de pasos pendientes por animar
                if f in self.colas_anim_pasos and len(self.colas_anim_pasos[f]) > 0:
                    # Toma el destino del paso actual
                    paso_dest_x, paso_dest_y = self.colas_anim_pasos[f][0]

                    # Si aún no tiene posición animada registrada, la inicia
                    if f not in self.posiciones_fichas_anim:
                        self.posiciones_fichas_anim[f] = [paso_dest_x, paso_dest_y, 0.0]

                    # Obtiene las coordenadas actuales de la ficha
                    curr_x, curr_y, _ = self.posiciones_fichas_anim[f]
                    # Calcula la distancia restante en X e Y
                    dx = paso_dest_x - curr_x
                    dy = paso_dest_y - curr_y
                    # Distancia euclidiana total al siguiente paso
                    dist = math.hypot(dx, dy)

                    # Si ya casi llegó a la casilla de este paso
                    if dist < 4.0:
                        # Coloca la ficha exactamente en el destino
                        self.posiciones_fichas_anim[f] = [paso_dest_x, paso_dest_y, 0.0]
                        # Remueve este paso ya completado de la cola
                        self.colas_anim_pasos[f].pop(0)
                    # Si todavía se está desplazando hacia el paso
                    else:
                        # Avanza una fracción hacia el destino
                        curr_x += dx * 0.35
                        curr_y += dy * 0.35
                        # Calcula el avance para hacer un saltito en arco
                        progreso = 1.0 - (dist / max(self.tam_celda, 1.0))
                        # Efecto de parábola vertical para dar efecto de salto
                        arc_y = -18 * math.sin(max(0.0, min(1.0, progreso)) * math.pi)
                        # Guarda la nueva posición intermedia
                        self.posiciones_fichas_anim[f] = [curr_x, curr_y, arc_y]
                        # Emite partículas de estela de color detrás de la ficha
                        self.particulas.emitir_estela_ficha(curr_x, curr_y + arc_y, get_rgb(f.color))

                # Si no está en animación paso a paso
                else:
                    # Si no tenía posición previa la inicia
                    if f not in self.posiciones_fichas_anim:
                        self.posiciones_fichas_anim[f] = [target_x, target_y, 0.0]
                    # Si ya existía, suaviza el movimiento hacia el destino
                    else:
                        curr_x, curr_y, _ = self.posiciones_fichas_anim[f]
                        curr_x += (target_x - curr_x) * 0.35
                        curr_y += (target_y - curr_y) * 0.35
                        self.posiciones_fichas_anim[f] = [curr_x, curr_y, 0.0]

                # Obtiene las coordenadas finales para dibujar la ficha
                px, py, arc_y = self.posiciones_fichas_anim[f]
                # Aplica la elevación del salto si corresponde
                render_y = py + arc_y

                # Comprueba si esta ficha puede ser movida
                es_valida = (f in movimientos_validos)
                # Distancia entre el puntero del mouse y la ficha
                dist_m = math.hypot(pos_mouse[0] - px, pos_mouse[1] - render_y)

                # Si es válida y el mouse está encima, la marca como activa bajo el cursor
                if es_valida and dist_m <= radio_ficha * 1.5:
                    self.ficha_hover_activa = f

                # Si es una ficha válida de un jugador humano, le dibuja un aura brillante
                if es_valida and not tema.es_bot(jug):
                    # Calcula el radio pulsante del aura dorada
                    radio_glow = radio_ficha + 4 + 3 * math.sin(self.ticks_glow * 0.2)
                    # Dibuja el círculo dorado alrededor de la ficha
                    pygame.draw.circle(self.pantalla, (255, 240, 80), (int(px), int(render_y)), int(radio_glow), width=3)

                # Ficha con la forma del Figma (gota con borde negro)
                # Ancho y alto proporcionales al tamaño del casillero
                w, h = int(self.tam_celda * 0.8), int(self.tam_celda * 1.2)
                # Carga la imagen de la ficha de ese color
                sprite = tema.imagen(f"ficha_{f.color.name.lower()}.png", (w, h))
                # Dibuja la ficha en pantalla centrada en su base
                self.pantalla.blit(sprite, (int(px - w / 2), int(render_y - h * 0.55)))

        # Vista previa de destino si el jugador pasa el cursor por encima de una ficha válida
        # Si hay una ficha válida bajo el cursor
        if self.ficha_hover_activa and self.ficha_hover_activa in movimientos_validos:
            # Calcula a qué casilla llegaría con el número del dado
            pos_dest = self.ficha_hover_activa.posicion + partida.dado if self.ficha_hover_activa.posicion > 0 else 1
            # Obtiene las coordenadas de esa casilla de destino
            dest_x, dest_y = self._obtener_px_posicion(self.ficha_hover_activa, pos_dest)
            # Dibuja un círculo dorado señalando la casilla destino
            pygame.draw.circle(self.pantalla, (255, 215, 0), (int(dest_x), int(dest_y)), int(radio_ficha * 0.8), width=3)

    # Dibuja los botones de REGLAS y PAUSA y los textos informativos a la derecha
    def _dibujar_panel_derecho(self):
        # Botones REGLAS y PAUSA y mensajes de la partida, como en el Figma
        # Obtiene la partida actual
        partida = self.gestor.partidaActual
        # Si no hay partida no dibuja nada
        if not partida:
            # Sale de la función
            return
        # Referencia a la pantalla
        p = self.pantalla
        # Crea el botón interactivo de REGLAS
        self.btn_reglas_inst = BotonFigma(p, (967, 57, 207, 82), "REGLAS", tema.GRADIENTE, tema.AMARILLO_BORDE, 4,
                                          tam_texto=40, contorno_texto=None)
        # Crea el botón interactivo de PAUSA
        self.btn_pausa_inst = BotonFigma(p, (1183, 57, 207, 82), "PAUSA", tema.GRADIENTE, tema.AMARILLO_BORDE, 4,
                                         tam_texto=48, contorno_texto=None)
        # Dibuja el botón de reglas en pantalla
        self.btn_reglas_inst.dibujar(p)
        # Dibuja el botón de pausa en pantalla
        self.btn_pausa_inst.dibujar(p)

        # Obtiene el jugador actual
        jugador_act = partida.obtenerJugadorActual()
        # Si hay un mensaje de relator específico
        if self.mensaje:
            # Usa ese mensaje
            mensaje = self.mensaje
        # Si la partida recién comienza y no se tiró el dado
        elif partida.turnosJugados <= 1 and partida.dado == 0:
            # Muestra aviso de inicio
            mensaje = "Partida Iniciada correctamente"
        # De lo contrario no muestra texto extra
        else:
            mensaje = ""
        # Divide el mensaje en renglones si es muy largo para que no se corte
        lineas = self._partir_texto(mensaje, tema.fuente(40), 380)
        # Recorre y dibuja cada línea del mensaje centrado
        for k, linea in enumerate(lineas):
            tema.texto_figma(p, linea, 0, 0, 40, centrado_en=(1205, 396 + (k - (len(lineas) - 1) / 2) * 44))
        # Obtiene el nombre del jugador actual
        nombre = jugador_act.nombre if jugador_act else ""
        # Muestra a quién le corresponde el turno actual
        tema.texto_figma(p, f"Turno de ‘{nombre}’", 0, 0, 40, centrado_en=(1205, 552))
        # Si falta tirar el dado y el turno es de un jugador humano, le da la indicación
        if not partida.dado and jugador_act and not tema.es_bot(jugador_act):
            tema.texto_figma(p, "Hacé clic en tu dado", 0, 0, 30, (255, 240, 150), centrado_en=(1205, 610))

    # Divide un texto en varias líneas para que quepa en un ancho máximo en píxeles
    def _partir_texto(self, texto, fuente, ancho_max):
        # Separa las palabras individuales y prepara las listas
        palabras, lineas, actual = texto.split(), [], ""
        # Recorre cada palabra
        for palabra in palabras:
            # Prueba cómo queda agregando la palabra
            prueba = f"{actual} {palabra}".strip()
            # Si entra en el ancho permitido
            if fuente.size(prueba)[0] <= ancho_max or not actual:
                # Agrega la palabra a la línea actual
                actual = prueba
            # Si no cabe
            else:
                # Guarda la línea completa
                lineas.append(actual)
                # Inicia una nueva línea con esta palabra
                actual = palabra
        # Si quedó texto pendiente lo agrega a la lista
        if actual:
            lineas.append(actual)
        # Devuelve la lista de renglones
        return lineas

    # Dibuja los puntos negros en la cara de un dado según su valor
    def _dibujar_puntos_dado(self, r, val):
        # Obtiene el centro del dado
        cx, cy = r.center
        # Distancia de separación de los puntos del centro
        d = r.width * 0.25
        # Tamaño del radio de cada punto negro
        radio = max(3, int(r.width * (0.22 if val == 1 else 0.09)))
        # Lista de coordenadas para los puntos
        coords = []
        # Si el valor es impar (1, 3 o 5), lleva un punto en el centro
        if val in (1, 3, 5):
            coords.append((cx, cy))
        # Si tiene puntos en las esquinas superior-izquierda e inferior-derecha
        if val in (2, 3, 4, 5, 6):
            coords += [(cx - d, cy - d), (cx + d, cy + d)]
        # Si tiene puntos en las otras dos esquinas
        if val in (4, 5, 6):
            coords += [(cx + d, cy - d), (cx - d, cy + d)]
        # Si sacó 6, agrega dos puntos en los bordes laterales medios
        if val == 6:
            coords += [(cx - d, cy), (cx + d, cy)]
        # Dibuja cada punto negro en la cara del dado
        for px, py in coords:
            pygame.draw.circle(self.pantalla, tema.NEGRO, (int(px), int(py)), radio)

    # Procesa los clics del mouse para tirar el dado, elegir fichas o usar botones
    def manejar_evento(self, evento):
        # Obtiene la partida actual
        partida = self.gestor.partidaActual
        # Si no hay partida, no hace nada
        if not partida:
            # Sale de la función
            return

        # Obtiene el jugador con el turno actual
        jugador_act = partida.obtenerJugadorActual()
        # Verifica si es una persona (no un bot)
        es_humano = jugador_act and not tema.es_bot(jugador_act)

        # Si el usuario hizo clic con el botón izquierdo
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            # Guarda la posición del clic
            pos = evento.pos

            # Si hizo clic en el botón de REGLAS
            if hasattr(self, 'btn_reglas_inst') and self.btn_reglas_inst.es_cliqueado(evento):
                # Abre la pantalla de reglas del juego
                self.interfaz.pantalla_reglas.abrir()
                # Cambia a la pantalla de reglas
                self.interfaz.ir_a("REGLAS")

            # Si hizo clic en el botón de PAUSA
            elif hasattr(self, 'btn_pausa_inst') and self.btn_pausa_inst.es_cliqueado(evento):
                # Pausa la partida en el gestor
                self.gestor.pausarPartida()
                # Cambia a la pantalla del menú de pausa
                self.interfaz.ir_a("PAUSA")

            # Si hizo clic sobre el dado de su base para lanzarlo
            elif self.btn_lanzar.collidepoint(pos) and es_humano and not partida.dado and not self.animando_dado:
                # Activa la animación del giro del dado
                self.animando_dado = True
                # Configura 12 cuadros de giro
                self.frames_anim_dado = 12

            # Si ya tiró el dado y hace clic para elegir una ficha
            elif es_humano and partida.dado and not self.animando_dado:
                # Obtiene las fichas que pueden moverse
                movimientos_validos = partida.obtenerMovimientosValidos()
                # Revisa si hizo clic sobre alguna de ellas
                for ficha in movimientos_validos:
                    # Obtiene las coordenadas actuales de la ficha
                    px, py, _ = self.posiciones_fichas_anim.get(ficha, (0, 0, 0))
                    # Calcula la distancia del clic a la ficha
                    distancia = math.hypot(pos[0] - px, pos[1] - py)
                    # Si el clic fue sobre la ficha
                    if distancia <= (self.tam_celda * 0.6):
                        # Juega esa ficha
                        self._jugar_ficha(ficha)
                        # Deja de revisar
                        break

#- get_rgb(): obtiene el color en formato RGB.
#- __init__(): prepara el tablero, las fichas y las animaciones.
#- _calcular_geometria(): calcula el tamaño y la posición del tablero.
#- dibujar(): muestra el tablero, las fichas, los dados y los botones.
#- _actualizar_turno_bot(): hace que los bots jueguen automáticamente.
#- _lanzar_dado(): tira el dado y muestra el resultado.
#- _jugar_ficha(): mueve la ficha elegida y comprueba si terminó la partida.
#- _seleccionar_mejor_movimiento_bot(): elige qué ficha moverá el bot.
#- _generar_pasos_animacion(): prepara los pasos para animar el movimiento de una ficha.
#- _dibujar_tablero_ludo(): dibuja el tablero.
#- _dibujar_etiquetas_jugadores(): muestra los nombres de los jugadores y destaca el turno actual.
#- _dibujar_dados_indicadores_jugadores(): muestra los dados de cada jugador.
#- _obtener_px_posicion(): calcula dónde debe aparecer una ficha en el tablero.
#- _dibujar_fichas(): muestra las fichas y sus movimientos animados.
#- _dibujar_panel_derecho(): muestra los botones de reglas y pausa, y los mensajes del juego.
#- _partir_texto(): divide un texto largo en varias líneas.
#- _dibujar_puntos_dado(): dibuja los puntos del dado según el número obtenido.
#- manejar_evento(): detecta los clics para tirar el dado, mover fichas, abrir las reglas o pausar.
#En resumen: este módulo controla la pantalla de juego, muestra los elementos y permite que los jugadores y los bots jueguen.