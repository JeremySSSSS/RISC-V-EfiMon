/* DOMINANTE ALU (~90%): cadenas de aritmetica/logica sobre registros, sin loads
 * ni ramas internas (loop desenrollado). Para que M2 pueda IDENTIFICAR alu: aqui
 * alu domina claramente, a diferencia de los mixtos donde nunca baja del 43%. */
#ifndef REPS
#define REPS 40
#endif
#define N 64
void run_workload(void){
  volatile int sink=0;
  for(int r=0;r<REPS;r++){
    int a=r|1, b=r^0x5a5a5a5a, c=r+0x12345, d=r*3+7;
    for(int i=0;i<N;i++){
      a=(a^b)+(c<<1);  b=(b+d)^(a>>2);  c=(c^a)+(d<<3);  d=(d+b)^(c>>1);  /* 16 alu */
      a+=c^d;          b^=a+c;          c+=b^d;          d^=a+b;
    }
    sink+=a+b+c+d;
  }
  (void)sink;
}
