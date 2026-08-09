#ifndef REPS
#define REPS 40
#endif
#define N 128
static float X[N],Y[N],Z[N]; static int init=0;
static void setup(void){ if(!init){ for(int i=0;i<N;i++){X[i]=1.0f+i*0.5f; Y[i]=2.0f+i*0.25f; Z[i]=0.5f+i*0.125f;} init=1; } }
/* dominado por fp_div (+ fp_mul + fp_add + fp_conv). RIESGO: fdiv */
void run_workload(void){ setup(); volatile float sink=0; volatile int isink=0;
  for(int r=0;r<REPS;r++){ float k=(float)(r|1);
    for(int i=0;i<N;i++){ float a=X[i]/(Y[i]+1.0f); float b=Z[i]*k;
      int q=(int)a; sink+=a+b+(float)q; isink+=q; } } (void)sink;(void)isink; }
