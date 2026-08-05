#ifndef REPS
#define REPS 40
#endif
#define N 512
static int A[N];
void run_workload(void){
  volatile int sink=0;
  for(int r=0;r<REPS;r++){
    int v=(r*2654435761u)|1;
    for(int i=0;i<N;i+=16){
      A[i+0]=v;  A[i+1]=v;  A[i+2]=v;  A[i+3]=v;
      A[i+4]=v;  A[i+5]=v;  A[i+6]=v;  A[i+7]=v;
      A[i+8]=v;  A[i+9]=v;  A[i+10]=v; A[i+11]=v;
      A[i+12]=v; A[i+13]=v; A[i+14]=v; A[i+15]=v;   /* 16 stores, offset inmediato */
    }
    sink+=A[r&(N-1)];
  }
  (void)sink;
}
