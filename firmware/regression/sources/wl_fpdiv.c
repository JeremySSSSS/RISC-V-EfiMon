/* DOMINANTE fp_div: estructura de M1 (operandos CONSTANTES en registros, sin
 * loads dentro del bucle, resultado descartado). fdiv.s. */
#ifndef REPS
#define REPS 40
#endif
void run_workload(void){
  volatile int sink=0;
  float a=7.5f, b=2.25f, c=0.75f, d=3.125f;
  for(int r=0;r<REPS;r++){
    float j;
    asm volatile("fdiv.s %0,%1,%2":"=f"(j):"f"(a),"f"(b));  /* 16 fdiv, operandos constantes */
    asm volatile("fdiv.s %0,%1,%2":"=f"(j):"f"(a),"f"(c));
    asm volatile("fdiv.s %0,%1,%2":"=f"(j):"f"(a),"f"(d));
    asm volatile("fdiv.s %0,%1,%2":"=f"(j):"f"(b),"f"(c));
    asm volatile("fdiv.s %0,%1,%2":"=f"(j):"f"(b),"f"(d));
    asm volatile("fdiv.s %0,%1,%2":"=f"(j):"f"(d),"f"(c));
    asm volatile("fdiv.s %0,%1,%2":"=f"(j):"f"(a),"f"(b));
    asm volatile("fdiv.s %0,%1,%2":"=f"(j):"f"(a),"f"(c));
    asm volatile("fdiv.s %0,%1,%2":"=f"(j):"f"(a),"f"(d));
    asm volatile("fdiv.s %0,%1,%2":"=f"(j):"f"(b),"f"(c));
    asm volatile("fdiv.s %0,%1,%2":"=f"(j):"f"(b),"f"(d));
    asm volatile("fdiv.s %0,%1,%2":"=f"(j):"f"(d),"f"(c));
    asm volatile("fdiv.s %0,%1,%2":"=f"(j):"f"(a),"f"(b));
    asm volatile("fdiv.s %0,%1,%2":"=f"(j):"f"(a),"f"(c));
    asm volatile("fdiv.s %0,%1,%2":"=f"(j):"f"(a),"f"(d));
    asm volatile("fdiv.s %0,%1,%2":"=f"(j):"f"(b),"f"(c));
    sink+=r;
  }
  (void)sink;
}
