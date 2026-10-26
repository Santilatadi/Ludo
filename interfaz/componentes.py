"""
Modulo componentes.py
Componentes de interfaz de usuario modernos, interactivos y adaptativos para Pygame.
Incluye botones con animación suave de escalado y el estilo del diseño de Figma
(relleno de color, borde redondeado y texto con contorno).
"""

# Importa pygame para la creación y dibujo de los elementos gráficos
import pygame


# Clase base para crear botones interactivos con animaciones
class BotonModerno: #clase padre

    # Constructor: inicializa el tamaño, texto, colores, fuente e icono del botón
    def __init__(self, rect, texto, color_base=(25, 75, 175), color_hover=(45, 115, 235), color_texto=(255, 255, 255), color_borde=(255, 251, 0), fuente=None, icono=""):
        # Guarda el rectángulo original con la posición y tamaño base
        self.rect_base = pygame.Rect(rect)
        # Rectángulo que cambiará de tamaño durante las animaciones
        self.rect_anim = pygame.Rect(rect)
        # Texto visible del botón
        self.texto = texto
        # Color del botón en estado normal
        self.color_base = color_base
        # Color del botón cuando el mouse pasa por encima
        self.color_hover = color_hover
        # Color del texto
        self.color_texto = color_texto
        # Color del borde del botón
        self.color_borde = color_borde
        # Tipografía para renderizar el texto
        self.fuente = fuente
        # Icono o símbolo opcional que acompaña al texto
        self.icono = icono

        # Indica si el cursor está sobre el botón
        self.es_hover = False
        # Guarda el estado del cursor en el fotograma anterior
        self.es_hover_prev = False
        # Escala actual del tamaño para la animación suave
        self.escala_actual = 1.0

    # Actualiza el estado de animación y detecta si el mouse está encima
    def actualizar(self, pos_mouse):
        # Guarda el estado hover previo
        self.es_hover_prev = self.es_hover
        # Comprueba si las coordenadas del mouse tocan el rectángulo base
        self.es_hover = self.rect_base.collidepoint(pos_mouse)

        # Si el mouse está encima agranda un 4% (1.04), si no vuelve al tamaño normal (1.0)
        target_escala = 1.04 if self.es_hover else 1.0
        # Realiza una transición suave hacia el tamaño objetivo
        self.escala_actual += (target_escala - self.escala_actual) * 0.25

        # Re-calcular rectángulo escalado manteniendo el centro
        # Calcula el nuevo ancho escalado
        w_scaled = int(self.rect_base.width * self.escala_actual)
        # Calcula el nuevo alto escalado
        h_scaled = int(self.rect_base.height * self.escala_actual)
        # Obtiene las coordenadas del centro original
        cx, cy = self.rect_base.center
        # Crea el rectángulo animado centrado en la misma posición
        self.rect_anim = pygame.Rect(cx - w_scaled // 2, cy - h_scaled // 2, w_scaled, h_scaled)

    # Dibuja el botón en la pantalla con sombra, relleno, borde y texto
    def dibujar(self, pantalla):
        # Obtiene la posición actual del cursor del mouse
        pos_m = pygame.mouse.get_pos()
        # Actualiza las animaciones según la posición del cursor
        self.actualizar(pos_m)

        # Elige el color hover si el mouse está encima, o el color base si no lo está
        col = self.color_hover if self.es_hover else self.color_base
        # Calcula el radio de las esquinas redondeadas
        radio = min(self.rect_anim.height // 2, 24)

        # Sombra, relleno y borde como en los botones del Figma
        # Desplaza el rectángulo hacia abajo para simular una sombra
        sombra = self.rect_anim.move(0, 4)
        # Dibuja la sombra oscura
        pygame.draw.rect(pantalla, (20, 0, 50), sombra, border_radius=radio)
        # Dibuja el cuerpo o relleno del botón
        pygame.draw.rect(pantalla, col[:3], self.rect_anim, border_radius=radio)
        # Dibuja el contorno o borde del botón (más grueso si el mouse está encima)
        pygame.draw.rect(pantalla, self.color_borde[:3], self.rect_anim, width=3 if self.es_hover else 2, border_radius=radio)

        # Prepara la cadena de texto combinando el icono con el texto
        str_display = f"{self.icono} {self.texto}".strip() if self.icono else self.texto
        # Si tiene una fuente asignada, dibuja el texto:
        if self.fuente:
            # Renderiza la superficie del texto en su color
            base = self.fuente.render(str_display, True, self.color_texto)
            # Renderiza el contorno oscuro del texto
            contorno = self.fuente.render(str_display, True, (40, 0, 90))
            # Centra el texto en el rectángulo del botón
            rect_txt = base.get_rect(center=self.rect_anim.center)
            # Dibuja el contorno alrededor en 8 direcciones distintas
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)):
                pantalla.blit(contorno, rect_txt.move(dx, dy))
            # Dibuja el texto principal en el centro
            pantalla.blit(base, rect_txt)

    # Comprueba si el usuario hizo clic izquierdo sobre el botón
    def es_cliqueado(self, evento):
        # Verifica si el evento es presionar un botón del mouse con el botón izquierdo (1)
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            # Verifica si el clic ocurrió dentro del área del botón
            if self.rect_anim.collidepoint(evento.pos):
                # Retorna True indicando que fue cliqueado
                return True
        # Si no fue presionado, retorna False
        return False


# Botón especial con fondo en degradé vertical
class BotonDegradado(BotonModerno):
    """Botón grande con degradé vertical (por ejemplo, INICIAR de Nueva Partida en el Figma)."""

    # Constructor: inicializa el botón con una lista de colores para el degradé
    def __init__(self, rect, texto, colores, fuente=None, color_borde=None):
        # Llama al constructor de la clase padre BotonModerno
        super().__init__(rect, texto, fuente=fuente, color_borde=color_borde or (255, 251, 0))
        # Guarda la lista de colores para el degradado
        self.colores = colores

    # Dibuja el botón con degradado y sombra
    def dibujar(self, pantalla):
        # Importa el módulo tema para usar sus funciones de dibujo
        from interfaz import tema
        # Actualiza la animación de hover con la posición del mouse
        self.actualizar(pygame.mouse.get_pos())
        # Calcula el radio de redondeo de las esquinas
        radio = min(self.rect_anim.height // 3, 30)
        # Dibuja la sombra oscura
        pygame.draw.rect(pantalla, (20, 0, 50), self.rect_anim.move(0, 5), border_radius=radio)
        # Dibuja el panel con el degradado de colores
        tema.panel(pantalla, self.rect_anim, self.colores, self.color_borde, radio=radio,
                   grosor=3 if self.es_hover else 0)
        # Si tiene fuente asignada, dibuja el texto centrado con su contorno
        if self.fuente:
            base = self.fuente.render(self.texto, True, self.color_texto)
            contorno = self.fuente.render(self.texto, True, (120, 10, 10))
            rect_txt = base.get_rect(center=self.rect_anim.center)
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                pantalla.blit(contorno, rect_txt.move(dx, dy))
            pantalla.blit(base, rect_txt)


# Botón que respeta exactamente las medidas y estilos definidos en el diseño de Figma
class BotonFigma(BotonModerno):
    """Botón dibujado con las medidas del Figma: rectángulo (con degradé o color liso),
    borde de color y texto Goldman con trazo. `rect_figma` está en coordenadas del Figma."""

    # Constructor: recibe las medidas originales de Figma y las adapta a la resolución actual
    def __init__(self, pantalla, rect_figma, texto, relleno, borde, trazo=4, radio=0, tam_texto=48,
                 color_texto=(255, 255, 255), contorno_texto=(0, 0, 0), trazo_texto=4, alinear="centro",
                 margen_texto=0):
        from interfaz import tema
        # Convierte las coordenadas del Figma a píxeles de la ventana actual y llama al padre
        super().__init__(tema.R(pantalla, *rect_figma), texto)
        # Guarda la referencia a la superficie de la pantalla
        self.pantalla_ref = pantalla
        # Guarda las coordenadas originales del diseño en Figma
        self.rect_figma = rect_figma
        # Guarda el color de relleno, de borde, grosor del trazo y radio de las esquinas
        self.relleno, self.borde, self.trazo, self.radio = relleno, borde, trazo, radio
        # Guarda el tamaño del texto, su color y su contorno
        self.tam_texto, self.color_texto, self.contorno_texto = tam_texto, color_texto, contorno_texto
        # Guarda el grosor del contorno, alineación (centro o izquierda) y márgenes
        self.trazo_texto, self.alinear, self.margen_texto = trazo_texto, alinear, margen_texto

    # Actualiza si el mouse está posado sobre el botón
    def actualizar(self, pos_mouse):
        # Verifica si el cursor colisiona con el botón
        self.es_hover = self.rect_base.collidepoint(pos_mouse)
        # Mantiene el rectángulo animado igual al base
        self.rect_anim = self.rect_base

    # Dibuja el botón adaptándolo a la escala actual de la ventana
    def dibujar(self, pantalla):
        from interfaz import tema
        # Actualiza el estado hover con la posición del mouse
        self.actualizar(pygame.mouse.get_pos())
        # Desempaqueta las coordenadas originales en Figma
        x, y, w, h = self.rect_figma
        # Dibuja el panel escalado con su relleno y borde
        tema.panel_figma(pantalla, x, y, w, h, self.relleno, self.borde, self.trazo, self.radio)
        # Si el cursor está encima, añade un brillo semitransparente blanco
        if self.es_hover:
            # Crea una capa transparente del tamaño del botón
            capa = pygame.Surface(self.rect_base.size, pygame.SRCALPHA)
            # Dibuja el brillo con transparencia
            pygame.draw.rect(capa, (255, 255, 255, 35), capa.get_rect(), border_radius=tema.T(pantalla, self.radio))
            # Pega el brillo sobre la pantalla
            pantalla.blit(capa, self.rect_base.topleft)
        # Separa el texto en líneas si tiene saltos de línea (\n)
        lineas = self.texto.split("\n")
        # Recorre cada línea de texto
        for i, linea in enumerate(lineas):
            # Calcula la posición vertical (Y) de la línea
            cy = y + h / 2 + (i - (len(lineas) - 1) / 2) * self.tam_texto * 1.15
            # Calcula el grosor escalado del contorno
            g = tema.T(pantalla, self.trazo_texto / 2) if self.contorno_texto else 0
            # Renderiza la superficie del texto con su contorno
            surf = tema.render_texto(linea, tema.T(pantalla, self.tam_texto), self.color_texto,
                                     self.contorno_texto, g)
            # Posiciona la línea a la izquierda o al centro según corresponda
            if self.alinear == "izquierda":
                rect = surf.get_rect(midleft=tema.P(pantalla, x + self.margen_texto, cy))
            else:
                rect = surf.get_rect(center=tema.P(pantalla, x + w / 2, cy))
            # Dibuja la línea de texto en pantalla
            pantalla.blit(surf, rect)



#1. Clase BotonModerno
#- __init__(): configura el botón, su texto, sus colores, su tamaño y su icono.
#- actualizar(): detecta si el mouse está encima del botón y hace que aumente un poco de tamaño.
#- dibujar(): dibuja el botón en pantalla, con su color, borde, sombra y texto.
#- es_cliqueado(): comprueba si el usuario hizo clic sobre el botón.
#2. Clase BotonDegradado
#Hereda de BotonModerno y permite crear botones con un degradado de colores.
#- __init__(): configura el botón y los colores del degradado.
#- dibujar(): dibuja el botón con degradado, sombra, borde y texto.
#3. Clase BotonFigma
#Hereda de BotonModerno y permite crear botones siguiendo el diseño realizado en Figma.
#- __init__(): configura la posición, el tamaño, los colores, el borde y el texto del botón.
#- actualizar(): comprueba si el mouse está encima del botón.
#- dibujar(): dibuja el botón respetando el diseño de Figma, incluyendo el relleno, el borde y el texto.