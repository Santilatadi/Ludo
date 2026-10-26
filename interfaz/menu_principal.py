"""
Modulo menu_principal.py
Frame "Menu Principal" del Figma: logo L U D O en cuatro círculos, tres botones con
degradé azul y borde rojo, y la ilustración del tablero con los dados.
"""

# Importa sys para cerrar el programa completamente con sys.exit()
import sys

# Importa pygame para la gestión de ventanas, eventos y gráficos
import pygame

# Importa el módulo tema con estilos, colores y fuentes
from interfaz import tema
# Importa la clase BotonFigma para crear los botones del menú
from interfaz.componentes import BotonFigma

# (letra, círculo x, y, color del borde, color de la letra) — frame "Menu Principal"
# Lista con la información de las 4 letras del logo LUDO y sus posiciones
LOGO = [("L", 403, 157, (66, 103, 254), (65, 95, 249)), ("U", 572, 154, (255, 4, 4), (250, 23, 27)),
        ("D", 741, 154, (9, 201, 15), (9, 201, 15)), ("O", 902, 157, (235, 229, 35), (180, 175, 14))]


# Representa la pantalla del Menú Principal del juego
class MenuPrincipal:

    # Constructor: inicializa pantalla, gestor de juego y variables de botones
    def __init__(self, pantalla, game_manager, interfaz_padre=None):
        # Superficie de la ventana donde se dibuja
        self.pantalla = pantalla
        # Referencia al GameManager
        self.gestor = game_manager
        # Referencia al controlador principal de pantallas (InterfazLudo)
        self.interfaz_padre = interfaz_padre
        # Mensaje de error a mostrar si falla alguna acción
        self.mensaje_error = ""
        # Rectángulos de los botones para detectar clics
        self.btn_nueva = self.btn_continuar = self.btn_salir = pygame.Rect(0, 0, 0, 0)

    # Función auxiliar para crear un botón con la posición Y y el texto indicados
    def _boton(self, y, texto):
        # Devuelve un BotonFigma con degradado azul y borde rojo
        return BotonFigma(self.pantalla, (98, y, 474, 141), texto, tema.GRADIENTE, tema.ROJO_BORDE, 4,
                          tam_texto=48, alinear="izquierda", margen_texto=37)

    # Dibuja todos los elementos visuales del menú principal
    def dibujar(self):
        # Asigna la pantalla a una variable corta p
        p = self.pantalla
        # Pinta el fondo con el color general
        p.fill(tema.FONDO)

        # Logo: círculos #d9d9d9 con borde de color y letras Fredoka One
        # Dibuja cada letra del logo LUDO dentro de su círculo
        for letra, x, y, borde, color in LOGO:
            # Escala las medidas del círculo al tamaño de la pantalla
            r = tema.R(p, x, y, 135, 135)
            # Rellena el círculo de color gris
            pygame.draw.ellipse(p, tema.GRIS, r)
            # Dibuja el borde de color alrededor del círculo
            pygame.draw.ellipse(p, borde, r, width=tema.T(p, 4))
            # Dibuja la letra centrada dentro del círculo
            tema.texto(p, letra, tema.T(p, 110), r.center, color=color, familia="fredoka")

        # Botones
        # Crea el botón de Nueva Partida
        self.boton_nueva = self._boton(367, "NUEVA\nPARTIDA")
        # Crea el botón de Continuar Partida
        self.boton_continuar = self._boton(554, "CONTINUAR\nPARTIDA")
        # Crea el botón de Salir al Escritorio
        self.boton_salir = self._boton(741, "SALIR AL\nESCRITORIO")
        # Dibuja cada uno de los 3 botones en la pantalla
        for boton in (self.boton_nueva, self.boton_continuar, self.boton_salir):
            boton.dibujar(p)
        # Guarda las áreas rectangulares para responder a los clics
        self.btn_nueva = self.boton_nueva.rect_base
        self.btn_continuar = self.boton_continuar.rect_base
        self.btn_salir = self.boton_salir.rect_base

        # Ilustración del tablero y los dados
        # Calcula el rectángulo de la imagen decorativa del Ludo
        r = tema.R(p, 741, 367, 613, 613)
        # Dibuja la imagen del tablero en la derecha
        p.blit(tema.imagen("menu_ludo.png", r.size), r.topleft)

        # Si hay un mensaje de error, lo dibuja en pantalla con color rojizo
        if self.mensaje_error:
            tema.texto_figma(p, self.mensaje_error, 0, 0, 30, (255, 120, 120), tema.NEGRO, 4,
                             centrado_en=(720, 320))

    # Procesa los eventos de teclado y mouse en el menú
    def manejar_evento(self, evento):
        # Detecta si se hizo clic izquierdo con el mouse
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            # Obtiene la posición (x, y) donde se hizo clic
            pos = evento.pos
            # Si se tocó el botón "Nueva Partida":
            if self.btn_nueva.collidepoint(pos):
                # CU-01 (DS N1): el GameManager crea la partida que se va a configurar
                # Limpia los errores anteriores
                self.mensaje_error = ""
                # Prepara la partida en el gestor
                self.gestor.iniciarPartida()
                # Reinicia los campos del formulario de configuración
                self.interfaz_padre.pantalla_config.reiniciar_formulario()
                # Cambia de pantalla a CONFIGURACION
                self.interfaz_padre.ir_a("CONFIGURACION")
            # Si se tocó el botón "Continuar Partida":
            elif self.btn_continuar.collidepoint(pos):
                # CU-14: se muestran las partidas guardadas para elegir cuál continuar
                # Obtiene la pantalla de continuar
                continuar = self.interfaz_padre.pantalla_continuar
                # Carga las partidas guardadas
                continuar.abrir()
                # Si hay partidas guardadas, va a la pantalla de continuación
                if continuar.partidas:
                    self.mensaje_error = ""
                    self.interfaz_padre.ir_a("CONTINUAR")
                # Si no hay partidas guardadas, muestra el aviso de error
                else:
                    self.mensaje_error = "No existe ninguna partida guardada."
            # Si se tocó el botón "Salir":
            elif self.btn_salir.collidepoint(pos):
                # Cierra la librería pygame
                pygame.quit()
                # Cierra la ejecución del programa
                sys.exit()



#- __init__(): prepara el menú principal.
#- _boton(): crea un botón con el diseño del juego.
#- dibujar(): muestra el logo, los botones y la imagen del tablero.
#- manejar_evento(): detecta qué botón toca el usuario:
#  - Nueva partida: empieza la configuración de una partida.
# - Continuar partida: permite elegir una partida guardada.
# - Salir al escritorio: cierra el juego.
#En resumen: este módulo muestra el menú principal y permite elegir qué hacer.