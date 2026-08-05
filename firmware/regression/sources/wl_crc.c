/* CRC32 bytewise (sin tabla) — ALU/logica pesada (xor/shift/and) + MEM + CTRL. */
#ifndef REPS
#define REPS 40000
#endif
#define LEN 128
static unsigned char buf[LEN];
void run_workload(void){
  volatile unsigned sink=0;
  for(int r=0;r<REPS;r++){
    for(int i=0;i<LEN;i++) buf[i]=(unsigned char)(i*31+r);
    unsigned crc=0xFFFFFFFFu;
    for(int i=0;i<LEN;i++){ crc^=buf[i];
      for(int b=0;b<8;b++) crc=(crc>>1)^(0xEDB88320u&(unsigned)(-(int)(crc&1))); }
    sink^=crc;
  }
  (void)sink;
}
