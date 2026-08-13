/* SHA-256 en assembly: perfil ALU/shift + MEM + CTRL, sin C. */
#ifndef REPS
#define REPS 70000
#endif

#include "platform.inc"

.section .data
.align 4
sha_msg:
    .word 0x61626380, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x00000180
sha_k:
    .word 0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5
    .word 0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174
    .word 0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da
    .word 0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967
    .word 0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85
    .word 0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070
    .word 0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3
    .word 0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
sha_h:
    .word 0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19

.section .text
.globl run_workload
.type run_workload, @function
run_workload:
    .option push
    .option norvc
    li t0, 0x6000
    csrs mstatus, t0
    la t2, sha_k
    la t3, sha_h
    la t4, sha_msg
    li t5, REPS
rep_loop:
    la t1, sha_msg
    lw a0, 0(t3); lw a1, 4(t3); lw a2, 8(t3); lw a3, 12(t3)
    lw a4, 16(t3); lw a5, 20(t3); lw a6, 24(t3); lw a7, 28(t3)
    li s0, 0
round_loop:
    slli s1, s0, 2
    add s2, t2, s1
    lw s3, 0(s2)
    lw s4, 0(t1)
    srli s5, a4, 6
    srli s6, a4, 11
    xor s5, s5, s6
    srli s6, a4, 25
    xor s5, s5, s6
    and s6, a4, a5
    not s7, a4
    and s7, s7, a6
    xor s6, s6, s7
    add s8, a7, s5
    add s8, s8, s6
    add s8, s8, s3
    add s8, s8, s4

    srli s5, a0, 2
    srli s6, a0, 13
    xor s5, s5, s6
    srli s6, a0, 22
    xor s5, s5, s6
    and s6, a0, a1
    and s7, a0, a2
    xor s6, s6, s7
    and s7, a1, a2
    xor s6, s6, s7
    add s9, s5, s6

    add a7, a6, zero
    add a6, a5, zero
    add a5, a4, zero
    add a4, a3, s8
    add a3, a2, zero
    add a2, a1, zero
    add a1, a0, zero
    add a0, s8, s9

    addi t1, t1, 4
    addi s0, s0, 1
    li s10, 16
    blt s0, s10, round_loop
    sw a0, 0(t3); sw a1, 4(t3); sw a2, 8(t3); sw a3, 12(t3)
    sw a4, 16(t3); sw a5, 20(t3); sw a6, 24(t3); sw a7, 28(t3)
    addi t5, t5, -1
    bnez t5, rep_loop
    .option pop
    ret
