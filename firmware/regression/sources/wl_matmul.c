/* MATMUL: multiplicacion de matrices enteras — MUL pesado + MEM + ALU + CTRL. */
#ifndef REPS
#define REPS 6000
#endif
#define M 12
static int A[M][M],B[M][M],C[M][M];
void run_workload(void){
  volatile int sink=0;
  for(int r=0;r<REPS;r++){
    for(int i=0;i<M;i++)for(int j=0;j<M;j++){A[i][j]=(i*7+j+r)&63;B[i][j]=(i+j*3+r)&63;}
    for(int i=0;i<M;i++)for(int j=0;j<M;j++){int s=0;for(int k=0;k<M;k++)s+=A[i][k]*B[k][j];C[i][j]=s;}
    sink+=C[0][0]+C[M-1][M-1];
  }
  (void)sink;
}
