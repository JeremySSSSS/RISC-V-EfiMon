# Verificacion funcional del clasificador en hardware: un solo ELF con fases.
RISCV ?= /home/jjsotoch/pulp/toolchain/v1.0.16-pulp-riscv-gcc-ubuntu-18
CROSS := $(RISCV)/bin/riscv32-unknown-elf-
CC    := $(CROSS)gcc

OUT := elf
ELF := $(OUT)/verificacion_hw.elf

FLAGS := -nostdlib -nostartfiles -static -Os -g -mabi=ilp32 \
	-Wl,-T,../bucles/fuentes/link.ld -Wl,--build-id=none \
	-I../bucles/fuentes -march=rv32imfc

.PHONY: all clean
all: $(ELF)

$(ELF): verificacion_hw.S ../bucles/fuentes/platform.inc ../bucles/fuentes/link.ld | $(OUT)
	$(CC) $(FLAGS) -o $@ $<

$(OUT):
	mkdir -p $(OUT)

clean:
	rm -f $(ELF)
