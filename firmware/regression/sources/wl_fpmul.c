#ifndef REPS
#define REPS 40
#endif
#define N 128
static float X[N],Y[N],Z[N]; static int init=0;
static void setup(void){ if(!init){ for(int i=0;i<N;i++){X[i]=1.0f+i*0.5f; Y[i]=2.0f+i*0.25f; Z[i]=0.5f+i*0.125f;} init=1; } }
void run_workload(void){ setup(); volatile float sink=0;
  for(int r=0;r<REPS;r++){ float a=1,b=1,c=1,d=1; float k=(float)(r|1)*1e-3f+1.0001f;
    for(int i=0;i<N;i++){ a=X[i]*k; b=Y[i]*k; c=Z[i]*k; d=X[i]*Y[i]; sink+=a+b+c+d; } }  /* fmul */
  (void)sink; }
