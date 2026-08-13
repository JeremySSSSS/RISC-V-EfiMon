// M1 - SWITCHING ALU<->CTRL (experimento Tiwari, overhead inter-instr).
// Alterna 1 alu y 1 ctrl al maximo (A,B,A,B...), operandos rotados. Se compara
// contra la prediccion base (e_alu*n_alu + e_ctrl*n_ctrl) -> el exceso es el overhead.
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
    li s0, 300000                 // LOOP_COUNT

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
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
    beq  x0, x0, 1f
1:
    xor  a4, t0, t3
    beq  x0, x0, 1f
1:
    xor  a4, t1, t4
    beq  x0, x0, 1f
1:
    xor  a4, t2, t5
    beq  x0, x0, 1f
1:
    xor  a4, t3, t6
    beq  x0, x0, 1f
1:
    xor  a4, t4, a0
    beq  x0, x0, 1f
1:
    xor  a4, t5, a3
    beq  x0, x0, 1f
1:
    xor  a4, t6, a5
    beq  x0, x0, 1f
1:
    xor  a4, a0, t0
    beq  x0, x0, 1f
1:
    xor  a4, a3, t1
    beq  x0, x0, 1f
1:
    xor  a4, a5, t2
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
