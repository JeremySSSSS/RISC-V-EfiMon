/* RADIX: conversion de base con divisor VARIABLE (div/rem en cadena hasta
 * agotar el numero). El divisor viene de un arreglo -> el compilador NO puede
 * convertir la division en multiplicacion (como haria con una constante). Da
 * a la categoria div un 4.o programa con perfil DISTINTO a gcd/modpow/trialdiv
 * (aqui div va mezclada con mem, no con ctrl), subiendo el soporte del
 * coeficiente y descorrelacionando div de ctrl. Entera, sin float -> segura. */
#ifndef REPS
#define REPS 30000
#endif
static const unsigned BASES[8]={3u,5u,7u,10u,11u,13u,16u,23u};
static unsigned DIGITS[40];
void run_workload(void){
  volatile unsigned sink=0;
  for(int r=0;r<REPS;r++){
    unsigned n=0x7fffffffu-(unsigned)r*97u;
    unsigned s=0;
    for(int b=0;b<8;b++){
      unsigned base=BASES[b];
      unsigned v=n; int k=0;
      while(v){
        DIGITS[k]=v%base;                       /* rem (div serial) */
        v/=base;                                /* div (div serial) */
        k++;
      }
      for(int i=0;i<k;i++) s+=DIGITS[i];
    }
    sink+=s;
  }
  (void)sink;
}
