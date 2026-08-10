// M1 - bucle dominado CTRL, footprint PARAMETRIZABLE (fetch/i-cache) + call/ret.
// El costo real de una transferencia de control TOMADA en el CV32E40P es el flush
// del fetch (~3 ciclos) MAS el refill de i-cache si el target no esta en cache.
// Ese refill depende del FOOTPRINT del codigo: un lazo chico cabe en la i-cache
// (solo flush -> subestima ~5.35 nJ); uno que desborda la i-cache re-busca desde
// L2 en cada pasada (flush + miss -> sobreestima). El punto "real" es el que
// reproduce el miss-rate de i-cache del codigo de validacion branchy.
//
// COMO USARLO: barrer FOOTPRINT_KB en el banco (p.ej. 4, 8, 16, 32, 64) y quedarse
// con el que MINIMIZA el error de M1 sobre los benchmarks ctrl-pesados (fsm, gcd).
//   make ../elf/ctrl.elf FOOTPRINT_KB=8  LOOP_COUNT=20000
// Reajustar LOOP_COUNT para ventana ~40 s (mas footprint -> mas ciclos/iter).
//
// Composicion: cada GROUP = 5 transferencias TOMADAS (los "victim" ALU tras cada
// salto se buscan y se descartan por el flush: NO retiran). Cada bloque agrega un
// jal+ret (patron call/return, redireccion por jalr). ctrl domina >96% de lo
// retirado (solo 4 updates ALU por bloque mantienen vivos los operandos).
#include "platform.inc"

#ifndef FOOTPRINT_KB
#define FOOTPRINT_KB 16                 // ~2-4x la i-cache del FC (barrer en banco)
#endif
#ifndef LOOP_COUNT
#define LOOP_COUNT 20000                // tune ~40 s en banco (depende del footprint)
#endif
#define GROUPS_PER_BLOCK 24
#define BLOCK_BYTES (20 + GROUPS_PER_BLOCK*44)   // 4 updates + jal + 24 grupos (11 instr)
#define FP_BLOCKS ((FOOTPRINT_KB*1024)/BLOCK_BYTES)

// Un GROUP: 5 saltos SIEMPRE tomados; cada uno salta sobre su "victim" (fetch
// perdido). Etiquetas unicas por \@ para desenrollar sin colisiones.
.macro CGROUP
    bne  t0, t1, .Lg1_\@
    xor  a0, t0, t1
.Lg1_\@:
    blt  t2, t3, .Lg2_\@
    add  a1, t2, t3
    sub  a2, t3, t2
.Lg2_\@:
    bgeu t1, t0, .Lg3_\@
    and  a3, t0, t2
.Lg3_\@:
    j    .Lg4_\@
    or   a4, t1, t3
.Lg4_\@:
    bne  t3, t2, .Lg5_\@
    xor  a5, t2, t3
.Lg5_\@:
.endm

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
    li s0, LOOP_COUNT

    gpio_high
    li t0, 0x100
    li t1, 0x101
    li t2, 0x80001111               // negativo con signo, enorme sin signo
    li t3, 0x00000F0F               // pequeno positivo

    csrr s1, mcycle
measurement_loop:
    .rept FP_BLOCKS
    addi t0, t0, 2                  // mantienen t1-t0=1 (bne/bgeu tomados),
    addi t1, t1, 2                  // t2<0<t3 (blt/bne tomados)
    addi t3, t3, 2
    xori t2, t2, 0x5A5
    .rept GROUPS_PER_BLOCK
    CGROUP
    .endr
    jal  ra, ctrl_sub              // call (ctrl) -> dentro ret (jalr, ctrl)
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

// subrutina: 2 branches tomados + ret (patron call/return)
ctrl_sub:
    bne  t0, t1, .Ls1
    nop
.Ls1:
    bltu t3, t2, .Ls2
    nop
.Ls2:
    ret

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
