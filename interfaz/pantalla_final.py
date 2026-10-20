"""
Modulo pantalla_final.py
Dibuja e interactúa con la Pantalla de Victoria / Finalización (Menú Victoria).
Celebra la victoria del ganador con ráfagas de confeti y efectos de resplandor.
"""

import pygame
from interfaz.efectos import SistemaParticulas, dibujar_panel_glassmorphism, dibujar_texto_glow
from interfaz.componentes import BotonModerno


class PantallaFinal:

    def __init__(self, pantalla, gestor_partida):
        self.pantalla = pantalla
        self.gestor = gestor_partida
        self.particulas = SistemaParticulas()

        self.fuente_banner = pygame.font.SysFont("Impact", 46, bold=True)
        if not self.fuente_banner:
            self.fuente_banner = pygame.font.SysFont("Arial", 44, bold=True)

        self.fuente_sub = pygame.font.SysFont("Arial", 22, bold=True)
        self.fuente_boton = pygame.font.SysFont("Arial", 22, bold=True)

        self.confeti_emitido = False

    def dibujar(self):
        ancho, alto = self.pantalla.get_size()

        # Emitir gran explosión de confeti la primera vez que se dibuja
        if not self.confeti_emitido:
            self.confeti_emitido = True
            self.particulas.emitir_confeti(ancho // 2, alto // 2, 140)

        # Capa translúcida sobre el juego
        superficie_oscura = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        superficie_oscura.fill((5, 10, 25, 180))
        self.pantalla.blit(superficie_oscura, (0, 0))

        # Dibujar fuegos artificiales/confeti
        self.particulas.actualizar_y_dibujar(self.pantalla)

        # Ventana Modal Glassmorphism Amarilla / Dorada
        w_box, h_box = 460, 420
        rect_box = pygame.Rect((ancho - w_box) // 2, (alto - h_box) // 2, w_box, h_box)

        dibujar_panel_glassmorphism(
            self.pantalla, rect_box,
            color_bg=(40, 30, 10, 240),
            color_borde=(255, 215, 0, 240),
            radio=20, grosor_borde=4
        )

        # Banner Superior de ¡VICTORIA IMPERIAL!
        rect_banner = pygame.Rect(rect_box.x + 20, rect_box.y + 25, rect_box.width - 40, 70)
        dibujar_panel_glassmorphism(self.pantalla, rect_banner, color_bg=(220, 30, 50, 220), color_borde=(255, 230, 0), radio=12)

        dibujar_texto_glow(
            self.pantalla, "¡VICTORIA!", self.fuente_banner,
            rect_banner.centerx, rect_banner.centery,
            color_texto=(255, 255, 255), color_resplandor=(255, 215, 0), centro=True
        )

        # Nombre del Ganador
        partida = self.gestor.partidaActual
        nombre_ganador = partida.ganador.nombre if (partida and partida.ganador) else "Jugador 1"

        dibujar_texto_glow(
            self.pantalla, f"¡{nombre_ganador}!", self.fuente_sub,
            ancho // 2, rect_box.y + 140,
            color_texto=(255, 220, 40), color_resplandor=(255, 100, 0), centro=True
        )

        txt_gan2 = self.fuente_sub.render("¡HA GANADO LA PARTIDA!", True, (240, 240, 255))
        self.pantalla.blit(txt_gan2, txt_gan2.get_rect(center=(ancho // 2, rect_box.y + 180)))

        # Botones Reiniciar y Volver al Menú
        bw, bh = 260, 46
        self.btn_reiniciar_inst = BotonModerno(
            ((ancho - bw) // 2, rect_box.bottom - 125, bw, bh), "Reiniciar Partida",
            color_base=(40, 160, 80), color_hover=(60, 190, 100),
            color_borde=(255, 215, 0), fuente=self.fuente_boton, icono=""
        )
        self.btn_menu_inst = BotonModerno(
            ((ancho - bw) // 2, rect_box.bottom - 65, bw, bh), "Volver al Menú",
            color_base=(16, 56, 168), color_hover=(35, 95, 235),
            color_borde=(255, 215, 0), fuente=self.fuente_boton, icono=""
        )
        self.btn_reiniciar_inst.dibujar(self.pantalla)
        self.btn_menu_inst.dibujar(self.pantalla)

    def manejar_evento(self, evento):
        if hasattr(self, 'btn_reiniciar_inst') and self.btn_reiniciar_inst.es_cliqueado(evento):
            self.confeti_emitido = False
            self.gestor.reiniciarPartida()

        elif hasattr(self, 'btn_menu_inst') and self.btn_menu_inst.es_cliqueado(evento):
            self.confeti_emitido = False
            self.gestor.cancelarPartida()
