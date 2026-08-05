#!/usr/bin/env python3
"""Thermal idle sweep -> fits P_idle(T) (thesis).

Runs a SHORT idle.elf (~15 s) in a loop while the board HEATS UP, logging for
each measurement the die temperature (XADC, via jtag) and P_idle (ESP32). At the
end it fits the line P_idle(T) = a + b*T by least squares. Since leakage rises with
temperature, b > 0; that line corrects the thermal drift of the floor.

IMPORTANT: start with the board COLD (just powered on after cooling down) to get a
temperature sweep. If the board is already at equilibrium (~39 C) all points fall
together and it cannot be fitted.

Usage:
    python3 thermal_sweep.py --n 40     # 40 measurements (~13 min) from a cold board
    python3 thermal_sweep.py --fit      # only re-fit the already-taken CSV
"""
import argparse
import csv
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "common"))
import jtag    # noqa: E402
import sheet   # noqa: E402

FUENTES = os.path.join(HERE, "regression", "sources")
ELF = os.path.join(HERE, "regression", "elf", "idle_sweep.elf")
CSV = os.path.join(HERE, "pidle_temp.csv")
FIT_CSV = os.path.join(HERE, "pidle_fit.csv")
RISCV = os.environ.get("RISCV", "/home/jjsotoch/pulp/toolchain/v1.0.16-pulp-riscv-gcc-ubuntu-18")
CC = f"{RISCV}/bin/riscv32-unknown-elf-gcc"


def build_idle_corto():
    """~15 s idle (IDLE_REPS=50). idle.S is self-contained (its own _start)."""
    subprocess.run(
        [CC, "-nostdlib", "-nostartfiles", "-static", "-Os", "-g", "-mabi=ilp32",
         "-Wl,-T,link.ld", "-Wl,--build-id=none", "-I.", "-march=rv32imc",
         "-DIDLE_REPS=50", "-o", ELF, "idle.S"],
        cwd=FUENTES, check=True)


def esperar_inbox(seen, timeout=45):
    t0 = time.time()
    while time.time() - t0 < timeout:
        filas = sheet.leer("inbox")
        if len(filas) > seen:
            return filas[-1], len(filas)
        time.sleep(3)
    raise TimeoutError("timeout waiting for ESP32 P_idle")


def fit(csvpath):
    T, P = [], []
    with open(csvpath) as f:
        for r in csv.DictReader(f):
            if r["temp_C"] and r["P_idle_W"]:
                T.append(float(r["temp_C"]))
                P.append(float(r["P_idle_W"]))
    T, P = np.array(T), np.array(P)
    if len(T) < 3:
        print("too few points to fit (>=3)")
        return
    A = np.vstack([np.ones_like(T), T]).T
    (a, b), *_ = np.linalg.lstsq(A, P, rcond=None)
    # drop transients (e.g. the 1st unsettled window, which falls well below the
    # line): points with residual > 3 sigma. A single outlier ruins the slope
    # and the R2.
    resid = P - (a + b * T)
    keep = np.abs(resid) <= 3 * resid.std()
    n_drop = int((~keep).sum())
    if n_drop and keep.sum() >= 3:
        T, P = T[keep], P[keep]
        A = np.vstack([np.ones_like(T), T]).T
        (a, b), *_ = np.linalg.lstsq(A, P, rcond=None)
        print(f"  (dropped {n_drop} point(s) beyond 3 sigma: transients)")
    spread = T.max() - T.min()
    pred = a + b * T
    ss_tot = ((P - P.mean()) ** 2).sum()
    r2 = 1 - ((P - pred) ** 2).sum() / ss_tot if ss_tot > 0 else float("nan")
    print(f"\n=== P_idle(T) FIT ===  (n={len(T)})")
    print(f"  P_idle(T) = {a:.4f} W + {b*1e3:.3f} mW/C * (T - 0)")
    print(f"  T sweep   : {T.min():.1f} .. {T.max():.1f} C   ({spread:.1f} C)")
    print(f"  P_idle    : {P.min():.4f} .. {P.max():.4f} W   ({(P.max()-P.min())*1e3:.1f} mW)")
    print(f"  slope     : {b*1e3:.2f} mW/C   R2={r2:.4f}")
    if spread < 3:
        print("  [WARNING] sweep < 3 C: force a wider range (fan / warm air ONLY on the FPGA).")

    # store the slope for verify.py's temperature correction:
    # P_idle(T) = P_idle_ref + b*(T - T_ref). Only 'b' is transferable across
    # sessions; the anchor (P_idle_ref, T_ref) is set by each characterization.
    with open(FIT_CSV, "w", newline="") as fd:
        w = csv.writer(fd)
        w.writerow([f"# P_idle(T)=a+b*T fit of the sweep {time.strftime('%Y-%m-%d %H:%M')}."
                    f" spread={spread:.1f}C, R2={r2:.4f}, n={len(T)}."])
        w.writerow(["parametro", "valor", "unidad"])
        w.writerow(["a", f"{a:.6f}", "W"])
        w.writerow(["b_W_per_C", f"{b:.8e}", "W/C"])
        w.writerow(["r2", f"{r2:.4f}", ""])
    print(f"  slope stored in {os.path.basename(FIT_CSV)} (used by verify.py)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40, help="number of idle measurements")
    ap.add_argument("--fit", action="store_true", help="only re-fit the existing CSV")
    args = ap.parse_args()

    if args.fit:
        fit(CSV)
        return

    build_idle_corto()
    # each run starts FRESH: archive a previous CSV so P_idle baselines from
    # different sessions are not mixed (inter-session drift ruins the fit).
    if os.path.exists(CSV):
        bak = CSV.replace(".csv", time.strftime("_%Y%m%d_%H%M.csv.bak"))
        os.rename(CSV, bak)
        print(f"(previous run archived in {os.path.basename(bak)})")
    seen = len(sheet.leer("inbox"))
    print("Thermal sweep: start with the board COLD. Idle ~15 s per measurement.\n")
    with open(CSV, "w", newline="") as fd:
        wr = csv.writer(fd)
        wr.writerow(["hora", "temp_C", "P_idle_W"])
        try:
            i = 1
            while i <= args.n:
                try:
                    jtag.run_one(ELF)
                    tC = jtag.ultima_temp_cC
                    fila, seen = esperar_inbox(seen)
                except TimeoutError:
                    # lost row (WiFi/Sheet hiccup): RETRY the measurement instead
                    # of aborting the sweep (with 60 measurements some hiccup happens).
                    print(f"  [{i:2d}/{args.n}]  window without ESP32 P_avg; retrying the measurement")
                    seen = sheet.n_filas("inbox")
                    continue
                P = float(str(fila["p_avg"]).replace(",", "."))
                t = f"{tC/100:.2f}" if tC is not None else ""
                wr.writerow([time.strftime("%H:%M:%S"), t, f"{P:.6f}"])
                fd.flush()
                print(f"  [{i:2d}/{args.n}]  T = {t} C   P_idle = {P:.4f} W")
                i += 1
        except KeyboardInterrupt:
            # manual stop (e.g. already enough range): fit with what was collected
            print(f"\n[manual stop after {i-1} measurements] fitting with what was collected.")
    fit(CSV)


if __name__ == "__main__":
    main()
