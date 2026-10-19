"""
Modulo sonidos.py
Gestor de sonido desactivado completamente a pedido del usuario.
"""


class GestorSonidos:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(GestorSonidos, cls).__new__(cls)
            cls._instancia._inicializado = False
        return cls._instancia

    def __init__(self):
        if self._inicializado:
            return
        self._inicializado = True
        self.mutado = True
        self.sonidos = {}

    def reproducir(self, nombre):
        # Sonido completamente eliminado del programa
        pass

    def alternar_mute(self):
        self.mutado = True
        return True
