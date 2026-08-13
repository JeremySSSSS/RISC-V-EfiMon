/* bitcount en assembly: Kernighan, ALU + CTRL + MEM. */
#ifndef REPS
#define REPS 5000
#endif
#define N 1024
#include "platform.inc"

.section .data
.align 4
data:
    .rept N
    .word 0xdeadbeef
    .endr

.section .text
.globl run_workload
.type run_workload, @function
run_workload:
    .option push
    .option norvc
    li t0, 0x6000
    csrs mstatus, t0
    la t1, data
    li t2, REPS
rep_loop:
    la t1, data
    li s0, 0
    li s1, 0
word_loop:
    lw s2, 0(t1)
    li s3, 0
bit_loop:
    beqz s2, done_bits
    addi s4, s2, -1
    and s2, s2, s4
    addi s3, s3, 1
    j bit_loop
done_bits:
    add s0, s0, s3
    addi t1, t1, 4
    addi s1, s1, 1
    li s5, N
    blt s1, s5, word_loop
    addi t2, t2, -1
    bnez t2, rep_loop
    .option pop
    ret
