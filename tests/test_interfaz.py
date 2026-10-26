"""
Pruebas de la interfaz Pygame, sin abrir ninguna ventana.

SDL_VIDEODRIVER=dummy hace que Pygame dibuje en memoria. Los clics se
simulan llamando a manejar_evento() de cada pantalla con un evento de mouse
en el centro del botón, igual que lo haría el bucle principal.
"""

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest

pygame = pytest.importorskip("pygame")

from conftest import RAIZ, casilla_global
from modelos.color import Color

pytestmark = pytest.mark.ui


# ----------------------------- Herramientas ----------------------------------

@pytest.fixture
def app(monkeypatch, tmp_path):
    """La aplicación completa, con el guardado redirigido a una carpeta temporal."""
    monkeypatch.chdir(RAIZ)                     # para que encuentre assets/
    from interfaz.interfaz import InterfazGrafica
    aplicacion = InterfazGrafica()
    yield aplicacion
    pygame.quit()


@pytest.fixture
def en_juego(app, crear_partida):
    """La aplicación con una partida de 4 jugadores humanos en curso."""
    def _preparar(cantidad=4, bots=False):
        app.gestor.partidaActual = crear_partida(cantidad, bots=bots)
        app.estado = "JUEGO"
        dibujar(app)
        return app.gestor.partidaActual
    return _preparar


@pytest.fixture
def dado_siempre(monkeypatch):
    """Todas las tiradas (incluida la animación) sacan el valor indicado."""
    def _fijar(valor):
        monkeypatch.setattr("random.randint", lambda a, b: valor)
    return _fijar


def dibujar(app, cuadros=1):
    for _ in range(cuadros):
        app._actualizar_y_dibujar()


def clic_en(pantalla, punto):
    pantalla.manejar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=punto))


def clic(app, pantalla, nombre_boton):
    """Dibuja el cuadro actual (ahí se crean los botones) y hace clic en uno."""
    dibujar(app)
    boton = getattr(pantalla, nombre_boton)
    clic_en(pantalla, getattr(boton, "rect_base", boton).center)


def tecla(pantalla, key, caracter=""):
    pantalla.manejar_evento(pygame.event.Event(pygame.KEYDOWN, key=key, unicode=caracter))


# ----------------------------- Dibujo ----------------------------------------

ESTADOS = ["MENU", "CONFIGURACION", "CONTINUAR", "JUEGO", "PAUSA", "REGLAS", "ESTADISTICAS", "FINAL"]


@pytest.mark.parametrize("estado", ESTADOS)
def test_cada_pantalla_se_dibuja_sin_errores(en_juego, app, estado):
    en_juego(4)
    app.estado_anterior = "JUEGO"
    app.estado = estado
    dibujar(app, 3)


def test_pantalla_completa_y_vuelta(app):
    app.toggle_pantalla_completa()
    app.toggle_pantalla_completa()
    assert not app.pantalla_completa
    dibujar(app)


# ----------------------------- Menú ------------------------------------------

def test_menu_nueva_partida_abre_la_configuracion(app):
    clic(app, app.menu_principal, "btn_nueva")
    assert app.estado == "CONFIGURACION"


def guardar(partida):
    """Guarda con la misma persistencia (temporal) que usa el GameManager."""
    import logica.game_manager as game_manager
    return game_manager.PersistenciaDeDatos().guardarPartida(partida)


def test_menu_continuar_sin_partida_guardada_avisa(app):
    clic(app, app.menu_principal, "btn_continuar")
    assert app.estado == "MENU" and "No existe" in app.menu_principal.mensaje_error


def test_menu_continuar_abre_la_pantalla_de_continuar(app, crear_partida):
    guardar(crear_partida(2))
    clic(app, app.menu_principal, "btn_continuar")
    assert app.estado == "CONTINUAR"


# ----------------------------- Configuración ---------------------------------

@pytest.fixture
def config(app):
    app.estado = "CONFIGURACION"
    return app.pantalla_config


def test_cantidad_de_jugadores_entre_2_y_4(app, config):
    for _ in range(5):
        clic(app, config, "btn_mas_inst")
    assert config.cant_jugadores == 4
    for _ in range(5):
        clic(app, config, "btn_menos_inst")
    assert config.cant_jugadores == 2


def test_las_flechas_cambian_el_color_del_jugador(app, config):
    # CU-04: la flecha asigna el siguiente color libre (nunca uno ya asignado)
    dibujar(app)
    assert config.colores[:2] == [Color.ROJO, Color.VERDE]
    clic_en(config, config.rects_arrow_right[0].center)
    assert config.colores[0] not in (Color.ROJO, Color.VERDE)
    assert app.gestor.partidaActual.jugadores[0].color == config.colores[0]
    dibujar(app)
    clic_en(config, config.rects_arrow_left[0].center)
    assert config.colores[0] == Color.ROJO


def test_con_4_jugadores_no_queda_otro_color(app, config):
    for _ in range(2):
        clic(app, config, "btn_mas_inst")
    dibujar(app)
    clic_en(config, config.rects_arrow_right[0].center)
    assert config.colores[0] == Color.ROJO and "color" in config.mensaje_error


def test_la_etiqueta_bot_hum_alterna_humano_y_bot(app, config):
    dibujar(app)
    assert config.es_bot_lista[1] is True
    clic_en(config, config.rects_tipo[1].center)
    assert config.es_bot_lista[1] is False and config.nombres[1] == "Jugador 2"
    dibujar(app)
    clic_en(config, config.rects_tipo[1].center)
    assert config.es_bot_lista[1] is True and config.nombres[1] == "Bot 2"


def test_escribir_el_nombre_de_un_jugador(app, config):
    dibujar(app)
    clic_en(config, config.rects_nombres[0].center)
    for _ in range(20):
        tecla(config, pygame.K_BACKSPACE)
    for letra in "Felix":
        tecla(config, pygame.K_a, letra)
    assert config.nombres[0] == "Felix"
    for letra in "ABCDEFGHIJ":
        tecla(config, pygame.K_a, letra)
    assert len(config.nombres[0]) == 12          # máximo 12 caracteres


def test_no_se_puede_iniciar_con_un_nombre_vacio(app, config):
    config.nombres[0] = "   "
    clic(app, config, "btn_iniciar_inst")
    assert app.estado == "CONFIGURACION" and "vacío" in config.mensaje_error


def test_no_se_puede_iniciar_con_nombres_repetidos(app, config):
    config.es_bot_lista[1] = False                # dos humanos con el mismo nombre
    config.nombres[1] = config.nombres[0]
    clic(app, config, "btn_iniciar_inst")
    assert app.estado == "CONFIGURACION" and "repetidos" in config.mensaje_error


def test_iniciar_crea_la_partida_con_lo_configurado(app, config):
    clic(app, config, "btn_mas_inst")                  # 3 jugadores
    clic(app, config, "btn_iniciar_inst")
    partida = app.gestor.partidaActual
    assert app.estado == "JUEGO" and partida.estado == "EN_CURSO"
    assert [j.nombre for j in partida.jugadores] == ["Jugador 1", "Bot 2", "Bot 3"]
    assert len({j.color for j in partida.jugadores}) == 3


def test_la_x_vuelve_al_menu(app, config):
    clic(app, config, "btn_volver_inst")
    assert app.estado == "MENU"


# ----------------------------- Juego -----------------------------------------

def test_clic_en_el_dado_tira_y_permite_mover(app, en_juego, dado_siempre):
    partida = en_juego(2)
    dado_siempre(6)
    clic(app, app.pantalla_juego, "btn_lanzar")
    dibujar(app, 15)                              # dura la animación del dado
    assert partida.dado == 6 and partida.obtenerMovimientosValidos()


def test_clic_en_una_ficha_valida_la_mueve(app, en_juego, dado_siempre):
    partida = en_juego(2)
    dado_siempre(6)
    clic(app, app.pantalla_juego, "btn_lanzar")
    dibujar(app, 15)
    ficha = partida.jugadores[0].fichas[0]
    x, y, _ = app.pantalla_juego.posiciones_fichas_anim[ficha]
    clic_en(app.pantalla_juego, (int(x), int(y)))
    assert ficha.posicion == 1


def test_los_bots_juegan_solos(app, en_juego):
    partida = en_juego(2, bots=True)
    hubo_jugada = False
    for _ in range(300):
        dibujar(app)
        hubo_jugada = hubo_jugada or partida.turnoActual != 0 or partida.dado != 0
    assert hubo_jugada


def test_boton_pausa(app, en_juego):
    en_juego(2)
    clic(app, app.pantalla_juego, "btn_pausa_inst")
    assert app.estado == "PAUSA"


def test_boton_reiniciar_pide_confirmacion_y_va_a_configuracion(app, en_juego):
    en_juego(2)
    clic(app, app.pantalla_juego, "btn_pausa_inst")
    clic(app, app.pantalla_pausa, "btn_reiniciar_inst")
    assert app.estado == "PAUSA"
    assert app.pantalla_pausa.confirmando_accion == "REINICIAR"
    clic(app, app.pantalla_pausa, "btn_conf_si_inst")
    assert app.estado == "CONFIGURACION" and app.gestor.partidaActual.estado == "CONFIGURACION"


# ----------------------------- Pausa -----------------------------------------

@pytest.fixture
def pausa(app, en_juego):
    en_juego(2)
    app.gestor.pausarPartida()
    app.ir_a("PAUSA")
    return app.pantalla_pausa


def test_pausa_continuar(app, pausa):
    clic(app, pausa, "btn_continuar_inst")
    assert app.estado == "JUEGO"


def test_pausa_reglas_y_volver(app, pausa):
    clic(app, pausa, "btn_reglas_inst")
    assert app.estado == "REGLAS"
    clic(app, app.pantalla_reglas, "btn_cerrar_inst")
    assert app.estado == "PAUSA"


def test_pausa_volver_al_menu_se_puede_cancelar(app, pausa):
    clic(app, pausa, "btn_menu_inst")
    assert pausa.confirmando_accion == "SALIR"
    clic(app, pausa, "btn_conf_no_inst")
    assert pausa.confirmando_accion is None and app.estado == "PAUSA"


def test_pausa_volver_al_menu_confirmado_descarta_la_partida(app, pausa):
    clic(app, pausa, "btn_menu_inst")
    clic(app, pausa, "btn_conf_si_inst")
    assert app.estado == "MENU" and app.gestor.partidaActual is None


def test_pausa_guardar_escribe_el_archivo_y_sale_al_menu(app, pausa):
    clic(app, pausa, "btn_guardar_inst")
    assert pausa.confirmando_accion == "GUARDAR"
    clic(app, pausa, "btn_conf_si_inst")
    assert app.estado == "MENU" and app.gestor.partidaActual is None
    assert app.gestor.reanudarPartidaGuardada()[0]


# ----------------------------- Continuar -------------------------------------

def test_continuar_carga_la_partida_guardada(app, crear_partida):
    guardada = crear_partida(3)
    guardar(guardada)
    clic(app, app.menu_principal, "btn_continuar")
    assert app.estado == "CONTINUAR"
    clic(app, app.pantalla_continuar, "btn_iniciar_inst")
    assert app.estado == "JUEGO"
    a, b = app.gestor.partidaActual.guardar(), guardada.guardar()
    a.pop("tiempoTranscurrido"), b.pop("tiempoTranscurrido")
    assert a == b


def test_continuar_x_vuelve_al_menu(app, crear_partida):
    guardar(crear_partida(2))
    clic(app, app.menu_principal, "btn_continuar")
    clic(app, app.pantalla_continuar, "btn_volver_inst")
    assert app.estado == "MENU" and app.gestor.partidaActual is None


# ----------------------------- Reglas y final --------------------------------

def test_reglas_scroll_y_escape(app):
    reglas = app.pantalla_reglas
    reglas.abrir()
    app.ir_a("REGLAS")
    dibujar(app)
    for _ in range(100):
        tecla(reglas, pygame.K_DOWN)
    assert reglas.scroll_y == reglas.max_scroll       # no pasa del final
    for _ in range(100):
        tecla(reglas, pygame.K_UP)
    assert reglas.scroll_y == 0
    tecla(reglas, pygame.K_ESCAPE)
    assert app.estado == "MENU"


def test_final_volver_al_menu(app, en_juego):
    en_juego(2)
    app.estado = "FINAL"
    clic(app, app.pantalla_final, "btn_menu_inst")
    assert app.estado == "MENU" and app.gestor.partidaActual is None


# ============================= Bugs conocidos ================================

def test_los_bots_no_juegan_con_la_partida_en_pausa(app, en_juego):
    partida = en_juego(2, bots=True)
    app.gestor.pausarPartida()
    dibujar(app, 300)
    assert partida.turnoActual == 0 and partida.dado == 0


def _alguna_pantalla_lleva_a(app, crear_partida, estado_origen, pantalla, objetivo):
    """Prueba todos los botones (atributos btn_*) de una pantalla y dice si
    alguno lleva al estado objetivo."""
    def preparar():
        app.gestor.partidaActual = crear_partida(2)
        app.estado = estado_origen
        dibujar(app)

    preparar()
    nombres = [n for n, v in vars(pantalla).items()
               if n.startswith("btn_") and isinstance(getattr(v, "rect_base", v), pygame.Rect)]
    for nombre in nombres:
        preparar()
        boton = getattr(pantalla, nombre)
        clic_en(pantalla, getattr(boton, "rect_base", boton).center)
        if app.estado == objetivo:
            return True
    return False


@pytest.mark.xfail(reason="Como en el Figma, Estadísticas (CU-15) se abre desde el menú de Pausa, "
                          "no directamente desde el juego ni desde la victoria.")
@pytest.mark.parametrize("origen, pantalla", [("JUEGO", "pantalla_juego"), ("FINAL", "pantalla_final")])
def test_se_puede_abrir_estadisticas(app, crear_partida, origen, pantalla):
    assert _alguna_pantalla_lleva_a(app, crear_partida, origen, getattr(app, pantalla), "ESTADISTICAS")


def test_se_puede_abrir_reglas_desde_el_juego(app, crear_partida):
    assert _alguna_pantalla_lleva_a(app, crear_partida, "JUEGO", app.pantalla_juego, "REGLAS")


def test_el_panel_muestra_el_mensaje_de_la_partida(app, en_juego, monkeypatch):
    from interfaz import tema
    en_juego(2)
    textos = []
    original = tema.render_texto
    monkeypatch.setattr(tema, "render_texto", lambda contenido, *a, **k: (textos.append(contenido),
                                                                        original(contenido, *a, **k))[1])
    app.pantalla_juego.mensaje = "Hola"
    dibujar(app)
    assert "Hola" in textos


def test_la_etiqueta_de_cada_jugador_tiene_su_color(app, en_juego, monkeypatch):
    partida = en_juego(4)
    bordes = []
    original = pygame.draw.rect

    def rect_espia(superficie, color, rect, width=0, *args, **kwargs):
        if width > 0:
            bordes.append(tuple(color)[:3])
        return original(superficie, color, rect, width, *args, **kwargs)

    monkeypatch.setattr(pygame.draw, "rect", rect_espia)
    app.pantalla_juego._dibujar_etiquetas_jugadores()
    monkeypatch.setattr(pygame.draw, "rect", original)
    from interfaz import tema
    assert bordes == [tema.COLOR_DADO[j.color] for j in partida.jugadores]


def test_continuar_muestra_los_jugadores_guardados(app, crear_partida, monkeypatch):
    from interfaz import tema
    guardada = crear_partida(2)
    guardada.jugadores[0].nombre = "Zoe"
    guardar(guardada)
    clic(app, app.menu_principal, "btn_continuar")
    textos = []
    original = tema.render_texto
    monkeypatch.setattr(tema, "render_texto", lambda contenido, *a, **k: (textos.append(contenido),
                                                                        original(contenido, *a, **k))[1])
    dibujar(app)
    assert "Zoe" in textos


# ---------------------- Coherencia entre modelo y dibujo ---------------------

def _base_del_color(pj, color):
    """Rectángulo de 6x6 celdas de la base, deducido de dónde se dibujan sus fichas."""
    filas = [r for r, _ in pj.GRID_BASE[color]]
    cols = [c for _, c in pj.GRID_BASE[color]]
    return math.floor(min(filas)) - 1, math.floor(min(cols)) - 1


def _toca_la_base(celda, base):
    fila, col = celda
    f0, c0 = base
    dentro_f = f0 <= fila <= f0 + 5
    dentro_c = c0 <= col <= c0 + 5
    return (dentro_c and fila in (f0 - 1, f0 + 6)) or (dentro_f and col in (c0 - 1, c0 + 6))


@pytest.mark.parametrize("color", list(Color))
def test_el_recorrido_del_modelo_coincide_con_el_tablero_dibujado(app, color):
    pj = app.pantalla_juego
    # 1) La casilla de salida (posición 1) está pegada a la base de ese color.
    salida = pj.GRID_CIRCUITO_52[casilla_global(color, 1)]
    assert _toca_la_base(salida, _base_del_color(pj, color))
    # 2) La última casilla del circuito (51) está pegada al pasillo de ese color (52).
    ultima = pj.GRID_CIRCUITO_52[casilla_global(color, 51)]
    pasillo = {Color.ROJO: pj.GRID_META_ROJO, Color.AZUL: pj.GRID_META_AZUL,
               Color.VERDE: pj.GRID_META_VERDE, Color.AMARILLO: pj.GRID_META_AMARILLO}[color][0]
    assert abs(ultima[0] - pasillo[0]) + abs(ultima[1] - pasillo[1]) == 1
