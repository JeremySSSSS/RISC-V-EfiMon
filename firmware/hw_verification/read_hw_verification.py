#!/usr/bin/env python3
"""Ejecuta el programa mixto de verificacion y guarda su composicion global."""
import csv
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GDB_BIN = os.environ.get("GDB_BIN", "gdb-multiarch")
ELF = os.path.join(HERE, "elf", "verificacion_hw.elf")
OUT_CSV = os.path.join(HERE, "verificacion_hw.csv")

GDB_SCRIPT = """\
set pagination off
set confirm off
target remote :3333
monitor reset halt
load
continue
x/32xw &results
"""

LO = {
    "n_alu": 0,
    "n_mul": 2,
    "n_mulh": 4,
    "n_div": 6,
    "n_mem": 8,
    "n_ctrl": 10,
    "n_fp_add": 12,
    "n_fp_mul": 14,
    "n_fp_fma": 16,
    "n_fp_div": 18,
    "n_fp_sqrt": 20,
    "n_fp_noncomp": 22,
    "n_fp_conv": 24,
    "c_div": 26,
}
LINE = re.compile(r"^0x[0-9a-fA-F]+:(\s+0x[0-9a-fA-F]+)+\s*$")
WORD = re.compile(r"0x[0-9a-fA-F]+")
PROMPT = re.compile(r"^(\(gdb\)\s*)+")


def val(w, idx):
    return w[idx] + (w[idx + 1] << 32)


def run_gdb():
    if not os.path.exists(ELF):
        subprocess.run(["make"], cwd=HERE, check=True)
    out = subprocess.run([GDB_BIN, ELF], input=GDB_SCRIPT,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, timeout=120).stdout
    words = []
    for line in out.splitlines():
        line = PROMPT.sub("", line.strip())
        if LINE.match(line):
            _, rest = line.split(":", 1)
            words.extend(int(x, 16) for x in WORD.findall(rest))
    if len(words) != 32:
        raise RuntimeError(f"se esperaban 32 words y llegaron {len(words)}\n{out}")
    return words


def main():
    w = run_gdb()
    row = {"date": time.strftime("%Y-%m-%d %H:%M:%S"), "program": "mixto_float"}
    for name, idx in LO.items():
        row[name] = val(w, idx)
    row["mcycle"] = (w[29] - w[28]) & 0xFFFFFFFF

    header = ["date", "program", "n_alu", "n_mul", "n_mulh", "n_div",
              "n_mem", "n_ctrl", "n_fp_add", "n_fp_mul", "n_fp_fma",
              "n_fp_div", "n_fp_sqrt", "n_fp_noncomp", "n_fp_conv",
              "c_div", "mcycle"]
    with open(OUT_CSV, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=header)
        wr.writeheader()
        wr.writerow(row)

    instr = sum(row[k] for k in ("n_alu", "n_mul", "n_mulh", "n_div",
                                 "n_mem", "n_ctrl", "n_fp_add", "n_fp_mul",
                                 "n_fp_fma", "n_fp_div", "n_fp_sqrt",
                                 "n_fp_noncomp", "n_fp_conv"))
    for k in ("n_alu", "n_mul", "n_mulh", "n_div", "n_mem", "n_ctrl",
              "n_fp_add", "n_fp_mul", "n_fp_fma", "n_fp_div", "n_fp_sqrt",
              "n_fp_noncomp", "n_fp_conv"):
        print(f"{k[2:]:5s}: {row[k]:7d}  {100*row[k]/instr:6.2f}%")
    print(f"c_div : {row['c_div']:7d}"
          f"  ({row['c_div']/row['n_div']:.1f} ciclos/div)")
    print(f"mcycle: {row['mcycle']}")
    print(f"CSV: {OUT_CSV}")


if __name__ == "__main__":
    sys.exit(main())
