/* PCG32: generador de numeros pseudoaleatorios de M.E. O'Neill (pcg_basic,
 * Apache-2.0, www.pcg-random.org), sin modificar. Carga de validacion densa
 * en mulh: el paso de estado es una multiplicacion 64x64 sobre RV32
 * (mul + mulhu + 2 mul por draw). Interfaz estandar de BEEBS
 * (initialise/benchmark/verify) para beebs_wrap.c.
 * Cada benchmark() re-siembra con la semilla de referencia y genera 1024
 * numeros, asi el resultado no depende de REPS. */
#include <stdint.h>

/* xor de los 1024 draws con la semilla de referencia (calculado con la
 * misma fuente compilada nativa; el resultado no depende de REPS) */
#ifndef EXPECTED_PCG32
#define EXPECTED_PCG32 0x619bdcbau
#endif

typedef struct { uint64_t state; uint64_t inc; } pcg32_random_t;

static uint32_t pcg32_random_r(pcg32_random_t *rng) {
  uint64_t oldstate = rng->state;
  rng->state = oldstate * 6364136223846793005ULL + rng->inc;
  uint32_t xorshifted = (uint32_t)(((oldstate >> 18u) ^ oldstate) >> 27u);
  uint32_t rot = (uint32_t)(oldstate >> 59u);
  return (xorshifted >> rot) | (xorshifted << ((-rot) & 31u));
}

void initialise_benchmark(void) {}

int benchmark(void) {
  /* semilla del demo de referencia de pcg_basic */
  pcg32_random_t rng = { 0x853c49e6748fea9bULL, 0xda3e39cb94b95bdbULL };
  uint32_t acc = 0;
  for (int i = 0; i < 1024; i++)
    acc ^= pcg32_random_r(&rng);
  return (int)acc;
}

int verify_benchmark(int r) {
  return r == (int)EXPECTED_PCG32;
}
