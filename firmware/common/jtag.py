#!/usr/bin/env python3
"""Loads a .elf over JTAG/GDB, runs it to ebreak and returns the 30 words of
'results' (28 classifier CSRs + mcycle start/end). Shared by the 3 methods and
the verifier. Requires OpenOCD (gdb server riscv.cpu on :3333).
"""
import os
import re
import subprocess
import time

GDB_BIN = os.environ.get("GDB_BIN", "gdb-multiarch")
RETRIES = int(os.environ.get("RETRIES", "5"))
GDB_TIMEOUT = int(os.environ.get("GDB_TIMEOUT", "480"))   # load + long run
# After dumping 'results', with the core halted at ebreak, read the die
# temperature from the XADC: enable GPIO pins io_19..30 (GPIO_EN + input mode) and
# read GPIO_IN -> 12-bit XADC code (see pulp_temp.h). 'TEMPCODE' is parsed by
# Python. Harmless if the bitstream has no XADC (returns 0).
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

# die temperature (centi-degrees) of the LAST run_one run; None if it could not
# be read. Xilinx conversion: T = code*503.975/4096 - 273.15.
ultima_temp_cC = None


def _temp_cC_de(code):
    return (code * 50397) // 4096 - 27315   # centi-degrees (C x 100)


def mcycle_de(words):
    """T in cycles = (mcycle_end - mcycle_start) & 32b, from the 30 result words."""
    w = [int(x, 16) for x in words]
    return (w[29] - w[28]) & MASK32


def ninstr_de(words):
    """Retired instructions: sum of the instruction categories.
    DIVCYC is excluded because it measures divider cycles, not instructions."""
    w = [int(x, 16) for x in words]
    return sum(w[i] + (w[i + 1] << 32)
               for i in (0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24))


# Temperature read WITHOUT running any elf: halt the core (the debug module stays
# as bus master), enable the XADC GPIO inputs and read the code. Loads or resets
# nothing; the next run resets anyway.
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
    """Die temperature [C] read over JTAG via XADC, without running a program.
    None if it could not be read (no OpenOCD, bitstream without XADC -> code 0)."""
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
    """Returns the 30 words (hex strings) of 'results' after running the elf."""
    out = ""
    for intento in range(1, RETRIES + 1):
        try:
            out = subprocess.run([GDB_BIN, elf], input=GDB_SCRIPT,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, timeout=GDB_TIMEOUT).stdout
        except subprocess.TimeoutExpired as e:
            out = e.stdout or ""
            print(f"    (attempt {intento}/{RETRIES}: GDB timeout "
                  f"after {GDB_TIMEOUT} s, retrying...)")
            time.sleep(2)
            continue
        if any(m in out for m in _BAD):
            print(f"    (attempt {intento}/{RETRIES}: unstable JTAG, retrying...)")
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
                    f"{elf}: trap in workload "
                    f"(mcause=0x{vals[1]:08x}, mepc=0x{vals[2]:08x})")
            global ultima_temp_cC
            mt = _TEMP.search(out)
            ultima_temp_cC = _temp_cC_de(int(mt.group(1))) if mt else None
            return words
        print(f"    (attempt {intento}/{RETRIES}: {len(words)}/32 words, retrying...)")
        time.sleep(2)
    raise RuntimeError(f"{elf}: failed after {RETRIES} attempts.\n--- last GDB output ---\n{out}")


IPC_MAX = 1.02     # max physical IPC (single-issue); > this = corrupt mcycle (wrap)


def run_medido(elf, get_pavg, reintentos=3):
    """Runs `elf` ONCE and returns (words, P_med) of that window.

    This used to run 'up to 5x and keep the clean one' because an unstable
    FT232H inflated mcycle non-deterministically. With the current bench the
    execution is reproducible (identical mcycle across runs and across days over
    ~140 audited runs), so the double confirmation run is unnecessary. The
    remaining guards are free: the whole measurement is retried if mcycle comes
    out CORRUPT (wrap -> IPC > 1.02) or if the ESP32 row does not arrive within
    get_pavg's short timeout (lost upload)."""
    for intento in range(1, reintentos + 1):
        words = run_one(elf)
        mc = mcycle_de(words)
        ni = ninstr_de(words)
        ipc = ni / mc if mc else 1e9
        # expected WALL-clock window duration: mcycle is ACTIVE time;
        # in the intensity variants the wall time is active/duty
        esperado = mc / 1e7
        if elf.endswith("_d60.elf"):
            esperado /= 0.60
        elif elf.endswith("_d30.elf"):
            esperado /= 0.30
        try:
            pmed = get_pavg(esperado_s=esperado)
        except TimeoutError:
            print(f"    attempt {intento}/{reintentos}: window without ESP32 "
                  f"P_avg; RETRYING the measurement (new window)")
            continue
        if ipc > IPC_MAX:
            print(f"    attempt {intento}/{reintentos}: mcycle={mc:,} "
                  f"IPC={ipc:.2f} CORRUPT (wrap); retrying")
            continue
        print(f"    ok: {mc/1e7:5.1f} s active ({mc:,} cycles)  IPC={ipc:.3f}")
        return words, pmed
    raise RuntimeError(f"{elf}: no valid measurement in {reintentos} attempts "
                       f"(corrupt mcycle or ESP32 not publishing P_avg)")
