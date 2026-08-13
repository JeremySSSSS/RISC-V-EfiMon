/* Escalado en sitio de un arreglo: perfil BALANCEADO, ninguna categoria
 * domina (alu, mem y mul repartidos, con ctrl del lazo). Rompe la dominancia
 * de alu tipica del codigo entero para probar el modelo fuera de ese regimen. */
#ifndef REPS
#define REPS 200000
#endif
#define N 256
#include "platform.inc"

.section .data
.align 4
buf:
    .rept N
    .word 3
    .endr

.section .text
.globl run_workload
.type run_workload, @function
run_workload:
    .option push
    .option norvc

    li   t6, REPS
rep_loop:
    la   t0, buf
    la   t1, buf + N*4
    li   t4, 0x01000193     /* multiplicador */
scan:
    lw   t2, 0(t0)          /* mem: carga    */
    mul  t3, t2, t4         /* mul           */
    add  t4, t4, t3         /* alu: varia    */
    sw   t3, 0(t0)          /* mem: guarda   */
    addi t0, t0, 4          /* alu: avanza   */
    bltu t0, t1, scan       /* ctrl          */
    addi t6, t6, -1
    bnez t6, rep_loop

    .option pop
    ret
.size run_workload, .-run_workload
