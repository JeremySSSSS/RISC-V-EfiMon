#!/usr/bin/env python3
"""I/O with the Google Sheet through the Web App (Apps Script), routing by
tab NAME (parameter 'hoja') -> no GIDs needed.

  subir(hoja, **campos)  -> appends a row to that tab
  leer(hoja)             -> list of dicts (one per row, keyed by header)
  ultima(hoja)           -> the last row (dict) or None

The ESP32 keeps posting to 'inbox' (Apps Script default) unchanged.
"""
import csv
import io
import time
import urllib.error
import urllib.parse
import urllib.request

# Web App URL (/exec): lives in config_local.py (not versioned; see
# config_local.py.example). Update it there after redeploying the Apps Script.
from config_local import SCRIPT_URL  # noqa: E402

REINTENTOS = 4   # the Apps Script returns transient 500s (cold start, tab creation)


def _get(params):
    """GET to the Web App with retries. The Apps Script raises transient 500s
    (cold start, first insertSheet) -> retry with backoff."""
    url = f"{SCRIPT_URL}?{urllib.parse.urlencode(params)}"
    for intento in range(1, REINTENTOS + 1):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return r.read().decode("utf-8")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            if intento == REINTENTOS:
                raise
            print(f"    [sheet] {e} (attempt {intento}/{REINTENTOS}); retrying...")
            time.sleep(2 * intento)


def subir(hoja, **campos):
    """Appends a row to tab 'hoja' with the given fields."""
    return _get(dict(hoja=hoja, **campos))


def leer(hoja):
    """Returns the tab rows as a list of dicts (keyed by header)."""
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
    """Number from the Sheet (es-ES locale: comma decimals)."""
    return float(str(x).replace(",", "."))


class Inbox:
    """Waits for the rows the ESP32 posts to 'inbox' (one per measured window).
    Detects a new row by count; get_pavg() blocks until it appears."""

    def __init__(self, hoja="inbox"):
        self.hoja = hoja
        self.seen = n_filas(hoja)

    def get_pavg(self, timeout=30, esperado_s=None):
        """Waits for the ESP32's new row and returns its p_avg. If the expected
        window duration (esperado_s) is known, it is checked against the row's
        duration_ms: a row with an incompatible duration is an OLD window that
        arrived late (e.g. from a retry) and is DISCARDED instead of being
        paired with the wrong run --- without this guard, a stray row would
        misalign every following run of the batch."""
        t0 = time.time()
        avisado = False
        while time.time() - t0 < timeout:
            filas = leer(self.hoja)
            if len(filas) > self.seen:
                self.seen = len(filas)
                fila = filas[-1]
                if esperado_s is not None and fila.get("duration_ms"):
                    dur = fnum(fila["duration_ms"]) / 1e3
                    if abs(dur - esperado_s) > max(2.0, 0.15 * esperado_s):
                        print(f"    [GUARD] ESP32 row with duration "
                              f"{dur:.1f} s (expected {esperado_s:.1f} s): "
                              f"misaligned old window, discarding it and "
                              f"waiting for the correct one")
                        continue
                return fnum(fila["p_avg"])
            if not avisado:   # a single notice, not one every 3 s
                print(f"    waiting for the ESP32 window (max {timeout} s)...")
                avisado = True
            time.sleep(3)
        raise TimeoutError(f"timeout waiting for a new row in '{self.hoja}'")
