#!/usr/bin/env python3
"""I/O con el Google Sheet a traves del Web App (Apps Script), enrutando por
NOMBRE de pestaña (parametro 'hoja') -> no hacen falta GIDs.

  subir(hoja, **campos)  -> agrega una fila a esa pestaña
  leer(hoja)             -> lista de dicts (una por fila, por encabezado)
  ultima(hoja)           -> la ultima fila (dict) o None

El ESP32 sigue subiendo a 'inbox' (default del Apps Script) sin cambios.
"""
import csv
import io
import time
import urllib.error
import urllib.parse
import urllib.request

# URL del Web App (/exec): vive en config_local.py (no versionado; ver
# config_local.py.example). Actualizar alli tras redeployar el Apps Script.
from config_local import SCRIPT_URL  # noqa: E402

REINTENTOS = 10  # el Apps Script da 500 transitorios (cold start, crear pestaña)
                 # y 404 INTERMITENTES en el redirect a googleusercontent (flakeo
                 # de Google bajo requests rapidos). Con mas reintentos + backoff
                 # un pico de fallos no aborta la campana entera.


def _get(params):
    """GET al Web App con reintentos. El Apps Script lanza 500 transitorios
    (arranque en frio, insertSheet la 1.ra vez) y 404 intermitentes en el
    redirect -> reintenta con backoff (cap 15 s)."""
    url = f"{SCRIPT_URL}?{urllib.parse.urlencode(params)}"
    for intento in range(1, REINTENTOS + 1):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return r.read().decode("utf-8")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            if intento == REINTENTOS:
                raise
            print(f"    [sheet] {e} (intento {intento}/{REINTENTOS}); reintento...")
            time.sleep(min(2 * intento, 15))


def subir(hoja, **campos):
    """Agrega una fila a la pestaña 'hoja' con los campos dados."""
    return _get(dict(hoja=hoja, **campos))


def leer(hoja):
    """Devuelve las filas de la pestaña como lista de dicts (por encabezado)."""
    text = _get(dict(hoja=hoja, accion="leer"))
    rows = [r for r in csv.reader(io.StringIO(text)) if r]
    if len(rows) < 2:
        return []
    hdr = rows[0]
    return [dict(zip(hdr, r)) for r in rows[1:]]


def ultima(hoja):
    filas = leer(hoja)
    return filas[-1] if filas else None


def n_filas(hoja):
    return len(leer(hoja))


def fnum(x):
    """Numero del Sheet (locale es-ES: decimales con coma)."""
    return float(str(x).replace(",", "."))


class Inbox:
    """Espera las filas que sube el ESP32 a 'inbox' (una por ventana medida).
    Detecta fila nueva por CONTENIDO de la ultima fila (no por conteo): el
    Apps Script poda el inbox (borra viejas al escribir), asi que la CUENTA no
    crece con cada ventana -> una deteccion por len() se cuelga. La 'fecha'
    hace unica cada fila, asi que comparar la ultima fila completa es robusto a
    la poda. get_pavg() bloquea hasta que la ultima fila cambie."""

    def __init__(self, hoja="inbox"):
        self.hoja = hoja
        self.marca = ultima(hoja)   # ultima fila conocida (o None), NO un conteo
        self.ultima_dur_s = None    # duracion de pared de la ULTIMA ventana devuelta
                                    # por get_pavg (para el wall real de las variantes
                                    # duty, que no asume el duty de diseno)

    def get_pavg(self, timeout=30, esperado_s=None):
        """Espera la fila nueva del ESP32 y devuelve su p_avg. Si se conoce la
        duracion esperada de la ventana (esperado_s), se verifica contra la
        duration_ms de la fila: una fila con duracion incompatible es una
        ventana VIEJA que llego tarde (p.ej. de un reintento) y se DESCARTA en
        vez de aparearse con la corrida equivocada --- sin esta guarda, una
        fila sobrante desalinea todas las corridas siguientes de la tanda."""
        t0 = time.time()
        avisado = False
        while time.time() - t0 < timeout:
            filas = leer(self.hoja)
            nueva = filas[-1] if filas else None
            if nueva is not None and nueva != self.marca:
                # p_avg puede venir VACIO por un instante: la lectura cayo sobre
                # una fila recien anexada por el ESP32 mientras la poda del Apps
                # Script reacomodaba filas. NO fijamos la marca -> se reintenta
                # hasta que la fila este completa (evita el crash de fnum('') y
                # evita perder la ventana, que tiene la misma 'fecha').
                try:
                    pval = fnum(nueva.get("p_avg", ""))
                except (ValueError, TypeError):
                    pval = None
                if pval is not None:
                    self.marca = nueva
                    dur = nueva.get("duration_ms", "")
                    try:
                        self.ultima_dur_s = fnum(dur) / 1e3 if dur else None
                    except (ValueError, TypeError):
                        self.ultima_dur_s = None
                    if esperado_s is not None and nueva.get("duration_ms"):
                        dur = fnum(nueva["duration_ms"]) / 1e3
                        if abs(dur - esperado_s) > max(2.0, 0.15 * esperado_s):
                            print(f"    [GUARDA] fila del ESP32 con duracion "
                                  f"{dur:.1f} s (esperaba {esperado_s:.1f} s): "
                                  f"ventana vieja desalineada, la descarto y sigo "
                                  f"esperando la correcta")
                            continue
                    return pval
            if not avisado:   # un solo aviso, no uno cada 3 s
                print(f"    esperando la ventana del ESP32 (max {timeout} s)...")
                avisado = True
            time.sleep(3)
        raise TimeoutError(f"timeout esperando fila nueva en '{self.hoja}'")

    def reset(self):
        """Fija la marca a la ultima fila ACTUAL: se llama JUSTO ANTES de correr
        el kernel, para que get_pavg solo acepte una fila DISTINTA subida DESPUES
        (drena las pendientes/atrasadas). Sin esto, una ventana vieja que llega
        tarde se aparea con la corrida equivocada (p.ej. fpdiv tomando la ventana
        de fpfma cuando sus duraciones son parecidas y el guard no las distingue)."""
        self.marca = ultima(self.hoja)
