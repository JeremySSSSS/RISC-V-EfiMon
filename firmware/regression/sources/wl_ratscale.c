#ifndef REPS
#define REPS 40
#endif
#define N 96
static int A[N]; static int init=0;
void run_workload(void){
  volatile int sink=0;
  if(!init){ for(int i=0;i<N;i++) A[i]=(int)(((unsigned)i*1103515245u+12345u)|1u); init=1; }
  for(int r=0;r<REPS;r++){
    int d=(r&255)+3;
    for(int i=0;i<N;i++){
      int hi=(int)(((long long)(A[i]^r)*1140671485LL)>>32);  /* mulh */
      int hj=(int)(((long long)(A[i]+r)*134775813LL)>>32);   /* mulh */
      sink += (hi/d) + (hj/d);                                /* div x2 */
    }
  }
  (void)sink;
}
