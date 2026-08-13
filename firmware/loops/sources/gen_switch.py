#!/usr/bin/env python3
"""Genera los kernels de SWITCHING inter-instruccion (experimento Tiwari, termino 2)
para M1. Cada kernel alterna DOS categorias al maximo (A,B,A,B,...) con operandos
rotados. Sirven para medir el overhead que los bucles dominados NO exponen:

    overhead_par = (P_med - P_idle)*T - (e_A*n_A + e_B*n_B[ o e_div*c_div])

El promedio de los overhead da la ESCALA de M1 (factor multiplicativo sobre la
energia por instruccion), sin depender de M2. Salida: sw_<A>_<B>.S en este dir.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
POOL = ["t0", "t1", "t2", "t3", "t4", "t5", "t6", "a0", "a3", "a5"]
INIT = ["0x7A3F158B", "0xC49E2D87", "0x5D18B3E9", "0xA7C46F21", "0x39F7D5A3",
        "0xE8B1C4D5", "0x6C2E9F47", "0x91D5B7E3", "0x4BF8A6D1", "0xD73C58A9"]
BLK = 10            # pares distintos por bloque (operandos rotados)
UNROLL = 48         # bloques desenrollados por iteracion

# LOOP_COUNT ~ para ~25 s a 10 MHz (se puede ajustar tras la 1a corrida)
LOOPS = {
    "alu_mem": 380000, "alu_mul": 380000, "alu_ctrl": 300000,
    "alu_mulh": 300000, "mem_mul": 360000, "mem_ctrl": 300000,
    "mul_mulh": 300000, "alu_div": 26000,
}


def op(cat, k):
    """Una instruccion de la categoria, con operandos del pool rotados por k."""
    i, j = k % BLK, (k + 3) % BLK
    if cat == "alu":
        return f"    xor  a4, {POOL[i]}, {POOL[j]}"
    if cat == "mul":
        return f"    mul  a4, {POOL[i]}, {POOL[j]}"
    if cat == "mulh":
        m = ["mulh", "mulhu", "mulhsu"][k % 3]
        return f"    {m:6s} a4, {POOL[i]}, {POOL[j]}"
    if cat == "mem":
        off = (k * 4) % 64
        return (f"    sw   {POOL[i]}, {off}(s2)" if k % 2 == 0
                else f"    lw   a4, {off}(s2)")
    if cat == "ctrl":
        return f"    beq  x0, x0, 1f\n1:"          # salto tomado (flush) = ctrl
    if cat == "div":
        d = ["div", "divu", "rem", "remu"][k % 4]
        return f"    {d:6s} a4, {POOL[i]}, a2"     # a2 = divisor no nulo fijo
    raise ValueError(cat)


def kernel(a, b):
    name = f"{a}_{b}"
    usa_mem = "mem" in (a, b)
    body = []
    for k in range(UNROLL * BLK):
        body.append(op(a, k))
        body.append(op(b, k))
    body = "\n".join(body)
    setup = "\n".join(f"    li {POOL[i]}, {INIT[i]}" for i in range(len(POOL)))
    mem_setup = "    la s2, data_words\n" if usa_mem else ""
    div_setup = "    li a2, 0x000037A1              // divisor no nulo\n" if "div" in (a, b) else ""
    data_sec = ("\n.align 4\ndata_words:\n    .space 64\n" if usa_mem else "")

    return f"""// M1 - SWITCHING {a.upper()}<->{b.upper()} (experimento Tiwari, overhead inter-instr).
// Alterna 1 {a} y 1 {b} al maximo (A,B,A,B...), operandos rotados. Se compara
// contra la prediccion base (e_{a}*n_{a} + e_{b}*n_{b}) -> el exceso es el overhead.
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
{mem_setup}{div_setup}    li s0, {LOOPS[name]}                 // LOOP_COUNT

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


PAIRS = [("alu", "mem"), ("alu", "mul"), ("alu", "ctrl"), ("alu", "mulh"),
         ("mem", "mul"), ("mem", "ctrl"), ("mul", "mulh"), ("alu", "div")]


def main():
    for a, b in PAIRS:
        path = os.path.join(HERE, f"sw_{a}_{b}.S")
        with open(path, "w") as f:
            f.write(kernel(a, b))
        print(f"  escrito sw_{a}_{b}.S")
    print(f"\n{len(PAIRS)} kernels de switching generados en {HERE}")


if __name__ == "__main__":
    main()
