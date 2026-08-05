#ifndef REPS
#define REPS 40
#endif
void run_workload(void){
  volatile long long sink=0;
  for(int r=0;r<REPS;r++){
    unsigned x=1000000007u^((unsigned)r*2654435761u), y=(0x9e3779b9u|1);
    long long h1=1,h2=0,k1=0,k2=1;
    for(int i=0;i<24 && y;i++){
      unsigned a=x/y;                    /* div */
      unsigned t=x-a*y;                  /* mul low */
      x=y; y=t;
      long long h=(long long)a*h1+h2;    /* mul+mulh */
      long long k=(long long)a*k1+k2;    /* mul+mulh */
      h2=h1; h1=h; k2=k1; k1=k;
    }
    sink+=h1^k1;
  }
  (void)sink;
}
