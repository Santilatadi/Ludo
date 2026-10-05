"""
Modulo pantalla_continuar.py
Dibuja e interactúa con la Pantalla de Continuar Partida (Cargar partida guardada).
Adaptada a la interfaz gráfica del diseño de especificación.
"""

import os
import pygame


class PantallaContinuar:

    def __init__(self, pantalla, gestor_partida, persistencia):
        self.pantalla = pantalla
        self.gestor = gestor_partida
        self.persistencia = persistencia

        ruta_fuente = "assets/font.ttf"
        if os.path.exists(ruta_fuente):
            self.fuente_titulo = pygame.font.Font(ruta_fuente, 34)
            self.fuente_sub = pygame.font.Font(ruta_fuente, 18)
            self.fuente_badge = pygame.font.Font(ruta_fuente, 14)
            self.fuente_boton = pygame.font.Font(ruta_fuente, 22)
        else:
            self.fuente_titulo = pygame.font.SysFont("Impact", 34, bold=True)
            self.fuente_sub = pygame.font.SysFont("Arial", 18, bold=True)
            self.fuente_badge = pygame.font.SysFont("Arial", 14, bold=True)
            self.fuente_boton = pygame.font.SysFont("Arial", 22, bold=True)

        self.mensaje_error = ""

    def _render_texto_delineado(self, texto, fuente, color_texto, color_borde=(0, 0, 0), grosor=1):
        if grosor <= 0 or color_borde is None or color_texto == color_borde:
            return fuente.render(texto, True, color_texto)

        surf_base = fuente.render(texto, True, color_texto)
        w, h = surf_base.get_size()
        surf_final = pygame.Surface((w + grosor * 2, h + grosor * 2), pygame.SRCALPHA)

        offsets = [
            (-grosor, 0), (grosor, 0), (0, -grosor), (0, grosor),
            (-grosor, -grosor), (-grosor, grosor), (grosor, -grosor), (grosor, grosor)
        ]
        surf_borde = fuente.render(texto, True, color_borde)
        for dx, dy in offsets:
            surf_final.blit(surf_borde, (dx + grosor, dy + grosor))

        surf_final.blit(surf_base, (grosor, grosor))
        return surf_final

    def dibujar(self):
        ancho, alto = self.pantalla.get_size()
        # Fondo Rosa / Magenta característico
        self.pantalla.fill((226, 120, 190))

        # Ventana modal central azul con borde rojo brillante
        w_win, h_win = min(680, ancho - 60), min(520, alto - 60)
        rect_win = pygame.Rect((ancho - w_win) // 2, (alto - h_win) // 2, w_win, h_win)

        # Fondo Azul Profundo
        pygame.draw.rect(self.pantalla, (16, 45, 120), rect_win, border_radius=12)
        pygame.draw.rect(self.pantalla, (220, 20, 60), rect_win, width=4, border_radius=12)

        # Título "CONTINUAR PARTIDA" en Amarillo Brillante super legible
        txt_tit = self._render_texto_delineado("CONTINUAR PARTIDA", self.fuente_titulo, (255, 220, 0), (0, 0, 0), 2)
        self.pantalla.blit(txt_tit, txt_tit.get_rect(center=(ancho // 2, rect_win.y + 45)))

        # Cuadro interior de lista de partidas
        rect_box = pygame.Rect(rect_win.x + 35, rect_win.y + 85, w_win - 70, h_win - 180)
        pygame.draw.rect(self.pantalla, (10, 25, 75), rect_box, border_radius=8)
        pygame.draw.rect(self.pantalla, (255, 255, 255), rect_box, width=3, border_radius=8)

        tiene_guardada = self.persistencia.existe_partida_guardada()

        if tiene_guardada:
            # Slot de partida guardada
            slot_rect = pygame.Rect(rect_box.x + 20, rect_box.y + 20, rect_box.width - 40, 95)
            pygame.draw.rect(self.pantalla, (18, 40, 100), slot_rect, border_radius=6)
            pygame.draw.rect(self.pantalla, (80, 130, 220), slot_rect, width=2, border_radius=6)

            # Información de la partida guardada
            txt_tiempo = self._render_texto_delineado("Partida Guardada", self.fuente_sub, (255, 255, 255), (0, 0, 0), 1)
            self.pantalla.blit(txt_tiempo, (slot_rect.x + 15, slot_rect.y + 14))

            # Jugadores con badges coloridos
            txt_lbl_j = self._render_texto_delineado("JUGADORES:", self.fuente_sub, (255, 220, 0), (0, 0, 0), 1)
            self.pantalla.blit(txt_lbl_j, (slot_rect.x + 15, slot_rect.y + 50))

            colors_badge = [(220, 50, 50), (40, 180, 80), (40, 120, 220), (240, 190, 40)]
            nombres = ["Jugador 1", "Jugador 2", "Jugador 3", "Jugador 4"]

            pos_x_b = slot_rect.x + 140
            for idx, (nom, col) in enumerate(zip(nombres, colors_badge)):
                txt_b = self.fuente_badge.render(nom, True, (255, 255, 255) if idx != 3 else (20, 20, 20))
                bw = txt_b.get_width() + 14
                rect_b = pygame.Rect(pos_x_b, slot_rect.y + 48, bw, 24)
                pygame.draw.rect(self.pantalla, col, rect_b, border_radius=4)
                pygame.draw.rect(self.pantalla, (0, 0, 0), rect_b, width=1, border_radius=4)
                self.pantalla.blit(txt_b, (rect_b.x + 7, rect_b.y + 3))
                pos_x_b += bw + 8
        else:
            txt_empty = self._render_texto_delineado("No hay ninguna partida guardada actualmente.", self.fuente_sub, (200, 220, 255), (0, 0, 0), 1)
            self.pantalla.blit(txt_empty, txt_empty.get_rect(center=rect_box.center))

        if self.mensaje_error:
            txt_err = self._render_texto_delineado(self.mensaje_error, self.fuente_sub, (255, 100, 100), (0, 0, 0), 1)
            self.pantalla.blit(txt_err, txt_err.get_rect(center=(ancho // 2, rect_win.bottom - 85)))

        # Botón INICIAR (rojo con borde amarillo)
        bw_btn, bh_btn = 180, 48
        self.btn_iniciar = pygame.Rect((ancho - bw_btn) // 2, rect_win.bottom - 68, bw_btn, bh_btn)

        pos_m = pygame.mouse.get_pos()
        hover = self.btn_iniciar.collidepoint(pos_m)
        color_btn = (245, 40, 50) if hover else (225, 30, 40)

        pygame.draw.rect(self.pantalla, color_btn, self.btn_iniciar, border_radius=8)
        pygame.draw.rect(self.pantalla, (255, 230, 0), self.btn_iniciar, width=3, border_radius=8)

        txt_ini = self._render_texto_delineado("INICIAR", self.fuente_boton, (255, 255, 255), (0, 0, 0), 1)
        self.pantalla.blit(txt_ini, txt_ini.get_rect(center=self.btn_iniciar.center))

        # Botón pequeño para volver
        self.btn_volver = pygame.Rect(rect_win.x + 20, rect_win.y + 15, 34, 34)
        pygame.draw.rect(self.pantalla, (220, 50, 50), self.btn_volver, border_radius=6)
        pygame.draw.rect(self.pantalla, (255, 255, 255), self.btn_volver, width=2, border_radius=6)
        txt_v = self.fuente_sub.render("X", True, (255, 255, 255))
        self.pantalla.blit(txt_v, txt_v.get_rect(center=self.btn_volver.center))

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos
            if self.btn_iniciar.collidepoint(pos):
                if self.persistencia.existe_partida_guardada():
                    partida, msg = self.persistencia.cargarPartida()
                    if partida:
                        self.gestor.partidaActual = partida
                        self.gestor.estado = "JUEGO"
                        self.mensaje_error = ""
                    else:
                        self.mensaje_error = msg
                else:
                    self.mensaje_error = "No hay partida guardada para cargar."

            elif self.btn_volver.collidepoint(pos):
                self.gestor.estado = "MENU"
