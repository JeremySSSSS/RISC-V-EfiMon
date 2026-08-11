#!/usr/bin/env python3
"""Validation with BOTH methods on the SAME runs. Loads each .elf, runs it once
over JTAG, retrieves the measured P_avg from the Sheet, and predicts power with
BOTH coefficient sets (loops and regression) using a single session baseline.
Since the counters are identical and only the coefficients differ, the measured
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
sys.path.insert(0, os.path.join(HERE, "common"))
import sheet      # noqa: E402
import model     # noqa: E402
import jtag       # noqa: E402

METHODS = ("loops", "regression")

# SHORT idle for the session baseline (~5 s window): 17 reps x 0.3 s. Enough to
# detect a drift of >2 mW (short-window noise: ~0.5 mW).
IDLE_CHECK_ELF = os.path.join(HERE, "loops", "elf", "idle_check.elf")
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
        cwd=os.path.join(HERE, "loops", "sources"), check=True)


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
                         "The coefficients are deltas, so only the baseline changes "
                         "between sessions; it is measured fresh, not reused from "
                         "characterization.")
    ap.add_argument("--repeats", type=int, default=1,
                    help="runs per load; P_med = average of the N windows "
                         "(lowers bench noise ~sqrt(N))")
    ap.add_argument("--solo", default=None, choices=["loops", "regression"],
                    help="run ONLY one method (e.g. loops if no M2 yet)")
    ap.add_argument("programas", nargs="+")
    args = ap.parse_args()

    # load BOTH coefficient sets; each file's own P_idle is ignored (a single
    # measured session baseline is used for both, so the measured power matches).
    pedidos = [args.solo] if args.solo else list(METHODS)
    coefs = {}
    mets = []
    for met in pedidos:
        cp = os.path.join(HERE, met, "coefficients.csv")
        if not os.path.exists(cp):
            print(f"  (warn: no coef for '{met}' at {cp}; skipping)")
            continue
        _, coefs[met] = model.cargar_coefficients(cp)
        mets.append(met)
    if not mets:
        sys.exit("no coefficients for any requested method (run M1/M2 first)")
    print("=== Validation (both methods on the same runs) ===")

    header = (["fecha", "method", "programa", "T_s", "P_med_W", "P_pred_W",
               "err_pct", "temp_C"] + model.COLS_CONTADORES)
    new = not os.path.exists(VERIF_CSV)
    fcsv = open(VERIF_CSV, "a", newline="")
    wr = csv.writer(fcsv)
    if new:
        wr.writerow(header)

    # one batch file per method, same timestamp -> parallel files (same measured)
    d_tandas = os.path.join(HERE, "validations")
    os.makedirs(d_tandas, exist_ok=True)
    ts0 = time.strftime("%Y%m%d_%H%M%S")
    batch = {}
    for met in mets:
        path = os.path.join(d_tandas, f"validation_{met}_measure_{ts0}.csv")
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
        w = [model.to_int(x) for x in words]
        T = ((w[29] - w[28]) & model.MASK32) / model.F_CLK
        cont = model.contadores(w)
        tC = jtag.ultima_temp_cC                       # die temperature (XADC)
        tstr = f"{tC/100:.2f}" if tC is not None else ""
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"{prog:12s} {pbar:9.4f} |"
        for met in mets:
            P_din = model.potencia_dinamica(w, coefs[met])   # the model (dynamic)
            P_pred = P_idle + P_din                          # single session baseline
            err = 100 * (P_pred - pbar) / pbar
            errs[met].append(abs(err))
            sheet.subir("verificacion", method=met, programa=prog, T_s=f"{T:.3f}",
                        P_med_W=f"{pbar:.6f}", P_pred_W=f"{P_pred:.6f}",
                        err_pct=f"{err:.4f}", temp_C=tstr,
                        **{k: cont[k] for k in model.COLS_CONTADORES})
            row = ([ts, met, prog, f"{T:.3f}", f"{pbar:.6f}", f"{P_pred:.6f}",
                    f"{err:.4f}", tstr] + [cont[k] for k in model.COLS_CONTADORES])
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
