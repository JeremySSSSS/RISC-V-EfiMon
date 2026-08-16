#!/usr/bin/env python3
"""Interfaz grafica (web local) para caracterizacion y validacion.

Envuelve los scripts existentes (caracterizar.py, verificar.py) SIN duplicar
logica: cada boton lanza el script como subproceso y la consola muestra su salida
en vivo. Un solo trabajo a la vez (el banco es exclusivo). Solo escucha en
localhost. Rediseno por pestanas: M1, M2 y Validar, cada una con sus controles y
un panel de datos (coeficientes, temperatura, graficas) de su ultima campana.

Uso:
    python3 gui.py            # abre http://localhost:8237 (solo esta PC)
    python3 gui.py --lan      # ademas accesible desde la red local (telefono)
"""
import csv as csvmod
import glob
import json
import math
import os
import re
import signal
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "comun"))
import modelo  # noqa: E402

PORT = 8237
CATS = ["alu", "mul", "mulh", "div", "mem", "ctrl", "fp_add", "fp_mul",
        "fp_fma", "fp_div", "fp_sqrt", "fp_noncomp", "fp_conv"]
# Set de calibracion M2 REDISENADO para que TODAS las categorias sean
# identificables: kernels DOMINANTES por categoria (d*, ~60-86% de su categoria)
# + sondas fp dominadas + mixtos (overhead realista + barrido de intensidad).
# Los dominantes rompen la colinealidad de los mixtos (donde mul/mulh/div/ctrl
# nunca pasaban del 27-38%). Ver caracterizar.py: DOM + FP_PROBES + MIXTOS.
PROGS_M2 = ["dmul", "dmulh", "ddiv", "dctrl", "fpadd", "fpmul", "fpfma", "fpdiv", "fpsqrt", "fpnoncomp", "fpconv", "memcpy", "matmul", "dotprod", "gcd", "radix", "histogram", "sort", "modmul", "memfill", "wmac", "mulhash64", "mulhscale", "mulhstream", "fir", "ratscale", "modpow", "trialdiv"]                                 # mixtos


def benchmarks():
    d = os.path.join(HERE, "benchmarks")
    return sorted(f[:-4] for f in os.listdir(d) if f.endswith(".elf")) \
        if os.path.isdir(d) else []


def es_carga_real_c(n):
    """Cargas 'reales' (kernels de BEEBS en benchmarks/beebs/, extra en
    benchmarks/extra/ o propias en C), a diferencia del conjunto oficial en
    ensamblador de histograma fijo."""
    return (os.path.exists(os.path.join(HERE, "benchmarks", "beebs", f"{n}.c"))
            or os.path.exists(os.path.join(HERE, "benchmarks", "extra", f"{n}.c"))
            or os.path.exists(os.path.join(HERE, "benchmarks", f"wl_{n}.c")))


# ---------------- trabajo en curso (uno a la vez: el banco es exclusivo) ----
class Trabajo:
    def __init__(self):
        self.lock = threading.Lock()
        self.proc = None
        self.cola = []         # comandos pendientes (tandas multiples)
        self.nombre = ""
        self.log = []          # lineas acumuladas de la corrida actual
        self.inicio = None

    def corriendo(self):
        return self.proc is not None and self.proc.poll() is None

    def corriendo_o_encolado(self):
        return self.corriendo() or self.cola

    def lanzar(self, nombre, cmds):
        """cmds: lista de argv a correr EN SECUENCIA (p.ej. N tandas).
        Se aborta la cola si un comando falla o si el usuario detiene."""
        with self.lock:
            if self.corriendo_o_encolado():
                return False, f"ya hay un trabajo corriendo: {self.nombre}"
            self.nombre, self.log, self.inicio = nombre, [], time.time()
            self.cola = list(cmds)
            threading.Thread(target=self._correr_cola, daemon=True).start()
            return True, "lanzado"

    def _correr_cola(self):
        total = len(self.cola)
        i = 0
        rc = 0
        while self.cola:
            i += 1
            cmd = self.cola.pop(0)
            if total > 1:
                self.log.append(f"===== tanda {i}/{total} =====")
            self.log.append(f"$ {' '.join(cmd)}")
            self.proc = subprocess.Popen(
                cmd, cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, start_new_session=True)
            for linea in self.proc.stdout:
                self.log.append(linea.rstrip("\n"))
            rc = self.proc.wait()
            if rc != 0 and self.cola:
                self.log.append(f"[GUI] rc={rc}: cancelo las {len(self.cola)} tandas restantes")
                self.cola = []
        dur = time.time() - self.inicio
        self.log.append(f"--- fin (rc={rc}, {dur/60:.1f} min) ---")

    def detener(self):
        if self.cola:
            self.log.append(f"[GUI] cola de {len(self.cola)} tandas cancelada")
            self.cola = []
        if self.corriendo():
            os.killpg(os.getpgid(self.proc.pid), signal.SIGINT)
            self.log.append("[GUI] SIGINT enviado (corte limpio)...")
            return True
        return False


JOB = Trabajo()

# marca el inicio del ULTIMO batch de validacion (cuando se presiona "Validate"):
# el panel solo muestra las tandas creadas DESPUES de esto -> cada press empieza
# de cero, pero acumula TODAS las runs de ese press (runs=N). None = sin press
# esta sesion (el panel cae al agrupado por cercania temporal, ver _ultima_validacion).
_VAL_BATCH_START = None

# ---------------- construccion de comandos (todo whitelisteado) -------------
PY = [sys.executable, "-u"]


def cmd_de(req):
    """req (dict del cliente) -> (nombre, [argv, ...]) o lanza ValueError."""
    a = req.get("accion")
    if a == "m1":
        cats = [c for c in req.get("cats", []) if c in CATS] or CATS
        cmd = PY + ["caracterizar.py", "bucles"] + cats
        rep = int(req.get("repeats", 1))
        if rep > 1:
            cmd += ["--repeats", str(min(rep, 30))]
        if req.get("nobuild"):
            cmd.append("--no-build")
        return en_campanas(f"M1 bucles ({','.join(cats)})", cmd, req)
    if a == "m2":
        # model: 'efimon' (paper: NNLS + intercept) or 'diferencial' (+ base alfa
        # + stall term; fixes efimon's mem undervaluation). div by n_div.
        model = req.get("model", "diferencial")
        if model not in ("efimon", "diferencial"):
            model = "diferencial"
        progs = [p for p in req.get("progs", []) if p in PROGS_M2] or PROGS_M2
        cmd = PY + ["caracterizar.py", "regresion", "--modelo", model] + progs
        if req.get("nobuild"):
            cmd.append("--no-build")
        if req.get("duty"):
            cmd.append("--duty")
        suf = " +duty" if req.get("duty") else ""
        return en_campanas(f"M2 regression [{model}]{suf}", cmd, req)
    if a == "verificar":
        progs = [p for p in req.get("progs", []) if p in benchmarks()]
        if not progs:
            raise ValueError("elegi al menos un benchmark")
        global _VAL_BATCH_START
        _VAL_BATCH_START = time.time()        # each "Validate" press starts a fresh batch
        cmd = PY + ["verificar.py"] + progs   # measures baseline; predicts with available methods
        solo = req.get("solo")                # None=both, 'bucles'=M1 only, 'regresion'=M2 only
        if solo in ("bucles", "regresion"):
            cmd += ["--solo", solo]
        n = min(max(int(req.get("campanas", 1)), 1), 30)
        suf = f" x{n} runs" if n > 1 else ""
        met = {"bucles": "M1 only", "regresion": "M2 only"}.get(solo, "both methods")
        return (f"Validate {met} ({len(progs)} prog){suf}", [cmd] * n)
    if a == "testm2":
        cmd = PY + ["test_m2.py"] + (["--duty"] if req.get("duty") else [])
        return ("Probar M2 (smoke-test)", [cmd])
    if a == "promediar":
        n = min(max(int(req.get("n", 3)), 2), 30)
        met = req.get("metodo", "bucles")
        if met not in ("bucles", "regresion"):
            met = "bucles"
        lbl = "M1" if met == "bucles" else "M2"
        return (f"Promediar {n} tandas {lbl}",
                [PY + ["promediar_tandas.py", "--metodo", met, "--n", str(n)]])
    if a == "m1full":
        cats = [c for c in req.get("cats", []) if c in CATS] or CATS
        m1 = PY + ["caracterizar.py", "bucles"] + cats
        kbs = [x for x in req.get("kb", "").replace(" ", "").split(",") if x.isdigit()] \
              or ["4", "8", "16", "24", "32", "48", "64", "96", "128", "192", "256"]
        lcref = min(max(int(req.get("lcref", 20000)), 500), 2000000)
        barr = PY + ["barrido_fetch.py", "--kb", ",".join(kbs), "--lc-ref", str(lcref)]
        return ("M1 completo (loops -> fetch)", [m1, barr])
    if a == "barrido":
        kbs = [x for x in req.get("kb", "").replace(" ", "").split(",") if x.isdigit()]
        if not kbs:
            raise ValueError("footprints invalidos (usa p.ej. 4,8,16,32,64,128,256)")
        lcref = min(max(int(req.get("lcref", 20000)), 500), 2000000)
        cmd = PY + ["barrido_fetch.py", "--kb", ",".join(kbs), "--lc-ref", str(lcref)]
        return (f"Barrido fetch ({len(kbs)} puntos)", [cmd])
    if a == "overhead":
        # experimento propio de M1: mide el overhead inter-instruccion y escribe
        # 'escala' en bucles/coeficientes.csv. Por defecto usa mezclas realistas;
        # con 'pairs' mide los pares 50/50 (mecanismo, NO escribe escala).
        cmd = PY + ["overhead_m1.py"]
        if req.get("pairs"):
            cmd.append("--pairs")
        if req.get("dry"):
            cmd.append("--dry")
        modo = "pares 50/50 (mecanismo)" if req.get("pairs") else "mezcla realista (escala)"
        return (f"Overhead inter-instruccion M1 - {modo}", [cmd])
    raise ValueError(f"accion desconocida: {a}")


def en_campanas(nombre, cmd, req):
    """N tandas EN SECUENCIA: la 1.a compila (salvo --no-build explicito);
    las demas siempre con --no-build -> binarios identicos entre tandas."""
    n = min(max(int(req.get("campanas", 1)), 1), 30)
    cmds = [cmd] + [cmd + ["--no-build"] if "--no-build" not in cmd else cmd
                    for _ in range(n - 1)]
    suf = f" x{n} tandas" if n > 1 else ""
    return nombre + suf, cmds


# ---------------- estado (coeficientes + temperatura + ultima validacion) ---
def _leer_coef(path, m1_ref=None):
    """Lee un coeficientes.csv completo -> dict con P_idle, T_idle, coef (nJ),
    extras (escala/fetch/stall), y meta del encabezado (R2/RMSE/cond/n).
    Si m1_ref (coef de M1) esta dado, marca las categorias heredadas (iguales)."""
    P_idle, coef = modelo.cargar_coeficientes(path)
    d = {"fecha": time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(path))),
         "P_idle_W": round(P_idle, 6) if P_idle is not None else None,
         "T_idle_C": modelo.ultimo_T_idle,
         "coef": {k: round(coef[k] * 1e9, 3) for k in CATS if k in coef},
         "escala": round(coef["escala"], 4) if "escala" in coef else None,
         "fetch_nWb": round(coef["fetch"] * 1e9, 3) if "fetch" in coef else None,
         "stall_nJ": round(coef["stall"] * 1e9, 3) if "stall" in coef else None,
         "b0_W": round(coef["b0"], 6) if "b0" in coef else None,
         "heredadas": []}
    if m1_ref:
        d["heredadas"] = [k for k in CATS if k in coef and k in m1_ref
                          and abs(coef[k] - m1_ref[k]) < 1e-15]
    with open(path) as f:
        head = f.readline()
    for key, pat in (("R2", r"R2=([0-9.]+)"), ("RMSE_mW", r"RMSE=([0-9.]+)"),
                     ("cond", r"cond=([0-9.eE+]+)"), ("n", r"n=([0-9]+)")):
        m = re.search(pat, head)
        if m:
            d[key] = m.group(1)
    return d, coef


def _csv_rows(path):
    with open(path) as f:
        return list(csvmod.DictReader(f))


def _ultima_validacion():
    """Validation of the latest SESSION: all runs (timestamps) done close together
    in time (gap < 45 min). The scatter shows points from ALL those runs (so you
    see run-to-run spread / reproducibility); RMSE and error% (RMSE / mean power)
    are computed over ALL accumulated points."""
    d = os.path.join(HERE, "validaciones")
    fs = glob.glob(os.path.join(d, "validacion_*_medir_*.csv"))
    if not fs:
        return None
    def _dt(ts):
        try:
            return time.mktime(time.strptime(ts, "%Y%m%d_%H%M%S"))
        except ValueError:
            return 0.0
    if _VAL_BATCH_START is not None:
        # only runs of the CURRENT "Validate" press: files created after the press
        # (a small margin absorbs clock/mtime jitter). Reset per press, accumulate
        # every run of that press (runs=N).
        keep = {f for f in fs if os.path.getmtime(f) >= _VAL_BATCH_START - 5}
        tss = sorted({"_".join(os.path.basename(f).rsplit("_", 2)[-2:]).replace(".csv", "")
                      for f in keep})
        if not tss:
            return None
        ses = tss
    else:
        # no press this GUI session (e.g. just restarted): fall back to grouping
        # the trailing runs done close together (gap < 45 min) as "the last batch".
        tss = sorted({"_".join(os.path.basename(f).rsplit("_", 2)[-2:]).replace(".csv", "")
                      for f in fs})
        if not tss:
            return None
        ses = [tss[-1]]
        for a in tss[-2::-1]:
            if _dt(ses[-1]) - _dt(a) <= 45 * 60:
                ses.append(a)
            else:
                break
        ses = sorted(set(ses))
    out = {"ts": (f"{ses[0]} … {ses[-1]}" if len(ses) > 1 else ses[-1]),
           "nruns": len(ses), "metodos": {}}
    for met in ("bucles", "regresion"):
        rows, meds = [], []
        for ts in ses:
            p = os.path.join(d, f"validacion_{met}_medir_{ts}.csv")
            if not os.path.exists(p):
                continue
            for r in _csv_rows(p):
                try:
                    med, pred = float(r["P_med_W"]), float(r["P_pred_W"])
                except (KeyError, ValueError):
                    continue
                rows.append({"prog": r.get("programa", ""), "med": round(med, 5),
                             "pred": round(pred, 5), "err": r.get("err_pct", ""),
                             "temp": r.get("temp_C", "")})
                meds.append(med)
        if not rows:
            continue
        # AVERAGE the measured power per program across runs (prediction is
        # deterministic, only P_med carries noise) -> the error metric uses the
        # noise-reduced per-program mean, so more runs => cleaner (lower) error.
        # 'rows' keeps ALL points for the scatter (shows run-to-run spread).
        byp = {}
        for x in rows:
            byp.setdefault(x["prog"], {"med": [], "pred": []})
            byp[x["prog"]]["med"].append(x["med"])
            byp[x["prog"]]["pred"].append(x["pred"])
        avg = [{"prog": p, "med": sum(o["med"]) / len(o["med"]),
                "pred": sum(o["pred"]) / len(o["pred"])} for p, o in byp.items()]
        pbar = sum(a["med"] for a in avg) / len(avg)
        rmse = math.sqrt(sum((a["pred"] - a["med"]) ** 2 for a in avg) / len(avg))
        out["metodos"][met] = {"rows": rows, "rmse_mW": round(rmse * 1e3, 3),
                               "err_pct": round(100 * rmse / pbar, 4),
                               "pbar": round(pbar, 5), "npts": len(rows),
                               "nbench": len(avg)}
    return out if out["metodos"] else None


def estado():
    est = {"metodos": {}, "validacion": None}
    m1_coef = None
    for met in ("bucles", "regresion"):
        p = os.path.join(HERE, met, "coeficientes.csv")
        if not os.path.exists(p):
            continue
        try:
            info, raw = _leer_coef(p, m1_ref=m1_coef)
            est["metodos"][met] = info
            if met == "bucles":
                m1_coef = raw
        except Exception as e:
            est["metodos"][met] = {"error": str(e)}
    try:
        est["validacion"] = _ultima_validacion()
    except Exception as e:
        est["validacion"] = {"error": str(e)}
    try:
        est["mix"] = _instr_mix()
    except Exception as e:
        est["mix"] = {"error": str(e)}
    try:
        est["vmix"] = _instr_mix_val()
    except Exception as e:
        est["vmix"] = {"error": str(e)}
    return est


_MIX_CATS = ["alu", "mul", "mulh", "div", "mem", "ctrl", "fp_add", "fp_mul",
             "fp_fma", "fp_div", "fp_sqrt", "fp_noncomp", "fp_conv"]


def _instr_mix():
    """Instruction-mix (% per category) of each base program in the last M2
    campaign, from regresion/datos.csv. Reads the last block starting at 'idle'
    and keeps the d100 base programs (no _d60/_d30)."""
    p = os.path.join(HERE, "regresion", "datos.csv")
    if not os.path.exists(p):
        return None
    rows = _csv_rows(p)
    idxs = [i for i, r in enumerate(rows) if r.get("programa") == "idle"]
    if not idxs:
        return None
    camp = rows[idxs[-1]:]
    out = []
    for r in camp:
        prog = r.get("programa", "")
        if prog == "idle" or prog.endswith(("_d60", "_d30")):
            continue
        ns = {}
        for c in _MIX_CATS:
            key = "n_div" if c == "div" else "n_" + c
            try:
                ns[c] = int(r.get(key, 0) or 0)
            except ValueError:
                ns[c] = 0
        tot = sum(ns.values()) or 1
        row = {"prog": prog, "tot": tot}
        row.update({c: round(100 * ns[c] / tot) for c in _MIX_CATS})
        out.append(row)
    return {"cats": _MIX_CATS, "rows": out}


def _instr_mix_val():
    """Instruction-mix (% per category) of each VALIDATION benchmark, from the
    latest validation batch. Counters are deterministic, so one row per program
    (first occurrence) is enough. Same categories/format as _instr_mix so the
    Validate tab reuses the M2 mix table."""
    d = os.path.join(HERE, "validaciones")
    fs = glob.glob(os.path.join(d, "validacion_bucles_medir_*.csv"))
    if _VAL_BATCH_START is not None:
        fs = [f for f in fs if os.path.getmtime(f) >= _VAL_BATCH_START - 5]
    if not fs:
        return None
    latest = max(fs, key=os.path.getmtime)
    seen, out = set(), []
    for r in _csv_rows(latest):
        prog = r.get("programa", "")
        if not prog or prog in seen:
            continue
        seen.add(prog)
        ns = {}
        for c in _MIX_CATS:
            key = "n_div" if c == "div" else "n_" + c
            try:
                ns[c] = int(r.get(key, 0) or 0)
            except ValueError:
                ns[c] = 0
        tot = sum(ns.values()) or 1
        row = {"prog": prog, "tot": tot}
        row.update({c: round(100 * ns[c] / tot) for c in _MIX_CATS})
        out.append(row)
    return {"cats": _MIX_CATS, "rows": out} if out else None


# ---------------- pagina (pestanas M1 / M2 / Validar) -----------------------
def _chips(ns, grp, on=True):
    return "".join(
        f'<label class="chip"><input type="checkbox" name="{grp}" value="{n}"'
        f'{" checked" if on else ""}>{n}</label>' for n in ns)


def pagina():
    bm = benchmarks()
    html = PAGINA_TMPL
    html = html.replace("__M1CATS__", _chips(CATS, "m1cat"))
    html = html.replace("__M2PROGS__", _chips(PROGS_M2, "m2prog"))
    html = html.replace("__VPROG__", _chips(bm, "vprog"))
    html = html.replace("__NM2__", str(len(PROGS_M2)))
    return html


PAGINA_TMPL = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>TFG bench — CV32E40P characterization</title>
<style>
 :root{--bg:#12151a;--pan:#1b2129;--bd:#2c3540;--in:#242c36;--fg:#dde3ea;--mut:#7d8894;--ac:#8fb4d8;--blue:#2d6cdf}
 *{box-sizing:border-box}
 body{font-family:system-ui,sans-serif;margin:0;background:var(--bg);color:var(--fg)}
 header{padding:9px 18px;background:var(--pan);border-bottom:1px solid var(--bd);
   display:flex;align-items:center;gap:12px}
 header h1{font-size:15px;margin:0}
 #dot{width:10px;height:10px;border-radius:50%;background:#4a5561}
 #dot.on{background:#37c871;box-shadow:0 0 8px #37c871}
 nav{display:flex;gap:2px;padding:0 12px;background:var(--pan);border-bottom:1px solid var(--bd)}
 nav button{background:none;border:0;border-bottom:2px solid transparent;color:var(--mut);
   padding:9px 16px;font-size:13px;cursor:pointer}
 nav button.act{color:var(--fg);border-bottom-color:var(--blue)}
 main{padding:12px;max-width:1400px;margin:0 auto}
 .tab{display:none} .tab.act{display:block}
 .cols{display:grid;grid-template-columns:420px 1fr;gap:12px}
 @media(max-width:950px){.cols{grid-template-columns:1fr}}
 .card{background:var(--pan);border:1px solid var(--bd);border-radius:8px;padding:12px;margin-bottom:12px}
 .card h2{font-size:12px;margin:0 0 8px;color:var(--ac);text-transform:uppercase;letter-spacing:.5px}
 .chip{display:inline-flex;align-items:center;gap:3px;background:var(--in);border:1px solid var(--bd);
   border-radius:12px;padding:2px 8px;margin:2px;font-size:12px;cursor:pointer}
 .fila{margin:6px 0;font-size:13px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
 button.b{background:var(--blue);color:#fff;border:0;border-radius:6px;padding:6px 14px;font-size:13px;cursor:pointer}
 button.b:disabled{background:#4a5561;cursor:not-allowed}
 button.g{background:#1f7a4d} button.s{background:#3a4a5c} button.rojo{background:#c0392b}
 select,input[type=number],input[type=text]{background:var(--in);color:var(--fg);
   border:1px solid var(--bd);border-radius:4px;padding:3px 6px}
 .nota{font-size:11px;color:var(--mut);margin-top:4px}
 table{border-collapse:collapse;font-size:12px;width:100%}
 td,th{border-bottom:1px solid var(--bd);padding:3px 6px;text-align:right}
 th:first-child,td:first-child{text-align:left}
 .kpi{display:flex;gap:14px;flex-wrap:wrap;margin:4px 0 10px}
 .kpi div{background:var(--in);border:1px solid var(--bd);border-radius:6px;padding:6px 12px;min-width:78px}
 .kpi b{display:block;font-size:16px;color:#fff} .kpi span{font-size:10px;color:var(--mut);text-transform:uppercase}
 .her{color:#c98b3a} .badge{font-size:9px;color:#c98b3a;border:1px solid #c98b3a55;border-radius:3px;padding:0 3px;margin-left:4px}
 #log{background:#0d1013;border:1px solid var(--bd);border-radius:8px;padding:10px;height:34vh;
   overflow:auto;font:12px/1.45 ui-monospace,monospace;white-space:pre-wrap;margin-top:12px}
 svg text{fill:var(--mut);font-size:10px} .lg{display:flex;gap:14px;font-size:11px;margin-top:4px}
 .sw{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:4px;vertical-align:middle}
</style></head><body>
<header><h1>TFG bench · CV32E40P / PULPissimo</h1>
 <span id="dot"></span><span id="quehace" style="font-size:13px;color:#9fb0c0">idle</span>
 <span style="flex:1"></span>
 <button id="btnstop" class="b rojo" disabled onclick="detener()">Stop</button></header>
<nav>
 <button class="tabbtn act" data-t="m1">M1 · Loops</button>
 <button class="tabbtn" data-t="m2">M2 · Regression</button>
 <button class="tabbtn" data-t="val">Validate</button>
</nav>
<main>

<section id="tab-m1" class="tab act"><div class="cols">
 <div>
  <div class="card"><h2>Characterize M1 (dominated loops)</h2>
   <div>__M1CATS__</div>
   <div class="fila">repeats <input type="number" id="m1rep" value="1" min="1" max="30" style="width:52px">
    runs <input type="number" id="m1n" value="1" min="1" max="30" style="width:52px">
    <label class="chip"><input type="checkbox" id="m1nb">no rebuild</label></div>
   <div class="fila"><button class="b" onclick="m1()">Characterize M1</button>
    <button class="b g" onclick="m1full()">M1 + Fetch (loops → sweep)</button></div>
   <div class="fila">average <input type="number" id="prn" value="3" min="2" max="20" style="width:52px"> runs
    <button class="b s" onclick="promediar()">Average</button></div>
   <div class="nota">~15 min per run (all categories, reps=1). Each run is backed up to bucles/campanas/</div></div>

  <div class="card"><h2>Inter-instruction overhead (scale)</h2>
   <div class="fila"><button class="b g" onclick="overhead()">Measure overhead</button>
    <label class="chip"><input type="checkbox" id="ovpairs">50/50 pairs (mechanism)</label>
    <label class="chip"><input type="checkbox" id="ovdry">dry</label></div>
   <div class="nota">realistic mix → writes the <b>scale</b> factor. With 50/50 pairs it characterizes the
    mechanism (does not write). M1-only experiment.</div></div>

  <div class="card"><h2>Fetch sweep (calibrate e_fetch)</h2>
   <div class="fila">KB <input type="text" id="fkb" value="4,8,16,24,32,48,64,96,128,192,256" style="width:210px"></div>
   <div class="fila">LOOP_COUNT ref <input type="number" id="flc" value="20000" min="500" style="width:80px">
    <button class="b" onclick="barrido()">Sweep footprint</button></div>
   <div class="nota">fits e_ctrl = e_flush + e_fetch·(n_fetch/n_ctrl). Result in barrido_fetch.csv</div></div>
 </div>
 <div>
  <div class="card"><h2>M1 coefficients — latest campaign</h2>
   <div id="m1meta" class="nota">loading…</div>
   <div id="m1kpi" class="kpi"></div>
   <div id="m1chart"></div>
   <div id="m1tab" style="margin-top:8px"></div></div>
 </div>
</div></section>

<section id="tab-m2" class="tab"><div class="cols">
 <div>
  <div class="card"><h2>Characterize M2 (regression)</h2>
   <div class="fila">model
    <select id="m2model">
     <option value="efimon">efimon (paper: NNLS + intercept)</option>
     <option value="diferencial" selected>differential (intercept + α + stall)</option>
    </select>
    runs <input type="number" id="m2n" value="1" min="1" max="30" style="width:52px">
    <label class="chip"><input type="checkbox" id="m2nb">no rebuild</label>
    <label class="chip"><input type="checkbox" id="m2duty">+duty (intensity sweep _d60/_d30)</label></div>
   <details><summary style="font-size:12px;cursor:pointer;color:#9fb0c0">programs (__NM2__): dominant + fp + mixed</summary>
    <div>__M2PROGS__</div></details>
   <div class="fila"><button class="b" onclick="m2()">Characterize M2</button>
    <button class="b s" onclick="testm2()">Smoke test</button>
    <label class="chip"><input type="checkbox" id="tmduty">+duty</label></div>
   <div class="fila">average <input type="number" id="prn2" value="3" min="2" max="30" style="width:52px"> tandas
    <button class="b s" onclick="promediarM2()">Average M2</button></div>
   <div class="nota">dominant kernels (d100) give identifiability of the 13 categories; mixed programs
    (×3 intensities) give overhead and P_static. Each run → regresion/campanas/.
    <b>average</b> = mean of the last N campaigns' coefficients (cancels session/idle bias; raw data can't
    be pooled across campaigns).</div></div>

  <div class="card"><h2>Instruction mix (% per program)</h2>
   <div class="nota">retired-instruction fraction of each calibration program (last campaign)</div>
   <div id="mixtab" style="margin-top:6px;overflow-x:auto"></div></div>
 </div>
 <div>
  <div class="card"><h2>M2 coefficients — latest campaign</h2>
   <div id="m2meta" class="nota">loading…</div>
   <div id="m2kpi" class="kpi"></div>
   <div id="m2chart"></div>
   <div id="m2tab" style="margin-top:8px"></div></div>
 </div>
</div></section>

<section id="tab-val" class="tab"><div class="cols">
 <div>
  <div class="card"><h2>Validate (held-out benchmarks)</h2>
   <div class="fila">method
    <select id="vmethod">
     <option value="both">both (M1 &amp; M2)</option>
     <option value="bucles">M1 only</option>
     <option value="regresion">M2 only</option>
    </select>
    runs <input type="number" id="vn" value="1" min="1" max="30" style="width:52px"></div>
   <div>__VPROG__</div>
   <div class="fila"><button class="b" onclick="verificar()">Validate</button>
    <button class="b s" onclick="marcar('vprog',true)">all</button>
    <button class="b s" onclick="marcar('vprog',false)">none</button></div>
   <div class="nota">measures session P_idle and predicts with the selected method(s). Error = RMSE / P̄
    (paper metric). Each run → validaciones/</div></div>

  <div class="card"><h2>M1 vs M2 coefficients</h2>
   <div class="nota">per-category energy [nJ]; M1 shown ×scale (effective)</div>
   <div id="cmpchart"></div>
   <div class="lg" id="cmpleg"></div></div>
 </div>
 <div>
  <div class="card"><h2>Latest validation — measured vs predicted</h2>
   <div id="vmeta" class="nota">loading…</div>
   <div id="vkpi" class="kpi"></div>
   <div style="display:flex;gap:28px;flex-wrap:wrap;align-items:flex-start">
    <div style="flex:1 1 0;min-width:240px;max-width:420px"><div class="nota" style="text-align:center">M1</div><div id="vchartM1"></div></div>
    <div style="flex:1 1 0;min-width:240px;max-width:420px"><div class="nota" style="text-align:center">M2</div><div id="vchartM2"></div></div>
   </div>
   <div class="lg" id="vleg" style="flex-wrap:wrap"></div>
   <div id="vtab" style="margin-top:8px"></div></div>
  <div class="card"><h2>Instruction mix (% per program)</h2>
   <div class="nota">retired-instruction share per category for each validation benchmark (from the latest batch).</div>
   <div id="vmixtab" style="margin-top:6px;overflow-x:auto"></div></div>
 </div>
</div></section>

<div id="log"></div>
</main>
<script>
let n=0, activo=false, timer=null;
const $=id=>document.getElementById(id);
const sel=g=>[...document.querySelectorAll(`input[name=${g}]:checked`)].map(e=>e.value);
function marcar(g,v){document.querySelectorAll(`input[name=${g}]`).forEach(e=>e.checked=v)}
function programar(ms){clearTimeout(timer); timer=setTimeout(sondear,ms)}

// pestanas
document.querySelectorAll('.tabbtn').forEach(b=>b.onclick=()=>{
 document.querySelectorAll('.tabbtn').forEach(x=>x.classList.remove('act'));
 document.querySelectorAll('.tab').forEach(x=>x.classList.remove('act'));
 b.classList.add('act'); $('tab-'+b.dataset.t).classList.add('act');
});

async function lanzar(req){
 const r=await fetch('/run',{method:'POST',body:JSON.stringify(req)});
 const j=await r.json();
 if(!j.ok) alert(j.msg); else {n=0;$('log').textContent='';}
 programar(100);
}
function m1(){lanzar({accion:'m1',cats:sel('m1cat'),repeats:+$('m1rep').value,campanas:+$('m1n').value,nobuild:$('m1nb').checked})}
function m1full(){lanzar({accion:'m1full',cats:sel('m1cat'),kb:$('fkb').value,lcref:+$('flc').value})}
function promediar(){lanzar({accion:'promediar',metodo:'bucles',n:+$('prn').value})}
function promediarM2(){lanzar({accion:'promediar',metodo:'regresion',n:+$('prn2').value})}
function overhead(){lanzar({accion:'overhead',pairs:$('ovpairs').checked,dry:$('ovdry').checked})}
function barrido(){lanzar({accion:'barrido',kb:$('fkb').value,lcref:+$('flc').value})}
function testm2(){lanzar({accion:'testm2',duty:$('tmduty').checked})}
function m2(){lanzar({accion:'m2',progs:sel('m2prog'),model:$('m2model').value,campanas:+$('m2n').value,nobuild:$('m2nb').checked,duty:$('m2duty').checked})}
function verificar(){const m=$('vmethod').value;lanzar({accion:'verificar',progs:sel('vprog'),campanas:+$('vn').value,solo:(m==='both')?null:m})}
async function detener(){await fetch('/stop',{method:'POST'})}

// ---- graficas (SVG inline) ----
const CATS=["alu","mul","mulh","div","mem","ctrl","fp_add","fp_mul","fp_fma","fp_div","fp_sqrt","fp_noncomp","fp_conv"];
function esc(s){return String(s).replace(/[<>&]/g,c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]))}
function barH(items){
 if(!items.length) return '<div class="nota">sin datos</div>';
 const max=Math.max(...items.map(i=>Math.abs(i.v)))||1, W=210, rh=17, H=items.length*rh+4;
 let s=`<svg width="100%" viewBox="0 0 330 ${H}" preserveAspectRatio="xMinYMin meet">`;
 items.forEach((it,i)=>{const y=i*rh+2, w=Math.abs(it.v)/max*W, col=it.her?'#c98b3a':'#2d6cdf';
  s+=`<text x="72" y="${y+12}" text-anchor="end">${esc(it.k)}</text>`;
  s+=`<rect x="78" y="${y+3}" width="${w.toFixed(1)}" height="11" rx="2" fill="${col}"/>`;
  s+=`<text x="${(80+w).toFixed(1)}" y="${y+12}" text-anchor="start" style="fill:#dde3ea">${it.v}</text>`;});
 return s+'</svg>';
}
// distinct color per validation program (hue wheel)
const PROGCOL={};
function progColor(p){
 if(PROGCOL[p]) return PROGCOL[p];
 const i=Object.keys(PROGCOL).length; const h=(i*47)%360;
 return PROGCOL[p]=`hsl(${h},70%,58%)`;
}
// one scatter (measured vs predicted); points colored by program, bisector shown
function scatter(pts, refLo, refHi){
 if(!pts||!pts.length) return '<div class="nota">no validation yet</div>';
 const vals=pts.flatMap(p=>[p.x,p.y]).concat(refLo!=null?[refLo,refHi]:[]);
 let lo=Math.min(...vals), hi=Math.max(...vals);
 const pad=(hi-lo)*0.1||0.001; lo-=pad; hi+=pad; const S=280, M=38, P=8;
 const X=v=>M+(v-lo)/(hi-lo)*(S-M-P), Y=v=>S-M-(v-lo)/(hi-lo)*(S-M-P);
 let s=`<svg viewBox="0 0 ${S} ${S}" preserveAspectRatio="xMidYMid meet" style="display:block;width:100%;height:auto;aspect-ratio:1/1">`;
 s+=`<line x1="${X(lo)}" y1="${Y(lo)}" x2="${X(hi)}" y2="${Y(hi)}" stroke="#4a5561" stroke-dasharray="4 3"/>`;
 s+=`<line x1="${M}" y1="${P}" x2="${M}" y2="${S-M}" stroke="#2c3540"/><line x1="${M}" y1="${S-M}" x2="${S-P}" y2="${S-M}" stroke="#2c3540"/>`;
 [lo,(lo+hi)/2,hi].forEach(v=>{s+=`<text x="${M-4}" y="${Y(v)+3}" text-anchor="end">${(v*1e3).toFixed(0)}</text>`;
   s+=`<text x="${X(v)}" y="${S-M+12}" text-anchor="middle">${(v*1e3).toFixed(0)}</text>`;});
 s+=`<text x="${S/2}" y="${S-3}" text-anchor="middle">P measured [mW]</text>`;
 s+=`<text x="11" y="${S/2}" text-anchor="middle" transform="rotate(-90 11 ${S/2})">P predicted [mW]</text>`;
 pts.forEach(p=>{s+=`<circle cx="${X(p.x).toFixed(1)}" cy="${Y(p.y).toFixed(1)}" r="3.2" fill="${p.color}" fill-opacity=".85" stroke="#0d1013" stroke-width=".4"><title>${esc(p.label)}</title></circle>`;});
 return s+'</svg>';
}
function kpi(items){return items.filter(i=>i.v!=null&&i.v!=='').map(i=>`<div><b>${i.v}</b><span>${i.l}</span></div>`).join('')}
// grouped bar chart: two series per category (M1 vs M2)
function barCmp(cats, s1, s2, c1, c2){
 const vals=cats.flatMap(c=>[s1[c]||0,s2[c]||0]); const max=Math.max(...vals,0.1);
 const rh=20, W=200, H=cats.length*rh+6;
 let s=`<svg width="100%" viewBox="0 0 360 ${H}" preserveAspectRatio="xMinYMin meet">`;
 cats.forEach((c,i)=>{const y=i*rh+2;
  const w1=(s1[c]||0)/max*W, w2=(s2[c]||0)/max*W;
  s+=`<text x="76" y="${y+13}" text-anchor="end">${esc(c)}</text>`;
  s+=`<rect x="80" y="${y+2}" width="${w1.toFixed(1)}" height="7" rx="1" fill="${c1}"/>`;
  s+=`<rect x="80" y="${y+10}" width="${w2.toFixed(1)}" height="7" rx="1" fill="${c2}"/>`;
  s+=`<text x="${(82+Math.max(w1,w2)).toFixed(1)}" y="${y+13}" style="fill:#dde3ea">${(s2[c]||0).toFixed(1)}</text>`;});
 return s+'</svg>';
}

// ---- state render ----
function renderCoef(pre, m){
 if(!m||m.error){$(pre+'meta').textContent=m?('error: '+m.error):'no campaign yet';
  $(pre+'kpi').innerHTML='';$(pre+'chart').innerHTML='';$(pre+'tab').innerHTML='';return;}
 $(pre+'meta').innerHTML=`latest: <b>${m.fecha||'?'}</b>` + (m.n?` · n=${m.n} runs`:'');
 const k=[{l:'P_idle [W]',v:m.P_idle_W},{l:'T_idle [°C]',v:m.T_idle_C}];
 if(m.escala!=null)k.push({l:'scale',v:m.escala});
 if(m.fetch_nWb!=null)k.push({l:'fetch [nW/B]',v:m.fetch_nWb});
 if(m.stall_nJ!=null)k.push({l:'stall [nJ/cyc]',v:m.stall_nJ});
 if(m.b0_W!=null)k.push({l:'b0 fit [W]',v:m.b0_W});
 if(m.R2)k.push({l:'R²',v:m.R2}); if(m.cond)k.push({l:'cond',v:(+m.cond).toFixed(0)});
 if(m.RMSE_mW)k.push({l:'RMSE [mW]',v:m.RMSE_mW});
 $(pre+'kpi').innerHTML=kpi(k);
 const her=new Set(m.heredadas||[]);
 // los coef de M2 ya vienen PLEGADOS del archivo (div/mulh/fp_div/fp_sqrt con su
 // energia completa por instruccion); se muestran tal cual, comparables con M1.
 const items=CATS.filter(c=>m.coef[c]!=null).map(c=>({k:c,v:m.coef[c],her:her.has(c)}));
 $(pre+'chart').innerHTML=barH(items);
 let t='<table><tr><th>category</th><th>coef [nJ]</th><th>source</th></tr>';
 items.forEach(it=>t+=`<tr><td>${it.k}${it.her?'<span class="badge">M1</span>':''}</td><td>${it.v}</td><td>${it.her?'<span class="her">inherited</span>':(pre==='m2'?'M2':'M1')}</td></tr>`);
 $(pre+'tab').innerHTML=t+'</table>';
}
function renderMix(mix,el){
 el=el||'mixtab';
 if(!mix||mix.error||!mix.rows){$(el).innerHTML='<div class="nota">'+(mix&&mix.error?mix.error:'no data yet')+'</div>';return;}
 const sh={alu:'alu',mul:'mul',mulh:'mlh',div:'div',mem:'mem',ctrl:'ctl',fp_add:'f+',fp_mul:'f*',fp_fma:'ffm',fp_div:'f/',fp_sqrt:'fsq',fp_noncomp:'fnc',fp_conv:'fcv'};
 let t='<table><tr><th>program</th>'+mix.cats.map(c=>`<th>${sh[c]||c}</th>`).join('')+'</tr>';
 mix.rows.forEach(r=>{t+=`<tr><td>${esc(r.prog)}</td>`+mix.cats.map(c=>{
   const v=r[c]||0; const bg=v>=40?'background:#2d6cdf33':(v>0?'background:#2d6cdf11':'');
   return `<td style="${bg}">${v||''}</td>`;}).join('')+'</tr>';});
 $(el).innerHTML=t+'</table>';
}
function renderCmp(e){
 const m1=e.metodos.bucles, m2=e.metodos.regresion;
 if(!m1||!m2||!m1.coef||!m2.coef){$('cmpchart').innerHTML='<div class="nota">need M1 and M2 coefficients</div>';$('cmpleg').innerHTML='';return;}
 const S=m1.escala||1;
 // M2 ya viene PLEGADO (energia completa por instruccion en las multi-ciclo), asi
 // que se compara directo contra M1 x escala. Ambos son energia por instruccion.
 const s1={}, s2={};
 CATS.forEach(c=>{if(m1.coef[c]!=null)s1[c]=m1.coef[c]*S; if(m2.coef[c]!=null)s2[c]=m2.coef[c];});
 const cats=CATS.filter(c=>s1[c]!=null||s2[c]!=null);
 $('cmpchart').innerHTML=barCmp(cats,s1,s2,'#2d6cdf','#c98b3a');
 $('cmpleg').innerHTML='<span><span class="sw" style="background:#2d6cdf"></span>M1 ×scale</span>'
  +'<span><span class="sw" style="background:#c98b3a"></span>M2 (plegado)</span>';
}
function renderValid(v){
 const clear=()=>{$('vkpi').innerHTML='';$('vchartM1').innerHTML='';$('vchartM2').innerHTML='';$('vleg').innerHTML='';$('vtab').innerHTML='';};
 if(!v||v.error||!v.metodos){$('vmeta').textContent=v&&v.error?('error: '+v.error):'no validation yet';clear();return;}
 $('vmeta').innerHTML=`session: <b>${v.ts||''}</b>`+(v.nruns>1?` · ${v.nruns} runs (all points shown)`:'');
 const nm={bucles:'M1',regresion:'M2'};
 const k=[];
 // shared measured/predicted range so both plots use the same axes
 let allv=[];
 for(const met of ['bucles','regresion']){const d=v.metodos[met]; if(!d)continue;
  d.rows.forEach(r=>{allv.push(r.med,r.pred);});}
 const lo=Math.min(...allv), hi=Math.max(...allv);
 for(const [met,el] of [['bucles','vchartM1'],['regresion','vchartM2']]){
  const d=v.metodos[met];
  if(!d){$(el).innerHTML='<div class="nota">n/a</div>';continue;}
  k.push({l:`${nm[met]} error% (paper)`,v:d.err_pct}); k.push({l:`${nm[met]} RMSE [mW]`,v:d.rmse_mW});
  const pts=d.rows.map(r=>({x:r.med,y:r.pred,color:progColor(r.prog),label:`${r.prog}: meas ${(r.med*1e3).toFixed(1)} / pred ${(r.pred*1e3).toFixed(1)} mW`}));
  $(el).innerHTML=scatter(pts,lo,hi);
 }
 $('vkpi').innerHTML=kpi(k);
 // per-program color legend (unique programs)
 const b=v.metodos.bucles, r=v.metodos.regresion, base=(b||r);
 const progs=[...new Set(base.rows.map(x=>x.prog))];
 $('vleg').innerHTML=progs.map(p=>`<span><span class="sw" style="background:${progColor(p)}"></span>${esc(p)}</span>`).join('');
 // table: per program, MEAN error across runs (if runs>1)
 const agg={};
 if(b) b.rows.forEach(x=>{(agg[x.prog]=agg[x.prog]||{}).m1=(agg[x.prog].m1||[]).concat(parseFloat(x.err)||0);});
 if(r) r.rows.forEach(x=>{(agg[x.prog]=agg[x.prog]||{}).m2=(agg[x.prog].m2||[]).concat(parseFloat(x.err)||0);});
 const mean=a=>a&&a.length?(a.reduce((s,y)=>s+y,0)/a.length):null;
 let t='<table><tr><th>benchmark</th>'+(b?'<th>M1 err%</th>':'')+(r?'<th>M2 err%</th>':'')+'</tr>';
 progs.forEach(p=>{const a=agg[p]||{};t+=`<tr><td><span class="sw" style="background:${progColor(p)}"></span>${esc(p)}</td>`+
  (b?`<td>${mean(a.m1)!=null?mean(a.m1).toFixed(2):''}</td>`:'')+(r?`<td>${mean(a.m2)!=null?mean(a.m2).toFixed(2):''}</td>`:'')+`</tr>`;});
 $('vtab').innerHTML=t+'</table>';
}
let ultEstado=0;
async function refrescarEstado(force){
 if(!force && Date.now()-ultEstado<4000) return; ultEstado=Date.now();
 const e=await (await fetch('/estado')).json();
 renderCoef('m1', e.metodos.bucles); renderCoef('m2', e.metodos.regresion);
 renderMix(e.mix); renderCmp(e); renderValid(e.validacion); renderMix(e.vmix,'vmixtab');
}
async function sondear(){
 const j=await (await fetch('/log?desde='+n)).json();
 if(j.lineas.length){const L=$('log');L.textContent+=j.lineas.join('\n')+'\n';n=j.n;L.scrollTop=L.scrollHeight;}
 const antes=activo; activo=j.corriendo;
 $('dot').className=activo?'on':''; $('btnstop').disabled=!activo;
 $('quehace').textContent=activo?j.nombre+' ('+j.min+' min)':'idle';
 programar(activo?700:2500);
 if(antes&&!activo) refrescarEstado(true);   // just finished: refresh data
 else if(!activo) refrescarEstado(false);
}
refrescarEstado(true); sondear();
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/":
            b = pagina().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
        elif u.path == "/log":
            desde = 0
            for kv in u.query.split("&"):
                if kv.startswith("desde="):
                    desde = int(kv[6:])
            mins = f"{(time.time()-JOB.inicio)/60:.1f}" if JOB.inicio else "0"
            self._json({"lineas": JOB.log[desde:], "n": len(JOB.log),
                        "corriendo": bool(JOB.corriendo_o_encolado()),
                        "nombre": JOB.nombre, "min": mins})
        elif u.path == "/estado":
            self._json(estado())
        else:
            self._json({"err": "no encontrado"}, 404)

    def do_POST(self):
        cuerpo = self.rfile.read(int(self.headers.get("Content-Length", 0)) or 0)
        if self.path == "/run":
            try:
                nombre, cmd = cmd_de(json.loads(cuerpo or b"{}"))
            except (ValueError, json.JSONDecodeError) as e:
                return self._json({"ok": False, "msg": str(e)})
            ok, msg = JOB.lanzar(nombre, cmd)
            self._json({"ok": ok, "msg": msg})
        elif self.path == "/stop":
            self._json({"ok": JOB.detener()})
        else:
            self._json({"err": "no encontrado"}, 404)


class Servidor(ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        # los navegadores (sobre todo el del telefono al apagar pantalla)
        # cortan conexiones keep-alive de golpe: no es un error del banco
        import sys as _sys
        e = _sys.exc_info()[1]
        if isinstance(e, (ConnectionResetError, BrokenPipeError, TimeoutError)):
            return
        super().handle_error(request, client_address)


if __name__ == "__main__":
    lan = "--lan" in sys.argv
    if "--puerto" in sys.argv:
        PORT = int(sys.argv[sys.argv.index("--puerto") + 1])
    srv = Servidor(("0.0.0.0" if lan else "127.0.0.1", PORT), H)
    print(f"GUI del banco: http://localhost:{PORT}   (Ctrl-C para salir)")
    if lan:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))          # no manda nada; solo resuelve la IP local
            print(f"  desde el telefono (misma WiFi): http://{s.getsockname()[0]}:{PORT}")
        finally:
            s.close()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        JOB.detener()
