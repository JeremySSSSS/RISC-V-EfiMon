#ifndef REPS
#define REPS 40
#endif
#define N 128
static float X[N],Y[N],Z[N]; static int init=0;
static void setup(void){ if(!init){ for(int i=0;i<N;i++){X[i]=1.0f+i*0.5f; Y[i]=2.0f+i*0.25f; Z[i]=0.5f+i*0.125f;} init=1; } }
/* combinado dominado por fp_add (+ fp_mul + fp_conv) */
void run_workload(void){ setup(); volatile float sink=0; volatile int isink=0;
  for(int r=0;r<REPS;r++){ float k=(float)(r|1);
    for(int i=0;i<N;i++){ float s1=X[i]+k, s2=Y[i]-k, s3=X[i]+Z[i];  /* fp_add */
      float p=X[i]*Y[i];                                             /* fp_mul */
      int q=(int)s1; float qf=(float)q;                              /* fp_conv */
      sink+=s1+s2+s3+p+qf; isink+=q; } } (void)sink;(void)isink; }
