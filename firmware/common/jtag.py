#!/usr/bin/env python3
"""Carga un .elf por JTAG/GDB, lo corre hasta ebreak y devuelve los 30 words de
'results' (28 CSR del clasificador + mcycle ini/fin). Comun a los 3 metodos y al
verificador. Requiere OpenOCD (gdb server riscv.cpu en :3333).
"""
import os
import re
import subprocess
import time

GDB_BIN = os.environ.get("GDB_BIN", "gdb-multiarch")
RETRIES = int(os.environ.get("RETRIES", "5"))
GDB_TIMEOUT = int(os.environ.get("GDB_TIMEOUT", "480"))   # load + corrida larga
# Tras volcar 'results', con el core halteado en ebreak, lee la temperatura del
# die por el XADC: habilita los pines GPIO io_19..30 (GPIO_EN + modo input) y lee
# GPIO_IN -> codigo de 12 bits del XADC (ver pulp_temp.h). 'TEMPCODE' lo parsea el
# Python. Inofensivo si el bitstream no tiene XADC (devuelve 0).
GDB_SCRIPT = """\
set pagination off
set confirm off
target remote :3333
monitor reset halt
load
continue
x/32xw &results
set {unsigned int}0x1A10100C = 0
set {unsigned int}0x1A101080 = {unsigned int}0x1A101080 | 0x7ff80000
printf "TEMPCODE %u\\n", ({unsigned int}0x1A101100 >> 19) & 0xfff
"""

_LINE = re.compile(r"^0x[0-9a-fA-F]+:(\s+0x[0-9a-fA-F]+)+\s*$")
_WORD = re.compile(r"0x[0-9a-fA-F]+")
_PROMPT = re.compile(r"^(\(gdb\)\s*)+")
_TEMP = re.compile(r"TEMPCODE\s+(\d+)")
_BAD = ("Could not read registers", "not supported by this target", "is `exec'")
MASK32 = 0xFFFFFFFF

# temperatura del die (centi-grados) de la ULTIMA corrida de run_one; None si no
# se pudo leer. Conversion Xilinx: T = code*503.975/4096 - 273.15.
ultima_temp_cC = None


def _temp_cC_de(code):
    return (code * 50397) // 4096 - 27315   # centi-grados (C x 100)


def mcycle_de(words):
    """T en ciclos = (mcycle_fin - mcycle_ini) & 32b, de los 30 words de results."""
    w = [int(x, 16) for x in words]
    return (w[29] - w[28]) & MASK32


def ninstr_de(words):
    """Instrucciones retiradas: suma de las categorías de instrucciones.
    DIVCYC se excluye porque mide ciclos del divisor, no instrucciones."""
    w = [int(x, 16) for x in words]
    return sum(w[i] + (w[i + 1] << 32)
               for i in (0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24))


# Lectura de temperatura SIN correr ningun elf: haltea el core (el modulo de
# depuracion queda como maestro del bus), habilita las entradas GPIO del XADC y
# lee el codigo. No carga ni resetea nada; la proxima corrida hace reset igual.
GDB_TEMP_SCRIPT = """\
set pagination off
set confirm off
target remote :3333
monitor halt
set {unsigned int}0x1A10100C = 0
set {unsigned int}0x1A101080 = {unsigned int}0x1A101080 | 0x7ff80000
printf "TEMPCODE %u\\n", ({unsigned int}0x1A101100 >> 19) & 0xfff
detach
"""


def leer_temp():
    """Temperatura del die [C] leida por JTAG via XADC, sin ejecutar programa.
    None si no se pudo leer (sin OpenOCD, bitstream sin XADC -> codigo 0)."""
    for _ in range(2):
        try:
            out = subprocess.run([GDB_BIN, "-n", "-q"], input=GDB_TEMP_SCRIPT,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, timeout=60).stdout
        except subprocess.TimeoutExpired:
            continue
        mt = _TEMP.search(out)
        if mt and int(mt.group(1)) != 0:
            return _temp_cC_de(int(mt.group(1))) / 100.0
        time.sleep(1)
    return None


def run_one(elf):
    """Devuelve los 30 words (strings hex) de 'results' tras correr el elf."""
    out = ""
    for intento in range(1, RETRIES + 1):
        try:
            out = subprocess.run([GDB_BIN, elf], input=GDB_SCRIPT,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, timeout=GDB_TIMEOUT).stdout
        except subprocess.TimeoutExpired as e:
            out = e.stdout or ""
            print(f"    (intento {intento}/{RETRIES}: timeout GDB "
                  f"tras {GDB_TIMEOUT} s, reintento...)")
            time.sleep(2)
            continue
        if any(m in out for m in _BAD):
            print(f"    (intento {intento}/{RETRIES}: JTAG inestable, reintento...)")
            time.sleep(2)
            continue
        words = []
        for line in out.splitlines():
            line = _PROMPT.sub("", line.strip())
            if _LINE.match(line):
                _, rest = line.split(":", 1)
                words.extend(_WORD.findall(rest))
        if len(words) == 32:
            vals = [int(x, 16) for x in words]
            if vals[0] == 0xBAD00BAD:
                raise RuntimeError(
                    f"{elf}: trap en workload "
                    f"(mcause=0x{vals[1]:08x}, mepc=0x{vals[2]:08x})")
            global ultima_temp_cC
            mt = _TEMP.search(out)
            ultima_temp_cC = _temp_cC_de(int(mt.group(1))) if mt else None
            return words
        print(f"    (intento {intento}/{RETRIES}: {len(words)}/32 words, reintento...)")
        time.sleep(2)
    raise RuntimeError(f"{elf}: fallo tras {RETRIES} intentos.\n--- ultima salida GDB ---\n{out}")


IPC_MAX = 1.02     # IPC fisico maximo (single-issue); > esto = mcycle corrupto (wrap)


def run_medido(elf, get_pavg, reintentos=3, reset=None):
    """Corre `elf` UNA vez y devuelve (words, P_med) de esa ventana.

    Antes esto corria 'hasta 5x y se quedaba con la limpia' porque el FT232H
    inestable inflaba mcycle de forma no determinista. Con el banco actual la
    ejecucion es reproducible (mcycle identico entre corridas y entre dias en
    ~140 corridas auditadas), asi que la doble corrida de confirmacion sobra.
    Guardas que quedan, gratis: se reintenta la medida completa si mcycle sale
    CORRUPTO (wrap -> IPC > 1.02) o si la fila del ESP32 no llega en el
    timeout corto de get_pavg (subida perdida)."""
    for intento in range(1, reintentos + 1):
        if reset is not None:
            reset()        # drena ventanas pendientes: solo cuenta la de ESTA corrida
        words = run_one(elf)
        mc = mcycle_de(words)
        ni = ninstr_de(words)
        ipc = ni / mc if mc else 1e9
        # duracion de PARED esperada de la ventana: mcycle es tiempo ACTIVO;
        # en las variantes de intensidad la pared es activo/duty
        esperado = mc / 1e7
        if elf.endswith("_d60.elf"):
            esperado /= 0.60
        elif elf.endswith("_d30.elf"):
            esperado /= 0.30
        try:
            pmed = get_pavg(esperado_s=esperado)
        except TimeoutError:
            print(f"    intento {intento}/{reintentos}: ventana sin P_avg del "
                  f"ESP32; REINTENTO la medida (nueva ventana)")
            continue
        if ipc > IPC_MAX:
            print(f"    intento {intento}/{reintentos}: mcycle={mc:,} "
                  f"IPC={ipc:.2f} CORRUPTO (wrap); reintento")
            continue
        print(f"    ok: {mc/1e7:5.1f} s activos ({mc:,} ciclos)  IPC={ipc:.3f}")
        return words, pmed
    raise RuntimeError(f"{elf}: sin medida valida en {reintentos} intentos "
                       f"(mcycle corrupto o ESP32 sin publicar P_avg)")
