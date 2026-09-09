"""
Modulo pantalla_final.py
Dibuja e interactúa con la Pantalla de Victoria / Finalización (CU-13).
Anuncia al ganador con una presentación festiva y ofrece opciones para reiniciar o volver al menú.
"""

import math
import random
import pygame


class PantallaFinal:

    def __init__(self, pantalla, gestor_partida):
        self.pantalla = pantalla
        self.gestor = gestor_partida
        self.fuente_titulo = pygame.font.SysFont("Arial", 48, bold=True)
        self.fuente_sub = pygame.font.SysFont("Arial", 28, bold=True)
        self.fuente_desc = pygame.font.SysFont("Arial", 20)
        self.fuente_boton = pygame.font.SysFont("Arial", 22, bold=True)

        # Generación de partículas de confeti animadas
        self.particulas = []
        for _ in range(70):
            self.particulas.append({
                "x": random.randint(0, 1024),
                "y": random.randint(-400, 0),
                "vx": random.uniform(-1, 1),
                "vy": random.uniform(2, 5),
                "color": random.choice([
                    (255, 60, 60), (60, 180, 255), (60, 230, 100), (255, 220, 40), (220, 80, 255)
                ]),
                "tam": random.randint(6, 12)
            })

    def dibujar(self):
        ancho, alto = self.pantalla.get_size()
        self.pantalla.fill((15, 22, 35))

        # Animación de confeti cayendo
        for p in self.particulas:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["y"] > alto:
                p["y"] = random.randint(-50, -10)
                p["x"] = random.randint(0, ancho)

            pygame.draw.circle(self.pantalla, p["color"], (int(p["x"]), int(p["y"])), p["tam"])

        # Cuadro de Victoria
        w_box, h_box = 520, 480
        rect_box = pygame.Rect((ancho - w_box) // 2, (alto - h_box) // 2, w_box, h_box)
        pygame.draw.rect(self.pantalla, (25, 35, 55), rect_box, border_radius=20)
        pygame.draw.rect(self.pantalla, (255, 215, 0), rect_box, width=4, border_radius=20)

        # Título y Trofeo
        txt_trofeo = self.fuente_titulo.render("🏆 VICTORIA 🏆", True, (255, 215, 0))
        self.pantalla.blit(txt_trofeo, txt_trofeo.get_rect(center=(ancho // 2, rect_box.y + 60)))

        # Nombre del Ganador
        partida = self.gestor.partidaActual
        nombre_ganador = partida.ganador.nombre if (partida and partida.ganador) else "Jugador"
        txt_gan = self.fuente_sub.render(f"¡{nombre_ganador.upper()} GANÓ!", True, (255, 255, 255))
        self.pantalla.blit(txt_gan, txt_gan.get_rect(center=(ancho // 2, rect_box.y + 130)))

        txt_desc = self.fuente_desc.render("Las 4 fichas llegaron con éxito a la meta.", True, (200, 220, 240))
        self.pantalla.blit(txt_desc, txt_desc.get_rect(center=(ancho // 2, rect_box.y + 180)))

        # Botones
        pos_y_base = rect_box.y + 240
        bw, bh = 320, 52
        bx = (ancho - bw) // 2

        self.btn_nueva = pygame.Rect(bx, pos_y_base, bw, bh)
        self.btn_stats = pygame.Rect(bx, pos_y_base + 70, bw, bh)
        self.btn_menu = pygame.Rect(bx, pos_y_base + 140, bw, bh)

        pos_m = pygame.mouse.get_pos()
        self._dibujar_boton(self.btn_nueva, "NUEVA PARTIDA", (40, 180, 80), pos_m)
        self._dibujar_boton(self.btn_stats, "ESTADÍSTICAS", (40, 120, 220), pos_m)
        self._dibujar_boton(self.btn_menu, "MENÚ PRINCIPAL", (200, 60, 60), pos_m)

    def _dibujar_boton(self, rect, texto, color_base, pos_mouse):
        hover = rect.collidepoint(pos_mouse)
        color = (min(color_base[0] + 30, 255), min(color_base[1] + 30, 255), min(color_base[2] + 30, 255)) if hover else color_base
        pygame.draw.rect(self.pantalla, color, rect, border_radius=12)
        pygame.draw.rect(self.pantalla, (255, 255, 255), rect, width=2, border_radius=12)
        txt = self.fuente_boton.render(texto, True, (255, 255, 255))
        self.pantalla.blit(txt, txt.get_rect(center=rect.center))

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos
            if self.btn_nueva.collidepoint(pos):
                self.gestor.estado = "CONFIGURACION"
            elif self.btn_stats.collidepoint(pos):
                self.gestor.consultarEstadisticas()
            elif self.btn_menu.collidepoint(pos):
                self.gestor.cancelarPartida()
