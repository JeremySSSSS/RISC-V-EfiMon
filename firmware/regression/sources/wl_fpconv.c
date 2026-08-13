/* DOMINANTE fp_conv: estructura de M1 (operandos CONSTANTES en registros, sin
 * loads dentro del bucle, resultado descartado). fcvt.w.s / fcvt.s.w (int<->float). */
#ifndef REPS
#define REPS 40
#endif
void run_workload(void){
  volatile int sink=0;
  float a=1.5f, b=2.25f, c=0.75f, d=3.125f;
  int p=3, q=7, s=11, t=17;
  for(int r=0;r<REPS;r++){
    float fj; int ij;
    asm volatile("fcvt.w.s %0,%1":"=r"(ij):"f"(a));  /* 16 fcvt, operandos constantes (int<->float) */
    asm volatile("fcvt.s.w %0,%1":"=f"(fj):"r"(p));
    asm volatile("fcvt.w.s %0,%1":"=r"(ij):"f"(b));
    asm volatile("fcvt.s.w %0,%1":"=f"(fj):"r"(q));
    asm volatile("fcvt.w.s %0,%1":"=r"(ij):"f"(c));
    asm volatile("fcvt.s.w %0,%1":"=f"(fj):"r"(s));
    asm volatile("fcvt.w.s %0,%1":"=r"(ij):"f"(d));
    asm volatile("fcvt.s.w %0,%1":"=f"(fj):"r"(t));
    asm volatile("fcvt.w.s %0,%1":"=r"(ij):"f"(a));
    asm volatile("fcvt.s.w %0,%1":"=f"(fj):"r"(p));
    asm volatile("fcvt.w.s %0,%1":"=r"(ij):"f"(b));
    asm volatile("fcvt.s.w %0,%1":"=f"(fj):"r"(q));
    asm volatile("fcvt.w.s %0,%1":"=r"(ij):"f"(c));
    asm volatile("fcvt.s.w %0,%1":"=f"(fj):"r"(s));
    asm volatile("fcvt.w.s %0,%1":"=r"(ij):"f"(d));
    asm volatile("fcvt.s.w %0,%1":"=f"(fj):"r"(t));
    sink+=r+ij;
  }
  (void)sink;
}
