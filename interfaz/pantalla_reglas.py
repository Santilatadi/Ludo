"""
Modulo pantalla_reglas.py
Dibuja e interactúa con la Ventana de Reglas del Ludo.
Muestra todas las reglas detalladas con alta legibilidad y soporte para scroll.
"""

import os
import sys

# Añadir el directorio raíz al PATH para permitir ejecuciones directas del script
directorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if directorio_raiz not in sys.path:
    sys.path.insert(0, directorio_raiz)

import pygame
from logica.reglas import Reglas


class PantallaReglas:

    def __init__(self, pantalla, gestor_partida):
        self.pantalla = pantalla
        self.gestor = gestor_partida
        self.scroll_y = 0

        ruta_fuente = "assets/font.ttf"
        if os.path.exists(ruta_fuente):
            self.fuente_titulo = pygame.font.Font(ruta_fuente, 36)
            self.fuente_seccion = pygame.font.Font(ruta_fuente, 17)
            self.fuente_texto = pygame.font.Font(ruta_fuente, 15)
        else:
            self.fuente_titulo = pygame.font.SysFont("Impact", 36, bold=True)
            self.fuente_seccion = pygame.font.SysFont("Arial", 17, bold=True)
            self.fuente_texto = pygame.font.SysFont("Arial", 15, bold=True)

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

        # Capa translúcida sobre la pantalla de juego
        superficie_oscura = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        superficie_oscura.fill((10, 15, 25, 180))
        self.pantalla.blit(superficie_oscura, (0, 0))

        # Ventana Modal (Azul con borde Rojo)
        w_box, h_box = min(620, ancho - 40), min(500, alto - 40)
        rect_box = pygame.Rect((ancho - w_box) // 2, (alto - h_box) // 2, w_box, h_box)

        pygame.draw.rect(self.pantalla, (16, 45, 120), rect_box, border_radius=10)
        pygame.draw.rect(self.pantalla, (220, 20, 60), rect_box, width=4, border_radius=10)

        # Encabezado "REGLAS DEL JUEGO"
        txt_tit = self._render_texto_delineado("REGLAS DEL JUEGO", self.fuente_titulo, (255, 220, 0), (0, 0, 0), 2)
        rect_tit = txt_tit.get_rect(center=(ancho // 2, rect_box.y + 40))
        self.pantalla.blit(txt_tit, rect_tit)

        # Botón X de cerrar en la esquina superior derecha del modal
        self.btn_cerrar = pygame.Rect(rect_box.right - 42, rect_box.y + 12, 32, 32)
        pygame.draw.rect(self.pantalla, (220, 30, 40), self.btn_cerrar, border_radius=6)
        pygame.draw.rect(self.pantalla, (255, 255, 255), self.btn_cerrar, width=2, border_radius=6)
        txt_x = self.fuente_seccion.render("X", True, (255, 255, 255))
        self.pantalla.blit(txt_x, txt_x.get_rect(center=self.btn_cerrar.center))

        # Línea divisoria roja horizontal
        y_div = rect_box.y + 75
        pygame.draw.line(self.pantalla, (220, 20, 60), (rect_box.x + 10, y_div), (rect_box.right - 10, y_div), 3)

        # Área recortada (Clip) para las reglas con scroll
        rect_clip = pygame.Rect(rect_box.x + 20, y_div + 15, w_box - 40, h_box - 105)
        self.pantalla.set_clip(rect_clip)

        lineas_reglas = Reglas.obtener_texto_reglas()

        y_offset = rect_clip.y - self.scroll_y
        max_y_alcanzado = y_offset

        for linea in lineas_reglas:
            if not linea.strip():
                y_offset += 12
                continue

            # Título de sección (ej: "1. Objetivo del Juego:")
            if linea[0].isdigit() and "." in linea[:3]:
                txt_surf = self._render_texto_delineado(linea, self.fuente_seccion, (255, 220, 0), (0, 0, 0), 1)
                self.pantalla.blit(txt_surf, (rect_clip.x + 5, y_offset))
                y_offset += 26
            else:
                # Viñeta / Detalle (ej: "   • Ser el primer jugador...")
                txt_surf = self._render_texto_delineado(linea.strip(), self.fuente_texto, (255, 255, 255), (0, 0, 0), 1)
                self.pantalla.blit(txt_surf, (rect_clip.x + 25, y_offset))
                y_offset += 24

            max_y_alcanzado = y_offset

        # Desactivar clip
        self.pantalla.set_clip(None)

        # Indicador visual de scroll si el contenido supera el área
        altura_total = max_y_alcanzado - (rect_clip.y - self.scroll_y)
        if altura_total > rect_clip.height:
            self.max_scroll = max(0, altura_total - rect_clip.height + 20)
            # Dibujar barra de scroll tenue a la derecha
            sb_w = 6
            sb_h = max(20, int((rect_clip.height / altura_total) * rect_clip.height))
            sb_y = rect_clip.y + int((self.scroll_y / self.max_scroll) * (rect_clip.height - sb_h))
            pygame.draw.rect(self.pantalla, (80, 120, 200), (rect_box.right - 14, rect_clip.y, sb_w, rect_clip.height), border_radius=3)
            pygame.draw.rect(self.pantalla, (255, 220, 0), (rect_box.right - 14, sb_y, sb_w, sb_h), border_radius=3)
        else:
            self.max_scroll = 0

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                if self.btn_cerrar.collidepoint(evento.pos):
                    self.gestor.volverDeReglas()
            elif evento.button == 4:  # Scroll Up
                self.scroll_y = max(0, self.scroll_y - 25)
            elif evento.button == 5:  # Scroll Down
                if hasattr(self, 'max_scroll'):
                    self.scroll_y = min(self.max_scroll, self.scroll_y + 25)
        elif evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.gestor.volverDeReglas()
            elif evento.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - 25)
            elif evento.key == pygame.K_DOWN:
                if hasattr(self, 'max_scroll'):
                    self.scroll_y = min(self.max_scroll, self.scroll_y + 25)
