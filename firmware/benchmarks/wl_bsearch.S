/* Busqueda binaria en assembly: perfil CTRL dominante (saltos data-dependent
 * impredecibles via xorshift) + MEM + ALU. Cubre la validacion de e_ctrl,
 * colineal en la calibracion por regresion. */
#ifndef REPS
#define REPS 1200000
#endif
#define N 64                  /* tabla ordenada: 0,2,4,...,126 */

.section .data
.align 4
tabla:
    .set v, 0
    .rept N
    .word v
    .set v, v+2
    .endr

.section .text
.globl run_workload
.type run_workload, @function
run_workload:
    .option push
    .option norvc

    la t0, tabla
    li t1, 0x2545F491         /* semilla xorshift */
    li s0, REPS
1:
    /* xorshift32 -> objetivo en [0,127] */
    slli t2, t1, 13
    xor  t1, t1, t2
    srli t2, t1, 17
    xor  t1, t1, t2
    slli t2, t1, 5
    xor  t1, t1, t2
    andi t3, t1, 127          /* objetivo */

    li t4, 0                  /* lo */
    li t5, N-1                /* hi */
2:
    bgt t4, t5, 4f            /* no encontrado */
    add t6, t4, t5
    srli t6, t6, 1            /* mid */
    slli t2, t6, 2
    add t2, t0, t2
    lw  t2, 0(t2)             /* tabla[mid] */
    beq t2, t3, 4f            /* encontrado */
    blt t2, t3, 3f
    addi t5, t6, -1           /* hi = mid-1 */
    j 2b
3:
    addi t4, t6, 1            /* lo = mid+1 */
    j 2b
4:
    addi s0, s0, -1
    bnez s0, 1b

    .option pop
    ret
.size run_workload, .-run_workload
