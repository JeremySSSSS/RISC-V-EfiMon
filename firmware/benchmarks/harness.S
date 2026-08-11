// Harness fisico para cargas REALES (Metodo 2). Envuelve un kernel
// 'run_workload()' (programa real, mezcla natural de instrucciones) entre la
// ventana GPIO8, y al final vuelca los 16 CSR + mcycle a 'results'
// (0x1c0082c0, 30 words). El kernel se enlaza desde un .c aparte.
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

    /* Limpia .bss: los kernels de BEEBS asumen estaticas en cero (entorno C
     * estandar), pero .bss es NOLOAD y el JTAG no lo reescribe al recargar.
     * La SRAM solo nace en cero con el bitstream: sin esta limpieza, la
     * SEGUNDA tanda hereda la basura del programa anterior (dijkstra se
     * colgaba porque el indice de su pool de memoria arrancaba corrupto). */
    la t0, __bss_start
    la t1, __bss_end
1:  bgeu t0, t1, 2f
    sw zero, 0(t0)
    addi t0, t0, 4
    j 1b
2:

    gpio_init
    csrci 0x320, 1            /* habilita mcycle */

    /* Habilita FP por si el kernel usa float (inofensivo si no). */
    li t0, 0x6000
    csrs mstatus, t0

    reset_category_counters

    gpio_high
    /* mcycle_ini a MEMORIA, no a un registro callee-saved: algunos kernels en
     * assembly (wl_sha256.S etc.) pisan s1..s11 sin salvarlos (violan la ABI) ->
     * si mcycle_ini viviera en s1, lo corromperian y T saldria basura. t0/t1 son
     * caller-saved (no hace falta que sobrevivan al call). */
    csrr t0, mcycle
    la   t1, mcyc_ini
    sw   t0, 0(t1)

    call run_workload        /* el programa real (puede pisar cualquier s-reg) */

    csrr s2, mcycle          /* mcycle_fin: leido DESPUES del call, sin call despues -> seguro */
    gpio_low

    la   t1, mcyc_ini
    lw   s1, 0(t1)           /* recupera mcycle_ini para dump_counters */
    dump_counters            /* 28 CSR + s1/s2 -> results */

finished:
    ebreak
    wfi
    j finished

trap_handler:
    li t0, GPIO_CLEAR0
    li t1, GPIO08_BIT
    sw t1, 0(t0)
    la t2, results
    li t3, 0xBAD00BAD
    sw t3, 0(t2)
    csrr t3, mcause
    sw t3, 4(t2)
    csrr t3, mepc
    sw t3, 8(t2)
    ebreak
    j trap_handler

    .option pop
.size _start, .-_start

.section .bss
.align 8
.globl results
results:
    .space 128
.align 4
mcyc_ini:
    .space 4
