/* xxHash64: funcion hash no criptografica de Y. Collet (BSD-2-Clause,
 * github.com/Cyan4973/xxHash), algoritmo de referencia en version
 * single-shot. Carga de validacion densa en mulh: cada carril procesa
 * palabras de 64 bits con multiplicaciones 64x64 sobre RV32. Interfaz
 * estandar de BEEBS para beebs_wrap.c. */
#include <stdint.h>

/* hash plegado del buffer de referencia (calculado con la misma fuente
 * compilada nativa; el resultado no depende de REPS) */
#ifndef EXPECTED_XXH64
#define EXPECTED_XXH64 0x72395f9du
#endif

#define P1 11400714785074694791ULL
#define P2 14029467366897019727ULL
#define P3  1609587929392839161ULL
#define P4  9650029242287828579ULL
#define P5  2870177450012600261ULL

static inline uint64_t rotl64(uint64_t x, unsigned r) {
  return (x << r) | (x >> (64u - r));
}

static inline uint64_t xxh_round(uint64_t acc, uint64_t input) {
  acc += input * P2;
  acc = rotl64(acc, 31);
  acc *= P1;
  return acc;
}

static inline uint64_t xxh_merge(uint64_t h, uint64_t v) {
  h ^= xxh_round(0, v);
  return h * P1 + P4;
}

static inline uint64_t read64(const uint8_t *p) {
  uint64_t x = 0;
  for (int i = 7; i >= 0; i--) x = (x << 8) | p[i];
  return x;
}

static inline uint32_t read32(const uint8_t *p) {
  return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
         ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static uint64_t xxh64(const uint8_t *p, unsigned len, uint64_t seed) {
  const uint8_t *end = p + len;
  uint64_t h;
  if (len >= 32) {
    uint64_t v1 = seed + P1 + P2, v2 = seed + P2, v3 = seed, v4 = seed - P1;
    do {
      v1 = xxh_round(v1, read64(p));      p += 8;
      v2 = xxh_round(v2, read64(p));      p += 8;
      v3 = xxh_round(v3, read64(p));      p += 8;
      v4 = xxh_round(v4, read64(p));      p += 8;
    } while (p + 32 <= end);
    h = rotl64(v1, 1) + rotl64(v2, 7) + rotl64(v3, 12) + rotl64(v4, 18);
    h = xxh_merge(h, v1); h = xxh_merge(h, v2);
    h = xxh_merge(h, v3); h = xxh_merge(h, v4);
  } else {
    h = seed + P5;
  }
  h += len;
  while (p + 8 <= end) { h ^= xxh_round(0, read64(p)); h = rotl64(h, 27) * P1 + P4; p += 8; }
  if (p + 4 <= end)    { h ^= (uint64_t)read32(p) * P1; h = rotl64(h, 23) * P2 + P3; p += 4; }
  while (p < end)      { h ^= (*p) * P5; h = rotl64(h, 11) * P1; p++; }
  h ^= h >> 33; h *= P2;
  h ^= h >> 29; h *= P3;
  h ^= h >> 32;
  return h;
}

static uint8_t buf[1024];

void initialise_benchmark(void) {
  for (unsigned i = 0; i < sizeof buf; i++)
    buf[i] = (uint8_t)(i * 167u + 13u);
}

int benchmark(void) {
  uint64_t h = xxh64(buf, sizeof buf, 0);
  return (int)(uint32_t)(h ^ (h >> 32));
}

int verify_benchmark(int r) {
  return r == (int)EXPECTED_XXH64;
}
