"""
Modulo componentes.py
Componentes de interfaz de usuario modernos, interactivos y adaptativos para Pygame.
Incluye botones con animación suave de escalado y diseño glassmorphism.
"""

import pygame
from interfaz.efectos import dibujar_panel_glassmorphism, dibujar_texto_glow


class BotonModerno:
    def __init__(self, rect, texto, color_base=(25, 75, 175), color_hover=(45, 115, 235), color_texto=(255, 255, 255), color_borde=(0, 220, 255), fuente=None, icono=""):
        self.rect_base = pygame.Rect(rect)
        self.rect_anim = pygame.Rect(rect)
        self.texto = texto
        self.color_base = color_base
        self.color_hover = color_hover
        self.color_texto = color_texto
        self.color_borde = color_borde
        self.fuente = fuente
        self.icono = icono

        self.es_hover = False
        self.es_hover_prev = False
        self.escala_actual = 1.0

    def actualizar(self, pos_mouse):
        self.es_hover_prev = self.es_hover
        self.es_hover = self.rect_base.collidepoint(pos_mouse)

        target_escala = 1.04 if self.es_hover else 1.0
        self.escala_actual += (target_escala - self.escala_actual) * 0.25

        # Re-calcular rectángulo escalado manteniendo el centro
        w_scaled = int(self.rect_base.width * self.escala_actual)
        h_scaled = int(self.rect_base.height * self.escala_actual)
        cx, cy = self.rect_base.center
        self.rect_anim = pygame.Rect(cx - w_scaled // 2, cy - h_scaled // 2, w_scaled, h_scaled)

    def dibujar(self, pantalla):
        pos_m = pygame.mouse.get_pos()
        self.actualizar(pos_m)

        col = self.color_hover if self.es_hover else self.color_base

        # Glassmorphism/Panel con sombra
        borde = self.color_borde if self.es_hover else (self.color_borde[0], self.color_borde[1], self.color_borde[2], 120)
        dibujar_panel_glassmorphism(pantalla, self.rect_anim, color_bg=(col[0], col[1], col[2], 220), color_borde=borde, radio=10)

        # Texto con icono
        str_display = f"{self.icono} {self.texto}".strip() if self.icono else self.texto

        if self.fuente:
            if self.es_hover:
                dibujar_texto_glow(pantalla, str_display, self.fuente, self.rect_anim.centerx, self.rect_anim.centery, color_texto=self.color_texto, color_resplandor=self.color_borde, centro=True)
            else:
                txt_s = self.fuente.render(str_display, True, self.color_texto)
                pantalla.blit(txt_s, txt_s.get_rect(center=self.rect_anim.center))

    def es_cliqueado(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect_anim.collidepoint(evento.pos):
                return True
        return False
