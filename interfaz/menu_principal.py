"""
Modulo menu_principal.py
Frame "Menu Principal" del Figma: logo L U D O en cuatro círculos, tres botones con
degradé azul y borde rojo, y la ilustración del tablero con los dados.
"""

import sys

import pygame

from interfaz import tema
from interfaz.componentes import BotonFigma

# (letra, círculo x, y, color del borde, color de la letra) — frame "Menu Principal"
LOGO = [("L", 403, 157, (66, 103, 254), (65, 95, 249)), ("U", 572, 154, (255, 4, 4), (250, 23, 27)),
        ("D", 741, 154, (9, 201, 15), (9, 201, 15)), ("O", 902, 157, (235, 229, 35), (180, 175, 14))]


class MenuPrincipal:

    def __init__(self, pantalla, game_manager, interfaz_padre=None):
        self.pantalla = pantalla
        self.gestor = game_manager
        self.interfaz_padre = interfaz_padre
        self.mensaje_error = ""
        self.btn_nueva = self.btn_continuar = self.btn_salir = pygame.Rect(0, 0, 0, 0)

    def _boton(self, y, texto):
        return BotonFigma(self.pantalla, (98, y, 474, 141), texto, tema.GRADIENTE, tema.ROJO_BORDE, 4,
                          tam_texto=48, alinear="izquierda", margen_texto=37)

    def dibujar(self):
        p = self.pantalla
        p.fill(tema.FONDO)

        # Logo: círculos #d9d9d9 con borde de color y letras Fredoka One
        for letra, x, y, borde, color in LOGO:
            r = tema.R(p, x, y, 135, 135)
            pygame.draw.ellipse(p, tema.GRIS, r)
            pygame.draw.ellipse(p, borde, r, width=tema.T(p, 4))
            tema.texto(p, letra, tema.T(p, 110), r.center, color=color, familia="fredoka")

        # Botones
        self.boton_nueva = self._boton(367, "NUEVA\nPARTIDA")
        self.boton_continuar = self._boton(554, "CONTINUAR\nPARTIDA")
        self.boton_salir = self._boton(741, "SALIR AL\nESCRITORIO")
        for boton in (self.boton_nueva, self.boton_continuar, self.boton_salir):
            boton.dibujar(p)
        self.btn_nueva = self.boton_nueva.rect_base
        self.btn_continuar = self.boton_continuar.rect_base
        self.btn_salir = self.boton_salir.rect_base

        # Ilustración del tablero y los dados
        r = tema.R(p, 741, 367, 613, 613)
        p.blit(tema.imagen("menu_ludo.png", r.size), r.topleft)

        if self.mensaje_error:
            tema.texto_figma(p, self.mensaje_error, 0, 0, 30, (255, 120, 120), tema.NEGRO, 4,
                             centrado_en=(720, 320))

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos
            if self.btn_nueva.collidepoint(pos):
                # CU-01 (DS N1): el GameManager crea la partida que se va a configurar
                self.mensaje_error = ""
                self.gestor.iniciarPartida()
                self.interfaz_padre.pantalla_config.reiniciar_formulario()
                self.interfaz_padre.ir_a("CONFIGURACION")
            elif self.btn_continuar.collidepoint(pos):
                # CU-14: se muestran las partidas guardadas para elegir cuál continuar
                continuar = self.interfaz_padre.pantalla_continuar
                continuar.abrir()
                if continuar.partidas:
                    self.mensaje_error = ""
                    self.interfaz_padre.ir_a("CONTINUAR")
                else:
                    self.mensaje_error = "No existe ninguna partida guardada."
            elif self.btn_salir.collidepoint(pos):
                pygame.quit()
                sys.exit()
