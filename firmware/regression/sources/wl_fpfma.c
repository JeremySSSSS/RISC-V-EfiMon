/* DOMINANTE fp_fma: estructura de M1 (operandos CONSTANTES en registros, sin
 * loads dentro del bucle, resultado descartado). fmadd.s. */
#ifndef REPS
#define REPS 40
#endif
void run_workload(void){
  volatile int sink=0;
  float a=1.5f, b=2.25f, c=0.75f, d=3.125f;
  for(int r=0;r<REPS;r++){
    float j;
    asm volatile("fmadd.s %0,%1,%2,%3":"=f"(j):"f"(a),"f"(b),"f"(c));  /* 16 fmadd, operandos constantes */
    asm volatile("fmadd.s %0,%1,%2,%3":"=f"(j):"f"(b),"f"(c),"f"(d));
    asm volatile("fmadd.s %0,%1,%2,%3":"=f"(j):"f"(c),"f"(d),"f"(a));
    asm volatile("fmadd.s %0,%1,%2,%3":"=f"(j):"f"(d),"f"(a),"f"(b));
    asm volatile("fmadd.s %0,%1,%2,%3":"=f"(j):"f"(a),"f"(c),"f"(b));
    asm volatile("fmadd.s %0,%1,%2,%3":"=f"(j):"f"(b),"f"(d),"f"(c));
    asm volatile("fmadd.s %0,%1,%2,%3":"=f"(j):"f"(c),"f"(a),"f"(d));
    asm volatile("fmadd.s %0,%1,%2,%3":"=f"(j):"f"(d),"f"(b),"f"(a));
    asm volatile("fmadd.s %0,%1,%2,%3":"=f"(j):"f"(a),"f"(b),"f"(d));
    asm volatile("fmadd.s %0,%1,%2,%3":"=f"(j):"f"(b),"f"(c),"f"(a));
    asm volatile("fmadd.s %0,%1,%2,%3":"=f"(j):"f"(c),"f"(d),"f"(b));
    asm volatile("fmadd.s %0,%1,%2,%3":"=f"(j):"f"(d),"f"(a),"f"(c));
    asm volatile("fmadd.s %0,%1,%2,%3":"=f"(j):"f"(a),"f"(d),"f"(c));
    asm volatile("fmadd.s %0,%1,%2,%3":"=f"(j):"f"(b),"f"(a),"f"(d));
    asm volatile("fmadd.s %0,%1,%2,%3":"=f"(j):"f"(c),"f"(b),"f"(a));
    asm volatile("fmadd.s %0,%1,%2,%3":"=f"(j):"f"(d),"f"(c),"f"(b));
    sink+=r;
  }
  (void)sink;
}
