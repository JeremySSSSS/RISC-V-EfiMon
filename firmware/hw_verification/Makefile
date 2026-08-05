# Verificacion funcional del clasificador en hardware: un solo ELF con fases.
RISCV ?= /home/jjsotoch/pulp/toolchain/v1.0.16-pulp-riscv-gcc-ubuntu-18
CROSS := $(RISCV)/bin/riscv32-unknown-elf-
CC    := $(CROSS)gcc

OUT := elf
ELF := $(OUT)/hw_verification.elf

FLAGS := -nostdlib -nostartfiles -static -Os -g -mabi=ilp32 \
	-Wl,-T,../loops/sources/link.ld -Wl,--build-id=none \
	-I../loops/sources -march=rv32imfc

.PHONY: all clean
all: $(ELF)

$(ELF): hw_verification.S ../loops/sources/platform.inc ../loops/sources/link.ld | $(OUT)
	$(CC) $(FLAGS) -o $@ $<

$(OUT):
	mkdir -p $(OUT)

clean:
	rm -f $(ELF)
