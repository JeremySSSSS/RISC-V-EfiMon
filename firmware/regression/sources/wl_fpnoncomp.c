#ifndef REPS
#define REPS 40
#endif
#define N 128
static float X[N],Y[N],Z[N]; static int init=0;
static void setup(void){ if(!init){ for(int i=0;i<N;i++){X[i]=1.0f+i*0.5f; Y[i]=2.0f+i*0.25f; Z[i]=0.5f+i*0.125f;} init=1; } }
void run_workload(void){ setup(); volatile float sink=0;
  for(int r=0;r<REPS;r++){ float k=(float)(r|1);
    for(int i=0;i<N;i++){ float x=X[i]+k,y=Y[i]; float mx,mn,ab; int eq;
      asm("fmax.s %0,%1,%2":"=f"(mx):"f"(x),"f"(y));
      asm("fmin.s %0,%1,%2":"=f"(mn):"f"(x),"f"(y));
      asm("fsgnjx.s %0,%1,%1":"=f"(ab):"f"(x));      /* |x| */
      asm("feq.s %0,%1,%2":"=r"(eq):"f"(x),"f"(y));
      sink+=mx+mn+ab+(float)eq; } } (void)sink; }
