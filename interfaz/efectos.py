"""
Modulo efectos.py
Sistema de partículas, animaciones visuales avanzadas y utilidades de renderizado.
Proporciona fondos dinámicos, glassmorphism, resplandores neon y física de confeti.
"""

import math
import random
import pygame


class Particula:
    def __init__(self, x, y, vx, vy, color, tam, vida, gravedad=0.0, tipo="circulo"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.tam_inicial = tam
        self.tam = tam
        self.vida_max = vida
        self.vida = vida
        self.gravedad = gravedad
        self.tipo = tipo
        self.rotacion = random.uniform(0, 360)
        self.v_rot = random.uniform(-6, 6)

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravedad
        self.vida -= 1
        self.rotacion += self.v_rot
        progreso = max(0.0, self.vida / float(self.vida_max))
        self.tam = self.tam_inicial * progreso

    def dibujar(self, pantalla):
        if self.vida <= 0 or self.tam <= 0.5:
            return

        alpha = int(255 * (self.vida / float(self.vida_max)))
        r, g, b = self.color[:3]
        col_alpha = (r, g, b, alpha)

        if self.tipo == "confeti":
            surf = pygame.Surface((int(self.tam * 2), int(self.tam * 1.2)), pygame.SRCALPHA)
            surf.fill(col_alpha)
            surf_rot = pygame.transform.rotate(surf, self.rotacion)
            pantalla.blit(surf_rot, surf_rot.get_rect(center=(int(self.x), int(self.y))))

        elif self.tipo == "estrella":
            puntos = []
            cx, cy = self.x, self.y
            rad = self.tam
            for i in range(10):
                r_i = rad if i % 2 == 0 else rad * 0.4
                ang = i * math.pi / 5 + math.radians(self.rotacion)
                puntos.append((cx + r_i * math.cos(ang), cy + r_i * math.sin(ang)))
            if len(puntos) > 2:
                pygame.draw.polygon(pantalla, col_alpha, puntos)

        else:  # "circulo" / "orb"
            surf = pygame.Surface((int(self.tam * 2), int(self.tam * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, col_alpha, (int(self.tam), int(self.tam)), int(self.tam))
            pantalla.blit(surf, (int(self.x - self.tam), int(self.y - self.tam)))


class SistemaParticulas:
    def __init__(self):
        self.particulas = []
        self.orbes_fondo = []
        self._generar_orbes_fondo()

    def _generar_orbes_fondo(self):
        colores_orbes = [
            (255, 100, 150), (100, 180, 255), (120, 240, 150),
            (255, 220, 100), (200, 120, 255)
        ]
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

    def emitir_confeti(self, cx, cy, cantidad=60):
        colores = [(255, 60, 60), (60, 220, 100), (60, 140, 255), (255, 220, 40), (230, 80, 255), (255, 150, 40)]
        for _ in range(cantidad):
            ang = random.uniform(0, math.pi * 2)
            vel = random.uniform(3.0, 10.0)
            vx = math.cos(ang) * vel
            vy = math.sin(ang) * vel - random.uniform(2.0, 6.0)
            tam = random.uniform(4, 9)
            vida = random.randint(40, 90)
            col = random.choice(colores)
            self.particulas.append(Particula(cx, cy, vx, vy, col, tam, vida, gravedad=0.25, tipo="confeti"))

    def emitir_estrellas(self, cx, cy, cantidad=15, color=(255, 235, 50)):
        for _ in range(cantidad):
            ang = random.uniform(0, math.pi * 2)
            vel = random.uniform(1.5, 4.5)
            vx = math.cos(ang) * vel
            vy = math.sin(ang) * vel
            tam = random.uniform(5, 10)
            vida = random.randint(20, 45)
            self.particulas.append(Particula(cx, cy, vx, vy, color, tam, vida, gravedad=0.05, tipo="estrella"))

    def emitir_estela_ficha(self, cx, cy, color):
        for _ in range(2):
            vx = random.uniform(-0.8, 0.8)
            vy = random.uniform(-0.8, 0.8)
            tam = random.uniform(3, 6)
            vida = random.randint(12, 24)
            self.particulas.append(Particula(cx, cy, vx, vy, color, tam, vida, gravedad=-0.02, tipo="circulo"))

    def actualizar_y_dibujar(self, pantalla):
        ancho, alto = pantalla.get_size()

        # Actualizar orbes de fondo
        for orb in self.orbes_fondo:
            orb["x"] += orb["vx"]
            orb["y"] += orb["vy"]
            orb["fase"] += 0.03

            if orb["y"] < -20:
                orb["y"] = alto + 20
                orb["x"] = random.uniform(0, ancho)
            if orb["x"] < -20:
                orb["x"] = ancho + 20
            elif orb["x"] > ancho + 20:
                orb["x"] = -20

            # Dibujar orbe tenue
            alpha = int(120 + 80 * math.sin(orb["fase"]))
            r, g, b = orb["color"]
            tam = orb["tam"] + 1.5 * math.sin(orb["fase"] * 0.5)

            surf = pygame.Surface((int(tam * 4), int(tam * 4)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (r, g, b, alpha // 3), (int(tam * 2), int(tam * 2)), int(tam * 2))
            pygame.draw.circle(surf, (r, g, b, alpha), (int(tam * 2), int(tam * 2)), int(tam))
            pantalla.blit(surf, (int(orb["x"] - tam * 2), int(orb["y"] - tam * 2)))

        # Actualizar partículas activas
        vivas = []
        for p in self.particulas:
            p.actualizar()
            if p.vida > 0 and p.tam > 0.5:
                p.dibujar(pantalla)
                vivas.append(p)
        self.particulas = vivas


def dibujar_panel_glassmorphism(pantalla, rect, color_bg=(20, 30, 60, 180), color_borde=(255, 255, 255, 100), radio=16, grosor_borde=2):
    """Dibuja un contenedor con efecto de vidrio esmerilado (Glassmorphism) y sombra tenue."""
    surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

    # Sombra de gota exterior
    sombra = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
    pygame.draw.rect(sombra, (0, 0, 0, 80), (6, 6, rect.width, rect.height), border_radius=radio)
    pantalla.blit(sombra, (rect.x - 3, rect.y + 3))

    # Cuerpo principal traslúcido
    pygame.draw.rect(surf, color_bg, (0, 0, rect.width, rect.height), border_radius=radio)
    # Resplandor/Borde superior brillante
    pygame.draw.rect(surf, color_borde, (0, 0, rect.width, rect.height), width=grosor_borde, border_radius=radio)

    pantalla.blit(surf, (rect.x, rect.y))


def dibujar_texto_glow(pantalla, texto, fuente, x, y, color_texto=(255, 255, 255), color_resplandor=(0, 200, 255), grosor=3, centro=False):
    """Renderiza texto con resplandor luminoso suave a su alrededor."""
    surf_base = fuente.render(texto, True, color_texto)
    w, h = surf_base.get_size()

    surf_glow = pygame.Surface((w + grosor * 4, h + grosor * 4), pygame.SRCALPHA)
    r_g, g_g, b_g = color_resplandor[:3]

    for dx in range(-grosor * 2, grosor * 2 + 1):
        for dy in range(-grosor * 2, grosor * 2 + 1):
            if dx != 0 or dy != 0:
                dist = math.hypot(dx, dy)
                if dist <= grosor * 2:
                    alpha = int(180 * (1.0 - dist / (grosor * 2.0)))
                    s_t = fuente.render(texto, True, (r_g, g_g, b_g, alpha))
                    surf_glow.blit(s_t, (dx + grosor * 2, dy + grosor * 2))

    surf_glow.blit(surf_base, (grosor * 2, grosor * 2))

    rect_final = surf_glow.get_rect()
    if centro:
        rect_final.center = (x, y)
    else:
        rect_final.topleft = (x, y)

    pantalla.blit(surf_glow, rect_final)
    return rect_final
