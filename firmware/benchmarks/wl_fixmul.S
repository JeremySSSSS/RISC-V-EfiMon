/* Producto punto-fijo Q31 en assembly: perfil MUL + MULH + ALU.
 * (a*b)>>32 requiere mulh; unico benchmark que ejercita MULH, la categoria
 * de soporte mas debil en la calibracion por regresion. */
#ifndef REPS
#define REPS 450000
#endif

.section .text
.globl run_workload
.type run_workload, @function
run_workload:
    .option push
    .option norvc

    li t0, 0x40000001       /* ~0.5 en Q31 */
    li t1, 0x2AAAAAAB       /* ~0.333 en Q31 */
    li s0, REPS
1:
    .rept 32
    mul  t2, t0, t1         /* parte baja */
    mulh t3, t0, t1         /* parte alta = resultado Q31 */
    add  t4, t3, t2
    addi t0, t0, 1          /* varia operandos */
    .endr
    addi s0, s0, -1
    bnez s0, 1b

    .option pop
    ret
.size run_workload, .-run_workload
