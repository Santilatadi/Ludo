"""
Modulo pantalla_pausa.py
Dibuja e interactúa con el Menú de Pausa (CU-10 a CU-12 y CU-14).
Permite reanudar, ver reglas, reiniciar, guardar la partida o salir al menú principal.
"""

import pygame


class PantallaPausa:

    def __init__(self, pantalla, gestor_partida, persistencia):
        self.pantalla = pantalla
        self.gestor = gestor_partida
        self.persistencia = persistencia
        self.fuente_titulo = pygame.font.SysFont("Arial", 40, bold=True)
        self.fuente_sub = pygame.font.SysFont("Arial", 20)
        self.fuente_boton = pygame.font.SysFont("Arial", 22, bold=True)

        self.confirmando_accion = None  # None, "REINICIAR" o "SALIR"
        self.mensaje_toast = ""

    def dibujar(self):
        ancho, alto = self.pantalla.get_size()

        # Capa translúcida sobre la pantalla de juego
        superficie_oscura = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        superficie_oscura.fill((10, 15, 25, 200))
        self.pantalla.blit(superficie_oscura, (0, 0))

        # Cuadro de Pausa central
        w_box, h_box = 450, 480
        rect_box = pygame.Rect((ancho - w_box) // 2, (alto - h_box) // 2, w_box, h_box)
        pygame.draw.rect(self.pantalla, (25, 35, 55), rect_box, border_radius=15)
        pygame.draw.rect(self.pantalla, (80, 110, 160), rect_box, width=3, border_radius=15)

        # Si hay una ventana de confirmación (Modal)
        if self.confirmando_accion:
            self._dibujar_confirmacion(rect_box)
            return

        # Título
        txt_tit = self.fuente_titulo.render("PARTIDA PAUSADA", True, (255, 255, 255))
        self.pantalla.blit(txt_tit, txt_tit.get_rect(center=(ancho // 2, rect_box.y + 50)))

        pos_y_base = rect_box.y + 110
        bw, bh = 320, 50
        bx = (ancho - bw) // 2

        self.btn_continuar = pygame.Rect(bx, pos_y_base, bw, bh)
        self.btn_reglas = pygame.Rect(bx, pos_y_base + 65, bw, bh)
        self.btn_reiniciar = pygame.Rect(bx, pos_y_base + 130, bw, bh)
        self.btn_guardar = pygame.Rect(bx, pos_y_base + 195, bw, bh)
        self.btn_menu = pygame.Rect(bx, pos_y_base + 260, bw, bh)

        pos_m = pygame.mouse.get_pos()
        self._dibujar_boton(self.btn_continuar, "CONTINUAR", (40, 180, 80), pos_m)
        self._dibujar_boton(self.btn_reglas, "REGLAS", (140, 80, 200), pos_m)
        self._dibujar_boton(self.btn_reiniciar, "REINICIAR PARTIDA", (220, 140, 40), pos_m)
        self._dibujar_boton(self.btn_guardar, "GUARDAR Y SALIR", (40, 120, 220), pos_m)
        self._dibujar_boton(self.btn_menu, "MENÚ PRINCIPAL", (200, 60, 60), pos_m)

        if self.mensaje_toast:
            txt_t = self.fuente_sub.render(self.mensaje_toast, True, (100, 255, 100))
            self.pantalla.blit(txt_t, txt_t.get_rect(center=(ancho // 2, rect_box.y + 440)))

    def _dibujar_confirmacion(self, rect_box):
        ancho, alto = self.pantalla.get_size()

        txt_pregunta = "¿Seguro que querés reiniciar?" if self.confirmando_accion == "REINICIAR" else "¿Seguro que querés salir?"
        txt_sub = "Se perderá el progreso actual no guardado."

        lbl1 = self.fuente_titulo.render(txt_pregunta, True, (255, 220, 40))
        lbl2 = self.fuente_sub.render(txt_sub, True, (220, 220, 220))

        self.pantalla.blit(lbl1, lbl1.get_rect(center=(ancho // 2, rect_box.y + 120)))
        self.pantalla.blit(lbl2, lbl2.get_rect(center=(ancho // 2, rect_box.y + 180)))

        bw, bh = 140, 50
        self.btn_conf_si = pygame.Rect(ancho // 2 - 160, rect_box.y + 280, bw, bh)
        self.btn_conf_no = pygame.Rect(ancho // 2 + 20, rect_box.y + 280, bw, bh)

        pos_m = pygame.mouse.get_pos()
        self._dibujar_boton(self.btn_conf_si, "CONFIRMAR", (200, 60, 60), pos_m)
        self._dibujar_boton(self.btn_conf_no, "CANCELAR", (80, 100, 130), pos_m)

    def _dibujar_boton(self, rect, texto, color_base, pos_mouse):
        hover = rect.collidepoint(pos_mouse)
        color = (min(color_base[0] + 30, 255), min(color_base[1] + 30, 255), min(color_base[2] + 30, 255)) if hover else color_base
        pygame.draw.rect(self.pantalla, color, rect, border_radius=10)
        pygame.draw.rect(self.pantalla, (255, 255, 255), rect, width=2, border_radius=10)
        txt = self.fuente_boton.render(texto, True, (255, 255, 255))
        self.pantalla.blit(txt, txt.get_rect(center=rect.center))

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos

            if self.confirmando_accion:
                if self.btn_conf_si.collidepoint(pos):
                    if self.confirmando_accion == "REINICIAR":
                        self.confirmando_accion = None
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

            elif self.btn_reiniciar.collidepoint(pos):
                self.confirmando_accion = "REINICIAR"

            elif self.btn_guardar.collidepoint(pos):
                if self.gestor.partidaActual:
                    exito, msg = self.persistencia.guardarPartida(self.gestor.partidaActual)
                    self.mensaje_toast = msg
                    if exito:
                        # Salir al menú principal después de guardar
                        self.gestor.estado = "MENU"

            elif self.btn_menu.collidepoint(pos):
                self.confirmando_accion = "SALIR"
