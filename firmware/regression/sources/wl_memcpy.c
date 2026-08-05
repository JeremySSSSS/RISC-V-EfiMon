/* MEMCPY/STREAM: copia un buffer grande, DESENROLLADO x8. ANCLA de alu-BAJO /
 * mem-ALTO. Clave del desenrollado: las 8 copias por iteracion usan OFFSET
 * INMEDIATO (lw/sw off(base)) -> NO recalculan direccion -> el unico alu es
 * 'i+=8' y el branch, amortizados entre 16 accesos de memoria. Asi mem domina
 * (~80%) en vez de quedar diluido por la aritmetica de indice (con el lazo
 * elemento-a-elemento alu se quedaba en ~57%). Le da PALANCA real al coef de mem
 * y baja la fraccion de alu, que en el resto de programas siempre domina.
 * Entera, sin float -> segura. */
#ifndef REPS
#define REPS 150000
#endif
#define N 512
static volatile int src[N], dst[N];
void run_workload(void){
  for(int r=0;r<REPS;r++){
    for(int i=0;i<N;i+=8){
      dst[i]  =src[i];   dst[i+1]=src[i+1]; dst[i+2]=src[i+2]; dst[i+3]=src[i+3];
      dst[i+4]=src[i+4]; dst[i+5]=src[i+5]; dst[i+6]=src[i+6]; dst[i+7]=src[i+7];
    }
    src[0]=dst[N-1];                              /* dependencia para que no se elimine */
  }
}
