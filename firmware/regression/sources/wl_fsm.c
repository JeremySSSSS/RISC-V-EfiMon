/* BRANCHY: lazo dominado por RAMAS data-dependent sobre un arreglo precalculado.
 * ANCLA de ctrl-ALTO / alu-bajo. Clave (corrige el alu=65% anterior): el lazo
 * caliente NO tiene el LCG (s*c+c = mul+add) -> los datos se generan UNA vez antes;
 * el cuerpo solo hace load + cadena de if/else (branches) + un acc. Desenrollado x8
 * para amortizar el i+=8 -> el alu del indice se diluye entre 8 ramas. Asi ctrl
 * (+ algo de mem) domina en vez de alu. Entera, sin float -> segura. */
#ifndef REPS
#define REPS 150000
#endif
#define K 512
static signed char d[K];
static int filled;
static inline int classify(signed char v){    /* 3-4 branches, sin alu pesado */
  if(v < -32) return -2;
  else if(v < 0) return -1;
  else if(v < 32) return 1;
  else return 2;
}
void run_workload(void){
  if(!filled){                                 /* genera los datos UNA vez (fuera del hot loop) */
    unsigned s=0x12345;
    for(int i=0;i<K;i++){ s=s*1103515245u+12345u; d[i]=(signed char)(s>>20); }
    filled=1;
  }
  volatile int sink=0;
  for(int r=0;r<REPS;r++){
    int acc=0;
    for(int i=0;i<K;i+=8){
      acc+=classify(d[i]);   acc+=classify(d[i+1]); acc+=classify(d[i+2]); acc+=classify(d[i+3]);
      acc+=classify(d[i+4]); acc+=classify(d[i+5]); acc+=classify(d[i+6]); acc+=classify(d[i+7]);
    }
    sink+=acc;
  }
  (void)sink;
}
