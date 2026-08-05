/* TRIALDIV: prueba de divisibilidad por division (n % d) sobre un rango de
 * divisores. ALTA fraccion de DIV/REM (el divisor serial ocupa muchos ciclos ->
 * sube c_div), con ctrl (la rama del if) y poco mem. 3.er programa con div para
 * darle soporte al coeficiente. Entera, sin float -> segura. */
#ifndef REPS
#define REPS 40000
#endif
void run_workload(void){
  volatile int sink=0;
  for(int r=0;r<REPS;r++){
    unsigned n=100003u+(unsigned)r*2u;
    int cnt=0;
    for(int d=2;d<=96;d++){
      if(n % (unsigned)d == 0) cnt++;             /* rem (div serial) */
      n += (n / (unsigned)d) & 1;                 /* div extra para subir c_div */
    }
    sink+=cnt;
  }
  (void)sink;
}
