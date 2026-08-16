/* fp_sqrt-dominante, carga MIXTA held-out. La FPU de este bitstream SOLO corre
 * fsqrt con operandos CONSTANTES en registro (cualquier input fresco la cuelga;
 * ver fpu_fmadd_restriccion). Asi que las raices operan sobre un set fijo de
 * constantes (k0..k3, cargadas una vez), pero envueltas en trabajo ENTERO real
 * que varia por elemento (indexado por datos) -> mezcla fp_sqrt + alu + mem + ctrl.
 * Held-out: distinta proporcion y estructura que el probe fpsqrt de calibracion
 * (que era fp casi pura). Resultado fp descartado; reduccion entera. */
#ifndef REPS
#define REPS 9000
#endif
#define N 512
static int A[N];
static int init = 0;

void run_workload(void) {
  volatile int sink = 0;
  if (!init) {
    unsigned s = 0x1234567u;
    for (int i = 0; i < N; i++) {
      s = s * 1103515245u + 12345u; A[i] = (int)((s >> 9) & 8191) + 1;
    }
    init = 1;
  }
  const float k0 = 7.5f, k1 = 2.25f, k2 = 0.75f, k3 = 3.125f;  /* en registros */
  for (int r = 0; r < REPS; r++) {
    int acc = 0;
    for (int i = 0; i < N; i++) {
      int v = A[i];
      int w = (v * 3 + (v >> 2)) ^ (i << 1);      /* alu real (mul/shift/xor) */
      float j;
      asm volatile("fsqrt.s %0,%1" : "=f"(j) : "f"(k0));   /* fp_sqrt, operandos const */
      asm volatile("fsqrt.s %0,%1" : "=f"(j) : "f"(k1));
      asm volatile("fsqrt.s %0,%1" : "=f"(j) : "f"(k2));
      asm volatile("fsqrt.s %0,%1" : "=f"(j) : "f"(k3));
      acc += w - (v & 15);                          /* reduccion entera */
    }
    sink += acc;
  }
  (void)sink;
}
