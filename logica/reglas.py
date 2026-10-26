"""
Modulo reglas.py
Contiene la definición estática y detallada de las reglas del Ludo (CU-06).
"""


# Clase que agrupa los textos informativos con las reglas del juego
class Reglas:

    # Método estático: se puede llamar sin necesidad de instanciar la clase Reglas()
    @staticmethod
    def obtener_texto_reglas() -> list:
        # Devuelve una lista de cadenas de texto con los puntos principales de las reglas
        return [
            # Punto 1: Explica la meta del juego
            "1. Objetivo del Juego:",
            "   • Ser el primer jugador en llevar sus 4 fichas desde la base hasta la meta final.",
            "",
            # Punto 2: Explica cómo sacar fichas de la base
            "2. Inicio y Salida de la Base:",
            "   • Cada jugador posee 4 fichas de un mismo color en su base inicial.",
            "   • Para sacar una ficha de la base a la casilla de salida se necesita sacar un 6 en el dado.",
            "",
            # Punto 3: Explica las tiradas del dado y la regla de los tres 6
            "3. Lanzamiento del Dado y Turnos:",
            "   • El dado se lanza en cada turno para determinar cuántas casillas avanza una ficha.",
            "   • Sacar un 6 otorga un turno extra inmediatamente después de mover.",
            "   • ¡Atención! Si se obtienen TRES 6 CONSECUTIVOS, el tercer 6 se anula y el turno pasa de inmediato al siguiente jugador.",
            "",
            # Punto 4: Explica cómo se comen las fichas rivales y las casillas con estrella
            "4. Capturas y Casillas Seguras:",
            "   • Si una ficha termina su movimiento en una casilla ocupada por una ficha rival, la ficha rival es capturada y regresa a su base.",
            "   • Las casillas marcadas con una estrella (salidas y zonas seguras) impiden las capturas.",
            "",
            # Punto 5: Explica las barreras formadas por dos fichas iguales
            "5. Barreras / Bloqueos:",
            "   • Dos fichas del mismo color en una misma casilla forman una barrera.",
            "   • Ninguna ficha (propia o rival) puede atravesar o aterrizar sobre una barrera.",
            "",
            # Punto 6: Explica la necesidad de número exacto para ganar
            "6. Llegada a la Meta:",
            "   • Para ingresar a la meta final se requiere el número exacto de casillas en el dado.",
            "   • Si el valor del dado supera el camino restante, la ficha no puede realizar el movimiento."
        ]

