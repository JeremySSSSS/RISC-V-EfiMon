/* LIMITADOR / saturacion suave (DSP real): aplica ganancia y satura cada muestra
 *   y = min(max(x*g, LO), HI)
 * Es un soft-clipper de audio / anti-windup de control. fp_noncomp DOMINANTE
 * (fmax/fmin), con fp_mul y fp_conv. Usa min/maxf de GCC -> fmax.s/fmin.s.
 *
 * Patron SEGURO (estilo gray): datos ENTEROS, floats via fcvt (sin flw), sin
 * cadenas largas, resultado entero. -ffp-contract=off. */
#ifndef REPS
#define REPS 8000
#endif
#define N 512
static int X[N];
static int init = 0;

void run_workload(void) {
  volatile int sink = 0;
  if (!init) {
    unsigned s = 0x13579bdfu;
    for (int i = 0; i < N; i++) {
      s = s * 1103515245u + 12345u; X[i] = (int)((s >> 7) & 4095) - 2048;
    }
    init = 1;
  }
  const float LO = -1000.0f, HI = 1000.0f;
  for (int r = 0; r < REPS; r++) {
    int acc = 0;
    float g = 1.0f + (float)(r & 15) * 0.05f;
    for (int i = 0; i < N; i++) {
      float x = (float)X[i];                       /* fcvt.s.w (no flw) */
      float v = x * g;                             /* fmul */
      float y;
      asm("fmax.s %0,%1,%2" : "=f"(y) : "f"(v), "f"(LO));  /* fmax.s directo */
      asm("fmin.s %0,%1,%2" : "=f"(y) : "f"(y), "f"(HI));  /* fmin.s directo */
      acc += (int)y;                               /* fcvt.w.s + acum. entera */
    }
    sink += acc;
  }
  (void)sink;
}
