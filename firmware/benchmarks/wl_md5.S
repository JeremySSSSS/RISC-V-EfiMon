/* MD5 en assembly: perfil ALU/logica + rotaciones + MEM + CTRL, sin C. */
#ifndef REPS
#define REPS 120000
#endif
#include "platform.inc"

.section .data
.align 4
md5_m:
    .word 0x67452301,0xefcdab89,0x98badcfe,0x10325476,0,0,0,0,0,0,0,0,0,0,0,0
md5_k:
    .word 0xd76aa478,0xe8c7b756,0x242070db,0xc1bdceee,0xf57c0faf,0x4787c62a,0xa8304613,0xfd469501
    .word 0x698098d8,0x8b44f7af,0xffff5bb1,0x895cd7be,0x6b901122,0xfd987193,0xa679438e,0x49b40821
    .word 0xf61e2562,0xc040b340,0x265e5a51,0xe9b6c7aa,0xd62f105d,0x02441453,0xd8a1e681,0xe7d3fbc8
    .word 0x21e1cde6,0xc33707d6,0xf4d50d87,0x455a14ed,0xa9e3e905,0xfcefa3f8,0x676f02d9,0x8d2a4c8a
    .word 0xfffa3942,0x8771f681,0x6d9d6122,0xfde5380c,0xa4beea44,0x4bdecfa9,0xf6bb4b60,0xbebfbc70
    .word 0x289b7ec6,0xeaa127fa,0xd4ef3085,0x04881d05,0xd9d4d039,0xe6db99e5,0x1fa27cf8,0xc4ac5665
    .word 0xf4292244,0x432aff97,0xab9423a7,0xfc93a039,0x655b59c3,0x8f0ccc92,0xffeff47d,0x85845dd1
    .word 0x6fa87e4f,0xfe2ce6e0,0xa3014314,0x4e0811a1,0xf7537e82,0xbd3af235,0x2ad7d2bb,0xeb86d391
md5_s:
    .byte 7,12,17,22, 7,12,17,22, 7,12,17,22, 7,12,17,22
    .byte 5,9,14,20, 5,9,14,20, 5,9,14,20, 5,9,14,20
    .byte 4,11,16,23, 4,11,16,23, 4,11,16,23, 4,11,16,23
    .byte 6,10,15,21, 6,10,15,21, 6,10,15,21, 6,10,15,21

.section .text
.globl run_workload
.type run_workload, @function
run_workload:
    .option push
    .option norvc
    li t0, 0x6000
    csrs mstatus, t0
    la t1, md5_m
    la t2, md5_k
    la t3, md5_s
    li t4, REPS
rep_loop:
    lw a0, 0(t1); lw a1, 4(t1); lw a2, 8(t1); lw a3, 12(t1)
    li t5, 0
round_loop:
    /* mezcla de las 4 funciones MD5; un solo bloque de 64 rondas */
    sltiu t6, t5, 16
    bnez t6, round_0_15
    sltiu t6, t5, 32
    bnez t6, round_16_31
    sltiu t6, t5, 48
    bnez t6, round_32_47
    j round_48_63
round_0_15:
    and t6, a1, a2
    not s0, a1
    and s0, s0, a3
    or t6, t6, s0
    mv s1, t5
    j do_round
round_16_31:
    and t6, a3, a1
    not s0, a3
    and s0, s0, a2
    or t6, t6, s0
    slli s1, t5, 2
    addi s1, s1, 1
    andi s1, s1, 15
    j do_round
round_32_47:
    xor t6, a1, a2
    xor t6, t6, a3
    slli s1, t5, 1
    addi s1, s1, 5
    andi s1, s1, 15
    j do_round
round_48_63:
    or t6, a1, a3
    not s0, a3
    xor t6, a2, t6
    xor t6, t6, s0
    slli s1, t5, 3
    andi s1, s1, 15
do_round:
    slli s0, t5, 2
    add s2, t2, s0
    lw s3, 0(s2)
    add s4, a0, t6
    add s4, s4, s3
    add s4, s4, t5
    lbu s5, 0(t3)
    sll s7, s4, s5
    li s6, 32
    sub s6, s6, s5
    srl s8, s4, s6
    or s4, s7, s8
    add a0, a3, zero
    add a3, a2, zero
    add a2, a1, zero
    add a1, a1, s4
    add t1, t1, zero
    addi t5, t5, 1
    li s6, 64
    bne t5, s6, round_loop
    sw a0, 0(t1); sw a1, 4(t1); sw a2, 8(t1); sw a3, 12(t1)
    addi t4, t4, -1
    bnez t4, rep_loop
    .option pop
    ret
