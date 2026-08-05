#ifndef REPS
#define REPS 40
#endif
#define L 64
static unsigned short num[L]; static int init=0;
void run_workload(void){
  volatile unsigned sink=0;
  if(!init){ for(int i=0;i<L;i++) num[i]=(i*40503+7)&0xffff; init=1; }
  for(int r=0;r<REPS;r++){
    unsigned d=((r&0x3fff)|1)+3, rem=0;
    for(int i=L-1;i>=0;i--){
      unsigned acc=(rem<<16)|num[i];   /* 32b */
      unsigned q=acc/d;                /* div */
      rem=acc-q*d;                     /* mul (low) */
      sink^=q;
    }
  }
  (void)sink;
}
