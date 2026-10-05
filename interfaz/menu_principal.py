"""
Modulo menu_principal.py
Dibuja e interactúa con el Menú Principal del juego Ludo.
Adaptado al 100% con la interfaz gráfica de Figma y recursos de imagen.
"""

import os
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
            self.fuente_logo = pygame.font.Font(ruta_fuente, 46)
            self.fuente_boton = pygame.font.Font(ruta_fuente, 20)
            self.fuente_sub = pygame.font.Font(ruta_fuente, 16)
        else:
            self.fuente_logo = pygame.font.SysFont("Impact", 44, bold=True)
            self.fuente_boton = pygame.font.SysFont("Arial", 20, bold=True)
            self.fuente_sub = pygame.font.SysFont("Arial", 16)

        # Cargar ilustración de fondo de dados y tablero si existe
        self.img_artwork = None
        ruta_art = "assets/ludo_artwork.png"
        if os.path.exists(ruta_art):
            try:
                self.img_artwork = pygame.image.load(ruta_art).convert_alpha()
            except Exception:
                self.img_artwork = None

    def _render_texto_delineado(self, texto, fuente, color_texto, color_borde=(0, 0, 0), grosor=1):
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
        ancho, alto = self.pantalla.get_size()
        # Canvas de fondo rosa / magenta exacto
        self.pantalla.fill((226, 120, 190))

        # 1. Logo L U D O en la parte superior central/izquierda
        self._dibujar_logo_ludo(ancho // 4 + 40, 80)

        # 2. Botones de menú a la izquierda
        w_btn, h_btn = 230, 50
        pos_x_btn = max(40, ancho // 10)
        pos_y_base = alto // 2 - 40

        self.btn_nueva = pygame.Rect(pos_x_btn, pos_y_base, w_btn, h_btn)
        self.btn_continuar = pygame.Rect(pos_x_btn, pos_y_base + 70, w_btn, h_btn)
        self.btn_salir = pygame.Rect(pos_x_btn, pos_y_base + 140, w_btn, h_btn)

        pos_m = pygame.mouse.get_pos()
        self._dibujar_boton_menu(self.btn_nueva, "NUEVA PARTIDA", pos_m)
        self._dibujar_boton_menu(self.btn_continuar, "CONTINUAR PARTIDA", pos_m)
        self._dibujar_boton_menu(self.btn_salir, "SALIR AL ESCRITORIO", pos_m)

        # 3. Ilustración 3D a la derecha
        if self.img_artwork:
            w_target = int(ancho * 0.46)
            h_target = int(w_target * (764 / 1024))
            img_scaled = pygame.transform.smoothscale(self.img_artwork, (w_target, h_target))
            pos_x_art = ancho - w_target - 30
            pos_y_art = (alto - h_target) // 2 + 30
            self.pantalla.blit(img_scaled, (pos_x_art, pos_y_art))

        # Mensaje de error si existe
        if self.gestor.mensaje_error:
            txt_err = self._render_texto_delineado(self.gestor.mensaje_error, self.fuente_sub, (255, 100, 100))
            self.pantalla.blit(txt_err, txt_err.get_rect(center=(ancho // 2, alto - 25)))

    def _dibujar_logo_ludo(self, cx, cy):
        letras = [('L', (40, 120, 220)), ('U', (220, 50, 50)), ('D', (40, 180, 80)), ('O', (190, 210, 40))]
        t_radius = 34
        spacing = 76
        total_w = len(letras) * spacing
        start_x = cx - total_w // 2 + spacing // 2

        # Recuadro azul celeste bordiando el logo
        rect_marco = pygame.Rect(cx - total_w // 2 - 15, cy - t_radius - 12, total_w + 30, t_radius * 2 + 24)
        pygame.draw.rect(self.pantalla, (80, 160, 240), rect_marco, width=2, border_radius=10)

        for i, (letra, col) in enumerate(letras):
            px = start_x + i * spacing
            pygame.draw.circle(self.pantalla, col, (px, cy), t_radius)
            pygame.draw.circle(self.pantalla, (255, 255, 255), (px, cy), t_radius, width=3)

            txt = self._render_texto_delineado(letra, self.fuente_logo, (255, 255, 255), (0, 0, 0), 2)
            self.pantalla.blit(txt, txt.get_rect(center=(px, cy)))

    def _dibujar_boton_menu(self, rect, texto, pos_mouse):
        hover = rect.collidepoint(pos_mouse)
        color = (25, 75, 175) if hover else (16, 50, 135)

        pygame.draw.rect(self.pantalla, color, rect, border_radius=6)
        pygame.draw.rect(self.pantalla, (20, 20, 20), rect, width=2, border_radius=6)

        txt_surf = self._render_texto_delineado(texto, self.fuente_boton, (255, 255, 255), (0, 0, 0), 2)
        self.pantalla.blit(txt_surf, txt_surf.get_rect(center=rect.center))

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
