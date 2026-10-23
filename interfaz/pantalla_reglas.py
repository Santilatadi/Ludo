"""
Modulo pantalla_reglas.py
Frame "Reglas" del Figma (CU-06): ventana con degradé azul y borde rojo, título
"Reglas del juego" en amarillo, una X para cerrar y las reglas con desplazamiento.
"""

import pygame

from interfaz import tema


class PantallaReglas:

    def __init__(self, pantalla, game_manager, interfaz=None):
        self.pantalla = pantalla
        self.gestor = game_manager
        self.interfaz = interfaz
        self.texto_reglas = ""
        self.scroll_y = 0
        self.max_scroll = 0

    def abrir(self):
        # CU-06: el GameManager obtiene las reglas de la persistencia
        self.scroll_y = 0
        self.texto_reglas = self.gestor.consultarReglas()

    def _cerrar(self):
        self.gestor.volverDeReglas()
        self.interfaz.estado = self.interfaz.estado_anterior

    def dibujar(self):
        p = self.pantalla
        tema.oscurecer(p)
        tema.panel_figma(p, 295, 57, 800, 800, tema.GRADIENTE, tema.ROJO_BORDE, 4)
        tema.texto_figma(p, "Reglas del juego", 0, 0, 48, (247, 255, 6), (173, 66, 4), 4, centrado_en=(681.5, 124.5))
        self.btn_cerrar_inst = tema.cruz_figma(p, 1020, 71)
        tema.linea_figma(p, 299, 193, 796)

        if not self.texto_reglas:
            # CU-06 A: no se pudieron cargar las reglas; se vuelve a intentar
            self.texto_reglas = self.gestor.consultarReglas()
        lineas = (self.texto_reglas or "1. No se pudieron cargar las reglas.\n   Reintentando...").split("\n")

        zona = tema.R(p, 330, 210, 740, 630)
        p.set_clip(zona)
        y = zona.y - self.scroll_y
        alto_titulo, alto_linea = tema.T(p, 40), tema.T(p, 32)
        for linea in lineas:
            if not linea.strip():
                y += tema.T(p, 14)
                continue
            if linea[0].isdigit() and "." in linea[:3]:
                surf = tema.render_texto(linea, tema.T(p, 32), (247, 255, 6), tema.NEGRO, tema.T(p, 2))
                p.blit(surf, (zona.x, y))
                y += alto_titulo
            else:
                for parte in self._partir(linea.strip(), tema.fuente(tema.T(p, 24)), zona.width - tema.T(p, 30)):
                    surf = tema.render_texto(parte, tema.T(p, 24), tema.BLANCO, tema.NEGRO, tema.T(p, 2))
                    p.blit(surf, (zona.x + tema.T(p, 26), y))
                    y += alto_linea
        p.set_clip(None)

        total = y + self.scroll_y - zona.y
        self.max_scroll = max(0, total - zona.height + tema.T(p, 20))
        if self.max_scroll:
            barra = pygame.Rect(zona.right + tema.T(p, 6), zona.y, tema.T(p, 10), zona.height)
            pygame.draw.rect(p, tema.NEGRO, barra, border_radius=barra.width // 2)
            alto = max(tema.T(p, 40), int(zona.height * zona.height / total))
            y0 = zona.y + int((zona.height - alto) * self.scroll_y / self.max_scroll)
            pygame.draw.rect(p, tema.BLANCO, (barra.x + 2, y0, barra.width - 4, alto), border_radius=barra.width // 2)

    def _partir(self, texto, fuente, ancho_max):
        palabras, lineas, actual = texto.split(), [], ""
        for palabra in palabras:
            prueba = f"{actual} {palabra}".strip()
            if fuente.size(prueba)[0] <= ancho_max or not actual:
                actual = prueba
            else:
                lineas.append(actual)
                actual = palabra
        if actual:
            lineas.append(actual)
        return lineas

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                if hasattr(self, 'btn_cerrar_inst') and self.btn_cerrar_inst.collidepoint(evento.pos):
                    self._cerrar()
            elif evento.button == 4:  # Scroll Up
                self.scroll_y = max(0, self.scroll_y - 25)
            elif evento.button == 5:  # Scroll Down
                if hasattr(self, 'max_scroll'):
                    self.scroll_y = min(self.max_scroll, self.scroll_y + 25)
        elif evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self._cerrar()
            elif evento.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - 25)
            elif evento.key == pygame.K_DOWN:
                if hasattr(self, 'max_scroll'):
                    self.scroll_y = min(self.max_scroll, self.scroll_y + 25)
