#ifndef REPS
#define REPS 40
#endif
#define N 256
static int A[N]; static int init=0;
static const int C[8]={0x6c8e9cf5,0x2545f491,0x5bd1e995,0x1b873593,0x27d4eb2f,0x165667b1,0x85ebca6b,0xc2b2ae35};
void run_workload(void){
  volatile int sink=0;
  if(!init){ for(int i=0;i<N;i++) A[i]=(i*2246822519u)|1; init=1; }
  for(int r=0;r<REPS;r++){
    int acc=0;
    for(int i=0;i<N;i++){
      int v=A[i]^r;
      acc+=(int)(((long long)v*C[0])>>32); acc+=(int)(((long long)v*C[1])>>32);
      acc+=(int)(((long long)v*C[2])>>32); acc+=(int)(((long long)v*C[3])>>32);
      acc+=(int)(((long long)v*C[4])>>32); acc+=(int)(((long long)v*C[5])>>32);
      acc+=(int)(((long long)v*C[6])>>32); acc+=(int)(((long long)v*C[7])>>32);  /* 8 mulh */
    }
    sink+=acc;
  }
  (void)sink;
}
