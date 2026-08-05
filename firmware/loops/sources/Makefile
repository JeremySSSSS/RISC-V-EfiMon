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

.PHONY: all clean
all: $(ELFS)

$(OUT)/%.elf: %.S platform.inc link.ld | $(OUT)
	$(CC) $(FLAGS) -march=$(ARCH) -o $@ $<

$(OUT):
	mkdir -p $(OUT)

clean:
	rm -f $(ELFS)
