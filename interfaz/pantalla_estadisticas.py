"""
Modulo pantalla_estadisticas.py
Dibuja e interactúa con la Pantalla de Estadísticas.
Muestra un panel dashboard con tarjetas de tiempo, turnos, tabla de posiciones y reconocimientos.
"""

import pygame
from interfaz.efectos import dibujar_panel_glassmorphism, dibujar_texto_glow
from interfaz.componentes import BotonModerno


class PantallaEstadisticas:

    def __init__(self, pantalla, gestor_partida):
        self.pantalla = pantalla
        self.gestor = gestor_partida

        self.fuente_titulo = pygame.font.SysFont("Arial", 36, bold=True)
        self.fuente_sub = pygame.font.SysFont("Arial", 22, bold=True)
        self.fuente_tabla = pygame.font.SysFont("Arial", 18)
        self.fuente_boton = pygame.font.SysFont("Arial", 22, bold=True)

    def dibujar(self):
        ancho, alto = self.pantalla.get_size()

        # Capa translúcida sobre el juego
        superficie_oscura = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        superficie_oscura.fill((5, 10, 25, 190))
        self.pantalla.blit(superficie_oscura, (0, 0))

        # Cuadro principal de datos Glassmorphism
        rect_box = pygame.Rect(80, 80, ancho - 160, alto - 160)
        dibujar_panel_glassmorphism(
            self.pantalla, rect_box,
            color_bg=(16, 35, 95, 240),
            color_borde=(255, 215, 0, 220),
            radio=20, grosor_borde=3
        )

        # Título
        dibujar_texto_glow(
            self.pantalla, "ESTADÍSTICAS DE LA PARTIDA", self.fuente_titulo,
            ancho // 2, rect_box.y + 40,
            color_texto=(255, 220, 40), color_resplandor=(0, 150, 255), centro=True
        )

        partida = self.gestor.partidaActual
        if not partida:
            txt_nodata = self.fuente_sub.render("No hay información de partida disponible.", True, (200, 200, 200))
            self.pantalla.blit(txt_nodata, txt_nodata.get_rect(center=(ancho // 2, alto // 2)))
            return

        partida.recopilarEstadisticas()
        segundos = getattr(partida, "tiempoTranscurrido", 0)
        minutos = segundos // 60
        seg_rest = segundos % 60
        tiempo_str = f"{minutos:02d}:{seg_rest:02d}"
        turnos_str = str(getattr(partida, "turnosJugados", 0))
        ganador_str = partida.ganador.nombre if partida.ganador else "Ninguno"

        # Tarjetas de Información general (Tiempo y Turnos)
        rect_t = pygame.Rect(rect_box.x + 40, rect_box.y + 85, (rect_box.width - 100) // 2, 45)
        rect_turn = pygame.Rect(rect_box.x + 60 + (rect_box.width - 100) // 2, rect_box.y + 85, (rect_box.width - 100) // 2, 45)

        dibujar_panel_glassmorphism(self.pantalla, rect_t, color_bg=(25, 50, 120, 200), color_borde=(0, 200, 255, 150), radio=10)
        dibujar_panel_glassmorphism(self.pantalla, rect_turn, color_bg=(25, 50, 120, 200), color_borde=(0, 200, 255, 150), radio=10)

        txt_tiempo = self.fuente_sub.render(f"Tiempo: {tiempo_str}", True, (220, 240, 255))
        txt_turnos = self.fuente_sub.render(f"Turnos: {turnos_str}", True, (220, 240, 255))
        self.pantalla.blit(txt_tiempo, txt_tiempo.get_rect(center=rect_t.center))
        self.pantalla.blit(txt_turnos, txt_turnos.get_rect(center=rect_turn.center))

        # Encabezado de Tabla de Jugadores
        py_tabla = rect_box.y + 150
        pygame.draw.line(self.pantalla, (100, 140, 220), (rect_box.x + 30, py_tabla), (rect_box.right - 30, py_tabla), 2)

        hdr_jug = self.fuente_sub.render("Jugador", True, (255, 255, 255))
        hdr_mov = self.fuente_sub.render("Movimientos", True, (255, 255, 255))
        hdr_pts = self.fuente_sub.render("Puntaje", True, (255, 255, 255))

        self.pantalla.blit(hdr_jug, (rect_box.x + 50, py_tabla + 10))
        self.pantalla.blit(hdr_mov, (rect_box.x + 280, py_tabla + 10))
        self.pantalla.blit(hdr_pts, (rect_box.x + 480, py_tabla + 10))

        # Filas de la tabla
        pos_y_fila = py_tabla + 45
        for j in partida.jugadores:
            movs = getattr(j, "movimientos", 0)
            pts = getattr(j, "puntaje", 0)
            txt_n = self.fuente_tabla.render(j.nombre, True, (240, 240, 240))
            txt_m = self.fuente_tabla.render(str(movs), True, (240, 240, 240))
            txt_p = self.fuente_tabla.render(f"{pts} pts", True, (255, 220, 40))

            self.pantalla.blit(txt_n, (rect_box.x + 50, pos_y_fila))
            self.pantalla.blit(txt_m, (rect_box.x + 310, pos_y_fila))
            self.pantalla.blit(txt_p, (rect_box.x + 490, pos_y_fila))
            pos_y_fila += 35

        # Ganador si aplica
        if ganador_str != "Ninguno":
            dibujar_texto_glow(
                self.pantalla, f"LÍDER ACTUAL: {ganador_str}", self.fuente_sub,
                rect_box.x + 40, rect_box.bottom - 45,
                color_texto=(255, 215, 0), color_resplandor=(255, 100, 0)
            )

        # Botón Volver
        self.btn_volver_inst = BotonModerno(
            ((ancho - 180) // 2, alto - 70, 180, 48), "VOLVER",
            color_base=(30, 100, 180), color_hover=(40, 140, 220),
            fuente=self.fuente_boton, icono=""
        )
        self.btn_volver_inst.dibujar(self.pantalla)

    def manejar_evento(self, evento):
        if hasattr(self, 'btn_volver_inst') and self.btn_volver_inst.es_cliqueado(evento):
            self.gestor.volver()
