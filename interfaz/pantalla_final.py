"""
Modulo pantalla_final.py
Dibuja e interactúa con la Pantalla de Victoria / Finalización (Menu Victoria).
Adaptado fielmente al diseño de la interfaz de referencia.
"""

import pygame


class PantallaFinal:

    def __init__(self, pantalla, gestor_partida):
        self.pantalla = pantalla
        self.gestor = gestor_partida

        self.fuente_banner = pygame.font.SysFont("Impact", 42, bold=True)
        if not self.fuente_banner:
            self.fuente_banner = pygame.font.SysFont("Arial", 40, bold=True)

        self.fuente_sub = pygame.font.SysFont("Arial", 20, bold=True)
        self.fuente_boton = pygame.font.SysFont("Arial", 20, bold=True)

    def _render_texto_delineado(self, texto, fuente, color_texto, color_borde=(0, 0, 0), grosor=2):
        surf_base = fuente.render(texto, True, color_texto)
        w, h = surf_base.get_size()
        surf_final = pygame.Surface((w + grosor * 2, h + grosor * 2), pygame.SRCALPHA)

        for dx in range(-grosor, grosor + 1):
            for dy in range(-grosor, grosor + 1):
                if dx != 0 or dy != 0:
                    surf_borde = fuente.render(texto, True, color_borde)
                    surf_final.blit(surf_borde, (dx + grosor, dy + grosor))

        surf_final.blit(surf_base, (grosor, grosor))
        return surf_final

    def dibujar(self):
        ancho, alto = self.pantalla.get_size()

        # Capa translúcida sobre la pantalla de juego
        superficie_oscura = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        superficie_oscura.fill((10, 15, 25, 170))
        self.pantalla.blit(superficie_oscura, (0, 0))

        # Ventana Modal Amarilla con borde Rojo
        w_box, h_box = 440, 360
        rect_box = pygame.Rect((ancho - w_box) // 2, (alto - h_box) // 2, w_box, h_box)

        pygame.draw.rect(self.pantalla, (245, 245, 120), rect_box, border_radius=12)
        pygame.draw.rect(self.pantalla, (220, 25, 50), rect_box, width=4, border_radius=12)

        # Banner Superior de ¡GANASTE!
        rect_banner = pygame.Rect(rect_box.x + 20, rect_box.y + 25, rect_box.width - 40, 65)
        pygame.draw.rect(self.pantalla, (255, 255, 255), rect_banner, border_radius=8)
        pygame.draw.rect(self.pantalla, (220, 25, 50), rect_banner, width=3, border_radius=8)

        txt_ganaste = self._render_texto_delineado("¡GANASTE!", self.fuente_banner, (255, 255, 255), (220, 25, 50), 3)
        self.pantalla.blit(txt_ganaste, txt_ganaste.get_rect(center=rect_banner.center))

        # Nombre del Ganador
        partida = self.gestor.partidaActual
        nombre_ganador = partida.ganador.nombre if (partida and partida.ganador) else "Jugador 1"

        txt_gan = self.fuente_sub.render(f"¡'{nombre_ganador}'", True, (20, 20, 20))
        txt_gan2 = self.fuente_sub.render("GANÓ LA PARTIDA!", True, (20, 20, 20))

        self.pantalla.blit(txt_gan, txt_gan.get_rect(center=(ancho // 2, rect_box.y + 140)))
        self.pantalla.blit(txt_gan2, txt_gan2.get_rect(center=(ancho // 2, rect_box.y + 170)))

        # Botón Volver al Menu blanco con icono circular ↺
        bw, bh = 260, 52
        self.btn_menu = pygame.Rect((ancho - bw) // 2, rect_box.bottom - 80, bw, bh)

        pos_m = pygame.mouse.get_pos()
        hover = self.btn_menu.collidepoint(pos_m)
        color_btn = (235, 235, 235) if hover else (255, 255, 255)

        pygame.draw.rect(self.pantalla, color_btn, self.btn_menu, border_radius=8)
        pygame.draw.rect(self.pantalla, (20, 20, 20), self.btn_menu, width=2, border_radius=8)

        txt_m = self.fuente_boton.render("Volver al Menu", True, (20, 20, 20))
        self.pantalla.blit(txt_m, (self.btn_menu.x + 20, self.btn_menu.centery - txt_m.get_height() // 2))

        # Icono circular azul ↺ a la derecha del botón
        r_circ = pygame.Rect(self.btn_menu.right - 42, self.btn_menu.centery - 18, 36, 36)
        pygame.draw.circle(self.pantalla, (40, 150, 240), r_circ.center, 18)
        txt_icon = self.fuente_sub.render("↺", True, (255, 255, 255))
        self.pantalla.blit(txt_icon, txt_icon.get_rect(center=r_circ.center))

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.btn_menu.collidepoint(evento.pos):
                self.gestor.cancelarPartida()
