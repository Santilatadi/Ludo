"""
Modulo pantalla_pausa.py
Frame "Pausa" del Figma (CU-10) y la ventana de confirmación del frame "Reiniciar",
que también se usa para salir al menú (CU-12) y para guardar (CU-14).
"""

# Importa el módulo tema con estilos, colores y fuentes
from interfaz import tema
# Importa la clase BotonFigma para crear los botones interactivos
from interfaz.componentes import BotonFigma

# (atributo, texto, color de relleno, y) — botones 695x95 del frame "Pausa"
# Lista con la configuración de cada botón del menú de pausa
BOTONES = [("btn_continuar_inst", "Continuar", (66, 103, 254), 214),
           ("btn_reiniciar_inst", "Reiniciar Partida", (191, 106, 2), 322),
           ("btn_reglas_inst", "Reglas", (66, 103, 254), 430),
           ("btn_stats_inst", "Estadísticas", (66, 103, 254), 538),
           ("btn_guardar_inst", "Guardar Partida", (9, 201, 15), 646),
           ("btn_menu_inst", "Volver al Menú", (255, 4, 4), 754)]

# Diccionario con los títulos y mensajes de confirmación según la acción
TEXTOS_CONFIRMACION = {
    "REINICIAR": ("Reiniciar", "Esta acción eliminará todo el\nprogreso de esta partida."),
    "SALIR": ("Volver al Menú", "Esta acción descartará el\nprogreso no guardado."),
    "GUARDAR": ("Guardar Partida", "Se guardará la partida y\nvolverás al menú principal."),
}


# Representa la pantalla de pausa y sus diálogos de confirmación
class PantallaPausa:

    # Constructor: inicializa pantalla, gestor y estado de confirmación
    def __init__(self, pantalla, game_manager, interfaz=None):
        # Superficie de la ventana donde se dibuja
        self.pantalla = pantalla
        # Referencia al GameManager
        self.gestor = game_manager
        # Referencia a la interfaz principal
        self.interfaz = interfaz
        # Acción que se está confirmando (None si no hay cartel de confirmación abierto)
        self.confirmando_accion = None  # None, "REINICIAR", "SALIR" o "GUARDAR"
        # Mensaje temporal de aviso (toast)
        self.mensaje_toast = ""

    # Dibuja el menú de pausa o el cartel de confirmación si está activo
    def dibujar(self):
        p = self.pantalla
        # Oscurece la pantalla del juego detrás
        tema.oscurecer(p)
        # Si se abrió un cartel de confirmación, dibuja ese cartel y termina
        if self.confirmando_accion:
            self._dibujar_modal_confirmacion()
            return

        # Dibuja el panel central azul con borde amarillo y esquinas redondeadas
        tema.panel_figma(p, 301, 57, 800, 859, tema.GRADIENTE, tema.AMARILLO_BORDE, 4, radio=50)
        # Dibuja el título "Pausa"
        tema.texto_figma(p, "Pausa", 0, 0, 96, contorno=(201, 192, 24), trazo=4, centrado_en=(719.5, 132))
        # Dibuja la línea divisoria
        tema.linea_figma(p, 317, 199, 765)
        # Recorre la lista de botones y dibuja cada uno en su posición
        for atributo, texto, relleno, y in BOTONES:
            x = 353 if atributo in ("btn_reiniciar_inst", "btn_menu_inst") else 350
            boton = BotonFigma(p, (x, y, 695, 95), texto, relleno, tema.AMARILLO, 4, radio=40, tam_texto=64,
                               contorno_texto=tema.AZUL)
            # Guarda la instancia del botón en self con su nombre de atributo
            setattr(self, atributo, boton)
            # Dibuja el botón en la pantalla
            boton.dibujar(p)

        # Si hay un mensaje toast de error, lo muestra al pie
        if self.mensaje_toast:
            # CU-14 A 4.a: el guardado falló
            tema.texto_figma(p, self.mensaje_toast, 0, 0, 28, (255, 120, 120), tema.NEGRO, 4,
                             centrado_en=(701, 890))

    # Dibuja el diálogo emergente para pedir confirmación al usuario
    def _dibujar_modal_confirmacion(self):
        p = self.pantalla
        # Obtiene el título y mensaje correspondiente a la acción actual
        titulo, mensaje = TEXTOS_CONFIRMACION.get(self.confirmando_accion, TEXTOS_CONFIRMACION["SALIR"])
        # Dibuja la ventana del modal con borde rojo
        tema.panel_figma(p, 92, 166, 1256, 627, tema.GRADIENTE, tema.ROJO_BORDE, 4)
        # Dibuja el título de la confirmación
        tema.texto_figma(p, titulo, 0, 0, 96, (235, 229, 35), (197, 18, 18), 4, centrado_en=(719.5, 229))
        # Dibuja la línea horizontal
        tema.linea_figma(p, 92, 304, 1256)
        # Muestra cada línea del mensaje de advertencia
        for k, linea in enumerate(mensaje.split("\n")):
            tema.texto_figma(p, linea, 0, 0, 64, centrado_en=(693.5, 351 + k * 70))
        # Pregunta "¿Está seguro de continuar?"
        tema.texto_figma(p, "¿Está seguro de continuar?", 0, 0, 64, (254, 216, 66), centrado_en=(699, 515))

        # Crea el botón gris de CANCELAR
        self.btn_conf_no_inst = BotonFigma(p, (165, 609, 470, 128), "CANCELAR", tema.GRIS, (255, 4, 4), 4,
                                           tam_texto=64, contorno_texto=(66, 133, 244))
        # Crea el botón rojo de CONFIRMAR
        self.btn_conf_si_inst = BotonFigma(p, (776, 609, 512, 128), "CONFIRMAR", (223, 14, 14), (66, 133, 244), 4,
                                           tam_texto=64)
        # Dibuja ambos botones
        self.btn_conf_no_inst.dibujar(p)
        self.btn_conf_si_inst.dibujar(p)

    # Maneja los eventos de clic en los botones de pausa o de confirmación
    def manejar_evento(self, evento):

        # Si el cartel de confirmación está abierto:
        if self.confirmando_accion:
            # Si presiona el botón CONFIRMAR:
            if hasattr(self, 'btn_conf_si_inst') and self.btn_conf_si_inst.es_cliqueado(evento):
                accion, self.confirmando_accion = self.confirmando_accion, None
                # Si confirmaba reiniciar:
                if accion == "REINICIAR":
                    # CU-11: se descarta la partida y se vuelve a configurar
                    self.gestor.confirmarReinicio()
                    self.interfaz.pantalla_config.reiniciar_formulario()
                    self.interfaz.ir_a("CONFIGURACION")
                # Si confirmaba salir al menú:
                elif accion == "SALIR":
                    # CU-12: se descartan los datos y se vuelve al menú
                    self.gestor.confirmarSalida()
                    self.interfaz.ir_a("MENU")
                # Si confirmaba guardar la partida:
                elif accion == "GUARDAR":
                    # CU-14: se guarda y se vuelve al menú; si falla, se informa (A 4.a)
                    exito, msg = self.gestor.confirmarGuardado()
                    self.mensaje_toast = "" if exito else msg
                    if exito:
                        self.interfaz.ir_a("MENU")

            # Si presiona el botón CANCELAR:
            elif hasattr(self, 'btn_conf_no_inst') and self.btn_conf_no_inst.es_cliqueado(evento):
                if self.confirmando_accion == "REINICIAR":
                    self.gestor.cancelarReinicio()
                elif self.confirmando_accion == "SALIR":
                    self.gestor.cancelarSalida()
                elif self.confirmando_accion == "GUARDAR":
                    self.gestor.cancelarGuardado()
                # Cierra el diálogo de confirmación
                self.confirmando_accion = None
            return

        # Si presiona "Continuar": reanuda la partida y vuelve al juego
        if hasattr(self, 'btn_continuar_inst') and self.btn_continuar_inst.es_cliqueado(evento):
            self.gestor.reanudarPartida()
            self.interfaz.ir_a("JUEGO")

        # Si presiona "Reiniciar Partida": abre el modal de confirmación de reinicio
        elif hasattr(self, 'btn_reiniciar_inst') and self.btn_reiniciar_inst.es_cliqueado(evento):
            self.confirmando_accion = "REINICIAR"

        # Si presiona "Reglas": abre la pantalla de reglas
        elif hasattr(self, 'btn_reglas_inst') and self.btn_reglas_inst.es_cliqueado(evento):
            self.interfaz.pantalla_reglas.abrir()
            self.interfaz.ir_a("REGLAS")

        # Si presiona "Estadísticas": abre la pantalla de estadísticas
        elif hasattr(self, 'btn_stats_inst') and self.btn_stats_inst.es_cliqueado(evento):
            self.interfaz.pantalla_stats.abrir()
            self.interfaz.ir_a("ESTADISTICAS")

        # Si presiona "Volver al Menú": comprueba si hay que pedir confirmación
        elif hasattr(self, 'btn_menu_inst') and self.btn_menu_inst.es_cliqueado(evento):
            # CU-12: solo se pide confirmación si hay una partida activa (A 3.b)
            if self.gestor.volverAlMenuPrinicipal():
                self.confirmando_accion = "SALIR"
            else:
                self.interfaz.ir_a("MENU")

        # Si presiona "Guardar Partida": pide confirmación antes de guardar
        elif hasattr(self, 'btn_guardar_inst') and self.btn_guardar_inst.es_cliqueado(evento):
            # CU-14: guardar pide confirmación y, si sale bien, vuelve al menú
            if self.gestor.partidaActual:
                self.mensaje_toast = ""
                self.confirmando_accion = "GUARDAR"



#- __init__(): prepara la pantalla de pausa.
#- dibujar(): muestra los botones de pausa.
#- _dibujar_modal_confirmacion(): muestra el mensaje para confirmar una acción.
#- manejar_evento(): detecta qué botón toca el usuario y realiza la acción correspondiente.
#En resumen: permite continuar, reiniciar, ver las reglas, consultar estadísticas, guardar la partida o volver al menú. Antes de algunas acciones, pide confirmación.