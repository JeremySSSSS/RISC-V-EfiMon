/* MULHI: acumula SOLO la palabra ALTA de productos 32x32 -> emite la instruccion
 * MULH casi sin MUL. Esto DECORRELACIONA mulh de mul (en el set actual mulh
 * siempre venia pegado a mul -> r=+0.77 -> la regresion sobreestimaba mulh 2-3x).
 * Como solo se usa (a*b)>>32, el compilador elimina la parte baja (el mul) por
 * dead-code -> queda mulh dominante. Entera, sin float -> segura. */
#ifndef REPS
#define REPS 100000
#endif
#define N 64
static int a[N], b[N];
void run_workload(void){
  volatile long long sink=0;
  for(int r=0;r<REPS;r++){
    for(int i=0;i<N;i++){ a[i]=(i*2654435761u)^(r*40503u); b[i]=(i*97u+r*7u)|1; }
    long long acc=0;
    for(int i=0;i<N;i++)
      acc += (int)(((long long)a[i]*(long long)b[i]) >> 32);   /* solo palabra alta -> mulh */
    sink+=acc;
  }
  (void)sink;
}
