/* MULHCHAIN [RETIRADO tras experimento del 13-jul-2026]: hizo su trabajo
 * (mulh 10.4->3.9 nJ, anclado) pero su ALU de mezcla tipo hash conmuta mas
 * que el alu compilado tipico y contamino la atribucion (alu +20%, mem -28%);
 * la validacion global quedo igual (0.20 vs 0.22%) con el error trasladado a
 * las cargas de alu. Segunda confirmacion de la dependencia del contexto
 * intra-categoria (la primera: los pares). Kernel original: cadena de productos ALTOS, mulh DENSO (~25%, 8 productos por vuelta sin derrames a pila) y SIN mul: solo se
 * usa la palabra alta ((int64)a*b)>>32, asi que GCC emite mulh/mulhu sin mul.
 * Razon de ser: en el resto del set mulh nunca pasa del 9% de las
 * instrucciones (mulhash64 9.0, mulhscale 7.5, dotprod 2.3) -> la regresion
 * estima su coeficiente con una palanca debil y lo sobreatribuye; la carga de
 * validacion wmul (58% mulh) lo expuso con +0.6..0.85% de error. Este kernel
 * le da a la regresion una composicion donde mulh domina, pero con el MISMO
 * contexto de codigo compilado que el resto del set (leccion de los pares: el
 * asm sintetico denso NO sirve de calibracion). Distinto de wmul (validacion):
 * alli bloques .rept de mulh/mulhu/mulhsu; aqui cadena C con dependencias.
 * Las dependencias entre productos impiden que el compilador los fusione. */
#ifndef REPS
#define REPS 2300000
#endif
void run_workload(void){
  volatile int sink=0;
  unsigned a=0x9e3779b9u, b=0x85ebca6bu;
  int acc=0;
  for(int r=0;r<REPS;r++){
    int      h1=(int)(((long long)(int)a*(int)b)>>32);
    unsigned h2=(unsigned)(((unsigned long long)a*(b^0x27d4eb2fu))>>32);
    int      h3=(int)(((long long)(int)(a+h2)*(int)(b-h1))>>32);
    unsigned h4=(unsigned)(((unsigned long long)(a^(unsigned)h1)*(b+(unsigned)h3))>>32);
    int      h5=(int)(((long long)(int)(a+h4)*(int)(b^h2))>>32);
    unsigned h6=(unsigned)(((unsigned long long)(a-(unsigned)h3)*(b+(unsigned)h5))>>32);
    int      h7=(int)(((long long)(int)(a^h6)*(int)(b+h4))>>32);
    unsigned h8=(unsigned)(((unsigned long long)(a+(unsigned)h5)*(b^(unsigned)h7))>>32);
    acc+=h1+h3+h5+h7;
    a+=h2+h6; b^=h4+h8;
  }
  sink+=acc; (void)sink;
}
