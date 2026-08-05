/* MULHASH64: hash multiplicativo de 64 bits (estilo fmix de MurmurHash). Cada
 * h *= constante64 sobre rv32 se expande a varias mul + mulh -> ALTA fraccion de
 * MULH (la categoria que solo aparecia en 1 programa). La cadena serial entera
 * (h depende del previo) NO cuelga: el deadlock es SOLO de la FPU, no del entero.
 * Sin float -> segura. */
#ifndef REPS
#define REPS 80000
#endif
#define K 64
void run_workload(void){
  volatile unsigned long long sink=0;
  for(int r=0;r<REPS;r++){
    unsigned long long h=(unsigned long long)r ^ 0x9e3779b97f4a7c15ULL;
    for(int i=0;i<K;i++){
      h ^= h >> 33;
      h *= 0xff51afd7ed558ccdULL;                 /* mul + mulh (64-bit) */
      h ^= h >> 29;
      h *= 0xc4ceb9fe1a85ec53ULL;                 /* mul + mulh (64-bit) */
    }
    sink += h;
  }
  (void)sink;
}
