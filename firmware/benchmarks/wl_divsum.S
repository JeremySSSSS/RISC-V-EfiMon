/* Suma de cocientes/restos N/i y M/i para i=1..K: perfil DIV dominante
 * (divu + remu, ambos categoria DIV, con divisor VARIABLE que ademas ejercita
 * las latencias del divisor serial). Distinta de primes (division de prueba
 * para primalidad) y de gcd/modpow/trialdiv/radix de calibracion. */
#ifndef REPS
#define REPS 42000
#endif
#define KMAX 96

.section .text
.globl run_workload
.type run_workload, @function
run_workload:
    .option push
    .option norvc

    li   s0, REPS
    li   s7, 0x00BC614E      /* N */
    li   s8, 0x0098967F      /* M */
    li   s9, 0               /* acumulador */
    li   s2, KMAX
1:
    li   s1, 1               /* i = 1 */
2:
    divu t2, s7, s1          /* N / i */
    remu t3, s7, s1          /* N % i */
    divu t4, s8, s1          /* M / i */
    remu t5, s8, s1          /* M % i */
    add  s9, s9, t2          /* alu */
    add  s9, s9, t4          /* alu */
    addi s1, s1, 1           /* alu: i++ */
    blt  s1, s2, 2b          /* ctrl (tomado casi siempre) */
    addi s0, s0, -1
    bnez s0, 1b

    .option pop
    ret
.size run_workload, .-run_workload
