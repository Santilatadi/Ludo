"""
Modulo pantalla_juego.py
Dibuja e interactúa con la Pantalla Principal del Juego de Ludo.
Diseño moderno en alta definición con animaciones 3D de dado, estelas de partículas,
relatoría de partida en vivo, vista previa de movimientos al pasar el cursor y trivia.
"""

import os
import math
import random
import pygame
from modelos.color import Color
from interfaz.efectos import SistemaParticulas, dibujar_panel_glassmorphism, dibujar_texto_glow
from interfaz.componentes import BotonModerno

COLOR_RGB = {
    Color.ROJO: (220, 50, 50),
    Color.AZUL: (40, 120, 220),
    Color.VERDE: (40, 180, 80),
    Color.AMARILLO: (240, 190, 40)
}


def get_rgb(col):
    if isinstance(col, Color):
        return COLOR_RGB.get(col, (200, 200, 200))
    return col


class PantallaJuego:

    def __init__(self, pantalla, gestor_partida, interfaz_padre=None):
        self.pantalla = pantalla
        self.gestor = gestor_partida
        self.interfaz_padre = interfaz_padre
        self.particulas = interfaz_padre.particulas if interfaz_padre else SistemaParticulas()

        ruta_fuente = "assets/font.ttf"
        if os.path.exists(ruta_fuente):
            self.fuente_titulo = pygame.font.Font(ruta_fuente, 24)
            self.fuente_sub = pygame.font.Font(ruta_fuente, 18)
            self.fuente_tag = pygame.font.Font(ruta_fuente, 16)
            self.fuente_msg = pygame.font.Font(ruta_fuente, 16)
            self.fuente_dado = pygame.font.Font(ruta_fuente, 42)
        else:
            self.fuente_titulo = pygame.font.SysFont("Impact", 24, bold=True)
            self.fuente_sub = pygame.font.SysFont("Arial", 18, bold=True)
            self.fuente_tag = pygame.font.SysFont("Arial", 16, bold=True)
            self.fuente_msg = pygame.font.SysFont("Arial", 16, bold=True)
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

        self.mensaje_relator = "¡Partida iniciada! Lanza el dado para comenzar."
        self.ficha_hover_activa = None

    def _calcular_geometria(self):
        ancho, alto = self.pantalla.get_size()
        ancho_panel = 280
        espacio_libre_ancho = ancho - ancho_panel - 60
        espacio_libre_alto = alto - 80

        tam_tablero = min(espacio_libre_ancho, espacio_libre_alto)
        tam_tablero = max(tam_tablero, 420)

        self.tam_celda = tam_tablero / 15.0
        self.ancho_tablero = self.tam_celda * 15
        self.alto_tablero = self.tam_celda * 15

        self.origen_x = (espacio_libre_ancho - self.ancho_tablero) // 2 + 30
        self.origen_y = (alto - self.alto_tablero) // 2 - 15

        self.pos_panel_x = self.origen_x + int(self.ancho_tablero) + 25
        self.pos_panel_y = self.origen_y
        self.ancho_panel = 260
        self.alto_panel = int(self.alto_tablero)

    def dibujar(self):
        partida_actual = self.gestor.partidaActual
        if getattr(self, '_partida_ref', None) != partida_actual or getattr(partida_actual, '_fue_reiniciada', False):
            if getattr(partida_actual, '_fue_reiniciada', False):
                partida_actual._fue_reiniciada = False
            self._partida_ref = partida_actual
            self.posiciones_fichas_anim.clear()
            self.colas_anim_pasos.clear()
            self.timer_bot = 0
            self.animando_dado = False
            self.ficha_hover_activa = None

        self.ticks_glow += 1
        self._calcular_geometria()
        ancho, alto = self.pantalla.get_size()

        # Canvas de fondo violeta según diseño en Figma
        self.pantalla.fill((46, 21, 90))

        self.particulas.actualizar_y_dibujar(self.pantalla)
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
                self.frames_anim_dado = 12
                self.timer_bot = 0

        elif partida.esperando_movimiento and not self.animando_dado:
            if self.timer_bot >= 35:
                movimientos_validos = partida.obtenerMovimientosValidos()
                if movimientos_validos:
                    ficha_elegida = self._seleccionar_mejor_movimiento_bot(jugador_act, movimientos_validos, partida.tablero)
                    if ficha_elegida:
                        pos_ant = ficha_elegida.posicion
                        self.gestor.seleccionarFicha(ficha_elegida)
                        pos_nue = ficha_elegida.posicion
                        self._generar_pasos_animacion(ficha_elegida, pos_ant, pos_nue)

                        if partida.estado == "FINALIZADA":
                            self.gestor.estado = "FINAL"
                            self.particulas.emitir_confeti(self.origen_x + self.ancho_tablero // 2, self.origen_y + self.alto_tablero // 2, 120)
                self.timer_bot = 0

    def _seleccionar_mejor_movimiento_bot(self, jugador, movimientos_validos: list, tablero):
        if not movimientos_validos:
            return None
        salida_colores = {Color.ROJO: 0, Color.VERDE: 13, Color.AMARILLO: 26, Color.AZUL: 39}
        casillas_seguras = {0, 8, 13, 21, 26, 34, 39, 47}
        partida = self.gestor.partidaActual
        if partida:
            for f in movimientos_validos:
                if not f.enBase and not f.enMeta and f.posicion <= 51:
                    casilla_proy = (salida_colores.get(f.color, 0) + (f.posicion + 1 - 1)) % 52
                    if casilla_proy not in casillas_seguras:
                        for jug_rival in partida.jugadores:
                            if jug_rival.color != jugador.color:
                                for f_rival in jug_rival.fichas:
                                    if not f_rival.enBase and not f_rival.enMeta and f_rival.posicion <= 51:
                                        c_rival = (salida_colores.get(f_rival.color, 0) + (f_rival.posicion - 1)) % 52
                                        if c_rival == casilla_proy:
                                            return f
        for f in movimientos_validos:
            if f.enBase:
                return f
        for f in movimientos_validos:
            if f.posicion + 1 > 51:
                return f
        return sorted(movimientos_validos, key=lambda x: x.posicion, reverse=True)[0]

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
        # Para almacenar los pasos de una animación.
        #durante la animación, va tomando las posiciones en orden para mostrar cómo avanza la ficha.
        #1. La ficha aparece en la posición 1.
        #2. Avanza a la posición 2.
        #3. Avanza a la posición 3.
        #Así, el movimiento se muestra progresivamente,
        #en lugar de hacer que la ficha aparezca directamente en el destino. 
        
        self.colas_anim_pasos[ficha] = pasos_coords

    def _dibujar_tablero_ludo(self):
        ox, oy = self.origen_x, self.origen_y
        cs = self.tam_celda

        # Sombra del tablero
        rect_sombra = pygame.Rect(ox + 8, oy + 8, self.ancho_tablero, self.alto_tablero)
        pygame.draw.rect(self.pantalla, (10, 15, 30, 100), rect_sombra, border_radius=12)

        rect_tablero = pygame.Rect(ox, oy, self.ancho_tablero, self.alto_tablero)
        pygame.draw.rect(self.pantalla, (255, 255, 255), rect_tablero, border_radius=12)

        # 4 Bases en esquinas
        self._dibujar_base(ox, oy, Color.ROJO, (0, 0))
        self._dibujar_base(ox, oy, Color.VERDE, (0, 9))
        self._dibujar_base(ox, oy, Color.AZUL, (9, 0))
        self._dibujar_base(ox, oy, Color.AMARILLO, (9, 9))

        # Caminitos a la meta
        for r, c in self.GRID_META_ROJO:
            pygame.draw.rect(self.pantalla, get_rgb(Color.ROJO), (ox + c * cs, oy + r * cs, cs, cs))
        for r, c in self.GRID_META_VERDE:
            pygame.draw.rect(self.pantalla, get_rgb(Color.VERDE), (ox + c * cs, oy + r * cs, cs, cs))
        for r, c in self.GRID_META_AZUL:
            pygame.draw.rect(self.pantalla, get_rgb(Color.AZUL), (ox + c * cs, oy + r * cs, cs, cs))
        for r, c in self.GRID_META_AMARILLO:
            pygame.draw.rect(self.pantalla, get_rgb(Color.AMARILLO), (ox + c * cs, oy + r * cs, cs, cs))

        # Casillas de salida
        colores_salida = [
            (6, 1, Color.ROJO), (1, 8, Color.VERDE), (13, 6, Color.AZUL), (8, 13, Color.AMARILLO)
        ]
        for r, c, col in colores_salida:
            pygame.draw.rect(self.pantalla, get_rgb(col), (ox + c * cs, oy + r * cs, cs, cs))

        # Estrellas en casillas seguras
        casillas_estrella = [
            ((6, 1), Color.ROJO), ((1, 8), Color.VERDE), ((13, 6), Color.AZUL), ((8, 13), Color.AMARILLO),
            ((2, 6), (150, 150, 150)), ((6, 12), (150, 150, 150)), ((12, 8), (150, 150, 150)), ((8, 2), (150, 150, 150))
        ]
        for (r, c), col in casillas_estrella:
            color_rgb = get_rgb(col)
            self._dibujar_estrella(ox + c * cs + cs // 2, oy + r * cs + cs // 2, cs * 0.34, color_rgb)

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
        pygame.draw.polygon(self.pantalla, get_rgb(Color.ROJO), [(cx, cy), (cx, cy + cz), center_pt])
        pygame.draw.polygon(self.pantalla, get_rgb(Color.VERDE), [(cx, cy), (cx + cz, cy), center_pt])
        pygame.draw.polygon(self.pantalla, get_rgb(Color.AMARILLO), [(cx + cz, cy), (cx + cz, cy + cz), center_pt])
        pygame.draw.polygon(self.pantalla, get_rgb(Color.AZUL), [(cx, cy + cz), (cx + cz, cy + cz), center_pt])

        # Borde dorado resplandeciente del tablero
        pygame.draw.rect(self.pantalla, (255, 215, 0), rect_tablero, width=4, border_radius=12)

    def _dibujar_base(self, ox, oy, color, offset_grid):
        cs = self.tam_celda
        r_off, c_off = offset_grid
        rect = pygame.Rect(ox + c_off * cs, oy + r_off * cs, 6 * cs, 6 * cs)
        pygame.draw.rect(self.pantalla, get_rgb(color), rect)
        pygame.draw.rect(self.pantalla, (20, 20, 20), rect, width=2)

        # Región interna blanca
        rect_inner = rect.inflate(-cs * 0.8, -cs * 0.8)
        pygame.draw.rect(self.pantalla, (255, 255, 255), rect_inner, border_radius=int(cs * 0.4))
        pygame.draw.rect(self.pantalla, (20, 20, 20), rect_inner, width=2, border_radius=int(cs * 0.4))

        # 4 Círculos blancos ovalados para las fichas
        spots = [(1.5, 1.5), (1.5, 3.5), (3.5, 1.5), (3.5, 3.5)]
        for sr, sc in spots:
            c_x = ox + (c_off + sc) * cs
            c_y = oy + (r_off + sr) * cs
            r_outer = cs * 0.65
            pygame.draw.ellipse(self.pantalla, get_rgb(color), (c_x - r_outer * 0.6, c_y - r_outer * 0.8, r_outer * 1.2, r_outer * 1.6))
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

        pos_por_color = {
            Color.ROJO: (ox + 3 * cs, oy - 22),
            Color.VERDE: (ox + 12 * cs, oy - 22),
            Color.AZUL: (ox + 3 * cs, oy + 15 * cs + 22),
            Color.AMARILLO: (ox + 12 * cs, oy + 15 * cs + 22)
        }

        jug_act = partida.obtenerJugadorActual()

        for jug in partida.jugadores:
            if jug.color not in pos_por_color:
                continue

            cx, cy = pos_por_color[jug.color]
            col_bg = (255, 235, 59) if jug_act == jug else (255, 255, 255)
            col_borde = jug.color.obtener_rgb()
            nom = jug.nombre

            # Indicador de turno con escala pulsatil
            es_turno = (jug_act == jug)
            scale = 1.05 + 0.05 * math.sin(self.ticks_glow * 0.15) if es_turno else 1.0

            txt_surf = self.fuente_tag.render(f"{'🤖 ' if jug.es_bot else '👤 '}{nom}", True, (20, 20, 20))
            bw, bh = max(120, int((txt_surf.get_width() + 30) * scale)), int(28 * scale)
            rect_lbl = pygame.Rect(cx - bw // 2, cy - bh // 2, bw, bh)

            borde = (255, 215, 0) if es_turno else col_borde
            pygame.draw.rect(self.pantalla, col_bg, rect_lbl, border_radius=14)
            pygame.draw.rect(self.pantalla, borde, rect_lbl, width=4 if es_turno else 2, border_radius=14)
            self.pantalla.blit(txt_surf, txt_surf.get_rect(center=rect_lbl.center))

    def _dibujar_dados_indicadores_jugadores(self):
        ox, oy = self.origen_x, self.origen_y
        cs = self.tam_celda

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
        ox, oy = self.origen_x, self.origen_y
        cs = self.tam_celda

        if pos == 0:
            spots = self.GRID_BASE[ficha.color]
            jugador = next((j for j in partida.jugadores if ficha in j.fichas), None) if partida else None
            idx = jugador.fichas.index(ficha) if (jugador and ficha in jugador.fichas) else 0
            spot = spots[idx % 4]
            r, c = spot
            return ox + c * cs, oy + r * cs
        elif pos == 58 or ficha.enMeta:
            return ox + 7.5 * cs, oy + 7.5 * cs
        elif pos <= 51:
            salida_colores = {Color.ROJO: 0, Color.VERDE: 13, Color.AMARILLO: 26, Color.AZUL: 39}
            c_global = (salida_colores.get(ficha.color, 0) + (pos - 1)) % 52
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
        radio_ficha = int(self.tam_celda * 0.36)
        pos_mouse = pygame.mouse.get_pos()

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
                        arc_y = -18 * math.sin(max(0.0, min(1.0, progreso)) * math.pi)
                        self.posiciones_fichas_anim[f] = [curr_x, curr_y, arc_y]
                        self.particulas.emitir_estela_ficha(curr_x, curr_y + arc_y, get_rgb(f.color))

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
                dist_m = math.hypot(pos_mouse[0] - px, pos_mouse[1] - render_y)

                if es_valida and dist_m <= radio_ficha * 1.5:
                    self.ficha_hover_activa = f

                if es_valida and not getattr(jug, "es_bot", False):
                    radio_glow = radio_ficha + 4 + 4 * math.sin(self.ticks_glow * 0.2)
                    pygame.draw.circle(self.pantalla, (255, 240, 80), (int(px), int(render_y)), int(radio_glow))
                    pygame.draw.circle(self.pantalla, (255, 255, 255), (int(px), int(render_y)), int(radio_glow - 2), width=2)

                # Ficha 3D estilizada
                pygame.draw.circle(self.pantalla, (20, 20, 20), (int(px) + 2, int(render_y) + 3), radio_ficha)
                pygame.draw.circle(self.pantalla, get_rgb(f.color), (int(px), int(render_y)), radio_ficha)
                pygame.draw.circle(self.pantalla, (255, 255, 255, 120), (int(px - 3), int(render_y - 4)), max(2, radio_ficha // 3))
                pygame.draw.circle(self.pantalla, (20, 20, 20), (int(px), int(render_y)), radio_ficha, width=2)

        # Vista previa de destino si el jugador pasa el cursor por encima de una ficha válida
        if self.ficha_hover_activa and self.ficha_hover_activa in movimientos_validos:
            pos_dest = self.ficha_hover_activa.posicion + partida.dado if self.ficha_hover_activa.posicion > 0 else 1
            dest_x, dest_y = self._obtener_px_posicion(self.ficha_hover_activa, pos_dest)
            pygame.draw.circle(self.pantalla, (255, 215, 0), (int(dest_x), int(dest_y)), int(radio_ficha * 0.8), width=3)

    def _dibujar_panel_derecho(self):
        partida = self.gestor.partidaActual
        if not partida:
            return

        px = self.pos_panel_x
        py = self.pos_panel_y

        # Panel traslúcido Glassmorphism
        rect_p = pygame.Rect(px - 20, py - 10, self.ancho_panel, self.alto_panel + 10)
        dibujar_panel_glassmorphism(self.pantalla, rect_p, color_bg=(16, 35, 95, 230), color_borde=(255, 215, 0, 200), radio=16)

        # 1. Botones superiores ordenados arriba (REGLAS, PAUSA y X)
        self.btn_reglas_inst = BotonModerno(
            (px - 10, py + 8, 92, 38), "REGLAS",
            color_base=(16, 56, 168), color_hover=(32, 75, 200),
            color_borde=(213, 27, 27), fuente=self.fuente_sub
        )
        self.btn_reglas_inst.dibujar(self.pantalla)

        self.btn_pausa_inst = BotonModerno(
            (px + 90, py + 8, 92, 38), "PAUSA",
            color_base=(16, 56, 168), color_hover=(32, 75, 200),
            color_borde=(213, 27, 27), fuente=self.fuente_sub
        )
        self.btn_pausa_inst.dibujar(self.pantalla)

        self.btn_salir_x = BotonModerno(
            (px + 190, py + 8, 38, 38), "X",
            color_base=(213, 27, 27), color_hover=(245, 50, 50),
            color_borde=(255, 220, 0), fuente=self.fuente_sub
        )
        self.btn_salir_x.dibujar(self.pantalla)

        # 2. Dado 3D Interactivo
        self.btn_lanzar = pygame.Rect(px - 10, py + 75, 54, 54)

        if self.animando_dado:
            self.frames_anim_dado -= 1
            self.dado_visual_temp = random.randint(1, 6)
            if self.frames_anim_dado <= 0:
                self.animando_dado = False
                self.gestor.lanzarDado()
                if partida.dado == 6:
                    self.particulas.emitir_estrellas(self.btn_lanzar.centerx, self.btn_lanzar.centery, 20)

        val_dado = self.dado_visual_temp if self.animando_dado else partida.dado

        # Efecto visual dado 3D
        col_dado_borde = (255, 215, 0) if (partida.esperando_movimiento and not self.animando_dado) else (0, 200, 83)
        pygame.draw.rect(self.pantalla, (255, 255, 255), self.btn_lanzar, border_radius=10)
        pygame.draw.rect(self.pantalla, col_dado_borde, self.btn_lanzar, width=4, border_radius=10)
        self._dibujar_puntos_dado(self.btn_lanzar.centerx, self.btn_lanzar.centery, val_dado if val_dado > 0 else 1)

        # 3. Mensajes del Sistema / Relator de Partida
        jugador_act = partida.obtenerJugadorActual()
        nom_j = jugador_act.nombre if jugador_act else "Jugador 1"

        if partida.dado_lanzado:
            str_relator = f"Turno de '{nom_j}': Sacó {partida.dado} 🎲"
        else:
            str_relator = f"Turno de '{nom_j}': ¡Lanza el dado!"

        dibujar_texto_glow(self.pantalla, "RELATOR DE JUEGO", self.fuente_sub, px + 55, py + 75, color_texto=(255, 215, 0), color_resplandor=(0, 0, 0))
        txt_m = self.fuente_msg.render(str_relator, True, (240, 240, 255))
        self.pantalla.blit(txt_m, (px + 55, py + 102))

    def _dibujar_puntos_dado(self, cx, cy, val):
        r_p = 4.0
        lx, rx = cx - 11, cx + 11
        ty, by = cy - 11, cy + 11

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
        es_humano = jugador_act and not getattr(jugador_act, "es_bot", False)

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos

            if hasattr(self, 'btn_reglas_inst') and self.btn_reglas_inst.es_cliqueado(evento):
                self.gestor.consultarReglas()

            elif hasattr(self, 'btn_pausa_inst') and self.btn_pausa_inst.es_cliqueado(evento):
                self.gestor.pausarPartida()

            elif hasattr(self, 'btn_salir_x') and self.btn_salir_x.es_cliqueado(evento):
                self.gestor.pausarPartida()
                if hasattr(self.interfaz_padre, 'pantalla_pausa'):
                    self.interfaz_padre.pantalla_pausa.confirmando_accion = "SALIR"

            elif self.btn_lanzar.collidepoint(pos) and es_humano and not partida.dado_lanzado and not self.animando_dado:
                self.animando_dado = True
                self.frames_anim_dado = 12

            elif es_humano and partida.esperando_movimiento and not self.animando_dado:
                movimientos_validos = partida.obtenerMovimientosValidos()
                for ficha in movimientos_validos:
                    px, py, _ = self.posiciones_fichas_anim.get(ficha, (0, 0, 0))
                    distancia = math.hypot(pos[0] - px, pos[1] - py)
                    if distancia <= (self.tam_celda * 0.6):
                        pos_ant = ficha.posicion
                        self.gestor.seleccionarFicha(ficha)
                        pos_nue = ficha.posicion
                        self._generar_pasos_animacion(ficha, pos_ant, pos_nue)

                        if partida.estado == "FINALIZADA":
                            self.gestor.estado = "FINAL"
                            self.particulas.emitir_confeti(self.origen_x + self.ancho_tablero // 2, self.origen_y + self.alto_tablero // 2, 120)
                        break
