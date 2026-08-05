// M1 - bucle dominado MEM.  ~20 s a 10 MHz.
// REDISENADO con operandos VARIADOS (misma leccion que ctrl): la version
// anterior repetia los mismos operandos por siempre y media la cota INFERIOR
// del costo (sin conmutacion de datos; el dato escrito era SIEMPRE 0xABCD1234). Diseno "pool de pares": 10
// registros con valores variados -> 45 pares DISTINTOS de operandos por
// bloque (conmutacion real entre operaciones consecutivas), resultados a un
// registro sumidero (sin realimentacion -> los valores no colapsan), y 2
// updates por iteracion que evolucionan el pool. Dominancia ~98%.
// Operandos inicializados DESPUES de gpio_high (el macro pisa t0/t1).
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
    li s0, 616000                 // LOOP_COUNT

    gpio_high

    li t0, 0x7A3F158B
    li t1, 0xC49E2D87
    li t2, 0x5D18B3E9
    li t3, 0xA7C46F21
    li t4, 0x39F7D5A3
    li t5, 0xE8B1C4D5
    li t6, 0x6C2E9F47
    li a0, 0x91D5B7E3
    li a1, 0x4BF8A6D1
    li a2, 0xD73C58A9

    csrr s1, mcycle
measurement_loop:
    .rept 4
    sw t0, 0(s2)
    lw a4, 12(s2)
    sw t1, 32(s2)
    lw a4, 44(s2)
    sw t2, 0(s2)
    lw a4, 12(s2)
    sw t3, 32(s2)
    lw a4, 44(s2)
    sw t4, 0(s2)
    lw a4, 12(s2)
    sw t5, 32(s2)
    lw a4, 44(s2)
    sw t6, 0(s2)
    lw a4, 12(s2)
    sw a0, 32(s2)
    lw a4, 44(s2)
    sw a1, 0(s2)
    lw a4, 12(s2)
    sw a2, 32(s2)
    lw a4, 44(s2)
    sw t0, 0(s2)
    lw a4, 12(s2)
    sw t1, 32(s2)
    lw a4, 44(s2)
    sw t2, 0(s2)
    lw a4, 12(s2)
    sw t3, 32(s2)
    lw a4, 44(s2)
    sw t4, 0(s2)
    lw a4, 12(s2)
    sw t5, 32(s2)
    lw a4, 44(s2)
    sw t6, 0(s2)
    lw a4, 12(s2)
    sw a0, 32(s2)
    lw a4, 44(s2)
    sw a1, 0(s2)
    lw a4, 12(s2)
    sw a2, 32(s2)
    lw a4, 44(s2)
    .endr
    addi t0, t0, 0x2F1
    addi a1, a1, 0x1B3
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
.align 4
data_words:
    .space 64
