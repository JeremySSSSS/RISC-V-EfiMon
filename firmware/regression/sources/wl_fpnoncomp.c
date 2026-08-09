#ifndef REPS
#define REPS 40
#endif
#define N 128
static float X[N],Y[N],Z[N]; static int init=0;
static void setup(void){ if(!init){ for(int i=0;i<N;i++){X[i]=1.0f+i*0.5f; Y[i]=2.0f+i*0.25f; Z[i]=0.5f+i*0.125f;} init=1; } }
/* combinado dominado por fp_noncomp (+ fp_add + fp_conv) */
void run_workload(void){ setup(); volatile float sink=0; volatile int isink=0;
  for(int r=0;r<REPS;r++){ float k=(float)(r|1);
    for(int i=0;i<N;i++){ float x=X[i]+k,lo=Y[i],hi=Z[i]+8.0f; float a,b,c; int gt;
      asm("fmax.s %0,%1,%2":"=f"(a):"f"(x),"f"(lo));
      asm("fmin.s %0,%1,%2":"=f"(b):"f"(a),"f"(hi));
      asm("fsgnjx.s %0,%1,%1":"=f"(c):"f"(b));
      asm("feq.s %0,%1,%2":"=r"(gt):"f"(b),"f"(hi));                 /* fp_noncomp x4 */
      int gi=(int)c; float gf=(float)gi;                            /* fp_conv */
      sink+=c+(float)gt+gf; isink+=gi; } } (void)sink;(void)isink; }/* fp_add */
