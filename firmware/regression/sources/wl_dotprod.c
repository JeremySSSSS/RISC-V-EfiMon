/* DOTPROD: producto punto entero de 64 bits (mul+mulh) y producto punto
 * float independiente (-ffp-contract=off, sin fmadd) -- MUL/MULH + FLOAT
 * + MEM + ALU. */
#ifndef REPS
#define REPS 120000
#endif
#define N 32
static int ia[N], ib[N];
static float fa[N], fb[N];
void run_workload(void){
  volatile long long sink=0;
  for(int r=0;r<REPS;r++){
    for(int i=0;i<N;i++){
      ia[i]=((i*5+r)&63)-32;
      ib[i]=((i*11+r*3)&63)-32;
      fa[i]=(float)ia[i]*0.5f;
      fb[i]=(float)ib[i]*0.25f;
    }
    long long acc=0;
    for(int i=0;i<N;i++)
      acc += (long long)ia[i]*(long long)ib[i];   /* mul + mulh */

    int fsum=0;
    for(int i=0;i<N;i++)
      fsum += (int)(fa[i]*fb[i]);                 /* float independiente, sin cadena */

    sink = acc + fsum;
  }
  (void)sink;
}
