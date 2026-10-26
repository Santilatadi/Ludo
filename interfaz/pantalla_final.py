"""
Modulo pantalla_final.py
Frame "Menu Victoria" del Figma (CU-13): ventana oliva con borde amarillo, cartel rojo
"¡VICTORIA!", el nombre del ganador y los botones Reiniciar Partida y Volver al Menu.
"""

# Importa pygame para la renderización de la interfaz
import pygame

# Importa las funciones y constantes de diseño visual
from interfaz import tema
# Importa la clase BotonFigma para crear los botones de victoria
from interfaz.componentes import BotonFigma
# Importa SistemaParticulas para generar el efecto de confeti
from interfaz.efectos import SistemaParticulas


# Representa la pantalla de victoria que aparece al ganar la partida
class PantallaFinal:

    # Constructor: inicializa pantalla, gestor, interfaz y sistema de confeti
    def __init__(self, pantalla, game_manager, interfaz=None):
        # Superficie de la ventana donde se dibuja
        self.pantalla = pantalla
        # Referencia al GameManager
        self.gestor = game_manager
        # Referencia al controlador de pantallas principal
        self.interfaz = interfaz
        # Crea el sistema de partículas para el confeti
        self.particulas = SistemaParticulas()
        # Desactiva las luces de fondo para esta ventana
        self.particulas.orbes_fondo = []
        # Bandera que indica si ya se disparó la explosión de confeti
        self.confeti_emitido = False

    # Dibuja la ventana emergente de victoria, el confeti y los botones
    def dibujar(self):
        p = self.pantalla
        # Si aún no se lanzó el confeti, dispara una lluvia de 140 papelitos de colores
        if not self.confeti_emitido:
            self.confeti_emitido = True
            self.particulas.emitir_confeti(*tema.P(p, 696, 300), 140)

        # Dibuja el marco de fondo oliva con esquinas redondeadas y borde amarillo
        tema.panel_figma(p, 296, 235, 800, 657, (75, 67, 0, 242), (253, 245, 32), 10, radio=40)
        # Dibuja la placa roja superior para el título
        tema.panel_figma(p, 373, 270, 694, 113, (213, 27, 27), (253, 245, 32), 4, radio=40)
        # Escribe el texto "¡VICTORIA!" con letras grandes y borde amarillo
        tema.texto_figma(p, "¡VICTORIA!", 0, 0, 64, contorno=(253, 245, 32), trazo=4, centrado_en=(725, 327.5))
        # Dibuja una línea horizontal negra de separación
        tema.linea_figma(p, 300, 402, 796, tema.NEGRO, 4)

        # Obtiene la partida actual para conocer el ganador
        partida = self.gestor.partidaActual
        # Obtiene el nombre del jugador ganador
        nombre = partida.ganador.nombre if (partida and partida.ganador) else "Jugador 1"
        # Muestra el nombre del ganador en amarillo brillante
        tema.texto_figma(p, f"¡{nombre}!", 0, 0, 48, (253, 245, 32), (242, 120, 6), 10, centrado_en=(708, 453.5))
        # Muestra el texto "¡ HA GANADO LA PARTIDA!"
        tema.texto_figma(p, "¡ HA GANADO LA PARTIDA!", 0, 0, 48, centrado_en=(721, 528))

        # Crea el botón verde de "Reiniciar Partida"
        self.btn_reiniciar_inst = BotonFigma(p, (465, 651, 485, 85), "Reiniciar Partida", (41, 173, 37),
                                             (253, 245, 32), 4, tam_texto=48)
        # Crea el botón azul de "Volver al Menu"
        self.btn_menu_inst = BotonFigma(p, (465, 755, 485, 94), "Volver al Menu", (27, 54, 192),
                                        (253, 245, 32), 4, tam_texto=48)
        # Dibuja ambos botones en pantalla
        self.btn_reiniciar_inst.dibujar(p)
        self.btn_menu_inst.dibujar(p)
        # Actualiza y dibuja las partículas de confeti cayendo
        self.particulas.actualizar_y_dibujar(p)

    # Procesa los clics en los botones de victoria
    def manejar_evento(self, evento):
        # Si el evento no es presionar el mouse, no hace nada
        if evento.type != pygame.MOUSEBUTTONDOWN:
            return
        # Si se hace clic en "Reiniciar Partida":
        if hasattr(self, 'btn_reiniciar_inst') and self.btn_reiniciar_inst.es_cliqueado(evento):
            # Restablece la bandera de confeti
            self.confeti_emitido = False
            # Reinicia la partida en el gestor
            self.gestor.reiniciarPartida()
            # Reinicia el formulario de configuración
            self.interfaz.pantalla_config.reiniciar_formulario()
            # Pasa a la pantalla de CONFIGURACION
            self.interfaz.ir_a("CONFIGURACION")
        # Si se hace clic en "Volver al Menu":
        elif hasattr(self, 'btn_menu_inst') and self.btn_menu_inst.es_cliqueado(evento):
            # Restablece la bandera de confeti
            self.confeti_emitido = False
            # Cancela la partida activa
            self.gestor.cancelarPartida()
            # Regresa a la pantalla del MENU
            self.interfaz.ir_a("MENU")


# - __init__(): prepara la pantalla y crea el sistema de partículas.
# - dibujar(): muestra la ventana con el cartel "¡VICTORIA!", el nombre del ganador, los botones y confeti.
# - manejar_evento(): detecta si se presiona "Reiniciar Partida" o "Volver al Menu".
#En resumen: se ejecuta cuando termina la partida y muestra los botones para continuar o volver al inicio.
