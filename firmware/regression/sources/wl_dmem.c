/* DOMINANTE MEM (~95%): stores con offset inmediato, MUY desenrollado (32 por
 * bloque) para que la indexacion/branch alu pese <5%. SOLO stores (sin loads:
 * la version load+store colgaba el JTAG). Da a la regresion de efimon un punto
 * con mem ALTO y alu ~0 -> rompe la colinealidad mem-alu (que hace que efimon
 * subvalue mem, absorbido por alu). Corre a d100 como los otros dominantes. */
#ifndef REPS
#define REPS 40
#endif
#define N 512
static int A[N];
void run_workload(void){
  volatile int sink=0;
  for(int r=0;r<REPS;r++){
    int v=(r*2654435761u)|1;
    for(int i=0;i<N;i+=32){
      A[i+0]=v;  A[i+1]=v;  A[i+2]=v;  A[i+3]=v;  A[i+4]=v;  A[i+5]=v;  A[i+6]=v;  A[i+7]=v;
      A[i+8]=v;  A[i+9]=v;  A[i+10]=v; A[i+11]=v; A[i+12]=v; A[i+13]=v; A[i+14]=v; A[i+15]=v;
      A[i+16]=v; A[i+17]=v; A[i+18]=v; A[i+19]=v; A[i+20]=v; A[i+21]=v; A[i+22]=v; A[i+23]=v;
      A[i+24]=v; A[i+25]=v; A[i+26]=v; A[i+27]=v; A[i+28]=v; A[i+29]=v; A[i+30]=v; A[i+31]=v;
    }
    sink+=A[r&(N-1)];
  }
  (void)sink;
}
