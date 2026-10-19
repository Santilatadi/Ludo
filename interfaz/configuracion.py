"""
Modulo configuracion.py
Dibuja e interactúa con la Pantalla de Configuración de Nueva Partida.
Adaptado con tarjetas visuales glassmorphism, avatar de bots/jugadores y botones sonoros interactivos.
"""

import os
import sys
import pygame

directorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if directorio_raiz not in sys.path:
    sys.path.insert(0, directorio_raiz)

from modelos.color import Color
from modelos.jugador import Jugador
from interfaz.efectos import SistemaParticulas, dibujar_panel_glassmorphism, dibujar_texto_glow
from interfaz.componentes import BotonModerno, BotonMute


class PantallaConfiguracion:

    def __init__(self, pantalla, gestor_partida):
        self.pantalla = pantalla
        self.gestor = gestor_partida

        ruta_fuente = "assets/font.ttf"
        if os.path.exists(ruta_fuente):
            self.fuente_titulo = pygame.font.Font(ruta_fuente, 42)
            self.fuente_sub = pygame.font.Font(ruta_fuente, 20)
            self.fuente_label = pygame.font.Font(ruta_fuente, 18)
            self.fuente_boton = pygame.font.Font(ruta_fuente, 24)
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

        self.btn_mute = BotonMute(10, 10)
        self.ticks = 0

    def dibujar(self):
        self.ticks += 1
        ancho, alto = self.pantalla.get_size()

        # Canvas de fondo violeta según diseño en Figma
        self.pantalla.fill((46, 21, 90))

        # Ventana modal Glassmorphism azul marino con borde dorado resplandeciente
        w_win, h_win = min(720, ancho - 40), min(540, alto - 40)
        rect_win = pygame.Rect((ancho - w_win) // 2, (alto - h_win) // 2, w_win, h_win)

        dibujar_panel_glassmorphism(
            self.pantalla, rect_win,
            color_bg=(16, 35, 95, 230),
            color_borde=(255, 215, 0, 220),
            radio=20, grosor_borde=3
        )

        # Encabezado "NUEVA PARTIDA"
        dibujar_texto_glow(
            self.pantalla, "NUEVA PARTIDA", self.fuente_titulo,
            ancho // 2, rect_win.y + 40,
            color_texto=(255, 255, 255), color_resplandor=(255, 215, 0), centro=True
        )

        # 1. Selector de Cantidad de Jugadores
        txt_c1 = self.fuente_sub.render("Cantidad de Jugadores:", True, (220, 240, 255))
        self.pantalla.blit(txt_c1, (rect_win.x + 45, rect_win.y + 95))

        # Botón -
        self.btn_menos_inst = BotonModerno(
            (rect_win.x + 310, rect_win.y + 88, 36, 36), "-",
            color_base=(220, 40, 50), color_hover=(250, 60, 70),
            fuente=self.fuente_sub
        )
        self.btn_menos_inst.dibujar(self.pantalla)

        # Círculo central indicador de cantidad
        rect_circ_cant = pygame.Rect(rect_win.x + 360, rect_win.y + 82, 48, 48)
        pygame.draw.circle(self.pantalla, (255, 215, 0), rect_circ_cant.center, 24)
        pygame.draw.circle(self.pantalla, (20, 20, 20), rect_circ_cant.center, 24, width=2)
        txt_c = self.fuente_sub.render(str(self.cant_jugadores), True, (20, 20, 20))
        self.pantalla.blit(txt_c, txt_c.get_rect(center=rect_circ_cant.center))

        # Botón +
        self.btn_mas_inst = BotonModerno(
            (rect_win.x + 420, rect_win.y + 88, 36, 36), "+",
            color_base=(220, 40, 50), color_hover=(250, 60, 70),
            fuente=self.fuente_sub
        )
        self.btn_mas_inst.dibujar(self.pantalla)

        # 2. Configuración de Jugadores (Cuadrícula 2x2 de Píldoras/Tarjetas)
        self.rects_nombres = []
        self.rects_arrow_left = []
        self.rects_arrow_right = []

        colores_borde_pildoras = [(255, 60, 60), (40, 220, 100), (40, 160, 255), (255, 215, 0)]
        colores_fondo_badge = [(100, 20, 20), (20, 80, 40), (20, 50, 100), (100, 85, 20)]

        w_pill, h_pill = 240, 52
        offsets_grid = [
            (rect_win.x + 80, rect_win.y + 165),   # P1 Top Left
            (rect_win.x + 380, rect_win.y + 165),  # P2 Top Right
            (rect_win.x + 80, rect_win.y + 245),   # P3 Bottom Left
            (rect_win.x + 380, rect_win.y + 245)   # P4 Bottom Right
        ]

        pos_m = pygame.mouse.get_pos()

        for i in range(4):
            if i >= self.cant_jugadores:
                continue

            rx, py = offsets_grid[i]
            rect_pill = pygame.Rect(rx, py, w_pill, h_pill)
            self.rects_nombres.append(rect_pill)

            col_borde = colores_borde_pildoras[i]
            col_bg_badge = colores_fondo_badge[i]

            # Tarjeta Glassmorphism
            dibujar_panel_glassmorphism(
                self.pantalla, rect_pill,
                color_bg=(col_bg_badge[0], col_bg_badge[1], col_bg_badge[2], 210),
                color_borde=col_borde, radio=14
            )

            # Flecha izquierda
            r_left = pygame.Rect(rx - 28, py + 12, 24, 28)
            self.rects_arrow_left.append(r_left)
            col_fl = (255, 215, 0) if r_left.collidepoint(pos_m) else (200, 200, 200)
            pygame.draw.polygon(self.pantalla, col_fl, [(r_left.right, r_left.y), (r_left.x, r_left.centery), (r_left.right, r_left.bottom)])

            # Flecha derecha
            r_right = pygame.Rect(rx + w_pill + 4, py + 12, 24, 28)
            self.rects_arrow_right.append(r_right)
            col_fr = (255, 215, 0) if r_right.collidepoint(pos_m) else (200, 200, 200)
            pygame.draw.polygon(self.pantalla, col_fr, [(r_right.x, r_right.y), (r_right.right, r_right.centery), (r_right.x, r_right.bottom)])

            # Icono Avatar (Robot vs Persona)
            icono_tipo = "🤖" if self.es_bot_lista[i] else "👤"
            txt_ico = self.fuente_sub.render(icono_tipo, True, (255, 255, 255))
            self.pantalla.blit(txt_ico, (rx + 12, py + 14))

            # Nombre dentro de la tarjeta
            nom_str = self.nombres[i]
            if self.es_bot_lista[i]:
                nom_str += " (Bot)"

            # Si el campo está activo para escribir, mostrar indicador |
            if self.campo_activo == i:
                nom_str += "|"

            txt_nom = self.fuente_pill.render(nom_str, True, (255, 255, 255))
            self.pantalla.blit(txt_nom, (rx + 48, py + 16))

        # Mensaje de Error
        if self.mensaje_error:
            dibujar_texto_glow(
                self.pantalla, self.mensaje_error, self.fuente_label,
                ancho // 2, rect_win.bottom - 105,
                color_texto=(255, 100, 100), color_resplandor=(255, 0, 0), centro=True
            )

        # Botón INICIAR
        bw_btn, bh_btn = 220, 52
        self.btn_iniciar_inst = BotonModerno(
            ((ancho - bw_btn) // 2, rect_win.bottom - 75, bw_btn, bh_btn),
            "INICIAR",
            color_base=(220, 30, 40), color_hover=(250, 50, 60),
            color_borde=(255, 230, 0), fuente=self.fuente_boton, icono="⚔️"
        )
        self.btn_iniciar_inst.dibujar(self.pantalla)

        # Botón Volver (X)
        self.btn_volver_inst = BotonModerno(
            (rect_win.x + 15, rect_win.y + 15, 36, 36), "X",
            color_base=(200, 40, 50), fuente=self.fuente_sub
        )
        self.btn_volver_inst.dibujar(self.pantalla)

    def manejar_evento(self, evento):

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos

            if hasattr(self, 'btn_menos_inst') and self.btn_menos_inst.es_cliqueado(evento):
                if self.cant_jugadores > 2:
                    self.cant_jugadores -= 1
                    self.mensaje_error = ""

            elif hasattr(self, 'btn_mas_inst') and self.btn_mas_inst.es_cliqueado(evento):
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

            if hasattr(self, 'btn_iniciar_inst') and self.btn_iniciar_inst.es_cliqueado(evento):
                if self._validar_configuracion():
                    self._crear_y_comenzar_partida()

            elif hasattr(self, 'btn_volver_inst') and self.btn_volver_inst.es_cliqueado(evento):
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
            nom = self.nombres[i].strip()
            if self.es_bot_lista[i] and "Bot" not in nom:
                nom = f"Bot {nom}"
            jugador = Jugador(
                nombre=nom,
                color=self.colores[i]
            )
            partida.jugadores.append(jugador)

        self.gestor.iniciarPartida()
