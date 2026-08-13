/* DOMINANTE DIV (~75%): 16 divisiones/restos INDEPENDIENTES por elemento via
 * `asm volatile` (div y rem son de la misma categoria). Resultado descartado.
 * 16 ops por load amortizan el overhead. El clasificador cuenta INSTRUCCIONES
 * (n_div), no ciclos, asi que la latencia alta del divisor no afecta la mezcla. */
#ifndef REPS
#define REPS 40
#endif
#define N 128
static int A[N]; static int init=0;
void run_workload(void){
  volatile int sink=0;
  if(!init){ for(int i=0;i<N;i++) A[i]=(int)((i*2654435761u)|0x40000001u); init=1; }
  int d0=0x00037a1,d1=0x0001f3b,d2=0x0002d59,d3=0x0000a2f,
      d4=0x0004bc7,d5=0x00011e5,d6=0x0003fd1,d7=0x0000e6b;
  for(int r=0;r<REPS;r++){
    int junk=0;
    for(int i=0;i<N;i++){
      int v=A[i]^(r<<8);
      asm volatile("div  %0,%1,%2":"=r"(junk):"r"(v),"r"(d0));  /* 8 div + 8 rem indep. */
      asm volatile("rem  %0,%1,%2":"=r"(junk):"r"(v),"r"(d1));
      asm volatile("div  %0,%1,%2":"=r"(junk):"r"(v),"r"(d2));
      asm volatile("rem  %0,%1,%2":"=r"(junk):"r"(v),"r"(d3));
      asm volatile("div  %0,%1,%2":"=r"(junk):"r"(v),"r"(d4));
      asm volatile("rem  %0,%1,%2":"=r"(junk):"r"(v),"r"(d5));
      asm volatile("div  %0,%1,%2":"=r"(junk):"r"(v),"r"(d6));
      asm volatile("rem  %0,%1,%2":"=r"(junk):"r"(v),"r"(d7));
      asm volatile("div  %0,%1,%2":"=r"(junk):"r"(v),"r"(d1));
      asm volatile("rem  %0,%1,%2":"=r"(junk):"r"(v),"r"(d2));
      asm volatile("div  %0,%1,%2":"=r"(junk):"r"(v),"r"(d3));
      asm volatile("rem  %0,%1,%2":"=r"(junk):"r"(v),"r"(d4));
      asm volatile("div  %0,%1,%2":"=r"(junk):"r"(v),"r"(d5));
      asm volatile("rem  %0,%1,%2":"=r"(junk):"r"(v),"r"(d6));
      asm volatile("div  %0,%1,%2":"=r"(junk):"r"(v),"r"(d7));
      asm volatile("rem  %0,%1,%2":"=r"(junk):"r"(v),"r"(d0));
      sink+=junk;
    }
  }
  (void)sink;
}
