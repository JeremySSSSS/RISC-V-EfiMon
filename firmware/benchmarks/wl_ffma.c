/* GANANCIA FIJA por muestra (DSP real): aplica una recta de calibracion con
 * ganancia y offset CONSTANTES:  y = GAIN*x + OFFSET.  Es la version mas cercana
 * al probe fpfma de M2 que SI corrio: dos de los tres operandos del fmadd son
 * CONSTANTES en registros (GAIN, OFFSET, cargados una vez), solo x cambia por
 * muestra. Asi el fmadd no reordena tres operandos frescos de fcvt (lo que
 * colgaba). fp_fma via __builtin_fmaf (fmadd.s aun con -ffp-contract=off).
 * Estructura de gray: datos ENTEROS -> fcvt (sin flw) -> resultado entero. */
#ifndef REPS
#define REPS 8000
#endif
#define N 512
static int X[N];
static int init = 0;

void run_workload(void) {
  volatile int sink = 0;
  if (!init) {
    unsigned s = 0x0badf00du;
    for (int i = 0; i < N; i++) {
      s = s * 1103515245u + 12345u; X[i] = (int)((s >> 8) & 4095) - 2048;
    }
    init = 1;
  }
  const float GAIN = 1.375f, OFFSET = 12.5f;   /* constantes -> quedan en registros */
  for (int r = 0; r < REPS; r++) {
    int acc = 0;
    for (int i = 0; i < N; i++) {
      float x = (float)X[i];                    /* fcvt.s.w (unico operando fresco) */
      float y = __builtin_fmaf(GAIN, x, OFFSET);/* fmadd.s: GAIN*x + OFFSET */
      acc += (int)y;                            /* fcvt.w.s */
    }
    sink += acc;
  }
  (void)sink;
}
