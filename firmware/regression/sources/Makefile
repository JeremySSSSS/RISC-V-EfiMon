# Programas de CALIBRACION del metodo 3 (regression lineal estilo EfiMon).
# Son programas REALES y MIXTOS, con perfiles de instruccion DISTINTOS entre si y
# DISTINTOS a los benchmarks de verificacion (benchmarks/). Cada .elf = harness.S
# (ventana GPIO + dump de 30 words a 'results') + un kernel run_workload().
# Salen a ../elf/, que es lo que consume characterize.py.
RISCV ?= /home/jjsotoch/pulp/toolchain/v1.0.16-pulp-riscv-gcc-ubuntu-18
CROSS := $(RISCV)/bin/riscv32-unknown-elf-
CC := $(CROSS)gcc
OUT := ../elf

# Set REDISENADO para DECORRELACIONAR (bajar VIF): cada categoria barre de bajo a
# alto independiente, y mulh/div/float aparecen en 3 programas c/u. Anclas nuevas
# de alu-bajo (memcpy/fsm) porque en el set viejo alu nunca bajaba de 47%.
# memcpy mem ALTO / alu bajo fsm ctrl ALTO / alu bajo
# crc alu ALTO matmul mul ALTO / mem
# mulhash64 mulh ALTO dotprod mul+mulh+float
# gcd div ALTO modpow div+mul
# trialdiv div (3.o) fpoly float ALTO (3.o)
# vecscale float / mem histogram mem ALTO disperso
# sort mem+ctrl+alu (balance)
BENCH := memcpy fsm crc matmul mulhash64 mulhscale dotprod gcd modpow trialdiv radix fpoly vecscale histogram sort wmac fir ratscale modmul memfill mulhstream
ELFS := $(addprefix $(OUT)/,$(addsuffix .elf,$(BENCH)))

FLAGS := -nostdlib -nostartfiles -static -Os -g -mabi=ilp32 \
	-Wl,-T,link.ld -Wl,--build-id=none -I.
KFLAGS := $(FLAGS) -fno-builtin -fno-tree-loop-distribute-patterns

.PHONY: all clean
include duty_variants.mk

all: $(ELFS) $(DUTY_ELFS) $(OUT)/idle.elf

# idle de referencia (wfi, piso pasivo) ~30 s -> da P_idle medido en sesion.
# .S auto-contenido (su propio _start), no usa harness.S.
# idle acortado a ~20 s (67 x 0.3 s), como el de loops: el INA228 promedia de
# sobra en esa ventana y el default de 1000 reps (~5 min) solo alargaba la campana
$(OUT)/idle.elf: idle.S platform.inc link.ld
	$(CC) $(FLAGS) -march=rv32imc -DIDLE_REPS=67 -o $@ idle.S

# enteros puros -> rv32imc
$(OUT)/sort.elf: harness.S wl_sort.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=20000 -o $@ harness.S wl_sort.c
$(OUT)/matmul.elf: harness.S wl_matmul.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=6000 -o $@ harness.S wl_matmul.c
$(OUT)/crc.elf: harness.S wl_crc.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=40000 -o $@ harness.S wl_crc.c
$(OUT)/gcd.elf: harness.S wl_gcd.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=30000 -o $@ harness.S wl_gcd.c
$(OUT)/histogram.elf: harness.S wl_histogram.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=200000 -o $@ harness.S wl_histogram.c
$(OUT)/modpow.elf: harness.S wl_modpow.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=60000 -o $@ harness.S wl_modpow.c
# nuevos (decorrelacion): anclas alu-bajo + mulh/div extra
$(OUT)/memcpy.elf: harness.S wl_memcpy.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=150000 -o $@ harness.S wl_memcpy.c
$(OUT)/fsm.elf: harness.S wl_fsm.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=150000 -o $@ harness.S wl_fsm.c
$(OUT)/mulhash64.elf: harness.S wl_mulhash64.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=80000 -o $@ harness.S wl_mulhash64.c
$(OUT)/trialdiv.elf: harness.S wl_trialdiv.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=40000 -o $@ harness.S wl_trialdiv.c
# decorrelacion 2: mulh SIN mul (rompe la pareja) + div con perfil mem
$(OUT)/mulhscale.elf: harness.S wl_mulhscale.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=120000 -o $@ harness.S wl_mulhscale.c
$(OUT)/radix.elf: harness.S wl_radix.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=30000 -o $@ harness.S wl_radix.c
# refuerzo mulh RETIRADO tras el experimento del 13-jul: fija mulh (10.4->3.9,
# estable) pero su alu denso contamina la atribucion (alu +20%, mem -28%) y la
# validation global no mejora (0.20 vs 0.22%). Ver wl_mulhchain.c
$(OUT)/mulhchain.elf: harness.S wl_mulhchain.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=2300000 -o $@ harness.S wl_mulhchain.c

# con float -> rv32imfc + -ffp-contract=off (sin fmadd; ops INDEPENDIENTES)
$(OUT)/dotprod.elf: harness.S wl_dotprod.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=120000 -o $@ harness.S wl_dotprod.c
$(OUT)/vecscale.elf: harness.S wl_vecscale.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=300000 -o $@ harness.S wl_vecscale.c
$(OUT)/fpoly.elf: harness.S wl_fpoly.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=200000 -o $@ harness.S wl_fpoly.c
# refuerzo float+mem RETIRADO: wl_saxpy.c no termina en este bitstream
# (modo de falla de la FPU) ni siquiera con el patron de vecscale; queda la
# regla por si se retoma con otro bitstream
$(OUT)/saxpy.elf: harness.S wl_saxpy.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imfc -ffp-contract=off -DREPS=230000 -o $@ harness.S wl_saxpy.c


# --- nuevos: mulh combinado con mem/mul/div (decorrelacionan mulh) ---
$(OUT)/wmac.elf: harness.S wl_wmac.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=40000 -o $@ harness.S wl_wmac.c
$(OUT)/fir.elf: harness.S wl_fir.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=25000 -o $@ harness.S wl_fir.c
$(OUT)/ratscale.elf: harness.S wl_ratscale.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=40000 -o $@ harness.S wl_ratscale.c
$(OUT)/modmul.elf: harness.S wl_modmul.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=40000 -o $@ harness.S wl_modmul.c


# --- alu-bajo / mulh-alto ctrl-bajo (decorrelacionan alu del modo comun y ctrl) ---
$(OUT)/memfill.elf: harness.S wl_memfill.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=30000 -o $@ harness.S wl_memfill.c
$(OUT)/mulhstream.elf: harness.S wl_mulhstream.c platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=30000 -o $@ harness.S wl_mulhstream.c

clean:
	rm -f $(ELFS)
