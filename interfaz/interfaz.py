"""
Modulo interfaz.py
Manejador principal de la Interfaz Gráfica del Ludo con Pygame.
Inicializa la ventana adaptativa, controla el reloj (60 FPS), administra
el modo Pantalla Completa (Fullscreen / Redimensionable con F11) y redirige eventos.
"""

# Importa pygame para la ventana y los gráficos
import pygame
# Importa GameManager para coordinar la lógica
from logica.game_manager import GameManager
# Importa la pantalla del Menú Principal
from interfaz.menu_principal import MenuPrincipal
# Importa la pantalla de Configuración de partida
from interfaz.configuracion import PantallaConfiguracion
# Importa la pantalla de Continuar partida guardada
from interfaz.pantalla_continuar import PantallaContinuar
# Importa la pantalla de Juego del tablero
from interfaz.pantalla_juego import PantallaJuego
# Importa la pantalla de Pausa
from interfaz.pantalla_pausa import PantallaPausa
# Importa la pantalla de Reglas del juego
from interfaz.pantalla_reglas import PantallaReglas
# Importa la pantalla de Estadísticas
from interfaz.pantalla_estadisticas import PantallaEstadisticas
# Importa la pantalla de Final de partida (Victoria)
from interfaz.pantalla_final import PantallaFinal
# Importa el sistema de partículas y efectos visuales
from interfaz.efectos import SistemaParticulas


# Clase principal que administra la ventana y el flujo entre pantallas
class InterfazGrafica:

    # Constructor: inicializa Pygame, la ventana, el reloj y todas las pantallas
    def __init__(self, ancho=1024, alto=720):
        # Inicializa todos los módulos internos de Pygame
        pygame.init()
        # Establece el título de la ventana
        pygame.display.set_caption("Ludo Imperial 3D - Edición Moderna")

        # Guarda el ancho por defecto de la ventana
        self.ancho_defecto = ancho
        # Guarda el alto por defecto de la ventana
        self.alto_defecto = alto
        # Bandera que indica si está en modo pantalla completa
        self.pantalla_completa = False

        # Crea la ventana con soporte para redimensionar (arrastrar bordes)
        self.pantalla = pygame.display.set_mode((ancho, alto), pygame.RESIZABLE)
        # Reloj para controlar los fotogramas por segundo (FPS)
        self.reloj = pygame.time.Clock()
        # Bandera que mantiene corriendo el bucle del juego
        self.ejecutando = True

        # Crea el sistema de partículas para efectos especiales
        self.particulas = SistemaParticulas()

        # Crea la instancia del gestor de lógica
        self.gestor = GameManager()

        # Pantalla que se muestra: la navegación es responsabilidad de la vista,
        # el GameManager solo resuelve las acciones del jugador.
        # Estado actual de la pantalla que se está mostrando
        self.estado = "MENU"
        # Estado anterior para saber a dónde volver
        self.estado_anterior = "MENU"

        # Instancia cada una de las pantallas pasándoles la ventana y el gestor
        self.menu_principal = MenuPrincipal(self.pantalla, self.gestor, self)
        self.pantalla_config = PantallaConfiguracion(self.pantalla, self.gestor, self)
        self.pantalla_continuar = PantallaContinuar(self.pantalla, self.gestor, self)
        self.pantalla_juego = PantallaJuego(self.pantalla, self.gestor, self)
        self.pantalla_pausa = PantallaPausa(self.pantalla, self.gestor, self)
        self.pantalla_reglas = PantallaReglas(self.pantalla, self.gestor, self)
        self.pantalla_stats = PantallaEstadisticas(self.pantalla, self.gestor, self)
        self.pantalla_final = PantallaFinal(self.pantalla, self.gestor, self)

    # Cambia la pantalla actual recordando cuál era la anterior
    def ir_a(self, estado):
        """Cambia de pantalla recordando la anterior (para volver de Reglas y Estadísticas)."""
        # Guarda el estado actual en el anterior
        self.estado_anterior = self.estado
        # Cambia al nuevo estado
        self.estado = estado

    # Alterna entre el modo de pantalla completa y modo ventana
    def toggle_pantalla_completa(self):
        # Invierte el valor booleano
        self.pantalla_completa = not self.pantalla_completa
        # Si activa pantalla completa:
        if self.pantalla_completa:
            self.pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        # Si desactiva, vuelve al tamaño de ventana por defecto
        else:
            self.pantalla = pygame.display.set_mode((self.ancho_defecto, self.alto_defecto), pygame.RESIZABLE)

        # Actualiza la referencia de la pantalla en todas las subclases
        self._actualizar_referencias_pantalla()

    # Pasa la nueva superficie de pantalla a cada submódulo cuando cambia de tamaño
    def _actualizar_referencias_pantalla(self):
        self.menu_principal.pantalla = self.pantalla
        self.pantalla_config.pantalla = self.pantalla
        self.pantalla_continuar.pantalla = self.pantalla
        self.pantalla_juego.pantalla = self.pantalla
        self.pantalla_pausa.pantalla = self.pantalla
        self.pantalla_reglas.pantalla = self.pantalla
        self.pantalla_stats.pantalla = self.pantalla
        self.pantalla_final.pantalla = self.pantalla

    # Bucle principal que mantiene funcionando el juego a 60 FPS
    def ejecutar(self):
        # Mientras ejecutando sea True:
        while self.ejecutando:
            # Procesa entradas del usuario (teclado, mouse, cerrar)
            self._procesar_eventos()
            # Dibuja la pantalla correspondiente al estado actual
            self._actualizar_y_dibujar()
            # Actualiza la imagen en el monitor
            pygame.display.flip()
            # Espera el tiempo necesario para mantener 60 fotogramas por segundo
            self.reloj.tick(60)

        # Cierra Pygame al salir del bucle
        pygame.quit()

    # Recibe los eventos de Pygame y se los envía a la pantalla activa
    def _procesar_eventos(self):
        # Recorre la cola de eventos producidos por el usuario
        for evento in pygame.event.get():
            # Si hace clic en la cruz de la ventana de Windows/Mac:
            if evento.type == pygame.QUIT:
                # Detiene el bucle principal
                self.ejecutando = False
                return

            # Tecla F11 para cambiar a pantalla completa:
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_F11:
                    self.toggle_pantalla_completa()

            # Evento cuando el usuario cambia el tamaño de la ventana arrastrando el borde:
            elif evento.type == pygame.VIDEORESIZE and not self.pantalla_completa:
                self.pantalla = pygame.display.set_mode((evento.w, evento.h), pygame.RESIZABLE)
                self._actualizar_referencias_pantalla()

            # Obtiene el estado actual de la interfaz
            estado = self.estado

            # Reenvía el evento a la pantalla que corresponda:
            if estado == "MENU":
                self.menu_principal.manejar_evento(evento)
            elif estado == "CONFIGURACION":
                self.pantalla_config.manejar_evento(evento)
            elif estado == "CONTINUAR":
                self.pantalla_continuar.manejar_evento(evento)
            elif estado == "JUEGO":
                self.pantalla_juego.manejar_evento(evento)
            elif estado == "PAUSA":
                self.pantalla_pausa.manejar_evento(evento)
            elif estado == "REGLAS":
                self.pantalla_reglas.manejar_evento(evento)
            elif estado == "ESTADISTICAS":
                self.pantalla_stats.manejar_evento(evento)
            elif estado == "FINAL":
                self.pantalla_final.manejar_evento(evento)

    # Limpia la pantalla y dibuja los componentes según el estado actual
    def _actualizar_y_dibujar(self):
        # Pinta el fondo oscuro general
        self.pantalla.fill((46, 21, 90))
        estado = self.estado

        # Llama al método dibujar() de la pantalla activa:
        if estado == "MENU":
            self.menu_principal.dibujar()
        elif estado == "CONFIGURACION":
            self.pantalla_config.dibujar()
        elif estado == "CONTINUAR":
            self.pantalla_continuar.dibujar()
        elif estado == "JUEGO":
            self.pantalla_juego.dibujar()
        elif estado == "PAUSA":
            self.pantalla_juego.dibujar()
            self.pantalla_pausa.dibujar()
        elif estado == "REGLAS":
            if self.estado_anterior in ("JUEGO", "PAUSA", "FINAL"):
                self.pantalla_juego.dibujar()
            self.pantalla_reglas.dibujar()
        elif estado == "ESTADISTICAS":
            if self.estado_anterior in ("JUEGO", "PAUSA", "FINAL"):
                self.pantalla_juego.dibujar()
            self.pantalla_stats.dibujar()
        elif estado == "FINAL":
            self.pantalla_juego.dibujar()
            self.pantalla_final.dibujar()


#ir_a(): cambia de pantalla.
#toggle_pantalla_completa(): activa/desactiva pantalla completa.
#_actualizar_referencias_pantalla(): actualiza la pantalla cuando cambia de tamaño la ventana.
#ejecutar(): bucle principal que procesa eventos, actualiza y dibuja (mantiene el juego funcionando a 60 FPS.).
#_procesar_eventos(): detecta los clics, las teclas y el cierre de la ventana
#_actualizar_y_dibujar(): muestra la pantalla que corresponde según el estado del juego.
