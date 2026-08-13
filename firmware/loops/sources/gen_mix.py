#!/usr/bin/env python3
"""Genera kernels de MEZCLA REALISTA para calibrar la escala de overhead de M1.

A diferencia de los sw_<A>_<B> (50/50, switching MAXIMO = peor caso), estos
reproducen perfiles de instrucciones tipicos de codigo embebido con switching
NATURAL (runs de misma categoria tipo basic-block). Miden el overhead que ve el
codigo REAL -> escala representativa (~1.1), no el peor caso (~1.2).

Tres perfiles que cubren el espacio realista:
  mix_gen  general      (alu-dominante, poco mem/ctrl)
  mix_mem  memoria alta (sort/memcpy/histogram)
  mix_ari  aritmetica   (mul/mulh, tipo mulhash/matmul)

Salida: mix_*.S en este dir. Los operandos y el dump son los del gen_switch.
"""
import os

from gen_switch import op, POOL, INIT, LOOPS  # noqa: F401  (reusa building-blocks)

HERE = os.path.dirname(os.path.abspath(__file__))
UNROLL = 64      # repeticiones del bloque por iteracion

# Patrones estilo "basic-block": runs de misma categoria y saltos esporadicos.
# La proporcion EXACTA no es critica (el overhead usa los n_i medidos); importa
# que sea realista y con switching natural.
PATRONES = {
    # ~60% alu, 13% mem, 13% ctrl, 7% mul, 7% mulh
    "mix_gen": ["alu", "alu", "alu", "mem", "alu", "alu", "mul", "alu",
                "ctrl", "alu", "alu", "mulh", "alu", "mem", "ctrl"],
    # ~43% alu, 36% mem, 14% ctrl, 7% mul   (memoria alta)
    "mix_mem": ["alu", "mem", "alu", "mem", "ctrl", "alu", "mem", "alu",
                "mul", "mem", "alu", "ctrl", "alu", "mem"],
    # ~43% alu, 21% mul, 14% mulh, 14% ctrl, 7% mem  (aritmetica)
    "mix_ari": ["alu", "mul", "alu", "mulh", "alu", "mul", "alu", "ctrl",
                "mul", "alu", "mulh", "alu", "mem", "ctrl"],
}
# LOOP_COUNT ~ para ~25 s a 10 MHz (ajustable tras la 1a corrida)
LOOPS_MIX = {"mix_gen": 240000, "mix_mem": 200000, "mix_ari": 200000}


def kernel(name, patron):
    usa_mem = "mem" in patron
    usa_div = "div" in patron
    body = []
    k = 0
    for _ in range(UNROLL):
        for cat in patron:
            body.append(op(cat, k))
            k += 1
    body = "\n".join(body)
    setup = "\n".join(f"    li {POOL[i]}, {INIT[i]}" for i in range(len(POOL)))
    mem_setup = "    la s2, data_words\n" if usa_mem else ""
    div_setup = "    li a2, 0x000037A1              // divisor no nulo\n" if usa_div else ""
    data_sec = ("\n.align 4\ndata_words:\n    .space 64\n" if usa_mem else "")
    props = ", ".join(f"{c}:{patron.count(c)}" for c in
                      ["alu", "mem", "ctrl", "mul", "mulh", "div"] if c in patron)

    return f"""// M1 - MEZCLA REALISTA '{name}' (calibra la escala de overhead inter-instr).
// Perfil por bloque ({props}), {len(patron)} instr, switching NATURAL (runs tipo
// basic-block). Contrasta con los sw_* (50/50, peor caso). Overhead vs base ->
// escala representativa de codigo real.
#include "platform.inc"

.section .text.start
.globl _start
.type _start, @function
_start:
    .option push
    .option norvc

    la sp, __stack_top
    la t0, trap_handler
    csrw mtvec, t0

    gpio_init
    csrci 0x320, 1                  // habilita mcycle

    reset_category_counters
{mem_setup}{div_setup}    li s0, {LOOPS_MIX[name]}                 // LOOP_COUNT

    gpio_high

{setup}

    csrr s1, mcycle
measurement_loop:
{body}
    addi s0, s0, -1
    bnez s0, measurement_loop
    csrr s2, mcycle

    gpio_low
    dump_counters

finished:
    ebreak
    wfi
    j finished

trap_handler:
    ebreak
    j trap_handler

    .option pop
.size _start, .-_start

.section .bss
.align 4
.globl results
results:
    .space 128
{data_sec}"""


def main():
    for name, patron in PATRONES.items():
        with open(os.path.join(HERE, f"{name}.S"), "w") as f:
            f.write(kernel(name, patron))
        print(f"  escrito {name}.S")
    print(f"\n{len(PATRONES)} kernels de mezcla realista generados en {HERE}")


if __name__ == "__main__":
    main()
