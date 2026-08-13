#!/usr/bin/env python3
"""Validation with BOTH methods on the SAME runs. Loads each .elf, runs it once
over JTAG, retrieves the measured P_avg from the Sheet, and predicts power with
BOTH coefficient sets (loops and regression) using a single session baseline.
Since the counters are identical and only the coeficientes differ, the measured
power is the same for both methods and the comparison isolates the model
difference. Each batch produces two parallel CSVs (validation_loops_*.csv and
validation_regression_*.csv) plus rows in the Sheet's 'verificacion' tab.

Usage:
    python3 verify.py mont64 ud jfdctint modexp bigdiv ratapprox
    python3 verify.py --repeats 3 --pidle measure <kernels...>
"""
import argparse
import csv
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "comun"))
import sheet      # noqa: E402
import modelo     # noqa: E402
import jtag       # noqa: E402

# La validacion corre idle_check (~40 s) y benchmarks (~10-100 s): fuerza un
# timeout amplio y varios reintentos aunque el entorno traiga un GDB_TIMEOUT/
# RETRIES chico (p.ej. el del smoke-test: GDB_TIMEOUT=15), que abortaria el idle.
if jtag.GDB_TIMEOUT < 120:
    jtag.GDB_TIMEOUT = 480
if jtag.RETRIES < 3:
    jtag.RETRIES = 5

METHODS = ("bucles", "regresion")

# SHORT idle for the session baseline (~5 s window): 17 reps x 0.3 s. Enough to
# detect a drift of >2 mW (short-window noise: ~0.5 mW).
IDLE_CHECK_ELF = os.path.join(HERE, "bucles", "elf", "idle_check.elf")
VERIF_CSV = os.path.join(HERE, "verificacion.csv")


def build_idle_check():
    # rebuild siempre: idle.S pudo cambiar (reps/ticks)
    riscv = os.environ.get("RISCV",
                           "/home/jjsotoch/pulp/toolchain/v1.0.16-pulp-riscv-gcc-ubuntu-18")
    subprocess.run(
        [f"{riscv}/bin/riscv32-unknown-elf-gcc",
         "-nostdlib", "-nostartfiles", "-static", "-Os", "-g", "-mabi=ilp32",
         "-Wl,-T,link.ld", "-Wl,--build-id=none", "-I.", "-march=rv32imc",
         "-DIDLE_REPS=1", "-o", IDLE_CHECK_ELF, "idle.S"],
        cwd=os.path.join(HERE, "bucles", "fuentes"), check=True)


def find_elf(prog):
    for cand in (os.path.join(HERE, "benchmarks", f"{prog}.elf"), prog):
        if os.path.exists(cand):
            return cand
    raise FileNotFoundError(f"{prog}.elf is not in benchmarks/ (nor a valid path)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pidle", default="measure",
                    help="session baseline used for BOTH methods: 'measure' "
                         "(default, measures idle_check on site) or a number in W. "
                         "The coeficientes are deltas, so only the baseline changes "
                         "between sessions; it is measured fresh, not reused from "
                         "characterization.")
    ap.add_argument("--repeats", type=int, default=1,
                    help="runs per load; P_med = average of the N windows "
                         "(lowers bench noise ~sqrt(N))")
    ap.add_argument("--solo", default=None, choices=["bucles", "regresion"],
                    help="correr SOLO un metodo (p.ej. 'bucles' si aun no hiciste M2)")
    ap.add_argument("programas", nargs="+")
    args = ap.parse_args()

    # load BOTH coefficient sets; each file's own P_idle is ignored (a single
    # measured session baseline is used for both, so the measured power matches).
    pedidos = [args.solo] if args.solo else list(METHODS)
    coefs = {}
    mets = []
    for met in pedidos:
        cp = os.path.join(HERE, met, "coeficientes.csv")
        if not os.path.exists(cp):
            print(f"  (aviso: no hay coef de '{met}' en {cp}; lo salto)")
            continue
        _, coefs[met] = modelo.cargar_coeficientes(cp)
        mets.append(met)
    if not mets:
        sys.exit("no hay coeficientes de ningun metodo pedido (corre M1/M2 primero)")
    print("=== Validation (both methods on the same runs) ===")

    header = (["fecha", "method", "programa", "T_s", "P_med_W", "P_pred_W",
               "err_pct", "temp_C"] + modelo.COLS_CONTADORES)
    new = not os.path.exists(VERIF_CSV)
    fcsv = open(VERIF_CSV, "a", newline="")
    wr = csv.writer(fcsv)
    if new:
        wr.writerow(header)

    # one batch file per method, same timestamp -> parallel files (same measured)
    d_tandas = os.path.join(HERE, "validaciones")
    os.makedirs(d_tandas, exist_ok=True)
    ts0 = time.strftime("%Y%m%d_%H%M%S")
    batch = {}
    for met in mets:
        path = os.path.join(d_tandas, f"validacion_{met}_medir_{ts0}.csv")
        fh = open(path, "w", newline="")
        w = csv.writer(fh)
        w.writerow(header)
        batch[met] = [fh, w, path]

    inbox = sheet.Inbox()

    # single session baseline (used for both methods)
    if args.pidle == "measure":
        build_idle_check()
        print("  measuring the session P_idle (idle_check, ~40 s)...")
        for intento in range(1, 4):
            # drena ventanas pendientes ANTES de correr: sin esto get_pavg agarra
            # una ventana RANCIA de la corrida anterior (midio "otro programa").
            # NO se pasa esperado_s: la ventana del idle reporta ~0 s de duracion
            # en el sheet (limitacion de la medicion en wfi) y el guard la botaria.
            inbox.reset()
            jtag.run_one(IDLE_CHECK_ELF)
            try:
                P_idle = inbox.get_pavg()
                break
            except TimeoutError:
                if intento == 3:
                    raise
                print(f"    idle: window without P_avg; RETRYING ({intento}/3)")
        print(f"  session P_idle = {P_idle:.4f} W\n")
    else:
        P_idle = float(args.pidle)
        print(f"  P_idle = {P_idle:.4f} W (set from the command line)\n")

    print(f"{'programa':12s} {'P_med[W]':>9s} | "
          f"{'loops[W]':>9s} {'err%':>7s} | {'regr[W]':>9s} {'err%':>7s}   T[s]")
    errs = {m: [] for m in mets}
    for prog in args.programas:
        elf = find_elf(prog)
        print(f"==> running {prog} over JTAG...")
        words, pbar = jtag.run_medido(elf, inbox.get_pavg)
        if args.repeats > 1:
            # execution is deterministic (same counters); only POWER is averaged
            pes = [pbar]
            for rep in range(2, args.repeats + 1):
                _, p2 = jtag.run_medido(elf, inbox.get_pavg)
                pes.append(p2)
                print(f"    rep {rep}/{args.repeats}: P = {p2:.4f} W")
            pbar = sum(pes) / len(pes)
            disp = (max(pes) - min(pes)) * 1e3
            print(f"    average of {args.repeats} reps: {pbar:.4f} W "
                  f"(range {disp:.2f} mW)")
        w = [modelo.to_int(x) for x in words]
        T = ((w[29] - w[28]) & modelo.MASK32) / modelo.F_CLK
        cont = modelo.contadores(w)
        tC = jtag.ultima_temp_cC                       # die temperature (XADC)
        tstr = f"{tC/100:.2f}" if tC is not None else ""
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"{prog:12s} {pbar:9.4f} |"
        for met in mets:
            P_din = modelo.potencia_dinamica(w, coefs[met])   # the model (dynamic)
            P_pred = P_idle + P_din                          # single session baseline
            err = 100 * (P_pred - pbar) / pbar
            errs[met].append(abs(err))
            sheet.subir("verificacion", method=met, programa=prog, T_s=f"{T:.3f}",
                        P_med_W=f"{pbar:.6f}", P_pred_W=f"{P_pred:.6f}",
                        err_pct=f"{err:.4f}", temp_C=tstr,
                        **{k: cont[k] for k in modelo.COLS_CONTADORES})
            row = ([ts, met, prog, f"{T:.3f}", f"{pbar:.6f}", f"{P_pred:.6f}",
                    f"{err:.4f}", tstr] + [cont[k] for k in modelo.COLS_CONTADORES])
            wr.writerow(row)
            batch[met][1].writerow(row)
            line += f" {P_pred:9.4f} {err:7.2f} |"
        fcsv.flush()
        for met in mets:
            batch[met][0].flush()
        print(line + f"  {T:5.1f}  {tstr}C")

    fcsv.close()
    for met in mets:
        batch[met][0].close()
    print()
    for met in mets:
        e = errs[met]
        if e:
            print(f"  {met:11s}: mean |err| {sum(e)/len(e):.2f}%   max {max(e):.2f}%")
    print(f"\nSaved to {VERIF_CSV} and the Sheet's 'verificacion' tab.")
    for met in mets:
        print(f"  {met}: {os.path.relpath(batch[met][2], HERE)}")


if __name__ == "__main__":
    main()
