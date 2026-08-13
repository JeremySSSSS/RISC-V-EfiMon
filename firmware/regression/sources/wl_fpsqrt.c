/* DOMINANTE fp_sqrt: estructura de M1 (operandos CONSTANTES en registros, sin
 * loads dentro del bucle, resultado descartado). fsqrt.s. */
#ifndef REPS
#define REPS 40
#endif
void run_workload(void){
  volatile int sink=0;
  float a=7.5f, b=2.25f, c=0.75f, d=3.125f;
  for(int r=0;r<REPS;r++){
    float j;
    asm volatile("fsqrt.s %0,%1":"=f"(j):"f"(a));  /* 16 fsqrt, operandos constantes */
    asm volatile("fsqrt.s %0,%1":"=f"(j):"f"(b));
    asm volatile("fsqrt.s %0,%1":"=f"(j):"f"(c));
    asm volatile("fsqrt.s %0,%1":"=f"(j):"f"(d));
    asm volatile("fsqrt.s %0,%1":"=f"(j):"f"(a));
    asm volatile("fsqrt.s %0,%1":"=f"(j):"f"(b));
    asm volatile("fsqrt.s %0,%1":"=f"(j):"f"(c));
    asm volatile("fsqrt.s %0,%1":"=f"(j):"f"(d));
    asm volatile("fsqrt.s %0,%1":"=f"(j):"f"(a));
    asm volatile("fsqrt.s %0,%1":"=f"(j):"f"(b));
    asm volatile("fsqrt.s %0,%1":"=f"(j):"f"(c));
    asm volatile("fsqrt.s %0,%1":"=f"(j):"f"(d));
    asm volatile("fsqrt.s %0,%1":"=f"(j):"f"(a));
    asm volatile("fsqrt.s %0,%1":"=f"(j):"f"(b));
    asm volatile("fsqrt.s %0,%1":"=f"(j):"f"(c));
    asm volatile("fsqrt.s %0,%1":"=f"(j):"f"(d));
    sink+=r;
  }
  (void)sink;
}
