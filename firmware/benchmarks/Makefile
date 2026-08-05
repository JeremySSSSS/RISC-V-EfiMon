# Benchmarks de validation del model (held-out, NUNCA usados en calibracion).
# Todos en assembly (.S): cada ELF = harness.S + wl_<nombre>.S.
# Los float usan SOLO el set FP probado en HW (fadd/fmul/fsub/fmax
# independientes, sin fmadd/cadenas seriales); ver comentario de cada wl_*.S.
RISCV ?= /home/jjsotoch/pulp/toolchain/v1.0.16-pulp-riscv-gcc-ubuntu-18
CROSS := $(RISCV)/bin/riscv32-unknown-elf-
CC    := $(CROSS)gcc

# Conjunto oficial ANTERIOR (ensamblador, histograma fijo): RETIRADO por
# decision de validar solo con codigo real de BEEBS. Los kernels sinteticos
# wl_*.S de exploracion no se incluyen en este repositorio.
BENCH_INT :=
BENCH_FP  :=
# Cargas REALES: kernels de BEEBS (Pallister et al. 2013) sin modificar, en
# beebs/<nombre>.c, adaptados por beebs_wrap.c (interfaz initialise/benchmark/
# verify -> run_workload). REPS apunta a ventanas de ~15-35 s a 10 MHz;
# ajustar tras la primera corrida si la ventana queda corta o larga.
BENCH_BEEBS := mont64 ud jfdctint nettleaes strsearch huffbench levenshtein ns aqsort
# gray: la unica propia (float); los kernels float de BEEBS usan double o
# acumulaciones dependientes que la FPU de este bitstream no ejecuta estable
BENCH_C_FP := gray
# Cargas reales que ejercitan mulh/div (validacion held-out): modexp (Montgomery),
# bigdiv (division larga), ratapprox (fracciones continuas). run_workload en C.
BENCH_MULHDIV := modexp bigdiv ratapprox
ELFS := $(addsuffix .elf,$(BENCH_INT) $(BENCH_FP) $(BENCH_BEEBS) $(BENCH_C_FP) $(BENCH_MULHDIV))

mont64.elf:      REPS := 20000
ud.elf:          REPS := 55000
jfdctint.elf:    REPS := 150000
nettleaes.elf:   REPS := 3000
# dijkstra: RETIRADO. Su reservador de memoria interno (qmalloc sobre pool
# estatico) siguio dando cuelgues intermitentes; sustituido por strsearch
# (stringsearch1 de BEEBS: Boyer-Moore-Horspool, mem+ctrl, sin pool).
# dijkstra.elf:    REPS := 280
strsearch.elf:   REPS := 8000
huffbench.elf:   REPS := 1800
levenshtein.elf: REPS := 4000
# ns: foo(400) es pura y su resultado se descarta -> GCC la eliminaba
# entera (tanda del 18-jul: 5 instr/rep). Sin analisis de pureza el
# llamado sobrevive.
ns.elf:          REPS := 20000
ns.elf:          KFLAGS += -fno-ipa-pure-const
aqsort.elf:      REPS := 18000
aqsort.elf:      KFLAGS += -DQUICK_SORT
# perlin (stb_perlin de BEEBS): RETIRADO. Sin instrucciones FP prohibidas
# (solo fadd/fmul/fsub/fcvt/feq), pero sus cadenas de lerps (~6-9 ops FP
# dependientes por punto) COLGARON en hardware. Con fqsort (comparaciones
# densas) y este, NINGUN kernel float de BEEBS es ejecutable en este
# bitstream: el resto usa fdiv/fsqrt o acumulacion dependiente. La carga
# float queda en gray (propia, patron probado).
# perlin.elf:      REPS := 1200
# perlin.elf:      ARCH := rv32imfc
# perlin.elf:      KFLAGS += -ffp-contract=off
# fqsort (qsort de BEEBS sobre floats): RETIRADO. Solo usa flw/fsw y
# comparaciones fle.s/flt.s, pero su lazo interno (load->flt.s->branch
# pegados) COLGO en hardware: tercera evidencia de la restriccion de la
# FPU del bitstream (cadenas dependientes, rafagas densas y ahora
# comparaciones densas). La carga float real queda en gray (aritmetica
# espaciada con memoria, el patron probado).
# fqsort.elf:      REPS := 4000
# fqsort.elf:      ARCH := rv32imfc
# fqsort.elf:      KFLAGS += -ffp-contract=off

FLAGS  := -nostdlib -nostartfiles -static -Os -g -mabi=ilp32 \
	-Wl,-T,link.ld -Wl,--build-id=none -I.
KFLAGS := $(FLAGS) -fno-builtin -fno-tree-loop-distribute-patterns

ARCH := rv32imc
$(addsuffix .elf,$(BENCH_FP)): ARCH := rv32imfc
# gray es float en C: rv32imfc y SIN contraccion a fmadd (fuera del conjunto
# probado de la FPU de este bitstream)
gray.elf: ARCH := rv32imfc
gray.elf: KFLAGS += -ffp-contract=off

.PHONY: all clean
all: $(ELFS)

%.elf: wl_%.S harness.S platform.inc link.ld
	$(CC) $(KFLAGS) -march=$(ARCH) -o $@ harness.S $<

%.elf: wl_%.c harness.S platform.inc link.ld
	$(CC) $(KFLAGS) -march=$(ARCH) -o $@ harness.S $<

# strsearch = stringsearch1 de BEEBS: tres unidades (dos buscadores con
# estado estatico propio + el arnes del benchmark)
strsearch.elf: beebs/stringsearch1.c beebs/fast.fwd.inc.c beebs/fast.rev.d12.c beebs_wrap.c beebs/support.h harness.S platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -Ibeebs -DNDEBUG -DREPS=$(REPS) -o $@ harness.S beebs_wrap.c beebs/stringsearch1.c beebs/fast.fwd.inc.c beebs/fast.rev.d12.c -lgcc

# -lgcc: algun kernel (ud) usa double en su verify_benchmark (fuera de la
# ventana de medicion); el soft-float lo aporta libgcc
%.elf: beebs/%.c beebs_wrap.c beebs/support.h harness.S platform.inc link.ld
	$(CC) $(KFLAGS) -march=$(ARCH) -Ibeebs -DNDEBUG -DREPS=$(REPS) -o $@ harness.S beebs_wrap.c $< -lgcc

# cargas extra (mulh): mismo wrapper e interfaz que BEEBS
%.elf: extra/%.c beebs_wrap.c harness.S platform.inc link.ld
	$(CC) $(KFLAGS) -march=$(ARCH) -Ibeebs -DNDEBUG -DREPS=$(REPS) -o $@ harness.S beebs_wrap.c $< -lgcc

# validacion mulh/div (run_workload en C, pasa REPS)
modexp.elf:    REPS := 20000
bigdiv.elf:    REPS := 20000
ratapprox.elf: REPS := 20000
$(addsuffix .elf,$(BENCH_MULHDIV)): %.elf: wl_%.c harness.S platform.inc link.ld
	$(CC) $(KFLAGS) -march=rv32imc -DREPS=$(REPS) -o $@ harness.S $<

clean:
	rm -f $(ELFS)
