/* Conteo de primos por division de prueba en assembly: DIV/REM + MUL + CTRL. */
#ifndef REPS
#define REPS 60
#endif
#define LIMIT 3000
#include "platform.inc"

.section .text
.globl run_workload
.type run_workload, @function
run_workload:
    .option push
    .option norvc
    li t0, 0x6000
    csrs mstatus, t0
    li t1, REPS
rep_loop:
    li s0, 0
    li s1, 2
n_loop:
    li s2, 1
    li s3, 2
d_loop:
    mul s4, s3, s3
    blt s1, s4, prime_done
    rem s5, s1, s3
    beqz s5, not_prime
    addi s3, s3, 1
    j d_loop
not_prime:
    li s2, 0
prime_done:
    add s0, s0, s2
    addi s1, s1, 1
    li s6, LIMIT
    blt s1, s6, n_loop
    addi t1, t1, -1
    bnez t1, rep_loop
    .option pop
    ret
