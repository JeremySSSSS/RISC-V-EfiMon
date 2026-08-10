// Bucle dominado por la categoria fp_fma: multiplicacion-acumulacion (fmadd/fnmsub).
// Un solo tipo de operacion FP domina el retiro para despejar su coeficiente
// energetico contra idle. (Antes se generaba desde fp.S con -DFP_FMA.)
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
    csrci 0x320, 1
    reset_category_counters

    li s0, 36000000  // LOOP_COUNT (~40 s)
    li t0, 0x6000
    csrs mstatus, t0
    la t0, fp_words
    flw ft0, 0(t0)
    flw ft1, 4(t0)
    flw ft2, 8(t0)
    flw ft3, 12(t0)

    gpio_high
    csrr s1, mcycle
measurement_loop:
    .rept 4
    fmadd.s ft4, ft0, ft1, ft2
    fnmsub.s ft4, ft1, ft2, ft3
    .endr
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
    .space 120

.section .data
.align 4
fp_words:
    .float 1.125
    .float 1.75
    .float 2.25
    .float 3.5
