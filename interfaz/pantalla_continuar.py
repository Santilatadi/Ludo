"""
Modulo pantalla_continuar.py
Frame "Continuar Partida" del Figma (CU-14): lista de partidas guardadas, con el
tiempo jugado y los jugadores de cada una en su color. Se muestran tres filas a la
vez (barra de desplazamiento a la derecha); se elige una y se retoma con INICIAR.
"""

import pygame

from interfaz import tema
from interfaz.componentes import BotonFigma, BotonModerno

FILAS_Y = (257, 410, 563)       # filas del Figma (1076x153)


class PantallaContinuar:

    def __init__(self, pantalla, game_manager, interfaz=None):
        self.pantalla = pantalla
        self.gestor = game_manager
        self.interfaz = interfaz
        self.partidas = []
        self.seleccion = 0
        self.desplazamiento = 0
        self.rects_filas = []
        self.mensaje_error = ""

    def abrir(self):
        # CU-14: se recorren las partidas guardadas con reanudarPartidaGuardada(numero)
        # (0 = la más reciente) y se anota lo que muestra cada fila del Figma.
        actual = self.gestor.partidaActual
        self.partidas = []
        numero = 0
        while self.gestor.reanudarPartidaGuardada(numero)[0]:
            partida = self.gestor.partidaActual
            self.partidas.append({"tiempoTranscurrido": int(partida.tiempoTranscurrido),
                                  "jugadores": [(j.nombre, j.getColor()) for j in partida.jugadores]})
            numero += 1
        self.gestor.partidaActual = actual
        self.seleccion = 0
        self.desplazamiento = 0
        self.mensaje_error = ""

    def dibujar(self):
        p = self.pantalla
        p.fill(tema.FONDO)
        tema.panel_figma(p, 111, 88, 1220, 805, tema.GRADIENTE, tema.ROJO_BORDE, 4)
        tema.texto_figma(p, "CONTINUAR PARTIDA", 0, 0, 90, contorno=tema.NEGRO, trazo=4, centrado_en=(723, 168))
        r = tema.R(p, 183, 217, 1081, 16)
        pygame.draw.rect(p, tema.GRIS, r, border_radius=r.height // 2)
        pygame.draw.rect(p, tema.NEGRO, r, width=tema.T(p, 4), border_radius=r.height // 2)

        # Filas con las partidas guardadas
        self.rects_filas = []
        for k, y in enumerate(FILAS_Y):
            i = self.desplazamiento + k
            fila = tema.R(p, 188, y, 1076, 153)
            pygame.draw.rect(p, tema.BLANCO, fila)
            elegida = i == self.seleccion and i < len(self.partidas)
            pygame.draw.rect(p, tema.AMARILLO if elegida else tema.NEGRO, fila, width=tema.T(p, 10 if elegida else 6))
            if i >= len(self.partidas):
                continue
            self.rects_filas.append((fila, i))
            datos = self.partidas[i]
            seg = datos["tiempoTranscurrido"]
            tema.texto_figma(p, f"Tiempo Jugado:  {seg // 60:02d}:{seg % 60:02d}", 219, y + 33, 40)
            x = tema.texto_figma(p, "JUGADORES:", 218, y + 92, 40).right + tema.T(p, 24)
            for nombre, color in datos["jugadores"]:
                surf = tema.render_texto(nombre, tema.T(p, 32), tema.COLOR_NOMBRE.get(color, tema.BLANCO),
                                         tema.NEGRO, tema.T(p, 2))
                rect = surf.get_rect(midleft=(x, tema.P(p, 0, y + 92 + 27)[1]))
                p.blit(surf, rect)
                x = rect.right + tema.T(p, 20)

        # Barra de desplazamiento del Figma
        pista = tema.R(p, 1284, 257, 22, 459)
        pygame.draw.rect(p, tema.NEGRO, pista, border_radius=pista.width // 2)
        total = max(len(self.partidas), len(FILAS_Y))
        alto = max(tema.T(p, 60), int(pista.height * len(FILAS_Y) / total))
        y0 = pista.y + int((pista.height - alto) * (self.desplazamiento / max(1, total - len(FILAS_Y))))
        barra = pygame.Rect(pista.x + tema.T(p, 5), y0 + tema.T(p, 4), pista.width - tema.T(p, 9), alto - tema.T(p, 8))
        pygame.draw.rect(p, tema.BLANCO, barra, border_radius=barra.width // 2)

        self.btn_iniciar_inst = BotonFigma(p, (475, 750, 491, 115), "INICIAR", tema.GRADIENTE_INICIAR, tema.NEGRO,
                                           4, tam_texto=96)
        self.btn_iniciar_inst.dibujar(p)

        # Volver al menú (también con Escape)
        self.btn_volver_inst = BotonModerno(tema.R(p, 1260, 98, 60, 60), "X", color_base=tema.ROJO_BORDE,
                                            color_hover=(255, 60, 60), color_borde=tema.NEGRO,
                                            fuente=tema.fuente(tema.T(p, 36)))
        self.btn_volver_inst.dibujar(p)

        if self.mensaje_error:
            tema.texto_figma(p, self.mensaje_error, 0, 0, 28, (255, 120, 120), tema.NEGRO, 4,
                             centrado_en=(720, 735))

    def _volver(self):
        self.interfaz.ir_a("MENU")

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if hasattr(self, "btn_iniciar_inst") and self.btn_iniciar_inst.es_cliqueado(evento):
                if not self.partidas:
                    self.mensaje_error = "No existe ninguna partida guardada."
                    return
                # CU-14: se carga la partida elegida y se retoma desde donde quedó
                exito, mensaje = self.gestor.reanudarPartidaGuardada(self.seleccion)
                if exito:
                    self.gestor.reanudarPartida()
                    self.interfaz.ir_a("JUEGO")
                else:
                    self.mensaje_error = mensaje
            elif hasattr(self, "btn_volver_inst") and self.btn_volver_inst.es_cliqueado(evento):
                self._volver()
            else:
                for fila, i in self.rects_filas:
                    if fila.collidepoint(evento.pos):
                        self.seleccion = i
                        self.mensaje_error = ""
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button in (4, 5):
            paso = -1 if evento.button == 4 else 1
            self.desplazamiento = max(0, min(len(self.partidas) - len(FILAS_Y), self.desplazamiento + paso))
        elif evento.type == pygame.MOUSEWHEEL:
            self.desplazamiento = max(0, min(len(self.partidas) - len(FILAS_Y), self.desplazamiento - evento.y))
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                self._volver()
            elif evento.key in (pygame.K_UP, pygame.K_DOWN) and self.partidas:
                self.seleccion = max(0, min(len(self.partidas) - 1,
                                            self.seleccion + (1 if evento.key == pygame.K_DOWN else -1)))
                if self.seleccion < self.desplazamiento:
                    self.desplazamiento = self.seleccion
                elif self.seleccion >= self.desplazamiento + len(FILAS_Y):
                    self.desplazamiento = self.seleccion - len(FILAS_Y) + 1
