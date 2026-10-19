"""
Modulo pantalla_continuar.py
Dibuja e interactúa con la Pantalla de Continuar Partida (Cargar partida guardada).
Adaptada con contenedores glassmorphism, insignias de jugadores y botones modernos interactivos.
"""

import os
import pygame
from interfaz.efectos import dibujar_panel_glassmorphism, dibujar_texto_glow
from interfaz.componentes import BotonModerno, BotonMute


class PantallaContinuar:

    def __init__(self, pantalla, gestor_partida, persistencia):
        self.pantalla = pantalla
        self.gestor = gestor_partida
        self.persistencia = persistencia

        ruta_fuente = "assets/font.ttf"
        if os.path.exists(ruta_fuente):
            self.fuente_titulo = pygame.font.Font(ruta_fuente, 34)
            self.fuente_sub = pygame.font.Font(ruta_fuente, 18)
            self.fuente_badge = pygame.font.Font(ruta_fuente, 14)
            self.fuente_boton = pygame.font.Font(ruta_fuente, 22)
        else:
            self.fuente_titulo = pygame.font.SysFont("Impact", 34, bold=True)
            self.fuente_sub = pygame.font.SysFont("Arial", 18, bold=True)
            self.fuente_badge = pygame.font.SysFont("Arial", 14, bold=True)
            self.fuente_boton = pygame.font.SysFont("Arial", 22, bold=True)

        self.mensaje_error = ""
        self.btn_mute = BotonMute(10, 10)
        self.indice_seleccionado = 0
        self.scroll_y = 0
        self.max_scroll = 0
        self.slots_rects = []
        self.partidas_actuales = []
        self.rect_box = None

    def dibujar(self):
        ancho, alto = self.pantalla.get_size()

        # Canvas de fondo violeta según diseño en Figma
        self.pantalla.fill((46, 21, 90))

        # Ventana modal Glassmorphism
        w_win, h_win = min(740, ancho - 40), min(540, alto - 50)
        rect_win = pygame.Rect((ancho - w_win) // 2, (alto - h_win) // 2, w_win, h_win)

        dibujar_panel_glassmorphism(
            self.pantalla, rect_win,
            color_bg=(16, 35, 95, 235),
            color_borde=(255, 215, 0, 220),
            radio=20, grosor_borde=3
        )

        # Título "PARTIDAS GUARDADAS"
        dibujar_texto_glow(
            self.pantalla, "PARTIDAS GUARDADAS", self.fuente_titulo,
            ancho // 2, rect_win.y + 45,
            color_texto=(255, 220, 0), color_resplandor=(0, 150, 255), centro=True
        )

        # Cuadro interior de lista de partidas Glassmorphism
        self.rect_box = pygame.Rect(rect_win.x + 30, rect_win.y + 82, w_win - 60, h_win - 165)
        dibujar_panel_glassmorphism(self.pantalla, self.rect_box, color_bg=(10, 25, 65, 200), color_borde=(255, 255, 255, 120), radio=12)

        self.partidas_actuales = self.persistencia.listar_partidas_guardadas()

        if self.partidas_actuales:
            if self.indice_seleccionado >= len(self.partidas_actuales):
                self.indice_seleccionado = max(0, len(self.partidas_actuales) - 1)

            h_slot = 84
            espacio_slot = 10
            total_alto = len(self.partidas_actuales) * (h_slot + espacio_slot) + 10
            self.max_scroll = max(0, total_alto - self.rect_box.height)
            self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

            # Aplicar recorte (clip) para no salirse del contenedor
            self.pantalla.set_clip(self.rect_box)

            self.slots_rects = []
            colors_map = {
                "ROJO": (220, 50, 50),
                "VERDE": (40, 180, 80),
                "AZUL": (40, 120, 220),
                "AMARILLO": (240, 190, 40)
            }

            ancho_slot = self.rect_box.width - 24 - (12 if self.max_scroll > 0 else 0)

            for idx, item in enumerate(self.partidas_actuales):
                y_pos = self.rect_box.y + 10 + idx * (h_slot + espacio_slot) - self.scroll_y
                slot_rect = pygame.Rect(self.rect_box.x + 12, y_pos, ancho_slot, h_slot)
                self.slots_rects.append((idx, slot_rect))

                # Renderizar únicamente si es visible dentro del clip
                if slot_rect.bottom < self.rect_box.top or slot_rect.top > self.rect_box.bottom:
                    continue

                es_sel = (idx == self.indice_seleccionado)
                col_bg = (28, 62, 145, 240) if es_sel else (16, 36, 92, 195)
                col_borde = (255, 215, 0, 255) if es_sel else (0, 180, 240, 150)
                grosor_borde = 3 if es_sel else 1

                dibujar_panel_glassmorphism(
                    self.pantalla, slot_rect,
                    color_bg=col_bg, color_borde=col_borde,
                    radio=10, grosor_borde=grosor_borde
                )

                # Encabezado del slot: Nombre y Fecha
                fecha = item.get("fecha", "")
                txt_titulo = self.fuente_sub.render(f"Partida #{idx + 1}  •  {fecha}", True, (255, 235, 100) if es_sel else (255, 255, 255))
                self.pantalla.blit(txt_titulo, (slot_rect.x + 14, slot_rect.y + 10))

                # Indicador de turno actual a la derecha
                jugadores_info = item.get("jugadores", [])
                turno_idx = item.get("turnoActual", 0)
                nom_turno = jugadores_info[turno_idx].get("nombre", f"J{turno_idx + 1}") if turno_idx < len(jugadores_info) else "Turno 1"
                txt_turno = self.fuente_badge.render(f"Turno de: {nom_turno}", True, (200, 230, 255))
                self.pantalla.blit(txt_turno, (slot_rect.right - txt_turno.get_width() - 14, slot_rect.y + 12))

                # Badges de los jugadores
                txt_lbl_j = self.fuente_badge.render("JUGADORES:", True, (255, 220, 0))
                self.pantalla.blit(txt_lbl_j, (slot_rect.x + 14, slot_rect.y + 46))

                pos_x_b = slot_rect.x + 105
                for j_data in jugadores_info:
                    nom = j_data.get("nombre", "Jugador")
                    col = colors_map.get(j_data.get("color"), (100, 100, 100))
                    icono = "(IA) " if j_data.get("es_bot") else ""
                    txt_b = self.fuente_badge.render(f"{icono}{nom}", True, (20, 20, 20) if j_data.get("color") == "AMARILLO" else (255, 255, 255))
                    bw = txt_b.get_width() + 12
                    rect_b = pygame.Rect(pos_x_b, slot_rect.y + 44, bw, 22)
                    pygame.draw.rect(self.pantalla, col, rect_b, border_radius=6)
                    pygame.draw.rect(self.pantalla, (0, 0, 0), rect_b, width=1, border_radius=6)
                    self.pantalla.blit(txt_b, (rect_b.x + 6, rect_b.y + 2))
                    pos_x_b += bw + 8

            # Barra de desplazamiento (Scrollbar) si hay muchas partidas
            if self.max_scroll > 0:
                bar_x = self.rect_box.right - 8
                bar_h = max(30, int(self.rect_box.height * (self.rect_box.height / total_alto)))
                bar_y = self.rect_box.y + int((self.scroll_y / self.max_scroll) * (self.rect_box.height - bar_h))
                pygame.draw.rect(self.pantalla, (255, 215, 0, 220), (bar_x, bar_y, 5, bar_h), border_radius=3)

            # Restablecer área de recorte
            self.pantalla.set_clip(None)

        else:
            self.slots_rects = []
            txt_empty = self.fuente_sub.render("No hay ninguna partida guardada actualmente.", True, (200, 220, 255))
            self.pantalla.blit(txt_empty, txt_empty.get_rect(center=self.rect_box.center))

        if self.mensaje_error:
            dibujar_texto_glow(
                self.pantalla, self.mensaje_error, self.fuente_sub,
                ancho // 2, rect_win.bottom - 75,
                color_texto=(255, 100, 100), color_resplandor=(255, 0, 0), centro=True
            )

        # Botones inferiores: CARGAR y ELIMINAR
        bw_cargar, bw_borrar = 210, 180
        espacio_btns = 20
        total_w_btns = bw_cargar + bw_borrar + espacio_btns
        x_base = (ancho - total_w_btns) // 2

        self.btn_iniciar_inst = BotonModerno(
            (x_base, rect_win.bottom - 60, bw_cargar, 46), "CARGAR",
            color_base=(30, 135, 60), color_hover=(45, 165, 75),
            color_borde=(255, 230, 0), fuente=self.fuente_boton, icono=""
        )
        self.btn_iniciar_inst.dibujar(self.pantalla)

        self.btn_eliminar_inst = BotonModerno(
            (x_base + bw_cargar + espacio_btns, rect_win.bottom - 60, bw_borrar, 46), "ELIMINAR",
            color_base=(190, 35, 45), color_hover=(220, 50, 60),
            color_borde=(255, 180, 180), fuente=self.fuente_boton, icono=""
        )
        self.btn_eliminar_inst.dibujar(self.pantalla)

        # Botón Volver (X)
        self.btn_volver_inst = BotonModerno(
            (rect_win.x + 20, rect_win.y + 15, 34, 34), "X",
            color_base=(200, 40, 50), fuente=self.fuente_sub
        )
        self.btn_volver_inst.dibujar(self.pantalla)

    def _cargar_seleccionada(self):
        if not self.partidas_actuales:
            self.mensaje_error = "No hay partidas guardadas para cargar."
            return

        if 0 <= self.indice_seleccionado < len(self.partidas_actuales):
            id_sel = self.partidas_actuales[self.indice_seleccionado]["id_partida"]
            partida = self.persistencia.cargarPartida(id_sel)
            if partida:
                self.gestor.partidaActual = partida
                self.gestor.estado = "JUEGO"
                self.mensaje_error = ""
            else:
                self.mensaje_error = "No se pudo cargar la partida seleccionada."
        else:
            self.mensaje_error = "Por favor selecciona una partida válida."

    def _eliminar_seleccionada(self):
        if not self.partidas_actuales:
            self.mensaje_error = "No hay partidas para eliminar."
            return

        if 0 <= self.indice_seleccionado < len(self.partidas_actuales):
            id_sel = self.partidas_actuales[self.indice_seleccionado]["id_partida"]
            exito, msg = self.persistencia.eliminarPartida(id_sel)
            if exito:
                self.mensaje_error = ""
                self.partidas_actuales = self.persistencia.listar_partidas_guardadas()
                if self.indice_seleccionado >= len(self.partidas_actuales):
                    self.indice_seleccionado = max(0, len(self.partidas_actuales) - 1)
            else:
                self.mensaje_error = msg

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEWHEEL:
            self.scroll_y = max(0, min(getattr(self, 'max_scroll', 0), self.scroll_y - evento.y * 35))

        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if hasattr(self, 'btn_iniciar_inst') and self.btn_iniciar_inst.es_cliqueado(evento):
                self._cargar_seleccionada()

            elif hasattr(self, 'btn_eliminar_inst') and self.btn_eliminar_inst.es_cliqueado(evento):
                self._eliminar_seleccionada()

            elif hasattr(self, 'btn_volver_inst') and self.btn_volver_inst.es_cliqueado(evento):
                self.gestor.estado = "MENU"

            elif self.rect_box and self.rect_box.collidepoint(evento.pos):
                for idx, slot_rect in self.slots_rects:
                    if slot_rect.collidepoint(evento.pos):
                        if self.indice_seleccionado == idx:
                            self._cargar_seleccionada()
                        else:
                            self.indice_seleccionado = idx
                        break
