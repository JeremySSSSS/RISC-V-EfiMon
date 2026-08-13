/* SORT: insertion sort — mezcla MEM (arreglo) + ALU (comparaciones/indices)
 * + CTRL (saltos de los bucles anidados). */
#ifndef REPS
#define REPS 20000
#endif
#define N 48
static int a[N];
void run_workload(void){
  volatile int sink=0;
  for(int r=0;r<REPS;r++){
    unsigned s=(unsigned)r*2654435761u;
    for(int i=0;i<N;i++){ s=s*1103515245u+12345u; a[i]=(int)((s>>16)&0x3ff); }
    for(int i=1;i<N;i++){ int k=a[i],j=i-1; while(j>=0&&a[j]>k){a[j+1]=a[j];j--;} a[j+1]=k; }
    sink+=a[0]+a[N-1];
  }
  (void)sink;
}
