/* support.h shim para correr los kernels de BEEBS sobre el harness del banco
 * (bare-metal, sin libc). Reemplaza al support.h original de BEEBS: aqui no
 * hay placa BEEBS que inicializar; la repeticion la controla el wrapper
 * (beebs_wrap.c) con REPS, asi que REPEAT_FACTOR queda en 1 y cada llamada a
 * benchmark() hace una pasada. */
#ifndef SUPPORT_H
#define SUPPORT_H

#define REPEAT_FACTOR 1
#define BOARD_REPEAT_FACTOR 1

void initialise_benchmark(void);
int  benchmark(void);
int  verify_benchmark(int r);

/* stubs minimos que algunos kernels referencian (los provee beebs_wrap.c) */
int printf(const char *fmt, ...);
unsigned int strlen(const char *s);

#endif
