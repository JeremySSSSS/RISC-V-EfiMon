/* Logistic seguro para validacion HW: el estado pseudoaleatorio se mantiene en
 * entero y selecciona operaciones FP independientes sobre operandos frescos.
 */
#ifndef REPS
#define REPS 20000
#endif
#define N 256

.section .data
.align 4
va:
    .rept N
    .word 0x3f000000
    .endr
vb:
    .rept N
    .word 0x4079999a
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
    li t5, 0x2545F491

    li s0, REPS
1:
    la t1, va
    la t2, vb
    la t3, vout
    li t4, N
2:
    slli t6, t5, 13
    xor  t5, t5, t6
    srli t6, t5, 17
    xor  t5, t5, t6
    slli t6, t5, 5
    xor  t5, t5, t6

    flw ft2, 0(t1)
    flw ft3, 0(t2)
    andi a0, t5, 1
    beqz a0, 3f
    fmul.s ft4, ft2, ft3
    j 4f
3:
    fadd.s ft4, ft2, ft3
4:
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
