"""
Modulo pantalla_final.py
Frame "Menu Victoria" del Figma (CU-13): ventana oliva con borde amarillo, cartel rojo
"¡VICTORIA!", el nombre del ganador y los botones Reiniciar Partida y Volver al Menu.
"""

import pygame

from interfaz import tema
from interfaz.componentes import BotonFigma
from interfaz.efectos import SistemaParticulas


class PantallaFinal:

    def __init__(self, pantalla, game_manager, interfaz=None):
        self.pantalla = pantalla
        self.gestor = game_manager
        self.interfaz = interfaz
        self.particulas = SistemaParticulas()
        self.particulas.orbes_fondo = []
        self.confeti_emitido = False

    def dibujar(self):
        p = self.pantalla
        if not self.confeti_emitido:
            self.confeti_emitido = True
            self.particulas.emitir_confeti(*tema.P(p, 696, 300), 140)

        tema.panel_figma(p, 296, 235, 800, 657, (75, 67, 0, 242), (253, 245, 32), 10, radio=40)
        tema.panel_figma(p, 373, 270, 694, 113, (213, 27, 27), (253, 245, 32), 4, radio=40)
        tema.texto_figma(p, "¡VICTORIA!", 0, 0, 64, contorno=(253, 245, 32), trazo=4, centrado_en=(725, 327.5))
        tema.linea_figma(p, 300, 402, 796, tema.NEGRO, 4)

        partida = self.gestor.partidaActual
        nombre = partida.ganador.nombre if (partida and partida.ganador) else "Jugador 1"
        tema.texto_figma(p, f"¡{nombre}!", 0, 0, 48, (253, 245, 32), (242, 120, 6), 10, centrado_en=(708, 453.5))
        tema.texto_figma(p, "¡ HA GANADO LA PARTIDA!", 0, 0, 48, centrado_en=(721, 528))

        self.btn_reiniciar_inst = BotonFigma(p, (465, 651, 485, 85), "Reiniciar Partida", (41, 173, 37),
                                             (253, 245, 32), 4, tam_texto=48)
        self.btn_menu_inst = BotonFigma(p, (465, 755, 485, 94), "Volver al Menu", (27, 54, 192),
                                        (253, 245, 32), 4, tam_texto=48)
        self.btn_reiniciar_inst.dibujar(p)
        self.btn_menu_inst.dibujar(p)
        self.particulas.actualizar_y_dibujar(p)

    def manejar_evento(self, evento):
        if evento.type != pygame.MOUSEBUTTONDOWN:
            return
        if hasattr(self, 'btn_reiniciar_inst') and self.btn_reiniciar_inst.es_cliqueado(evento):
            self.confeti_emitido = False
            self.gestor.reiniciarPartida()
            self.interfaz.pantalla_config.reiniciar_formulario()
            self.interfaz.ir_a("CONFIGURACION")
        elif hasattr(self, 'btn_menu_inst') and self.btn_menu_inst.es_cliqueado(evento):
            self.confeti_emitido = False
            self.gestor.cancelarPartida()
            self.interfaz.ir_a("MENU")
