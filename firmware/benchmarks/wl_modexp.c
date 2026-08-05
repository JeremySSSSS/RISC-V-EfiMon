#ifndef REPS
#define REPS 40
#endif
typedef unsigned u32; typedef unsigned long long u64;
static u32 monmul(u32 a,u32 b,u32 n,u32 ninv){
  u64 t=(u64)a*b;                 /* mul+mulh */
  u32 m=(u32)t*ninv;              /* mul */
  u64 u=(t+(u64)m*n)>>32;         /* mul+mulh */
  if(u>=n) u-=n;
  return (u32)u;
}
void run_workload(void){
  volatile u32 sink=0;
  u32 n=0xF0000F1u|1;
  u32 ninv=n; for(int i=0;i<5;i++) ninv*= 2u-n*ninv;  /* -n^-1 mod 2^32 (Newton) */
  ninv=(u32)-ninv;
  for(int r=0;r<REPS;r++){
    u32 base=(0x9e3779b9u^(u32)r)|1, acc=1u; u32 e=0x10001u;
    while(e){ if(e&1) acc=monmul(acc,base,n,ninv); base=monmul(base,base,n,ninv); e>>=1; }
    sink^=acc;
  }
  (void)sink;
}
