"""
Modulo menu_principal.py
Dibuja e interactúa con el Menú Principal del juego Ludo.
Incluye animaciones de partículas en segundo plano, soporte para pantalla completa,
tarjetas con estilo glassmorphism y diseño ultramoderno.
"""

import math
import random
import pygame


class MenuPrincipal:

    def __init__(self, pantalla, gestor_partida, persistencia, interfaz_padre=None):
        self.pantalla = pantalla
        self.gestor = gestor_partida
        self.persistencia = persistencia
        self.interfaz_padre = interfaz_padre

        self.fuente_titulo = pygame.font.SysFont("Arial", 54, bold=True)
        self.fuente_subtitulo = pygame.font.SysFont("Arial", 20)
        self.fuente_boton = pygame.font.SysFont("Arial", 22, bold=True)

        # Inicialización de partículas flotantes animadas de fondo
        self.particulas_fondo = []
        for _ in range(45):
            self.particulas_fondo.append({
                "x": random.randint(0, 1920),
                "y": random.randint(0, 1080),
                "vx": random.uniform(-0.5, 0.5),
                "vy": random.uniform(-0.8, -0.2),
                "tam": random.randint(4, 10),
                "color": random.choice([
                    (220, 50, 50, 80), (40, 120, 220, 80), (40, 180, 80, 80), (240, 190, 40, 80)
                ]),
                "angulo": random.uniform(0, 360)
            })

    def dibujar(self):
        ancho, alto = self.pantalla.get_size()
        self.pantalla.fill((12, 18, 30))  # Fondo oscuro profundo

        # Dibuja partículas animadas de fondo
        self._dibujar_particulas_fondo(ancho, alto)

        # Tarjeta central con sombra (Glassmorphism)
        w_card, h_card = 480, 560
        rect_card = pygame.Rect((ancho - w_card) // 2, (alto - h_card) // 2, w_card, h_card)
        pygame.draw.rect(self.pantalla, (22, 32, 52), rect_card, border_radius=20)
        pygame.draw.rect(self.pantalla, (50, 75, 115), rect_card, width=2, border_radius=20)

        # Título principal con brillo
        txt_titulo = self.fuente_titulo.render("JUEGO LUDO", True, (255, 255, 255))
        rect_titulo = txt_titulo.get_rect(center=(ancho // 2, rect_card.y + 60))
        self.pantalla.blit(txt_titulo, rect_titulo)

        txt_sub = self.fuente_subtitulo.render("Edición Ultramoderna con Bots & Animaciones", True, (170, 200, 235))
        rect_sub = txt_sub.get_rect(center=(ancho // 2, rect_card.y + 110))
        self.pantalla.blit(txt_sub, rect_sub)

        # Botones de navegación
        pos_y_base = rect_card.y + 160
        ancho_boton, alto_boton = 360, 54
        pos_x = (ancho - ancho_boton) // 2

        self.btn_nueva = pygame.Rect(pos_x, pos_y_base, ancho_boton, alto_boton)
        self.btn_reanudar = pygame.Rect(pos_x, pos_y_base + 75, ancho_boton, alto_boton)
        self.btn_reglas = pygame.Rect(pos_x, pos_y_base + 150, ancho_boton, alto_boton)
        self.btn_fullscreen = pygame.Rect(pos_x, pos_y_base + 225, ancho_boton, alto_boton)
        self.btn_salir = pygame.Rect(pos_x, pos_y_base + 300, ancho_boton, alto_boton)

        pos_mouse = pygame.mouse.get_pos()

        # Botón Nueva Partida
        self._dibujar_boton(self.btn_nueva, "NUEVA PARTIDA", (40, 180, 80), pos_mouse)

        # Botón Reanudar Partida
        tiene_guardada = self.persistencia.existe_partida_guardada()
        color_reanudar = (40, 120, 220) if tiene_guardada else (80, 95, 120)
        self._dibujar_boton(self.btn_reanudar, "REANUDAR PARTIDA", color_reanudar, pos_mouse, habilitado=tiene_guardada)

        # Botón Reglas
        self._dibujar_boton(self.btn_reglas, "REGLAS", (240, 160, 40), pos_mouse)

        # Botón Pantalla Completa
        es_fs = self.interfaz_padre and self.interfaz_padre.pantalla_completa
        txt_fs = "⛶ PANTALLA COMPLETA (F11)" if not es_fs else "⛶ MODO VENTANA (F11)"
        self._dibujar_boton(self.btn_fullscreen, txt_fs, (140, 80, 200), pos_mouse)

        # Botón Salir
        self._dibujar_boton(self.btn_salir, "SALIR", (220, 60, 60), pos_mouse)

        # Mensajes de estado / error
        if self.gestor.mensaje_error:
            fuente_err = pygame.font.SysFont("Arial", 16, bold=True)
            txt_err = fuente_err.render(self.gestor.mensaje_error, True, (255, 100, 100))
            rect_err = txt_err.get_rect(center=(ancho // 2, rect_card.bottom - 25))
            self.pantalla.blit(txt_err, rect_err)

    def _dibujar_particulas_fondo(self, ancho, alto):
        for p in self.particulas_fondo:
            p["x"] += p["vx"]
            p["y"] += p["vy"]

            if p["y"] < -20:
                p["y"] = alto + 20
                p["x"] = random.randint(0, ancho)

            # Dibujar partícula con un brillo suave
            s = pygame.Surface((p["tam"] * 2, p["tam"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, p["color"], (p["tam"], p["tam"]), p["tam"])
            self.pantalla.blit(s, (int(p["x"]), int(p["y"])))

    def _dibujar_boton(self, rect, texto, color_base, pos_mouse, habilitado=True):
        hover = rect.collidepoint(pos_mouse) and habilitado
        color = (min(color_base[0] + 35, 255), min(color_base[1] + 35, 255), min(color_base[2] + 35, 255)) if hover else color_base

        # Si hay hover se aplica una elevación suave
        rect_dibujo = rect.move(0, -3) if hover else rect
        pygame.draw.rect(self.pantalla, color, rect_dibujo, border_radius=12)
        pygame.draw.rect(self.pantalla, (255, 255, 255), rect_dibujo, width=2, border_radius=12)

        txt_surf = self.fuente_boton.render(texto, True, (255, 255, 255) if habilitado else (160, 160, 160))
        rect_txt = txt_surf.get_rect(center=rect_dibujo.center)
        self.pantalla.blit(txt_surf, rect_txt)

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos
            if self.btn_nueva.collidepoint(pos):
                self.gestor.mensaje_error = ""
                self.gestor.estado = "CONFIGURACION"
            elif self.btn_reanudar.collidepoint(pos) and self.persistencia.existe_partida_guardada():
                partida, msg = self.persistencia.cargarPartida()
                if partida:
                    self.gestor.partidaActual = partida
                    self.gestor.estado = "JUEGO"
                    self.gestor.mensaje_error = ""
                else:
                    self.gestor.mensaje_error = msg
            elif self.btn_reglas.collidepoint(pos):
                self.gestor.consultarReglas()
            elif self.btn_fullscreen.collidepoint(pos) and self.interfaz_padre:
                self.interfaz_padre.toggle_pantalla_completa()
            elif self.btn_salir.collidepoint(pos):
                pygame.quit()
                exit()
