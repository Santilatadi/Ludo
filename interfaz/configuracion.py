"""
Modulo configuracion.py
Dibuja e interactúa con la Pantalla de Configuración de Nueva Partida (CU-01 a CU-05).
Permite seleccionar cantidad total de jugadores (2 a 4), alternar entre Jugador Humano y Bot (IA),
ingresar nombres y seleccionar colores únicos con una estética visual moderna.
"""

import pygame
from modelos.color import Color
from modelos.jugador import Jugador


class PantallaConfiguracion:

    def __init__(self, pantalla, gestor_partida):
        self.pantalla = pantalla
        self.gestor = gestor_partida
        self.fuente_titulo = pygame.font.SysFont("Arial", 40, bold=True)
        self.fuente_sub = pygame.font.SysFont("Arial", 20, bold=True)
        self.fuente_label = pygame.font.SysFont("Arial", 18)
        self.fuente_boton = pygame.font.SysFont("Arial", 20, bold=True)
        self.fuente_badge = pygame.font.SysFont("Arial", 14, bold=True)

        self.cant_jugadores = 2
        self.es_bot_lista = [False, True, True, True]  # Jugador 1 Humano por defecto, resto Bots
        self.nombres = ["Santiago", "Bot 1", "Bot 2", "Bot 3"]
        self.colores = [Color.ROJO, Color.AZUL, Color.VERDE, Color.AMARILLO]
        self.campo_activo = None
        self.mensaje_error = ""

    def dibujar(self):
        # Fondo degradado azul noche moderno
        self.pantalla.fill((15, 22, 38))
        ancho, alto = self.pantalla.get_size()

        # Encabezado
        txt_tit = self.fuente_titulo.render("CONFIGURACIÓN DE PARTIDA", True, (255, 255, 255))
        rect_tit = txt_tit.get_rect(center=(ancho // 2, 45))
        self.pantalla.blit(txt_tit, rect_tit)

        # 1. Selector de Cantidad de Jugadores
        txt_cant_lbl = self.fuente_sub.render("Cantidad Total de Jugadores:", True, (180, 210, 240))
        self.pantalla.blit(txt_cant_lbl, (ancho // 2 - 220, 95))

        self.btn_menos = pygame.Rect(ancho // 2 + 70, 90, 40, 40)
        self.btn_mas = pygame.Rect(ancho // 2 + 170, 90, 40, 40)

        pos_m = pygame.mouse.get_pos()
        self._dibujar_boton_peq(self.btn_menos, "-", (60, 80, 120), pos_m)
        self._dibujar_boton_peq(self.btn_mas, "+", (60, 80, 120), pos_m)

        txt_cant = self.fuente_titulo.render(str(self.cant_jugadores), True, (255, 215, 0))
        self.pantalla.blit(txt_cant, txt_cant.get_rect(center=(ancho // 2 + 135, 108)))

        # 2. Configuración por Jugador (Humano/Bot, Nombre y Color)
        pos_y_base = 160
        colores_lista = Color.obtener_todos()

        self.rects_nombres = []
        self.rects_colores = []
        self.rects_toggle_bot = []

        for i in range(self.cant_jugadores):
            pos_y = pos_y_base + i * 110

            # Tarjeta de jugador (Glassmorphism card)
            rect_card = pygame.Rect(80, pos_y, ancho - 160, 95)
            pygame.draw.rect(self.pantalla, (25, 36, 58), rect_card, border_radius=12)
            pygame.draw.rect(self.pantalla, (45, 65, 100), rect_card, width=2, border_radius=12)

            # Etiqueta
            lbl_j = self.fuente_sub.render(f"Jugador {i + 1}", True, (255, 255, 255))
            self.pantalla.blit(lbl_j, (105, pos_y + 15))

            # Botón Toggle Humano / Bot
            rect_toggle = pygame.Rect(205, pos_y + 12, 115, 32)
            self.rects_toggle_bot.append(rect_toggle)
            es_bot = self.es_bot_lista[i]
            color_toggle = (140, 60, 200) if es_bot else (40, 180, 90)
            texto_toggle = "🤖 BOT" if es_bot else "👤 HUMANO"

            pygame.draw.rect(self.pantalla, color_toggle, rect_toggle, border_radius=8)
            pygame.draw.rect(self.pantalla, (255, 255, 255), rect_toggle, width=1, border_radius=8)
            txt_t = self.fuente_badge.render(texto_toggle, True, (255, 255, 255))
            self.pantalla.blit(txt_t, txt_t.get_rect(center=rect_toggle.center))

            # Campo de entrada de Nombre
            rect_nombre = pygame.Rect(340, pos_y + 12, 220, 36)
            self.rects_nombres.append(rect_nombre)
            es_activo = (self.campo_activo == i)
            color_borde = (255, 215, 0) if es_activo else (80, 100, 140)

            pygame.draw.rect(self.pantalla, (18, 26, 42), rect_nombre, border_radius=6)
            pygame.draw.rect(self.pantalla, color_borde, rect_nombre, width=2, border_radius=6)

            txt_nom = self.fuente_label.render(self.nombres[i], True, (240, 240, 240))
            self.pantalla.blit(txt_nom, (rect_nombre.x + 10, rect_nombre.y + 7))

            # Selector de Color
            lbl_c = self.fuente_label.render("Color:", True, (180, 210, 240))
            self.pantalla.blit(lbl_c, (580, pos_y + 18))

            opciones_color_j = []
            for col_idx, col in enumerate(colores_lista):
                rect_col = pygame.Rect(640 + col_idx * 70, pos_y + 12, 60, 36)
                opciones_color_j.append((rect_col, col))
                es_sel = (self.colores[i] == col)

                color_rgb = col.obtener_rgb()
                pygame.draw.rect(self.pantalla, color_rgb, rect_col, border_radius=6)
                if es_sel:
                    pygame.draw.rect(self.pantalla, (255, 255, 255), rect_col, width=4, border_radius=6)
                else:
                    pygame.draw.rect(self.pantalla, (40, 40, 40), rect_col, width=1, border_radius=6)

            self.rects_colores.append(opciones_color_j)

        # Mensaje de Error
        if self.mensaje_error:
            txt_err = self.fuente_label.render(self.mensaje_error, True, (255, 100, 100))
            self.pantalla.blit(txt_err, txt_err.get_rect(center=(ancho // 2, alto - 105)))

        # Botones Inferiores: INICIAR y VOLVER
        self.btn_iniciar = pygame.Rect(ancho // 2 - 190, alto - 75, 180, 50)
        self.btn_volver = pygame.Rect(ancho // 2 + 10, alto - 75, 180, 50)

        self._dibujar_boton_principal(self.btn_iniciar, "INICIAR PARTIDA", (40, 180, 80), pos_m)
        self._dibujar_boton_principal(self.btn_volver, "VOLVER", (200, 60, 60), pos_m)

    def _dibujar_boton_peq(self, rect, texto, color_base, pos_mouse):
        hover = rect.collidepoint(pos_mouse)
        color = (min(color_base[0] + 30, 255), min(color_base[1] + 30, 255), min(color_base[2] + 30, 255)) if hover else color_base
        pygame.draw.rect(self.pantalla, color, rect, border_radius=8)
        pygame.draw.rect(self.pantalla, (255, 255, 255), rect, width=2, border_radius=8)
        txt = self.fuente_sub.render(texto, True, (255, 255, 255))
        self.pantalla.blit(txt, txt.get_rect(center=rect.center))

    def _dibujar_boton_principal(self, rect, texto, color_base, pos_mouse):
        hover = rect.collidepoint(pos_mouse)
        color = (min(color_base[0] + 30, 255), min(color_base[1] + 30, 255), min(color_base[2] + 30, 255)) if hover else color_base
        pygame.draw.rect(self.pantalla, color, rect, border_radius=10)
        pygame.draw.rect(self.pantalla, (255, 255, 255), rect, width=2, border_radius=10)
        txt = self.fuente_boton.render(texto, True, (255, 255, 255))
        self.pantalla.blit(txt, txt.get_rect(center=rect.center))

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos

            # Botones de cantidad de jugadores
            if self.btn_menos.collidepoint(pos):
                if self.cant_jugadores > 2:
                    self.cant_jugadores -= 1
                    self.mensaje_error = ""

            elif self.btn_mas.collidepoint(pos):
                if self.cant_jugadores < 4:
                    self.cant_jugadores += 1
                    self.mensaje_error = ""

            # Clic en botones Toggle Humano / Bot
            for i, rect_t in enumerate(self.rects_toggle_bot):
                if rect_t.collidepoint(pos):
                    self.es_bot_lista[i] = not self.es_bot_lista[i]
                    if self.es_bot_lista[i]:
                        self.nombres[i] = f"Bot {i + 1}"
                    else:
                        if self.nombres[i].startswith("Bot"):
                            self.nombres[i] = f"Jugador {i + 1}"
                    self.mensaje_error = ""

            # Clic en entrada de texto
            self.campo_activo = None
            for idx, r_nom in enumerate(self.rects_nombres):
                if r_nom.collidepoint(pos):
                    self.campo_activo = idx
                    break

            # Clic en selector de color
            for i, opciones in enumerate(self.rects_colores):
                for rect_c, col in opciones:
                    if rect_c.collidepoint(pos):
                        self.colores[i] = col
                        self.mensaje_error = ""

            # Botón Iniciar
            if self.btn_iniciar.collidepoint(pos):
                if self._validar_configuracion():
                    self._crear_y_comenzar_partida()

            # Botón Volver
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

        # Validar nombres vacíos
        for i, nom in enumerate(nombres_activos):
            if not nom:
                self.mensaje_error = f"El nombre del Jugador {i + 1} no puede estar vacío."
                return False

        # Validar nombres repetidos
        if len(nombres_activos) != len(set(nombres_activos)):
            self.mensaje_error = "No se permiten nombres repetidos entre los jugadores."
            return False

        # Validar colores repetidos
        colores_activos = [self.colores[i] for i in range(self.cant_jugadores)]
        if len(colores_activos) != len(set(colores_activos)):
            self.mensaje_error = "Cada jugador debe tener un color diferente. Cambia los colores repetidos."
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
