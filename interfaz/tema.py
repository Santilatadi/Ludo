"""
Modulo tema.py
Medidas, colores, fuentes e imágenes del diseño de Figma (Ing SW 2).

Todos los frames del Figma miden 1440x960. Las pantallas dibujan con las
coordenadas del Figma y estas funciones las llevan al tamaño de la ventana
(se mantiene la proporción y se centra), así la interfaz queda igual al diseño.
"""

# Funciones del sistema operativo para manejo de rutas de archivos
import os
# Expresiones regulares para verificar patrones de texto
import re

# Librería Pygame para gráficos y sonido
import pygame

# Importa la clase de colores del juego
from modelos.color import Color

# Ancho y alto del diseño original en Figma
ANCHO_FIGMA, ALTO_FIGMA = 1440, 960

# Colores del Figma
# Color violeta oscuro de fondo principal
FONDO = (46, 20, 90)                    # #2e145a
# Degradado azul de dos tonos para paneles y botones
GRADIENTE = ((66, 103, 254), (11, 27, 93))       # #4267fe -> #0b1b5d (paneles y botones)
# Degradado amarillo a rojo para el botón iniciar
GRADIENTE_INICIAR = ((254, 216, 66), (246, 36, 39))  # #fed842 -> #f62427
# Color rojo para bordes
ROJO_BORDE = (213, 27, 27)              # #d51b1b
# Color amarillo para bordes
AMARILLO_BORDE = (235, 229, 35)         # #ebe523
# Color amarillo brillante
AMARILLO = (253, 245, 32)               # #fdf520
# Color gris claro
GRIS = (217, 217, 217)                  # #d9d9d9
# Color negro estándar
NEGRO = (0, 0, 0)
# Color blanco estándar
BLANCO = (255, 255, 255)
# Color azul brillante
AZUL = (66, 103, 254)                   # #4267fe
# Color rojo para textos llamativos
ROJO_TEXTO = (250, 23, 27)              # #fa171b
# Color naranja para resaltar el dado activo
DADO_ACTIVO = (244, 179, 59)            # dado del jugador con el turno
# Color amarillo brillante para resaltar el turno actual
TURNO = (255, 225, 0)                   # #ffe100 (etiqueta del jugador con el turno)

# Color de cada jugador en las píldoras de configuración y en las etiquetas del tablero
# Diccionario que relaciona cada color del juego con su código RGB
COLOR_JUGADOR = {
    # Color rojo del jugador
    Color.ROJO: (255, 4, 4),            # #ff0404
    # Color verde del jugador
    Color.VERDE: (52, 168, 83),         # #34a853
    # Color azul del jugador
    Color.AZUL: (66, 133, 244),         # #4285f4
    # Color amarillo del jugador
    Color.AMARILLO: (235, 229, 35),     # #ebe523
}
# Bordes de los dados y nombres en "Continuar Partida"
# Colores para los dados según el jugador
COLOR_DADO = {Color.ROJO: (255, 4, 4), Color.VERDE: (9, 201, 15), Color.AZUL: (66, 103, 254),
              Color.AMARILLO: (253, 245, 32)}
# Colores para los nombres de los jugadores
COLOR_NOMBRE = {Color.ROJO: (255, 4, 4), Color.VERDE: (9, 201, 15), Color.AZUL: (66, 133, 244),
                Color.AMARILLO: (253, 245, 32)}

# Nombre en español de cada color
NOMBRE_COLOR = {Color.ROJO: "Rojo", Color.VERDE: "Verde", Color.AZUL: "Azul", Color.AMARILLO: "Amarillo"}

# Ruta a la carpeta de recursos como imágenes y tipografías
_ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
# Nombres de los archivos de fuentes utilizados
_FUENTES = {"goldman": "Goldman-Bold.ttf", "fredoka": "FredokaOne-Regular.ttf"}
# Memoria temporal para fuentes ya cargadas
_cache_fuentes = {}
# Memoria temporal para textos ya dibujados
_cache_textos = {}
# Memoria temporal para paneles ya generados
_cache_paneles = {}
# Memoria temporal para imágenes cargadas
_cache_imagenes = {}


# Vacía todas las memorias temporales de recursos
def limpiar_cache():
    """Limpia todos los caches de superficies y fuentes al reiniciar Pygame."""
    # Borra las fuentes guardadas
    _cache_fuentes.clear()
    # Borra los textos guardados
    _cache_textos.clear()
    # Borra los paneles guardados
    _cache_paneles.clear()
    # Borra las imágenes guardadas
    _cache_imagenes.clear()


# Guarda la función original de inicialización de Pygame
_orig_pygame_init = pygame.init
# Intercepta el inicio de Pygame para limpiar la memoria temporal
def _hooked_pygame_init(*args, **kwargs):
    # Limpia las memorias temporales
    limpiar_cache()
    # Llama a la función de inicio original
    return _orig_pygame_init(*args, **kwargs)
# Reemplaza la función original por la interceptada
pygame.init = _hooked_pygame_init

# Guarda la función original de cierre de Pygame
_orig_pygame_quit = pygame.quit
# Intercepta el cierre de Pygame para limpiar la memoria temporal
def _hooked_pygame_quit(*args, **kwargs):
    # Limpia las memorias temporales
    limpiar_cache()
    # Llama a la función de cierre original
    return _orig_pygame_quit(*args, **kwargs)
# Reemplaza la función original por la interceptada
pygame.quit = _hooked_pygame_quit

# Si el módulo de fuentes de Pygame existe
if hasattr(pygame, "font") and hasattr(pygame.font, "init"):
    # Guarda la función original de inicio de fuentes
    _orig_font_init = pygame.font.init
    # Intercepta el inicio del módulo de fuentes
    def _hooked_font_init(*args, **kwargs):
        # Limpia las fuentes guardadas
        _cache_fuentes.clear()
        # Limpia los textos guardados
        _cache_textos.clear()
        # Llama a la inicialización original
        return _orig_font_init(*args, **kwargs)
    # Reemplaza la función original
    pygame.font.init = _hooked_font_init

# Si el módulo de fuentes de Pygame tiene función de cierre
if hasattr(pygame, "font") and hasattr(pygame.font, "quit"):
    # Guarda la función original de cierre de fuentes
    _orig_font_quit = pygame.font.quit
    # Intercepta el cierre del módulo de fuentes
    def _hooked_font_quit(*args, **kwargs):
        # Limpia las fuentes guardadas
        _cache_fuentes.clear()
        # Limpia los textos guardados
        _cache_textos.clear()
        # Llama al cierre original
        return _orig_font_quit(*args, **kwargs)
    # Reemplaza la función original
    pygame.font.quit = _hooked_font_quit


# ---------------------------------------------------------------------------
# Escala del Figma a la ventana
# ---------------------------------------------------------------------------

# Calcula la escala y los márgenes para centrar el diseño en la ventana
def escala(pantalla) -> tuple[float, float, float]:
    # Obtiene el ancho y alto real de la ventana
    ancho, alto = pantalla.get_size()
    # Calcula el factor de escala proporcional
    esc = min(ancho / ANCHO_FIGMA, alto / ALTO_FIGMA)
    # Devuelve el factor de escala y los desplazamientos X e Y para centrar
    return esc, (ancho - ANCHO_FIGMA * esc) / 2, (alto - ALTO_FIGMA * esc) / 2


# Transforma coordenadas de Figma a un rectángulo adaptado a la ventana
def R(pantalla, x, y, w=0, h=0) -> pygame.Rect:
    """Rectángulo del Figma (x, y, ancho, alto) llevado a la ventana."""
    # Obtiene la escala y los desplazamientos
    esc, ox, oy = escala(pantalla)
    # Calcula la posición X e Y escalada
    x0, y0 = round(ox + x * esc), round(oy + y * esc)
    # Devuelve el rectángulo escalado con tamaño mínimo de 1 píxel
    return pygame.Rect(x0, y0, max(1, round(ox + (x + w) * esc) - x0), max(1, round(oy + (y + h) * esc) - y0))


# Transforma un punto (X, Y) de Figma a píxeles de la ventana
def P(pantalla, x, y) -> tuple[int, int]:
    # Obtiene la escala y los desplazamientos
    esc, ox, oy = escala(pantalla)
    # Devuelve el punto redondeado a enteros
    return round(ox + x * esc), round(oy + y * esc)


# Escala un valor de tamaño (texto, borde, radio) según la ventana
def T(pantalla, valor) -> int:
    """Una medida del Figma (tamaño de letra, grosor de borde, radio) en píxeles de la ventana."""
    # Multiplica por la escala y asegura que valga al menos 1
    return max(1, round(valor * escala(pantalla)[0]))


# ---------------------------------------------------------------------------
# Fuentes, textos e imágenes
# ---------------------------------------------------------------------------

# Obtiene un objeto fuente cargado y optimizado en memoria
def fuente(tam: int, familia: str = "goldman") -> pygame.font.Font:
    # Si las fuentes de Pygame no están iniciadas, las inicia
    if not pygame.font.get_init():
        # Inicializa el subsistema de fuentes
        pygame.font.init()
    # Clave para identificar la fuente en memoria
    clave = (familia, tam)
    # Busca si ya está cargada
    f = _cache_fuentes.get(clave)
    # Si aún no estaba en memoria
    if f is None:
        # Arma la ruta al archivo de la fuente
        ruta = os.path.join(_ASSETS, _FUENTES[familia])
        # Carga la tipografía del archivo o usa Arial si no existe
        f = pygame.font.Font(ruta, tam) if os.path.exists(ruta) else pygame.font.SysFont("Arial", tam, bold=True)
        # La guarda en memoria para usarla después
        _cache_fuentes[clave] = f
        # Limpia textos anteriores para liberar espacio
        _cache_textos.clear()
    # Devuelve la fuente lista para escribir
    return f


# Genera una imagen con el texto y opcionalmente un contorno
def render_texto(contenido, tam, color=BLANCO, contorno=None, grosor=0, familia="goldman") -> pygame.Surface:
    """Texto con trazo (stroke) alrededor, como los textos del Figma. Se guarda en caché."""
    # Clave única para guardar este texto en memoria
    clave = (contenido, tam, tuple(color), tuple(contorno) if contorno else None, grosor, familia)
    # Busca si el texto ya fue dibujado antes
    surf = _cache_textos.get(clave)
    # Si no estaba en memoria
    if surf is None:
        # Obtiene la fuente correspondiente
        f = fuente(tam, familia)
        # Dibuja el texto principal
        base = f.render(contenido, True, color)
        # Si tiene contorno y grosor especificado
        if contorno and grosor:
            # Guarda el grosor del contorno
            g = grosor
            # Crea una superficie transparente más grande para alojar el contorno
            surf = pygame.Surface((base.get_width() + 2 * g, base.get_height() + 2 * g), pygame.SRCALPHA)
            # Dibuja el texto con el color del contorno
            sombra = f.render(contenido, True, contorno)
            # Dibuja copias alrededor en forma circular para formar el contorno
            for dx in range(-g, g + 1):
                # Recorre verticalmente
                for dy in range(-g, g + 1):
                    # Si el punto cae dentro del círculo del radio
                    if dx * dx + dy * dy <= g * g:
                        # Estampa el texto de contorno
                        surf.blit(sombra, (g + dx, g + dy))
            # Dibuja el texto principal encima del contorno
            surf.blit(base, (g, g))
        # Si no tiene contorno
        else:
            # Usa el texto simple directamente
            surf = base
        # Si la memoria de textos supera los 600 elementos
        if len(_cache_textos) > 600:
            # Limpia la memoria para evitar saturación
            _cache_textos.clear()
        # Guarda la superficie en memoria temporal
        _cache_textos[clave] = surf
    # Devuelve la imagen del texto lista
    return surf


# Dibuja un texto en pantalla en una posición determinada
def texto(pantalla, contenido, tam, centro, color=BLANCO, contorno=None, grosor=2, izquierda=False,
          familia="goldman"):
    """Dibuja un texto centrado en `centro` (o con su borde izquierdo ahí si izquierda=True)."""
    # Renderiza la imagen del texto con su contorno
    surf = render_texto(contenido, tam, color, contorno, grosor if contorno else 0, familia)
    # Posiciona el rectángulo alineado a la izquierda o al centro
    rect = surf.get_rect(midleft=centro) if izquierda else surf.get_rect(center=centro)
    # Dibuja el texto en la pantalla
    pantalla.blit(surf, rect)
    # Devuelve el rectángulo ocupado
    return rect


# Dibuja un texto usando las medidas exactas del diseño de Figma
def texto_figma(pantalla, contenido, x, y, tam, color=BLANCO, contorno=NEGRO, trazo=4, centrado_en=None,
                familia="goldman"):
    """Texto ubicado como en el Figma: (x, y) es la esquina superior izquierda de la caja de texto.
    Con centrado_en=(cx, cy) se centra en ese punto del Figma."""
    # Escala el tamaño del texto y el grosor del contorno
    t, g = T(pantalla, tam), (T(pantalla, trazo / 2) if contorno else 0)
    # Genera la imagen del texto con los estilos dados
    surf = render_texto(contenido, t, color, contorno, g, familia)
    # Si se especificó un punto central
    if centrado_en is not None:
        # Centra el texto en esa posición
        rect = surf.get_rect(center=P(pantalla, *centrado_en))
    # Si se ubicó por esquina superior izquierda
    else:
        # Coloca la esquina superior izquierda
        rect = surf.get_rect(topleft=P(pantalla, x, y))
        # Ajusta el margen por el grosor del contorno
        rect.move_ip(-g, -g)
    # Dibuja el texto en pantalla
    pantalla.blit(surf, rect)
    # Devuelve el rectángulo ocupado
    return rect


# Carga, escala y guarda en memoria una imagen de los recursos
def imagen(nombre: str, tam=None) -> pygame.Surface:
    """Imagen de assets/ (exportada del Figma), escalada y guardada en caché."""
    # Clave única para identificar la imagen
    clave = (nombre, tam)
    # Busca si ya está en memoria con ese tamaño
    surf = _cache_imagenes.get(clave)
    # Si no estaba en memoria
    if surf is None:
        # Busca la imagen original sin escalar
        original = _cache_imagenes.get((nombre, None))
        # Si tampoco estaba la original
        if original is None:
            # Carga la imagen desde el archivo en assets
            original = pygame.image.load(os.path.join(_ASSETS, nombre))
            # Guarda la imagen original en memoria
            _cache_imagenes[(nombre, None)] = original
        # Si se pidió tamaño específico la escala suavemente, sino usa la original
        surf = original if tam is None else pygame.transform.smoothscale(original, (max(1, tam[0]), max(1, tam[1])))
        # Si hay más de 80 imágenes en memoria
        if len(_cache_imagenes) > 80:
            # Limpia la memoria temporal
            _cache_imagenes.clear()
            # Conserva la imagen original
            _cache_imagenes[(nombre, None)] = original
        # Guarda la imagen procesada en memoria
        _cache_imagenes[clave] = surf
    # Devuelve la imagen lista
    return surf


# ---------------------------------------------------------------------------
# Formas
# ---------------------------------------------------------------------------

# Crea una superficie con degradado de colores de izquierda a derecha
def degradado(tam, inicio, fin) -> pygame.Surface:
    """Degradé horizontal de izquierda a derecha, como los del Figma (RGB o RGBA)."""
    # Separa ancho y alto
    w, h = tam
    # Crea una superficie con canal de transparencia
    surf = pygame.Surface((max(1, w), max(1, h)), pygame.SRCALPHA)
    # Asegura que el color de inicio tenga canal alfa (transparencia)
    a = inicio if len(inicio) == 4 else (*inicio, 255)
    # Asegura que el color final tenga canal alfa
    b = fin if len(fin) == 4 else (*fin, 255)
    # Recorre cada columna de píxeles
    for x in range(w):
        # Calcula la proporción de transición entre 0 y 1
        t = x / max(1, w - 1)
        # Interpola los canales de color suavemente
        col = tuple(int(a[k] + (b[k] - a[k]) * t) for k in range(4))
        # Dibuja una línea vertical con el color resultante
        pygame.draw.line(surf, col, (x, 0), (x, h))
    # Devuelve la superficie con el degradado
    return surf


# Dibuja un panel con fondo degradado o sólido, bordes y esquinas redondeadas
def panel(pantalla, rect, colores=GRADIENTE, borde=ROJO_BORDE, radio=0, grosor=3):
    """Rectángulo con degradé vertical (o color liso), esquinas redondeadas y borde."""
    # Convierte a objeto Rect de Pygame
    rect = pygame.Rect(rect)
    # Si se pasó un solo color, lo duplica para degradado plano
    if len(colores) in (3, 4) and isinstance(colores[0], int):
        # Convierte en tupla de dos colores idénticos
        colores = (colores, colores)
    # Clave única para guardar el panel en memoria
    clave = (rect.size, tuple(colores[0]), tuple(colores[1]), radio)
    # Busca si el panel ya existe en memoria
    cuerpo = _cache_paneles.get(clave)
    # Si no estaba en memoria
    if cuerpo is None:
        # Genera el degradado con los colores pedidos
        cuerpo = degradado(rect.size, colores[0], colores[1])
        # Si tiene esquinas redondeadas
        if radio:
            # Crea una máscara transparente del mismo tamaño
            mascara = pygame.Surface(rect.size, pygame.SRCALPHA)
            # Dibuja un rectángulo redondeado opaco en la máscara
            pygame.draw.rect(mascara, (255, 255, 255, 255), (0, 0, *rect.size), border_radius=radio)
            # Aplica la máscara recortando las esquinas exteriores
            cuerpo.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # Si hay más de 64 paneles en memoria
        if len(_cache_paneles) > 64:
            # Limpia la memoria temporal
            _cache_paneles.clear()
        # Guarda el panel en memoria
        _cache_paneles[clave] = cuerpo
    # Dibuja el panel en pantalla en la posición dada
    pantalla.blit(cuerpo, rect.topleft)
    # Si tiene borde y grosor
    if grosor and borde:
        # Dibuja el contorno con el color y radio dados
        pygame.draw.rect(pantalla, borde, rect, width=grosor, border_radius=radio)


# Dibuja un panel escalando automáticamente las coordenadas de Figma
def panel_figma(pantalla, x, y, w, h, colores=GRADIENTE, borde=ROJO_BORDE, trazo=4, radio=0):
    # Calcula el rectángulo escalado
    r = R(pantalla, x, y, w, h)
    # Dibuja el panel adaptado
    panel(pantalla, r, colores, borde, T(pantalla, radio) if radio else 0, T(pantalla, trazo) if trazo else 0)
    # Devuelve el rectángulo resultante
    return r


# Dibuja una capa negra semitransparente sobre toda la pantalla
def oscurecer(pantalla, alpha=128):
    """Capa negra al 50 % que el Figma pone detrás de las ventanas emergentes."""
    # Crea una superficie del tamaño completo de la pantalla con canal de transparencia
    capa = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA)
    # Llena la superficie con color negro y la transparencia indicada
    capa.fill((0, 0, 0, alpha))
    # Superpone la capa oscura sobre la pantalla
    pantalla.blit(capa, (0, 0))


# Dibuja una línea horizontal escalando las medidas de Figma
def linea_figma(pantalla, x, y, largo, color=(255, 4, 4), trazo=4):
    # Dibuja la línea entre el punto inicial y el punto final escalados
    pygame.draw.line(pantalla, color, P(pantalla, x, y), P(pantalla, x + largo, y), T(pantalla, trazo))


# Dibuja una cruz "X" según el diseño de Figma para botones de cerrar
def cruz_figma(pantalla, x, y, lado=75, trazo=15, color=NEGRO) -> pygame.Rect:
    """La "X" negra de cerrar del Figma (Reglas y Estadísticas)."""
    # Calcula el rectángulo escalado
    r = R(pantalla, x, y, lado, lado)
    # Calcula el grosor escalado
    g = T(pantalla, trazo)
    # Reduce un poco el área para dejar margen interior
    m = r.inflate(-r.width // 4, -r.height // 4)
    # Dibuja la primera línea diagonal de la cruz
    pygame.draw.line(pantalla, color, m.topleft, m.bottomright, g)
    # Dibuja la segunda línea diagonal de la cruz
    pygame.draw.line(pantalla, color, m.topright, m.bottomleft, g)
    # Devuelve el rectángulo que encierra la cruz
    return r


# Dibuja una flecha triangular apuntando a la izquierda o a la derecha
def flecha(pantalla, rect, derecha: bool, color, borde=NEGRO, grosor=2):
    # Convierte a objeto Rect de Pygame
    r = pygame.Rect(rect)
    # Si la flecha apunta hacia la derecha
    if derecha:
        # Define los 3 vértices del triángulo hacia la derecha
        puntos = [(r.x, r.y), (r.right, r.centery), (r.x, r.bottom)]
    # Si apunta hacia la izquierda
    else:
        # Define los 3 vértices del triángulo hacia la izquierda
        puntos = [(r.right, r.y), (r.x, r.centery), (r.right, r.bottom)]
    # Dibuja el triángulo relleno con su color
    pygame.draw.polygon(pantalla, color, puntos)
    # Si tiene borde
    if borde:
        # Dibuja el contorno del triángulo
        pygame.draw.polygon(pantalla, borde, puntos, width=grosor)


# Comprueba si un jugador es un bot controlado por la máquina
def es_bot(jugador) -> bool:
    """Los jugadores de la consola se registran como "Bot n" (CU-03, alternativa C)."""
    # Verifica si el nombre del jugador cumple con el patrón "Bot número"
    return bool(jugador and re.fullmatch(r"Bot \d+", jugador.nombre or ""))

#**limpiar_cache():** Borra los elementos guardados temporalmente.
#**_hooked_pygame_init():** Limpia la memoria temporal cuando inicia Pygame.
#**_hooked_pygame_quit():** Limpia la memoria temporal cuando se cierra Pygame.
#**_hooked_font_init():** Limpia los textos y las fuentes guardadas cuando se inicializan las fuentes.
#**_hooked_font_quit():** Limpia las fuentes y los textos cuando se cierran.
#**escala():** Calcula cuánto deben ajustarse los elementos al tamaño de la ventana.
#**R():** Ajusta el tamaño y la posición de los rectángulos.
#**P():** Ajusta la posición de los elementos.
#**T():** Ajusta el tamaño de los textos y los bordes.
#**fuente():** Carga las fuentes de texto.
#**render_texto():** Prepara un texto con su color y contorno.
#**texto():** Dibuja textos en la pantalla.
#**texto_figma():** Dibuja textos respetando el diseño de Figma.
#**imagen():** Carga y ajusta imágenes.
#**degradado():** Crea una transición entre colores.
#**panel():** Dibuja paneles con fondo, bordes y esquinas redondeadas.
#**panel_figma():** Dibuja paneles respetando las medidas de Figma.
#**oscurecer():** Oscurece el fondo cuando aparece una ventana emergente.
#**linea_figma():** Dibuja líneas en la pantalla.
#**cruz_figma():** Dibuja una cruz para cerrar ventanas.
#**flecha():** Dibuja flechas hacia la izquierda o derecha.
#**es_bot():** Comprueba si un jugador es controlado por la computadora.
#En resumen: tema.py contiene los colores, las fuentes y las funciones que permiten dibujar todas las pantallas del Ludo con el mismo diseño.