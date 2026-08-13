/* SAXPY [RETIRADO de la calibracion]: NO TERMINA en este bitstream ni con
 * el patron de vecscale --- la FPU de este bitstream no tolera este kernel
 * (modo de falla conocido, ver 6.1 del documento). Se conserva por si se
 * retoma con un bitstream con FPU sana.
 *
 * Original: C[i] = A[i]*s + B[i] sobre arreglos float: FLOAT (~20%) + MEM (~28%,
 * 2 cargas + 2 escrituras por elemento). Razon de ser: cubre la region
 * float+mem densa del espacio de composicion --- el perfil de las cargas de
 * validacion flotantes (fpgain: 23% float + 38% mem) --- que fpoly (float
 * alto, mem 10%) y vecscale (26/13) no alcanzan: sin ella la regresion nunca
 * ve el costo del float acompañado de trafico real de memoria.
 *
 * ESTRUCTURA CALCADA de vecscale (el patron FP probado en este bitstream):
 * relleno de UN arreglo por vuelta (un solo fcvt por elemento) y lazo
 * principal con fmul+fadd+fcvt independientes por elemento, sin cadenas
 * (-ffp-contract=off evita fmadd). La primera version rellenaba DOS arreglos
 * por vuelta (dos fcvt adyacentes por iteracion) y NO TERMINABA en hardware:
 * el mismo modo de falla de la FPU que restringe las cargas de validacion.
 * B[] se llena una unica vez; A[] se refresca cada vuelta como en vecscale. */
#ifndef REPS
#define REPS 230000
#endif
#define N 64
static float A[N], B[N], C[N];
void run_workload(void){
  volatile int sink=0;
  const float s=1.0009765625f;
  static int init=0;
  if(!init){
    for(int i=0;i<N;i++) B[i]=(float)((i*7)&127);
    init=1;
  }
  for(int r=0;r<REPS;r++){
    for(int i=0;i<N;i++) A[i]=(float)(((i*13+r)&255)-128);  /* como vecscale */
    int acc=0;
    for(int i=0;i<N;i++){
      float v=A[i]*s+B[i];        /* flw + flw + fmul + fadd */
      C[i]=v;                     /* fsw */
      acc+=(int)v;                /* fcvt.w.s; acumula en entero */
    }
    sink+=acc;
  }
  (void)sink;
}
