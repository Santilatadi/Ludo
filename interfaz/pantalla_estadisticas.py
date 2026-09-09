"""
Modulo pantalla_estadisticas.py
Dibuja e interactúa con la Pantalla de Estadísticas (CU-15).
Muestra movimientos por jugador, turnos totales, tiempo transcurrido y puntajes.
"""

import pygame
from logica.estadisticas import Estadisticas


class PantallaEstadisticas:

    def __init__(self, pantalla, gestor_partida):
        self.pantalla = pantalla
        self.gestor = gestor_partida
        self.estadisticas = Estadisticas()
        self.fuente_titulo = pygame.font.SysFont("Arial", 36, bold=True)
        self.fuente_sub = pygame.font.SysFont("Arial", 22, bold=True)
        self.fuente_tabla = pygame.font.SysFont("Arial", 18)
        self.fuente_boton = pygame.font.SysFont("Arial", 22, bold=True)

    def dibujar(self):
        self.pantalla.fill((20, 28, 45))
        ancho, alto = self.pantalla.get_size()

        # Título
        txt_tit = self.fuente_titulo.render("ESTADÍSTICAS DE LA PARTIDA", True, (255, 220, 40))
        self.pantalla.blit(txt_tit, txt_tit.get_rect(center=(ancho // 2, 50)))

        partida = self.gestor.partidaActual
        if not partida:
            txt_nodata = self.fuente_sub.render("No hay información de partida disponible.", True, (200, 200, 200))
            self.pantalla.blit(txt_nodata, txt_nodata.get_rect(center=(ancho // 2, alto // 2)))
            return

        resumen = self.estadisticas.obtener_resumen(partida)

        # Cuadro principal de datos
        rect_box = pygame.Rect(80, 100, ancho - 160, alto - 200)
        pygame.draw.rect(self.pantalla, (30, 42, 65), rect_box, border_radius=15)
        pygame.draw.rect(self.pantalla, (60, 90, 130), rect_box, width=2, border_radius=15)

        # Información general (Tiempo y Turnos)
        txt_tiempo = self.fuente_sub.render(f"Tiempo transcurrido: {resumen['tiempo']}", True, (200, 230, 255))
        txt_turnos = self.fuente_sub.render(f"Turnos totales: {resumen['turnos_totales']}", True, (200, 230, 255))
        self.pantalla.blit(txt_tiempo, (rect_box.x + 40, rect_box.y + 30))
        self.pantalla.blit(txt_turnos, (rect_box.x + 350, rect_box.y + 30))

        # Encabezado de Tabla de Jugadores
        py_tabla = rect_box.y + 90
        pygame.draw.line(self.pantalla, (100, 120, 160), (rect_box.x + 30, py_tabla), (rect_box.right - 30, py_tabla), 2)

        hdr_jug = self.fuente_sub.render("Jugador", True, (255, 255, 255))
        hdr_mov = self.fuente_sub.render("Movimientos", True, (255, 255, 255))
        hdr_pts = self.fuente_sub.render("Puntaje", True, (255, 255, 255))

        self.pantalla.blit(hdr_jug, (rect_box.x + 50, py_tabla + 10))
        self.pantalla.blit(hdr_mov, (rect_box.x + 280, py_tabla + 10))
        self.pantalla.blit(hdr_pts, (rect_box.x + 480, py_tabla + 10))

        # Filas de la tabla
        pos_y_fila = py_tabla + 45
        for j_info in resumen["jugadores"]:
            txt_n = self.fuente_tabla.render(j_info["nombre"], True, (240, 240, 240))
            txt_m = self.fuente_tabla.render(str(j_info["movimientos"]), True, (240, 240, 240))
            txt_p = self.fuente_tabla.render(str(j_info["puntaje"]), True, (255, 220, 40))

            self.pantalla.blit(txt_n, (rect_box.x + 50, pos_y_fila))
            self.pantalla.blit(txt_m, (rect_box.x + 310, pos_y_fila))
            self.pantalla.blit(txt_p, (rect_box.x + 500, pos_y_fila))
            pos_y_fila += 35

        # Ganador si aplica
        if resumen["ganador"] != "Ninguno":
            txt_gan = self.fuente_sub.render(f"🏆 Ganador actual: {resumen['ganador']}", True, (255, 215, 0))
            self.pantalla.blit(txt_gan, (rect_box.x + 40, rect_box.bottom - 45))

        # Botón Volver
        self.btn_volver = pygame.Rect((ancho - 180) // 2, alto - 75, 180, 50)
        pos_m = pygame.mouse.get_pos()
        hover = self.btn_volver.collidepoint(pos_m)
        color_btn = (40, 140, 220) if hover else (30, 100, 180)

        pygame.draw.rect(self.pantalla, color_btn, self.btn_volver, border_radius=10)
        pygame.draw.rect(self.pantalla, (255, 255, 255), self.btn_volver, width=2, border_radius=10)
        txt_v = self.fuente_boton.render("VOLVER", True, (255, 255, 255))
        self.pantalla.blit(txt_v, txt_v.get_rect(center=self.btn_volver.center))

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.btn_volver.collidepoint(evento.pos):
                self.gestor.volverDeEstadisticas()
