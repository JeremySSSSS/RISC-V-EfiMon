# Test de bring-up del XADC: harness.S (de benchmarks, da _start) + wl_temp.c.
# El header pulp_temp.h vive en ../comun. Genera test_temp.elf.
RISCV ?= /home/jjsotoch/pulp/toolchain/v1.0.16-pulp-riscv-gcc-ubuntu-18
CROSS := $(RISCV)/bin/riscv32-unknown-elf-
CC    := $(CROSS)gcc
BM    := ../benchmarks

FLAGS := -nostdlib -nostartfiles -static -Os -g -mabi=ilp32 \
	-Wl,-T,$(BM)/link.ld -Wl,--build-id=none -I$(BM) -I../comun \
	-fno-builtin -fno-tree-loop-distribute-patterns -march=rv32imc

.PHONY: all clean
all: test_temp.elf

test_temp.elf: $(BM)/harness.S wl_temp.c $(BM)/platform.inc $(BM)/link.ld ../comun/pulp_temp.h
	$(CC) $(FLAGS) -o $@ $(BM)/harness.S wl_temp.c

clean:
	rm -f test_temp.elf
