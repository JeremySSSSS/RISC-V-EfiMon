#ifndef REPS
#define REPS 40
#endif
#define N 128
static float X[N],Y[N],Z[N]; static int init=0;
static void setup(void){ if(!init){ for(int i=0;i<N;i++){X[i]=1.0f+i*0.5f; Y[i]=2.0f+i*0.25f; Z[i]=0.5f+i*0.125f;} init=1; } }
/* dominado por fp_fma (+ fp_mul + fp_add). RIESGO: cadena fmadd */
void run_workload(void){ setup(); volatile float sink=0;
  for(int r=0;r<REPS;r++){ float k=(float)(r|1)*1e-3f;
    for(int i=0;i<N;i++){ float a=__builtin_fmaf(X[i],Y[i],k);
      float b=__builtin_fmaf(Y[i],Z[i],k); float c=X[i]*Z[i];
      sink+=a+b+c; } } (void)sink; }
