#ifndef REPS
#define REPS 40
#endif
#define N 128
static float X[N],Y[N],Z[N]; static int init=0;
static void setup(void){ if(!init){ for(int i=0;i<N;i++){X[i]=1.0f+i*0.5f; Y[i]=2.0f+i*0.25f; Z[i]=0.5f+i*0.125f;} init=1; } }
/* combinado dominado por fp_conv (+ fp_add + fp_mul) */
void run_workload(void){ setup(); volatile float sink=0; volatile int isink=0;
  for(int r=0;r<REPS;r++){ float k=(float)(r|1);
    for(int i=0;i<N;i++){ int a=(int)(X[i]+k); float af=(float)a;    /* fp_conv */
      int b=(int)Y[i]; float bf=(float)b;                           /* fp_conv */
      float p=Z[i]*bf;                                              /* fp_mul */
      sink+=af+bf+p; isink+=a+b; } } (void)sink;(void)isink; }      /* fp_add */
