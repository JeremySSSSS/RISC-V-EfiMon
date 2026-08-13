/* DIAGNOSTICO fp_sqrt: fsqrt.s sobre dato FRESCO (fcvt) pero RESULTADO DESCARTADO
 * (no lo lee ninguna instruccion dependiente; acumulo entero aparte). Aisla si el
 * cuelgue de la version "real" era el CONSUMIDOR dependiente del sqrt (fcvt.w.s
 * pegado) o el INPUT fresco a la unidad DIVSQRT.
 *   - corre  -> el cuelgue es el consumidor: hay que desacoplar sqrt de su lectura.
 *   - cuelga -> DIVSQRT no tolera input fresco; fp_sqrt no admite dato real. */
#ifndef REPS
#define REPS 8000
#endif
#define N 512
static int X[N];
static int init = 0;

void run_workload(void) {
  volatile int sink = 0;
  if (!init) {
    unsigned s = 0x1234567u;
    for (int i = 0; i < N; i++) {
      s = s * 1103515245u + 12345u; X[i] = (int)((s >> 9) & 1023) + 1;  /* >0 */
    }
    init = 1;
  }
  for (int r = 0; r < REPS; r++) {
    int acc = 0;
    for (int i = 0; i < N; i++) {
      float x = (float)X[i];                         /* fcvt.s.w (fresco) */
      float m;
      asm volatile("fsqrt.s %0,%1" : "=f"(m) : "f"(x));  /* fsqrt, resultado NO leido */
      acc += X[i];                                   /* acum ENTERO, no toca m */
    }
    sink += acc;
  }
  (void)sink;
}
