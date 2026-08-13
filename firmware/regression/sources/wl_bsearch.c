/* BSEARCH: busqueda binaria sobre arreglo ordenado, target pseudo-aleatorio
 * (xorshift, sin mul/div) -- CTRL (saltos data-dependent) + MEM + ALU puro. */
#ifndef REPS
#define REPS 2000000
#endif
#define N 64
static int arr[N];
void run_workload(void){
  volatile int sink=0;
  for(int i=0;i<N;i++) arr[i]=i*3+1;
  unsigned s=12345u;
  for(int r=0;r<REPS;r++){
    s^=s<<13; s^=s>>17; s^=s<<5;
    int target=(int)(s&255);
    int lo=0,hi=N-1,found=-1;
    while(lo<=hi){
      int mid=(lo+hi)>>1;
      int v=arr[mid];
      if(v==target){found=mid;break;}
      else if(v<target) lo=mid+1;
      else hi=mid-1;
    }
    sink+=found+lo;
  }
  (void)sink;
}
