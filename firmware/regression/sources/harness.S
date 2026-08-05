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

    gpio_init
    csrci 0x320, 1            /* habilita mcycle */
#ifdef CHUNKS
    enable_timer_wakeup       /* wfi con despertar por timer (modo duty) */
#endif

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

#ifdef CHUNKS
    /* Modo DUTY (barrido de intensidad estilo EfiMon): el kernel corre en
     * CHUNKS tandas con SLEEP_TICKS de wfi entre ellas. Misma composicion de
     * instrucciones (el kernel se compila con REPS/CHUNKS y se llama CHUNKS
     * veces), intensidad efectiva menor. El contador de tandas vive en
     * MEMORIA: los kernels pueden pisar cualquier registro. */
    li   t0, CHUNKS
    la   t1, chunk_cnt
    sw   t0, 0(t1)
chunk_loop:
    call run_workload
    wfi_idle SLEEP_TICKS
    la   t1, chunk_cnt
    lw   t0, 0(t1)
    addi t0, t0, -1
    sw   t0, 0(t1)
    bnez t0, chunk_loop
#else
    call run_workload        /* el programa real (puede pisar cualquier s-reg) */
#endif

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
    ebreak
    j trap_handler

    .option pop
.size _start, .-_start

.section .bss
.align 8
.globl results
results:
    .space 120
.align 4
mcyc_ini:
    .space 4
.align 4
chunk_cnt:
    .space 4
