#ifndef REPS
#define REPS 40
#endif
#define N 128
static int A[N], B[N]; static int init=0;
void run_workload(void){
  volatile long long sink=0;
  if(!init){ for(int i=0;i<N;i++){A[i]=(i*2654435761u)|1; B[i]=(i*40503+7)|1;} init=1; }
  for(int r=0;r<REPS;r++){
    long long acc=0; int k=(r|1);
    for(int i=0;i<N;i++) acc += (long long)(A[i]^k)*(long long)(B[i]+k); /* mul+mulh */
    sink+=acc;
  }
  (void)sink;
}
