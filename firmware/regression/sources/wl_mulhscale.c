/* MULHSCALE: escalado en punto fijo Q31 tomando SOLO la palabra alta del
 * producto: (int32)(((int64)a*b)>>32). Cuando unicamente se usa la parte alta,
 * GCC emite MULH sin MUL -> desacopla la pareja mul/mulh, que en el resto del
 * set siempre aparece junta (mulhash64, dotprod) y deja la regresion sin forma
 * de separar sus costos (mul llego a salir negativo). Con matmul (mul solo) y
 * este (mulh dominante), las columnas quedan independientes. Entera, sin
 * float -> segura. */
#ifndef REPS
#define REPS 120000
#endif
#define K 32
static int G[K];
void run_workload(void){
  volatile int sink=0;
  for(int r=0;r<REPS;r++){
    int g=(r|1)<<8;
    for(int i=0;i<K;i++) G[i]=g+i*2654435761u;
    int acc=0;
    for(int i=0;i<K;i++){
      int hi=(int)(((long long)G[i]*(long long)(g^0x5bd1e995))>>32); /* mulh */
      acc+=hi;
      g+=hi|1;
    }
    sink+=acc;
  }
  (void)sink;
}
