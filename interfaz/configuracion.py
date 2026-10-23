"""
Modulo configuracion.py
Dibuja e interactúa con la Pantalla de Configuración de Nueva Partida.
Sigue el frame "Configuracion Nueva Partida" del Figma: cantidad de jugadores (CU-02),
nombres y tipo de cada jugador (CU-03) y elección de color con las flechas (CU-04).
"""

import os
import sys
import pygame

directorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if directorio_raiz not in sys.path:
    sys.path.insert(0, directorio_raiz)

from modelos.color import Color
from interfaz import tema
from interfaz.componentes import BotonModerno, BotonFigma


class PantallaConfiguracion:

    def __init__(self, pantalla, game_manager, interfaz=None):
        self.pantalla = pantalla
        self.gestor = game_manager
        self.interfaz = interfaz
        self.reiniciar_formulario()

    def reiniciar_formulario(self):
        # Valores iniciales de la pantalla (nueva partida o reinicio, CU-11)
        self.cant_jugadores = 2
        self.es_bot_lista = [False, True, True, True]
        self.nombres = ["Jugador 1", "Bot 2", "Bot 3", "Bot 4"]
        self.colores = [Color.ROJO, Color.VERDE, Color.AZUL, Color.AMARILLO]   # orden del Figma
        self.campo_activo = None
        self.mensaje_error = ""

        self.ticks = 0

    def _sincronizar_partida(self):
        # CU-01 y CU-02: la partida en configuración del GameManager tiene la cantidad de
        # jugadores y el color de cada uno que muestra la pantalla.
        partida = self.gestor.partidaActual
        if partida is None or partida.estado != "CONFIGURACION":
            self.gestor.iniciarPartida()
            partida = self.gestor.partidaActual
        if partida.numeroJugadores() == self.cant_jugadores:
            return
        self.gestor.configurarCantidadJugadores(self.cant_jugadores)
        for i in range(self.cant_jugadores):
            exito, _ = self.gestor.seleccionarColor(self.colores[i], i)
            if not exito:
                self.colores[i] = self.gestor.seleccionarColores()[0]
                self.gestor.seleccionarColor(self.colores[i], i)

    def dibujar(self):
        # Frame "Configuracion Nueva Partida" del Figma
        self.ticks += 1
        self._sincronizar_partida()
        p = self.pantalla
        pos_m = pygame.mouse.get_pos()

        p.fill(tema.FONDO)
        tema.panel_figma(p, 111, 88, 1220, 805, tema.GRADIENTE, tema.ROJO_BORDE, 4)
        tema.texto_figma(p, "NUEVA PARTIDA", 0, 0, 96, contorno=(255, 251, 0), trazo=4, centrado_en=(721, 172))
        barra = tema.R(p, 282, 217, 878, 16)
        pygame.draw.rect(p, tema.GRIS, barra, border_radius=barra.height // 2)
        pygame.draw.rect(p, tema.NEGRO, barra, width=tema.T(p, 4), border_radius=barra.height // 2)

        # CU-02: cantidad de jugadores ("-" y "+" rojos a los lados del número)
        tema.texto_figma(p, "Cantidad", 183, 312, 36)
        tema.texto_figma(p, "Jugadores", 183, 350, 36)
        self.btn_menos_inst = BotonModerno(tema.R(p, 438, 302, 52, 70), "-")
        self.btn_mas_inst = BotonModerno(tema.R(p, 615, 302, 56, 70), "+")
        for boton, cx in ((self.btn_menos_inst, 463.5), (self.btn_mas_inst, 642.5)):
            claro = boton.rect_base.collidepoint(pos_m)
            tema.texto_figma(p, boton.texto, 0, 0, 64, (255, 90, 90) if claro else tema.ROJO_TEXTO, tema.NEGRO, 2,
                             centrado_en=(cx, 337))
        cantidad = tema.R(p, 505, 306, 94, 66)
        pygame.draw.rect(p, tema.GRIS, cantidad, border_radius=cantidad.height // 2)
        pygame.draw.rect(p, tema.NEGRO, cantidad, width=tema.T(p, 4), border_radius=cantidad.height // 2)
        tema.texto_figma(p, str(self.cant_jugadores), 0, 0, 64, tema.ROJO_TEXTO, tema.NEGRO, 2, centrado_en=(552, 339))

        # CU-03 y CU-04: un renglón por jugador con su nombre; el borde es su color
        tema.texto_figma(p, "Jugadores", 183, 429, 48)
        self.rects_nombres = []
        self.rects_arrow_left = []
        self.rects_arrow_right = []
        self.rects_tipo = []
        posiciones = [(300, 523), (824, 523), (300, 645), (824, 645)]
        for i in range(self.cant_jugadores):
            fx, fy = posiciones[i]
            col = tema.COLOR_JUGADOR.get(self.colores[i], tema.BLANCO)
            pildora = tema.R(p, fx, fy, 327, 61)
            self.rects_nombres.append(pildora)
            pygame.draw.rect(p, tema.BLANCO, pildora, border_radius=pildora.height // 2)
            pygame.draw.rect(p, col, pildora, width=tema.T(p, 5), border_radius=pildora.height // 2)

            # Flechas grises: cambian el color del jugador (CU-04)
            izq, der = tema.R(p, fx - 33, fy + 15, 24, 30), tema.R(p, fx + 336, fy + 15, 24, 30)
            self.rects_arrow_left.append(izq)
            self.rects_arrow_right.append(der)
            for r, derecha in ((izq, False), (der, True)):
                tema.flecha(p, r, derecha, (255, 251, 120) if r.collidepoint(pos_m) else tema.GRIS, tema.NEGRO,
                            tema.T(p, 4))

            # Nombre sobre la línea; "BOT" a la izquierda si lo controla la consola (CU-03 C)
            nombre = self.nombres[i] + ("|" if self.campo_activo == i and self.ticks % 60 < 30 else "")
            tema.texto_figma(p, nombre, 0, 0, 30, (30, 30, 40), None, centrado_en=(fx + 166, fy + 30))
            pygame.draw.line(p, tema.NEGRO, tema.P(p, fx + 30, fy + 53), tema.P(p, fx + 301, fy + 53), tema.T(p, 4))
            tipo = tema.R(p, fx + 12, fy + 14, 52, 30)
            self.rects_tipo.append(tipo)
            if self.es_bot_lista[i] or tipo.collidepoint(pos_m):
                pygame.draw.rect(p, (60, 60, 80) if self.es_bot_lista[i] else tema.GRIS, tipo,
                                 border_radius=tipo.height // 2)
                tema.texto(p, "BOT", tema.T(p, 20), tipo.center,
                           color=tema.BLANCO if self.es_bot_lista[i] else (90, 90, 110))

        if self.mensaje_error:
            tema.texto_figma(p, self.mensaje_error, 0, 0, 28, (255, 230, 230), tema.ROJO_BORDE, 4,
                             centrado_en=(721, 268))

        self.btn_iniciar_inst = BotonFigma(p, (475, 750, 491, 115), "INICIAR", tema.GRADIENTE_INICIAR, tema.NEGRO, 4,
                                           tam_texto=96)
        self.btn_iniciar_inst.dibujar(p)

        # Cancelar la configuración y volver al menú (CU-01 A y CU-04 B); también con Escape
        self.btn_volver_inst = BotonModerno(tema.R(p, 1260, 98, 60, 60), "X", color_base=tema.ROJO_BORDE,
                                            color_hover=(255, 60, 60), color_borde=tema.NEGRO,
                                            fuente=tema.fuente(tema.T(p, 36)))
        self.btn_volver_inst.dibujar(p)

    def _cambiar_color(self, i, paso):
        # CU-04: las flechas recorren los colores y se asigna el siguiente disponible.
        orden = list(Color)
        disponibles = self.gestor.seleccionarColores()
        actual = orden.index(self.colores[i]) if self.colores[i] in orden else 0
        for k in range(1, len(orden)):
            candidato = orden[(actual + paso * k) % len(orden)]
            if candidato in disponibles:
                exito, mensaje = self.gestor.seleccionarColor(candidato, i)
                if exito:
                    self.colores[i] = candidato
                self.mensaje_error = "" if exito else mensaje
                return
        # CU-04, alternativa A: no queda ningún otro color libre
        self.mensaje_error = "No hay otro color disponible: todos están asignados."

    def _alternar_bot(self, i):
        self.es_bot_lista[i] = not self.es_bot_lista[i]
        if self.es_bot_lista[i]:
            self.nombres[i] = f"Bot {i + 1}"
        elif self.nombres[i].startswith("Bot"):
            self.nombres[i] = f"Jugador {i + 1}"
        self.mensaje_error = ""

    def manejar_evento(self, evento):

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos

            # CU-02: la cantidad la valida el GameManager (mínimo 2, máximo 4)
            cambio = 0
            if hasattr(self, 'btn_menos_inst') and self.btn_menos_inst.es_cliqueado(evento):
                cambio = -1
            elif hasattr(self, 'btn_mas_inst') and self.btn_mas_inst.es_cliqueado(evento):
                cambio = 1
            if cambio:
                self._sincronizar_partida()
                exito, mensaje = self.gestor.configurarCantidadJugadores(self.cant_jugadores + cambio)
                self.mensaje_error = "" if exito else mensaje
                if exito:
                    self.cant_jugadores += cambio
                    if cambio > 0:
                        # El jugador nuevo recibe un color libre (lo puede cambiar con las flechas)
                        nuevo = self.cant_jugadores - 1
                        exito, _ = self.gestor.seleccionarColor(self.colores[nuevo], nuevo)
                        if not exito:
                            self.colores[nuevo] = self.gestor.seleccionarColores()[0]
                            self.gestor.seleccionarColor(self.colores[nuevo], nuevo)
                return

            # CU-04: las flechas de cada píldora cambian el color del jugador
            for i, r_l in enumerate(self.rects_arrow_left):
                if r_l.collidepoint(pos):
                    self._cambiar_color(i, -1)
                    return
            for i, r_r in enumerate(self.rects_arrow_right):
                if r_r.collidepoint(pos):
                    self._cambiar_color(i, 1)
                    return

            # Etiqueta BOT/HUM: alterna entre jugador humano y bot
            for i, r_t in enumerate(getattr(self, "rects_tipo", [])):
                if r_t.collidepoint(pos):
                    self._alternar_bot(i)
                    return

            self.campo_activo = None
            for idx, r_nom in enumerate(self.rects_nombres):
                if r_nom.collidepoint(pos):
                    self.campo_activo = idx
                    break

            if hasattr(self, 'btn_iniciar_inst') and self.btn_iniciar_inst.es_cliqueado(evento):
                self._crear_y_comenzar_partida()

            elif hasattr(self, 'btn_volver_inst') and self.btn_volver_inst.es_cliqueado(evento):
                # CU-01 y CU-04, alternativa cancelar: se descartan los datos y se vuelve al menú
                self.mensaje_error = ""
                self.gestor.cancelarSeleccionColores()
                self.interfaz.ir_a("MENU")

        elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE and self.campo_activo is None:
            self.mensaje_error = ""
            self.gestor.cancelarSeleccionColores()
            self.interfaz.ir_a("MENU")

        elif evento.type == pygame.KEYDOWN and self.campo_activo is not None:
            idx = self.campo_activo
            if evento.key == pygame.K_BACKSPACE:
                self.nombres[idx] = self.nombres[idx][:-1]
            elif evento.key in (pygame.K_RETURN, pygame.K_TAB):
                self.campo_activo = None
            else:
                if len(self.nombres[idx]) < 12 and evento.unicode.isprintable():
                    self.nombres[idx] += evento.unicode

    def _crear_y_comenzar_partida(self):
        # DS N1: se configura una partida nueva con la cantidad, los nombres (CU-03) y los
        # colores (CU-04) de la pantalla; DS N5: el GameManager la valida e inicia.
        self.gestor.cancelarPartida()
        self.gestor.iniciarPartida()
        self.gestor.configurarCantidadJugadores(self.cant_jugadores)
        for i in range(self.cant_jugadores):
            exito, mensaje = self.gestor.registrarNombre(None if self.es_bot_lista[i] else self.nombres[i], i)
            if exito:
                exito, mensaje = self.gestor.seleccionarColor(self.colores[i], i)
            if not exito:
                self.mensaje_error = mensaje
                return

        exito, mensaje = self.gestor.iniciarPartida()
        self.mensaje_error = "" if exito else mensaje
        if exito:
            self.interfaz.ir_a("JUEGO")
