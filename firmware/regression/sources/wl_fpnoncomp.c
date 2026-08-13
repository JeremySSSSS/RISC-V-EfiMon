/* DOMINANTE fp_noncomp: estructura de M1 (operandos CONSTANTES en registros, sin
 * loads dentro del bucle, resultado descartado). fmax/fmin/fsgnj/feq/fabs. */
#ifndef REPS
#define REPS 40
#endif
void run_workload(void){
  volatile int sink=0;
  float a=1.5f, b=2.25f, c=0.75f, d=3.125f;
  for(int r=0;r<REPS;r++){
    float j; int e;
    asm volatile("fmax.s  %0,%1,%2":"=f"(j):"f"(a),"f"(b));  /* 16 fp_noncomp, operandos constantes */
    asm volatile("fmin.s  %0,%1,%2":"=f"(j):"f"(a),"f"(c));
    asm volatile("fsgnj.s %0,%1,%2":"=f"(j):"f"(b),"f"(c));
    asm volatile("fsgnjx.s %0,%1,%2":"=f"(j):"f"(b),"f"(a));
    asm volatile("fmax.s  %0,%1,%2":"=f"(j):"f"(d),"f"(a));
    asm volatile("fmin.s  %0,%1,%2":"=f"(j):"f"(d),"f"(b));
    asm volatile("fabs.s  %0,%1":"=f"(j):"f"(a));
    asm volatile("fneg.s  %0,%1":"=f"(j):"f"(b));
    asm volatile("feq.s   %0,%1,%2":"=r"(e):"f"(a),"f"(b));
    asm volatile("flt.s   %0,%1,%2":"=r"(e):"f"(a),"f"(c));
    asm volatile("fle.s   %0,%1,%2":"=r"(e):"f"(b),"f"(c));
    asm volatile("fmax.s  %0,%1,%2":"=f"(j):"f"(a),"f"(d));
    asm volatile("fmin.s  %0,%1,%2":"=f"(j):"f"(b),"f"(a));
    asm volatile("fsgnj.s %0,%1,%2":"=f"(j):"f"(d),"f"(a));
    asm volatile("fmax.s  %0,%1,%2":"=f"(j):"f"(b),"f"(d));
    asm volatile("feq.s   %0,%1,%2":"=r"(e):"f"(d),"f"(b));
    sink+=r+e;
  }
  (void)sink;
}
