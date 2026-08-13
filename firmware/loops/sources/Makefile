# Metodo 1 (loops dominados): un .elf por categoria desde su .S. Salida -> ../elf/.
RISCV ?= /home/jjsotoch/pulp/toolchain/v1.0.16-pulp-riscv-gcc-ubuntu-18
CROSS := $(RISCV)/bin/riscv32-unknown-elf-
CC    := $(CROSS)gcc

CATS := alu mul mulh div mem ctrl fp_add fp_mul fp_fma fp_div fp_sqrt fp_noncomp fp_conv idle
OUT  := ../elf
ELFS := $(addprefix $(OUT)/,$(addsuffix .elf,$(CATS)))

FLAGS := -nostdlib -nostartfiles -static -Os -g -mabi=ilp32 \
	-Wl,-T,link.ld -Wl,--build-id=none -I.

# Las categorias FP se compilan con la extension F (rv32imfc); el resto sin ella.
ARCH := rv32imc
FP_CATS := fp_add fp_mul fp_fma fp_div fp_sqrt fp_noncomp fp_conv
$(addprefix $(OUT)/,$(addsuffix .elf,$(FP_CATS))): ARCH := rv32imfc

# Kernels de SWITCHING (experimento Tiwari de overhead inter-instruccion, M1).
# No entran en 'all' (experimento aparte); se construyen con 'make switch'.
# Generados por gen_switch.py; usan el pattern rule generico (rv32imc).
SWITCH := sw_alu_mem sw_alu_mul sw_alu_ctrl sw_alu_mulh \
	sw_mem_mul sw_mem_ctrl sw_mul_mulh sw_alu_div
SWITCH_ELFS := $(addprefix $(OUT)/,$(addsuffix .elf,$(SWITCH)))
# Mezclas realistas (gen_mix.py): calibran la escala representativa de M1.
MIX := mix_gen mix_mem mix_ari
MIX_ELFS := $(addprefix $(OUT)/,$(addsuffix .elf,$(MIX)))

.PHONY: all clean switch mix
all: $(ELFS)
switch: $(SWITCH_ELFS)
mix: $(MIX_ELFS)

$(OUT)/%.elf: %.S platform.inc link.ld | $(OUT)
	$(CC) $(FLAGS) -march=$(ARCH) -o $@ $<

$(OUT):
	mkdir -p $(OUT)


# ctrl con footprint parametrizable (barrer en banco):
#   make -B ../elf/ctrl.elf FOOTPRINT_KB=8 LOOP_COUNT=20000  (-B: forzar rebuild al barrer)
FOOTPRINT_KB ?= 16
$(OUT)/ctrl.elf: ctrl.S platform.inc link.ld | $(OUT)
	$(CC) $(FLAGS) -march=rv32imc -DFOOTPRINT_KB=$(FOOTPRINT_KB)$(if $(LOOP_COUNT), -DLOOP_COUNT=$(LOOP_COUNT)) -o $@ ctrl.S

clean:
	rm -f $(ELFS)
