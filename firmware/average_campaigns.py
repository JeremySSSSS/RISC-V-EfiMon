#!/usr/bin/env python3
"""Promedia los coeficientes de las ultimas N tandas (respaldos con timestamp en
<metodo>/campanas/) y los escribe en <metodo>/coeficientes.csv.

Las "tandas" (campanas) corren la campana entera varias veces y cada una
sobreescribe el coef (la ultima queda); este script toma las N mas recientes y
promedia parametro por parametro -> cancela el sesgo sesion-a-sesion (idle,
termico) que una sola campana no puede quitar.

M1 (bucles): promedia los coef de bucles dominados; preserva una fila 'fetch'
existente (del barrido). M2 (regresion): promedia los coef del ajuste NNLS de
cada campana (los coef diferenciales son deltas comparables entre campanas, asi
que promediarlos es correcto; NO se pueden mezclar los DATOS crudos porque cada
campana tiene su propio idle). Orden M1: tandas -> promediar -> barrido.

Uso:
    python3 promediar_tandas.py                       # M1, 3 ultimas
    python3 promediar_tandas.py --n 5
    python3 promediar_tandas.py --metodo regresion --n 10   # M2
"""
import argparse
import csv
import glob
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def load(f):
    c = {}
    for r in csv.reader(open(f)):
        if r and r[0] not in ("parametro", "") and not r[0].startswith("#"):
            try:
                c[r[0]] = (float(r[1]), r[2] if len(r) > 2 else "")
            except ValueError:
                pass
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3,
                    help="cuantas tandas recientes promediar (default 3)")
    ap.add_argument("--metodo", default="bucles", choices=["bucles", "regresion"],
                    help="que campana promediar (default bucles = M1)")
    args = ap.parse_args()

    campanas = os.path.join(HERE, args.metodo, "campanas")
    COEF = os.path.join(HERE, args.metodo, "coeficientes.csv")
    es_m1 = args.metodo == "bucles"

    files = sorted(glob.glob(os.path.join(campanas, "*.csv")),
                   key=os.path.getmtime)[-args.n:]
    if not files:
        raise SystemExit(f"no hay respaldos en {campanas} (corre {args.metodo} con tandas)")

    cs = [load(f) for f in files]
    keys = []
    for c in cs:
        for k in c:
            if k not in keys:
                keys.append(k)

    # M1: preserva un 'fetch' que ya estuviera en coeficientes.csv (del barrido)
    fetch_prev = None
    if es_m1 and os.path.exists(COEF):
        prev = load(COEF)
        if "fetch" in prev and "fetch" not in keys:
            fetch_prev = prev["fetch"]

    avg = {}
    for k in keys:
        vals = [c[k][0] for c in cs if k in c]
        unit = next((c[k][1] for c in cs if k in c), "")
        avg[k] = (sum(vals) / len(vals), unit, len(vals))
    if fetch_prev is not None:
        avg["fetch"] = (fetch_prev[0], fetch_prev[1], 0)

    cab = ["P_idle", "b0", "T_idle"]                 # van primero, solo si existen
    order = [k for k in cab if k in avg] + [k for k in avg if k not in cab]
    desc = ("Bucles dominados (M1)" if es_m1 else "Regresion NNLS (M2)")
    with open(COEF, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([f"# {desc} - PROMEDIO de {len(files)} tandas. "
                    f"Generado {time.strftime('%Y-%m-%d %H:%M:%S')}.",
                    "coef=(P_cat-P_idle)*T/n; div usa DIVCYC." if es_m1
                    else "coef diferenciales promediados campana a campana."])
        w.writerow(["parametro", "coef", "unidad"])
        for k in order:
            v, u, _ = avg[k]
            w.writerow([k, f"{v:.6e}", u])

    print(f"Promedio de {len(files)} tandas -> {os.path.relpath(COEF, HERE)}:")
    for fn in files:
        print(f"  + {os.path.basename(fn)}")
    print(f"\n{'param':11s} {'promedio':>11} {'unid':>8} {'n':>3}")
    for k in order:
        v, u, n = avg[k]
        sc = 1e9 if u in ("J/instr", "J/ciclo") else 1
        us = "nJ" if sc > 1 else (u or "-")
        tag = " (del barrido)" if k == "fetch" and n == 0 else ""
        print(f"{k:11s} {v*sc:11.3f} {us:>8} {n:>3}{tag}")
    if es_m1 and "fetch" not in avg:
        print("\n(sin 'fetch': corre el barrido despues para ctrl-flush + fetch)")


if __name__ == "__main__":
    main()
