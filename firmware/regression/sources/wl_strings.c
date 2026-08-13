/* STRINGS: strlen + memcpy + compara — MEM (loads/stores) + CTRL + ALU. */
#ifndef REPS
#define REPS 200000
#endif
#define SLEN 64
static char src[SLEN], dst[SLEN];
void run_workload(void){
  volatile int sink=0;
  for(int r=0;r<REPS;r++){
    for(int i=0;i<SLEN-1;i++) src[i]=(char)('A'+((i+r)&31)); src[SLEN-1]=0;
    int len=0; while(src[len]) len++;
    for(int i=0;i<=len;i++) dst[i]=src[i];
    int d=0; for(int i=0;i<len;i++) d+=(dst[i]!=src[i]);
    sink+=len+d;
  }
  (void)sink;
}
