"""
Modulo estadisticas.py
Administra y calcula las estadísticas de la partida (CU-15).
"""

import time


class Estadisticas:

    def __init__(self):
        # Registra el tiempo de inicio de la partida y contadores de eventos
        self.tiempo_inicio = time.time()
        self.movimientos_por_jugador = {}
        self.turnos_totales = 0
        self.capturas_totales = 0

    def registrar_movimiento(self, nombre_jugador: str):
        # Incrementa el conteo de movimientos para el jugador indicado.
        self.movimientos_por_jugador[nombre_jugador] = self.movimientos_por_jugador.get(nombre_jugador, 0) + 1

    def registrar_turno(self):
        # Incrementa el número total de turnos transcurridos.
        self.turnos_totales += 1

    def registrar_captura(self):
        # Incrementa el conteo global de capturas.
        self.capturas_totales += 1

    def obtener_tiempo_formateado(self) -> str:
        # Devuelve el tiempo transcurrido en minutos y segundos (ej. 05:42).
        segundos = int(time.time() - self.tiempo_inicio)
        minutos = segundos // 60
        seg_restantes = segundos % 60
        return f"{minutos:02d}:{seg_restantes:02d}"

    def calcular_puntaje(self, jugador) -> int:
        # Calcula un puntaje representativo basado en el avance de las fichas del jugador.
        # Ficha en base: 0 pts, Ficha en meta: 100 pts, Ficha en camino: valor de su posición.
        puntaje = 0
        for f in jugador.fichas:
            if f.enMeta:
                puntaje += 100
            elif not f.enBase:
                puntaje += f.posicion
        return puntaje

    def obtener_resumen(self, partida) -> dict:
        # Genera un diccionario con el resumen completo de estadísticas de la partida.
        resumen_jugadores = []
        for j in partida.jugadores:
            resumen_jugadores.append({
                "nombre": j.nombre,
                "color": j.color.name,
                "movimientos": self.movimientos_por_jugador.get(j.nombre, 0),
                "puntaje": self.calcular_puntaje(j)
            })

        return {
            "tiempo": self.obtener_tiempo_formateado(),
            "turnos_totales": self.turnos_totales,
            "jugadores": resumen_jugadores,
            "ganador": partida.ganador.nombre if partida.ganador else "Ninguno"
        }
