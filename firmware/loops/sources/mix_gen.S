// M1 - MEZCLA REALISTA 'mix_gen' (calibra la escala de overhead inter-instr).
// Perfil por bloque (alu:9, mem:2, ctrl:2, mul:1, mulh:1), 15 instr, switching NATURAL (runs tipo
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
    la s2, data_words
    li s0, 240000                 // LOOP_COUNT

    gpio_high

    li t0, 0x7A3F158B
    li t1, 0xC49E2D87
    li t2, 0x5D18B3E9
    li t3, 0xA7C46F21
    li t4, 0x39F7D5A3
    li t5, 0xE8B1C4D5
    li t6, 0x6C2E9F47
    li a0, 0x91D5B7E3
    li a3, 0x4BF8A6D1
    li a5, 0xD73C58A9

    csrr s1, mcycle
measurement_loop:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 12(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 52(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 8(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 48(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 4(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 44(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 0(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 40(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 60(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 36(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 56(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 32(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 52(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 28(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 48(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 24(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 44(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 20(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 40(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 16(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 36(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 12(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 32(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 8(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 28(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 4(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 24(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 0(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 20(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 60(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 16(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 56(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 12(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 52(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 8(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 48(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 4(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 44(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 0(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 40(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 60(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 36(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 56(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 32(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 52(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 28(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 48(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 24(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 44(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 20(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 40(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 16(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 36(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 12(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 32(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 8(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 28(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 4(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 24(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 0(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 20(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 60(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 16(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 56(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 12(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 52(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 8(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 48(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 4(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 44(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 0(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 40(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 60(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 36(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 56(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 32(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 52(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 28(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 48(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 24(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 44(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 20(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 40(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 16(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 36(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 12(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 32(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 8(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 28(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 4(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 24(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 0(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 20(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 60(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 16(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 56(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 12(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 52(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 8(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 48(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 4(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 44(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 0(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 40(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 60(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 36(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 56(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 32(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 52(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 28(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 48(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 24(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 44(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 20(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 40(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 16(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 36(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 12(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 32(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 8(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 28(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 4(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 24(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 0(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    xor  a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 20(s2)
    xor  a4, t4, a0
    xor  a4, t5, a3
    mul  a4, t6, a5
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    xor  a4, t0, t3
    mulhsu a4, t1, t4
    xor  a4, t2, t5
    lw   a4, 60(s2)
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    xor  a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 16(s2)
    xor  a4, a5, t2
    xor  a4, t0, t3
    mul  a4, t1, t4
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    xor  a4, t5, a3
    mulhsu a4, t6, a5
    xor  a4, a0, t0
    sw   a3, 56(s2)
    beq  x0, x0, 1f
1:
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

.align 4
data_words:
    .space 64
