# Programas de CALIBRACION del metodo 3 (regresion lineal estilo EfiMon).
# Son programas REALES y MIXTOS, con perfiles de instruccion DISTINTOS entre si y
# DISTINTOS a los benchmarks de verificacion (benchmarks/). Cada .elf = harness.S
# (ventana GPIO + dump de 30 words a 'results') + un kernel run_workload().
# Salen a ../elf/, que es lo que consume caracterizar.py.
RISCV ?= /home/jjsotoch/pulp/toolchain/v1.0.16-pulp-riscv-gcc-ubuntu-18
CROSS := $(RISCV)/bin/riscv32-unknown-elf-
CC    := $(CROSS)gcc
OUT   := ../elf

# Set REDISENADO para DECORRELACIONAR (bajar VIF): cada categoria barre de bajo a
# alto independiente, y mulh/div/float aparecen en 3 programas c/u. Anclas nuevas
# de alu-bajo (memcpy/fsm) porque en el set viejo alu nunca bajaba de 47%.
#   memcpy    mem ALTO / alu bajo     fsm       ctrl ALTO / alu bajo
#   crc       alu ALTO               matmul     mul ALTO / mem
#   mulhash64 mulh ALTO              dotprod    mul+mulh+float
#   gcd       div ALTO               modpow     div+mul
#   trialdiv  div (3.o)              fpoly      float ALTO (3.o)
#   vecscale  float / mem            histogram  mem ALTO disperso
#   sort      mem+ctrl+alu (balance)
BENCH := memcpy fsm crc matmul mulhash64 mulhscale dotprod gcd modpow trialdiv radix fpoly vecscale histogram sort wmac fir ratscale modmul memfill mulhstream
ELFS  := $(addprefix $(OUT)/,$(addsuffix .elf,$(BENCH)))

# Sondas por-categoria FP: un kernel DOMINADO por cada una de las 7 categorias
# float (fp_add/fp_mul/fp_fma/fp_div/fp_sqrt/fp_noncomp/fp_conv). NO estan en
# BENCH ni en DEFAULT_PROGS: se prueban una por una (fdiv/fsqrt y cadenas fmadd
# dependientes cuelgan la FPU de este bitstream). `make fp` compila; se corren con
# `caracterizar.py regresion fpadd ...` y se integran las que sobrevivan.
FP_PROBE := fpadd fpmul fpfma fpdiv fpsqrt fpnoncomp fpconv
FP_ELFS  := $(addprefix $(OUT)/,$(addsuffix .elf,$(FP_PROBE)))

# Kernels DOMINANTES por categoria entera (uno por alu/mul/mulh/div/mem/ctrl,
# ~60-86% de esa categoria) para que la regresion de M2 pueda IDENTIFICAR cada
# una (rompen la colinealidad de los mixtos). Entran en 'all'.
DOM := dalu dmul dmulh ddiv dmem dctrl
DOM_ELFS := $(addprefix $(OUT)/,$(addsuffix .elf,$(DOM)))

FLAGS  := -nostdlib -nostartfiles -static -Os -g -mabi=ilp32 \
	-Wl,-T,link.ld -Wl,--build-id=none -I.
KFLAGS := $(FLAGS) -fno-builtin -fno-tree-loop-distribute-patterns

.PHONY: all clean
include duty_variants.mk

all: $(ELFS) $(DUTY_ELFS) $(DOM_ELFS) $(OUT)/idle.elf
.PHONY: fp dom
fp: $(FP_ELFS)
dom: $(DOM_ELFS)

# Kernels dominantes (rv32imc; asm volatile fuerza la categoria objetivo). REPS
# calibrados para ~12 s a 10 MHz -> misma cadencia que los mixtos: da tiempo al
# ESP32 a capturar/subir la ventana y NO martilla el Sheet (las corridas cortas
# de ~4s disparaban 404 y "ventana sin P_avg"). Medido en la campana real.
$(OUT)/dalu.elf:  harness.S wl_dalu.c  platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=1800000 -o $@ harness.S wl_dalu.c
$(OUT)/dmul.elf:  harness.S wl_dmul.c  platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=17000   -o $@ harness.S wl_dmul.c
$(OUT)/dmulh.elf: harness.S wl_dmulh.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=5100    -o $@ harness.S wl_dmulh.c
$(OUT)/ddiv.elf:  harness.S wl_ddiv.c  platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=2600    -o $@ harness.S wl_ddiv.c
$(OUT)/dmem.elf:  harness.S wl_dmem.c  platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=130000  -o $@ harness.S wl_dmem.c
$(OUT)/dctrl.elf: harness.S wl_dctrl.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=23000   -o $@ harness.S wl_dctrl.c

# idle de referencia (wfi, piso pasivo) ~30 s -> da P_idle medido en sesion.
# .S auto-contenido (su propio _start), no usa harness.S.
# idle acortado a ~20 s (67 x 0.3 s), como el de bucles: el INA228 promedia de
# sobra en esa ventana y el default de 1000 reps (~5 min) solo alargaba la campana
# idle de referencia (piso pasivo, wfi): 1 rep x 400M ticks = ~40 s a 10 MHz,
# igual que el idle de M1. Ventana amplia para que el ESP32 promedie bien P_idle.
$(OUT)/idle.elf: idle.S platform.inc link.ld
	$(CC) $(FLAGS) -march=rv32imc -DIDLE_REPS=1 -DIDLE_TICKS=400000000 -o $@ idle.S

# enteros puros -> rv32imc
$(OUT)/sort.elf:      harness.S wl_sort.c      platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=15697   -o $@ harness.S wl_sort.c
$(OUT)/matmul.elf:    harness.S wl_matmul.c    platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=4036    -o $@ harness.S wl_matmul.c
$(OUT)/crc.elf:       harness.S wl_crc.c       platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=9760   -o $@ harness.S wl_crc.c
$(OUT)/gcd.elf:       harness.S wl_gcd.c       platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=6959   -o $@ harness.S wl_gcd.c
$(OUT)/histogram.elf: harness.S wl_histogram.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=15482  -o $@ harness.S wl_histogram.c
$(OUT)/modpow.elf:    harness.S wl_modpow.c    platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=21945   -o $@ harness.S wl_modpow.c
# nuevos (decorrelacion): anclas alu-bajo + mulh/div extra
$(OUT)/memcpy.elf:    harness.S wl_memcpy.c    platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=27946  -o $@ harness.S wl_memcpy.c
$(OUT)/fsm.elf:       harness.S wl_fsm.c       platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=15088  -o $@ harness.S wl_fsm.c
$(OUT)/mulhash64.elf: harness.S wl_mulhash64.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=56404   -o $@ harness.S wl_mulhash64.c
$(OUT)/trialdiv.elf:  harness.S wl_trialdiv.c  platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=18203   -o $@ harness.S wl_trialdiv.c
# decorrelacion 2: mulh SIN mul (rompe la pareja) + div con perfil mem
$(OUT)/mulhscale.elf: harness.S wl_mulhscale.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=160894  -o $@ harness.S wl_mulhscale.c
$(OUT)/radix.elf:     harness.S wl_radix.c     platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=17118   -o $@ harness.S wl_radix.c
# refuerzo mulh RETIRADO tras el experimento del 13-jul: fija mulh (10.4->3.9,
# estable) pero su alu denso contamina la atribucion (alu +20%, mem -28%) y la
# validacion global no mejora (0.20 vs 0.22%). Ver wl_mulhchain.c
$(OUT)/mulhchain.elf: harness.S wl_mulhchain.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=2300000 -o $@ harness.S wl_mulhchain.c

# con float -> rv32imfc + -ffp-contract=off (sin fmadd; ops INDEPENDIENTES)
$(OUT)/dotprod.elf:   harness.S wl_dotprod.c   platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=60150 -o $@ harness.S wl_dotprod.c
$(OUT)/vecscale.elf:  harness.S wl_vecscale.c  platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=77720 -o $@ harness.S wl_vecscale.c
$(OUT)/fpoly.elf:     harness.S wl_fpoly.c     platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=64378 -o $@ harness.S wl_fpoly.c
# refuerzo float+mem RETIRADO: wl_saxpy.c no termina en este bitstream
# (modo de falla de la FPU) ni siquiera con el patron de vecscale; queda la
# regla por si se retoma con otro bitstream
$(OUT)/saxpy.elf:     harness.S wl_saxpy.c     platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=230000 -o $@ harness.S wl_saxpy.c


# --- nuevos: mulh combinado con mem/mul/div (decorrelacionan mulh) ---
$(OUT)/wmac.elf:  harness.S wl_wmac.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=41973   -o $@ harness.S wl_wmac.c
$(OUT)/fir.elf:  harness.S wl_fir.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=30000   -o $@ harness.S wl_fir.c
$(OUT)/ratscale.elf:  harness.S wl_ratscale.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=18000   -o $@ harness.S wl_ratscale.c
$(OUT)/modmul.elf:  harness.S wl_modmul.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=27000   -o $@ harness.S wl_modmul.c


# --- alu-bajo / mulh-alto ctrl-bajo (decorrelacionan alu del modo comun y ctrl) ---
$(OUT)/memfill.elf:  harness.S wl_memfill.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=131352   -o $@ harness.S wl_memfill.c
$(OUT)/mulhstream.elf:  harness.S wl_mulhstream.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc  -DREPS=8500   -o $@ harness.S wl_mulhstream.c

# --- sondas por-categoria FP (rv32imfc, -ffp-contract=off; lazo caliente dominado
# por SU categoria). REPS bajos en div/sqrt/fma: lentas y candidatas a colgar. ---
# REPS ~12 s (misma cadencia que los mixtos; evita 404/ventana-perdida por
# corridas cortas). Estructura M1: operandos constantes, sin loads (evita el
# deadlock de la FPU). Medido en la campana real (fpadd/mul/noncomp/conv ~3.6s a
# 1.5M -> 5M; fma 1.9s a 800k -> 5M; div/sqrt ~1.2s a 40k -> 400k).
$(OUT)/fpadd.elf:  harness.S wl_fpadd.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=5000000 -o $@ harness.S wl_fpadd.c
$(OUT)/fpmul.elf:  harness.S wl_fpmul.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=5000000 -o $@ harness.S wl_fpmul.c
$(OUT)/fpnoncomp.elf:  harness.S wl_fpnoncomp.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=5000000 -o $@ harness.S wl_fpnoncomp.c
$(OUT)/fpconv.elf:  harness.S wl_fpconv.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=5000000 -o $@ harness.S wl_fpconv.c
$(OUT)/fpfma.elf:  harness.S wl_fpfma.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=5000000 -o $@ harness.S wl_fpfma.c
$(OUT)/fpdiv.elf:  harness.S wl_fpdiv.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=400000 -o $@ harness.S wl_fpdiv.c
$(OUT)/fpsqrt.elf:  harness.S wl_fpsqrt.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=400000 -o $@ harness.S wl_fpsqrt.c

clean:
	rm -f $(ELFS) $(FP_ELFS)
