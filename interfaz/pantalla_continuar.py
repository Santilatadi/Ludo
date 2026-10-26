"""
Modulo pantalla_continuar.py
Frame "Continuar Partida" del Figma (CU-14): lista de partidas guardadas, con el
tiempo jugado y los jugadores de cada una en su color. Se muestran tres filas a la
vez (barra de desplazamiento a la derecha); se elige una y se retoma con INICIAR.
"""

# Importa pygame para la renderización y eventos
import pygame

# Importa el módulo tema con estilos, colores y fuentes
from interfaz import tema
# Importa los componentes de botones interactivos
from interfaz.componentes import BotonFigma, BotonModerno

# Posiciones verticales (Y) de las 3 tarjetas de partidas en la pantalla
FILAS_Y = (257, 410, 563)       # filas del Figma (1076x153)


# Representa la pantalla para seleccionar y continuar una partida guardada
class PantallaContinuar:

    # Constructor: inicializa pantalla, gestor y variables de la lista de partidas
    def __init__(self, pantalla, game_manager, interfaz=None):
        # Superficie de la ventana donde se dibuja
        self.pantalla = pantalla
        # Referencia al gestor GameManager
        self.gestor = game_manager
        # Referencia al controlador de pantallas principal
        self.interfaz = interfaz
        # Lista con la información de las partidas guardadas encontradas
        self.partidas = []
        # Índice de la partida seleccionada actualmente
        self.seleccion = 0
        # Desplazamiento de la lista (scroll de filas)
        self.desplazamiento = 0
        # Áreas rectangulares de las filas visibles para detectar clics
        self.rects_filas = []
        # Mensaje de error para mostrar al usuario
        self.mensaje_error = ""

    # Abre la pantalla y lee todas las partidas guardadas en el disco
    def abrir(self):
        # CU-14: se recorren las partidas guardadas con reanudarPartidaGuardada(numero)
        # (0 = la más reciente) y se anota lo que muestra cada fila del Figma.
        # Guarda la partida activa actual para no sobrescribirla
        actual = self.gestor.partidaActual
        # Vacía la lista
        self.partidas = []
        numero = 0
        # Va cargando una a una las partidas guardadas hasta que no haya más
        while self.gestor.reanudarPartidaGuardada(numero)[0]:
            partida = self.gestor.partidaActual
            # Añade los datos resumidos a la lista (tiempo y lista de jugadores con color)
            self.partidas.append({"tiempoTranscurrido": int(partida.tiempoTranscurrido),
                                  "jugadores": [(j.nombre, j.getColor()) for j in partida.jugadores]})
            numero += 1
        # Restaura la partida activa original
        self.gestor.partidaActual = actual
        # Selecciona la primera partida por defecto
        self.seleccion = 0
        # Reinicia el scroll
        self.desplazamiento = 0
        # Limpia errores anteriores
        self.mensaje_error = ""

    # Dibuja la lista de partidas, las tarjetas, la barra de scroll y el botón iniciar
    def dibujar(self):
        p = self.pantalla
        # Pinta el fondo general
        p.fill(tema.FONDO)
        # Dibuja el panel central azul con borde rojo
        tema.panel_figma(p, 111, 88, 1220, 805, tema.GRADIENTE, tema.ROJO_BORDE, 4)
        # Dibuja el título "CONTINUAR PARTIDA"
        tema.texto_figma(p, "CONTINUAR PARTIDA", 0, 0, 90, contorno=tema.NEGRO, trazo=4, centrado_en=(723, 168))
        # Dibuja una barra gris decorativa debajo del título
        r = tema.R(p, 183, 217, 1081, 16)
        pygame.draw.rect(p, tema.GRIS, r, border_radius=r.height // 2)
        pygame.draw.rect(p, tema.NEGRO, r, width=tema.T(p, 4), border_radius=r.height // 2)

        # Filas con las partidas guardadas
        self.rects_filas = []
        # Dibuja hasta 3 filas visibles a la vez
        for k, y in enumerate(FILAS_Y):
            i = self.desplazamiento + k
            fila = tema.R(p, 188, y, 1076, 153)
            # Rellena la tarjeta con color blanco
            pygame.draw.rect(p, tema.BLANCO, fila)
            # Determina si esta fila es la seleccionada por el usuario
            elegida = i == self.seleccion and i < len(self.partidas)
            # Dibuja el borde (amarillo grueso si está elegida, negro si no)
            pygame.draw.rect(p, tema.AMARILLO if elegida else tema.NEGRO, fila, width=tema.T(p, 10 if elegida else 6))
            # Si no hay partida para este casillero de la lista, salta a la siguiente
            if i >= len(self.partidas):
                continue
            # Guarda el rectángulo y el índice para detectar clics
            self.rects_filas.append((fila, i))
            datos = self.partidas[i]
            seg = datos["tiempoTranscurrido"]
            # Muestra el tiempo jugado en minutos y segundos
            tema.texto_figma(p, f"Tiempo Jugado:  {seg // 60:02d}:{seg % 60:02d}", 219, y + 33, 40)
            # Muestra la etiqueta "JUGADORES:"
            x = tema.texto_figma(p, "JUGADORES:", 218, y + 92, 40).right + tema.T(p, 24)
            # Muestra los nombres de los jugadores con sus respectivos colores
            for nombre, color in datos["jugadores"]:
                surf = tema.render_texto(nombre, tema.T(p, 32), tema.COLOR_NOMBRE.get(color, tema.BLANCO),
                                         tema.NEGRO, tema.T(p, 2))
                rect = surf.get_rect(midleft=(x, tema.P(p, 0, y + 92 + 27)[1]))
                p.blit(surf, rect)
                x = rect.right + tema.T(p, 20)

        # Barra de desplazamiento del Figma
        # Dibuja el carril negro de la barra de scroll
        pista = tema.R(p, 1284, 257, 22, 459)
        pygame.draw.rect(p, tema.NEGRO, pista, border_radius=pista.width // 2)
        total = max(len(self.partidas), len(FILAS_Y))
        alto = max(tema.T(p, 60), int(pista.height * len(FILAS_Y) / total))
        # Calcula la posición del indicador blanco según el scroll
        y0 = pista.y + int((pista.height - alto) * (self.desplazamiento / max(1, total - len(FILAS_Y))))
        barra = pygame.Rect(pista.x + tema.T(p, 5), y0 + tema.T(p, 4), pista.width - tema.T(p, 9), alto - tema.T(p, 8))
        pygame.draw.rect(p, tema.BLANCO, barra, border_radius=barra.width // 2)

        # Crea y dibuja el botón verde "INICIAR" para reanudar la partida seleccionada
        self.btn_iniciar_inst = BotonFigma(p, (475, 750, 491, 115), "INICIAR", tema.GRADIENTE_INICIAR, tema.NEGRO,
                                           4, tam_texto=96)
        self.btn_iniciar_inst.dibujar(p)

        # Volver al menú (también con Escape)
        # Botón rojo con una "X" en la esquina superior derecha
        self.btn_volver_inst = BotonModerno(tema.R(p, 1260, 98, 60, 60), "X", color_base=tema.ROJO_BORDE,
                                            color_hover=(255, 60, 60), color_borde=tema.NEGRO,
                                            fuente=tema.fuente(tema.T(p, 36)))
        self.btn_volver_inst.dibujar(p)

        # Muestra el mensaje de error si ocurrió algún problema
        if self.mensaje_error:
            tema.texto_figma(p, self.mensaje_error, 0, 0, 28, (255, 120, 120), tema.NEGRO, 4,
                             centrado_en=(720, 735))

    # Regresa al menú principal
    def _volver(self):
        self.interfaz.ir_a("MENU")

    # Procesa clics, rueda del mouse y flechas del teclado
    def manejar_evento(self, evento):
        # Clic izquierdo del mouse:
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            # Si presiona el botón INICIAR:
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
            # Si presiona el botón "X" de volver:
            elif hasattr(self, "btn_volver_inst") and self.btn_volver_inst.es_cliqueado(evento):
                self._volver()
            # Si hace clic sobre alguna fila de la lista:
            else:
                for fila, i in self.rects_filas:
                    if fila.collidepoint(evento.pos):
                        self.seleccion = i
                        self.mensaje_error = ""
        # Rueda del mouse (botones 4 y 5):
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button in (4, 5):
            paso = -1 if evento.button == 4 else 1
            self.desplazamiento = max(0, min(len(self.partidas) - len(FILAS_Y), self.desplazamiento + paso))
        # Evento nativo de rueda del mouse (touchpad o rueda moderna):
        elif evento.type == pygame.MOUSEWHEEL:
            self.desplazamiento = max(0, min(len(self.partidas) - len(FILAS_Y), self.desplazamiento - evento.y))
        # Teclado:
        elif evento.type == pygame.KEYDOWN:
            # ESC para volver
            if evento.key == pygame.K_ESCAPE:
                self._volver()
            # Flechas arriba y abajo para cambiar de partida seleccionada
            elif evento.key in (pygame.K_UP, pygame.K_DOWN) and self.partidas:
                self.seleccion = max(0, min(len(self.partidas) - 1,
                                            self.seleccion + (1 if evento.key == pygame.K_DOWN else -1)))
                # Ajusta el scroll si la selección sale de la vista
                if self.seleccion < self.desplazamiento:
                    self.desplazamiento = self.seleccion
                elif self.seleccion >= self.desplazamiento + len(FILAS_Y):
                    self.desplazamiento = self.seleccion - len(FILAS_Y) + 1


#- __init__(): prepara la pantalla.
#- abrir(): busca las partidas guardadas y las muestra en una lista.
#- dibujar(): muestra las partidas, el tiempo jugado y los jugadores.
#- _volver(): vuelve al menú principal.
#- manejar_evento(): detecta los clics y las teclas para seleccionar una partida, desplazarse por la lista, volver al menú o continuar jugando.
#En resumen: permite elegir una partida guardada y continuarla desde donde quedó.