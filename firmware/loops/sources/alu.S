// M1 - bucle dominado ALU.  ~20 s a 10 MHz (11.25M iter x 256 instr/iter).
// 256 add/xor/slli por iteracion (ALU simple, 1 ciclo) + addi/bnez de control.
// Desenrollado x4 (vs 64) para que el overhead addi/bnez pese 1-en-256 (0.4%).
// Ventana de medicion = flanco de GPIO8 (-> ESP32). Al final vuelca los 16 CSR
// + mcycle ini/fin a 'results' (leer por JTAG con  x/30xw &results).
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
    csrci 0x320, 1                  // habilita mcycle (mcountinhibit.CY = 0)

    reset_category_counters
    li s0, 1538462                 // LOOP_COUNT

    gpio_high                       // abre la ventana medida

    li t0, 0x12345
    li t1, 0x06789

    csrr s1, mcycle
measurement_loop:
    .rept 64
    addi t0, t0, 1
    xor  t1, t1, t0
    slli t2, t0, 2
    add  t3, t1, t2
    .endr
    addi s0, s0, -1
    bnez s0, measurement_loop
    csrr s2, mcycle

    gpio_low                        // cierra la ventana
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
