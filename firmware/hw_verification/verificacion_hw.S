// Verificacion funcional en hardware: un solo programa mixto.
// Replica la idea de clasif_rand.c de simulacion (mezcla pseudoaleatoria de
// categorias), pero agrega FLOAT porque en el bitstream real la FPU esta activa.
// La ventana completa reinicia una sola vez los CSR y produce un unico
// results[30] con la composicion global del programa.
#include "platform.inc"

.equ ITERS, 1500
.equ SEED,  0xC0FFEE01

.macro xorshift reg tmp
    slli \tmp, \reg, 13
    xor  \reg, \reg, \tmp
    srli \tmp, \reg, 17
    xor  \reg, \reg, \tmp
    slli \tmp, \reg, 5
    xor  \reg, \reg, \tmp
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
    csrci 0x320, 1                  // habilita mcycle

    // FPU habilitada para cubrir la categoria que no entra en simulacion.
    li t0, 0x6000
    csrs mstatus, t0
    la t0, float_words
    flw ft0, 0(t0)
    flw ft1, 4(t0)
    flw ft2, 8(t0)
    flw ft3, 12(t0)
    flw ft4, 16(t0)
    flw ft5, 20(t0)

    li s0, ITERS                    // iteraciones de la regresion mixta
    li s5, SEED                     // estado pseudoaleatorio reproducible
    la s6, data_words

    reset_category_counters
    csrr s1, mcycle

main_loop:
    // Equivalente bare-metal a xorshift32(&rng), tres veces.
    xorshift s5, t6
    mv s7, s5                       // r: selecciona categoria
    xorshift s5, t6
    mv s8, s5                       // a
    xorshift s5, t6
    ori s9, s5, 1                   // b: divisor no nulo

    // r % 13 sin llamar a runtime: remu tambien cuenta como DIV, igual que el
    // codigo C de simulacion incluye el costo real del despachador.
    li t0, 13
    remu t1, s7, t0

    beqz t1, case_alu
    li t0, 1
    beq t1, t0, case_mul
    li t0, 2
    beq t1, t0, case_mulh
    li t0, 3
    beq t1, t0, case_div
    li t0, 4
    beq t1, t0, case_mem
    li t0, 5
    beq t1, t0, case_ctrl
    li t0, 6
    beq t1, t0, case_fp_add
    li t0, 7
    beq t1, t0, case_fp_mul
    li t0, 8
    beq t1, t0, case_fp_fma
    li t0, 9
    beq t1, t0, case_fp_div
    li t0, 10
    beq t1, t0, case_fp_sqrt
    li t0, 11
    beq t1, t0, case_fp_noncomp
    j case_fp_conv

case_alu:
    add  t0, s8, s9
    xor  t1, t0, s8
    slli t2, t1, 3
    sltu t3, t2, s9
    j case_done

case_mul:
    mul t0, s8, s9
    mul t1, t0, s8
    mul t2, t1, s9
    j case_done

case_mulh:
    mulh   t0, s8, s9
    mulhu  t1, s8, s9
    mulhsu t2, s8, s9
    j case_done

case_div:
    div  t0, s8, s9
    remu t1, s8, s9
    j case_done

case_mem:
    sw s8, 0(s6)
    sw s9, 4(s6)
    lw t0, 0(s6)
    lw t1, 4(s6)
    j case_done

case_ctrl:
    andi t0, s7, 1
    beqz t0, 1f
    addi t1, zero, 7
1:
    j case_done

case_fp_add:
    fadd.s ft10, ft0, ft1
    fsub.s ft11, ft2, ft3
    j case_done

case_fp_mul:
    fmul.s ft10, ft0, ft1
    fmul.s ft11, ft2, ft3
    j case_done

case_fp_fma:
    fmadd.s ft10, ft0, ft1, ft2
    fnmsub.s ft11, ft1, ft2, ft3
    j case_done

case_fp_div:
    fdiv.s ft10, ft0, ft1
    fdiv.s ft11, ft2, ft3
    j case_done

case_fp_sqrt:
    fsqrt.s ft10, ft0
    fsqrt.s ft11, ft2
    j case_done

case_fp_noncomp:
    fmin.s ft10, ft0, ft1
    fmax.s ft11, ft2, ft3
    fsgnj.s ft10, ft0, ft1
    feq.s t0, ft2, ft3
    j case_done

case_fp_conv:
    fcvt.s.w ft10, s8
    fcvt.w.s t0, ft0
    j case_done

case_done:
    addi s0, s0, -1
    bnez s0, main_loop

    csrr s2, mcycle
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
.align 4
data_words:
    .space 32

.section .data
.align 4
float_words:
    .float 1.1234567
    .float 1.7654321
    .float 1.3141593
    .float 1.9182736
    .float 1.5556667
    .float 1.2468013
