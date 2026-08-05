#!/usr/bin/env python3
"""Generates the intensity variants (_d60/_d30) of NEW calibration programs.
Runs the base ELF once over JTAG (only needs OpenOCD, not the power bench),
measures its cycles with mcycle, computes the work per batch (REPS) and the
pauses (SLEEP_TICKS) for 60% and 30% intensity, and appends the rules to
sources/duty_variants.mk. At the end it rebuilds everything.

Usage:  python3 gen_duty.py mulhchain saxpy
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "common"))
import jtag  # noqa: E402

FUENTES = os.path.join(HERE, "sources")
MK = os.path.join(FUENTES, "duty_variants.mk")
CHUNKS = 10
ACT_D60 = 1.2e7      # ACTIVE cycles per batch at d60 (12 s total at 10 MHz)
ACT_D30 = 0.6e7      # active cycles per batch at d30 (6 s total)


def regla_base(prog):
    """Extracts (base REPS, architecture flags) from the Makefile rule."""
    mk = open(os.path.join(FUENTES, "Makefile")).read()
    m = re.search(rf"\$\(OUT\)/{prog}\.elf:.*?\n\t\$\(CC\) \$\(KFLAGS\) "
                  rf"(-march=\S+(?: -ffp-contract=off)?)\s+-DREPS=(\d+)", mk)
    if not m:
        sys.exit(f"{prog}: could not find its rule in sources/Makefile")
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
            sys.exit(f"missing {elf}: run 'make' in sources/ first")
        print(f"==> measuring {p} over JTAG (base ELF, ~10-15 s)...")
        words = jtag.run_one(elf)
        mc = jtag.mcycle_de(words)
        cyc = mc / reps_base
        print(f"    mcycle={mc:,}  ({mc/1e7:.1f} s active, "
              f"{cyc:.1f} cycles/rep)")
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
        f.write(f"\n# --- added by gen_duty.py: {' '.join(progs)} ---\n")
        f.write("DUTY_ELFS += " + " ".join(duty_elfs) + "\n\n")
        f.write("\n".join(bloques))
    print(f"\n{len(bloques)} rules added to duty_variants.mk; rebuilding...")
    subprocess.run(["make", "all"], cwd=FUENTES, check=True)
    print("done: _d60/_d30 variants generated and compiled.")


if __name__ == "__main__":
    main()
