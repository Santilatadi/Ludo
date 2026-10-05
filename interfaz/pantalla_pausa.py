"""
Modulo pantalla_pausa.py
Dibuja e interactúa con el Menú de Pausa y la Ventana de Reinicio de Partida.
Adaptado 100% al diseño visual exacto de Figma.
"""

import os
import sys

directorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if directorio_raiz not in sys.path:
    sys.path.insert(0, directorio_raiz)

import pygame


class PantallaPausa:

    def __init__(self, pantalla, gestor_partida, persistencia):
        self.pantalla = pantalla
        self.gestor = gestor_partida
        self.persistencia = persistencia

        ruta_fuente = "assets/font.ttf"
        if os.path.exists(ruta_fuente):
            self.fuente_titulo = pygame.font.Font(ruta_fuente, 42)
            self.fuente_sub = pygame.font.Font(ruta_fuente, 18)
            self.fuente_boton = pygame.font.Font(ruta_fuente, 24)
        else:
            self.fuente_titulo = pygame.font.SysFont("Impact", 40, bold=True)
            self.fuente_sub = pygame.font.SysFont("Arial", 18, bold=True)
            self.fuente_boton = pygame.font.SysFont("Arial", 22, bold=True)

        self.confirmando_accion = None  # None, "REINICIAR" o "SALIR"
        self.mensaje_toast = ""

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
        superficie_oscura.fill((10, 15, 25, 170))
        self.pantalla.blit(superficie_oscura, (0, 0))

        # Ventana Modal (Azul con borde Rojo)
        w_box, h_box = 440, 420
        rect_box = pygame.Rect((ancho - w_box) // 2, (alto - h_box) // 2, w_box, h_box)

        pygame.draw.rect(self.pantalla, (16, 56, 168), rect_box, border_radius=6)
        pygame.draw.rect(self.pantalla, (220, 20, 60), rect_box, width=4, border_radius=6)

        if self.confirmando_accion:
            self._dibujar_modal_confirmacion(rect_box)
            return

        # Header "Pausa"
        txt_tit = self._render_texto_delineado("Pausa", self.fuente_titulo, (255, 255, 255), (0, 0, 0), 2)
        rect_tit = txt_tit.get_rect(center=(ancho // 2, rect_box.y + 45))
        self.pantalla.blit(txt_tit, rect_tit)

        # Línea divisoria roja horizontal
        y_div = rect_box.y + 85
        pygame.draw.line(self.pantalla, (220, 20, 60), (rect_box.x + 4, y_div), (rect_box.right - 4, y_div), 3)

        # 3 Botones apilados con fondo blanco y BORDE ROJO como Figma:
        # Continuar, Reglas, Volver al Menu
        pos_y_base = y_div + 25
        bw, bh = 280, 52
        bx = (ancho - bw) // 2

        self.btn_continuar = pygame.Rect(bx, pos_y_base, bw, bh)
        self.btn_reglas = pygame.Rect(bx, pos_y_base + 75, bw, bh)
        self.btn_menu = pygame.Rect(bx, pos_y_base + 150, bw, bh)
        self.btn_guardar = pygame.Rect(bx, pos_y_base + 225, bw, 36)

        pos_m = pygame.mouse.get_pos()
        self._dibujar_boton_pausa_figma(self.btn_continuar, "Continuar", pos_m)
        self._dibujar_boton_pausa_figma(self.btn_reglas, "Reglas", pos_m)
        self._dibujar_boton_pausa_figma(self.btn_menu, "Volver al Menu", pos_m)

        # Botón Guardar
        self._dibujar_boton_pausa_figma(self.btn_guardar, "Guardar Partida", pos_m)

        if self.mensaje_toast:
            txt_t = self.fuente_sub.render(self.mensaje_toast, True, (100, 255, 100))
            self.pantalla.blit(txt_t, txt_t.get_rect(center=(ancho // 2, rect_box.bottom - 15)))

    def _dibujar_modal_confirmacion(self, rect_box):
        ancho, alto = self.pantalla.get_size()

        titulo_str = "Reiniciar" if self.confirmando_accion == "REINICIAR" else "Salir"
        txt_tit = self._render_texto_delineado(titulo_str, self.fuente_titulo, (255, 255, 255), (0, 0, 0), 2)
        self.pantalla.blit(txt_tit, txt_tit.get_rect(center=(ancho // 2, rect_box.y + 45)))

        y_div = rect_box.y + 85
        pygame.draw.line(self.pantalla, (220, 20, 60), (rect_box.x + 4, y_div), (rect_box.right - 4, y_div), 3)

        txt1 = self._render_texto_delineado("Esta accion eliminará todo el", self.fuente_sub, (255, 255, 255), (0, 0, 0), 1)
        txt1_2 = self._render_texto_delineado("progreso de esta partida.", self.fuente_sub, (255, 255, 255), (0, 0, 0), 1)
        txt2 = self._render_texto_delineado("Esta seguro?", self.fuente_sub, (255, 255, 255), (0, 0, 0), 1)

        self.pantalla.blit(txt1, txt1.get_rect(center=(ancho // 2, rect_box.y + 130)))
        self.pantalla.blit(txt1_2, txt1_2.get_rect(center=(ancho // 2, rect_box.y + 155)))
        self.pantalla.blit(txt2, txt2.get_rect(center=(ancho // 2, rect_box.y + 200)))

        bw, bh = 150, 48
        self.btn_conf_no = pygame.Rect(ancho // 2 - 165, rect_box.y + 270, bw, bh)
        self.btn_conf_si = pygame.Rect(ancho // 2 + 15, rect_box.y + 270, bw, bh)

        pos_m = pygame.mouse.get_pos()
        self._dibujar_boton_pausa_figma(self.btn_conf_no, "CANCELAR", pos_m)
        self._dibujar_boton_pausa_figma(self.btn_conf_si, "CONFIRMAR", pos_m)

    def _dibujar_boton_pausa_figma(self, rect, texto, pos_mouse):
        hover = rect.collidepoint(pos_mouse)
        color_bg = (240, 240, 245) if hover else (255, 255, 255)

        # Fondo blanco rectangular con BORDE ROJO como Figma
        pygame.draw.rect(self.pantalla, color_bg, rect, border_radius=6)
        pygame.draw.rect(self.pantalla, (220, 20, 60), rect, width=3, border_radius=6)

        # Texto Azul Noche nítido sin sobre-delineado negro
        txt = self.fuente_boton.render(texto, True, (16, 45, 120))
        self.pantalla.blit(txt, txt.get_rect(center=rect.center))

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos

            if self.confirmando_accion:
                if self.btn_conf_si.collidepoint(pos):
                    if self.confirmando_accion == "REINICIAR":
                        self.confirmando_accion = None
                        self.gestor.cancelarPartida()
                        self.gestor.estado = "CONFIGURACION"
                    elif self.confirmando_accion == "SALIR":
                        self.confirmando_accion = None
                        self.gestor.cancelarPartida()

                elif self.btn_conf_no.collidepoint(pos):
                    self.confirmando_accion = None
                return

            if self.btn_continuar.collidepoint(pos):
                self.gestor.reanudar()

            elif self.btn_reglas.collidepoint(pos):
                self.gestor.consultarReglas()

            elif self.btn_menu.collidepoint(pos):
                self.confirmando_accion = "SALIR"

            elif self.btn_guardar.collidepoint(pos):
                if self.gestor.partidaActual:
                    exito, msg = self.persistencia.guardarPartida(self.gestor.partidaActual)
                    self.mensaje_toast = msg
                    if exito:
                        self.gestor.estado = "MENU"
