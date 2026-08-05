/* MODPOW: exponenciacion modular por cuadrados (square-and-multiply). Mezcla
 * MUL (base*base, res*base) + DIV/REM (% mod) pesada + CTRL (lazo de bits).
 * Entera, sin float -> segura. Refuerza DIV y MUL juntos, mezcla DISTINTA a gcd
 * (gcd es rem en cadena de Euclides; aqui es mul+rem por cada bit del exponente). */
#ifndef REPS
#define REPS 60000
#endif
static unsigned modpow(unsigned base, unsigned exp, unsigned mod){
  unsigned res=1; base%=mod;
  while(exp){
    if(exp&1) res=(res*base)%mod;     /* mul + rem */
    exp>>=1;
    base=(base*base)%mod;             /* mul + rem */
  }
  return res;
}
void run_workload(void){
  volatile unsigned sink=0;
  for(int r=0;r<REPS;r++){
    unsigned acc=0;
    for(int i=1;i<=16;i++){
      unsigned b=(unsigned)(i*2654435761u + r);
      unsigned e=(unsigned)((i*97+r)&0xff)|1;
      unsigned m=(unsigned)((i*40503+r*7)&0x7fff)|1;
      acc+=modpow(b,e,m);
    }
    sink+=acc;
  }
  (void)sink;
}
