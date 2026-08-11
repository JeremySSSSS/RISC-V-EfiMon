.equ GPIO_MODE0,      0x1A101008
.equ GPIO_SET0,       0x1A101200
.equ GPIO_CLEAR0,     0x1A101280
.equ PAD_IO08_CFG,     0x1A121044
.equ PAD_IO08_MUX,     0x1A121048
.equ PAD_IO09_CFG,     0x1A12104C
.equ PAD_IO09_MUX,     0x1A121050
.equ PAD_IO10_CFG,     0x1A121054
.equ PAD_IO10_MUX,     0x1A121058
.equ PAD_IO11_CFG,     0x1A12105C
.equ PAD_IO11_MUX,     0x1A121060

.equ GPIO08_BIT,       (1 << 8)
.equ GPIO08_MODE_OUT,  (1 << 16)
.equ LED_BITS,         ((1 << 9) | (1 << 10) | (1 << 11))
.equ LED_MODE_OUT,     ((1 << 18) | (1 << 20) | (1 << 22))
.equ PAD_IO08_GPIO,    14
.equ PAD_IO09_GPIO,    14
.equ PAD_IO10_GPIO,    14
.equ PAD_IO11_GPIO,    14
.equ PAD_CFG_OUTPUT,   ((1 << 3) | (1 << 0))

# Clasificador v3: 14 contadores de 64 bits (pares LO/HI).
# FLW/FSW cuentan en MEM; las operaciones de la FPU tienen contador propio.
.equ CSR_CAT_ALU_LO,    0xBC0
.equ CSR_CAT_ALU_HI,    0xBC1
.equ CSR_CAT_MUL_LO,    0xBC2
.equ CSR_CAT_MUL_HI,    0xBC3
.equ CSR_CAT_MULH_LO,   0xBC4
.equ CSR_CAT_MULH_HI,   0xBC5
.equ CSR_CAT_DIV_LO,    0xBC6
.equ CSR_CAT_DIV_HI,    0xBC7
.equ CSR_CAT_MEM_LO,    0xBC8
.equ CSR_CAT_MEM_HI,    0xBC9
.equ CSR_CAT_CTRL_LO,   0xBCA
.equ CSR_CAT_CTRL_HI,   0xBCB
.equ CSR_CAT_FP_ADD_LO,     0xBCC
.equ CSR_CAT_FP_ADD_HI,     0xBCD
.equ CSR_CAT_FP_MUL_LO,     0xBCE
.equ CSR_CAT_FP_MUL_HI,     0xBCF
.equ CSR_CAT_FP_FMA_LO,     0xBD0
.equ CSR_CAT_FP_FMA_HI,     0xBD1
.equ CSR_CAT_FP_DIV_LO,     0xBD2
.equ CSR_CAT_FP_DIV_HI,     0xBD3
.equ CSR_CAT_FP_SQRT_LO,    0xBD4
.equ CSR_CAT_FP_SQRT_HI,    0xBD5
.equ CSR_CAT_FP_NONCOMP_LO, 0xBD6
.equ CSR_CAT_FP_NONCOMP_HI, 0xBD7
.equ CSR_CAT_FP_CONV_LO,    0xBD8
.equ CSR_CAT_FP_CONV_HI,    0xBD9
.equ CSR_CAT_DIVCYC_LO,     0xBDA
.equ CSR_CAT_DIVCYC_HI,     0xBDB
.equ CSR_CAT_FETCH_LO,   0xBDC
.equ CSR_CAT_FETCH_HI,   0xBDD

.macro gpio_init
    li t0, PAD_IO08_MUX
    li t1, PAD_IO08_GPIO
    sw t1, 0(t0)

    li t0, PAD_IO08_CFG
    li t1, PAD_CFG_OUTPUT
    sw t1, 0(t0)

    li t0, GPIO_MODE0
    li t1, GPIO08_MODE_OUT
    sw t1, 0(t0)

    li t0, GPIO_CLEAR0
    li t1, GPIO08_BIT
    sw t1, 0(t0)
.endm

.macro gpio_high
    li t0, GPIO_SET0
    li t1, GPIO08_BIT
    sw t1, 0(t0)
.endm

.macro gpio_low
    li t0, GPIO_CLEAR0
    li t1, GPIO08_BIT
    sw t1, 0(t0)
.endm

# Reset de los 28 CSR del clasificador v3.
.macro reset_category_counters
    csrw CSR_CAT_ALU_LO, zero
    csrw CSR_CAT_ALU_HI, zero
    csrw CSR_CAT_MUL_LO, zero
    csrw CSR_CAT_MUL_HI, zero
    csrw CSR_CAT_MULH_LO, zero
    csrw CSR_CAT_MULH_HI, zero
    csrw CSR_CAT_DIV_LO, zero
    csrw CSR_CAT_DIV_HI, zero
    csrw CSR_CAT_MEM_LO, zero
    csrw CSR_CAT_MEM_HI, zero
    csrw CSR_CAT_CTRL_LO, zero
    csrw CSR_CAT_CTRL_HI, zero
    csrw CSR_CAT_FP_ADD_LO, zero
    csrw CSR_CAT_FP_ADD_HI, zero
    csrw CSR_CAT_FP_MUL_LO, zero
    csrw CSR_CAT_FP_MUL_HI, zero
    csrw CSR_CAT_FP_FMA_LO, zero
    csrw CSR_CAT_FP_FMA_HI, zero
    csrw CSR_CAT_FP_DIV_LO, zero
    csrw CSR_CAT_FP_DIV_HI, zero
    csrw CSR_CAT_FP_SQRT_LO, zero
    csrw CSR_CAT_FP_SQRT_HI, zero
    csrw CSR_CAT_FP_NONCOMP_LO, zero
    csrw CSR_CAT_FP_NONCOMP_HI, zero
    csrw CSR_CAT_FP_CONV_LO, zero
    csrw CSR_CAT_FP_CONV_HI, zero
    csrw CSR_CAT_DIVCYC_LO, zero
    csrw CSR_CAT_DIVCYC_HI, zero
    csrw CSR_CAT_FETCH_LO, zero
    csrw CSR_CAT_FETCH_HI, zero
.endm

# Lee los 28 CSR y los vuelca a 'results' junto con mcycle ini/fin (s1/s2).
# results = 30 words: [28 CSR en orden 0xBC0..0xBDB][mcycle_ini][mcycle_fin]
.macro dump_counters
    la   s4, results
    csrr t0, CSR_CAT_ALU_LO;        sw t0,   0(s4)
    csrr t0, CSR_CAT_ALU_HI;        sw t0,   4(s4)
    csrr t0, CSR_CAT_MUL_LO;        sw t0,   8(s4)
    csrr t0, CSR_CAT_MUL_HI;        sw t0,  12(s4)
    csrr t0, CSR_CAT_MULH_LO;       sw t0,  16(s4)
    csrr t0, CSR_CAT_MULH_HI;       sw t0,  20(s4)
    csrr t0, CSR_CAT_DIV_LO;        sw t0,  24(s4)
    csrr t0, CSR_CAT_DIV_HI;        sw t0,  28(s4)
    csrr t0, CSR_CAT_MEM_LO;        sw t0,  32(s4)
    csrr t0, CSR_CAT_MEM_HI;        sw t0,  36(s4)
    csrr t0, CSR_CAT_CTRL_LO;       sw t0,  40(s4)
    csrr t0, CSR_CAT_CTRL_HI;       sw t0,  44(s4)
    csrr t0, CSR_CAT_FP_ADD_LO;     sw t0,  48(s4)
    csrr t0, CSR_CAT_FP_ADD_HI;     sw t0,  52(s4)
    csrr t0, CSR_CAT_FP_MUL_LO;     sw t0,  56(s4)
    csrr t0, CSR_CAT_FP_MUL_HI;     sw t0,  60(s4)
    csrr t0, CSR_CAT_FP_FMA_LO;     sw t0,  64(s4)
    csrr t0, CSR_CAT_FP_FMA_HI;     sw t0,  68(s4)
    csrr t0, CSR_CAT_FP_DIV_LO;     sw t0,  72(s4)
    csrr t0, CSR_CAT_FP_DIV_HI;     sw t0,  76(s4)
    csrr t0, CSR_CAT_FP_SQRT_LO;    sw t0,  80(s4)
    csrr t0, CSR_CAT_FP_SQRT_HI;    sw t0,  84(s4)
    csrr t0, CSR_CAT_FP_NONCOMP_LO; sw t0,  88(s4)
    csrr t0, CSR_CAT_FP_NONCOMP_HI; sw t0,  92(s4)
    csrr t0, CSR_CAT_FP_CONV_LO;    sw t0,  96(s4)
    csrr t0, CSR_CAT_FP_CONV_HI;    sw t0, 100(s4)
    csrr t0, CSR_CAT_DIVCYC_LO;     sw t0, 104(s4)
    csrr t0, CSR_CAT_DIVCYC_HI;     sw t0, 108(s4)
    sw s1, 112(s4)
    sw s2, 116(s4)
    csrr t0, CSR_CAT_FETCH_LO;      sw t0, 120(s4)
    csrr t0, CSR_CAT_FETCH_HI;      sw t0, 124(s4)
.endm
