"""
Modulo pantalla_reglas.py
Dibuja e interactúa con la Pantalla de Reglas del Ludo (CU-06).
Muestra las reglas de forma clara y permite regresar al estado anterior.
"""

import pygame
from logica.reglas import Reglas


class PantallaReglas:

    def __init__(self, pantalla, gestor_partida):
        self.pantalla = pantalla
        self.gestor = gestor_partida
        self.fuente_titulo = pygame.font.SysFont("Arial", 36, bold=True)
        self.fuente_texto = pygame.font.SysFont("Arial", 18)
        self.fuente_boton = pygame.font.SysFont("Arial", 22, bold=True)

    def dibujar(self):
        self.pantalla.fill((20, 28, 45))
        ancho, alto = self.pantalla.get_size()

        # Título
        txt_tit = self.fuente_titulo.render("REGLAS DEL JUEGO LUDO", True, (255, 220, 40))
        self.pantalla.blit(txt_tit, txt_tit.get_rect(center=(ancho // 2, 50)))

        # Cuadro contenedor de texto
        rect_box = pygame.Rect(60, 95, ancho - 120, alto - 180)
        pygame.draw.rect(self.pantalla, (30, 40, 60), rect_box, border_radius=12)
        pygame.draw.rect(self.pantalla, (70, 90, 130), rect_box, width=2, border_radius=12)

        # Renderizar líneas de texto de las reglas
        lineas = Reglas.obtener_texto_reglas()
        pos_y = rect_box.y + 20
        for linea in lineas:
            es_titulo_seccion = linea and linea[0].isdigit()
            color = (255, 200, 80) if es_titulo_seccion else (230, 235, 245)
            fuente = pygame.font.SysFont("Arial", 19, bold=True) if es_titulo_seccion else self.fuente_texto

            txt_linea = fuente.render(linea, True, color)
            self.pantalla.blit(txt_linea, (rect_box.x + 25, pos_y))
            pos_y += 24

        # Botón Volver
        self.btn_volver = pygame.Rect((ancho - 180) // 2, alto - 70, 180, 48)
        pos_m = pygame.mouse.get_pos()
        hover = self.btn_volver.collidepoint(pos_m)
        color_btn = (230, 70, 70) if hover else (200, 50, 50)

        pygame.draw.rect(self.pantalla, color_btn, self.btn_volver, border_radius=10)
        pygame.draw.rect(self.pantalla, (255, 255, 255), self.btn_volver, width=2, border_radius=10)
        txt_v = self.fuente_boton.render("VOLVER", True, (255, 255, 255))
        self.pantalla.blit(txt_v, txt_v.get_rect(center=self.btn_volver.center))

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.btn_volver.collidepoint(evento.pos):
                self.gestor.volverDeReglas()
