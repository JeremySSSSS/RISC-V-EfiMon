/* DOMINANTE fp_add: replica la estructura del bucle de M1 (fp_add.S) que SI
 * corre en este bitstream: operandos CONSTANTES en registros (sin loads de
 * memoria dentro del bucle) y resultado descartado. La version con `flw` por
 * elemento deadlockeaba la FPU (load-use al FPU). Bucle plano, sin arrays. */
#ifndef REPS
#define REPS 40
#endif
void run_workload(void){
  volatile int sink=0;
  /* 4 operandos constantes en registros FP (como ft0..ft3 de M1) */
  float a=1.5f, b=2.25f, c=0.75f, d=3.125f;
  for(int r=0;r<REPS;r++){
    float j;
    asm volatile("fadd.s %0,%1,%2":"=f"(j):"f"(a),"f"(b));  /* 16 fadd/fsub, operandos CONSTANTES */
    asm volatile("fsub.s %0,%1,%2":"=f"(j):"f"(c),"f"(d));
    asm volatile("fadd.s %0,%1,%2":"=f"(j):"f"(a),"f"(c));
    asm volatile("fsub.s %0,%1,%2":"=f"(j):"f"(b),"f"(d));
    asm volatile("fadd.s %0,%1,%2":"=f"(j):"f"(a),"f"(d));
    asm volatile("fsub.s %0,%1,%2":"=f"(j):"f"(b),"f"(c));
    asm volatile("fadd.s %0,%1,%2":"=f"(j):"f"(c),"f"(a));
    asm volatile("fsub.s %0,%1,%2":"=f"(j):"f"(d),"f"(b));
    asm volatile("fadd.s %0,%1,%2":"=f"(j):"f"(a),"f"(b));
    asm volatile("fsub.s %0,%1,%2":"=f"(j):"f"(c),"f"(d));
    asm volatile("fadd.s %0,%1,%2":"=f"(j):"f"(a),"f"(c));
    asm volatile("fsub.s %0,%1,%2":"=f"(j):"f"(b),"f"(d));
    asm volatile("fadd.s %0,%1,%2":"=f"(j):"f"(a),"f"(d));
    asm volatile("fsub.s %0,%1,%2":"=f"(j):"f"(b),"f"(c));
    asm volatile("fadd.s %0,%1,%2":"=f"(j):"f"(c),"f"(a));
    asm volatile("fsub.s %0,%1,%2":"=f"(j):"f"(d),"f"(b));
    sink+=r;
  }
  (void)sink;
}
