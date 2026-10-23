"""
Modulo tema.py
Medidas, colores, fuentes e imágenes del diseño de Figma (Ing SW 2).

Todos los frames del Figma miden 1440x960. Las pantallas dibujan con las
coordenadas del Figma y estas funciones las llevan al tamaño de la ventana
(se mantiene la proporción y se centra), así la interfaz queda igual al diseño.
"""

import os
import re

import pygame

from modelos.color import Color

ANCHO_FIGMA, ALTO_FIGMA = 1440, 960

# Colores del Figma
FONDO = (46, 20, 90)                    # #2e145a
GRADIENTE = ((66, 103, 254), (11, 27, 93))       # #4267fe -> #0b1b5d (paneles y botones)
GRADIENTE_INICIAR = ((254, 216, 66), (246, 36, 39))  # #fed842 -> #f62427
ROJO_BORDE = (213, 27, 27)              # #d51b1b
AMARILLO_BORDE = (235, 229, 35)         # #ebe523
AMARILLO = (253, 245, 32)               # #fdf520
GRIS = (217, 217, 217)                  # #d9d9d9
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
AZUL = (66, 103, 254)                   # #4267fe
ROJO_TEXTO = (250, 23, 27)              # #fa171b
DADO_ACTIVO = (244, 179, 59)            # dado del jugador con el turno
TURNO = (255, 225, 0)                   # #ffe100 (etiqueta del jugador con el turno)

# Color de cada jugador en las píldoras de configuración y en las etiquetas del tablero
COLOR_JUGADOR = {
    Color.ROJO: (255, 4, 4),            # #ff0404
    Color.VERDE: (52, 168, 83),         # #34a853
    Color.AZUL: (66, 133, 244),         # #4285f4
    Color.AMARILLO: (235, 229, 35),     # #ebe523
}
# Bordes de los dados y nombres en "Continuar Partida"
COLOR_DADO = {Color.ROJO: (255, 4, 4), Color.VERDE: (9, 201, 15), Color.AZUL: (66, 103, 254),
              Color.AMARILLO: (253, 245, 32)}
COLOR_NOMBRE = {Color.ROJO: (255, 4, 4), Color.VERDE: (9, 201, 15), Color.AZUL: (66, 133, 244),
                Color.AMARILLO: (253, 245, 32)}

NOMBRE_COLOR = {Color.ROJO: "Rojo", Color.VERDE: "Verde", Color.AZUL: "Azul", Color.AMARILLO: "Amarillo"}

_ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
_FUENTES = {"goldman": "Goldman-Bold.ttf", "fredoka": "FredokaOne-Regular.ttf"}
_cache_fuentes = {}
_cache_textos = {}
_cache_paneles = {}
_cache_imagenes = {}


# ---------------------------------------------------------------------------
# Escala del Figma a la ventana
# ---------------------------------------------------------------------------

def escala(pantalla) -> tuple[float, float, float]:
    ancho, alto = pantalla.get_size()
    esc = min(ancho / ANCHO_FIGMA, alto / ALTO_FIGMA)
    return esc, (ancho - ANCHO_FIGMA * esc) / 2, (alto - ALTO_FIGMA * esc) / 2


def R(pantalla, x, y, w=0, h=0) -> pygame.Rect:
    """Rectángulo del Figma (x, y, ancho, alto) llevado a la ventana."""
    esc, ox, oy = escala(pantalla)
    x0, y0 = round(ox + x * esc), round(oy + y * esc)
    return pygame.Rect(x0, y0, max(1, round(ox + (x + w) * esc) - x0), max(1, round(oy + (y + h) * esc) - y0))


def P(pantalla, x, y) -> tuple[int, int]:
    esc, ox, oy = escala(pantalla)
    return round(ox + x * esc), round(oy + y * esc)


def T(pantalla, valor) -> int:
    """Una medida del Figma (tamaño de letra, grosor de borde, radio) en píxeles de la ventana."""
    return max(1, round(valor * escala(pantalla)[0]))


# ---------------------------------------------------------------------------
# Fuentes, textos e imágenes
# ---------------------------------------------------------------------------

def fuente(tam: int, familia: str = "goldman") -> pygame.font.Font:
    clave = (familia, tam)
    f = _cache_fuentes.get(clave)
    if f is not None:
        try:
            f.render(" ", True, NEGRO)
        except pygame.error:
            f = None        # pygame se cerró y volvió a iniciar: la fuente ya no sirve
    if f is None:
        ruta = os.path.join(_ASSETS, _FUENTES[familia])
        f = pygame.font.Font(ruta, tam) if os.path.exists(ruta) else pygame.font.SysFont("Arial", tam, bold=True)
        _cache_fuentes[clave] = f
        _cache_textos.clear()
    return f


def render_texto(contenido, tam, color=BLANCO, contorno=None, grosor=0, familia="goldman") -> pygame.Surface:
    """Texto con trazo (stroke) alrededor, como los textos del Figma. Se guarda en caché."""
    clave = (contenido, tam, tuple(color), tuple(contorno) if contorno else None, grosor, familia)
    surf = _cache_textos.get(clave)
    if surf is None:
        f = fuente(tam, familia)
        base = f.render(contenido, True, color)
        if contorno and grosor:
            g = grosor
            surf = pygame.Surface((base.get_width() + 2 * g, base.get_height() + 2 * g), pygame.SRCALPHA)
            sombra = f.render(contenido, True, contorno)
            for dx in range(-g, g + 1):
                for dy in range(-g, g + 1):
                    if dx * dx + dy * dy <= g * g:
                        surf.blit(sombra, (g + dx, g + dy))
            surf.blit(base, (g, g))
        else:
            surf = base
        if len(_cache_textos) > 600:
            _cache_textos.clear()
        _cache_textos[clave] = surf
    return surf


def texto(pantalla, contenido, tam, centro, color=BLANCO, contorno=None, grosor=2, izquierda=False,
          familia="goldman"):
    """Dibuja un texto centrado en `centro` (o con su borde izquierdo ahí si izquierda=True)."""
    surf = render_texto(contenido, tam, color, contorno, grosor if contorno else 0, familia)
    rect = surf.get_rect(midleft=centro) if izquierda else surf.get_rect(center=centro)
    pantalla.blit(surf, rect)
    return rect


def texto_figma(pantalla, contenido, x, y, tam, color=BLANCO, contorno=NEGRO, trazo=4, centrado_en=None,
                familia="goldman"):
    """Texto ubicado como en el Figma: (x, y) es la esquina superior izquierda de la caja de texto.
    Con centrado_en=(cx, cy) se centra en ese punto del Figma."""
    t, g = T(pantalla, tam), (T(pantalla, trazo / 2) if contorno else 0)
    surf = render_texto(contenido, t, color, contorno, g, familia)
    if centrado_en is not None:
        rect = surf.get_rect(center=P(pantalla, *centrado_en))
    else:
        rect = surf.get_rect(topleft=P(pantalla, x, y))
        rect.move_ip(-g, -g)
    pantalla.blit(surf, rect)
    return rect


def imagen(nombre: str, tam=None) -> pygame.Surface:
    """Imagen de assets/ (exportada del Figma), escalada y guardada en caché."""
    clave = (nombre, tam)
    surf = _cache_imagenes.get(clave)
    if surf is None:
        original = _cache_imagenes.get((nombre, None))
        if original is None:
            original = pygame.image.load(os.path.join(_ASSETS, nombre))
            _cache_imagenes[(nombre, None)] = original
        surf = original if tam is None else pygame.transform.smoothscale(original, (max(1, tam[0]), max(1, tam[1])))
        if len(_cache_imagenes) > 80:
            _cache_imagenes.clear()
            _cache_imagenes[(nombre, None)] = original
        _cache_imagenes[clave] = surf
    return surf


# ---------------------------------------------------------------------------
# Formas
# ---------------------------------------------------------------------------

def degradado(tam, inicio, fin) -> pygame.Surface:
    """Degradé horizontal de izquierda a derecha, como los del Figma (RGB o RGBA)."""
    w, h = tam
    surf = pygame.Surface((max(1, w), max(1, h)), pygame.SRCALPHA)
    a = inicio if len(inicio) == 4 else (*inicio, 255)
    b = fin if len(fin) == 4 else (*fin, 255)
    for x in range(w):
        t = x / max(1, w - 1)
        col = tuple(int(a[k] + (b[k] - a[k]) * t) for k in range(4))
        pygame.draw.line(surf, col, (x, 0), (x, h))
    return surf


def panel(pantalla, rect, colores=GRADIENTE, borde=ROJO_BORDE, radio=0, grosor=3):
    """Rectángulo con degradé vertical (o color liso), esquinas redondeadas y borde."""
    rect = pygame.Rect(rect)
    if len(colores) in (3, 4) and isinstance(colores[0], int):
        colores = (colores, colores)
    clave = (rect.size, tuple(colores[0]), tuple(colores[1]), radio)
    cuerpo = _cache_paneles.get(clave)
    if cuerpo is None:
        cuerpo = degradado(rect.size, colores[0], colores[1])
        if radio:
            mascara = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(mascara, (255, 255, 255, 255), (0, 0, *rect.size), border_radius=radio)
            cuerpo.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        if len(_cache_paneles) > 64:
            _cache_paneles.clear()
        _cache_paneles[clave] = cuerpo
    pantalla.blit(cuerpo, rect.topleft)
    if grosor and borde:
        pygame.draw.rect(pantalla, borde, rect, width=grosor, border_radius=radio)


def panel_figma(pantalla, x, y, w, h, colores=GRADIENTE, borde=ROJO_BORDE, trazo=4, radio=0):
    r = R(pantalla, x, y, w, h)
    panel(pantalla, r, colores, borde, T(pantalla, radio) if radio else 0, T(pantalla, trazo) if trazo else 0)
    return r


def oscurecer(pantalla, alpha=128):
    """Capa negra al 50 % que el Figma pone detrás de las ventanas emergentes."""
    capa = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA)
    capa.fill((0, 0, 0, alpha))
    pantalla.blit(capa, (0, 0))


def linea_figma(pantalla, x, y, largo, color=(255, 4, 4), trazo=4):
    pygame.draw.line(pantalla, color, P(pantalla, x, y), P(pantalla, x + largo, y), T(pantalla, trazo))


def cruz_figma(pantalla, x, y, lado=75, trazo=15, color=NEGRO) -> pygame.Rect:
    """La "X" negra de cerrar del Figma (Reglas y Estadísticas)."""
    r = R(pantalla, x, y, lado, lado)
    g = T(pantalla, trazo)
    m = r.inflate(-r.width // 4, -r.height // 4)
    pygame.draw.line(pantalla, color, m.topleft, m.bottomright, g)
    pygame.draw.line(pantalla, color, m.topright, m.bottomleft, g)
    return r


def flecha(pantalla, rect, derecha: bool, color, borde=NEGRO, grosor=2):
    r = pygame.Rect(rect)
    if derecha:
        puntos = [(r.x, r.y), (r.right, r.centery), (r.x, r.bottom)]
    else:
        puntos = [(r.right, r.y), (r.x, r.centery), (r.right, r.bottom)]
    pygame.draw.polygon(pantalla, color, puntos)
    if borde:
        pygame.draw.polygon(pantalla, borde, puntos, width=grosor)


def es_bot(jugador) -> bool:
    """Los jugadores de la consola se registran como "Bot n" (CU-03, alternativa C)."""
    return bool(jugador and re.fullmatch(r"Bot \d+", jugador.nombre or ""))
