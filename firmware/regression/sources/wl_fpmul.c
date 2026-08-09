#ifndef REPS
#define REPS 40
#endif
#define N 128
static float X[N],Y[N],Z[N]; static int init=0;
static void setup(void){ if(!init){ for(int i=0;i<N;i++){X[i]=1.0f+i*0.5f; Y[i]=2.0f+i*0.25f; Z[i]=0.5f+i*0.125f;} init=1; } }
/* combinado dominado por fp_mul (+ fp_add + fp_noncomp) */
void run_workload(void){ setup(); volatile float sink=0;
  for(int r=0;r<REPS;r++){ float k=(float)(r|1)*1e-3f+1.0f;
    for(int i=0;i<N;i++){ float a=X[i]*k, b=Y[i]*Z[i], c=X[i]*Z[i];  /* fp_mul */
      float m; asm("fmax.s %0,%1,%2":"=f"(m):"f"(a),"f"(b));         /* fp_noncomp */
      sink+=a+b+c+m; } } (void)sink; }                              /* fp_add */
