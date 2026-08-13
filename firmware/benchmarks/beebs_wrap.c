/* Wrapper comun para los kernels de BEEBS: adapta su interfaz estandar
 * (initialise_benchmark / benchmark / verify_benchmark) al run_workload()
 * que espera el harness del banco, y provee los stubs de libc que algunos
 * kernels referencian (printf de depuracion, strlen). El kernel se compila
 * SIN modificar desde benchmarks/beebs/<nombre>.c. */
#ifndef REPS
#define REPS 1000
#endif

void initialise_benchmark(void);
int  benchmark(void);
int  verify_benchmark(int r);

/* printf de depuracion de algunos kernels: no hay consola en el SoC */
int printf(const char *fmt, ...) { (void)fmt; return 0; }

/* abort() de stringsearch1: solo se llamaria con un patron de mas de 256
 * caracteres, que aqui no existe; debe enlazar de todas formas */
void abort(void) { for (;;) ; }

unsigned int strlen(const char *s) {
  unsigned int n = 0;
  while (s[n]) n++;
  return n;
}

void *memset(void *d, int v, unsigned int n) {
  unsigned char *p = d;
  while (n--) *p++ = (unsigned char)v;
  return d;
}

void *memcpy(void *d, const void *s, unsigned int n) {
  unsigned char *pd = d; const unsigned char *ps = s;
  while (n--) *pd++ = *ps++;
  return d;
}

/* floor() de math.h que usa stb_perlin; sus argumentos alli son siempre
 * positivos, asi que truncar alcanza (el soft-double lo aporta libgcc) */
double floor(double x) {
  int i = (int)x;
  if ((double)i > x) i--;
  return i;
}

void run_workload(void) {
  volatile int sink = 0;
  int r = 0;
  initialise_benchmark();
  for (int i = 0; i < REPS; i++)
    r = benchmark();
  sink += verify_benchmark(r);
}
