#!/usr/bin/env python3
"""Caracterizacion de coeficientes energeticos — script UNICO para los 2 metodos:

  bucles    (M1): un bucle dominado por categoria, aislada contra idle.
                  coef_i = (P_cat - P_idle) * T / n_i   (TODO por n_i, incl. div:
                  la latencia ~fija c~21 queda plegada en el coef, no se usa DIVCYC)
  regresion (M2): programas mixtos reales; NNLS CON intercepto (modelo efimon,
                  el del paper): P_med = P_static + sum e_i * (n_i / T),
                  con barrido de intensidad d100/d60/d30

Cada metodo guarda datos.csv y coeficientes.csv en su directorio (bucles/ o
regresion/) y sube a su pestaña del Sheet. verificar.py consume esos
coeficientes.csv con el mismo formato comun.

Uso:
    python3 caracterizar.py bucles --repeats 2
    python3 caracterizar.py bucles alu mul div
    python3 caracterizar.py regresion
    python3 caracterizar.py regresion --refit
    python3 caracterizar.py regresion --pidle bucles
"""
import argparse
import csv
import os
import re
import shutil
import statistics
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "comun"))
import jtag      # noqa: E402
import modelo    # noqa: E402
import sheet     # noqa: E402

# La campana tiene corridas LARGAS (idle ~40 s, variantes _d30 ~20 s de ventana),
# asi que fuerza un timeout amplio y varios reintentos aunque el entorno traiga
# un GDB_TIMEOUT/RETRIES chico (p.ej. el del smoke-test: GDB_TIMEOUT=15). Sin
# esto, el idle de 40 s aborta la campana entera al primer intento.
if jtag.GDB_TIMEOUT < 120:
    jtag.GDB_TIMEOUT = 480
if jtag.RETRIES < 3:
    jtag.RETRIES = 5

F_CLK = modelo.F_CLK
DIR_BUCLES = os.path.join(HERE, "bucles")
DIR_REGR = os.path.join(HERE, "regresion")

# --- comun a ambos metodos -------------------------------------------------

def respaldar_coef(coef_csv):
    """Copia con timestamp en campanas/: coeficientes.csv se sobreescribe en
    cada campana, pero el juego de CADA campana queda respaldado (para el
    analisis de reproducibilidad y para poder restaurar un juego anterior)."""
    d = os.path.join(os.path.dirname(coef_csv), "campanas")
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, time.strftime("coeficientes_%Y%m%d_%H%M%S.csv"))
    shutil.copy(coef_csv, dst)
    return dst


def run_make(met_dir):
    subprocess.run(["make", "-B", "all"], cwd=os.path.join(met_dir, "fuentes"), check=True)


def find_elf(prog, met_dir):
    # idle.elf vive en bucles/ (es el run de referencia del piso para ambos)
    for cand in (os.path.join(met_dir, "elf", f"{prog}.elf"),
                 os.path.join(DIR_BUCLES, "elf", f"{prog}.elf"), prog):
        if os.path.exists(cand):
            return cand
    raise FileNotFoundError(f"{prog}.elf no existe (corre 'make' en {met_dir}/fuentes)")


def medir_uno(prog, elf, inbox):
    """Corre un elf por JTAG y devuelve (P_med, T, contadores, temp_str)."""
    if prog == "idle":
        # idle (wfi) es robusto a la inflacion del JTAG (una ventana de idle
        # inflada sigue midiendo idle) y tiene IPC~0 por diseno -> 1 corrida.
        # Si la fila del ESP32 no llega (subida perdida), se reintenta la
        # MEDIDA completa hasta 3 veces en vez de abortar la campana.
        for intento in range(1, 4):
            inbox.reset()          # drena ventanas pendientes antes de medir
            words = jtag.run_one(elf)
            try:
                P_med = inbox.get_pavg()
                break
            except TimeoutError:
                if intento == 3:
                    raise
                print(f"    idle: ventana sin P_avg del ESP32; REINTENTO "
                      f"({intento}/3)")
    else:
        words, P_med = jtag.run_medido(elf, inbox.get_pavg, reset=inbox.reset)
    w = [modelo.to_int(x) for x in words]
    cont = modelo.contadores(w)
    T = cont["mcycle"] / F_CLK
    # Variantes de ciclo de trabajo: mcycle se CONGELA durante el wfi, asi que
    # mcycle/F_CLK es solo el tiempo ACTIVO. La ventana real (wall) la MIDE el
    # ESP32 (duration_ms): la usamos directo en vez de asumir el duty de diseno
    # (mcycle/duty). Robusto a kernels fetch-dominados como dctrl, donde la
    # intensidad real NO es exactamente 60/30% -> mcycle/duty daba T mal.
    if prog.endswith(("_d60", "_d30")):
        dur = getattr(inbox, "ultima_dur_s", None)
        if dur and dur > 0:
            T = dur                                  # wall REAL del ESP32
        else:                                        # fallback: duty de diseno
            T /= 0.60 if prog.endswith("_d60") else 0.30
    tC = jtag.ultima_temp_cC                 # temperatura del die (XADC), centi-C
    tstr = f"{tC/100:.2f}" if tC is not None else ""
    return P_med, T, cont, tstr


def subir_sheet(hoja, **campos):
    try:    # la pestaña del Sheet es secundaria: datos.csv ya tiene la fila
        sheet.subir(hoja, **campos)
    except Exception as e:
        print(f"    [aviso] no se pudo subir a '{hoja}' ({e}); sigo (esta en datos.csv)")


def rotar_si_header_distinto(path, header):
    """Si datos.csv existe con OTRO encabezado (esquema viejo), lo aparta a
    datos_legacy_*.csv en vez de apendear filas desalineadas."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        actual = next(csv.reader(f), None)
    if actual != header:
        legado = path.replace(".csv", time.strftime("_legacy_%Y%m%d_%H%M.csv"))
        os.rename(path, legado)
        print(f"[aviso] {os.path.basename(path)} tenia esquema viejo -> movido a {os.path.basename(legado)}")


# --- metodo 1: bucles dominados ---------------------------------------------

CATS = ["idle", "alu", "mul", "mulh", "div", "mem", "ctrl",
        "fp_add", "fp_mul", "fp_fma", "fp_div", "fp_sqrt",
        "fp_noncomp", "fp_conv"]
COEF_CATS = CATS[1:]
# div se calibra por INSTRUCCION (n_div): la latencia ~fija del bucle dominado
# (c~21) queda plegada en el coeficiente. Modelo homogeneo (todo por conteo).
DENOM = {"alu": "n_alu", "mul": "n_mul", "mulh": "n_mulh", "div": "n_div",
         "mem": "n_mem", "ctrl": "n_ctrl", "fp_add": "n_fp_add",
         "fp_mul": "n_fp_mul", "fp_fma": "n_fp_fma", "fp_div": "n_fp_div",
         "fp_sqrt": "n_fp_sqrt", "fp_noncomp": "n_fp_noncomp",
         "fp_conv": "n_fp_conv"}


def cmd_bucles(args):
    datos_csv = os.path.join(DIR_BUCLES, "datos.csv")
    coef_csv = os.path.join(DIR_BUCLES, "coeficientes.csv")

    cats = args.categorias or CATS
    invalid = [c for c in cats if c not in CATS]
    if invalid:
        sys.exit(f"categorias invalidas: {', '.join(invalid)}")
    if "idle" not in cats:
        cats = ["idle"] + cats

    if not args.no_build:
        run_make(DIR_BUCLES)
    for cat in cats:
        find_elf(cat, DIR_BUCLES)

    header = ["fecha", "categoria", "rep", "P_med_W", "T_s", "temp_C"] + modelo.COLS_CONTADORES
    rotar_si_header_distinto(datos_csv, header)
    inbox = sheet.Inbox()
    runs = {c: [] for c in cats}
    new = not os.path.exists(datos_csv)
    with open(datos_csv, "a", newline="") as fd:
        wr = csv.writer(fd)
        if new:
            wr.writerow(header)
        t0 = time.time()
        total = len(cats) * args.repeats
        i = 0
        for cat in cats:
            elf = find_elf(cat, DIR_BUCLES)
            for rep in range(1, args.repeats + 1):
                i += 1
                nom = cat if args.repeats == 1 else f"{cat} (rep {rep}/{args.repeats})"
                eta = ""
                if i > 1:
                    falta = (time.time() - t0) / (i - 1) * (total - i + 1)
                    eta = f"   [faltan ~{falta/60:.0f} min]"
                print(f"==> [{i:2d}/{total}] {nom}{eta}")
                P_med, T, cont, tstr = medir_uno(cat, elf, inbox)
                runs[cat].append({"P_med": P_med, "T": T, "cont": cont, "temp": tstr})
                ts = time.strftime("%Y-%m-%d %H:%M:%S")
                wr.writerow([ts, cat, rep, f"{P_med:.6f}", f"{T:.6f}", tstr]
                            + [cont[k] for k in modelo.COLS_CONTADORES])
                fd.flush()
                subir_sheet("bucles", categoria=cat, rep=rep, P_med_W=f"{P_med:.6f}",
                            T_s=f"{T:.6f}", temp_C=tstr,
                            **{k: cont[k] for k in modelo.COLS_CONTADORES})
                die = f"   die {tstr} C" if tstr else ""
                if cat == "idle":
                    print(f"    P = {P_med:.4f} W  (linea base de la sesion){die}")
                else:
                    sobre = (P_med - runs["idle"][0]["P_med"]) * 1e3 \
                        if runs.get("idle") else None
                    txt = f"  ({sobre:+6.1f} mW sobre idle)" if sobre is not None else ""
                    print(f"    P = {P_med:.4f} W{txt}   ventana {T:5.1f} s{die}")
                time.sleep(3)

    P_idle = statistics.mean(r["P_med"] for r in runs["idle"])
    # temperatura del die a la que se midio la linea base: la P_idle vale para esa
    # condicion termica; se guarda para poder corregir la deriva por temperatura.
    temps_idle = [float(r["temp"]) for r in runs["idle"] if r.get("temp")]
    T_idle = statistics.mean(temps_idle) if temps_idle else None
    coefs = {}
    resumen = []
    for cat in COEF_CATS:
        if not runs.get(cat):
            continue
        cat_coefs, deltas, denoms = [], [], []
        for r in runs[cat]:
            delta = r["P_med"] - P_idle
            denom = r["cont"][DENOM[cat]]
            if denom <= 0:
                raise RuntimeError(f"{cat}: denominador {DENOM[cat]} es 0")
            cat_coefs.append(delta * r["T"] / denom)
            deltas.append(delta)
            denoms.append(denom)
        coefs[cat] = statistics.mean(cat_coefs)
        resumen.append((cat, statistics.mean(deltas), statistics.mean(denoms),
                        coefs[cat], len(cat_coefs)))

    # Fusion con el archivo previo: una corrida parcial (p.ej. solo ctrl) NO
    # borra los coeficientes de las otras categorias. Es valido mezclar: cada
    # coef es un delta interno a SU sesion (P_cat y P_idle de la misma sesion);
    # P_idle/T_idle del archivo quedan los de HOY, que son los que la
    # verificacion de hoy necesita como linea base.
    if os.path.exists(coef_csv):
        try:
            _, prev = modelo.cargar_coeficientes(coef_csv)
            faltan = {c: v for c, v in prev.items()
                      if c in COEF_CATS and c not in coefs}
            if faltan:
                print(f"  (conservo del archivo previo: {', '.join(sorted(faltan))})")
                coefs.update(faltan)
        except Exception as e:
            print(f"  [aviso] no pude leer coeficientes previos ({e}); "
                  f"escribo solo lo medido")

    with open(coef_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([f"# Bucles dominados (M1). Generado {time.strftime('%Y-%m-%d %H:%M:%S')}.",
                    "coef=(P_cat-P_idle)*T/n_i por instruccion (div: c~21 plegado)."])
        w.writerow(["parametro", "coef", "unidad"])
        w.writerow(["P_idle", f"{P_idle:.6f}", "W"])
        if T_idle is not None:
            w.writerow(["T_idle", f"{T_idle:.2f}", "C"])
        for cat in COEF_CATS:
            if cat in coefs:
                w.writerow([cat, f"{coefs[cat]:.6e}", "J/instr"])

    tstr = f" @ {T_idle:.1f} C" if T_idle is not None else ""
    print(f"\n=== M1 bucles: coeficientes de la sesion ===")
    print(f"P_idle = {P_idle:.4f} W{tstr}   (n_idle = {len(runs['idle'])})")
    print(f"{'categoria':10s} {'delta[mW]':>10s} {'eventos':>15s} {'coef[nJ]':>9s}  unidad     reps")
    for cat, delta, denom, coef, n in resumen:
        print(f"{cat:10s} {delta*1e3:10.2f} {denom:15,.0f} {coef*1e9:9.3f}  {'nJ/instr':9s} {n}")
    resp = respaldar_coef(coef_csv)
    print(f"\nGuardado: {datos_csv}, {coef_csv} + pestaña 'bucles' del Sheet.")
    print(f"copia de esta campana: {os.path.relpath(resp, HERE)}")
    print(f"siguiente paso: python3 verificar.py --metodo bucles <benchmarks>")


# --- metodo 2: regresion con linea base fija ---------------------------------

# categorias del modelo y el contador que regresiona cada una. div va por
# INSTRUCCION (n_div), homogeneo con M1 (modelo B): antes iba por ciclo (c_div),
# lo que le daba una tasa ~20x mayor y empujaba el modo comun/overhead hacia ctrl.
DYN = ["alu", "mul", "mulh", "div", "mem", "ctrl", "fp_add", "fp_mul",
       "fp_fma", "fp_div", "fp_sqrt", "fp_noncomp", "fp_conv"]
REGR = {"alu": "n_alu", "mul": "n_mul", "mulh": "n_mulh", "div": "n_div",
        "mem": "n_mem", "ctrl": "n_ctrl", "fp_add": "n_fp_add",
        "fp_mul": "n_fp_mul", "fp_fma": "n_fp_fma", "fp_div": "n_fp_div",
        "fp_sqrt": "n_fp_sqrt", "fp_noncomp": "n_fp_noncomp",
        "fp_conv": "n_fp_conv"}
# Kernels DOMINANTES por categoria: dan IDENTIFICABILIDAD a la regresion (rompen
# la colinealidad). Corren a d100. dmem es SOLO-STORES (73% mem, alu bajo): rompe
# la colinealidad mem-alu que hacia que efimon subvalue mem (absorbido por alu).
# dalu NO se usa (alu ya domina en los mixtos y colgaba el JTAG por IPC alto).
DOM = ["dmul", "dmulh", "ddiv", "dctrl"]
# Sondas fp DOMINANTES (una por categoria fp). Estructura de M1: operandos
# CONSTANTES en registros, sin loads dentro del bucle (el flw por elemento
# deadlockeaba la FPU de este bitstream). Corren a d100. Cada una domina ~55% su
# categoria -> identificable, ya NO se hereda de M1.
FP_PROBES = ["fpadd", "fpmul", "fpfma", "fpdiv", "fpsqrt", "fpnoncomp", "fpconv"]
# Programas MIXTOS: aportan el OVERHEAD inter-instruccion realista y el barrido de
# intensidad (_d60/_d30) que ancla P_static. Ampliado con usuarios de mul/mulh/div
# (mulhash64, mulhscale, mulhstream, fir, ratscale, modpow, trialdiv) para SUBIR
# el soporte de esas categorias (antes 4-9/21 -> el diferencial las inflaba por
# pocos puntos). Todos existen y tienen sus duty variants.
MIXTOS = ["memcpy", "matmul", "dotprod", "gcd", "radix", "histogram", "sort",
          "modmul", "memfill", "wmac",
          "mulhash64", "mulhscale", "mulhstream", "fir", "ratscale",
          "modpow", "trialdiv"]
# La expansion de intensidad (_d60/_d30) es DATA-DRIVEN: se expande CADA programa
# que YA tenga su variante generada en fuentes/duty_variants.mk (via gen_duty.py);
# los que no la tienen corren a d100. Asi "todos con duty" = generar la variante de
# cada uno con gen_duty, sin tocar codigo, y ninguno se rompe por falta de ELF.
# DUTY_BAD: programas con variante pero que NO se deben expandir. Vacio desde que
# el wall de las variantes duty se toma del duration_ms medido por el ESP32 (no del
# mcycle/duty): eso arreglo dctrl (fetch-dominado, cuyo mcycle no daba el duty real).
DUTY_BAD = set()
DEFAULT_PROGS = DOM + FP_PROBES + MIXTOS


def _progs_con_duty():
    """Programas con variante _d60/_d30 ya generada (en duty_variants.mk), menos
    los DUTY_BAD. La expansion de intensidad usa SOLO estos; el resto va a d100."""
    mk = os.path.join(DIR_REGR, "fuentes", "duty_variants.mk")
    if not os.path.exists(mk):
        return set()
    return set(re.findall(r"(\w+)_d60\.elf\s*:", open(mk).read())) - DUTY_BAD


def cargar_pidle(fuente):
    """fuente = 'bucles' (lee P_idle de bucles/coeficientes.csv) o un numero en W."""
    try:
        return float(fuente)
    except ValueError:
        pass
    if fuente != "bucles":
        sys.exit(f"--pidle invalido: {fuente} (usa medir|bucles o un numero en W)")
    path = os.path.join(DIR_BUCLES, "coeficientes.csv")
    P_idle, _ = modelo.cargar_coeficientes(path)
    if P_idle is None:
        sys.exit(f"no encontre P_idle en {path}; caracteriza primero con 'bucles'")
    return P_idle


def _temp_f(s):
    """Temperatura del CSV/Sheet a float; tolera coma decimal (locale es-ES) y
    vacio. None si no se puede parsear -> sin correccion para esa corrida."""
    try:
        return float(str(s).replace(",", ".")) if s not in (None, "") else None
    except ValueError:
        return None


def leer_datos(datos_csv):
    """Lee de datos.csv la ULTIMA campana completa -> [(prog, P_med, T, cont,
    temp)] (--refit). datos.csv acumula TODAS las campanas historicas: mezclar
    campanas en un re-ajuste da basura. Cada campana empieza
    con su fila 'idle' (protocolo), asi que se toma desde el ultimo idle que
    encabece un bloque con >= DYN+1 corridas de calibracion."""
    todas = []
    with open(datos_csv) as f:
        for r in csv.DictReader(f):
            cont = {k: int(r.get(k, 0)) for k in modelo.COLS_CONTADORES}
            prog = r["programa"]
            if prog.endswith(("_d60", "_d30")):
                # duty: usa el wall REAL medido (columna T_s, escrita por
                # medir_uno desde duration_ms del ESP32). Fallback al /duty viejo
                # si la fila no lo trae (datos historicos).
                try:
                    T = float(r["T_s"])
                except (KeyError, ValueError, TypeError):
                    T = cont["mcycle"] / F_CLK / (0.60 if prog.endswith("_d60") else 0.30)
            else:
                T = cont["mcycle"] / F_CLK
            todas.append((r["programa"], float(r["P_med_W"]), T,
                          cont, r.get("temp_C", "")))
    campanas = []
    for fila in todas:
        if fila[0] == "idle" or not campanas:
            campanas.append([])
        campanas[-1].append(fila)
    completas = [c for c in campanas
                 if sum(1 for f in c if f[0] != "idle") >= len(DYN) + 1]
    if not completas:
        sys.exit(f"{datos_csv}: ninguna campana completa (idle + >={len(DYN)+1} corridas)")
    mayor = max(len(c) for c in completas)
    if len(completas[-1]) < mayor:
        print(f"[AVISO] la ultima campana tiene {len(completas[-1])} corridas pero "
              f"hay una anterior con {mayor}: parece PARCIAL (abortada). El refit "
              f"usa la ultima igual; si no era la intencion, borra sus filas de "
              f"datos.csv o vuelve a medir.")
    return completas[-1]


MIN_SUP = 1   # soporte minimo (programas base con la categoria activa) para que
              # M2 la regresione; 0 => columna nula (singular) -> hereda M1. Cada
              # categoria tiene su kernel DOMINANTE (dmul/dmulh/ddiv/dctrl + las 7
              # fp*), asi que 1 programa fuertemente dominante ya la hace
              # identificable. alu/mem no tienen dominante pero dominan en los
              # mixtos (memcpy 65%, memfill 83%).


def ajustar_efimon(cal_rows, idle_rows):
    """Ajuste al estilo EfiMon: NNLS CON INTERCEPTO sobre la potencia TOTAL.
    Requiere el barrido de intensidad (variantes _d60/_d30: misma composicion,
    distinta utilizacion), que decorrelaciona el modo comun de las categorias
    por diseno experimental. Las filas de idle (tasas 0) anclan el intercepto,
    que hace el papel de P_static (ec. 5 de EfiMon).

    Solo regresiona las categorias IDENTIFICABLES (soporte >= MIN_SUP en los
    programas base): una categoria que casi no aparece -o nunca- da una columna
    (casi) nula que vuelve la matriz singular (cond -> 1e35) y NNLS reparte su
    potencia de forma arbitraria, clavando categorias debiles en 0. Las no
    identificables (tipicamente las fp, y a veces div) quedan fuera del ajuste y
    se heredan de M1 aguas arriba. La columna de FETCH se OMITE aqui: en el set
    de calibracion el footprint casi no varia (col. casi constante, colineal con
    el intercepto) -> el termino de fetch lo aporta M1 (barrido), no M2."""
    from scipy.optimize import nnls
    rows = cal_rows + idle_rows
    base = [r for r in cal_rows if not r[0].endswith(("_d60", "_d30"))]
    cats = [c for c in DYN
            if sum(1 for r in base if r[3][REGR[c]] > 0) >= MIN_SUP]
    R = np.array([[r[3][REGR[c]] / r[2] if r[2] > 0 else 0.0 for c in cats]
                  for r in rows])
    y = np.array([r[1] for r in rows])
    X = np.hstack([np.ones((len(y), 1)), R])
    sd = X.std(0); sd[0] = 1.0; sd[sd == 0] = 1.0
    e, _ = nnls(X / sd, y)
    e = e / sd
    P_static = e[0]
    coefs = dict(zip(cats, e[1:1 + len(cats)]))
    pred = X @ e
    resid = y - pred
    ss_res = float(resid @ resid)
    delta = y - P_static
    ss_tot = float(delta @ delta)
    info = {"P_idle": P_static, "cats": cats,
            "r2": 1 - ss_res / ss_tot if ss_tot > 0 else float("nan"),
            "rmse": (ss_res / len(y)) ** 0.5,
            "cond": float(np.linalg.cond(X / sd)),
            "pred_abs": pred[:len(cal_rows)]}
    return coefs, info


def ajustar_diferencial(rows, P_idle):
    """Regresion DIFERENCIAL no negativa (inspirada en EfiMon): separa la
    intensidad de la composicion. delta = alfa*r_total + sum extra_k * r_k,
    con NNLS (coeficientes >= 0). alfa = costo base por instruccion retirada
    (modo comun: fetch/pipeline/switching); extra_k = sobrecosto de la categoria
    sobre ese base. A diferencia de efimon, el modo comun (el overhead
    inter-instruccion) NO se vuelca en una sola categoria (ctrl) sino en alfa,
    que se reparte sobre TODAS las instrucciones -> escala parejo con cualquier
    mezcla y GENERALIZA (transfiere a benchmarks con otra composicion).
    Coeficientes absolutos guardados: cat = alfa + extra; div por ciclo =
    extra_div; div_n = alfa (por instr).

    Solo mete en el ajuste las categorias IDENTIFICABLES (soporte >= MIN_SUP en
    programas base): una columna (casi) nula -tipico de las fp que no se
    ejecutan- vuelve el sistema singular (cond=inf). Las no identificables se
    heredan de M1 aguas arriba."""
    from scipy.optimize import nnls
    base = [r for r in rows if not r[0].endswith(("_d60", "_d30"))]
    cats = [c for c in DYN
            if sum(1 for r in base if r[3][REGR[c]] > 0) >= MIN_SUP]
    # r_total = tasa de instrucciones retiradas (todas por CONTEO, div incluido
    # via n_div -> homogeneo). alfa*r_total = modo comun (overhead por instr).
    Tn = np.array([r[2] for r in rows])
    rtot = np.array([sum(r[3][REGR[c]] for c in cats) for r in rows]) / Tn
    # REFERENCIA = mul (la categoria mas barata, segun M1 mul<alu): alfa = e_mul.
    # Asi las demas (alu, mem, fp...) tienen extra POSITIVO y se separan del piso,
    # en vez de aplastarse todas en alfa (con alu de referencia, mul<alu daba extra
    # negativo -> la NNLS lo clampeaba a 0 y quedaban alu=mul=mem=... iguales).
    ref = "mul" if "mul" in cats else "alu"
    otras = [c for c in cats if c != ref]            # ref = alfa puro (sin extra)
    Rx = np.array([[r[3][REGR[c]] / r[2] for c in otras] for r in rows])
    # TERMINO DE STALL (Tiwari, 3.er termino): ciclos que NO retiran instruccion
    # (latencia multi-ciclo de div/mulh/fp_div/fp_sqrt + burbujas de pipeline).
    # Consumen potencia que el modelo por-instruccion (alfa+extra) ignora ->
    # subvalua los programas de mucho stall. n_stall = mcycle - instr retiradas.
    stall = np.array([r[3].get("n_stall", 0) / r[2] for r in rows])
    # INTERCEPTO ajustado (b0), NO se resta el idle medido. Empiricamente da
    # coeficientes MUCHO mas estables campana a campana: el idle medido tiene ruido
    # (~3 mW sesion a sesion) que, restado a TODOS los puntos, contamina el ajuste;
    # el intercepto ABSORBE ese ruido de linea base y el barrido de duty lo deja
    # bien identificado (b0 sale ~= idle medido). La prediccion sigue usando el
    # idle de la SESION de validacion (b0 es solo de calibracion / chequeo).
    ones = np.ones((len(rows), 1))
    X = np.hstack([ones, rtot[:, None], Rx, stall[:, None]])
    y = np.array([r[1] for r in rows])               # P_med (con intercepto)
    sd = X.std(0); sd[sd == 0] = 1.0
    e, _ = nnls(X / sd, y)
    e = e / sd
    b0 = e[0]
    alfa = e[1]
    extras = dict(zip(otras, e[2:2 + len(otras)]))
    e_stall = e[-1]
    coefs = {ref: alfa}                               # energia POR INSTRUCCION (ref=piso)
    for c in otras:                                  # div incluido, uniforme
        coefs[c] = alfa + extras[c]
    coefs["stall"] = e_stall                         # energia POR CICLO de stall
    # PLIEGA los ciclos multi-ciclo en el coeficiente: coef += stall*(ciclos-1).
    # Asi div/mulh/fp_div/fp_sqrt quedan con su ENERGIA COMPLETA por instruccion
    # (comparable con M1, ~10 nJ div). potencia_dinamica descuenta esos ciclos del
    # stall -> misma prediccion, coeficientes con sentido fisico. Equivalente exacto.
    for c, ciclos in modelo.CICLOS_PLEGADOS.items():
        coefs[c] = coefs.get(c, 0.0) + e_stall * (ciclos - 1)
    pred = X @ e                                     # predice P_med (incluye b0)
    delta = y - P_idle                               # senal dinamica (R2 comparable)
    resid = y - pred                                 # residual (b0 ~= idle -> dinamico)
    ss_res = float(resid @ resid); ss_tot = float(delta @ delta)
    info = {"P_idle": P_idle, "b0": b0, "alfa": alfa, "cats": cats, "e_stall": e_stall,
            "r2": 1 - ss_res / ss_tot if ss_tot > 0 else float("nan"),
            "rmse": (ss_res / len(y)) ** 0.5,
            "cond": float(np.linalg.cond(X / sd)),
            "pred_abs": pred}
    return coefs, info


def ajustar(rows, P_idle):
    """Regresion SIN intercepto con P_idle FIJO: delta = P_med - P_idle = R @ e.
    R[k,c] = contador_c / T (tasa). Se escalan las columnas (solo dividir por sd,
    SIN centrar, para conservar el origen del modelo sin intercepto) y se resuelve
    por lstsq; luego se des-escala. Devuelve (coefs, info)."""
    R = np.array([[r[3][REGR[c]] / r[2] for c in DYN] for r in rows])
    delta = np.array([r[1] for r in rows]) - P_idle
    sd = R.std(0)
    sd[sd == 0] = 1.0
    Rs = R / sd
    e_s, *_ = np.linalg.lstsq(Rs, delta, rcond=None)
    e = e_s / sd
    pred = R @ e
    resid = delta - pred
    ss_res = float(resid @ resid)
    ss_tot = float(delta @ delta)                  # vs 0: no hay intercepto
    info = {
        "P_idle": P_idle,
        "r2": 1 - ss_res / ss_tot if ss_tot > 0 else float("nan"),
        "rmse": (ss_res / len(delta)) ** 0.5,
        "cond": float(np.linalg.cond(Rs)),
        "pred_abs": pred + P_idle,                 # P predicha absoluta por corrida
    }
    return dict(zip(DYN, e)), info


def medir_regresion(progs, no_build, datos_csv):
    """Corre cada programa por JTAG, recupera P_avg del Sheet, escribe datos.csv."""
    if not no_build:
        run_make(DIR_REGR)
    elfs = {p: find_elf(p, DIR_REGR) for p in progs}
    header = ["fecha", "programa", "P_med_W", "T_s", "temp_C"] + modelo.COLS_CONTADORES
    rotar_si_header_distinto(datos_csv, header)
    inbox = sheet.Inbox()
    rows = []
    new = not os.path.exists(datos_csv)
    with open(datos_csv, "a", newline="") as fd:
        wr = csv.writer(fd)
        if new:
            wr.writerow(header)
        t0 = time.time()
        P_idle_ses = None                      # primera corrida idle de la sesion
        # ETA por CLASE de corrida: una variante _d30 tarda ~3x mas de reloj
        # que su version al 100% (misma actividad, estirada con pausas), asi
        # que un promedio simple sub/sobre-estima segun el orden de la campana
        clase = lambda p: ("idle" if p == "idle" else
                           "d60" if p.endswith("_d60") else
                           "d30" if p.endswith("_d30") else "d100")
        dur = {}                               # clase -> [duraciones medidas]
        for i, prog in enumerate(progs, 1):
            duty = {"d60": "int. 60%", "d30": "int. 30%", "idle": "linea base",
                    "d100": "int. 100%"}[clase(prog)]
            eta = ""
            if dur:
                media = sum(sum(v) for v in dur.values()) / sum(len(v) for v in dur.values())
                est = lambda c: sum(dur[c]) / len(dur[c]) if dur.get(c) else media
                falta = sum(est(clase(p)) for p in progs[i - 1:])
                eta = f"   [faltan ~{falta/60:.0f} min]"
            print(f"==> [{i:2d}/{len(progs)}] {prog:14s} ({duty}){eta}")
            t_run = time.time()
            P_med, T, cont, tstr = medir_uno(prog, elfs[prog], inbox)
            rows.append((prog, P_med, T, cont, tstr))
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            wr.writerow([ts, prog, f"{P_med:.6f}", f"{T:.6f}", tstr]
                        + [cont[k] for k in modelo.COLS_CONTADORES])
            fd.flush()
            subir_sheet("regresion", programa=prog, P_med_W=f"{P_med:.6f}", T_s=f"{T:.6f}",
                        temp_C=tstr, **{k: cont[k] for k in modelo.COLS_CONTADORES})
            die = f"   die {tstr} C" if tstr else ""
            if prog == "idle":
                P_idle_ses = P_med
                print(f"    P = {P_med:.4f} W  (linea base de la sesion){die}")
            else:
                sobre = f"  ({(P_med-P_idle_ses)*1e3:+6.1f} mW sobre idle)" \
                        if P_idle_ses is not None else ""
                print(f"    P = {P_med:.4f} W{sobre}   ventana {T:5.1f} s{die}")
            dur.setdefault(clase(prog), []).append(time.time() - t_run + 3)
            time.sleep(3)
    print(f"\ncampana de medicion: {len(progs)} corridas en "
          f"{(time.time()-t0)/60:.0f} min")
    return rows


def cmd_regresion(args):
    datos_csv = os.path.join(DIR_REGR, "datos.csv")
    coef_csv = os.path.join(DIR_REGR, "coeficientes.csv")

    if args.refit:
        if not os.path.exists(datos_csv):
            sys.exit(f"no existe {datos_csv}; corre la medicion primero (sin --refit)")
        rows = leer_datos(datos_csv)
        print(f"--refit: ultima campana completa de datos.csv "
              f"({len(rows)} corridas, sin volver a medir)")
    else:
        progs = args.programas or DEFAULT_PROGS
        if not getattr(args, "medir_solo", False) and len(progs) < len(DYN) + 1:
            sys.exit(f"hacen falta >= {len(DYN)+1} programas mixtos (M > 7 incognitas); "
                     f"diste {len(progs)}")
        # con --pidle medir, idle.elf va PRIMERO en la misma sesion (mismo piso)
        # Barrido de intensidad (efimon): expande a _d60/_d30 SOLO los mixtos.
        # Los kernels DOMINANTES (d*) y las sondas fp corren a d100: aportan la
        # SEPARACION de categorias (identificabilidad); el barrido de intensidad
        # que ancla P_static lo dan los mixtos. Asi los dominantes/fp no necesitan
        # variantes de duty (que requieren un pase de timing previo).
        if args.modelo == "efimon" or getattr(args, "duty", False):
            con_duty = _progs_con_duty()
            progs = [v for q in progs
                     for v in ((q, q + "_d60", q + "_d30") if q in con_duty else [q])]
        run_list = (["idle"] + progs) if args.pidle == "medir" else progs
        rows = medir_regresion(run_list, args.no_build, datos_csv)

    if getattr(args, "medir_solo", False):
        print("\n--medir-solo: SIN ajuste. Resumen (T = wall real medido por el ESP32):")
        print(f"  {'prog':16}{'P_med[W]':>10}{'T_wall[s]':>11}{'mcycle':>13}")
        for prog, P, T, cont, ts in rows:
            print(f"  {prog:16}{P:>10.5f}{T:>11.2f}{cont['mcycle']:>13,}")
        return

    # separa la corrida de referencia (idle) de las de calibracion
    cal_rows = [r for r in rows if r[0] != "idle"]
    idle_rows = [r for r in rows if r[0] == "idle"]
    if args.pidle == "medir":
        if not idle_rows:
            sys.exit("--pidle medir pero no hay corrida 'idle' (mide sin --refit, o usa --pidle bucles)")
        P_idle = idle_rows[-1][1]
        T_idle = _temp_f(idle_rows[-1][4]) if len(idle_rows[-1]) > 4 else None
        fuente = f"idle medido en sesion ({P_idle:.4f} W)"
    else:
        P_idle = cargar_pidle(args.pidle)
        # si viene de bucles, hereda su T_idle; si es un numero suelto, no hay
        T_idle = modelo.ultimo_T_idle if args.pidle == "bucles" else None
        fuente = args.pidle

    if len(cal_rows) < len(DYN) + 1:
        sys.exit(f"solo {len(cal_rows)} programas de calibracion; hacen falta >= {len(DYN)+1}")

    print(f"\n=== ajuste M2 [modelo {args.modelo}] ===")
    if args.modelo == "efimon":
        if not idle_rows:
            sys.exit("--modelo efimon necesita la corrida de idle en sesion (--pidle medir)")
        coefs, info = ajustar_efimon(cal_rows, idle_rows)
        dif = (info["P_idle"] - P_idle) * 1e3
        print(f"P_static (intercepto ajustado) = {info['P_idle']:.4f} W   "
              f"(idle medido {P_idle:.4f} W, diferencia {dif:+.1f} mW)")
        P_idle = info["P_idle"]
    elif args.modelo == "diferencial":
        coefs, info = ajustar_diferencial(cal_rows, P_idle)
        print(f"alfa (costo base por instruccion) = {info['alfa']*1e9:.3f} nJ   "
              f"P_idle = {P_idle:.4f} W (fijo, de '{fuente}')")
    else:
        coefs, info = ajustar(cal_rows, P_idle)
        print(f"P_idle = {P_idle:.4f} W (fijo, de '{fuente}'; sin intercepto)")

    # Hibrido M2+M1: las categorias que M2 (efimon/diferencial) NO puede
    # identificar (soporte < MIN_SUP: tipicamente las fp que no se ejecutan y a
    # veces div) se HEREDAN de M1 (bucles dominados, que si las midio aisladas).
    # Igual el termino de fetch (M2 lo omite: footprint casi constante en la
    # calibracion). Asi la matriz de M2 no queda singular por columnas nulas.
    info["heredadas"] = []
    if args.modelo in ("efimon", "diferencial"):
        m1_path = os.path.join(DIR_BUCLES, "coeficientes.csv")
        if os.path.exists(m1_path):
            _, m1 = modelo.cargar_coeficientes(m1_path)
            for c in DYN:
                if c not in coefs:
                    coefs[c] = m1.get(c, 0.0)
                    info["heredadas"].append(c)
            if "fetch" in m1:
                coefs["fetch"] = m1["fetch"]
        else:
            for c in DYN:
                coefs.setdefault(c, 0.0)
            print(f"  [AVISO] no hay M1 en {m1_path}; categorias no "
                  f"identificables quedan en 0")
        print(f"  M2 regresiona {len(info['cats'])} categorias "
              f"({', '.join(info['cats'])}); "
              f"hereda de M1: {', '.join(info['heredadas']) or '(ninguna)'}")

    with open(coef_csv, "w", newline="") as f:
        wc = csv.writer(f)
        desc = {"clasico": f"linea base FIJA de '{fuente}', SIN intercepto",
                "diferencial": "NNLS diferencial (alfa*r_total + sobrecostos)",
                "efimon": "NNLS CON INTERCEPTO ajustado (P_idle = P_static de la"
                          " regresion; barrido de intensidad d100/d60/d30)"}[args.modelo]
        wc.writerow([f"# Regresion (M2, modelo {args.modelo}). Generado {time.strftime('%Y-%m-%d %H:%M:%S')}."
                     f" {desc}. n={len(cal_rows)} corridas,"
                     f" R2={info['r2']:.4f}, RMSE={info['rmse']*1e3:.2f} mW, cond={info['cond']:.1f}"])
        wc.writerow(["parametro", "coef", "unidad"])
        wc.writerow(["P_idle", f"{info['P_idle']:.6f}", "W"])
        if "b0" in info:                              # intercepto ajustado (chequeo
            wc.writerow(["b0", f"{info['b0']:.6f}", "W"])  # de consistencia vs P_idle)
        if T_idle is not None:
            wc.writerow(["T_idle", f"{T_idle:.2f}", "C"])
        for c in DYN:
            wc.writerow([c, f"{coefs[c]:.6e}", "J/instr"])   # todo por instruccion (div: n_div)
        if "stall" in coefs:
            wc.writerow(["stall", f"{coefs['stall']:.6e}", "J/ciclo"])  # ciclos sin retiro
        if "fetch" in coefs:
            wc.writerow(["fetch", f"{coefs['fetch']:.6e}", "W/byte"])  # potencia de fetch ~ footprint

    print(f"{len(cal_rows)} corridas de calibracion"
          + (f" + {len(idle_rows)} idle" if args.modelo == "efimon" and idle_rows else "")
          + f":  R2={info['r2']:.4f}  RMSE={info['rmse']*1e3:.2f} mW  "
            f"cond={info['cond']:.1f}")

    # soporte = en cuantos programas base (sin variantes de intensidad) la
    # categoria esta activa: con soporte bajo el coeficiente es fragil
    base = [r for r in cal_rows if not r[0].endswith(("_d60", "_d30"))]
    heredadas = set(info.get("heredadas", []))
    print(f"\n{'categoria':10s} {'coef[nJ]':>9s}  unidad     soporte     fuente")
    for c in DYN:
        sop = sum(1 for r in base if r[3][REGR[c]] > 0)
        src = "M1 (heredado)" if c in heredadas else "M2"
        flag = "   <-- NEGATIVO" if coefs[c] < 0 else ""
        print(f"{c:10s} {coefs[c]*1e9:9.3f}  {'nJ/instr':9s} {sop:2d}/{len(base)} prog   {src}{flag}")
    if "fetch" in coefs:
        rngs = [r[3]["n_fetch"] for r in base if r[3].get("n_fetch", 0) > 0]
        span = f"{min(rngs)}..{max(rngs)} B" if rngs else "-"
        print(f"{'fetch':10s} {coefs['fetch']*1e9:9.3f}  nW/byte   footprint {span}")

    print("\nresiduos del ajuste (medido - ajustado), peores primero:")
    print(f"{'programa':16s} {'med[W]':>8s} {'fit[W]':>8s} {'resid[mW]':>10s} {'resid[%]':>9s}")
    pares_rp = sorted(zip(cal_rows, info["pred_abs"]),
                      key=lambda rp: -abs(rp[0][1] - rp[1]))
    for r, pa in pares_rp:
        prog, P_med = r[0], r[1]
        print(f"{prog:16s} {P_med:8.4f} {pa:8.4f} {(P_med-pa)*1e3:+10.2f} "
              f"{100*(P_med-pa)/P_med:+9.3f}")
    peor = pares_rp[0]
    print(f"\npeor residuo: {peor[0][0]} "
          f"({(peor[0][1]-peor[1])*1e3:+.2f} mW = {100*(peor[0][1]-peor[1])/peor[0][1]:+.3f}%)")
    resp = respaldar_coef(coef_csv)
    print(f"Guardado: {coef_csv}")
    print(f"copia de esta campana: {os.path.relpath(resp, HERE)}")
    print("siguiente paso: python3 verificar.py --metodo regresion <benchmarks>")


# --- entrada ------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="metodo", required=True)

    ab = sub.add_parser("bucles", aliases=["1"], help="M1: bucles dominados por categoria")
    ab.add_argument("categorias", nargs="*", default=CATS,
                    help="categorias a medir; si se omite mide idle+7 categorias")
    ab.add_argument("--repeats", "--repeat", type=int, default=1)
    ab.add_argument("--no-build", action="store_true", help="no recompilar ELF antes de medir")
    ab.set_defaults(fn=cmd_bucles)

    ar = sub.add_parser("regresion", aliases=["2"], help="M2: regresion sobre programas mixtos")
    ar.add_argument("programas", nargs="*", default=DEFAULT_PROGS,
                    help="conjunto de calibracion; si se omite usa el por defecto")
    ar.add_argument("--modelo", default="efimon", choices=["clasico", "diferencial", "efimon"],
                    help="ajuste: 'clasico' (tasas por categoria, lstsq) o "
                         "'diferencial' (alfa*r_total + sobrecostos, NNLS) o "
                         "'efimon' (NNLS con intercepto + barrido de intensidad "
                         "_d60/_d30; corre 3 variantes por programa)")
    ar.add_argument("--pidle", default="medir",
                    help="P_idle FIJO: 'medir' (corre idle.elf en ESTA sesion, default), "
                         "'bucles' (de su coeficientes.csv) o un numero en W")
    ar.add_argument("--refit", action="store_true",
                    help="NO mide: re-ajusta desde datos.csv (para reusar mediciones ya hechas)")
    ar.add_argument("--no-build", action="store_true", help="no recompilar ELF antes de medir")
    ar.add_argument("--duty", action="store_true",
                    help="fuerza el barrido de intensidad _d60/_d30 de los mixtos "
                         "aunque el modelo NO sea efimon (p.ej. diferencial): mas "
                         "puntos a distinta actividad -> fit mejor condicionado")
    ar.add_argument("--medir-solo", dest="medir_solo", action="store_true",
                    help="solo MIDE (escribe datos.csv) y muestra P_med/T/mcycle, "
                         "SIN ajustar; sirve para validar timings de pocos programas "
                         "(p.ej. dctrl --duty). Ignora el minimo de programas.")
    ar.set_defaults(fn=cmd_regresion)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
