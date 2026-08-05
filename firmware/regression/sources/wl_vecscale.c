/* VECSCALE: escalado/clamp de un vector float -> entero. FLOAT (fmul + fadd con
 * constantes) + MEM (loads float) + ALU/CTRL. Patron INDEPENDIENTE como dotprod:
 * cada elemento es (int)(x[i]*scale + bias), SIN acumulador flotante en cadena
 * (la suma final va en entero) -> NO cuelga la FPU de este bitstream. Mezcla
 * float DISTINTA a dotprod (alli es producto punto; aqui es map elemento a
 * elemento con fmul+fadd por muestra). */
#ifndef REPS
#define REPS 300000
#endif
#define N 64
static float x[N];
void run_workload(void){
  volatile int sink=0;
  const float scale=1.25f, bias=0.5f;
  for(int r=0;r<REPS;r++){
    for(int i=0;i<N;i++) x[i]=(float)(((i*7+r)&255)-128);
    int acc=0;
    for(int i=0;i<N;i++){
      float v=x[i]*scale+bias;            /* fmul + fadd, ambos independientes por i */
      acc+=(int)v;                        /* fcvt; acumulacion en ENTERO, sin cadena fp */
    }
    sink+=acc;
  }
  (void)sink;
}
