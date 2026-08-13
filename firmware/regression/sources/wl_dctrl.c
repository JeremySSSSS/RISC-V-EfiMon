/* DOMINANTE CTRL (~90%): replica la mezcla de control REAL de M1 (ctrl.S):
 * BRANCHES CONDICIONALES TOMADOS (comparacion + salto, flush del pipeline) mas
 * llamadas a funcion. La version anterior usaba saltos `j` incondicionales, que
 * son mas BARATOS que los branches/calls reales -> subvaluaba ctrl (e_impl 3.6
 * vs 5.65 de M1). Los operandos hacen que las 4 ramas de cada grupo se TOMEN. */
#ifndef REPS
#define REPS 40
#endif

/* funcion hoja con branches internos: jal (call) + ret + 2 branches tomados */
static int __attribute__((noinline)) csub(int x){
  asm volatile(
    "bne  %0,zero,1f\n nop\n1:\n"
    "blt  %0,zero,2f\n nop\n2:\n"
    : : "r"(x|1) : );
  return x ^ 1;
}

void run_workload(void){
  volatile int sink=0;
  for(int r=0;r<REPS;r++){
    /* 16 grupos x 4 branches condicionales TOMADOS (como CGROUP de M1). Los
     * operandos garantizan que se tomen: t0!=t1, t2<0<t3, t1>=t0, t3!=t2. La
     * instruccion saltada (xor/add/and) NO se ejecuta -> ctrl domina. */
    asm volatile(
      "li t0, 0x100\n"
      "li t1, 0x101\n"
      "li t2, 0x80001111\n"       /* negativo con signo */
      "li t3, 0x00000f0f\n"       /* pequeno positivo */
      ".rept 16\n"
      "bne  t0,t1,1f\n xor a0,t0,t1\n1:\n"    /* tomado (t0!=t1) */
      "blt  t2,t3,2f\n add a0,t2,t3\n2:\n"    /* tomado (neg<pos) */
      "bgeu t1,t0,3f\n and a0,t0,t2\n3:\n"    /* tomado (t1>=t0 unsigned) */
      "bne  t3,t2,4f\n xor a0,t2,t3\n4:\n"    /* tomado (t3!=t2) */
      ".endr\n"
      : : : "t0","t1","t2","t3","a0");
    sink += csub(sink);            /* jal + ret (call real) */
  }
  (void)sink;
}
