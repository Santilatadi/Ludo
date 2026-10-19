"""
Modulo pantalla_pausa.py
Dibuja e interactúa con el Menú de Pausa y la Ventana de Reinicio de Partida.
Adaptado con contenedores glassmorphism, botones modernos interactivos y notificaciones toast.
"""

import os
import sys
import pygame

directorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if directorio_raiz not in sys.path:
    sys.path.insert(0, directorio_raiz)

from interfaz.efectos import dibujar_panel_glassmorphism, dibujar_texto_glow
from interfaz.componentes import BotonModerno, BotonMute


class PantallaPausa:

    def __init__(self, pantalla, gestor_partida, persistencia):
        self.pantalla = pantalla
        self.gestor = gestor_partida
        self.persistencia = persistencia

        ruta_fuente = "assets/font.ttf"
        if os.path.exists(ruta_fuente):
            self.fuente_titulo = pygame.font.Font(ruta_fuente, 42)
            self.fuente_sub = pygame.font.Font(ruta_fuente, 18)
            self.fuente_boton = pygame.font.Font(ruta_fuente, 22)
        else:
            self.fuente_titulo = pygame.font.SysFont("Impact", 40, bold=True)
            self.fuente_sub = pygame.font.SysFont("Arial", 18, bold=True)
            self.fuente_boton = pygame.font.SysFont("Arial", 22, bold=True)

        self.confirmando_accion = None  # None, "REINICIAR" o "SALIR"
        self.mensaje_toast = ""
        self.btn_mute = BotonMute(10, 10)

    def dibujar(self):
        ancho, alto = self.pantalla.get_size()

        # Capa translúcida sobre la pantalla de juego
        superficie_oscura = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        superficie_oscura.fill((5, 10, 25, 180))
        self.pantalla.blit(superficie_oscura, (0, 0))

        # Ventana Modal Glassmorphism
        w_box, h_box = min(460, ancho - 40), min(500, alto - 40)
        rect_box = pygame.Rect((ancho - w_box) // 2, (alto - h_box) // 2, w_box, h_box)

        dibujar_panel_glassmorphism(
            self.pantalla, rect_box,
            color_bg=(16, 35, 95, 235),
            color_borde=(255, 215, 0, 220),
            radio=20, grosor_borde=3
        )

        if self.confirmando_accion:
            self._dibujar_modal_confirmacion(rect_box)
            return

        # Header "PAUSA"
        dibujar_texto_glow(
            self.pantalla, "PAUSA", self.fuente_titulo,
            ancho // 2, rect_box.y + 45,
            color_texto=(255, 255, 255), color_resplandor=(255, 215, 0), centro=True
        )

        # Línea divisoria roja horizontal
        y_div = rect_box.y + 85
        pygame.draw.line(self.pantalla, (220, 20, 60), (rect_box.x + 20, y_div), (rect_box.right - 20, y_div), 2)

        # Botones apilados
        pos_y_base = y_div + 15
        bw, bh = 280, 44
        bx = (ancho - bw) // 2

        self.btn_continuar_inst = BotonModerno(
            (bx, pos_y_base, bw, bh), "Continuar",
            color_base=(0, 85, 255), color_hover=(35, 115, 255),
            fuente=self.fuente_boton, icono=""
        )
        self.btn_reiniciar_inst = BotonModerno(
            (bx, pos_y_base + 52, bw, bh), "Reiniciar Partida",
            color_base=(210, 110, 20), color_hover=(235, 135, 35),
            fuente=self.fuente_boton, icono=""
        )
        self.btn_reglas_inst = BotonModerno(
            (bx, pos_y_base + 104, bw, bh), "Reglas",
            color_base=(0, 85, 255), color_hover=(35, 115, 255),
            fuente=self.fuente_boton, icono=""
        )
        self.btn_stats_inst = BotonModerno(
            (bx, pos_y_base + 156, bw, bh), "Estadísticas",
            color_base=(0, 85, 255), color_hover=(35, 115, 255),
            fuente=self.fuente_boton, icono=""
        )
        self.btn_guardar_inst = BotonModerno(
            (bx, pos_y_base + 208, bw, bh), "Guardar Partida",
            color_base=(40, 160, 80), color_hover=(60, 190, 100),
            fuente=self.fuente_boton, icono=""
        )
        self.btn_menu_inst = BotonModerno(
            (bx, pos_y_base + 260, bw, bh), "Volver al Menú",
            color_base=(200, 40, 50), color_hover=(230, 60, 70),
            fuente=self.fuente_boton, icono=""
        )

        self.btn_continuar_inst.dibujar(self.pantalla)
        self.btn_reiniciar_inst.dibujar(self.pantalla)
        self.btn_reglas_inst.dibujar(self.pantalla)
        self.btn_stats_inst.dibujar(self.pantalla)
        self.btn_guardar_inst.dibujar(self.pantalla)
        self.btn_menu_inst.dibujar(self.pantalla)

        if self.mensaje_toast:
            dibujar_texto_glow(
                self.pantalla, self.mensaje_toast, self.fuente_sub,
                ancho // 2, rect_box.bottom - 15,
                color_texto=(100, 255, 100), color_resplandor=(0, 200, 0), centro=True
            )


    def _dibujar_modal_confirmacion(self, rect_box):
        ancho, alto = self.pantalla.get_size()

        titulo_str = "REINICIAR" if self.confirmando_accion == "REINICIAR" else "SALIR AL MENÚ"
        dibujar_texto_glow(
            self.pantalla, titulo_str, self.fuente_titulo,
            ancho // 2, rect_box.y + 45,
            color_texto=(255, 220, 0), color_resplandor=(255, 50, 50), centro=True
        )

        y_div = rect_box.y + 85
        pygame.draw.line(self.pantalla, (220, 20, 60), (rect_box.x + 20, y_div), (rect_box.right - 20, y_div), 2)

        txt1 = self.fuente_sub.render("Esta acción descartará todo el", True, (240, 240, 255))
        txt1_2 = self.fuente_sub.render("progreso no guardado de esta partida.", True, (240, 240, 255))
        txt2 = self.fuente_sub.render("¿Estás seguro de continuar?", True, (255, 220, 100))

        self.pantalla.blit(txt1, txt1.get_rect(center=(ancho // 2, rect_box.y + 130)))
        self.pantalla.blit(txt1_2, txt1_2.get_rect(center=(ancho // 2, rect_box.y + 155)))
        self.pantalla.blit(txt2, txt2.get_rect(center=(ancho // 2, rect_box.y + 200)))

        bw, bh = 150, 48
        self.btn_conf_no_inst = BotonModerno(
            (ancho // 2 - 165, rect_box.y + 270, bw, bh), "CANCELAR",
            color_base=(80, 90, 110), fuente=self.fuente_boton
        )
        self.btn_conf_si_inst = BotonModerno(
            (ancho // 2 + 15, rect_box.y + 270, bw, bh), "CONFIRMAR",
            color_base=(220, 40, 50), fuente=self.fuente_boton
        )

        self.btn_conf_no_inst.dibujar(self.pantalla)
        self.btn_conf_si_inst.dibujar(self.pantalla)

    def manejar_evento(self, evento):

        if self.confirmando_accion:
            if hasattr(self, 'btn_conf_si_inst') and self.btn_conf_si_inst.es_cliqueado(evento):
                if self.confirmando_accion == "REINICIAR":
                    self.confirmando_accion = None
                    self.gestor.reiniciarPartida()
                elif self.confirmando_accion == "SALIR":
                    self.confirmando_accion = None
                    self.gestor.cancelarPartida()

            elif hasattr(self, 'btn_conf_no_inst') and self.btn_conf_no_inst.es_cliqueado(evento):
                self.confirmando_accion = None
            return

        if hasattr(self, 'btn_continuar_inst') and self.btn_continuar_inst.es_cliqueado(evento):
            self.gestor.reanudar()

        elif hasattr(self, 'btn_reiniciar_inst') and self.btn_reiniciar_inst.es_cliqueado(evento):
            self.confirmando_accion = "REINICIAR"

        elif hasattr(self, 'btn_reglas_inst') and self.btn_reglas_inst.es_cliqueado(evento):
            self.gestor.consultarReglas()

        elif hasattr(self, 'btn_stats_inst') and self.btn_stats_inst.es_cliqueado(evento):
            self.gestor.consultarEstadisticas()

        elif hasattr(self, 'btn_menu_inst') and self.btn_menu_inst.es_cliqueado(evento):
            self.confirmando_accion = "SALIR"

        elif hasattr(self, 'btn_guardar_inst') and self.btn_guardar_inst.es_cliqueado(evento):
            if self.gestor.partidaActual:
                exito, msg = self.persistencia.guardarPartida(self.gestor.partidaActual)
                self.mensaje_toast = "¡Partida guardada con éxito!" if exito else msg
