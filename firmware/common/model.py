#!/usr/bin/env python3

import csv
import os

F_CLK = 10e6
MASK32 = 0xFFFFFFFF
# LO word of each counter in 'results' (28 CSR + mcycle start/end).
WLO = {
    "alu": 0, "mul": 2, "mulh": 4, "div_n": 6, "mem": 8, "ctrl": 10,
    "fp_add": 12, "fp_mul": 14, "fp_fma": 16, "fp_div": 18,
    "fp_sqrt": 20, "fp_noncomp": 22, "fp_conv": 24, "divcyc": 26,
    "fetch": 30,   # w30=fetch_min, w31=fetch_max (rango=max-min)   # w30=fetch_min, w31=fetch_max -> rango = max-min (footprint)
}
INSTR = ["alu", "mul", "mulh", "mem", "ctrl", "fp_add", "fp_mul",
         "fp_fma", "fp_div", "fp_sqrt", "fp_noncomp", "fp_conv"]
# 'div' goes by CYCLE (DIVCYC), not by instruction (hybrid model)


def to_int(s):
    s = s.strip()
    return int(s, 16) if s.lower().startswith("0x") else int(s)


def val(w, lo):
    return w[lo] + (w[lo + 1] << 32)


# die temperature (C) at which P_idle was measured in the last coefficients.csv
# read; None if the file does not carry it. Records the baseline thermal condition.
ultimo_T_idle = None


def cargar_coefficients(path):
    """Reads a coefficients.csv (common format) -> (P_idle, {cat: coef}).
    The baseline temperature (row 'T_idle', if present) is stored in the global
    model.ultimo_T_idle and is NOT put into coef."""
    global ultimo_T_idle
    ultimo_T_idle = None
    P_idle = None
    coef = {}
    with open(path) as f:
        for row in csv.reader(f):
            # skip comments, header and empty/mangled rows (e.g. the
            # '#...' line that LibreOffice re-saves as ',,')
            if not row or not row[0].strip() or row[0].startswith("#") or row[0] == "parametro":
                continue
            name = row[0].strip()
            c = float(row[1])
            if name == "P_idle":
                P_idle = c
            elif name == "T_idle":
                ultimo_T_idle = c
            else:
                coef[name] = c
    return P_idle, coef


def cargar_pendiente_termica(path):
    """Slope b [W/C] of the P_idle(T) fit from the thermal sweep
    (pidle_fit.csv, row 'b_W_per_C'). None if there is no sweep."""
    if not os.path.exists(path):
        return None
    with open(path) as f:
        for row in csv.reader(f):
            if row and row[0].strip() == "b_W_per_C":
                return float(row[1])
    return None


def correccion_termica(temp, T_idle, b):
    """Baseline temperature leakage term: b*(T - T_idle) [W].
    P_idle(T) = P_idle_ref + correccion_termica(T, T_ref, b). Returns 0 if
    any datum is missing (no sweep or no temperature reading)."""
    if b is None or T_idle is None or temp is None:
        return 0.0
    return b * (temp - T_idle)


def potencia_dinamica(w, coef):
    """DYNAMIC power [W] of the run (w = 30 words of 'results'). This is the MODEL
    itself: instruction energy / T. WITHOUT idle."""
    T_cyc = (w[29] - w[28]) & MASK32
    E = sum(coef.get(c, 0.0) * val(w, WLO[c]) for c in INSTR)   # per instruction
    E += coef.get("div", 0.0) * val(w, WLO["divcyc"])           # div per cycle
    E += coef.get("div_n", 0.0) * val(w, WLO["div_n"])          # div: base cost per instr (differential model)
    P = E / (T_cyc / F_CLK)
    rng = (w[31] - w[30]) if w[31] >= w[30] else 0              # fetch range = footprint [bytes]
    P += coef.get("fetch", 0.0) * rng                          # fetch power (Tiwari) ~ footprint
    return P


def predecir(w, P_idle, coef):
    """Approx TOTAL power [W] = P_idle (static) + dynamic power. Idle is added ONLY
    here, at the end of the computation; the model itself (potencia_dinamica) is dynamic."""
    return P_idle + potencia_dinamica(w, coef)


def contadores(w):
    """Decodes ALL classifier counters from the 30 words, to store them
    alongside each run (everything available)."""
    return {
        "n_alu":   val(w, WLO["alu"]),
        "n_mul":   val(w, WLO["mul"]),
        "n_mulh":  val(w, WLO["mulh"]),
        "n_div":   val(w, WLO["div_n"]),
        "c_div":   val(w, WLO["divcyc"]),
        "n_mem":   val(w, WLO["mem"]),
        "n_ctrl":  val(w, WLO["ctrl"]),
        "n_fp_add": val(w, WLO["fp_add"]),
        "n_fp_mul": val(w, WLO["fp_mul"]),
        "n_fp_fma": val(w, WLO["fp_fma"]),
        "n_fp_div": val(w, WLO["fp_div"]),
        "n_fp_sqrt": val(w, WLO["fp_sqrt"]),
        "n_fp_noncomp": val(w, WLO["fp_noncomp"]),
        "n_fp_conv": val(w, WLO["fp_conv"]),
        "n_fetch": (w[31] - w[30]) if w[31] >= w[30] else 0,  # rango fetch = max-min (footprint)
        "mcycle":  (w[29] - w[28]) & MASK32,
    }


# counter column order (for CSV/Sheet)
COLS_CONTADORES = ["n_alu", "n_mul", "n_mulh", "n_div", "c_div",
                   "n_mem", "n_ctrl", "n_fp_add", "n_fp_mul", "n_fp_fma",
                   "n_fp_div", "n_fp_sqrt", "n_fp_noncomp", "n_fp_conv",
                   "n_fetch", "mcycle"]
