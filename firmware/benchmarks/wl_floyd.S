/* Floyd-Warshall simplificado en assembly: ALU + MEM + CTRL. */
#ifndef REPS
#define REPS 400
#endif
#define N 16
#include "platform.inc"

.section .data
.align 4
dist:
    .rept (N*N)
    .word 1000
    .endr

.section .text
.globl run_workload
.type run_workload, @function
run_workload:
    .option push
    .option norvc
    li t0, 0x6000
    csrs mstatus, t0
    la t1, dist
    li t2, REPS
rep_loop:
    li s0, 0
k_loop:
    li s1, 0
i_loop:
    li s2, 0
j_loop:
    /* dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]) */
    slli s3, s0, 4
    add s3, s3, s1
    slli s3, s3, 2
    add s4, t1, s3
    slli s5, s0, 4
    add s5, s5, s2
    slli s5, s5, 2
    add s6, t1, s5
    slli s7, s2, 4
    add s7, s7, s1
    slli s7, s7, 2
    add s8, t1, s7
    lw a0, 0(s4)
    lw a1, 0(s6)
    lw a2, 0(s8)
    add a1, a1, a2
    blt a1, a0, update
    j no_update
update:
    sw a1, 0(s4)
no_update:
    addi s2, s2, 1
    li s9, N
    blt s2, s9, j_loop
    addi s1, s1, 1
    li s9, N
    blt s1, s9, i_loop
    addi s0, s0, 1
    li s9, N
    blt s0, s9, k_loop
    addi t2, t2, -1
    bnez t2, rep_loop
    .option pop
    ret
