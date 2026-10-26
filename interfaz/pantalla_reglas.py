"""
Modulo pantalla_reglas.py
Frame "Reglas" del Figma (CU-06): ventana con degradé azul y borde rojo, título
"Reglas del juego" en amarillo, una X para cerrar y las reglas con desplazamiento.
"""

# Importa pygame para renderizado y eventos
import pygame

# Importa el módulo con funciones de tema y estilos
from interfaz import tema


# Representa la ventana modal para leer las reglas del juego de Ludo
class PantallaReglas:

    # Constructor: inicializa pantalla, gestor, textos y variables de desplazamiento (scroll)
    def __init__(self, pantalla, game_manager, interfaz=None):
        # Superficie de la ventana donde se dibuja
        self.pantalla = pantalla
        # Referencia al GameManager
        self.gestor = game_manager
        # Referencia al controlador principal de pantallas
        self.interfaz = interfaz
        # Cadena de texto con las reglas completas
        self.texto_reglas = ""
        # Desplazamiento vertical actual en píxeles
        self.scroll_y = 0
        # Límite máximo de desplazamiento permitido hacia abajo
        self.max_scroll = 0

    # Abre la pantalla de reglas y carga el texto desde la persistencia
    def abrir(self):
        # CU-06: el GameManager obtiene las reglas de la persistencia
        # Reinicia el desplazamiento arriba de todo
        self.scroll_y = 0
        # Pide las reglas al gestor
        self.texto_reglas = self.gestor.consultarReglas()

    # Cierra la ventana de reglas y regresa al estado anterior del juego
    def _cerrar(self):
        # Notifica al gestor que se vuelve de las reglas
        self.gestor.volverDeReglas()
        # Restaura el estado previo en la interfaz
        self.interfaz.estado = self.interfaz.estado_anterior

    # Dibuja la ventana, el texto de las reglas y la barra de desplazamiento
    def dibujar(self):
        p = self.pantalla
        # Oscurece la pantalla de atrás
        tema.oscurecer(p)
        # Dibuja el marco principal de la ventana con borde rojo
        tema.panel_figma(p, 295, 57, 800, 800, tema.GRADIENTE, tema.ROJO_BORDE, 4)
        # Dibuja el título "Reglas del juego" en letras amarillas
        tema.texto_figma(p, "Reglas del juego", 0, 0, 48, (247, 255, 6), (173, 66, 4), 4, centrado_en=(681.5, 124.5))
        # Dibuja la cruz de cierre en la esquina
        self.btn_cerrar_inst = tema.cruz_figma(p, 1020, 71)
        # Dibuja la línea divisoria
        tema.linea_figma(p, 299, 193, 796)

        # Si aún no tiene el texto cargado, intenta cargarlo
        if not self.texto_reglas:
            # CU-06 A: no se pudieron cargar las reglas; se vuelve a intentar
            self.texto_reglas = self.gestor.consultarReglas()
        # Divide el texto en líneas separadas por salto de línea
        lineas = (self.texto_reglas or "1. No se pudieron cargar las reglas.\n   Reintentando...").split("\n")

        # Define el área visible donde se recortará el texto que hace scroll
        zona = tema.R(p, 330, 210, 740, 630)
        # Activa el recorte para que no se dibuje texto fuera de la caja
        p.set_clip(zona)
        # Calcula la posición Y inicial restando el scroll acumulado
        y = zona.y - self.scroll_y
        alto_titulo, alto_linea = tema.T(p, 40), tema.T(p, 32)
        # Recorre cada línea de texto
        for linea in lineas:
            # Si la línea está vacía, añade un pequeño espacio vertical
            if not linea.strip():
                y += tema.T(p, 14)
                continue
            # Si la línea empieza con un número (es título de sección):
            if linea[0].isdigit() and "." in linea[:3]:
                # Renderiza el título en amarillo con contorno negro
                surf = tema.render_texto(linea, tema.T(p, 32), (247, 255, 6), tema.NEGRO, tema.T(p, 2))
                p.blit(surf, (zona.x, y))
                y += alto_titulo
            # Si es texto normal:
            else:
                # Divide el texto largo en renglones que quepan en el ancho
                for parte in self._partir(linea.strip(), tema.fuente(tema.T(p, 24)), zona.width - tema.T(p, 30)):
                    # Renderiza cada renglón en color blanco
                    surf = tema.render_texto(parte, tema.T(p, 24), tema.BLANCO, tema.NEGRO, tema.T(p, 2))
                    p.blit(surf, (zona.x + tema.T(p, 26), y))
                    y += alto_linea
        # Desactiva el recorte para volver a dibujar en toda la pantalla
        p.set_clip(None)

        # Calcula la altura total ocupada por el texto
        total = y + self.scroll_y - zona.y
        # Calcula el máximo que se puede scrollear hacia abajo
        self.max_scroll = max(0, total - zona.height + tema.T(p, 20))
        # Si el texto es más largo que la ventana, dibuja la barra de desplazamiento:
        if self.max_scroll:
            barra = pygame.Rect(zona.right + tema.T(p, 6), zona.y, tema.T(p, 10), zona.height)
            pygame.draw.rect(p, tema.NEGRO, barra, border_radius=barra.width // 2)
            alto = max(tema.T(p, 40), int(zona.height * zona.height / total))
            y0 = zona.y + int((zona.height - alto) * self.scroll_y / self.max_scroll)
            pygame.draw.rect(p, tema.BLANCO, (barra.x + 2, y0, barra.width - 4, alto), border_radius=barra.width // 2)

    # Divide un texto largo en varias líneas para que no se salga de la pantalla
    def _partir(self, texto, fuente, ancho_max):
        # Separa en palabras individuales
        palabras, lineas, actual = texto.split(), [], ""
        for palabra in palabras:
            prueba = f"{actual} {palabra}".strip()
            # Si entra en el ancho, suma la palabra al renglón
            if fuente.size(prueba)[0] <= ancho_max or not actual:
                actual = prueba
            # Si no entra, pasa al renglón siguiente
            else:
                lineas.append(actual)
                actual = palabra
        if actual:
            lineas.append(actual)
        return lineas

    # Maneja la rueda del mouse, clics y flechas del teclado para hacer scroll
    def manejar_evento(self, evento):
        # Eventos del mouse:
        if evento.type == pygame.MOUSEBUTTONDOWN:
            # Clic izquierdo en la cruz de cierre:
            if evento.button == 1:
                if hasattr(self, 'btn_cerrar_inst') and self.btn_cerrar_inst.collidepoint(evento.pos):
                    self._cerrar()
            # Rueda del mouse hacia arriba (subir):
            elif evento.button == 4:  # Scroll Up
                self.scroll_y = max(0, self.scroll_y - 25)
            # Rueda del mouse hacia abajo (bajar):
            elif evento.button == 5:  # Scroll Down
                if hasattr(self, 'max_scroll'):
                    self.scroll_y = min(self.max_scroll, self.scroll_y + 25)
        # Eventos de teclado:
        elif evento.type == pygame.KEYDOWN:
            # ESC o ENTER para cerrar
            if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self._cerrar()
            # Flecha hacia arriba para subir el texto
            elif evento.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - 25)
            # Flecha hacia abajo para bajar el texto
            elif evento.key == pygame.K_DOWN:
                if hasattr(self, 'max_scroll'):
                    self.scroll_y = min(self.max_scroll, self.scroll_y + 25)


# - __init__(): prepara la pantalla de reglas.
# - abrir(): carga las reglas del juego.
# - _cerrar(): cierra las reglas y vuelve a la pantalla anterior.
# - dibujar(): muestra las reglas en pantalla.
# - _partir(): divide los textos largos en varias líneas.
# - manejar_evento(): permite cerrar las reglas o desplazarse por el texto usando el mouse o las teclas.
#En resumen: muestra las reglas del Ludo y permite leerlas y desplazarse por ellas.