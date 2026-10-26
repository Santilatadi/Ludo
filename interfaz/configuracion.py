"""
Modulo configuracion.py
Dibuja e interactúa con la Pantalla de Configuración de Nueva Partida.
Sigue el frame "Configuracion Nueva Partida" del Figma: cantidad de jugadores (CU-02),
nombres y tipo de cada jugador (CU-03) y elección de color con las flechas (CU-04).
"""

# Herramientas del sistema operativo para rutas
import os
# Herramientas del sistema de Python
import sys
# Librería Pygame para la interfaz visual
import pygame

# Obtiene la ruta de la carpeta principal del proyecto
directorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Si no está en la lista de rutas del sistema
if directorio_raiz not in sys.path:
    # Agrega la ruta para permitir importar módulos propios
    sys.path.insert(0, directorio_raiz)

# Importa los colores del juego
from modelos.color import Color
# Importa el tema visual con estilos y colores
from interfaz import tema
# Importa los componentes de botones interactivos
from interfaz.componentes import BotonModerno, BotonFigma


# Clase que gestiona la pantalla de configuración de partida
class PantallaConfiguracion:

    # Constructor que inicializa la pantalla de configuración
    def __init__(self, pantalla, game_manager, interfaz=None):
        # Guarda la ventana gráfica donde se dibuja todo
        self.pantalla = pantalla
        # Guarda el gestor que controla las reglas del juego
        self.gestor = game_manager
        # Guarda la interfaz principal para cambiar entre pantallas
        self.interfaz = interfaz
        # Establece los valores iniciales del formulario
        self.reiniciar_formulario()

    # Reinicia las opciones a sus valores por defecto
    def reiniciar_formulario(self):
        # Valores iniciales de la pantalla (nueva partida o reinicio, CU-11)
        # Cantidad de jugadores inicial (2 por defecto)
        self.cant_jugadores = 2
        # Indica si cada jugador es bot (el primero humano, los demás bots)
        self.es_bot_lista = [False, True, True, True]
        # Nombres sugeridos para cada jugador
        self.nombres = ["Jugador 1", "Bot 2", "Bot 3", "Bot 4"]
        # Colores asignados por defecto a cada jugador
        self.colores = [Color.ROJO, Color.VERDE, Color.AZUL, Color.AMARILLO]   # orden del Figma
        # Índice del cuadro de texto que se está editando (ninguno al inicio)
        self.campo_activo = None
        # Mensaje de error para avisar al usuario si algo falla
        self.mensaje_error = ""

        # Contador de cuadros para animar el cursor de texto
        self.ticks = 0

    # Sincroniza la partida del gestor con los datos de la pantalla
    def _sincronizar_partida(self):
        # CU-01 y CU-02: la partida en configuración del GameManager tiene la cantidad de
        # jugadores y el color de cada uno que muestra la pantalla.
        # Obtiene la partida actual del gestor
        partida = self.gestor.partidaActual
        # Si no existe partida o no está en configuración
        if partida is None or partida.estado != "CONFIGURACION":
            # Inicia una nueva partida en estado de configuración
            self.gestor.iniciarPartida()
            # Actualiza la referencia a la partida actual
            partida = self.gestor.partidaActual
        # Si la cantidad de jugadores ya coincide, no hace nada más
        if partida.numeroJugadores() == self.cant_jugadores:
            # Sale de la función
            return
        # Ajusta la cantidad de jugadores en el gestor
        self.gestor.configurarCantidadJugadores(self.cant_jugadores)
        # Recorre cada jugador para asignarle su color
        for i in range(self.cant_jugadores):
            # Intenta asignar el color elegido al jugador
            exito, _ = self.gestor.seleccionarColor(self.colores[i], i)
            # Si el color no estaba disponible
            if not exito:
                # Elige el primer color libre disponible
                self.colores[i] = self.gestor.seleccionarColores()[0]
                # Le asigna ese nuevo color al jugador
                self.gestor.seleccionarColor(self.colores[i], i)

    # Dibuja todos los elementos gráficos de la pantalla de configuración
    def dibujar(self):
        # Frame "Configuracion Nueva Partida" del Figma
        # Incrementa el contador de cuadros para animaciones
        self.ticks += 1
        # Asegura que el gestor tenga los datos sincronizados
        self._sincronizar_partida()
        # Referencia corta a la pantalla
        p = self.pantalla
        # Obtiene las coordenadas actuales del cursor del mouse
        pos_m = pygame.mouse.get_pos()

        # Pinta el fondo general de la pantalla
        p.fill(tema.FONDO)
        # Dibuja el panel principal con bordes redondeados
        tema.panel_figma(p, 111, 88, 1220, 805, tema.GRADIENTE, tema.ROJO_BORDE, 4)
        # Dibuja el título "NUEVA PARTIDA" en la parte superior
        tema.texto_figma(p, "NUEVA PARTIDA", 0, 0, 96, contorno=(255, 251, 0), trazo=4, centrado_en=(721, 172))
        # Calcula el rectángulo para la barra divisoria horizontal
        barra = tema.R(p, 282, 217, 878, 16)
        # Dibuja el fondo gris de la barra
        pygame.draw.rect(p, tema.GRIS, barra, border_radius=barra.height // 2)
        # Dibuja el borde negro alrededor de la barra
        pygame.draw.rect(p, tema.NEGRO, barra, width=tema.T(p, 4), border_radius=barra.height // 2)

        # CU-02: cantidad de jugadores ("-" y "+" rojos a los lados del número)
        # Muestra la palabra "Cantidad"
        tema.texto_figma(p, "Cantidad", 183, 312, 36)
        # Muestra la palabra "Jugadores" debajo de "Cantidad"
        tema.texto_figma(p, "Jugadores", 183, 350, 36)
        # Crea el botón interactivo para restar jugadores
        self.btn_menos_inst = BotonModerno(tema.R(p, 438, 302, 52, 70), "-")
        # Crea el botón interactivo para sumar jugadores
        self.btn_mas_inst = BotonModerno(tema.R(p, 615, 302, 56, 70), "+")
        # Dibuja los botones de sumar y restar con cambio de brillo al pasar el mouse
        for boton, cx in ((self.btn_menos_inst, 463.5), (self.btn_mas_inst, 642.5)):
            # Comprueba si el mouse está sobre el botón
            claro = boton.rect_base.collidepoint(pos_m)
            # Dibuja el texto "+" o "-" con su color correspondiente
            tema.texto_figma(p, boton.texto, 0, 0, 64, (255, 90, 90) if claro else tema.ROJO_TEXTO, tema.NEGRO, 2,
                             centrado_en=(cx, 337))
        # Calcula el rectángulo donde se muestra el número de jugadores
        cantidad = tema.R(p, 505, 306, 94, 66)
        # Dibuja el fondo de la caja del número
        pygame.draw.rect(p, tema.GRIS, cantidad, border_radius=cantidad.height // 2)
        # Dibuja el borde exterior de la caja
        pygame.draw.rect(p, tema.NEGRO, cantidad, width=tema.T(p, 4), border_radius=cantidad.height // 2)
        # Escribe el número actual de jugadores en el centro de la caja
        tema.texto_figma(p, str(self.cant_jugadores), 0, 0, 64, tema.ROJO_TEXTO, tema.NEGRO, 2, centrado_en=(552, 339))

        # CU-03 y CU-04: un renglón por jugador con su nombre; el borde es su color
        # Título de la sección de nombres de jugadores
        tema.texto_figma(p, "Jugadores", 183, 429, 48)
        # Lista para guardar los rectángulos de cada campo de nombre
        self.rects_nombres = []
        # Lista para los rectángulos de las flechas izquierdas
        self.rects_arrow_left = []
        # Lista para los rectángulos de las flechas derechas
        self.rects_arrow_right = []
        # Lista para los rectángulos del botón de tipo de jugador (Bot/Humano)
        self.rects_tipo = []
        # Posiciones en pantalla para las 4 filas de jugadores
        posiciones = [(300, 523), (824, 523), (300, 645), (824, 645)]
        # Dibuja la tarjeta de configuración de cada jugador activo
        for i in range(self.cant_jugadores):
            # Obtiene las coordenadas X e Y de la tarjeta
            fx, fy = posiciones[i]
            # Obtiene el color visual correspondiente al jugador
            col = tema.COLOR_JUGADOR.get(self.colores[i], tema.BLANCO)
            # Crea el rectángulo con forma redondeada tipo píldora
            pildora = tema.R(p, fx, fy, 327, 61)
            # Guarda el rectángulo para detectar clics
            self.rects_nombres.append(pildora)
            # Dibuja el fondo blanco de la tarjeta
            pygame.draw.rect(p, tema.BLANCO, pildora, border_radius=pildora.height // 2)
            # Dibuja el borde con el color del jugador
            pygame.draw.rect(p, col, pildora, width=tema.T(p, 5), border_radius=pildora.height // 2)

            # Flechas grises: cambian el color del jugador (CU-04)
            # Calcula los rectángulos de las flechas izquierda y derecha
            izq, der = tema.R(p, fx - 33, fy + 15, 24, 30), tema.R(p, fx + 336, fy + 15, 24, 30)
            # Guarda la flecha izquierda en la lista
            self.rects_arrow_left.append(izq)
            # Guarda la flecha derecha en la lista
            self.rects_arrow_right.append(der)
            # Dibuja ambas flechas con color iluminado si el mouse pasa por encima
            for r, derecha in ((izq, False), (der, True)):
                # Dibuja la flecha en la dirección correspondiente
                tema.flecha(p, r, derecha, (255, 251, 120) if r.collidepoint(pos_m) else tema.GRIS, tema.NEGRO,
                            tema.T(p, 4))

            # Nombre sobre la línea; "BOT" a la izquierda si lo controla la consola (CU-03 C)
            # Agrega un cursor parpadeante si se está escribiendo en este campo
            nombre = self.nombres[i] + ("|" if self.campo_activo == i and self.ticks % 60 < 30 else "")
            # Dibuja el texto del nombre del jugador
            tema.texto_figma(p, nombre, 0, 0, 30, (30, 30, 40), None, centrado_en=(fx + 166, fy + 30))
            # Dibuja la línea decorativa debajo del nombre
            pygame.draw.line(p, tema.NEGRO, tema.P(p, fx + 30, fy + 53), tema.P(p, fx + 301, fy + 53), tema.T(p, 4))
            # Rectángulo para el botón que cambia si es BOT o humano
            tipo = tema.R(p, fx + 12, fy + 14, 52, 30)
            # Guarda el rectángulo del botón BOT
            self.rects_tipo.append(tipo)
            # Si es bot o el cursor pasa por encima, dibuja la etiqueta BOT
            if self.es_bot_lista[i] or tipo.collidepoint(pos_m):
                # Dibuja el fondo de la etiqueta BOT
                pygame.draw.rect(p, (60, 60, 80) if self.es_bot_lista[i] else tema.GRIS, tipo,
                                 border_radius=tipo.height // 2)
                # Escribe la palabra "BOT" en el botón
                tema.texto(p, "BOT", tema.T(p, 20), tipo.center,
                           color=tema.BLANCO if self.es_bot_lista[i] else (90, 90, 110))

        # Si hay un mensaje de error, lo muestra en rojo
        if self.mensaje_error:
            # Dibuja el texto del mensaje de error centrado
            tema.texto_figma(p, self.mensaje_error, 0, 0, 28, (255, 230, 230), tema.ROJO_BORDE, 4,
                             centrado_en=(721, 268))

        # Botón grande para iniciar la partida
        self.btn_iniciar_inst = BotonFigma(p, (475, 750, 491, 115), "INICIAR", tema.GRADIENTE_INICIAR, tema.NEGRO, 4,
                                           tam_texto=96)
        # Dibuja el botón INICIAR en pantalla
        self.btn_iniciar_inst.dibujar(p)

        # Cancelar la configuración y volver al menú (CU-01 A y CU-04 B); también con Escape
        # Botón con una "X" roja para cancelar y volver atrás
        self.btn_volver_inst = BotonModerno(tema.R(p, 1260, 98, 60, 60), "X", color_base=tema.ROJO_BORDE,
                                            color_hover=(255, 60, 60), color_borde=tema.NEGRO,
                                            fuente=tema.fuente(tema.T(p, 36)))
        # Dibuja el botón de volver
        self.btn_volver_inst.dibujar(p)

    # Cambia el color del jugador buscando el siguiente o anterior disponible
    def _cambiar_color(self, i, paso):
        # CU-04: las flechas recorren los colores y se asigna el siguiente disponible.
        # Lista de todos los colores del juego
        orden = list(Color)
        # Obtiene qué colores están libres actualmente
        disponibles = self.gestor.seleccionarColores()
        # Encuentra la posición actual del color del jugador
        actual = orden.index(self.colores[i]) if self.colores[i] in orden else 0
        # Recorre la lista de colores en la dirección indicada por paso
        for k in range(1, len(orden)):
            # Calcula el siguiente color candidato en forma circular
            candidato = orden[(actual + paso * k) % len(orden)]
            # Si el color candidato está disponible
            if candidato in disponibles:
                # Intenta asignárselo al jugador en el gestor
                exito, mensaje = self.gestor.seleccionarColor(candidato, i)
                # Si tuvo éxito, actualiza el color en la lista visual
                if exito:
                    self.colores[i] = candidato
                # Borra el error si tuvo éxito o guarda el mensaje si falló
                self.mensaje_error = "" if exito else mensaje
                # Termina la búsqueda
                return
        # CU-04, alternativa A: no queda ningún otro color libre
        # Muestra aviso de que no hay colores disponibles
        self.mensaje_error = "No hay otro color disponible: todos están asignados."

    # Cambia un jugador entre tipo humano y tipo bot
    def _alternar_bot(self, i):
        # Invierte el valor (de humano a bot o viceversa)
        self.es_bot_lista[i] = not self.es_bot_lista[i]
        # Si ahora es bot, asigna un nombre predeterminado de bot
        if self.es_bot_lista[i]:
            self.nombres[i] = f"Bot {i + 1}"
        # Si era bot y volvió a humano, asigna un nombre predeterminado de jugador
        elif self.nombres[i].startswith("Bot"):
            self.nombres[i] = f"Jugador {i + 1}"
        # Limpia cualquier mensaje de error anterior
        self.mensaje_error = ""

    # Procesa los clics del mouse y las teclas presionadas
    def manejar_evento(self, evento):

        # Si el usuario hizo clic con el botón izquierdo del mouse
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            # Obtiene la posición donde se hizo clic
            pos = evento.pos

            # CU-02: la cantidad la valida el GameManager (mínimo 2, máximo 4)
            # Variable para saber si se suma o resta un jugador
            cambio = 0
            # Si hizo clic en el botón de restar
            if hasattr(self, 'btn_menos_inst') and self.btn_menos_inst.es_cliqueado(evento):
                # Resta uno
                cambio = -1
            # Si hizo clic en el botón de sumar
            elif hasattr(self, 'btn_mas_inst') and self.btn_mas_inst.es_cliqueado(evento):
                # Suma uno
                cambio = 1
            # Si se presionó alguno de los dos botones
            if cambio:
                # Sincroniza la partida antes de modificarla
                self._sincronizar_partida()
                # Pide al gestor configurar la nueva cantidad
                exito, mensaje = self.gestor.configurarCantidadJugadores(self.cant_jugadores + cambio)
                # Guarda el mensaje de error si falló
                self.mensaje_error = "" if exito else mensaje
                # Si el gestor aceptó el cambio
                if exito:
                    # Aplica el cambio en la cantidad de jugadores
                    self.cant_jugadores += cambio
                    # Si se agregó un jugador nuevo
                    if cambio > 0:
                        # El jugador nuevo recibe un color libre (lo puede cambiar con las flechas)
                        # Índice del nuevo jugador
                        nuevo = self.cant_jugadores - 1
                        # Intenta asignarle su color por defecto
                        exito, _ = self.gestor.seleccionarColor(self.colores[nuevo], nuevo)
                        # Si ese color estaba ocupado
                        if not exito:
                            # Toma el primer color libre disponible
                            self.colores[nuevo] = self.gestor.seleccionarColores()[0]
                            # Le asigna ese color al nuevo jugador
                            self.gestor.seleccionarColor(self.colores[nuevo], nuevo)
                # Termina el procesamiento de este clic
                return

            # CU-04: las flechas de cada píldora cambian el color del jugador
            # Revisa si se cliqueó alguna flecha izquierda
            for i, r_l in enumerate(self.rects_arrow_left):
                # Si el clic fue dentro de la flecha
                if r_l.collidepoint(pos):
                    # Cambia hacia el color anterior
                    self._cambiar_color(i, -1)
                    # Termina el evento
                    return
            # Revisa si se cliqueó alguna flecha derecha
            for i, r_r in enumerate(self.rects_arrow_right):
                # Si el clic fue dentro de la flecha
                if r_r.collidepoint(pos):
                    # Cambia hacia el color siguiente
                    self._cambiar_color(i, 1)
                    # Termina el evento
                    return

            # Etiqueta BOT/HUM: alterna entre jugador humano y bot
            # Revisa si se hizo clic en el botón de BOT de algún jugador
            for i, r_t in enumerate(getattr(self, "rects_tipo", [])):
                # Si el clic fue en ese botón
                if r_t.collidepoint(pos):
                    # Alterna entre persona y bot
                    self._alternar_bot(i)
                    # Termina el evento
                    return

            # Desactiva el campo de texto activo por defecto
            self.campo_activo = None
            # Revisa si se hizo clic en el nombre de algún jugador para editarlo
            for idx, r_nom in enumerate(self.rects_nombres):
                # Si el clic fue en esa tarjeta de nombre
                if r_nom.collidepoint(pos):
                    # Activa ese campo para escribir
                    self.campo_activo = idx
                    # Deja de buscar
                    break

            # Si hizo clic en el botón INICIAR
            if hasattr(self, 'btn_iniciar_inst') and self.btn_iniciar_inst.es_cliqueado(evento):
                # Valida y comienza la partida
                self._crear_y_comenzar_partida()

            # Si hizo clic en el botón volver (X)
            elif hasattr(self, 'btn_volver_inst') and self.btn_volver_inst.es_cliqueado(evento):
                # CU-01 y CU-04, alternativa cancelar: se descartan los datos y se vuelve al menú
                # Limpia mensajes de error
                self.mensaje_error = ""
                # Cancela la selección de colores en el gestor
                self.gestor.cancelarSeleccionColores()
                # Vuelve a la pantalla del menú principal
                self.interfaz.ir_a("MENU")

        # Si se presionó Escape y no se estaba editando ningún texto
        elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE and self.campo_activo is None:
            # Limpia los errores
            self.mensaje_error = ""
            # Cancela la selección en el gestor
            self.gestor.cancelarSeleccionColores()
            # Vuelve al menú principal
            self.interfaz.ir_a("MENU")

        # Si se presionó una tecla mientras se editaba el nombre de un jugador
        elif evento.type == pygame.KEYDOWN and self.campo_activo is not None:
            # Guarda el índice del jugador que se está editando
            idx = self.campo_activo
            # Si se presionó la tecla de borrar (Backspace)
            if evento.key == pygame.K_BACKSPACE:
                # Quita la última letra del nombre
                self.nombres[idx] = self.nombres[idx][:-1]
            # Si se presionó Enter o Tabulador
            elif evento.key in (pygame.K_RETURN, pygame.K_TAB):
                # Desactiva la edición del campo
                self.campo_activo = None
            # Para cualquier otra tecla escrita
            else:
                # Si el nombre tiene menos de 12 letras y el caracter es legible
                if len(self.nombres[idx]) < 12 and evento.unicode.isprintable():
                    # Agrega la letra al final del nombre
                    self.nombres[idx] += evento.unicode

    # Valida y crea la partida con los datos configurados
    def _crear_y_comenzar_partida(self):
        # DS N1: se configura una partida nueva con la cantidad, los nombres (CU-03) y los
        # colores (CU-04) de la pantalla; DS N5: el GameManager la valida e inicia.
        # Cancela cualquier partida previa que estuviera cargada
        self.gestor.cancelarPartida()
        # Prepara una nueva partida limpia en el gestor
        self.gestor.iniciarPartida()
        # Establece la cantidad de jugadores seleccionada
        self.gestor.configurarCantidadJugadores(self.cant_jugadores)
        # Registra el nombre y color de cada jugador
        for i in range(self.cant_jugadores):
            # Registra el nombre (None si es bot para que use el predeterminado)
            exito, mensaje = self.gestor.registrarNombre(None if self.es_bot_lista[i] else self.nombres[i], i)
            # Si el nombre es válido, asigna su color
            if exito:
                exito, mensaje = self.gestor.seleccionarColor(self.colores[i], i)
            # Si algo falló
            if not exito:
                # Guarda el mensaje de error y no continúa
                self.mensaje_error = mensaje
                # Sale de la función
                return

        # Da inicio formal a la partida en el gestor
        exito, mensaje = self.gestor.iniciarPartida()
        # Guarda el error si falló o borra el mensaje si tuvo éxito
        self.mensaje_error = "" if exito else mensaje
        # Si la partida inició con éxito
        if exito:
            # Pasa a la pantalla del juego
            self.interfaz.ir_a("JUEGO")


#__init__(): prepara la pantalla.
#reiniciar_formulario(): pone los valores iniciales.
#_sincronizar_partida(): actualiza la configuración de la partida.
#dibujar(): muestra la pantalla y sus botones.
#_cambiar_color(): cambia el color del jugador.
#_alternar_bot(): cambia entre persona y bot.
#manejar_evento(): detecta los clics y las teclas.
#_crear_y_comenzar_partida(): configura e inicia el juego.
