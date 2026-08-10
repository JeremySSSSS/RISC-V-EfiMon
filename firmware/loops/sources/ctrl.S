// M1 - bucle dominado CTRL, version FOOTPRINT (fetch/i-cache).
// El ctrl.S anterior era un lazo diminuto (~500 B) que cabia en la i-cache: media
// solo el flush del branch tomado (~5.35 nJ) y quedaba ~1.7x por debajo de la
// regression, que sobre codigo real ve ademas el costo de FETCH (saltos a codigo
// disperso -> misses de i-cache, refill desde L2). Esta version DESENROLLA el
// cuerpo hasta ~16 KB (> i-cache del FC) para que cada pasada re-busque el codigo
// desde L2, pagando ese costo como el codigo real. Si el coef sube hacia ~9,
// confirma que el loop chico subestimaba; si se queda en ~5-6, el exceso de la
// regression es otra cosa (contexto, no fetch).
//   - branches condicionales SIEMPRE tomados (flush 3 ciclos), operandos que
//     cambian; distancias variadas; instruccion victima (fetch perdido) tras c/u.
//   - Dominancia ctrl >95%: 4 updates ALU cada 24 grupos de saltos.
// Ajustar LOOP_COUNT en el banco para ventana ~20 s (el fetch agrega ciclos).
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
    li s0, 36750                    // LOOP_COUNT (tune ~20 s en banco)

    gpio_high
    li t0, 0x100
    li t1, 0x101
    li t2, 0x80001111
    li t3, 0x00000F0F

    csrr s1, mcycle
measurement_loop:
    // FOOTPRINT: 32 bloques de (update + 24 grupos) -> ~16 KB de codigo por pasada
    .rept 32
    addi t0, t0, 2
    addi t1, t1, 2
    addi t3, t3, 2
    xori t2, t2, 0x5A5
    .rept 24
    bne  t0, t1, 1f
    xor  a0, t0, t1
1:  blt  t2, t3, 2f
    add  a1, t2, t3
    sub  a2, t3, t2
2:  bgeu t1, t0, 3f
    and  a3, t0, t2
3:  j    4f
    or   a4, t1, t3
4:  bne  t3, t2, 5f
    xor  a5, t2, t3
5:
    .endr
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
