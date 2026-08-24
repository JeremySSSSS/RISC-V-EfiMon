#!/usr/bin/env python3

import csv
import os

F_CLK = 10e6
MASK32 = 0xFFFFFFFF
# word LO de cada contador en 'results' (28 CSR + mcycle ini/fin).
WLO = {
    "alu": 0, "mul": 2, "mulh": 4, "div_n": 6, "mem": 8, "ctrl": 10,
    "fp_add": 12, "fp_mul": 14, "fp_fma": 16, "fp_div": 18,
    "fp_sqrt": 20, "fp_noncomp": 22, "fp_conv": 24, "divcyc": 26,
    "fetch": 30,   # w30=fetch_min, w31=fetch_max (rango=max-min)
}
INSTR = ["alu", "mul", "mulh", "mem", "ctrl", "fp_add", "fp_mul",
         "fp_fma", "fp_div", "fp_sqrt", "fp_noncomp", "fp_conv"]
# Ciclos ~por instruccion de las categorias MULTI-CICLO. En el M2 diferencial su
# coeficiente PLIEGA estos ciclos (energia completa por instruccion, comparable con
# M1), y potencia_dinamica los DESCUENTA del stall para no doble-contar. Valores
# reales medidos de los bucles dominados de M1 (mcycle/n_cat): div=21 (=DIVCYC),
# mulh=5, fp_div=12, fp_sqrt=6. El resto de las categorias son de 1 ciclo.
CICLOS_PLEGADOS = {"div": 21, "mulh": 5, "fp_div": 12, "fp_sqrt": 6}


def to_int(s):
    s = s.strip()
    return int(s, 16) if s.lower().startswith("0x") else int(s)


def val(w, lo):
    return w[lo] + (w[lo + 1] << 32)


# temperatura del die (C) a la que se midio P_idle en el ultimo coeficientes.csv
# leido; None si el archivo no la trae. Registra la condicion termica de la base.
ultimo_T_idle = None


def cargar_coeficientes(path):
    """Lee un coeficientes.csv (formato comun) -> (P_idle, {cat: coef}).
    La temperatura de la linea base (fila 'T_idle', si existe) queda en el global
    modelo.ultimo_T_idle y NO se mete en coef."""
    global ultimo_T_idle
    ultimo_T_idle = None
    P_idle = None
    coef = {}
    with open(path) as f:
        for row in csv.reader(f):
            # salta comentarios, encabezado y filas vacias/mutiladas (p.ej. la
            # linea '#...' que LibreOffice re-guarda como ',,')
            if not row or not row[0].strip() or row[0].startswith("#") or row[0] == "parameter":
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
    """Pendiente b [W/C] del ajuste P_idle(T) del barrido termico
    (pidle_fit.csv, fila 'b_W_per_C'). None si no hay barrido."""
    if not os.path.exists(path):
        return None
    with open(path) as f:
        for row in csv.reader(f):
            if row and row[0].strip() == "b_W_per_C":
                return float(row[1])
    return None


def correccion_termica(temp, T_idle, b):
    """Termino de fuga por temperatura de la linea base: b*(T - T_idle) [W].
    P_idle(T) = P_idle_ref + correccion_termica(T, T_ref, b). Devuelve 0 si
    falta algun dato (sin barrido o sin lectura de temperatura)."""
    if b is None or T_idle is None or temp is None:
        return 0.0
    return b * (temp - T_idle)


def potencia_dinamica(w, coef):
    """P DINAMICA [W] del run (w = 32 words de 'results'). MODELO UNIFICADO:

        P_din = (escala / T) * sum_i  e_i * n_i

    e_i = energia por INSTRUCCION de la categoria (la latencia c_i esta plegada en
    el coeficiente): alu/mem/ctrl/mul/fp* son de 1 ciclo; mulh pliega c=5; div
    pliega c=21 (latencia ~fija del bucle dominado; energia por division). Asi el
    modelo es homogeneo: solo conteos por categoria, sin usar contadores de ciclo.
    'escala' corrige el overhead inter-instruccion (bucles dominados lo sub-estiman)."""
    T_cyc = (w[29] - w[28]) & MASK32
    n_div = val(w, WLO["div_n"])
    E = sum(coef.get(c, 0.0) * val(w, WLO[c]) for c in INSTR)   # e_i * n_i (mulh: c=5 plegado)
    E += coef.get("div", 0.0) * n_div                          # e_div * n_div (c=21 plegado)
    # termino de STALL (M2 diferencial): potencia de los ciclos que NO retiran
    # instruccion. Los coef de las cat MULTI-CICLO (div/mulh/fp_div/fp_sqrt) ya
    # PLIEGAN sus ciclos en el coeficiente, asi que esos ciclos se DESCUENTAN del
    # stall (si no, doble conteo). El stall queda para los ciclos "sobrantes":
    # fetch, flush de branch, load-use, burbujas. n_stall = mcycle - retiradas -
    # ciclos-extra-plegados. Ver CICLOS_PLEGADOS.
    if coef.get("stall"):
        total = sum(val(w, WLO[c]) for c in INSTR) + n_div
        extra = sum((c - 1) * (n_div if k == "div" else val(w, WLO[k]))
                    for k, c in CICLOS_PLEGADOS.items())
        n_stall = T_cyc - total - extra
        if n_stall > 0:
            E += coef["stall"] * n_stall
    E *= coef.get("escala", 1.0)                                # overhead inter-instruccion (M1)
    return E / (T_cyc / F_CLK)


def predecir(w, P_idle, coef):
    """P TOTAL aprox [W] = P_idle (estatica) + P dinamica. El idle se suma SOLO
    aqui, al final del calculo; el modelo en si (potencia_dinamica) es dinamico."""
    return P_idle + potencia_dinamica(w, coef)


def contadores(w):
    """Decodifica TODOS los contadores del clasificador de los 30 words, para
    guardarlos junto a cada corrida (todo lo posible)."""
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
        # ciclos de stall = mcycle - instrucciones retiradas (div cuenta como 1);
        # latencia multi-ciclo de div + load-use + saltos. Termino Tiwari de M1.
        "n_stall": max(0, ((w[29] - w[28]) & MASK32)
                     - (sum(val(w, WLO[c]) for c in INSTR) + val(w, WLO["div_n"]))),
    }


# orden de columnas de contadores (para CSV/Sheet)
COLS_CONTADORES = ["n_alu", "n_mul", "n_mulh", "n_div", "c_div",
                   "n_mem", "n_ctrl", "n_fp_add", "n_fp_mul", "n_fp_fma",
                   "n_fp_div", "n_fp_sqrt", "n_fp_noncomp", "n_fp_conv",
                   "n_fetch", "mcycle", "n_stall"]
