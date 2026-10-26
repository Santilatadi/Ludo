"""
main.py
Punto de entrada principal para ejecutar la aplicación del juego Ludo.
"""

import os
import sys

# Si falta pygame pero existe un entorno virtual local (.venv), relanzar con él:
try:
    import pygame
except ModuleNotFoundError:
    venv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv")
    venv_python = os.path.join(venv_dir, "bin", "python")
    if os.path.exists(venv_python) and os.path.abspath(sys.prefix) != os.path.abspath(venv_dir):
        os.execv(venv_python, [venv_python] + sys.argv)
    raise

from interfaz.interfaz import InterfazGrafica

if __name__ == "__main__":
    app = InterfazGrafica()
    app.ejecutar()
