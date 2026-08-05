/* GCD + modular: Euclides (%) y divisiones — DIV/REM pesado + ALU + CTRL. */
#ifndef REPS
#define REPS 30000
#endif
static int gcd(int a,int b){ while(b){int t=a%b;a=b;b=t;} return a; }
void run_workload(void){
  volatile int sink=0;
  for(int r=0;r<REPS;r++){
    int acc=0;
    for(int i=1;i<=40;i++){
      int x=(i*9973+r*7)|1, y=(i*4099+r*3)|1;
      acc+=gcd(x,y);
      acc+= x % (y|1);
      acc+= (x*131) / (y|7);
    }
    sink+=acc;
  }
  (void)sink;
}
