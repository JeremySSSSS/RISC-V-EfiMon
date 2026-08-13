#!/usr/bin/env python3
"""Genera las variantes de intensidad (_d60/_d30) de programas NUEVOS de
calibracion. Corre el ELF base una vez por JTAG (solo necesita OpenOCD, no el
banco de potencia), mide sus ciclos con mcycle, calcula el trabajo por tanda
(REPS) y las pausas (SLEEP_TICKS) para 60% y 30% de intensidad, y agrega las
reglas a fuentes/duty_variants.mk. Al final recompila todo.

Uso:  python3 gen_duty.py mulhchain saxpy
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "comun"))
import jtag  # noqa: E402

FUENTES = os.path.join(HERE, "fuentes")
MK = os.path.join(FUENTES, "duty_variants.mk")
CHUNKS = 10
ACT_D60 = 7.2e6      # ciclos ACTIVOS por tanda a d60 (12 s totales a 10 MHz)
ACT_D30 = 3.6e6      # ciclos activos por tanda a d30 (6 s totales)


def regla_base(prog):
    """Extrae (REPS base, flags de arquitectura) de la regla del Makefile."""
    mk = open(os.path.join(FUENTES, "Makefile")).read()
    m = re.search(rf"\$\(OUT\)/{prog}\.elf:.*?\n\t\$\(CC\) \$\(KFLAGS\) "
                  rf"(-march=\S+(?: -ffp-contract=off)?)\s+-DREPS=(\d+)", mk)
    if not m:
        sys.exit(f"{prog}: no encontre su regla en fuentes/Makefile")
    return int(m.group(2)), m.group(1)


def main():
    progs = sys.argv[1:]
    if not progs:
        sys.exit(__doc__)
    bloques = []
    duty_elfs = []
    for p in progs:
        reps_base, flags = regla_base(p)
        elf = os.path.join(HERE, "elf", f"{p}.elf")
        if not os.path.exists(elf):
            sys.exit(f"falta {elf}: corre 'make' en fuentes/ primero")
        print(f"==> midiendo {p} por JTAG (ELF base, ~10-15 s)...")
        words = jtag.run_one(elf)
        mc = jtag.mcycle_de(words)
        cyc = mc / reps_base
        print(f"    mcycle={mc:,}  ({mc/1e7:.1f} s activos, "
              f"{cyc:.1f} ciclos/rep)")
        r60 = max(1, round(ACT_D60 / cyc))
        r30 = max(1, round(ACT_D30 / cyc))
        s60 = round(r60 * cyc * (1 - 0.60) / 0.60)
        s30 = round(r30 * cyc * (1 - 0.30) / 0.30)
        src = f"wl_{p}.c"
        for suf, r, sl in (("d60", r60, s60), ("d30", r30, s30)):
            duty_elfs.append(f"$(OUT)/{p}_{suf}.elf")
            bloques.append(
                f"$(OUT)/{p}_{suf}.elf: harness.S {src} platform.inc link.ld\n"
                f"\t$(CC) $(KFLAGS) {flags} -DREPS={r} -DCHUNKS={CHUNKS} "
                f"-DSLEEP_TICKS={sl} -o $@ harness.S {src}\n")
    with open(MK, "a") as f:
        f.write(f"\n# --- agregado por gen_duty.py: {' '.join(progs)} ---\n")
        f.write("DUTY_ELFS += " + " ".join(duty_elfs) + "\n\n")
        f.write("\n".join(bloques))
    print(f"\n{len(bloques)} reglas agregadas a duty_variants.mk; recompilando...")
    subprocess.run(["make", "all"], cwd=FUENTES, check=True)
    print("listo: variantes _d60/_d30 generadas y compiladas.")


if __name__ == "__main__":
    main()
