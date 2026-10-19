"""
Modulo pantalla_reglas.py
Dibuja e interactúa con la Ventana de Reglas del Ludo.
Muestra todas las reglas detalladas con alta legibilidad, estilización glassmorphism y soporte para scroll.
"""

import os
import sys
import pygame

directorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if directorio_raiz not in sys.path:
    sys.path.insert(0, directorio_raiz)

from logica.reglas import Reglas
from interfaz.efectos import dibujar_panel_glassmorphism, dibujar_texto_glow
from interfaz.componentes import BotonModerno


class PantallaReglas:

    def __init__(self, pantalla, gestor_partida):
        self.pantalla = pantalla
        self.gestor = gestor_partida
        self.scroll_y = 0

        ruta_fuente = "assets/font.ttf"
        if os.path.exists(ruta_fuente):
            self.fuente_titulo = pygame.font.Font(ruta_fuente, 38)
            self.fuente_seccion = pygame.font.Font(ruta_fuente, 18)
            self.fuente_texto = pygame.font.Font(ruta_fuente, 15)
        else:
            self.fuente_titulo = pygame.font.SysFont("Impact", 36, bold=True)
            self.fuente_seccion = pygame.font.SysFont("Arial", 18, bold=True)
            self.fuente_texto = pygame.font.SysFont("Arial", 15, bold=True)

    def dibujar(self):
        ancho, alto = self.pantalla.get_size()

        # Capa translúcida sobre la pantalla de juego
        superficie_oscura = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        superficie_oscura.fill((5, 10, 25, 190))
        self.pantalla.blit(superficie_oscura, (0, 0))

        # Ventana Modal Glassmorphism
        w_box, h_box = min(660, ancho - 40), min(520, alto - 40)
        rect_box = pygame.Rect((ancho - w_box) // 2, (alto - h_box) // 2, w_box, h_box)

        dibujar_panel_glassmorphism(
            self.pantalla, rect_box,
            color_bg=(16, 35, 95, 240),
            color_borde=(255, 215, 0, 220),
            radio=20, grosor_borde=3
        )

        # Encabezado "REGLAS DEL JUEGO"
        dibujar_texto_glow(
            self.pantalla, "REGLAS DEL JUEGO", self.fuente_titulo,
            ancho // 2, rect_box.y + 40,
            color_texto=(255, 220, 0), color_resplandor=(255, 120, 0), centro=True
        )

        # Botón X de cerrar en la esquina superior derecha
        self.btn_cerrar_inst = BotonModerno(
            (rect_box.right - 45, rect_box.y + 15, 34, 34), "X",
            color_base=(220, 40, 50), fuente=self.fuente_seccion
        )
        self.btn_cerrar_inst.dibujar(self.pantalla)

        # Línea divisoria roja horizontal
        y_div = rect_box.y + 75
        pygame.draw.line(self.pantalla, (220, 20, 60), (rect_box.x + 20, y_div), (rect_box.right - 20, y_div), 2)

        # Área recortada (Clip) para las reglas con scroll
        rect_clip = pygame.Rect(rect_box.x + 25, y_div + 15, w_box - 50, h_box - 105)
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
                dibujar_texto_glow(
                    self.pantalla, linea, self.fuente_seccion,
                    rect_clip.x + 5, y_offset,
                    color_texto=(255, 220, 0), color_resplandor=(0, 0, 0)
                )
                y_offset += 28
            else:
                # Viñeta / Detalle
                txt_surf = self.fuente_texto.render(linea.strip(), True, (240, 240, 255))
                self.pantalla.blit(txt_surf, (rect_clip.x + 25, y_offset))
                y_offset += 24

            max_y_alcanzado = y_offset

        # Desactivar clip
        self.pantalla.set_clip(None)

        # Indicador visual de scroll
        altura_total = max_y_alcanzado - (rect_clip.y - self.scroll_y)
        if altura_total > rect_clip.height:
            self.max_scroll = max(0, altura_total - rect_clip.height + 20)
            sb_w = 8
            sb_h = max(24, int((rect_clip.height / altura_total) * rect_clip.height))
            sb_y = rect_clip.y + int((self.scroll_y / self.max_scroll) * (rect_clip.height - sb_h))
            pygame.draw.rect(self.pantalla, (40, 60, 100), (rect_box.right - 16, rect_clip.y, sb_w, rect_clip.height), border_radius=4)
            pygame.draw.rect(self.pantalla, (255, 215, 0), (rect_box.right - 16, sb_y, sb_w, sb_h), border_radius=4)
        else:
            self.max_scroll = 0

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                if hasattr(self, 'btn_cerrar_inst') and self.btn_cerrar_inst.es_cliqueado(evento):
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
