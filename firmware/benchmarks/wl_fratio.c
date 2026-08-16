/* fp_div-dominante, carga MIXTA held-out. La FPU de este bitstream SOLO corre
 * fdiv con operandos CONSTANTES en registro (input fresco la cuelga, incluso 1
 * solo; ver fpu_fmadd_restriccion). Las divisiones operan sobre un set fijo de
 * constantes (num/den fijos en registro), envueltas en trabajo ENTERO real que
 * varia por elemento -> mezcla fp_div + alu + mem. Held-out: distinta proporcion
 * que el probe fpdiv de calibracion. Resultado fp descartado; reduccion entera. */
#ifndef REPS
#define REPS 9000
#endif
#define N 512
static int A[N];
static int init = 0;

void run_workload(void) {
  volatile int sink = 0;
  if (!init) {
    unsigned s = 0x2468acefu;
    for (int i = 0; i < N; i++) {
      s = s * 1103515245u + 12345u; A[i] = (int)((s >> 8) & 8191) + 1;
    }
    init = 1;
  }
  const float a = 7.5f, b = 2.25f, c = 0.75f, d = 3.125f;  /* en registros */
  for (int r = 0; r < REPS; r++) {
    int acc = 0;
    for (int i = 0; i < N; i++) {
      int v = A[i];
      int w = (v * 5 - (v >> 3)) + (i & 63);       /* alu real */
      float j;
      asm volatile("fdiv.s %0,%1,%2" : "=f"(j) : "f"(a), "f"(b));  /* fp_div, const/const */
      asm volatile("fdiv.s %0,%1,%2" : "=f"(j) : "f"(a), "f"(c));
      asm volatile("fdiv.s %0,%1,%2" : "=f"(j) : "f"(d), "f"(b));
      asm volatile("fdiv.s %0,%1,%2" : "=f"(j) : "f"(d), "f"(c));
      acc += w ^ (v & 31);                          /* reduccion entera */
    }
    sink += acc;
  }
  (void)sink;
}
