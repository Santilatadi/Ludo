"""
Modulo pantalla_estadisticas.py
Frame de "Estadísticas de la Partida" del Figma (CU-15): ventana con degradé azul y
borde amarillo, tiempo y turnos jugados y una tabla con cada jugador.
"""

import pygame

from interfaz import tema


class PantallaEstadisticas:

    def __init__(self, pantalla, game_manager, interfaz=None):
        self.pantalla = pantalla
        self.gestor = game_manager
        self.interfaz = interfaz
        self.resumen = ""

    def abrir(self):
        # CU-15: el GameManager pide a la Partida que recopile las estadísticas
        self.resumen = self.gestor.verEstadisticas()

    def _caja(self, x, y, w, h, texto):
        p = self.pantalla
        r = tema.R(p, x, y, w, h)
        pygame.draw.rect(p, (16, 36, 92), r, border_radius=tema.T(p, 10))
        pygame.draw.rect(p, (60, 120, 230), r, width=tema.T(p, 3), border_radius=tema.T(p, 10))
        tema.texto_figma(p, texto, 0, 0, 32, centrado_en=(x + w / 2, y + h / 2))

    def dibujar(self):
        p = self.pantalla
        tema.oscurecer(p)
        tema.panel_figma(p, 86, 57, 1270, 800, tema.GRADIENTE, tema.AMARILLO_BORDE, 4, radio=50)
        tema.texto_figma(p, "Estadísticas de la Partida", 0, 0, 80, contorno=(201, 192, 24), trazo=4,
                         centrado_en=(666.5, 131))
        self.btn_volver_inst = tema.cruz_figma(p, 1270, 78)
        tema.linea_figma(p, 90, 197, 1260)

        partida = self.gestor.partidaActual
        if not partida:
            tema.texto_figma(p, "No hay estadísticas para mostrar.", 0, 0, 40, centrado_en=(721, 450))
            return

        segundos = partida.tiempoTranscurrido
        self._caja(130, 225, 560, 64, f"Tiempo: {segundos // 60:02d}:{segundos % 60:02d}")
        self._caja(750, 225, 560, 64, f"Turnos: {partida.turnosJugados}")
        tema.linea_figma(p, 130, 315, 1180, (60, 120, 230), 3)

        columnas = ((150, "Jugador"), (620, "Movimientos"), (950, "Puntaje"))
        for x, titulo in columnas:
            tema.texto_figma(p, titulo, x, 335, 36)
        for k, jugador in enumerate(partida.jugadores):
            y = 405 + k * 70
            fila = tema.R(p, 130, y - 8, 1180, 60)
            pygame.draw.rect(p, (16, 36, 92), fila, border_radius=tema.T(p, 10))
            tema.texto_figma(p, jugador.nombre, 150, y, 34, tema.COLOR_NOMBRE.get(jugador.color, tema.BLANCO))
            tema.texto_figma(p, str(jugador.movimientos), 620, y, 34)
            tema.texto_figma(p, f"{jugador.puntaje} pts", 950, y, 34, (254, 216, 66))

        if partida.ganador:
            tema.texto_figma(p, f"Ganador: {partida.ganador.nombre}", 0, 0, 40, (254, 216, 66),
                             centrado_en=(721, 800))

    def manejar_evento(self, evento):
        cerrar = (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and hasattr(self, "btn_volver_inst")
                  and self.btn_volver_inst.collidepoint(evento.pos))
        if cerrar or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
            self.gestor.volver()
            self.interfaz.estado = self.interfaz.estado_anterior
