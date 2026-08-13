/* DOMINANTE fp_mul: estructura de M1 (operandos CONSTANTES en registros, sin
 * loads dentro del bucle, resultado descartado). El flw por elemento
 * deadlockeaba la FPU de este bitstream. */
#ifndef REPS
#define REPS 40
#endif
void run_workload(void){
  volatile int sink=0;
  float a=1.5f, b=2.25f, c=0.75f, d=3.125f;
  for(int r=0;r<REPS;r++){
    float j;
    asm volatile("fmul.s %0,%1,%2":"=f"(j):"f"(a),"f"(b));  /* 16 fmul, operandos constantes */
    asm volatile("fmul.s %0,%1,%2":"=f"(j):"f"(c),"f"(d));
    asm volatile("fmul.s %0,%1,%2":"=f"(j):"f"(a),"f"(c));
    asm volatile("fmul.s %0,%1,%2":"=f"(j):"f"(b),"f"(d));
    asm volatile("fmul.s %0,%1,%2":"=f"(j):"f"(a),"f"(d));
    asm volatile("fmul.s %0,%1,%2":"=f"(j):"f"(b),"f"(c));
    asm volatile("fmul.s %0,%1,%2":"=f"(j):"f"(c),"f"(a));
    asm volatile("fmul.s %0,%1,%2":"=f"(j):"f"(d),"f"(b));
    asm volatile("fmul.s %0,%1,%2":"=f"(j):"f"(a),"f"(b));
    asm volatile("fmul.s %0,%1,%2":"=f"(j):"f"(c),"f"(d));
    asm volatile("fmul.s %0,%1,%2":"=f"(j):"f"(a),"f"(c));
    asm volatile("fmul.s %0,%1,%2":"=f"(j):"f"(b),"f"(d));
    asm volatile("fmul.s %0,%1,%2":"=f"(j):"f"(a),"f"(d));
    asm volatile("fmul.s %0,%1,%2":"=f"(j):"f"(b),"f"(c));
    asm volatile("fmul.s %0,%1,%2":"=f"(j):"f"(c),"f"(a));
    asm volatile("fmul.s %0,%1,%2":"=f"(j):"f"(d),"f"(b));
    sink+=r;
  }
  (void)sink;
}
