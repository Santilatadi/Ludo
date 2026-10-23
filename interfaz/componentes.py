"""
Modulo componentes.py
Componentes de interfaz de usuario modernos, interactivos y adaptativos para Pygame.
Incluye botones con animación suave de escalado y el estilo del diseño de Figma
(relleno de color, borde redondeado y texto con contorno).
"""

import pygame


class BotonModerno:
    def __init__(self, rect, texto, color_base=(25, 75, 175), color_hover=(45, 115, 235), color_texto=(255, 255, 255), color_borde=(255, 251, 0), fuente=None, icono=""):
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
        radio = min(self.rect_anim.height // 2, 24)

        # Sombra, relleno y borde como en los botones del Figma
        sombra = self.rect_anim.move(0, 4)
        pygame.draw.rect(pantalla, (20, 0, 50), sombra, border_radius=radio)
        pygame.draw.rect(pantalla, col[:3], self.rect_anim, border_radius=radio)
        pygame.draw.rect(pantalla, self.color_borde[:3], self.rect_anim, width=3 if self.es_hover else 2, border_radius=radio)

        str_display = f"{self.icono} {self.texto}".strip() if self.icono else self.texto
        if self.fuente:
            base = self.fuente.render(str_display, True, self.color_texto)
            contorno = self.fuente.render(str_display, True, (40, 0, 90))
            rect_txt = base.get_rect(center=self.rect_anim.center)
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)):
                pantalla.blit(contorno, rect_txt.move(dx, dy))
            pantalla.blit(base, rect_txt)

    def es_cliqueado(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect_anim.collidepoint(evento.pos):
                return True
        return False


class BotonDegradado(BotonModerno):
    """Botón grande con degradé vertical (por ejemplo, INICIAR de Nueva Partida en el Figma)."""

    def __init__(self, rect, texto, colores, fuente=None, color_borde=None):
        super().__init__(rect, texto, fuente=fuente, color_borde=color_borde or (255, 251, 0))
        self.colores = colores

    def dibujar(self, pantalla):
        from interfaz import tema
        self.actualizar(pygame.mouse.get_pos())
        radio = min(self.rect_anim.height // 3, 30)
        pygame.draw.rect(pantalla, (20, 0, 50), self.rect_anim.move(0, 5), border_radius=radio)
        tema.panel(pantalla, self.rect_anim, self.colores, self.color_borde, radio=radio,
                   grosor=3 if self.es_hover else 0)
        if self.fuente:
            base = self.fuente.render(self.texto, True, self.color_texto)
            contorno = self.fuente.render(self.texto, True, (120, 10, 10))
            rect_txt = base.get_rect(center=self.rect_anim.center)
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                pantalla.blit(contorno, rect_txt.move(dx, dy))
            pantalla.blit(base, rect_txt)


class BotonFigma(BotonModerno):
    """Botón dibujado con las medidas del Figma: rectángulo (con degradé o color liso),
    borde de color y texto Goldman con trazo. `rect_figma` está en coordenadas del Figma."""

    def __init__(self, pantalla, rect_figma, texto, relleno, borde, trazo=4, radio=0, tam_texto=48,
                 color_texto=(255, 255, 255), contorno_texto=(0, 0, 0), trazo_texto=4, alinear="centro",
                 margen_texto=0):
        from interfaz import tema
        super().__init__(tema.R(pantalla, *rect_figma), texto)
        self.pantalla_ref = pantalla
        self.rect_figma = rect_figma
        self.relleno, self.borde, self.trazo, self.radio = relleno, borde, trazo, radio
        self.tam_texto, self.color_texto, self.contorno_texto = tam_texto, color_texto, contorno_texto
        self.trazo_texto, self.alinear, self.margen_texto = trazo_texto, alinear, margen_texto

    def actualizar(self, pos_mouse):
        self.es_hover = self.rect_base.collidepoint(pos_mouse)
        self.rect_anim = self.rect_base

    def dibujar(self, pantalla):
        from interfaz import tema
        self.actualizar(pygame.mouse.get_pos())
        x, y, w, h = self.rect_figma
        tema.panel_figma(pantalla, x, y, w, h, self.relleno, self.borde, self.trazo, self.radio)
        if self.es_hover:
            capa = pygame.Surface(self.rect_base.size, pygame.SRCALPHA)
            pygame.draw.rect(capa, (255, 255, 255, 35), capa.get_rect(), border_radius=tema.T(pantalla, self.radio))
            pantalla.blit(capa, self.rect_base.topleft)
        lineas = self.texto.split("\n")
        for i, linea in enumerate(lineas):
            cy = y + h / 2 + (i - (len(lineas) - 1) / 2) * self.tam_texto * 1.15
            g = tema.T(pantalla, self.trazo_texto / 2) if self.contorno_texto else 0
            surf = tema.render_texto(linea, tema.T(pantalla, self.tam_texto), self.color_texto,
                                     self.contorno_texto, g)
            if self.alinear == "izquierda":
                rect = surf.get_rect(midleft=tema.P(pantalla, x + self.margen_texto, cy))
            else:
                rect = surf.get_rect(center=tema.P(pantalla, x + w / 2, cy))
            pantalla.blit(surf, rect)
