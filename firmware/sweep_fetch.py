#!/usr/bin/env python3
"""Barrido de FOOTPRINT_KB del bucle ctrl para CALIBRAR e_fetch (termino de Tiwari).

Requiere el bitstream con el contador n_fetch ya sintetizado. Por cada footprint:
compila ctrl.elf con ese FOOTPRINT_KB, lo mide (idle + ctrl en la misma sesion),
y lee del CSV el coeficiente de ctrl y n_fetch/n_ctrl. Al final ajusta

    e_ctrl(footprint) = e_flush + e_fetch * (n_fetch / n_ctrl)

por minimos cuadrados: la PENDIENTE es e_fetch [J por cruce de fetch] y el
INTERCEPTO es e_flush [J por ctrl, sin fetch]. Reporta R^2 (si es alto, el modelo
lineal de Tiwari aguanta; si no, hay que mover FETCH_BLK_LSB en el RTL y re-sintetizar).

Uso:
    python3 barrido_fetch.py
    python3 barrido_fetch.py --kb 4,8,16,32,64,128,256 --lc-ref 20000
"""
import argparse
import csv
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FUENTES = os.path.join(HERE, "loops", "fuentes")
ELF = os.path.join(HERE, "loops", "elf", "ctrl.elf")
DATOS = os.path.join(HERE, "loops", "datos.csv")
CHARACTERIZE = os.path.join(HERE, "characterize.py")

CATS = ["n_alu", "n_mul", "n_mulh", "n_div", "n_mem", "n_ctrl", "n_fp_add",
        "n_fp_mul", "n_fp_fma", "n_fp_div", "n_fp_sqrt", "n_fp_noncomp", "n_fp_conv"]


def build(kb, lc):
    subprocess.run(["make", "-B", "../elf/ctrl.elf",
                    f"FOOTPRINT_KB={kb}", f"LOOP_COUNT={lc}"],
                   cwd=FUENTES, check=True)


def medir():
    subprocess.run([sys.executable, CHARACTERIZE, "loops", "ctrl", "--no-build"],
                   cwd=HERE, check=True)


def ultimo_punto():
    """Ultima corrida ctrl del datos.csv + su idle de sesion -> dict con el punto."""
    rows = list(csv.DictReader(open(DATOS)))
    ci = [i for i, r in enumerate(rows) if r["categoria"] == "ctrl"]
    if not ci:
        raise RuntimeError("no hay corridas ctrl en datos.csv")
    r = rows[ci[-1]]
    ri = None
    for j in range(ci[-1] - 1, -1, -1):
        if rows[j]["categoria"] == "idle":
            ri = rows[j]
            break
    if ri is None:
        raise RuntimeError("no encontre idle antes del ultimo ctrl")
    if "n_fetch" not in r:
        raise RuntimeError("el CSV no tiene columna n_fetch: falta sintetizar el "
                           "contador o reconstruir firmware")
    Pc, Pi = float(r["P_med_W"]), float(ri["P_med_W"])
    T = float(r["T_s"])
    nc = int(r["n_ctrl"]); nf = int(r["n_fetch"]); mc = int(r["mcycle"])
    ntot = sum(int(r[k]) for k in CATS)
    return {
        "coef_nJ": (Pc - Pi) * T / nc * 1e9,     # e_ctrl medido [nJ/ctrl]
        "rng":     nf,                             # rango fetch = footprint [bytes]
        "cic_ctrl": mc / nc,
        "dP_mW":   (Pc - Pi) * 1e3,
        "ctrl_pct": 100 * nc / ntot,
        "T_s":     T,
        "n_fetch": nf, "n_ctrl": nc,
    }


def ajuste(xs, ys):
    """Minimos cuadrados y = a + b x. Devuelve (a, b, R2)."""
    n = len(xs)
    mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx if sxx else 0.0
    a = my - b * mx
    sst = sum((y - my) ** 2 for y in ys)
    ssr = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - ssr / sst if sst else 1.0
    return a, b, r2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kb", default="4,8,16,24,32,48,64,96,128,192,256",
                    help="footprints en KB, separados por coma")
    ap.add_argument("--lc-ref", type=int, default=20000,
                    help="LOOP_COUNT de referencia @16KB (se escala ~1/KB para "
                         "igualar la ventana; el coef es indep. de la ventana)")
    args = ap.parse_args()
    kbs = [int(x) for x in args.kb.split(",")]

    if not os.path.exists(CHARACTERIZE):
        sys.exit(f"no encuentro {CHARACTERIZE}")

    # asegura idle.elf al dia (el barrido corre caracterizar con --no-build)
    subprocess.run(["make", "-B", "../elf/idle.elf"], cwd=FUENTES, check=True)

    pts = []
    for kb in kbs:
        lc = max(500, round(args.lc_ref * 16 / kb))
        print(f"\n===== FOOTPRINT_KB={kb}  LOOP_COUNT={lc} =====")
        build(kb, lc)
        medir()
        p = ultimo_punto()
        p["kb"] = kb
        pts.append(p)
        print(f"  -> coef={p['coef_nJ']:.2f} nJ  rango={p['rng']}  "
              f"cic/ctrl={p['cic_ctrl']:.2f}  ctrl%={p['ctrl_pct']:.1f}")

    # tabla
    print("\n" + "=" * 64)
    print(f"{'KB':>4} {'coef[nJ]':>9} {'rango':>9} {'cic/ctrl':>8} {'dP[mW]':>7} {'ctrl%':>6}")
    for p in pts:
        print(f"{p['kb']:>4} {p['coef_nJ']:9.2f} {p['rng']:9d} "
              f"{p['cic_ctrl']:8.2f} {p['dP_mW']:7.1f} {p['ctrl_pct']:5.1f}")

    # ajuste e_ctrl vs (n_fetch/n_ctrl)
    xs = [p["rng"] for p in pts]
    ys = [p["coef_nJ"] for p in pts]
    a, b, r2 = ajuste(xs, ys)
    print("\n--- ajuste  e_ctrl = e_flush + e_fetch * (n_fetch/n_ctrl) ---")
    print(f"  e_flush (intercepto) = {a:.3f} nJ/ctrl   (ctrl sin fetch)")
    print(f"  e_fetch (pendiente)  = {b*1e3:.4f} pJ por byte de footprint")
    print(f"  R^2 = {r2:.4f}   {'(lineal OK)' if r2 > 0.9 else '(pobre -> mover FETCH_BLK_LSB y re-sintetizar)'}")

    out = os.path.join(HERE, "sweep_fetch.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kb", "coef_nJ", "rango_bytes", "cic_ctrl",
                    "dP_mW", "ctrl_pct", "T_s", "n_fetch", "n_ctrl"])
        for p in pts:
            w.writerow([p["kb"], f"{p['coef_nJ']:.4f}", str(p["rng"]),
                        f"{p['cic_ctrl']:.3f}", f"{p['dP_mW']:.2f}",
                        f"{p['ctrl_pct']:.2f}", f"{p['T_s']:.3f}",
                        p["n_fetch"], p["n_ctrl"]])
    print(f"\nGuardado: {out}")


if __name__ == "__main__":
    main()
