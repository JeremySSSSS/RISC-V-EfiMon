// M3 - referencia IDLE WFI LARGA (~5 min a 10 MHz: 1000 x 0.3 s).
// Linea base del piso bien promediada (como la de m1): mas muestras del ESP32 ->
// media de P_idle mas estable, menos ruido en el delta. Abre UNA ventana GPIO y
// duerme el core con wfi despertado por el FC timer (piso pasivo real).
#include "platform.inc"

#ifndef IDLE_REPS
#define IDLE_REPS  1000       // 1000 x 0.3 s ~ 5 min (como m1)
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
    .space 72
