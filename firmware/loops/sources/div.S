// M1 - bucle dominado DIV.  ~20 s a 10 MHz (557.5k iter x 256 instr/iter).
// 256 div/divu/rem/remu (divisor serial, data-dependent ~21 cic/div) por iteracion.
// Desenrollado x4 (vs 64) para que el overhead addi/bnez pese 1-en-256 (0.4%).
// El coeficiente de esta categoria es p_div (pJ/CICLO de DIVCYC), modelo hibrido.
// Ventana de medicion = flanco de GPIO8 (-> ESP32). Vuelca 16 CSR + mcycle a 'results'.
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
    li s0, 74335                   // LOOP_COUNT

    gpio_high

    li a1, 0x7FFFFF01               // dividendo
    li a2, 0x000037A1               // divisor (no nulo)

    csrr s1, mcycle
measurement_loop:
    .rept 64
    div  t0, a1, a2
    divu t1, a1, a2
    rem  t2, a1, a2
    remu t3, a1, a2
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
    .space 128
