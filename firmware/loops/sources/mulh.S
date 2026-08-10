// M1 - bucle dominado MULH.  ~20 s a 10 MHz.
// REDISENADO con operandos VARIADOS (misma leccion que ctrl): la version
// anterior repetia los mismos operandos por siempre y media la cota INFERIOR
// del costo (sin conmutacion de datos; multiciclo -> efecto x5). Diseno "pool de pares": 10
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
    li s0, 441545                 // LOOP_COUNT

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
    mulh a4, t0, t1
    mulhu a4, t0, t2
    mulhsu a4, t0, t3
    mulh a4, t0, t4
    mulhu a4, t0, t5
    mulhsu a4, t0, t6
    mulh a4, t0, a0
    mulhu a4, t0, a1
    mulhsu a4, t0, a2
    mulh a4, t1, t2
    mulhu a4, t1, t3
    mulhsu a4, t1, t4
    mulh a4, t1, t5
    mulhu a4, t1, t6
    mulhsu a4, t1, a0
    mulh a4, t1, a1
    mulhu a4, t1, a2
    mulhsu a4, t2, t3
    mulh a4, t2, t4
    mulhu a4, t2, t5
    mulhsu a4, t2, t6
    mulh a4, t2, a0
    mulhu a4, t2, a1
    mulhsu a4, t2, a2
    mulh a4, t3, t4
    mulhu a4, t3, t5
    mulhsu a4, t3, t6
    mulh a4, t3, a0
    mulhu a4, t3, a1
    mulhsu a4, t3, a2
    mulh a4, t4, t5
    mulhu a4, t4, t6
    mulhsu a4, t4, a0
    mulh a4, t4, a1
    mulhu a4, t4, a2
    mulhsu a4, t5, t6
    mulh a4, t5, a0
    mulhu a4, t5, a1
    mulhsu a4, t5, a2
    mulh a4, t6, a0
    mulhu a4, t6, a1
    mulhsu a4, t6, a2
    mulh a4, a0, a1
    mulhu a4, a0, a2
    mulhsu a4, a1, a2
    .endr
    addi t0, t0, 0x2F1              // evoluciona el pool (2 regs/iter)
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
