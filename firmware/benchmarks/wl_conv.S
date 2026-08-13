/* Convolucion 1D en assembly: perfil MUL + MEM + CTRL. */
#ifndef REPS
#define REPS 22000
#endif
#define N 512
#define K 16
#include "platform.inc"

.section .data
.align 4
sig:
    .rept N
    .word 1
    .endr
kern:
    .rept K
    .word 2
    .endr
out:
    .rept N
    .word 0
    .endr

.section .text
.globl run_workload
.type run_workload, @function
run_workload:
    .option push
    .option norvc
    li t0, 0x6000
    csrs mstatus, t0
    la t1, sig
    la t2, kern
    la t3, out
    li t4, REPS
rep_loop:
    li s0, 0                  /* i */
outer_i:
    li s1, 0                  /* k */
    li s2, 0                  /* acc */
inner_k:
    add s3, s0, s1
    slli s3, s3, 2
    add s4, t1, s3
    slli s5, s1, 2
    add s6, t2, s5
    lw s7, 0(s4)
    lw s8, 0(s6)
    mul s9, s7, s8
    add s2, s2, s9
    addi s1, s1, 1
    li s10, K
    blt s1, s10, inner_k
    slli s3, s0, 2
    add s4, t3, s3
    sw s2, 0(s4)
    addi s0, s0, 1
    li s10, N-K
    blt s0, s10, outer_i
    addi t4, t4, -1
    bnez t4, rep_loop
    .option pop
    ret
