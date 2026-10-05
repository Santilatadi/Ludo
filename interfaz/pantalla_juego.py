"""
Modulo pantalla_juego.py
Dibuja e interactúa con la Pantalla Principal del Juego de Ludo.
Adaptado 100% al diseño visual exacto de Figma.
"""

import os
import math
import random
import pygame
from modelos.color import Color


class PantallaJuego:

    def __init__(self, pantalla, gestor_partida, interfaz_padre=None):
        self.pantalla = pantalla
        self.gestor = gestor_partida
        self.interfaz_padre = interfaz_padre

        ruta_fuente = "assets/font.ttf"
        if os.path.exists(ruta_fuente):
            self.fuente_titulo = pygame.font.Font(ruta_fuente, 24)
            self.fuente_sub = pygame.font.Font(ruta_fuente, 18)
            self.fuente_tag = pygame.font.Font(ruta_fuente, 16)
            self.fuente_msg = pygame.font.Font(ruta_fuente, 18)
            self.fuente_dado = pygame.font.Font(ruta_fuente, 42)
        else:
            self.fuente_titulo = pygame.font.SysFont("Impact", 24, bold=True)
            self.fuente_sub = pygame.font.SysFont("Arial", 18, bold=True)
            self.fuente_tag = pygame.font.SysFont("Arial", 16, bold=True)
            self.fuente_msg = pygame.font.SysFont("Arial", 18, bold=True)
            self.fuente_dado = pygame.font.SysFont("Arial", 42, bold=True)

        self.GRID_CIRCUITO_52 = [
            (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (5, 6), (4, 6), (3, 6), (2, 6), (1, 6), (0, 6), (0, 7), (0, 8),
            (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 9), (6, 10), (6, 11), (6, 12), (6, 13), (6, 14), (7, 14), (8, 14),
            (8, 13), (8, 12), (8, 11), (8, 10), (8, 9), (9, 8), (10, 8), (11, 8), (12, 8), (13, 8), (14, 8), (14, 7), (14, 6),
            (13, 6), (12, 6), (11, 6), (10, 6), (9, 6), (8, 5), (8, 4), (8, 3), (8, 2), (8, 1), (8, 0), (7, 0), (6, 0)
        ]

        self.GRID_META_ROJO = [(7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6)]
        self.GRID_META_VERDE = [(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7)]
        self.GRID_META_AMARILLO = [(7, 13), (7, 12), (7, 11), (7, 10), (7, 9), (7, 8)]
        self.GRID_META_AZUL = [(13, 7), (12, 7), (11, 7), (10, 7), (9, 7), (8, 7)]

        self.GRID_BASE = {
            Color.ROJO: [(1.5, 1.5), (1.5, 3.5), (3.5, 1.5), (3.5, 3.5)],
            Color.VERDE: [(1.5, 10.5), (1.5, 12.5), (3.5, 10.5), (3.5, 12.5)],
            Color.AMARILLO: [(10.5, 10.5), (10.5, 12.5), (12.5, 10.5), (12.5, 12.5)],
            Color.AZUL: [(10.5, 1.5), (10.5, 3.5), (12.5, 1.5), (12.5, 3.5)]
        }

        self.animando_dado = False
        self.frames_anim_dado = 0
        self.dado_visual_temp = 1
        self.posiciones_fichas_anim = {}
        self.colas_anim_pasos = {}
        self.ticks_glow = 0
        self.timer_bot = 0

    def _render_texto_delineado(self, texto, fuente, color_texto, color_borde=(0, 0, 0), grosor=3):
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

    def _calcular_geometria(self):
        ancho, alto = self.pantalla.get_size()
        ancho_panel = 280
        espacio_libre_ancho = ancho - ancho_panel - 60
        espacio_libre_alto = alto - 60

        tam_tablero = min(espacio_libre_ancho, espacio_libre_alto)
        tam_tablero = max(tam_tablero, 420)

        self.tam_celda = tam_tablero / 15.0
        self.ancho_tablero = self.tam_celda * 15
        self.alto_tablero = self.tam_celda * 15

        self.origen_x = (espacio_libre_ancho - self.ancho_tablero) // 2 + 30
        self.origen_y = (alto - self.alto_tablero) // 2

        self.pos_panel_x = self.origen_x + int(self.ancho_tablero) + 25
        self.pos_panel_y = self.origen_y
        self.ancho_panel = 250
        self.alto_panel = int(self.alto_tablero)

    def dibujar(self):
        self.ticks_glow += 1
        self._calcular_geometria()
        # Canvas Rosa / Magenta
        self.pantalla.fill((226, 120, 190))

        self._actualizar_turno_bot()
        self._dibujar_tablero_ludo()
        self._dibujar_etiquetas_jugadores()
        self._dibujar_dados_indicadores_jugadores()
        self._dibujar_fichas()
        self._dibujar_panel_derecho()

    def _actualizar_turno_bot(self):
        partida = self.gestor.partidaActual
        if not partida or partida.estado != "EN_CURSO":
            return

        if any(len(cola) > 0 for cola in self.colas_anim_pasos.values()):
            return

        jugador_act = partida.obtenerJugadorActual()
        if not jugador_act or not jugador_act.es_bot:
            self.timer_bot = 0
            return

        self.timer_bot += 1

        if not partida.dado_lanzado and not self.animando_dado:
            if self.timer_bot >= 25:
                self.animando_dado = True
                self.frames_anim_dado = 10
                self.timer_bot = 0

        elif partida.esperando_movimiento and not self.animando_dado:
            if self.timer_bot >= 35:
                movimientos_validos = partida.obtenerMovimientosValidos()
                if movimientos_validos:
                    ficha_elegida = jugador_act.seleccionar_mejor_movimiento(movimientos_validos, partida.tablero)
                    if ficha_elegida:
                        pos_ant = ficha_elegida.posicion
                        self.gestor.seleccionarFicha(ficha_elegida)
                        pos_nue = ficha_elegida.posicion
                        self._generar_pasos_animacion(ficha_elegida, pos_ant, pos_nue)

                        if partida.estado == "FINALIZADA":
                            self.gestor.estado = "FINAL"
                self.timer_bot = 0

    def _generar_pasos_animacion(self, ficha, pos_inicio, pos_fin):
        if pos_inicio == pos_fin:
            return

        pasos_coords = []
        if pos_inicio == 0:
            px, py = self._obtener_px_posicion(ficha, 1)
            pasos_coords.append((px, py))
        else:
            for p in range(pos_inicio + 1, pos_fin + 1):
                px, py = self._obtener_px_posicion(ficha, p)
                pasos_coords.append((px, py))

        self.colas_anim_pasos[ficha] = pasos_coords

    def _dibujar_tablero_ludo(self):
        ox, oy = self.origen_x, self.origen_y
        cs = self.tam_celda

        rect_tablero = pygame.Rect(ox, oy, self.ancho_tablero, self.alto_tablero)
        pygame.draw.rect(self.pantalla, (255, 255, 255), rect_tablero)

        # 4 Bases en esquinas
        self._dibujar_base(ox, oy, Color.ROJO, (0, 0))
        self._dibujar_base(ox, oy, Color.VERDE, (0, 9))
        self._dibujar_base(ox, oy, Color.AZUL, (9, 0))
        self._dibujar_base(ox, oy, Color.AMARILLO, (9, 9))

        # Caminitos a la meta
        for r, c in self.GRID_META_ROJO:
            pygame.draw.rect(self.pantalla, Color.ROJO.obtener_rgb(), (ox + c * cs, oy + r * cs, cs, cs))
        for r, c in self.GRID_META_VERDE:
            pygame.draw.rect(self.pantalla, Color.VERDE.obtener_rgb(), (ox + c * cs, oy + r * cs, cs, cs))
        for r, c in self.GRID_META_AZUL:
            pygame.draw.rect(self.pantalla, Color.AZUL.obtener_rgb(), (ox + c * cs, oy + r * cs, cs, cs))
        for r, c in self.GRID_META_AMARILLO:
            pygame.draw.rect(self.pantalla, Color.AMARILLO.obtener_rgb(), (ox + c * cs, oy + r * cs, cs, cs))

        # Casillas de salida
        colores_salida = [
            (6, 1, Color.ROJO), (1, 8, Color.VERDE), (13, 6, Color.AZUL), (8, 13, Color.AMARILLO)
        ]
        for r, c, col in colores_salida:
            pygame.draw.rect(self.pantalla, col.obtener_rgb(), (ox + c * cs, oy + r * cs, cs, cs))

        # Estrellas en casillas seguras
        casillas_estrella = [
            ((6, 1), Color.ROJO), ((1, 8), Color.VERDE), ((13, 6), Color.AZUL), ((8, 13), Color.AMARILLO),
            ((2, 6), (150, 150, 150)), ((6, 12), (150, 150, 150)), ((12, 8), (150, 150, 150)), ((8, 2), (150, 150, 150))
        ]
        for (r, c), col in casillas_estrella:
            color_rgb = col.obtener_rgb() if isinstance(col, Color) else col
            self._dibujar_estrella(ox + c * cs + cs // 2, oy + r * cs + cs // 2, cs * 0.32, color_rgb)

        # Rejilla del circuito con líneas negras delgadas
        for i in range(16):
            pygame.draw.line(self.pantalla, (20, 20, 20), (ox, oy + i * cs), (ox + self.ancho_tablero, oy + i * cs), 1)
            pygame.draw.line(self.pantalla, (20, 20, 20), (ox + i * cs, oy), (ox + i * cs, oy + self.alto_tablero), 1)

        # Centro (Meta Triángulos)
        cx, cy = ox + 6 * cs, oy + 6 * cs
        cz = 3 * cs
        rect_meta = pygame.Rect(cx, cy, cz, cz)
        pygame.draw.rect(self.pantalla, (255, 255, 255), rect_meta)

        center_pt = (cx + cz // 2, cy + cz // 2)
        pygame.draw.polygon(self.pantalla, Color.ROJO.obtener_rgb(), [(cx, cy), (cx, cy + cz), center_pt])
        pygame.draw.polygon(self.pantalla, Color.VERDE.obtener_rgb(), [(cx, cy), (cx + cz, cy), center_pt])
        pygame.draw.polygon(self.pantalla, Color.AMARILLO.obtener_rgb(), [(cx + cz, cy), (cx + cz, cy + cz), center_pt])
        pygame.draw.polygon(self.pantalla, Color.AZUL.obtener_rgb(), [(cx, cy + cz), (cx + cz, cy + cz), center_pt])

        # Borde negro grueso alrededor del tablero
        pygame.draw.rect(self.pantalla, (20, 20, 20), rect_tablero, width=4)

    def _dibujar_base(self, ox, oy, color, offset_grid):
        cs = self.tam_celda
        r_off, c_off = offset_grid
        rect = pygame.Rect(ox + c_off * cs, oy + r_off * cs, 6 * cs, 6 * cs)
        pygame.draw.rect(self.pantalla, color.obtener_rgb(), rect)
        pygame.draw.rect(self.pantalla, (20, 20, 20), rect, width=2)

        # Región interna blanca
        rect_inner = rect.inflate(-cs * 0.8, -cs * 0.8)
        pygame.draw.rect(self.pantalla, (255, 255, 255), rect_inner, border_radius=int(cs * 0.4))
        pygame.draw.rect(self.pantalla, (20, 20, 20), rect_inner, width=2, border_radius=int(cs * 0.4))

        # 4 Círculos blancos ovalados verticales para las fichas de la base
        spots = [(1.5, 1.5), (1.5, 3.5), (3.5, 1.5), (3.5, 3.5)]
        for sr, sc in spots:
            c_x = ox + (c_off + sc) * cs
            c_y = oy + (r_off + sr) * cs
            r_outer = cs * 0.65
            pygame.draw.ellipse(self.pantalla, color.obtener_rgb(), (c_x - r_outer * 0.6, c_y - r_outer * 0.8, r_outer * 1.2, r_outer * 1.6))
            pygame.draw.ellipse(self.pantalla, (20, 20, 20), (c_x - r_outer * 0.6, c_y - r_outer * 0.8, r_outer * 1.2, r_outer * 1.6), width=2)

    def _dibujar_estrella(self, cx, cy, radio, color):
        puntos = []
        for i in range(10):
            r = radio if i % 2 == 0 else radio / 2.2
            angulo = i * math.pi / 5 - math.pi / 2
            puntos.append((cx + r * math.cos(angulo), cy + r * math.sin(angulo)))
        pygame.draw.polygon(self.pantalla, color, puntos)
        pygame.draw.polygon(self.pantalla, (20, 20, 20), puntos, width=1)

    def _dibujar_etiquetas_jugadores(self):
        partida = self.gestor.partidaActual
        if not partida:
            return

        ox, oy = self.origen_x, self.origen_y
        cs = self.tam_celda

        # Ajuste exacto de colores de bordes y fondos de etiquetas según Figma:
        # P1: Fondo Amarillo (#FFEB3B), Borde Rojo (#FF0000)
        # P2: Fondo Blanco, Borde Verde (#00C853)
        # P3: Fondo Blanco, Borde Azul (#0091EA)
        # P4: Fondo Blanco, Borde Amarillo (#AEEA00)
        estilos_lbl = [
            ((255, 235, 59), (255, 0, 0), "Nombre 1"),
            ((255, 255, 255), (0, 200, 83), "Nombre 2"),
            ((255, 255, 255), (0, 145, 234), "Nombre 3"),
            ((255, 255, 255), (174, 234, 0), "Nombre 4")
        ]

        pos_etiquetas = [
            (ox + 3 * cs, oy - 22),       # Top Left
            (ox + 12 * cs, oy - 22),      # Top Right
            (ox + 3 * cs, oy + 15 * cs + 22),   # Bottom Left
            (ox + 12 * cs, oy + 15 * cs + 22)   # Bottom Right
        ]

        for i in range(min(4, len(partida.jugadores))):
            cx, cy = pos_etiquetas[i]
            col_bg, col_borde, nom_default = estilos_lbl[i]

            nom = partida.jugadores[i].nombre if i < len(partida.jugadores) else nom_default

            txt_surf = self._render_texto_delineado(nom, self.fuente_tag, (20, 20, 20), (255, 255, 255), 1)
            bw, bh = max(110, txt_surf.get_width() + 30), 28
            rect_lbl = pygame.Rect(cx - bw // 2, cy - bh // 2, bw, bh)

            pygame.draw.rect(self.pantalla, col_bg, rect_lbl, border_radius=14)
            pygame.draw.rect(self.pantalla, col_borde, rect_lbl, width=3, border_radius=14)
            self.pantalla.blit(txt_surf, txt_surf.get_rect(center=rect_lbl.center))

    def _dibujar_dados_indicadores_jugadores(self):
        ox, oy = self.origen_x, self.origen_y
        cs = self.tam_celda

        # 4 Cuadros de dados con bordes de color correspondientes a las bases:
        # Red, Green, Blue, Yellow
        dados_config = [
            (ox - 35, oy + 3 * cs, (255, 0, 0)),
            (ox + 15 * cs + 35, oy + 3 * cs, (0, 200, 83)),
            (ox - 35, oy + 12 * cs, (0, 145, 234)),
            (ox + 15 * cs + 35, oy + 12 * cs, (255, 214, 0))
        ]

        for px, py, col_borde in dados_config:
            r_d = pygame.Rect(px - 14, py - 14, 28, 28)
            pygame.draw.rect(self.pantalla, (255, 255, 255), r_d, border_radius=4)
            pygame.draw.rect(self.pantalla, col_borde, r_d, width=3, border_radius=4)
            pygame.draw.circle(self.pantalla, (20, 20, 20), r_d.center, 3)

    def _obtener_px_posicion(self, ficha, pos: int) -> tuple[float, float]:
        partida = self.gestor.partidaActual
        tablero = partida.tablero
        ox, oy = self.origen_x, self.origen_y
        cs = self.tam_celda

        if pos == 0:
            spots = self.GRID_BASE[ficha.color]
            spot = spots[(ficha.id_ficha - 1) % 4]
            r, c = spot
            return ox + c * cs, oy + r * cs
        elif pos == 58 or ficha.enMeta:
            return ox + 7.5 * cs, oy + 7.5 * cs
        elif pos <= 51:
            f_temp = type('FichaTemp', (), {'enBase': False, 'enMeta': False, 'posicion': pos, 'color': ficha.color})()
            c_global = tablero.obtener_casilla_global(f_temp)
            r, c = self.GRID_CIRCUITO_52[c_global]
            return ox + (c + 0.5) * cs, oy + (r + 0.5) * cs
        else:
            idx = pos - 52
            grid_meta = {
                Color.ROJO: self.GRID_META_ROJO,
                Color.VERDE: self.GRID_META_VERDE,
                Color.AMARILLO: self.GRID_META_AMARILLO,
                Color.AZUL: self.GRID_META_AZUL
            }[ficha.color]
            r, c = grid_meta[idx]
            return ox + (c + 0.5) * cs, oy + (r + 0.5) * cs

    def _dibujar_fichas(self):
        partida = self.gestor.partidaActual
        if not partida:
            return

        movimientos_validos = partida.obtenerMovimientosValidos() if partida.esperando_movimiento else []
        radio_ficha = int(self.tam_celda * 0.35)

        for jug in partida.jugadores:
            for f in jug.fichas:
                target_x, target_y = self._obtener_px_posicion(f, f.posicion)

                if f in self.colas_anim_pasos and len(self.colas_anim_pasos[f]) > 0:
                    paso_dest_x, paso_dest_y = self.colas_anim_pasos[f][0]

                    if f not in self.posiciones_fichas_anim:
                        self.posiciones_fichas_anim[f] = [paso_dest_x, paso_dest_y, 0.0]

                    curr_x, curr_y, _ = self.posiciones_fichas_anim[f]
                    dx = paso_dest_x - curr_x
                    dy = paso_dest_y - curr_y
                    dist = math.hypot(dx, dy)

                    if dist < 4.0:
                        self.posiciones_fichas_anim[f] = [paso_dest_x, paso_dest_y, 0.0]
                        self.colas_anim_pasos[f].pop(0)
                    else:
                        curr_x += dx * 0.35
                        curr_y += dy * 0.35
                        progreso = 1.0 - (dist / max(self.tam_celda, 1.0))
                        arc_y = -15 * math.sin(max(0.0, min(1.0, progreso)) * math.pi)
                        self.posiciones_fichas_anim[f] = [curr_x, curr_y, arc_y]

                else:
                    if f not in self.posiciones_fichas_anim:
                        self.posiciones_fichas_anim[f] = [target_x, target_y, 0.0]
                    else:
                        curr_x, curr_y, _ = self.posiciones_fichas_anim[f]
                        curr_x += (target_x - curr_x) * 0.35
                        curr_y += (target_y - curr_y) * 0.35
                        self.posiciones_fichas_anim[f] = [curr_x, curr_y, 0.0]

                px, py, arc_y = self.posiciones_fichas_anim[f]
                render_y = py + arc_y

                es_valida = (f in movimientos_validos)
                if es_valida and not jug.es_bot:
                    radio_glow = radio_ficha + 4 + 3 * math.sin(self.ticks_glow * 0.2)
                    pygame.draw.circle(self.pantalla, (255, 240, 80), (int(px), int(render_y)), int(radio_glow))
                    pygame.draw.circle(self.pantalla, (255, 255, 255), (int(px), int(render_y)), int(radio_glow - 2), width=2)

                # Peón/Ficha estilizado de Ludo
                pygame.draw.circle(self.pantalla, (20, 20, 20), (int(px), int(render_y) + 2), radio_ficha)
                pygame.draw.circle(self.pantalla, f.color.obtener_rgb(), (int(px), int(render_y)), radio_ficha)
                pygame.draw.circle(self.pantalla, (20, 20, 20), (int(px), int(render_y)), radio_ficha, width=2)
                pygame.draw.circle(self.pantalla, (255, 255, 255), (int(px - 3), int(render_y - 3)), max(2, radio_ficha // 3))

    def _dibujar_panel_derecho(self):
        partida = self.gestor.partidaActual
        if not partida:
            return

        px = self.pos_panel_x
        py = self.pos_panel_y

        # 1. Icono de Pergamino / Reglas a la izquierda del botón PAUSA
        r_perg = pygame.Rect(px - 10, py + 2, 34, 38)
        pygame.draw.rect(self.pantalla, (80, 220, 240), r_perg, border_radius=6)
        pygame.draw.rect(self.pantalla, (20, 20, 20), r_perg, width=2, border_radius=6)
        txt_p_icon = self.fuente_sub.render("📜", True, (20, 20, 20))
        self.pantalla.blit(txt_p_icon, txt_p_icon.get_rect(center=r_perg.center))

        # 2. Botón PAUSA (Azul con BORDE ROJO según Figma)
        self.btn_pausa = pygame.Rect(px + 35, py, 130, 42)
        pos_m = pygame.mouse.get_pos()
        hover = self.btn_pausa.collidepoint(pos_m)
        col_p = (25, 95, 235) if hover else (0, 85, 255)

        pygame.draw.rect(self.pantalla, col_p, self.btn_pausa, border_radius=4)
        pygame.draw.rect(self.pantalla, (255, 0, 0), self.btn_pausa, width=3, border_radius=4)

        txt_p = self._render_texto_delineado("PAUSA", self.fuente_titulo, (255, 255, 255), (0, 0, 0), 2)
        self.pantalla.blit(txt_p, txt_p.get_rect(center=self.btn_pausa.center))

        # 3. Caja de Dado Blanca (Interactiva)
        self.btn_lanzar = pygame.Rect(px - 10, py + 75, 48, 48)
        pygame.draw.rect(self.pantalla, (255, 255, 255), self.btn_lanzar, border_radius=6)
        pygame.draw.rect(self.pantalla, (0, 200, 83), self.btn_lanzar, width=3, border_radius=6)

        if self.animando_dado:
            self.frames_anim_dado -= 1
            self.dado_visual_temp = random.randint(1, 6)
            if self.frames_anim_dado <= 0:
                self.animando_dado = False
                partida.tirarDado()

        val_dado = self.dado_visual_temp if self.animando_dado else partida.dado
        self._dibujar_puntos_dado(self.btn_lanzar.centerx, self.btn_lanzar.centery, val_dado if val_dado > 0 else 1)

        # 4. Mensajes del Sistema (Exactamente como en Figma)
        # Linea 1 y 2: "Partida Iniciada correctamente"
        txt_msg1 = self._render_texto_delineado("Partida Iniciada", self.fuente_msg, (255, 255, 255), (0, 0, 0), 2)
        txt_msg1_2 = self._render_texto_delineado("correctamente", self.fuente_msg, (255, 255, 255), (0, 0, 0), 2)
        self.pantalla.blit(txt_msg1, (px + 50, py + 75))
        self.pantalla.blit(txt_msg1_2, (px + 50, py + 95))

        # Linea 3: "Turno de 'jugador 1'"
        jugador_act = partida.obtenerJugadorActual()
        nom_j = jugador_act.nombre.lower() if jugador_act else "jugador 1"
        txt_msg2 = self._render_texto_delineado(f"Turno de '{nom_j}'", self.fuente_msg, (255, 255, 255), (0, 0, 0), 2)
        self.pantalla.blit(txt_msg2, (px + 50, py + 135))

        # 5. Botón Reiniciar circular celeste ↺ abajo a la derecha
        self.btn_reiniciar = pygame.Rect(px + 140, py + int(self.alto_tablero) - 50, 46, 46)
        pygame.draw.circle(self.pantalla, (226, 120, 190), self.btn_reiniciar.center, 23)
        txt_ref = self._render_texto_delineado("↺", self.fuente_dado, (0, 153, 255), (255, 255, 255), 2)
        self.pantalla.blit(txt_ref, txt_ref.get_rect(center=self.btn_reiniciar.center))

    def _dibujar_puntos_dado(self, cx, cy, val):
        r_p = 3.5
        lx, rx = cx - 10, cx + 10
        ty, by = cy - 10, cy + 10

        coords = []
        if val in (1, 3, 5):
            coords.append((cx, cy))
        if val in (2, 3, 4, 5, 6):
            coords.extend([(lx, ty), (rx, by)])
        if val in (4, 5, 6):
            coords.extend([(rx, ty), (lx, by)])
        if val == 6:
            coords.extend([(lx, cy), (rx, cy)])

        for px, py in coords:
            pygame.draw.circle(self.pantalla, (20, 20, 20), (int(px), int(py)), int(r_p))

    def manejar_evento(self, evento):
        partida = self.gestor.partidaActual
        if not partida:
            return

        jugador_act = partida.obtenerJugadorActual()
        es_humano = jugador_act and not jugador_act.es_bot

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos

            if self.btn_lanzar.collidepoint(pos) and es_humano and not partida.dado_lanzado and not self.animando_dado:
                self.animando_dado = True
                self.frames_anim_dado = 12

            elif self.btn_pausa.collidepoint(pos):
                self.gestor.pausar()

            elif self.btn_reiniciar.collidepoint(pos):
                self.gestor.pausar()
                if hasattr(self.interfaz_padre, 'pantalla_pausa'):
                    self.interfaz_padre.pantalla_pausa.confirmando_accion = "REINICIAR"

            elif es_humano and partida.esperando_movimiento and not self.animando_dado:
                movimientos_validos = partida.obtenerMovimientosValidos()
                for ficha in movimientos_validos:
                    px, py, _ = self.posiciones_fichas_anim.get(ficha, (0, 0, 0))
                    distancia = math.hypot(pos[0] - px, pos[1] - py)
                    if distancia <= (self.tam_celda * 0.55):
                        pos_ant = ficha.posicion
                        self.gestor.seleccionarFicha(ficha)
                        pos_nue = ficha.posicion
                        self._generar_pasos_animacion(ficha, pos_ant, pos_nue)

                        if partida.estado == "FINALIZADA":
                            self.gestor.estado = "FINAL"
                        break
