/* NORMALIZACION por razon (DSP real): calcula la razon de dos canales
 *   q = num / den   (p.ej. reflectancia = reflejado/incidente, o normalizar una
 * senal por una referencia por-muestra). fp_div DOMINANTE. Los denominadores
 * VARIAN por elemento, asi que el compilador NO puede cambiar la division por un
 * reciproco constante -> queda fdiv real.
 *
 * Patron SEGURO (estilo gray): datos ENTEROS, floats via fcvt (sin flw), arbol
 * corto, resultado entero. -ffp-contract=off. */
#ifndef REPS
#define REPS 8000
#endif
#define N 512
static int NUM[N], DEN[N];
static int init = 0;

void run_workload(void) {
  volatile int sink = 0;
  if (!init) {
    unsigned s = 0x2468acefu;
    for (int i = 0; i < N; i++) {
      s = s * 1103515245u + 12345u; NUM[i] = (int)((s >> 8) & 8191) + 1;
      s = s * 1103515245u + 12345u; DEN[i] = (int)((s >> 8) & 1023) + 3;  /* != 0 */
    }
    init = 1;
  }
  for (int r = 0; r < REPS; r++) {
    int acc = 0;
    for (int i = 0; i < N; i++) {
      float num = (float)NUM[i];            /* fcvt.s.w (no flw) */
      float den = (float)(DEN[i] + (r & 7));/* varia -> fdiv no se hoistea */
      float q = num / den;                  /* fdiv */
      acc += (int)(q * 16.0f);              /* fmul + fcvt.w.s + acum. entera */
    }
    sink += acc;
  }
  (void)sink;
}
