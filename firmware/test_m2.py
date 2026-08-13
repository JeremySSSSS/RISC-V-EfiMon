#!/usr/bin/env python3
"""Smoke-test de los programas de calibracion M2: corre cada uno por JTAG (solo
contadores, timeout corto) y reporta OK / TRAP / CUELGUE. Sirve para verificar
que todos corren antes de la campana completa (~18 min).

Uso:
    python3 test_m2.py                # los 21 base
    python3 test_m2.py --duty         # ademas las variantes _d60/_d30
    python3 test_m2.py --fp           # ademas las sondas fp (candidatas a colgar)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "comun"))
os.environ.setdefault("GDB_TIMEOUT", "30")   # cuelgue -> falla en 30s
import jtag      # noqa: E402
import modelo    # noqa: E402

# set de calibracion M2 actual: dominantes (enteros + fp) + mixtos
BASE = ["dmul", "dmulh", "ddiv", "dctrl", "fpadd", "fpmul", "fpfma", "fpdiv", "fpsqrt", "fpnoncomp", "fpconv", "memcpy", "matmul", "dotprod", "gcd", "radix", "histogram", "sort", "modmul", "memfill", "wmac", "mulhash64", "mulhscale", "mulhstream", "fir", "ratscale", "modpow", "trialdiv"]
FP = ["fpadd", "fpmul", "fpfma", "fpdiv", "fpsqrt", "fpnoncomp", "fpconv"]
DIR_ELF = os.path.join(HERE, "regresion", "elf")


def test(prog):
    elf = os.path.join(DIR_ELF, f"{prog}.elf")
    if not os.path.exists(elf):
        return "FALTA .elf (make all)", False
    try:
        words = jtag.run_one(elf)
        w = [modelo.to_int(x) for x in words]
        cont = modelo.contadores(w)
        ntot = sum(cont[k] for k in ("n_alu", "n_mul", "n_mulh", "n_div", "n_mem",
                                     "n_ctrl", "n_fp_add", "n_fp_mul", "n_fp_fma",
                                     "n_fp_div", "n_fp_sqrt", "n_fp_noncomp", "n_fp_conv"))
        T = cont["mcycle"] / modelo.F_CLK
        return f"OK  T={T:5.1f}s  n={ntot:>10,}  fetch={cont['n_fetch']:>7}", True
    except RuntimeError as e:
        msg = str(e)
        if "trap" in msg:
            return "TRAP (illegal/csr?)", False
        return "CUELGUE/timeout", False


def main():
    # nombres sueltos en la linea de comando -> corre SOLO esos (p.ej.
    # 'test_m2.py fpadd fpdiv' para probar 2 sondas sin los 21 enteros)
    explicitos = [a for a in sys.argv[1:] if not a.startswith("-")]
    if explicitos:
        progs = explicitos
        print(f"=== smoke-test M2: SOLO {len(progs)} pedidos "
              f"(GDB_TIMEOUT={os.environ['GDB_TIMEOUT']}s) ===\n")
        _run(progs)
        return
    progs = list(BASE)
    if "--fp" in sys.argv:
        progs += FP
    if "--duty" in sys.argv:
        extra = []
        for b in BASE:
            for suf in ("_d60", "_d30"):
                if os.path.exists(os.path.join(DIR_ELF, f"{b}{suf}.elf")):
                    extra.append(f"{b}{suf}")
        progs += extra

    print(f"=== smoke-test M2: {len(progs)} programas (GDB_TIMEOUT={os.environ['GDB_TIMEOUT']}s) ===\n")
    _run(progs)


def _run(progs):
    ok = mal = 0
    malos = []
    for p in progs:
        estado, good = test(p)
        print(f"  {p:16s} {estado}")
        if good:
            ok += 1
        else:
            mal += 1
            malos.append(p)
    print(f"\n{ok} OK,  {mal} con problema  (de {len(progs)})")
    if malos:
        print("  problemas:", ", ".join(malos))
    else:
        print("  todos corren -> podes largar la campana M2")


if __name__ == "__main__":
    main()
