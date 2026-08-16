/* fp_noncomp-dominante, carga MIXTA held-out. La FPU de este bitstream SOLO corre
 * fmax/fmin/fsgnj/cmp con operandos CONSTANTES en registro (input fresco la cuelga;
 * ver fpu_fmadd_restriccion). Las ops noncomp operan sobre un set fijo de constantes
 * (en registro), envueltas en trabajo ENTERO real que varia por elemento -> mezcla
 * fp_noncomp + alu + mem. Held-out: distinta proporcion/estructura que el probe
 * fpnoncomp de calibracion. Resultado fp descartado; reduccion entera. */
#ifndef REPS
#define REPS 9000
#endif
#define N 512
static int A[N];
static int init = 0;

void run_workload(void) {
  volatile int sink = 0;
  if (!init) {
    unsigned s = 0x13579bdfu;
    for (int i = 0; i < N; i++) {
      s = s * 1103515245u + 12345u; A[i] = (int)((s >> 7) & 8191) + 1;
    }
    init = 1;
  }
  const float a = 1.5f, b = 2.25f, c = 0.75f, d = 3.125f;  /* en registros */
  for (int r = 0; r < REPS; r++) {
    int acc = 0;
    for (int i = 0; i < N; i++) {
      int v = A[i];
      int w = (v * 7 + (v >> 1)) - (i & 127);      /* alu real */
      float j;
      asm volatile("fmax.s  %0,%1,%2" : "=f"(j) : "f"(a), "f"(b));  /* fp_noncomp, const */
      asm volatile("fmin.s  %0,%1,%2" : "=f"(j) : "f"(a), "f"(c));
      asm volatile("fsgnj.s %0,%1,%2" : "=f"(j) : "f"(d), "f"(a));
      asm volatile("fmax.s  %0,%1,%2" : "=f"(j) : "f"(b), "f"(d));
      acc += w + (v & 7);                           /* reduccion entera */
    }
    sink += acc;
  }
  (void)sink;
}
