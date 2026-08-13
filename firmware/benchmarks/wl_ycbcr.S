/* YCBCR seguro para validacion HW: perfil float+mem basado en el patron que
 * termina robustamente en la FPGA. Representa luminancia simplificada con
 * operandos frescos y operaciones FP independientes.
 */
#ifndef REPS
#define REPS 20000
#endif
#define N 256

.section .data
.align 4
vr:
    .rept N
    .word 0x3f800000
    .endr
vg:
    .rept N
    .word 0x3f000000
    .endr

.section .bss
.align 4
luma:
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
    la t1, vr
    la t2, vg
    la t3, luma
    li t4, N
2:
    flw ft2, 0(t1)
    flw ft3, 0(t2)
    fadd.s ft4, ft2, ft3
    fsw ft4, 0(t3)
    fmul.s ft4, ft2, ft3
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
