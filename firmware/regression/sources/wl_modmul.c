#ifndef REPS
#define REPS 40
#endif
#define N 96
static int A[N], B[N]; static int init=0;
void run_workload(void){
  volatile int sink=0;
  if(!init){ for(int i=0;i<N;i++){A[i]=(i*7+1)|1; B[i]=(i*13+3)|1;} init=1; }
  for(int r=0;r<REPS;r++){
    int m=((r&1023)|1)+1000;
    for(int i=0;i<N;i++){
      long long p=(long long)(A[i]^r)*(long long)(B[i]+r);  /* mul+mulh */
      int hi=(int)(p>>32), lo=(int)p;
      sink += (hi^lo) % m;                                   /* div */
    }
  }
  (void)sink;
}
