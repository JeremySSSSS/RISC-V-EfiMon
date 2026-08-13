/* DOMINANTE MULH (~75%): 16 multiplicaciones ALTAS (mulh) INDEPENDIENTES por
 * elemento via `asm volatile` -> mulh PURO (sin el mul bajo del producto de 64
 * bits en C). 16 ops por load amortizan el overhead. Rompe la colinealidad. */
#ifndef REPS
#define REPS 40
#endif
#define N 256
static int A[N]; static int init=0;
void run_workload(void){
  volatile int sink=0;
  if(!init){ for(int i=0;i<N;i++) A[i]=(i*2246822519u)|1; init=1; }
  int c0=0x6c8e9cf5,c1=0x2545f491,c2=0x5bd1e995,c3=0x1b873593,
      c4=0x27d4eb2f,c5=0x165667b1,c6=0x7feb352d,c7=0x846ca68b;
  for(int r=0;r<REPS;r++){
    int junk=0;
    for(int i=0;i<N;i++){
      int v=A[i]^r;
      asm volatile("mulh %0,%1,%2":"=r"(junk):"r"(v),"r"(c0));  /* 16 mulh independientes */
      asm volatile("mulh %0,%1,%2":"=r"(junk):"r"(v),"r"(c1));
      asm volatile("mulh %0,%1,%2":"=r"(junk):"r"(v),"r"(c2));
      asm volatile("mulh %0,%1,%2":"=r"(junk):"r"(v),"r"(c3));
      asm volatile("mulh %0,%1,%2":"=r"(junk):"r"(v),"r"(c4));
      asm volatile("mulh %0,%1,%2":"=r"(junk):"r"(v),"r"(c5));
      asm volatile("mulh %0,%1,%2":"=r"(junk):"r"(v),"r"(c6));
      asm volatile("mulh %0,%1,%2":"=r"(junk):"r"(v),"r"(c7));
      asm volatile("mulh %0,%1,%2":"=r"(junk):"r"(v),"r"(c0));
      asm volatile("mulh %0,%1,%2":"=r"(junk):"r"(v),"r"(c1));
      asm volatile("mulh %0,%1,%2":"=r"(junk):"r"(v),"r"(c2));
      asm volatile("mulh %0,%1,%2":"=r"(junk):"r"(v),"r"(c3));
      asm volatile("mulh %0,%1,%2":"=r"(junk):"r"(v),"r"(c4));
      asm volatile("mulh %0,%1,%2":"=r"(junk):"r"(v),"r"(c5));
      asm volatile("mulh %0,%1,%2":"=r"(junk):"r"(v),"r"(c6));
      asm volatile("mulh %0,%1,%2":"=r"(junk):"r"(v),"r"(c7));
      sink+=junk;
    }
  }
  (void)sink;
}
