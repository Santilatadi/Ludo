"""
Modulo interfaz.py
Manejador principal de la Interfaz Gráfica del Ludo con Pygame.
Inicializa la ventana adaptativa, controla el reloj (60 FPS), administra
el modo Pantalla Completa (Fullscreen / Redimensionable con F11) y redirige eventos.
"""

import pygame
from logica.gestor_partida import GestorPartida
from persistencia.persistencia import Persistencia
from interfaz.menu_principal import MenuPrincipal
from interfaz.configuracion import PantallaConfiguracion
from interfaz.pantalla_continuar import PantallaContinuar
from interfaz.pantalla_juego import PantallaJuego
from interfaz.pantalla_pausa import PantallaPausa
from interfaz.pantalla_reglas import PantallaReglas
from interfaz.pantalla_estadisticas import PantallaEstadisticas
from interfaz.pantalla_final import PantallaFinal


class InterfazGrafica:

    def __init__(self, ancho=1024, alto=720):
        pygame.init()
        pygame.display.set_caption("Juego Ludo")

        self.ancho_defecto = ancho
        self.alto_defecto = alto
        self.pantalla_completa = False

        self.pantalla = pygame.display.set_mode((ancho, alto), pygame.RESIZABLE)
        self.reloj = pygame.time.Clock()
        self.ejecutando = True

        self.gestor = GestorPartida()
        self.persistencia = Persistencia()

        self.menu_principal = MenuPrincipal(self.pantalla, self.gestor, self.persistencia, self)
        self.pantalla_config = PantallaConfiguracion(self.pantalla, self.gestor)
        self.pantalla_continuar = PantallaContinuar(self.pantalla, self.gestor, self.persistencia)
        self.pantalla_juego = PantallaJuego(self.pantalla, self.gestor, self)
        self.pantalla_pausa = PantallaPausa(self.pantalla, self.gestor, self.persistencia)
        self.pantalla_reglas = PantallaReglas(self.pantalla, self.gestor)
        self.pantalla_stats = PantallaEstadisticas(self.pantalla, self.gestor)
        self.pantalla_final = PantallaFinal(self.pantalla, self.gestor)

    def toggle_pantalla_completa(self):
        self.pantalla_completa = not self.pantalla_completa
        if self.pantalla_completa:
            self.pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.pantalla = pygame.display.set_mode((self.ancho_defecto, self.alto_defecto), pygame.RESIZABLE)

        self._actualizar_referencias_pantalla()

    def _actualizar_referencias_pantalla(self):
        self.menu_principal.pantalla = self.pantalla
        self.pantalla_config.pantalla = self.pantalla
        self.pantalla_continuar.pantalla = self.pantalla
        self.pantalla_juego.pantalla = self.pantalla
        self.pantalla_pausa.pantalla = self.pantalla
        self.pantalla_reglas.pantalla = self.pantalla
        self.pantalla_stats.pantalla = self.pantalla
        self.pantalla_final.pantalla = self.pantalla

    def ejecutar(self):
        while self.ejecutando:
            self._procesar_eventos()
            self._actualizar_y_dibujar()
            pygame.display.flip()
            self.reloj.tick(60)

        pygame.quit()

    def _procesar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutando = False
                return

            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                self.toggle_pantalla_completa()

            elif evento.type == pygame.VIDEORESIZE and not self.pantalla_completa:
                self.pantalla = pygame.display.set_mode((evento.w, evento.h), pygame.RESIZABLE)
                self._actualizar_referencias_pantalla()

            estado = self.gestor.estado

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

    def _actualizar_y_dibujar(self):
        estado = self.gestor.estado

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
            if self.gestor.estado_anterior in ("JUEGO", "PAUSA", "FINAL"):
                self.pantalla_juego.dibujar()
            self.pantalla_reglas.dibujar()
        elif estado == "ESTADISTICAS":
            if self.gestor.estado_anterior in ("JUEGO", "PAUSA", "FINAL"):
                self.pantalla_juego.dibujar()
            self.pantalla_stats.dibujar()
        elif estado == "FINAL":
            self.pantalla_juego.dibujar()
            self.pantalla_final.dibujar()
