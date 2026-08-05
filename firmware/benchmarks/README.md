# benchmarks — validation loads (BEEBS)

Model validation uses **BEEBS kernels** (Pallister, Hollis and Bennett, 2013 —
the standard embedded energy-benchmark suite), with the **unmodified** sources
in `beebs/` (GPL license, see `beebs/LICENSE`). `beebs_wrap.c` connects their
standard interface (`initialise_benchmark`/`benchmark`/`verify_benchmark`) to the
harness `run_workload()` and provides the libc stubs some kernels reference
(debug printf, strlen, memset/memcpy, floor). No load takes part in calibration.

## The set

- `mont64` — 64-bit Montgomery multiplication (**dense mul + mulh**, 128-bit arithmetic).
- `ud` — integer LU decomposition (**real divisions** by pivots).
- `jfdctint` — JPEG integer DCT (dense mul).
- `nettleaes` — AES from the Nettle library (alu + mem).
- `strsearch` — Boyer–Moore–Horspool pattern search (stringsearch1; mem + ctrl).
  Replaces `dijkstra`, retired due to intermittent hangs of its internal
  memory allocator over a static pool.
- `huffbench` — Huffman compression/decompression (mem + ctrl).
- `levenshtein` — string edit distance (mem + alu).
- `ns` — multidimensional array search (mem + ctrl).
- `aqsort` — integer quicksort (sglib, `-DQUICK_SORT`; mem + ctrl).
- `wl_gray.c` — the only **own** load: RGB→luminance per pixel in float
  (fadd/fmul/fcvt without fmadd, `-ffp-contract=off`).

Each kernel's `REPS` (Makefile) targets ~15–35 s windows at 10 MHz; adjust after
the first run.

## Why gray is not from BEEBS

ALL float kernels in the suite were checked against this bitstream's FPU and none
turned out to be runnable:

- `ludcmp`, `minver`, `qurt`, `sqrt`, `newlib-*`: use fdiv/fsqrt, outside the
  FPU's tested set.
- `matmult-float`: dependent accumulation (the pattern that hung saxpy).
- `fqsort` (float qsort): only fle/flt comparisons — **hung in HW** (dense FP
  comparisons, a third unstable pattern).
- `perlin` (stb_perlin): only fadd/fmul/fsub/fcvt/feq — **hung in HW** (chains of
  ~6–9 dependent FP lerps).
- The rest of the BEEBS floats use `double` (soft-float: does not exercise the FPU).

`gray` uses the only pattern this bitstream runs stably: FP arithmetic with
independent operands spaced by memory and integers (like the hardware's
successful tests). The retired kernels stay in `beebs/` as evidence (fqsort.c,
perlin.c) with their rules commented out in the Makefile.

`harness.S` + `link.ld` + `platform.inc` are the shared harness.
