"""
Modulo configuracion.py
Dibuja e interactúa con la Pantalla de Configuración de Nueva Partida.
Adaptado 100% al diseño exacto de Figma.
"""

import os
import sys

directorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if directorio_raiz not in sys.path:
    sys.path.insert(0, directorio_raiz)

import pygame
from modelos.color import Color
from modelos.jugador import Jugador


class PantallaConfiguracion:

    def __init__(self, pantalla, gestor_partida):
        self.pantalla = pantalla
        self.gestor = gestor_partida

        ruta_fuente = "assets/font.ttf"
        if os.path.exists(ruta_fuente):
            self.fuente_titulo = pygame.font.Font(ruta_fuente, 42)
            self.fuente_sub = pygame.font.Font(ruta_fuente, 20)
            self.fuente_label = pygame.font.Font(ruta_fuente, 18)
            self.fuente_boton = pygame.font.Font(ruta_fuente, 26)
            self.fuente_pill = pygame.font.Font(ruta_fuente, 16)
        else:
            self.fuente_titulo = pygame.font.SysFont("Impact", 40, bold=True)
            self.fuente_sub = pygame.font.SysFont("Arial", 20, bold=True)
            self.fuente_label = pygame.font.SysFont("Arial", 18, bold=True)
            self.fuente_boton = pygame.font.SysFont("Arial", 24, bold=True)
            self.fuente_pill = pygame.font.SysFont("Arial", 16, bold=True)

        self.cant_jugadores = 2
        self.es_bot_lista = [False, True, True, True]
        self.nombres = ["Jugador 1", "Jugador 2", "Jugador 3", "Jugador 4"]
        self.colores = [Color.ROJO, Color.AZUL, Color.VERDE, Color.AMARILLO]
        self.campo_activo = None
        self.mensaje_error = ""

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
        # Canvas Rosa / Magenta
        self.pantalla.fill((226, 120, 190))

        # Ventana modal azul con borde rojo brillante
        w_win, h_win = min(680, ancho - 60), min(520, alto - 60)
        rect_win = pygame.Rect((ancho - w_win) // 2, (alto - h_win) // 2, w_win, h_win)

        pygame.draw.rect(self.pantalla, (16, 56, 168), rect_win, border_radius=10)
        pygame.draw.rect(self.pantalla, (220, 20, 60), rect_win, width=4, border_radius=10)

        # Encabezado "NUEVA PARTIDA"
        txt_tit = self._render_texto_delineado("NUEVA PARTIDA", self.fuente_titulo, (255, 255, 255), (0, 0, 0), 3)
        rect_tit = txt_tit.get_rect(center=(ancho // 2, rect_win.y + 45))
        self.pantalla.blit(txt_tit, rect_tit)

        # Doble subrayado debajo del título
        y_line = rect_tit.bottom - 4
        pygame.draw.line(self.pantalla, (255, 255, 255), (rect_tit.x + 10, y_line), (rect_tit.right - 10, y_line), 2)
        pygame.draw.line(self.pantalla, (255, 255, 255), (rect_tit.x + 10, y_line + 4), (rect_tit.right - 10, y_line + 4), 2)

        pos_m = pygame.mouse.get_pos()

        # 1. Cantidad Jugadores (izquierda)
        txt_c1 = self._render_texto_delineado("Cantidad", self.fuente_sub, (255, 255, 255), (0, 0, 0), 2)
        txt_c2 = self._render_texto_delineado("Jugadores", self.fuente_sub, (255, 255, 255), (0, 0, 0), 2)
        self.pantalla.blit(txt_c1, (rect_win.x + 45, rect_win.y + 105))
        self.pantalla.blit(txt_c2, (rect_win.x + 45, rect_win.y + 128))

        # Botón - (Rojo)
        self.btn_menos = pygame.Rect(rect_win.x + 215, rect_win.y + 122, 22, 22)
        pygame.draw.rect(self.pantalla, (220, 30, 40), self.btn_menos)
        txt_m = self._render_texto_delineado("-", self.fuente_sub, (255, 255, 255), (0, 0, 0), 2)
        self.pantalla.blit(txt_m, txt_m.get_rect(center=self.btn_menos.center))

        # Círculo central rojo con la cantidad
        rect_circ_cant = pygame.Rect(rect_win.x + 250, rect_win.y + 105, 52, 52)
        pygame.draw.circle(self.pantalla, (220, 30, 40), rect_circ_cant.center, 26)
        pygame.draw.circle(self.pantalla, (20, 20, 20), rect_circ_cant.center, 26, width=2)
        txt_c = self._render_texto_delineado(str(self.cant_jugadores), self.fuente_titulo, (255, 255, 255), (0, 0, 0), 3)
        self.pantalla.blit(txt_c, txt_c.get_rect(center=rect_circ_cant.center))

        # Botón + (Rojo)
        self.btn_mas = pygame.Rect(rect_win.x + 315, rect_win.y + 122, 22, 22)
        pygame.draw.rect(self.pantalla, (220, 30, 40), self.btn_mas)
        txt_p = self._render_texto_delineado("+", self.fuente_sub, (255, 255, 255), (0, 0, 0), 2)
        self.pantalla.blit(txt_p, txt_p.get_rect(center=self.btn_mas.center))

        # 2. Jugadores (Etiqueta + 4 Píldoras en cuadrícula 2x2)
        txt_j_lbl = self._render_texto_delineado("Jugadores", self.fuente_sub, (255, 255, 255), (0, 0, 0), 2)
        self.pantalla.blit(txt_j_lbl, (rect_win.x + 45, rect_win.y + 185))

        self.rects_nombres = []
        self.rects_arrow_left = []
        self.rects_arrow_right = []

        # Bordes coloridos de cada entrada según Figma:
        # P1: Rojo (#FF0000), P2: Verde (#00C853), P3: Azul (#0091EA), P4: Amarillo (#FFD600)
        colores_borde_pildoras = [(255, 0, 0), (0, 200, 83), (0, 145, 234), (255, 214, 0)]

        w_pill, h_pill = 220, 38
        offsets_grid = [
            (rect_win.x + 80, rect_win.y + 225),   # Top Left (P1)
            (rect_win.x + 360, rect_win.y + 225),  # Top Right (P2)
            (rect_win.x + 80, rect_win.y + 285),   # Bottom Left (P3)
            (rect_win.x + 360, rect_win.y + 285)   # Bottom Right (P4)
        ]

        for i in range(4):
            if i >= self.cant_jugadores:
                # Ocultar o deshabilitar jugadores que excedan la cantidad seleccionada
                continue

            rx, py = offsets_grid[i]
            rect_pill = pygame.Rect(rx, py, w_pill, h_pill)
            self.rects_nombres.append(rect_pill)

            # Fondo blanco de píldora
            pygame.draw.rect(self.pantalla, (255, 255, 255), rect_pill, border_radius=19)

            # Borde colorido especifico de cada jugador
            col_borde = colores_borde_pildoras[i]
            pygame.draw.rect(self.pantalla, col_borde, rect_pill, width=3, border_radius=19)

            # Flecha izquierda
            r_left = pygame.Rect(rx - 22, py + 8, 20, 22)
            self.rects_arrow_left.append(r_left)
            pygame.draw.polygon(self.pantalla, (200, 200, 200), [(r_left.right, r_left.y), (r_left.x, r_left.centery), (r_left.right, r_left.bottom)])
            pygame.draw.polygon(self.pantalla, (20, 20, 20), [(r_left.right, r_left.y), (r_left.x, r_left.centery), (r_left.right, r_left.bottom)], width=2)

            # Flecha derecha
            r_right = pygame.Rect(rx + w_pill + 2, py + 8, 20, 22)
            self.rects_arrow_right.append(r_right)
            pygame.draw.polygon(self.pantalla, (200, 200, 200), [(r_right.x, r_right.y), (r_right.right, r_right.centery), (r_right.x, r_right.bottom)])
            pygame.draw.polygon(self.pantalla, (20, 20, 20), [(r_right.x, r_right.y), (r_right.right, r_right.centery), (r_right.x, r_right.bottom)], width=2)

            # Nombre dentro de la píldora
            nom_str = self.nombres[i]
            if self.es_bot_lista[i]:
                nom_str += " (Bot)"

            txt_nom = self.fuente_pill.render(nom_str, True, (20, 20, 20))
            self.pantalla.blit(txt_nom, txt_nom.get_rect(center=rect_pill.center))

        # Mensaje de Error
        if self.mensaje_error:
            txt_err = self.fuente_label.render(self.mensaje_error, True, (255, 100, 100))
            self.pantalla.blit(txt_err, txt_err.get_rect(center=(ancho // 2, rect_win.bottom - 95)))

        # Botón INICIAR (Rojo con borde Amarillo como Figma)
        bw_btn, bh_btn = 220, 54
        self.btn_iniciar = pygame.Rect((ancho - bw_btn) // 2, rect_win.bottom - 75, bw_btn, bh_btn)

        hover = self.btn_iniciar.collidepoint(pos_m)
        color_btn = (245, 40, 40) if hover else (225, 30, 30)

        pygame.draw.rect(self.pantalla, color_btn, self.btn_iniciar, border_radius=6)
        pygame.draw.rect(self.pantalla, (255, 230, 0), self.btn_iniciar, width=4, border_radius=6)

        txt_ini = self._render_texto_delineado("INICIAR", self.fuente_boton, (255, 255, 255), (0, 0, 0), 3)
        self.pantalla.blit(txt_ini, txt_ini.get_rect(center=self.btn_iniciar.center))

        # Botón Volver (X)
        self.btn_volver = pygame.Rect(rect_win.x + 15, rect_win.y + 15, 32, 32)
        pygame.draw.rect(self.pantalla, (220, 30, 40), self.btn_volver, border_radius=4)
        txt_v = self._render_texto_delineado("X", self.fuente_sub, (255, 255, 255), (0, 0, 0), 2)
        self.pantalla.blit(txt_v, txt_v.get_rect(center=self.btn_volver.center))

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos

            if self.btn_menos.collidepoint(pos):
                if self.cant_jugadores > 2:
                    self.cant_jugadores -= 1
                    self.mensaje_error = ""

            elif self.btn_mas.collidepoint(pos):
                if self.cant_jugadores < 4:
                    self.cant_jugadores += 1
                    self.mensaje_error = ""

            # Clic en flechas de píldoras
            for i, r_l in enumerate(self.rects_arrow_left):
                if r_l.collidepoint(pos):
                    self.es_bot_lista[i] = not self.es_bot_lista[i]
                    if self.es_bot_lista[i]:
                        self.nombres[i] = f"Bot {i + 1}"
                    else:
                        if self.nombres[i].startswith("Bot"):
                            self.nombres[i] = f"Jugador {i + 1}"
                    self.mensaje_error = ""

            for i, r_r in enumerate(self.rects_arrow_right):
                if r_r.collidepoint(pos):
                    self.es_bot_lista[i] = not self.es_bot_lista[i]
                    if self.es_bot_lista[i]:
                        self.nombres[i] = f"Bot {i + 1}"
                    else:
                        if self.nombres[i].startswith("Bot"):
                            self.nombres[i] = f"Jugador {i + 1}"
                    self.mensaje_error = ""

            self.campo_activo = None
            for idx, r_nom in enumerate(self.rects_nombres):
                if r_nom.collidepoint(pos):
                    self.campo_activo = idx
                    break

            if self.btn_iniciar.collidepoint(pos):
                if self._validar_configuracion():
                    self._crear_y_comenzar_partida()

            elif self.btn_volver.collidepoint(pos):
                self.gestor.estado = "MENU"

        elif evento.type == pygame.KEYDOWN and self.campo_activo is not None:
            idx = self.campo_activo
            if evento.key == pygame.K_BACKSPACE:
                self.nombres[idx] = self.nombres[idx][:-1]
            elif evento.key in (pygame.K_RETURN, pygame.K_TAB):
                self.campo_activo = None
            else:
                if len(self.nombres[idx]) < 12 and evento.unicode.isprintable():
                    self.nombres[idx] += evento.unicode

    def _validar_configuracion(self) -> bool:
        nombres_activos = [self.nombres[i].strip() for i in range(self.cant_jugadores)]
        for i, nom in enumerate(nombres_activos):
            if not nom:
                self.mensaje_error = f"El nombre del Jugador {i + 1} no puede estar vacío."
                return False

        if len(nombres_activos) != len(set(nombres_activos)):
            self.mensaje_error = "No se permiten nombres repetidos."
            return False

        self.mensaje_error = ""
        return True

    def _crear_y_comenzar_partida(self):
        partida = self.gestor.partidaActual
        if not partida:
            from modelos.partida import Partida
            partida = Partida()
            self.gestor.partidaActual = partida

        partida.configurarCantidadJugadores(self.cant_jugadores)
        partida.jugadores = []

        for i in range(self.cant_jugadores):
            jugador = Jugador(
                nombre=self.nombres[i].strip(),
                color=self.colores[i],
                es_bot=self.es_bot_lista[i]
            )
            partida.jugadores.append(jugador)

        self.gestor.iniciarPartida()
