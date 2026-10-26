"""
Modulo efectos.py
Sistema de partículas, animaciones visuales avanzadas y utilidades de renderizado.
Proporciona fondos dinámicos, glassmorphism, resplandores neon y física de confeti.
"""

# Importa math para cálculos trigonométricos (seno, coseno, distancias)
import math
# Importa random para generar variaciones aleatorias en las partículas
import random
# Importa pygame para renderizado gráfico
import pygame


# Representa una sola partícula individual (círculo, confeti o estrella)
class Particula:
    # Constructor: inicializa posición, velocidad, color, tamaño, vida y tipo
    def __init__(self, x, y, vx, vy, color, tam, vida, gravedad=0.0, tipo="circulo"):
        # Posición horizontal en pantalla
        self.x = x
        # Posición vertical en pantalla
        self.y = y
        # Velocidad en el eje X
        self.vx = vx
        # Velocidad en el eje Y
        self.vy = vy
        # Color de la partícula
        self.color = color
        # Tamaño inicial para calcular el encogimiento
        self.tam_inicial = tam
        # Tamaño actual de la partícula
        self.tam = tam
        # Duración máxima en fotogramas
        self.vida_max = vida
        # Fotogramas restantes de vida
        self.vida = vida
        # Aceleración hacia abajo (gravedad)
        self.gravedad = gravedad
        # Forma de la partícula ("circulo", "confeti", "estrella")
        self.tipo = tipo
        # Ángulo inicial de rotación al azar (0 a 360 grados)
        self.rotacion = random.uniform(0, 360)
        # Velocidad de giro o rotación
        self.v_rot = random.uniform(-6, 6)

    # Actualiza la física de la partícula en cada fotograma
    def actualizar(self):
        # Mueve la posición en X según la velocidad
        self.x += self.vx
        # Mueve la posición en Y según la velocidad
        self.y += self.vy
        # Aplica la gravedad aumentando la velocidad de caída
        self.vy += self.gravedad
        # Reduce la vida en 1 fotograma
        self.vida -= 1
        # Gira la partícula
        self.rotacion += self.v_rot
        # Calcula el porcentaje de vida que le queda (de 1.0 a 0.0)
        progreso = max(0.0, self.vida / float(self.vida_max))
        # Reduce su tamaño progresivamente
        self.tam = self.tam_inicial * progreso

    # Dibuja la partícula en la pantalla según su tipo y transparencia
    def dibujar(self, pantalla):
        # Si se le acabó la vida o es microscópica, no se dibuja
        if self.vida <= 0 or self.tam <= 0.5:
            return

        # Calcula la transparencia alfa (se desvanece al morir)
        alpha = int(255 * (self.vida / float(self.vida_max)))
        # Extrae los componentes de color RGB
        r, g, b = self.color[:3]
        # Combina el color con su transparencia
        col_alpha = (r, g, b, alpha)

        # Si es de tipo confeti rectangular:
        if self.tipo == "confeti":
            # Crea una superficie pequeña con canal de transparencia
            surf = pygame.Surface((int(self.tam * 2), int(self.tam * 1.2)), pygame.SRCALPHA)
            # Pinta el rectángulo con su color y transparencia
            surf.fill(col_alpha)
            # Rota el confeti según su ángulo actual
            surf_rot = pygame.transform.rotate(surf, self.rotacion)
            # Dibuja el confeti rotado centrado en su posición
            pantalla.blit(surf_rot, surf_rot.get_rect(center=(int(self.x), int(self.y))))

        # Si es de tipo estrella de 5 puntas:
        elif self.tipo == "estrella":
            # Lista para almacenar los vértices de la estrella
            puntos = []
            # Centro de la estrella
            cx, cy = self.x, self.y
            # Radio exterior de las puntas
            rad = self.tam
            # Calcula los 10 puntos alternando radio externo e interno
            for i in range(10):
                r_i = rad if i % 2 == 0 else rad * 0.4
                ang = i * math.pi / 5 + math.radians(self.rotacion)
                puntos.append((cx + r_i * math.cos(ang), cy + r_i * math.sin(ang)))
            # Si tiene suficientes puntos, dibuja el polígono de la estrella
            if len(puntos) > 2:
                pygame.draw.polygon(pantalla, col_alpha, puntos)

        # Si es de tipo círculo u orbe:
        else:  # "circulo" / "orb"
            # Crea la superficie transparente
            surf = pygame.Surface((int(self.tam * 2), int(self.tam * 2)), pygame.SRCALPHA)
            # Dibuja el círculo en la superficie
            pygame.draw.circle(surf, col_alpha, (int(self.tam), int(self.tam)), int(self.tam))
            # Dibuja la superficie en la pantalla
            pantalla.blit(surf, (int(self.x - self.tam), int(self.y - self.tam)))


# Administrador que controla todas las partículas y efectos de fondo
class SistemaParticulas:
    # Constructor: inicializa las listas y genera las luces flotantes de fondo
    def __init__(self):
        # Lista de partículas temporales (confeti, estrellas, estelas)
        self.particulas = []
        # Lista de orbes luminosos que flotan en el fondo
        self.orbes_fondo = []
        # Crea los orbes iniciales
        self._generar_orbes_fondo()

    # Genera 25 orbes luminosos flotantes con colores y velocidades aleatorias
    def _generar_orbes_fondo(self):
        # Paleta de colores suaves para los orbes
        colores_orbes = [
            (255, 100, 150), (100, 180, 255), (120, 240, 150),
            (255, 220, 100), (200, 120, 255)
        ]
        # Genera 25 orbes con posiciones y oscilaciones aleatorias
        for _ in range(25):
            self.orbes_fondo.append({
                "x": random.uniform(0, 1280),
                "y": random.uniform(0, 820),
                "vx": random.uniform(-0.4, 0.4),
                "vy": random.uniform(-0.6, -0.1),
                "tam": random.uniform(3, 8),
                "color": random.choice(colores_orbes),
                "fase": random.uniform(0, math.pi * 2)
            })

    # Lanza una explosión de confeti de colores desde una posición dada
    def emitir_confeti(self, cx, cy, cantidad=60):
        # Colores festivos para el confeti
        colores = [(255, 60, 60), (60, 220, 100), (60, 140, 255), (255, 220, 40), (230, 80, 255), (255, 150, 40)]
        # Crea la cantidad solicitada de papelitos de confeti
        for _ in range(cantidad):
            ang = random.uniform(0, math.pi * 2)
            vel = random.uniform(3.0, 10.0)
            vx = math.cos(ang) * vel
            vy = math.sin(ang) * vel - random.uniform(2.0, 6.0)
            tam = random.uniform(4, 9)
            vida = random.randint(40, 90)
            col = random.choice(colores)
            # Agrega la partícula de confeti con gravedad
            self.particulas.append(Particula(cx, cy, vx, vy, col, tam, vida, gravedad=0.25, tipo="confeti"))

    # Emite chispas en forma de estrellas doradas
    def emitir_estrellas(self, cx, cy, cantidad=15, color=(255, 235, 50)):
        # Crea las estrellas con direcciones en abanico
        for _ in range(cantidad):
            ang = random.uniform(0, math.pi * 2)
            vel = random.uniform(1.5, 4.5)
            vx = math.cos(ang) * vel
            vy = math.sin(ang) * vel
            tam = random.uniform(5, 10)
            vida = random.randint(20, 45)
            # Agrega la partícula con forma de estrella
            self.particulas.append(Particula(cx, cy, vx, vy, color, tam, vida, gravedad=0.05, tipo="estrella"))

    # Crea un rastro luminoso detrás de una ficha en movimiento
    def emitir_estela_ficha(self, cx, cy, color):
        # Crea 2 pequeñas partículas de humo o luz
        for _ in range(2):
            vx = random.uniform(-0.8, 0.8)
            vy = random.uniform(-0.8, 0.8)
            tam = random.uniform(3, 6)
            vida = random.randint(12, 24)
            # Agrega la partícula circular suave
            self.particulas.append(Particula(cx, cy, vx, vy, color, tam, vida, gravedad=-0.02, tipo="circulo"))

    # Actualiza las posiciones y dibuja todas las partículas y fondos
    def actualizar_y_dibujar(self, pantalla):
        # Obtiene las dimensiones de la pantalla
        ancho, alto = pantalla.get_size()

        # Actualizar orbes de fondo
        for orb in self.orbes_fondo:
            # Mueve el orbe en X e Y
            orb["x"] += orb["vx"]
            orb["y"] += orb["vy"]
            # Avanza la fase de parpadeo suave
            orb["fase"] += 0.03

            # Si el orbe sale por arriba, reaparece abajo
            if orb["y"] < -20:
                orb["y"] = alto + 20
                orb["x"] = random.uniform(0, ancho)
            # Si sale por los laterales, reaparece en el lado opuesto
            if orb["x"] < -20:
                orb["x"] = ancho + 20
            elif orb["x"] > ancho + 20:
                orb["x"] = -20

            # Dibujar orbe tenue
            # Calcula la opacidad variable con la función seno
            alpha = int(120 + 80 * math.sin(orb["fase"]))
            r, g, b = orb["color"]
            # Modula ligeramente el tamaño para un efecto de respiración
            tam = orb["tam"] + 1.5 * math.sin(orb["fase"] * 0.5)

            # Crea la superficie del orbe y dibuja su brillo y núcleo
            surf = pygame.Surface((int(tam * 4), int(tam * 4)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (r, g, b, alpha // 3), (int(tam * 2), int(tam * 2)), int(tam * 2))
            pygame.draw.circle(surf, (r, g, b, alpha), (int(tam * 2), int(tam * 2)), int(tam))
            pantalla.blit(surf, (int(orb["x"] - tam * 2), int(orb["y"] - tam * 2)))

        # Actualizar partículas activas
        vivas = []
        # Recorre cada partícula activa
        for p in self.particulas:
            # Actualiza su física
            p.actualizar()
            # Si sigue con vida, la dibuja y la conserva
            if p.vida > 0 and p.tam > 0.5:
                p.dibujar(pantalla)
                vivas.append(p)
        # Reemplaza la lista solo con las partículas sobrevivientes
        self.particulas = vivas


# Dibuja un panel con estilo moderno traslúcido tipo vidrio
def dibujar_panel_glassmorphism(pantalla, rect, color_bg=(20, 30, 60, 180), color_borde=(255, 255, 255, 100), radio=16, grosor_borde=2):
    """Dibuja un contenedor con efecto de vidrio esmerilado (Glassmorphism) y sombra tenue."""
    # Crea la superficie transparente del tamaño del panel
    surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

    # Sombra de gota exterior
    # Crea una superficie para la sombra un poco más grande
    sombra = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
    pygame.draw.rect(sombra, (0, 0, 0, 80), (6, 6, rect.width, rect.height), border_radius=radio)
    pantalla.blit(sombra, (rect.x - 3, rect.y + 3))

    # Cuerpo principal traslúcido
    pygame.draw.rect(surf, color_bg, (0, 0, rect.width, rect.height), border_radius=radio)
    # Resplandor/Borde superior brillante
    pygame.draw.rect(surf, color_borde, (0, 0, rect.width, rect.height), width=grosor_borde, border_radius=radio)

    # Dibuja el panel terminado en la pantalla
    pantalla.blit(surf, (rect.x, rect.y))


# Renderiza texto con un efecto de aura o resplandor neon
def dibujar_texto_glow(pantalla, texto, fuente, x, y, color_texto=(255, 255, 255), color_resplandor=(0, 200, 255), grosor=3, centro=False):
    """Renderiza texto con resplandor luminoso suave a su alrededor."""
    # Renderiza la capa de texto frontal
    surf_base = fuente.render(texto, True, color_texto)
    # Obtiene ancho y alto del texto
    w, h = surf_base.get_size()

    # Crea la superficie expandida para que quepa el resplandor
    surf_glow = pygame.Surface((w + grosor * 4, h + grosor * 4), pygame.SRCALPHA)
    r_g, g_g, b_g = color_resplandor[:3]

    # Dibuja copias difuminadas alrededor en capas circulares
    for dx in range(-grosor * 2, grosor * 2 + 1):
        for dy in range(-grosor * 2, grosor * 2 + 1):
            if dx != 0 or dy != 0:
                dist = math.hypot(dx, dy)
                if dist <= grosor * 2:
                    # Cuanto más lejos del centro, más transparente
                    alpha = int(180 * (1.0 - dist / (grosor * 2.0)))
                    s_t = fuente.render(texto, True, (r_g, g_g, b_g, alpha))
                    surf_glow.blit(s_t, (dx + grosor * 2, dy + grosor * 2))

    # Dibuja el texto frontal nítido sobre el resplandor
    surf_glow.blit(surf_base, (grosor * 2, grosor * 2))

    # Calcula la posición del rectángulo (centrado o desde la esquina superior izquierda)
    rect_final = surf_glow.get_rect()
    if centro:
        rect_final.center = (x, y)
    else:
        rect_final.topleft = (x, y)

    # Imprime el texto con resplandor en la pantalla
    pantalla.blit(surf_glow, rect_final)
    # Retorna el rectángulo ocupado
    return rect_final

