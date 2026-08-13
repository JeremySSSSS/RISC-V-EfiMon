/* DOMINANTE MUL (~75%): 16 multiplicaciones bajas (mul) INDEPENDIENTES por
 * elemento, resultado descartado a un registro basura via `asm volatile` (mismo
 * truco que los bucles dominados de M1). 16 ops por load amortizan el overhead
 * (load/xor/branch) -> mul domina. Rompe la colinealidad alu-mul de los mixtos. */
#ifndef REPS
#define REPS 40
#endif
#define N 256
static int A[N]; static int init=0;
void run_workload(void){
  volatile int sink=0;
  if(!init){ for(int i=0;i<N;i++) A[i]=(i*2654435761u)|1; init=1; }
  int c0=0x6c8e9cf5,c1=0x2545f491,c2=0x5bd1e995,c3=0x1b873593,
      c4=0x27d4eb2f,c5=0x165667b1,c6=0x7feb352d,c7=0x846ca68b;
  for(int r=0;r<REPS;r++){
    int junk=0;
    for(int i=0;i<N;i++){
      int v=A[i]^r;
      asm volatile("mul %0,%1,%2":"=r"(junk):"r"(v),"r"(c0));   /* 16 mul independientes */
      asm volatile("mul %0,%1,%2":"=r"(junk):"r"(v),"r"(c1));
      asm volatile("mul %0,%1,%2":"=r"(junk):"r"(v),"r"(c2));
      asm volatile("mul %0,%1,%2":"=r"(junk):"r"(v),"r"(c3));
      asm volatile("mul %0,%1,%2":"=r"(junk):"r"(v),"r"(c4));
      asm volatile("mul %0,%1,%2":"=r"(junk):"r"(v),"r"(c5));
      asm volatile("mul %0,%1,%2":"=r"(junk):"r"(v),"r"(c6));
      asm volatile("mul %0,%1,%2":"=r"(junk):"r"(v),"r"(c7));
      asm volatile("mul %0,%1,%2":"=r"(junk):"r"(v),"r"(c0));
      asm volatile("mul %0,%1,%2":"=r"(junk):"r"(v),"r"(c1));
      asm volatile("mul %0,%1,%2":"=r"(junk):"r"(v),"r"(c2));
      asm volatile("mul %0,%1,%2":"=r"(junk):"r"(v),"r"(c3));
      asm volatile("mul %0,%1,%2":"=r"(junk):"r"(v),"r"(c4));
      asm volatile("mul %0,%1,%2":"=r"(junk):"r"(v),"r"(c5));
      asm volatile("mul %0,%1,%2":"=r"(junk):"r"(v),"r"(c6));
      asm volatile("mul %0,%1,%2":"=r"(junk):"r"(v),"r"(c7));
      sink+=junk;
    }
  }
  (void)sink;
}
