"""
Modulo pantalla_juego.py
Frame "Partida" del Figma: tablero en el centro con el nombre de cada jugador arriba
y abajo, un dado al costado de cada base, los botones REGLAS y PAUSA arriba a la
derecha y los mensajes de la partida debajo.
"""

import math
import random
import pygame
from modelos.color import Color
from interfaz.efectos import SistemaParticulas
from interfaz import tema
from interfaz.componentes import BotonFigma

COLOR_RGB = {
    Color.ROJO: (220, 50, 50),
    Color.AZUL: (40, 120, 220),
    Color.VERDE: (40, 180, 80),
    Color.AMARILLO: (240, 190, 40)
}


# Esquina del tablero de cada color: 0 arriba-izq, 1 arriba-der, 2 abajo-izq, 3 abajo-der
ESQUINA_COLOR = {Color.ROJO: 0, Color.VERDE: 1, Color.AZUL: 2, Color.AMARILLO: 3}


def get_rgb(col):
    if isinstance(col, Color):
        return COLOR_RGB.get(col, (200, 200, 200))
    return col


class PantallaJuego:

    def __init__(self, pantalla, game_manager, interfaz_padre=None):
        self.pantalla = pantalla
        self.gestor = game_manager
        self.interfaz_padre = interfaz_padre
        self.interfaz = interfaz_padre
        self.mensaje = ""
        self.particulas = interfaz_padre.particulas if interfaz_padre else SistemaParticulas()
        self.particulas.orbes_fondo = []      # el fondo del Figma es liso

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

        # Centros de los círculos de cada base en la imagen del tablero del Figma (fila, columna)
        self.GRID_BASE = {
            Color.ROJO: [(1.91, 1.93), (1.91, 4.11), (4.16, 1.93), (4.16, 4.12)],
            Color.VERDE: [(1.91, 10.85), (1.91, 13.05), (4.16, 10.86), (4.17, 13.04)],
            Color.AMARILLO: [(10.83, 10.85), (10.83, 13.04), (13.08, 10.85), (13.08, 13.04)],
            Color.AZUL: [(10.83, 1.93), (10.83, 4.12), (13.08, 1.92), (13.09, 4.12)]
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
        self.btn_lanzar = pygame.Rect(-100, -100, 0, 0)

    def _calcular_geometria(self):
        # Tablero del Figma: 752x752 en (198, 104), 15x15 casilleros
        tablero = tema.R(self.pantalla, 198, 104, 752, 752)
        self.tam_celda = tablero.width / 15.0
        self.ancho_tablero = self.alto_tablero = tablero.width
        self.origen_x, self.origen_y = tablero.x, tablero.y

    def dibujar(self):
        partida_actual = self.gestor.partidaActual
        if getattr(self, '_partida_ref', None) is not partida_actual:
            self._partida_ref = partida_actual
            self.mensaje = ""
            self.posiciones_fichas_anim.clear()
            self.colas_anim_pasos.clear()
            self.timer_bot = 0
            self.animando_dado = False
            self.ficha_hover_activa = None

        self.ticks_glow += 1
        self._calcular_geometria()
        self.pantalla.fill(tema.FONDO)

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
        if not jugador_act or not tema.es_bot(jugador_act):
            self.timer_bot = 0
            return

        self.timer_bot += 1

        if not partida.dado and not self.animando_dado:
            if self.timer_bot >= 25:
                self.animando_dado = True
                self.frames_anim_dado = 12
                self.timer_bot = 0

        elif partida.dado and not self.animando_dado:
            if self.timer_bot >= 35:
                movimientos_validos = partida.obtenerMovimientosValidos()
                if movimientos_validos:
                    ficha_elegida = self._seleccionar_mejor_movimiento_bot(jugador_act, movimientos_validos, partida.tablero)
                    if ficha_elegida:
                        self._jugar_ficha(ficha_elegida)
                self.timer_bot = 0

    def _lanzar_dado(self):
        # CU-07/CU-08: el mensaje se arma con lo que devolvió el GameManager.
        partida = self.gestor.partidaActual
        jugador = partida.obtenerJugadorActual()
        valor = self.gestor.lanzarDado()
        if partida.obtenerJugadorActual() is not jugador:
            if valor == 6:
                self.mensaje = f"¡3 seis seguidos! {jugador.nombre} pierde el turno."
            else:
                self.mensaje = f"{jugador.nombre} sacó {valor} y no tiene movimientos válidos."
        else:
            self.mensaje = f"{jugador.nombre} sacó {valor}: elige una ficha."
        return valor

    def _jugar_ficha(self, ficha):
        # CU-08 y CU-09 (DS N8 y N9): el GameManager mueve la ficha elegida.
        partida = self.gestor.partidaActual
        jugador = partida.obtenerJugadorActual()
        pos_ant = ficha.posicion
        if not self.gestor.seleccionarFicha(ficha):
            return False
        self._generar_pasos_animacion(ficha, pos_ant, ficha.posicion)
        if partida.estado == "FINALIZADA":
            # CU-13: hay ganador, se muestra la pantalla de victoria
            self.gestor.finalizarPartida()
            self.particulas.emitir_confeti(self.origen_x + self.ancho_tablero // 2, self.origen_y + self.alto_tablero // 2, 120)
            self.interfaz.ir_a("FINAL")
        elif partida.obtenerJugadorActual() is jugador:
            self.mensaje = f"{jugador.nombre} sacó 6: vuelve a tirar."
        else:
            self.mensaje = f"Turno de {partida.obtenerJugadorActual().nombre}."
        return True

    def _seleccionar_mejor_movimiento_bot(self, jugador, movimientos_validos: list, tablero):
        if not movimientos_validos:
            return None
        salida_colores = {Color.ROJO: 0, Color.VERDE: 13, Color.AMARILLO: 26, Color.AZUL: 39}
        partida = self.gestor.partidaActual
        if partida:
            for f in movimientos_validos:
                if not f.enBase and not f.enMeta and f.posicion <= 51:
                    casilla_proy = (salida_colores.get(f.color, 0) + (f.posicion + 1 - 1)) % 52
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
        # Imagen del tablero exportada del Figma, con su borde negro de 10
        r = pygame.Rect(self.origen_x, self.origen_y, self.ancho_tablero, self.alto_tablero)
        self.pantalla.blit(tema.imagen("tablero.png", r.size), r.topleft)
        g = tema.T(self.pantalla, 10)
        pygame.draw.rect(self.pantalla, tema.NEGRO, r.inflate(g, g), width=g)

    def _dibujar_etiquetas_jugadores(self):
        # Píldoras 303x61 con el borde del color de la esquina; la del turno se rellena de amarillo
        partida = self.gestor.partidaActual
        if not partida:
            return
        p = self.pantalla
        posiciones = {0: (198, 26), 1: (647, 26), 2: (198, 873), 3: (647, 873)}
        jug_act = partida.obtenerJugadorActual()
        for jug in partida.jugadores[:4]:
            x, y = posiciones[ESQUINA_COLOR.get(jug.color, 0)]
            r = tema.R(p, x, y, 303, 61)
            relleno = (245, 223, 52) if jug is jug_act else tema.BLANCO   # #ffe100 al 76 % (Figma)
            pygame.draw.rect(p, relleno, r, border_radius=r.height // 2)
            pygame.draw.rect(p, tema.COLOR_DADO[jug.color], r, width=tema.T(p, 6), border_radius=r.height // 2)
            tema.texto_figma(p, jug.nombre, 0, 0, 40, trazo=6, centrado_en=(x + 151.5, y + 30.5))

    def _dibujar_dados_indicadores_jugadores(self):
        # Un dado de 95x95 al costado de cada base; el del jugador con el turno es el que
        # se lanza (CU-07), se pinta de naranja y muestra el valor obtenido.
        partida = self.gestor.partidaActual
        p = self.pantalla
        posiciones = {0: (86, 214), 1: (967, 214), 2: (86, 667), 3: (967, 667)}
        jug_act = partida.obtenerJugadorActual() if partida else None
        self.btn_lanzar = pygame.Rect(-100, -100, 0, 0)
        for jug in (partida.jugadores[:4] if partida else []):
            x, y = posiciones[ESQUINA_COLOR.get(jug.color, 0)]
            r = tema.R(p, x, y, 95, 95)
            valor = 1
            fondo = tema.BLANCO
            if jug is jug_act:
                self.btn_lanzar = r
                if self.animando_dado:
                    self.frames_anim_dado -= 1
                    self.dado_visual_temp = random.randint(1, 6)
                    if self.frames_anim_dado <= 0:
                        self.animando_dado = False
                        self._lanzar_dado()
                        if partida.dado == 6:
                            self.particulas.emitir_estrellas(r.centerx, r.centery, 20)
                valor = self.dado_visual_temp if self.animando_dado else (partida.dado or 1)
                if not partida.dado or self.animando_dado:
                    fondo = tema.DADO_ACTIVO        # falta tirar: el dado se resalta
            pygame.draw.rect(p, fondo, r)
            pygame.draw.rect(p, tema.COLOR_DADO[jug.color], r, width=tema.T(p, 6))
            self._dibujar_puntos_dado(r, valor)

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

        movimientos_validos = partida.obtenerMovimientosValidos()
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

                if es_valida and not tema.es_bot(jug):
                    radio_glow = radio_ficha + 4 + 3 * math.sin(self.ticks_glow * 0.2)
                    pygame.draw.circle(self.pantalla, (255, 240, 80), (int(px), int(render_y)), int(radio_glow), width=3)

                # Ficha con la forma del Figma (gota con borde negro)
                w, h = int(self.tam_celda * 0.8), int(self.tam_celda * 1.2)
                sprite = tema.imagen(f"ficha_{f.color.name.lower()}.png", (w, h))
                self.pantalla.blit(sprite, (int(px - w / 2), int(render_y - h * 0.55)))

        # Vista previa de destino si el jugador pasa el cursor por encima de una ficha válida
        if self.ficha_hover_activa and self.ficha_hover_activa in movimientos_validos:
            pos_dest = self.ficha_hover_activa.posicion + partida.dado if self.ficha_hover_activa.posicion > 0 else 1
            dest_x, dest_y = self._obtener_px_posicion(self.ficha_hover_activa, pos_dest)
            pygame.draw.circle(self.pantalla, (255, 215, 0), (int(dest_x), int(dest_y)), int(radio_ficha * 0.8), width=3)

    def _dibujar_panel_derecho(self):
        # Botones REGLAS y PAUSA y mensajes de la partida, como en el Figma
        partida = self.gestor.partidaActual
        if not partida:
            return
        p = self.pantalla
        self.btn_reglas_inst = BotonFigma(p, (967, 57, 207, 82), "REGLAS", tema.GRADIENTE, tema.AMARILLO_BORDE, 4,
                                          tam_texto=40, contorno_texto=None)
        self.btn_pausa_inst = BotonFigma(p, (1183, 57, 207, 82), "PAUSA", tema.GRADIENTE, tema.AMARILLO_BORDE, 4,
                                         tam_texto=48, contorno_texto=None)
        self.btn_reglas_inst.dibujar(p)
        self.btn_pausa_inst.dibujar(p)

        jugador_act = partida.obtenerJugadorActual()
        if self.mensaje:
            mensaje = self.mensaje
        elif partida.turnosJugados <= 1 and partida.dado == 0:
            mensaje = "Partida Iniciada correctamente"
        else:
            mensaje = ""
        lineas = self._partir_texto(mensaje, tema.fuente(40), 380)
        for k, linea in enumerate(lineas):
            tema.texto_figma(p, linea, 0, 0, 40, centrado_en=(1205, 396 + (k - (len(lineas) - 1) / 2) * 44))
        nombre = jugador_act.nombre if jugador_act else ""
        tema.texto_figma(p, f"Turno de ‘{nombre}’", 0, 0, 40, centrado_en=(1205, 552))
        if not partida.dado and jugador_act and not tema.es_bot(jugador_act):
            tema.texto_figma(p, "Hacé clic en tu dado", 0, 0, 30, (255, 240, 150), centrado_en=(1205, 610))

    def _partir_texto(self, texto, fuente, ancho_max):
        palabras, lineas, actual = texto.split(), [], ""
        for palabra in palabras:
            prueba = f"{actual} {palabra}".strip()
            if fuente.size(prueba)[0] <= ancho_max or not actual:
                actual = prueba
            else:
                lineas.append(actual)
                actual = palabra
        if actual:
            lineas.append(actual)
        return lineas

    def _dibujar_puntos_dado(self, r, val):
        cx, cy = r.center
        d = r.width * 0.25
        radio = max(3, int(r.width * (0.22 if val == 1 else 0.09)))
        coords = []
        if val in (1, 3, 5):
            coords.append((cx, cy))
        if val in (2, 3, 4, 5, 6):
            coords += [(cx - d, cy - d), (cx + d, cy + d)]
        if val in (4, 5, 6):
            coords += [(cx + d, cy - d), (cx - d, cy + d)]
        if val == 6:
            coords += [(cx - d, cy), (cx + d, cy)]
        for px, py in coords:
            pygame.draw.circle(self.pantalla, tema.NEGRO, (int(px), int(py)), radio)

    def manejar_evento(self, evento):
        partida = self.gestor.partidaActual
        if not partida:
            return

        jugador_act = partida.obtenerJugadorActual()
        es_humano = jugador_act and not tema.es_bot(jugador_act)

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos

            if hasattr(self, 'btn_reglas_inst') and self.btn_reglas_inst.es_cliqueado(evento):
                self.interfaz.pantalla_reglas.abrir()
                self.interfaz.ir_a("REGLAS")

            elif hasattr(self, 'btn_pausa_inst') and self.btn_pausa_inst.es_cliqueado(evento):
                self.gestor.pausarPartida()
                self.interfaz.ir_a("PAUSA")

            elif self.btn_lanzar.collidepoint(pos) and es_humano and not partida.dado and not self.animando_dado:
                self.animando_dado = True
                self.frames_anim_dado = 12

            elif es_humano and partida.dado and not self.animando_dado:
                movimientos_validos = partida.obtenerMovimientosValidos()
                for ficha in movimientos_validos:
                    px, py, _ = self.posiciones_fichas_anim.get(ficha, (0, 0, 0))
                    distancia = math.hypot(pos[0] - px, pos[1] - py)
                    if distancia <= (self.tam_celda * 0.6):
                        self._jugar_ficha(ficha)
                        break
