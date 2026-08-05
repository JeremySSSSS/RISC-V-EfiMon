/* HISTOGRAM: conteo por bins + suma prefija sobre un arreglo. Mezcla MEM pesada
 * (load del dato + load/store del bin) + ALU (mascara/indice) + CTRL (lazos).
 * Entera, sin float -> segura. Mezcla DISTINTA a sort (aqui no hay compare-swap,
 * es acceso disperso a la tabla de bins). */
#ifndef REPS
#define REPS 200000
#endif
#define N 256
#define BINS 64
static unsigned char a[N];
static int hist[BINS];
void run_workload(void){
  volatile int sink=0;
  for(int r=0;r<REPS;r++){
    unsigned s=(unsigned)r*2654435761u;
    for(int i=0;i<N;i++){ s=s*1103515245u+12345u; a[i]=(unsigned char)((s>>16)&(BINS-1)); }
    for(int b=0;b<BINS;b++) hist[b]=0;
    for(int i=0;i<N;i++) hist[a[i]]++;            /* MEM dispersa + ALU */
    int acc=0;
    for(int b=0;b<BINS;b++){ acc+=hist[b]; hist[b]=acc; }   /* suma prefija */
    sink+=hist[BINS-1];
  }
  (void)sink;
}
