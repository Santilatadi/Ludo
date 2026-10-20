"""
Modulo menu_principal.py
Dibuja e interactúa con el Menú Principal del juego Ludo.
Fielmente adaptado al diseño de Figma:
- Fondo rosa/lila vibrante
- Logo 'L U D O' con círculos plateados/blancos, bordes de color y letras coloreadas
- 3 botones con relleno azul, borde rojo llamativo y tipografía en dos líneas delineada
- Ilustración 3D con dados y tablero
"""

import os
import math
import pygame


class MenuPrincipal:

    def __init__(self, pantalla, gestor_partida, persistencia, interfaz_padre=None):
        self.pantalla = pantalla
        self.gestor = gestor_partida
        self.persistencia = persistencia
        self.interfaz_padre = interfaz_padre

        # Carga de tipografía personalizada
        ruta_fuente = "assets/font.ttf"
        if os.path.exists(ruta_fuente):
            self.fuente_logo = pygame.font.Font(ruta_fuente, 52)
            self.fuente_boton = pygame.font.Font(ruta_fuente, 24)
            self.fuente_sub = pygame.font.Font(ruta_fuente, 16)
        else:
            self.fuente_logo = pygame.font.SysFont("Impact", 50, bold=True)
            self.fuente_boton = pygame.font.SysFont("Arial", 22, bold=True)
            self.fuente_sub = pygame.font.SysFont("Arial", 16, bold=True)

        # Cargar ilustración de fondo de dados y tablero si existe
        self.img_artwork = None
        ruta_art = "assets/ludo_artwork.png"
        if os.path.exists(ruta_art):
            try:
                self.img_artwork = pygame.image.load(ruta_art).convert_alpha()
            except Exception:
                self.img_artwork = None

        self.ticks = 0
        self.hover_prev = {}

    def _render_texto_delineado(self, texto, fuente, color_texto, color_borde=(0, 0, 0), grosor=2):
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
        self.ticks += 1
        ancho, alto = self.pantalla.get_size()

        # Canvas de fondo violeta según diseño en Figma
        self.pantalla.fill((46, 21, 90))

        # 1. Logo L U D O (Círculos con fondo plata/blanco y letras/bordes de color)
        pos_y_logo = int(alto * 0.19)
        self._dibujar_logo_ludo(int(ancho * 0.45), pos_y_logo)

        # 2. Botones de menú a la izquierda (3 botones exactamente como Figma)
        w_btn = int(min(270, ancho * 0.28))
        h_btn = int(min(68, alto * 0.12))
        pos_x_btn = max(50, int(ancho * 0.08))
        pos_y_base = int(alto * 0.38)
        espaciado = h_btn + 22

        self.btn_nueva = pygame.Rect(pos_x_btn, pos_y_base, w_btn, h_btn)
        self.btn_continuar = pygame.Rect(pos_x_btn, pos_y_base + espaciado, w_btn, h_btn)
        self.btn_salir = pygame.Rect(pos_x_btn, pos_y_base + espaciado * 2, w_btn, h_btn)

        pos_m = pygame.mouse.get_pos()
        self._dibujar_boton_dos_lineas(self.btn_nueva, "NUEVA", "PARTIDA", pos_m)
        self._dibujar_boton_dos_lineas(self.btn_continuar, "CONTINUAR", "PARTIDA", pos_m)
        self._dibujar_boton_dos_lineas(self.btn_salir, "SALIR AL", "ESCRITORIO", pos_m)

        # 3. Ilustración 3D a la derecha (Tablero y dados)
        if self.img_artwork:
            w_target = int(min(ancho * 0.46, 460))
            h_target = int(w_target * (764 / 1024))
            img_scaled = pygame.transform.smoothscale(self.img_artwork, (w_target, h_target))
            pos_x_art = ancho - w_target - max(30, int(ancho * 0.05))
            pos_y_art = (alto - h_target) // 2 + 35 + math.sin(self.ticks * 0.04) * 4.0
            self.pantalla.blit(img_scaled, (pos_x_art, pos_y_art))

        # Mensaje de error si existe
        if self.gestor.mensaje_error:
            txt_err = self._render_texto_delineado(self.gestor.mensaje_error, self.fuente_sub, (255, 100, 100), (0, 0, 0), 2)
            self.pantalla.blit(txt_err, txt_err.get_rect(center=(ancho // 2, alto - 25)))

    def _dibujar_logo_ludo(self, cx, cy):
        letras = [
            ('L', (65, 95, 249)),
            ('U', (254, 15, 15)),
            ('D', (10, 201, 16)),
            ('O', (198, 194, 18))
        ]
        t_radius = 34
        spacing = 76
        total_w = len(letras) * spacing
        start_x = cx - total_w // 2 + spacing // 2

        for i, (letra, col) in enumerate(letras):
            px = start_x + i * spacing
            py = cy + math.sin(self.ticks * 0.05 + i * 0.5) * 3.0

            # Círculo interior blanco/plateado
            pygame.draw.circle(self.pantalla, (217, 217, 217), (int(px), int(py)), t_radius)
            # Borde exterior de color grueso
            pygame.draw.circle(self.pantalla, col, (int(px), int(py)), t_radius, width=4)

            # Letra coloreada
            txt = self.fuente_logo.render(letra, True, col)
            self.pantalla.blit(txt, txt.get_rect(center=(int(px), int(py))))

    def _dibujar_boton_dos_lineas(self, rect, linea1, linea2, pos_mouse):
        hover = rect.collidepoint(pos_mouse)
        clave = f"{linea1}_{linea2}"
        self.hover_prev[clave] = hover

        # Relleno azul con elevación sutil en hover
        color_bg = (32, 68, 175) if hover else (22, 48, 140)
        pygame.draw.rect(self.pantalla, color_bg, rect, border_radius=4)
        # Borde rojo intenso
        pygame.draw.rect(self.pantalla, (213, 27, 27), rect, width=4, border_radius=4)

        # Texto en dos líneas con borde negro delineado
        txt_s1 = self._render_texto_delineado(linea1, self.fuente_boton, (255, 255, 255), (0, 0, 0), 2)
        txt_s2 = self._render_texto_delineado(linea2, self.fuente_boton, (255, 255, 255), (0, 0, 0), 2)

        total_h = txt_s1.get_height() + txt_s2.get_height() + 2
        y_start = rect.centery - total_h // 2

        rect_t1 = txt_s1.get_rect(centerx=rect.centerx, top=y_start)
        rect_t2 = txt_s2.get_rect(centerx=rect.centerx, top=rect_t1.bottom + 2)

        self.pantalla.blit(txt_s1, rect_t1)
        self.pantalla.blit(txt_s2, rect_t2)

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos
            if self.btn_nueva.collidepoint(pos):
                self.gestor.mensaje_error = ""
                self.gestor.estado = "CONFIGURACION"
            elif self.btn_continuar.collidepoint(pos):
                self.gestor.mensaje_error = ""
                self.gestor.estado = "CONTINUAR"
            elif self.btn_salir.collidepoint(pos):
                pygame.quit()
                exit()
