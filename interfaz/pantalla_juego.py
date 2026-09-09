"""
Modulo pantalla_juego.py
Dibuja e interactúa con la Pantalla Principal del Juego de Ludo.
Soporta centrado adaptativo a cualquier resolución / pantalla completa,
animación de movimiento de fichas PASO A PASO CELDA POR CELDA con efecto salto (hop),
tiro de dado 3D animado y panel de control dinámico.
"""

import math
import random
import pygame
from modelos.color import Color


class PantallaJuego:

    def __init__(self, pantalla, gestor_partida, interfaz_padre=None):
        self.pantalla = pantalla
        self.gestor = gestor_partida
        self.interfaz_padre = interfaz_padre

        # Fuentes
        self.fuente_titulo = pygame.font.SysFont("Arial", 26, bold=True)
        self.fuente_sub = pygame.font.SysFont("Arial", 18, bold=True)
        self.fuente_msg = pygame.font.SysFont("Arial", 16)
        self.fuente_dado = pygame.font.SysFont("Arial", 46, bold=True)

        # Mapeo de cuadrícula 15x15 (fila, columna) para las 52 casillas del circuito
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

        # Estado de animación
        self.animando_dado = False
        self.frames_anim_dado = 0
        self.dado_visual_temp = 1
        self.posiciones_fichas_anim = {}  # {ficha: [curr_x, curr_y, arc_y]}
        self.colas_anim_pasos = {}        # {ficha: [[x1,y1], [x2,y2], ...]}
        self.ticks_glow = 0
        self.timer_bot = 0

    def _calcular_geometria(self):
        # Calcula dinámicamente el tamaño del tablero y paneles adaptándose a la resolución actual
        ancho, alto = self.pantalla.get_size()

        # Ancho reservado para el panel lateral de control
        ancho_panel = 320
        espacio_libre_ancho = ancho - ancho_panel - 60
        espacio_libre_alto = alto - 80

        # Tamaño del tablero (15 celdas)
        tam_tablero = min(espacio_libre_ancho, espacio_libre_alto)
        tam_tablero = max(tam_tablero, 450)  # Tamaño mínimo 450px

        self.tam_celda = tam_tablero / 15.0
        self.ancho_tablero = self.tam_celda * 15
        self.alto_tablero = self.tam_celda * 15

        # Centrar el tablero a la izquierda
        self.origen_x = (espacio_libre_ancho - self.ancho_tablero) // 2 + 40
        self.origen_y = (alto - self.alto_tablero) // 2

        # Posición del panel de control a la derecha
        self.pos_panel_x = max(self.origen_x + int(self.ancho_tablero) + 30, ancho - 340)
        self.pos_panel_y = self.origen_y
        self.ancho_panel = 310
        self.alto_panel = int(self.alto_tablero)

    def dibujar(self):
        self.ticks_glow += 1
        self._calcular_geometria()
        self.pantalla.fill((14, 22, 36))  # Fondo marino oscuro

        # Actualizar automatización del Bot
        self._actualizar_turno_bot()

        # Dibuja el tablero de Ludo
        self._dibujar_tablero_ludo()

        # Dibuja fichas con animación de salto paso a paso
        self._dibujar_fichas()

        # Dibuja el panel de control
        self._dibujar_panel_control()

    def _actualizar_turno_bot(self):
        partida = self.gestor.partidaActual
        if not partida or partida.estado != "EN_CURSO":
            return

        # Si hay fichas realizando animación de pasos, esperar a que terminen
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
        # Genera la cola de posiciones intermediate (x, y) celda por celda para la animación paso a paso
        if pos_inicio == pos_fin:
            return

        pasos_coords = []
        if pos_inicio == 0:
            # Salida de la base directamente a posición 1
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

        # Marco y fondo
        rect_tablero = pygame.Rect(ox, oy, self.ancho_tablero, self.alto_tablero)
        pygame.draw.rect(self.pantalla, (248, 248, 244), rect_tablero)

        # 4 Bases
        self._dibujar_base(ox, oy, Color.ROJO, (0, 0))
        self._dibujar_base(ox, oy, Color.VERDE, (0, 9))
        self._dibujar_base(ox, oy, Color.AZUL, (9, 0))
        self._dibujar_base(ox, oy, Color.AMARILLO, (9, 9))

        # Caminitos a la meta
        for r, c in self.GRID_META_ROJO:
            pygame.draw.rect(self.pantalla, Color.ROJO.obtener_rgb_claro(), (ox + c * cs, oy + r * cs, cs, cs))
        for r, c in self.GRID_META_VERDE:
            pygame.draw.rect(self.pantalla, Color.VERDE.obtener_rgb_claro(), (ox + c * cs, oy + r * cs, cs, cs))
        for r, c in self.GRID_META_AZUL:
            pygame.draw.rect(self.pantalla, Color.AZUL.obtener_rgb_claro(), (ox + c * cs, oy + r * cs, cs, cs))
        for r, c in self.GRID_META_AMARILLO:
            pygame.draw.rect(self.pantalla, Color.AMARILLO.obtener_rgb_claro(), (ox + c * cs, oy + r * cs, cs, cs))

        # Casillas de salida
        colores_salida = [
            (6, 1, Color.ROJO), (1, 8, Color.VERDE), (13, 6, Color.AZUL), (8, 13, Color.AMARILLO)
        ]
        for r, c, col in colores_salida:
            pygame.draw.rect(self.pantalla, col.obtener_rgb_claro(), (ox + c * cs, oy + r * cs, cs, cs))

        # Estrellas en casillas seguras
        casillas_estrella = [(6, 1), (2, 6), (1, 8), (6, 12), (8, 13), (12, 8), (13, 6), (8, 2)]
        for r, c in casillas_estrella:
            self._dibujar_estrella(ox + c * cs + cs // 2, oy + r * cs + cs // 2, cs * 0.32, (240, 190, 30))

        # Rejilla
        for i in range(16):
            pygame.draw.line(self.pantalla, (210, 210, 210), (ox, oy + i * cs), (ox + self.ancho_tablero, oy + i * cs), 1)
            pygame.draw.line(self.pantalla, (210, 210, 210), (ox + i * cs, oy), (ox + i * cs, oy + self.alto_tablero), 1)

        # Centro (Meta Triángulos)
        cx, cy = ox + 6 * cs, oy + 6 * cs
        cz = 3 * cs
        rect_meta = pygame.Rect(cx, cy, cz, cz)
        pygame.draw.rect(self.pantalla, (240, 240, 240), rect_meta)

        center_pt = (cx + cz // 2, cy + cz // 2)
        pygame.draw.polygon(self.pantalla, Color.ROJO.obtener_rgb(), [(cx, cy), (cx, cy + cz), center_pt])
        pygame.draw.polygon(self.pantalla, Color.VERDE.obtener_rgb(), [(cx, cy), (cx + cz, cy), center_pt])
        pygame.draw.polygon(self.pantalla, Color.AMARILLO.obtener_rgb(), [(cx + cz, cy), (cx + cz, cy + cz), center_pt])
        pygame.draw.polygon(self.pantalla, Color.AZUL.obtener_rgb(), [(cx, cy + cz), (cx + cz, cy + cz), center_pt])

        pygame.draw.rect(self.pantalla, (30, 30, 30), rect_tablero, width=4)

    def _dibujar_base(self, ox, oy, color, offset_grid):
        cs = self.tam_celda
        r_off, c_off = offset_grid
        rect = pygame.Rect(ox + c_off * cs, oy + r_off * cs, 6 * cs, 6 * cs)
        pygame.draw.rect(self.pantalla, color.obtener_rgb(), rect)
        rect_inner = rect.inflate(-cs * 0.75, -cs * 0.75)
        pygame.draw.rect(self.pantalla, (255, 255, 255), rect_inner, border_radius=int(cs * 0.35))

    def _dibujar_estrella(self, cx, cy, radio, color):
        puntos = []
        for i in range(10):
            r = radio if i % 2 == 0 else radio / 2.2
            angulo = i * math.pi / 5 - math.pi / 2
            puntos.append((cx + r * math.cos(angulo), cy + r * math.sin(angulo)))
        pygame.draw.polygon(self.pantalla, color, puntos)
        pygame.draw.polygon(self.pantalla, (255, 255, 255), puntos, width=1)

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
            # Posición temporal para cálculo global
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
        radio_ficha = int(self.tam_celda * 0.36)

        for jug in partida.jugadores:
            for f in jug.fichas:
                target_x, target_y = self._obtener_px_posicion(f, f.posicion)

                # Si hay pasos de animación pendientes (paso a paso hop)
                if f in self.colas_anim_pasos and len(self.colas_anim_pasos[f]) > 0:
                    paso_dest_x, paso_dest_y = self.colas_anim_pasos[f][0]

                    if f not in self.posiciones_fichas_anim:
                        self.posiciones_fichas_anim[f] = [paso_dest_x, paso_dest_y, 0.0]

                    curr_x, curr_y, _ = self.posiciones_fichas_anim[f]
                    dx = paso_dest_x - curr_x
                    dy = paso_dest_y - curr_y
                    dist = math.hypot(dx, dy)

                    if dist < 4.0:
                        # Llegó a la celda intermedia, pasar a la siguiente
                        self.posiciones_fichas_anim[f] = [paso_dest_x, paso_dest_y, 0.0]
                        self.colas_anim_pasos[f].pop(0)
                    else:
                        # Mover con arco vertical (efecto salto)
                        curr_x += dx * 0.35
                        curr_y += dy * 0.35
                        progreso = 1.0 - (dist / max(self.tam_celda, 1.0))
                        arc_y = -15 * math.sin(max(0.0, min(1.0, progreso)) * math.pi)
                        self.posiciones_fichas_anim[f] = [curr_x, curr_y, arc_y]

                else:
                    # Desplazamiento normal directo
                    if f not in self.posiciones_fichas_anim:
                        self.posiciones_fichas_anim[f] = [target_x, target_y, 0.0]
                    else:
                        curr_x, curr_y, _ = self.posiciones_fichas_anim[f]
                        curr_x += (target_x - curr_x) * 0.35
                        curr_y += (target_y - curr_y) * 0.35
                        self.posiciones_fichas_anim[f] = [curr_x, curr_y, 0.0]

                px, py, arc_y = self.posiciones_fichas_anim[f]
                render_y = py + arc_y

                # Resaltar fichas seleccionables con destello (✨●)
                es_valida = (f in movimientos_validos)
                if es_valida and not jug.es_bot:
                    radio_glow = radio_ficha + 4 + 3 * math.sin(self.ticks_glow * 0.2)
                    pygame.draw.circle(self.pantalla, (255, 240, 80), (int(px), int(render_y)), int(radio_glow))
                    pygame.draw.circle(self.pantalla, (255, 255, 255), (int(px), int(render_y)), int(radio_glow - 2), width=2)

                # Cuerpo de la ficha
                pygame.draw.circle(self.pantalla, (20, 20, 20), (int(px), int(render_y) + 3), radio_ficha)
                pygame.draw.circle(self.pantalla, f.color.obtener_rgb(), (int(px), int(render_y)), radio_ficha)
                pygame.draw.circle(self.pantalla, (255, 255, 255), (int(px), int(render_y)), radio_ficha, width=2)
                pygame.draw.circle(self.pantalla, (255, 255, 255), (int(px - 3), int(render_y - 3)), max(2, radio_ficha // 3))

    def _dibujar_panel_control(self):
        partida = self.gestor.partidaActual
        if not partida:
            return

        pos_x = self.pos_panel_x
        pos_y = self.pos_panel_y
        ancho_p = self.ancho_panel

        # Fondo del panel lateral (Glassmorphic dark card)
        rect_panel = pygame.Rect(pos_x, pos_y, ancho_p, int(self.alto_tablero))
        pygame.draw.rect(self.pantalla, (24, 36, 56), rect_panel, border_radius=15)
        pygame.draw.rect(self.pantalla, (55, 80, 120), rect_panel, width=2, border_radius=15)

        # 1. Jugador Actual Banner
        jugador_act = partida.obtenerJugadorActual()
        if jugador_act:
            rect_banner = pygame.Rect(pos_x + 15, pos_y + 20, ancho_p - 30, 65)
            pygame.draw.rect(self.pantalla, jugador_act.color.obtener_rgb(), rect_banner, border_radius=12)
            pygame.draw.rect(self.pantalla, (255, 255, 255), rect_banner, width=2, border_radius=12)

            tipo_str = " (BOT 🤖)" if jugador_act.es_bot else " (HUMANO 👤)"
            txt_j = self.fuente_sub.render("TURNO ACTUAL" + tipo_str, True, (240, 240, 240))
            txt_nom = self.fuente_titulo.render(jugador_act.nombre, True, (255, 255, 255))
            self.pantalla.blit(txt_j, (pos_x + 25, pos_y + 25))
            self.pantalla.blit(txt_nom, (pos_x + 25, pos_y + 48))

        # 2. Área de Dado Animado
        rect_dado_box = pygame.Rect(pos_x + 80, pos_y + 115, 150, 110)
        pygame.draw.rect(self.pantalla, (242, 246, 250), rect_dado_box, border_radius=15)
        pygame.draw.rect(self.pantalla, (90, 110, 140), rect_dado_box, width=3, border_radius=15)

        if self.animando_dado:
            self.frames_anim_dado -= 1
            self.dado_visual_temp = random.randint(1, 6)
            if self.frames_anim_dado <= 0:
                self.animando_dado = False
                partida.tirarDado()

        val_dado_mostrar = self.dado_visual_temp if self.animando_dado else partida.dado
        txt_dado = self.fuente_dado.render(str(val_dado_mostrar) if val_dado_mostrar > 0 else "-", True, (20, 30, 50))
        self.pantalla.blit(txt_dado, txt_dado.get_rect(center=rect_dado_box.center))

        # Botón Lanzar Dado
        self.btn_lanzar = pygame.Rect(pos_x + 25, pos_y + 245, ancho_p - 50, 48)
        es_humano = jugador_act and not jugador_act.es_bot
        puede_lanzar = es_humano and not partida.dado_lanzado and not self.animando_dado
        color_btn_lanzar = (40, 180, 80) if puede_lanzar else (90, 100, 120)
        self._dibujar_boton(self.btn_lanzar, "LANZAR DADO", color_btn_lanzar, puede_lanzar)

        # 3. Mensaje de Estado
        rect_msg = pygame.Rect(pos_x + 20, pos_y + 310, ancho_p - 40, 105)
        pygame.draw.rect(self.pantalla, (18, 26, 42), rect_msg, border_radius=10)
        pygame.draw.rect(self.pantalla, (60, 80, 115), rect_msg, width=1, border_radius=10)

        txt_msg = self.fuente_msg.render(partida.mensaje_estado, True, (220, 235, 255))
        self.pantalla.blit(txt_msg, (pos_x + 30, pos_y + 325))

        # 4. Botones Pausa, Estadísticas y Reglas
        self.btn_pausa = pygame.Rect(pos_x + 25, pos_y + 430, ancho_p - 50, 42)
        self.btn_stats = pygame.Rect(pos_x + 25, pos_y + 485, (ancho_p - 60) // 2, 42)
        self.btn_reglas = pygame.Rect(pos_x + 25 + (ancho_p - 60) // 2 + 10, pos_y + 485, (ancho_p - 60) // 2, 42)

        self._dibujar_boton(self.btn_pausa, "PAUSAR", (220, 140, 40))
        self._dibujar_boton(self.btn_stats, "ESTADÍSTICAS", (40, 120, 220))
        self._dibujar_boton(self.btn_reglas, "REGLAS", (140, 80, 200))

    def _dibujar_boton(self, rect, texto, color_base, habilitado=True):
        pos_m = pygame.mouse.get_pos()
        hover = rect.collidepoint(pos_m) and habilitado
        color = (min(color_base[0] + 35, 255), min(color_base[1] + 35, 255), min(color_base[2] + 35, 255)) if hover else color_base
        pygame.draw.rect(self.pantalla, color, rect, border_radius=8)
        pygame.draw.rect(self.pantalla, (255, 255, 255), rect, width=2, border_radius=8)
        txt = self.fuente_sub.render(texto, True, (255, 255, 255) if habilitado else (160, 160, 160))
        self.pantalla.blit(txt, txt.get_rect(center=rect.center))

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

            elif self.btn_stats.collidepoint(pos):
                self.gestor.consultarEstadisticas()

            elif self.btn_reglas.collidepoint(pos):
                self.gestor.consultarReglas()

            elif es_humano and partida.esperando_movimiento and not self.animando_dado:
                movimientos_validos = partida.obtenerMovimientosValidos()
                for ficha in movimientos_validos:
                    px, py, _ = self.posiciones_fichas_anim.get(ficha, (0, 0, 0))
                    distancia = math.hypot(pos[0] - px, pos[1] - py)
                    if distancia <= (self.tam_celda * 0.5):
                        pos_ant = ficha.posicion
                        self.gestor.seleccionarFicha(ficha)
                        pos_nue = ficha.posicion
                        self._generar_pasos_animacion(ficha, pos_ant, pos_nue)

                        if partida.estado == "FINALIZADA":
                            self.gestor.estado = "FINAL"
                        break
