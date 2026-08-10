// M1 - linea base IDLE WFI. ~20 s a 10 MHz (67 x 0.3 s).
// Abre una sola ventana GPIO y duerme el core con wfi despertado por FC timer.
// Da P_idle pasivo para restar a los loops homogeneos.
#include "platform.inc"

#ifndef IDLE_REPS
#define IDLE_REPS  40
#endif
#define IDLE_TICKS 3000000

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
    enable_timer_wakeup
    csrci 0x320, 1                  // habilita mcycle

    reset_category_counters
    li s0, IDLE_REPS

    gpio_high

    csrr s1, mcycle
measurement_loop:
    wfi_idle IDLE_TICKS
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
