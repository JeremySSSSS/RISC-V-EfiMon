/* Producto ancho 64-bit: perfil MULH dominante. Usa las tres variantes de
 * multiplicacion alta (mulh/mulhu/mulhsu, todas categoria MULH) sin mul, para
 * reforzar la categoria de soporte mas debil. Distinta de fixmul (Q31, con
 * mul) y de los nucleos de calibracion mulhash64/mulhscale. */
#ifndef REPS
#define REPS 900000
#endif

.section .text
.globl run_workload
.type run_workload, @function
run_workload:
    .option push
    .option norvc

    li   t0, 0x9E3779B1      /* operandos que varian */
    li   t1, 0x7F4A7C15
    li   s0, REPS
1:
    .rept 16
    mulh   t2, t0, t1        /* alta con signo   */
    mulhu  t3, t0, t1        /* alta sin signo   */
    mulhsu t4, t0, t1        /* mixta            */
    add    t5, t2, t3        /* alu: combina     */
    xor    t0, t4, t5        /* alu: varia t0    */
    .endr
    addi s0, s0, -1
    bnez s0, 1b

    .option pop
    ret
.size run_workload, .-run_workload
