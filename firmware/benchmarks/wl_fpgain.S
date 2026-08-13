/* FLOAT intenso pero seguro: operandos frescos desde memoria y operaciones FP
 * independientes. Evita rafagas FP puras, que en este bitstream no terminan
 * de forma fiable dentro del harness de validacion.
 */
#ifndef REPS
#define REPS 20000
#endif
#define N 256

.section .data
.align 4
va:
    .rept N
    .word 0x3f8fcd6f
    .endr
vb:
    .rept N
    .word 0x400ccccd
    .endr

.section .bss
.align 4
vout:
    .space N*4

.section .text
.globl run_workload
.type run_workload, @function
run_workload:
    .option push
    .option norvc

    li t0, 0x6000
    csrs mstatus, t0

    li s0, REPS
1:
    la t1, va
    la t2, vb
    la t3, vout
    li t4, N
2:
    flw ft2, 0(t1)
    flw ft3, 0(t2)
    fadd.s ft4, ft2, ft3
    fsw ft4, 0(t3)
    fmul.s ft4, ft2, ft3
    fsw ft4, 0(t3)
    fsub.s ft4, ft3, ft2
    fsw ft4, 0(t3)
    addi t1, t1, 4
    addi t2, t2, 4
    addi t3, t3, 4
    addi t4, t4, -1
    bnez t4, 2b
    addi s0, s0, -1
    bnez s0, 1b

    .option pop
    ret
.size run_workload, .-run_workload
