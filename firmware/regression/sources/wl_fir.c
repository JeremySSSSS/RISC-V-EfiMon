#ifndef REPS
#define REPS 40
#endif
#define N 128
static int x[N]; static int init=0;
static const int C0=0x6c8e9cf5,C1=0x2545f491,C2=0x5bd1e995,C3=0x1b873593;
void run_workload(void){
  volatile int sink=0;
  if(!init){ for(int i=0;i<N;i++) x[i]=(i*2246822519u)|1; init=1; }
  for(int r=0;r<REPS;r++){
    int acc=0;
    for(int i=0;i<N;i++){
      int v=x[i]^r;                                     /* depende de r */
      acc += (int)(((long long)v*C0)>>32);             /* mulh */
      acc += (int)(((long long)v*C1)>>32);             /* mulh */
      acc += (int)(((long long)v*C2)>>32);             /* mulh */
      acc += (int)(((long long)v*C3)>>32);             /* mulh */
    }
    sink+=acc;
  }
  (void)sink;
}
