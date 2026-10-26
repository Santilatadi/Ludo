"""
Modulo pantalla_estadisticas.py
Frame de "Estadísticas de la Partida" del Figma (CU-15): ventana con degradé azul y
borde amarillo, tiempo y turnos jugados y una tabla con cada jugador.
"""

# Importa pygame para renderizado y eventos
import pygame

# Importa el módulo de estilos visuales tema
from interfaz import tema


# Representa la pantalla modal de estadísticas de la partida
class PantallaEstadisticas:

    # Constructor: inicializa pantalla, gestor y texto de resumen
    def __init__(self, pantalla, game_manager, interfaz=None):
        # Superficie de la ventana donde se dibuja
        self.pantalla = pantalla
        # Referencia al gestor del juego
        self.gestor = game_manager
        # Referencia a la interfaz principal
        self.interfaz = interfaz
        # Texto del resumen de la partida
        self.resumen = ""

    # Carga las estadísticas recopiladas desde el gestor
    def abrir(self):
        # CU-15: el GameManager pide a la Partida que recopile las estadísticas
        # Obtiene el informe estadístico
        self.resumen = self.gestor.verEstadisticas()

    # Función auxiliar para dibujar una tarjeta o caja azul con texto adentro
    def _caja(self, x, y, w, h, texto):
        p = self.pantalla
        # Convierte las medidas a píxeles escalados
        r = tema.R(p, x, y, w, h)
        # Rellena el fondo de la caja con azul oscuro
        pygame.draw.rect(p, (16, 36, 92), r, border_radius=tema.T(p, 10))
        # Dibuja el borde azul claro redondeado
        pygame.draw.rect(p, (60, 120, 230), r, width=tema.T(p, 3), border_radius=tema.T(p, 10))
        # Dibuja el texto centrado en la caja
        tema.texto_figma(p, texto, 0, 0, 32, centrado_en=(x + w / 2, y + h / 2))

    # Dibuja la ventana emergente con todas las estadísticas
    def dibujar(self):
        p = self.pantalla
        # Oscurece el juego de fondo con una capa semitransparente
        tema.oscurecer(p)
        # Dibuja el panel principal grande con degradado y borde amarillo
        tema.panel_figma(p, 86, 57, 1270, 800, tema.GRADIENTE, tema.AMARILLO_BORDE, 4, radio=50)
        # Dibuja el título "Estadísticas de la Partida"
        tema.texto_figma(p, "Estadísticas de la Partida", 0, 0, 80, contorno=(201, 192, 24), trazo=4,
                          centrado_en=(666.5, 131))
        # Dibuja la cruz de cierre en la esquina superior derecha
        self.btn_volver_inst = tema.cruz_figma(p, 1270, 78)
        # Dibuja una línea divisoria debajo del título
        tema.linea_figma(p, 90, 197, 1260)

        # Obtiene la partida actual
        partida = self.gestor.partidaActual
        # Si no hay partida, muestra mensaje avisándolo y sale
        if not partida:
            tema.texto_figma(p, "No hay estadísticas para mostrar.", 0, 0, 40, centrado_en=(721, 450))
            return

        # Lee los segundos transcurridos
        segundos = partida.tiempoTranscurrido
        # Dibuja la caja con el tiempo en formato MM:SS
        self._caja(130, 225, 560, 64, f"Tiempo: {segundos // 60:02d}:{segundos % 60:02d}")
        # Dibuja la caja con el total de turnos jugados
        self._caja(750, 225, 560, 64, f"Turnos: {partida.turnosJugados}")
        # Dibuja una línea separadora antes de la tabla de jugadores
        tema.linea_figma(p, 130, 315, 1180, (60, 120, 230), 3)

        # Encabezados de las columnas de la tabla
        columnas = ((150, "Jugador"), (620, "Movimientos"), (950, "Puntaje"))
        # Dibuja cada título de columna
        for x, titulo in columnas:
            tema.texto_figma(p, titulo, x, 335, 36)
        # Recorre a cada jugador para mostrar su fila de datos
        for k, jugador in enumerate(partida.jugadores):
            # Calcula la posición Y de la fila
            y = 405 + k * 70
            # Calcula el rectángulo de fondo de la fila
            fila = tema.R(p, 130, y - 8, 1180, 60)
            # Dibuja la tarjeta azul para la fila
            pygame.draw.rect(p, (16, 36, 92), fila, border_radius=tema.T(p, 10))
            # Muestra el nombre con el color del jugador
            tema.texto_figma(p, jugador.nombre, 150, y, 34, tema.COLOR_NOMBRE.get(jugador.color, tema.BLANCO))
            # Muestra la cantidad de movimientos
            tema.texto_figma(p, str(jugador.movimientos), 620, y, 34)
            # Muestra el puntaje acumulado en amarillo
            tema.texto_figma(p, f"{jugador.puntaje} pts", 950, y, 34, (254, 216, 66))

        # Si ya hay un ganador definido, lo muestra al pie del panel
        if partida.ganador:
            tema.texto_figma(p, f"Ganador: {partida.ganador.nombre}", 0, 0, 40, (254, 216, 66),
                             centrado_en=(721, 800))

    # Gestiona los clics en la cruz o la tecla Escape para cerrar
    def manejar_evento(self, evento):
        # Comprueba si se hizo clic izquierdo en el botón de la cruz
        cerrar = (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and hasattr(self, "btn_volver_inst")
                  and self.btn_volver_inst.collidepoint(evento.pos))
        # Si se presionó cerrar o la tecla ESC:
        if cerrar or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
            # Notifica al gestor que se vuelve
            self.gestor.volver()
            # Restaura el estado anterior en la interfaz
            self.interfaz.estado = self.interfaz.estado_anterior


# - __init__(): prepara la pantalla.
#- _caja(): dibuja una caja para mostrar texto.
#- dibujar(): muestra las estadísticas de la partida actual (tiempo, turnos, jugadores y ganador).
#- manejar_evento(): cierra la pantalla y vuelve al estado anterior (por ejemplo, al menú o a la partida).
#En resumen: muestra un resumen de la partida actual y permite volver a donde estabas.
