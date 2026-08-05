/* FPOLY: varios productos float INDEPENDIENTES por elemento, acumulados en ENTERO.
 * 3.er programa con float. CLAVE (corrige el cuelgue anterior): la FPU de este
 * bitstream se traba con cadenas de dependencia FP profundas (>=3 ops FP en
 * cadena). La version polinomio (xi*xi*c + xi*c + c) encadenaba fmul->fmul->fadd
 * ->fadd (profundidad 4) y COLGABA. Aqui cada termino es un fmul AISLADO (prof. 1)
 * seguido de un fcvt (prof. 2); NADA de fadd->fadd ni fmul->fadd->fadd. La suma va
 * en entero. Mismo patron seguro que vecscale/dotprod. -ffp-contract=off (sin fmadd). */
#ifndef REPS
#define REPS 200000
#endif
#define N 64
static float x[N];
void run_workload(void){
  volatile int sink=0;
  for(int r=0;r<REPS;r++){
    for(int i=0;i<N;i++) x[i]=(float)(((i*5+r)&127)-64);
    int acc=0;
    for(int i=0;i<N;i++){
      float xi=x[i];
      float a = xi*xi;          /* fmul, prof.1 */
      float b = xi*1.5f;        /* fmul, prof.1 (independiente de a) */
      float c = xi*0.25f;       /* fmul, prof.1 (independiente) */
      acc += (int)a + (int)b + (int)c;   /* 3 fcvt prof.2; suma en ENTERO */
    }
    sink+=acc;
  }
  (void)sink;
}
